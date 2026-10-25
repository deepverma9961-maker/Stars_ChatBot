import logging
from fastapi import APIRouter, BackgroundTasks, Query, Request
from fastapi.responses import Response
from ..models.outreach import (
    SendBundleRequest, SendBundleResponse,
    MakeCallRequest, MakeCallResponse,
    OutreachLogEntry, OutreachLogsResponse, SyncStatusResponse,
)
from ..models.message_ai import GenerateMessageRequest, GenerateMessageResponse
from ..services.outreach_service import execute_bundle, make_voice_call, resolve_contact
from ..services.outreach_logger import log_outreach, get_outreach_logs, sync_pending_statuses, update_outreach_by_sid
from ..services import message_ai
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["outreach"])


@router.post("/outreach/send-bundle", response_model=SendBundleResponse)
def send_bundle(req: SendBundleRequest):
    return execute_bundle(req)


@router.post("/outreach/make-call", response_model=MakeCallResponse)
def make_call(req: MakeCallRequest):
    phone = req.phone or resolve_contact(req.member_name, "Call")
    if not phone:
        return MakeCallResponse(status="failed", detail="No verified contact found. Add a phone number in the Verified Contacts table.")
    success, call_sid, err = make_voice_call(phone, req.script)
    status = "initiated" if success else "failed"
    log_outreach(
        channel="Call",
        member_name=req.member_name,
        contact_used=phone,
        measure=req.measure,
        measure_code=req.measure_code,
        status=status,
        provider_sid=call_sid if success else "",
        error_detail="" if success else err,
        script_body=req.script,
    )
    if success:
        return MakeCallResponse(status="initiated", call_sid=call_sid, to_number=phone,
                                detail=f"Call initiated to {phone}")
    return MakeCallResponse(status="failed", to_number=phone, detail=err)


@router.get("/outreach/logs", response_model=OutreachLogsResponse)
def outreach_logs(
    limit: int = Query(50, le=200),
    channel: str | None = Query(None),
    status: str | None = Query(None),
):
    rows = get_outreach_logs(limit=limit, channel=channel, status=status)
    entries = []
    for r in rows:
        entries.append(OutreachLogEntry(
            id=r.get("id"),
            created_at=str(r.get("created_at", "")),
            member_name=r.get("member_name", ""),
            channel=r.get("channel", ""),
            contact_used=r.get("contact_used", ""),
            measure=r.get("measure", ""),
            measure_code=r.get("measure_code", ""),
            campaign_name=r.get("campaign_name", ""),
            status=r.get("status", ""),
            provider_sid=r.get("provider_sid", ""),
            error_detail=r.get("error_detail", ""),
            script_body=r.get("script_body", ""),
            updated_at=str(r.get("updated_at", "")),
            member_selection=r.get("member_selection") or "",
            interaction_log=r.get("interaction_log") or "",
        ))
    return OutreachLogsResponse(total=len(entries), logs=entries)


@router.post("/outreach/sync-status", response_model=SyncStatusResponse)
def sync_status():
    result = sync_pending_statuses()
    return SyncStatusResponse(
        synced=result["synced"],
        updated=result["updated"],
        results=result["results"],
    )


@router.get("/outreach/test-db-write")
def test_db_write():
    """Diagnostic endpoint: tests table creation and insert, returns errors."""
    from ..db import execute_write, query, table_exists
    from ..config import settings
    table = f"{settings.silver}.outreach_activity_log"
    steps = []

    # Step 1: Check connection
    try:
        from ..db import query as q
        q("SELECT 1")
        steps.append({"step": "connection", "ok": True})
    except Exception as e:
        steps.append({"step": "connection", "ok": False, "error": str(e)})
        return {"steps": steps}

    # Step 2: Check if table exists
    try:
        exists = table_exists(table)
        steps.append({"step": "table_exists_check", "ok": True, "exists": exists, "table": table})
    except Exception as e:
        steps.append({"step": "table_exists_check", "ok": False, "error": str(e)})

    # Step 3: Try CREATE TABLE
    try:
        execute_write(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id              BIGINT GENERATED ALWAYS AS IDENTITY,
                created_at      TIMESTAMP,
                member_name     STRING,
                channel         STRING,
                contact_used    STRING,
                measure         STRING,
                measure_code    STRING,
                campaign_name   STRING,
                status          STRING,
                provider_sid    STRING,
                error_detail    STRING,
                script_body     STRING,
                updated_at      TIMESTAMP
            )
        """)
        steps.append({"step": "create_table", "ok": True})
    except Exception as e:
        steps.append({"step": "create_table", "ok": False, "error": str(e)})
        return {"steps": steps}

    # Step 4: Try INSERT
    try:
        execute_write(f"""
            INSERT INTO {table}
                (member_name, channel, contact_used, status, provider_sid)
            VALUES
                ('__TEST__', 'Test', 'test@test.com', 'test', 'TEST_SID')
        """)
        steps.append({"step": "insert", "ok": True})
    except Exception as e:
        steps.append({"step": "insert", "ok": False, "error": str(e)})
        return {"steps": steps}

    # Step 5: Try SELECT back
    try:
        rows = query(f"SELECT * FROM {table} WHERE member_name = '__TEST__' LIMIT 1")
        steps.append({"step": "select_back", "ok": True, "row_count": len(rows)})
    except Exception as e:
        steps.append({"step": "select_back", "ok": False, "error": str(e)})

    # Step 6: Cleanup test row
    try:
        execute_write(f"DELETE FROM {table} WHERE member_name = '__TEST__'")
        steps.append({"step": "cleanup", "ok": True})
    except Exception as e:
        steps.append({"step": "cleanup", "ok": False, "error": str(e)})

    return {"steps": steps}


# ── Twilio Webhooks ──────────────────────────────────────────────

def _twiml(xml_body: str) -> Response:
    return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>{xml_body}', media_type="text/xml")


_SLOT_MAP = {
    "1": "tomorrow morning at 9 AM",
    "2": "tomorrow afternoon at 2 PM",
    "3": "tomorrow afternoon at 3:30 PM",
    "4": "callback requested",
}


@router.post("/outreach/call-gather")
async def call_gather(request: Request, bg: BackgroundTasks):
    """Twilio Gather webhook — handles main menu digit press (1=schedule, 2=AI agent).
    DB updates run in background so the TwiML response returns immediately
    (Twilio times out at 15 s)."""
    form = await request.form()
    digits = form.get("Digits", "")
    call_sid = form.get("CallSid", "")
    logger.info("call-gather: SID=%s Digits=%s", call_sid, digits)

    base = settings.app_base_url.rstrip("/")

    if digits == "1":
        bg.add_task(update_outreach_by_sid, call_sid, "scheduling", "Member pressed 1 - scheduling")
        slot_url = f"{base}/api/outreach/call-slot"
        # ALL Say inside Gather so DTMF is captured from the very start
        return _twiml(
            '<Response>'
            f'<Gather numDigits="1" action="{slot_url}" method="POST" timeout="10">'
            '<Say voice="Polly.Joanna-Neural">'
            '<prosody rate="95%">'
            'Great! Here are available time slots.'
            '<break time="400ms"/>'
            'Press 1 for tomorrow morning at 9 A M.'
            '<break time="300ms"/>'
            'Press 2 for tomorrow afternoon at 2 P M.'
            '<break time="300ms"/>'
            'Press 3 for tomorrow afternoon at 3 30 P M.'
            '<break time="300ms"/>'
            'Press 4 to request a callback with more options.'
            '</prosody>'
            '</Say>'
            '</Gather>'
            '<Say voice="Polly.Joanna-Neural">We did not receive your selection. A coordinator will call you to schedule. Goodbye.</Say>'
            '</Response>'
        )

    if digits == "2":
        bg.add_task(update_outreach_by_sid, call_sid, "ai-conversation", "Member pressed 2 - AI agent")
        agent_url = f"{base}/api/outreach/call-agent"
        return _twiml(
            '<Response>'
            '<Gather input="speech" action="' + agent_url + '" method="POST" '
            'speechTimeout="2" timeout="10" language="en-US">'
            '<Say voice="Polly.Joanna-Neural">'
            '<break time="300ms"/>Hi, I am your StarPulse care coordinator. '
            'How can I help you today?</Say>'
            '</Gather>'
            '<Say voice="Polly.Joanna-Neural">I did not hear anything. Thank you for your time. Goodbye.</Say>'
            '</Response>'
        )

    bg.add_task(update_outreach_by_sid, call_sid, "no-action", f"Member pressed {digits or 'nothing'}",
                member_selection="No action taken")
    return _twiml(
        '<Response>'
        '<Say voice="Polly.Joanna-Neural">Thank you for your time. Goodbye.</Say>'
        '</Response>'
    )


@router.post("/outreach/call-slot")
async def call_slot(request: Request, bg: BackgroundTasks):
    """Twilio Gather webhook — handles time-slot selection after Press 1."""
    form = await request.form()
    digits = form.get("Digits", "")
    call_sid = form.get("CallSid", "")
    logger.info("call-slot: SID=%s Digits=%s", call_sid, digits)

    slot = _SLOT_MAP.get(digits, "callback requested")
    bg.add_task(update_outreach_by_sid, call_sid, "scheduled", f"Slot: {slot}",
                member_selection=f"Scheduled: {slot}")

    if digits == "4":
        return _twiml(
            '<Response>'
            '<Say voice="Polly.Joanna-Neural">Your callback request has been noted. '
            'A care coordinator will reach out to you within 24 hours with more options. '
            'Thank you and have a great day!</Say>'
            '</Response>'
        )

    return _twiml(
        '<Response>'
        '<Say voice="Polly.Joanna-Neural">'
        '<emphasis level="moderate">You are confirmed</emphasis> for ' + slot + '. '
        'You will receive an SMS confirmation shortly. Thank you and have a great day!</Say>'
        '</Response>'
    )


# ── In-memory conversation store (keyed by CallSid) ─────────────
_conversations: dict[str, list[dict]] = {}


@router.post("/outreach/call-agent")
async def call_agent(request: Request, bg: BackgroundTasks):
    """Speech-based AI agent — Twilio sends speech-to-text via Gather,
    we reply with Claude's response as TwiML <Say>, then loop."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    speech = form.get("SpeechResult", "")
    logger.info("call-agent: SID=%s Speech=%s", call_sid, speech[:120] if speech else "(empty)")

    base = settings.app_base_url.rstrip("/")
    agent_url = f"{base}/api/outreach/call-agent"

    if not speech:
        return _twiml(
            '<Response>'
            '<Say voice="Polly.Joanna-Neural"><break time="300ms"/>I did not catch that. Could you please repeat?</Say>'
            f'<Gather input="speech" action="{agent_url}" method="POST" '
            'speechTimeout="2" timeout="10" language="en-US"/>'
            '<Say voice="Polly.Joanna-Neural">Thank you for your time. Goodbye.</Say>'
            '</Response>'
        )

    # Build / extend conversation for this call
    if call_sid not in _conversations:
        _conversations[call_sid] = []
    _conversations[call_sid].append({"role": "user", "content": speech})

    # Query Claude
    from ..services.voice_agent import query_claude
    ai_reply = await query_claude(_conversations[call_sid])
    _conversations[call_sid].append({"role": "assistant", "content": ai_reply})

    # Log each turn to audit trail: "Member: ... → AI: ..."
    turn_num = len(_conversations[call_sid]) // 2
    turn_log = f"Turn {turn_num} — Member: {speech[:80]} → AI: {ai_reply[:80]}"
    bg.add_task(update_outreach_by_sid, call_sid, "ai-conversation", turn_log)

    # Clean up old conversations (keep max 50)
    if len(_conversations) > 50:
        oldest = list(_conversations.keys())[0]
        del _conversations[oldest]

    # Escape for XML
    safe_reply = ai_reply.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Check for goodbye signals
    goodbye_words = ["goodbye", "bye", "take care", "have a great day", "thank you for calling"]
    is_ending = any(w in ai_reply.lower() for w in goodbye_words)

    if is_ending:
        turn_summary = f"AI conversation ended after {turn_num} turns"
        bg.add_task(update_outreach_by_sid, call_sid, "ai-completed", turn_summary,
                    member_selection=f"AI Agent: {turn_num} turns completed")
        if call_sid in _conversations:
            del _conversations[call_sid]
        return _twiml(
            '<Response>'
            f'<Say voice="Polly.Joanna-Neural"><break time="300ms"/>{safe_reply}</Say>'
            '</Response>'
        )

    return _twiml(
        '<Response>'
        f'<Gather input="speech" action="{agent_url}" method="POST" '
        'speechTimeout="2" timeout="10" language="en-US">'
        f'<Say voice="Polly.Joanna-Neural"><break time="300ms"/>{safe_reply}</Say>'
        '</Gather>'
        '<Say voice="Polly.Joanna-Neural">I did not hear a response. Thank you for your time. Goodbye.</Say>'
        '</Response>'
    )


@router.post("/outreach/call-status")
async def call_status(request: Request, bg: BackgroundTasks):
    """Twilio status callback — updates final call status."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    status = form.get("CallStatus", "")
    duration = form.get("CallDuration", "")
    logger.info("call-status: SID=%s Status=%s Duration=%s", call_sid, status, duration)

    if call_sid and status:
        detail = f"Duration: {duration}s" if duration else ""
        bg.add_task(update_outreach_by_sid, call_sid, status, detail)

    return Response(content="OK", media_type="text/plain")


# ── Fallback templates (used when LLM is unavailable) ─────────────
_FB_SMS = (
    "Hi {first}, this is your {plan} care team. You have an upcoming {measure} "
    "screening due. Call 1-800-555-0100 or reply YES to schedule. We're here to help!"
)
_FB_EMAIL_BODY = (
    "Dear {first},\n\n"
    "We hope this message finds you well. As part of our ongoing care coordination, "
    "we wanted to reach out regarding your {measure} screening that is currently due.\n\n"
    "Staying on top of preventive screenings is one of the most important steps you "
    "can take for your long-term health. We would love to help you get this scheduled "
    "at a time that works best for you.\n\n"
    "To book your appointment:\n"
    "- Call us at 1-800-555-0100\n"
    "- Reply to this email\n"
    "- Visit our member portal at myhealth.starpulse.com\n\n"
    "Warm regards,\n"
    "{plan} Care Team"
)
_FB_EMAIL_SUBJECT = "Your {measure} screening is due"
_FB_CALL = (
    "Hi {first}, this is {plan} calling about your {measure}. "
    "We want to make sure you get this covered — can we help schedule it today?"
)


def _first_name(full: str) -> str:
    return (full or "there").strip().split(" ")[0]


def _fallback_message(req: GenerateMessageRequest) -> tuple[str, str | None]:
    if req.use_placeholders:
        # Batch path: leave [Name] / [Measure] tokens for execute_bundle() to fill.
        ctx = {"first": "[Name]", "measure": "[Measure]", "plan": req.plan_name or "your health plan"}
    else:
        ctx = {
            "first": _first_name(req.member_name),
            "measure": req.measure_name or "preventive care",
            "plan": req.plan_name or "your health plan",
        }
    if req.channel == "SMS":
        body = _FB_SMS.format(**ctx)
        return (body[:157] + "...") if len(body) > 160 else body, None
    if req.channel == "Email":
        return _FB_EMAIL_BODY.format(**ctx), _FB_EMAIL_SUBJECT.format(**ctx)
    return _FB_CALL.format(**ctx), None


@router.post("/outreach/generate-message", response_model=GenerateMessageResponse)
def generate_message(req: GenerateMessageRequest) -> GenerateMessageResponse:
    body, subject, source, model = message_ai.generate_outreach_message(req)
    if source == "ai" and body:
        return GenerateMessageResponse(body=body, subject=subject, source="ai", model=model)
    fb_body, fb_subject = _fallback_message(req)
    return GenerateMessageResponse(body=fb_body, subject=fb_subject, source="fallback", model=None)
