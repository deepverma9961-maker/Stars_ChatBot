"""LLM-backed outreach-message generator.

Calls Anthropic's Claude (haiku tier by default) to produce per-member, per-
channel outreach copy for the Agent Execution page. Falls back silently to the
legacy hardcoded templates if the SDK isn't installed, the API key isn't set,
or the call fails — so the page never breaks.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Optional, Tuple

from ..config import settings
from ..models.message_ai import GenerateMessageRequest

logger = logging.getLogger("message_ai")

# Simple in-process TTL cache keyed by a stable hash of the inputs.
# A batch view of 25 members with identical (channel, measure, gap, plan)
# should fire one generation, not 25.
_CACHE_TTL_SEC = 60 * 60  # 1 hour
_cache: dict[str, tuple[float, dict]] = {}


def _cache_key(req: GenerateMessageRequest) -> str:
    raw = json.dumps({
        "c": req.channel,
        "m": req.measure_code,
        "n": req.measure_name,
        "g": req.gap_status,
        "p": req.plan_name,
        "a": req.age // 5,  # bucket by 5-year band
        "t": bool(req.use_placeholders),
    }, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def is_live() -> bool:
    return bool(settings.anthropic_api_key)


_PLACEHOLDER_NOTE = (
    "\nThis message will be sent to many recipients. Use the literal token [Name] "
    "wherever the first name should appear, and [Measure] wherever the measure name "
    "should appear. Do not invent names; use only the tokens."
)


def _system_prompt(channel: str, use_placeholders: bool = False) -> str:
    if channel == "SMS":
        base = (
            "You are a Medicare Stars outreach copywriter for a US health plan. "
            "Generate ONE SMS message to a Medicare Advantage member who has an open care gap. "
            "Hard constraints:\n"
            "- Body must be at most 160 characters total, including spaces.\n"
            "- Address the member by first name only.\n"
            "- Mention the measure once, in plain English (do not use the measure code).\n"
            "- Include exactly one clear call-to-action: either 'Reply YES' or a phone number.\n"
            "- No emoji, no markdown, no PHI beyond first name.\n"
            "- Empathetic, brief, non-alarmist. CMS-compliant tone.\n"
            'Respond with strict JSON in the form {"body": "..."} and nothing else.'
        )
        return base + (_PLACEHOLDER_NOTE if use_placeholders else "")
    if channel == "Email":
        base = (
            "You are a Medicare Stars outreach copywriter for a US health plan. "
            "Generate ONE email to a Medicare Advantage member who has an open care gap. "
            "Hard constraints:\n"
            "- Subject at most 60 characters.\n"
            "- Body at most 140 words; plain text only, no markdown.\n"
            "- Open with 'Dear <first name>,' and close with 'Warm regards,\\n<Plan Name> Care Team'.\n"
            "- Mention the measure in plain English (not the code).\n"
            "- Offer three ways to act: call 1-800-555-0100, reply to the email, or visit the member portal.\n"
            "- Empathetic, action-oriented, non-alarmist. CMS-compliant tone.\n"
            'Respond with strict JSON in the form {"subject": "...", "body": "..."} and nothing else.'
        )
        return base + (_PLACEHOLDER_NOTE if use_placeholders else "")
    # Call
    return (
        "You are coaching a call-center agent who is about to dial a Medicare member about an open care gap. "
        "Generate a 2-3 sentence opener the agent will read aloud. "
        "Hard constraints:\n"
        "- Begin with a warm hello using the member's first name.\n"
        "- State the purpose plainly and mention the measure in plain English.\n"
        "- End with an open question inviting the member to schedule.\n"
        "- Plain text only, no quotation marks around the script.\n"
        'Respond with strict JSON in the form {"body": "..."} and nothing else.'
    )


def _user_context(req: GenerateMessageRequest) -> str:
    first = (req.member_name or "Member").strip().split(" ")[0]
    return json.dumps({
        "member_first_name": first,
        "age_band": _age_band(req.age),
        "measure_code": req.measure_code or None,
        "measure_name": req.measure_name or "preventive care",
        "gap_status": req.gap_status,
        "days_open": req.days_open,
        "plan_name": req.plan_name,
        "prior_outreach_count": req.prior_outreach_count,
    })


def _age_band(age: int) -> str:
    if age <= 0:
        return "unknown"
    if age < 70:
        return "65-69"
    if age < 75:
        return "70-74"
    if age < 80:
        return "75-79"
    if age < 85:
        return "80-84"
    return "85+"


def _parse_json_payload(text: str) -> Optional[dict]:
    """Anthropic responses sometimes wrap JSON in prose; extract the first
    balanced JSON object."""
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return None


def generate_outreach_message(req: GenerateMessageRequest) -> Tuple[Optional[str], Optional[str], str, Optional[str]]:
    """Returns (body, subject, source, model_name).

    Source is 'ai' on success, 'fallback' on any failure. Caller is responsible
    for substituting the fallback template when source == 'fallback'.
    """
    if not is_live():
        return None, None, "fallback", None

    # Cache hit?
    key = _cache_key(req)
    now = time.time()
    hit = _cache.get(key)
    if hit and (now - hit[0]) < _CACHE_TTL_SEC:
        cached = hit[1]
        return cached.get("body"), cached.get("subject"), "ai", cached.get("model")

    try:
        import anthropic  # imported lazily so the rest of the app doesn't depend on it
    except Exception as e:
        logger.warning("anthropic SDK not installed: %s", e)
        return None, None, "fallback", None

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        model = settings.anthropic_model or "claude-haiku-4-5"
        resp = client.messages.create(
            model=model,
            max_tokens=400,
            system=_system_prompt(req.channel, req.use_placeholders),
            messages=[{"role": "user", "content": _user_context(req)}],
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        )
        payload = _parse_json_payload(text)
        if not payload or "body" not in payload:
            logger.warning("AI response did not contain a body: %s", text[:200])
            return None, None, "fallback", None
        body = str(payload["body"]).strip()
        subject = str(payload.get("subject", "")).strip() or None
        # Hard-enforce SMS length cap
        if req.channel == "SMS" and len(body) > 160:
            body = body[:157].rstrip() + "..."
        _cache[key] = (now, {"body": body, "subject": subject, "model": model})
        return body, subject, "ai", model
    except Exception as e:
        logger.error("Anthropic call failed: %s", e)
        return None, None, "fallback", None
