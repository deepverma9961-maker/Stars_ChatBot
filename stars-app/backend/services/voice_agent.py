"""
Twilio ConversationRelay WebSocket handler — bridges voice calls to Claude AI.

Protocol: Twilio sends JSON messages over WSS:
  - {"type":"setup", ...}    → session init
  - {"type":"prompt", "voicePrompt":"..."} → speech-to-text from caller
  - {"type":"interrupt"}     → caller interrupted AI speech

We respond with:
  - {"type":"text", "token":"..."} → text for TTS playback to caller
"""
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from ..config import settings

logger = logging.getLogger("voice_agent")

_SYSTEM_PROMPT = (
    "You are a friendly and professional Medicare care coordinator for StarPulse. "
    "You are speaking with a member on the phone about their healthcare gap. "
    "Keep responses short (1-3 sentences) since this is a voice conversation. "
    "Be warm, empathetic, and helpful. Help them understand why their screening "
    "or medication adherence matters, and assist with scheduling if they want. "
    "If they want to schedule, offer time slots: tomorrow morning 9 AM, "
    "tomorrow afternoon 2 PM, or tomorrow afternoon 3:30 PM. "
    "If they have questions about their health plan, answer helpfully. "
    "Never provide specific medical diagnoses — recommend they speak with their doctor. "
    "End the conversation gracefully when the member is satisfied. "
    "Speak naturally and conversationally. Use filler phrases like 'Sure thing', "
    "'Let me help with that', 'That is a great question'. "
    "Avoid lists or bullet points — use flowing sentences. Keep a warm, unhurried tone."
)

# Lazy-init async client (created on first use)
_aclient = None


def _get_async_client():
    global _aclient
    if _aclient is None:
        if not settings.anthropic_api_key:
            return None
        import anthropic
        _aclient = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _aclient


async def handle_voice_agent(websocket: WebSocket):
    await websocket.accept()
    conversation = []
    call_sid = ""

    # Check API key upfront
    if not settings.anthropic_api_key:
        logger.error("Voice agent: ANTHROPIC_API_KEY not set — sending apology and closing")
        await websocket.send_text(json.dumps({
            "type": "text",
            "token": "I apologize, our AI care coordinator is temporarily unavailable. "
                     "Please call back and press 1 to schedule an appointment, "
                     "or call our care line at 1-800-555-0100. Thank you.",
            "last": True,
        }))
        await websocket.close()
        return

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type", "")

            if msg_type == "setup":
                call_sid = msg.get("callSid", "")
                logger.info("Voice agent session started: SID=%s", call_sid)
                continue

            if msg_type == "interrupt":
                logger.info("Voice agent interrupted: SID=%s", call_sid)
                continue

            if msg_type == "prompt":
                user_text = msg.get("voicePrompt", "").strip()
                if not user_text:
                    continue

                logger.info("Voice agent prompt: SID=%s text=%s", call_sid, user_text[:100])
                conversation.append({"role": "user", "content": user_text})

                response_text = await _query_claude(conversation)
                conversation.append({"role": "assistant", "content": response_text})

                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": response_text,
                    "last": True,
                }))

            if msg_type == "dtmf":
                digit = msg.get("digit", "")
                logger.info("Voice agent DTMF: SID=%s digit=%s", call_sid, digit)

    except WebSocketDisconnect:
        logger.info("Voice agent disconnected: SID=%s", call_sid)
    except Exception as e:
        logger.error("Voice agent error: SID=%s err=%s", call_sid, e, exc_info=True)


async def query_claude(conversation: list[dict]) -> str:
    """Public helper — used by both WebSocket agent and HTTP call-agent endpoint."""
    return await _query_claude(conversation)


async def _query_claude(conversation: list[dict]) -> str:
    try:
        client = _get_async_client()
        if client is None:
            return "I apologize, the AI assistant is temporarily unavailable. Please try again later."
        response = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=200,
            system=_SYSTEM_PROMPT,
            messages=conversation,
        )
        return response.content[0].text
    except Exception as e:
        logger.error("Claude API error: %s", e)
        return "I apologize, I'm having a brief technical issue. Could you please repeat that?"
