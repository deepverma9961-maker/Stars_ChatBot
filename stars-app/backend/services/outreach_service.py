import logging
from ..config import settings
from ..db import query
from ..models.outreach import (
    SendBundleRequest, SendBundleResponse, RecipientResult,
)
from .outreach_logger import log_outreach

logger = logging.getLogger("outreach")

_TABLE = f"{settings.silver}.verified_contacts"



def get_verified_contacts() -> list[dict]:
    """Fetch all active verified contacts from Databricks."""
    try:
        return query(f"""
            SELECT id, phone, email, is_active, created_at
            FROM {_TABLE}
            WHERE is_active = TRUE
            ORDER BY created_at DESC
        """)
    except Exception as e:
        logger.warning("Could not fetch verified contacts: %s", e)
        return []


def get_all_contacts() -> list[dict]:
    """Fetch all contacts (active + inactive) for management UI."""
    try:
        return query(f"""
            SELECT id, phone, email, is_active, created_at
            FROM {_TABLE}
            ORDER BY created_at DESC
        """)
    except Exception as e:
        logger.warning("Could not fetch contacts: %s", e)
        return []


def resolve_contact(member_name: str, channel: str, recipient_index: int = 0) -> str:
    """Round-robin across active verified contacts.

    If 2 active contacts: index 0→A, 1→B, 2→A, 3→B  (50/50)
    If 3 active contacts: index 0→A, 1→B, 2→C, 3→A   (33/33/33)
    """
    contacts = get_verified_contacts()
    if channel in ("SMS", "Call"):
        phones = [c["phone"] for c in contacts if c.get("phone")]
        if phones:
            return phones[recipient_index % len(phones)]
        return ""
    else:  # Email
        emails = [c["email"] for c in contacts if c.get("email")]
        if emails:
            return emails[recipient_index % len(emails)]
        return ""


def send_sms(to_number: str, body: str) -> tuple[bool, str]:
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        message = client.messages.create(
            body=body,
            from_=settings.twilio_from_number,
            to=to_number,
        )
        logger.info("SMS sent to %s: SID=%s", to_number, message.sid)
        return True, message.sid
    except Exception as e:
        logger.error("SMS failed to %s: %s", to_number, e)
        return False, str(e)


def send_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        message = Mail(
            from_email=settings.sendgrid_from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body,
        )
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)
        logger.info("Email sent to %s: status=%s", to_email, response.status_code)
        return True, f"status_{response.status_code}"
    except Exception as e:
        logger.error("Email failed to %s: %s", to_email, e)
        return False, str(e)


def make_voice_call(to_number: str, script: str) -> tuple[bool, str, str]:
    """Place an automated Twilio voice call with interactive DTMF menu."""
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        # Twilio Functions handle webhooks (Databricks Apps blocks external POST with 401)
        twilio_fn_base = "https://starpulse-webhooks-1622-prod.twil.io"
        gather_url = f"{twilio_fn_base}/call-gather"
        # Status callback still goes to our backend via tunnel/deployed URL
        base = settings.app_base_url.rstrip("/")
        status_url = f"{base}/api/outreach/call-status"

        safe_script = script.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # <Say> MUST be inside <Gather> so Twilio captures DTMF while speaking
        twiml = (
            '<Response>'
            '<Say voice="Polly.Joanna-Neural" language="en-US">'
            '<prosody rate="95%">' + safe_script + '</prosody>'
            '</Say>'
            '<Pause length="1"/>'
            '<Gather numDigits="1" action="' + gather_url + '" method="POST" timeout="10">'
            '<Say voice="Polly.Joanna-Neural">'
            '<prosody rate="95%">'
            'Press 1 to schedule your appointment now.'
            '<break time="400ms"/>'
            'Press 2 to speak with an AI care coordinator.'
            '<break time="400ms"/>'
            'Or simply hang up if no action is needed.'
            '</prosody>'
            '</Say>'
            '</Gather>'
            '<Say voice="Polly.Joanna-Neural">We did not receive your selection. Thank you for your time. Goodbye.</Say>'
            '</Response>'
        )

        call = client.calls.create(
            twiml=twiml,
            from_=settings.twilio_from_number,
            to=to_number,
            status_callback=status_url,
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        logger.info("Voice call placed to %s: SID=%s", to_number, call.sid)
        return True, call.sid, ""
    except Exception as e:
        logger.error("Voice call failed to %s: %s", to_number, e)
        return False, "", str(e)


def execute_bundle(req: SendBundleRequest) -> SendBundleResponse:
    results: list[RecipientResult] = []
    for i, recipient in enumerate(req.recipients):
        first_name = recipient.member_name.split(" ")[0]
        replacements = {
            "{name}": first_name, "[Name]": first_name,
            "{full_name}": recipient.member_name, "[Full Name]": recipient.member_name,
            "{measure}": recipient.measure, "[Measure]": recipient.measure,
            "{measure_code}": recipient.measure_code, "[Measure Code]": recipient.measure_code,
            "{age}": str(recipient.age), "[Age]": str(recipient.age),
            "{pcp}": recipient.pcp, "[PCP]": recipient.pcp,
            "{gap}": recipient.gap, "[Gap]": recipient.gap,
            "{propensity}": str(recipient.propensity), "[Propensity]": str(recipient.propensity),
        }
        body = req.message_template
        for placeholder, value in replacements.items():
            body = body.replace(placeholder, value)
        contact = resolve_contact(recipient.member_name, req.channel, recipient_index=i)

        if req.channel == "SMS":
            success, detail = send_sms(contact, body)
        elif req.channel == "Email":
            subject = f"Health Reminder for {first_name} — {recipient.measure_code or recipient.measure} Screening"
            success, detail = send_email(contact, subject, body)
        else:
            success, detail = False, f"Unsupported channel: {req.channel}"

        row_status = "delivered" if success else "failed"
        results.append(RecipientResult(
            member_name=recipient.member_name,
            contact_used=contact,
            status=row_status,
            detail=detail,
        ))
        try:
            log_outreach(
                channel=req.channel,
                member_name=recipient.member_name,
                contact_used=contact,
                measure=recipient.measure,
                measure_code=recipient.measure_code,
                campaign_name=getattr(req, "campaign_name", ""),
                status=row_status,
                provider_sid=detail if success else "",
                error_detail="" if success else detail,
                script_body=body,
            )
        except Exception:
            logger.warning("Failed to log outreach for %s", recipient.member_name)

    succeeded = sum(1 for r in results if r.status == "delivered")
    return SendBundleResponse(
        channel=req.channel,
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )
