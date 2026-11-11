from __future__ import annotations

import logging
from datetime import datetime, timezone

from ...services.message_ai import generate_outreach_message, is_live as ai_is_live
from ...services.outreach_service import (
    send_sms, send_email, make_voice_call, resolve_contact,
)
from ...services.outreach_logger import log_outreach
from ...models.message_ai import GenerateMessageRequest
from ..models.nba import RecommendedAction
from ..models.communication import (
    CommunicationRequest, CommunicationResponse, MessageDeliveryResult,
)

logger = logging.getLogger("agent.communication")

_FALLBACK_TEMPLATES = {
    "SMS": "Hi {name}, this is a reminder about your {measure} screening. Please call us at 1-800-555-0100 to schedule.",
    "Email": "Dear {name},\n\nWe noticed you have an open care gap for {measure}. Please schedule your appointment at your earliest convenience.\n\nCall 1-800-555-0100 or visit your member portal.\n\nWarm regards,\n{plan} Care Team",
    "Call": "Hello {name}, I'm calling from {plan} about your {measure} care gap. We'd like to help you schedule your screening. Would you have a moment to discuss available times?",
}


class CommunicationAgent:

    def execute(self, req: CommunicationRequest) -> CommunicationResponse:
        results: list[MessageDeliveryResult] = []

        for i, action in enumerate(req.actions):
            result = self._process_action(action, req, i)
            results.append(result)

        total_sent = sum(1 for r in results if r.delivery_status == "delivered")
        total_failed = sum(1 for r in results if r.delivery_status == "failed")
        total_dry = sum(1 for r in results if r.delivery_status == "dry_run")

        return CommunicationResponse(
            results=results,
            total_sent=total_sent,
            total_failed=total_failed,
            total_dry_run=total_dry,
            campaign_name=req.campaign_name,
            source="ai" if ai_is_live() else "fallback",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _process_action(
        self,
        action: RecommendedAction,
        req: CommunicationRequest,
        index: int,
    ) -> MessageDeliveryResult:
        channel = action.recommended_channel
        gen_req = self._build_generate_request(action, req.plan_name)

        body, subject, msg_source, _ = generate_outreach_message(gen_req)

        if not body:
            first_name = action.display_name.split(" ")[0]
            template = _FALLBACK_TEMPLATES.get(channel, _FALLBACK_TEMPLATES["SMS"])
            body = template.format(
                name=first_name,
                measure=action.measure_name,
                plan=req.plan_name,
            )
            if channel == "Email" and not subject:
                subject = f"Health Reminder — {action.measure_name}"
            msg_source = "fallback"

        contact = resolve_contact(action.display_name, channel, index)

        if req.dry_run:
            return MessageDeliveryResult(
                member_key=action.member_key,
                display_name=action.display_name,
                channel=channel,
                message_body=body,
                message_subject=subject,
                message_source=msg_source,
                delivery_status="dry_run",
                delivery_detail="Preview only — not sent",
                contact_used=contact,
                cost_estimate=action.cost_estimate,
            )

        success, detail = False, ""
        if channel == "SMS":
            success, detail = send_sms(contact, body)
        elif channel == "Email":
            success, detail = send_email(contact, subject or "Health Reminder", body)
        elif channel == "Call":
            success, sid, err = make_voice_call(contact, body)
            detail = sid if success else err

        status = "delivered" if success else "failed"

        try:
            log_outreach(
                channel=channel,
                member_name=action.display_name,
                contact_used=contact,
                measure=action.measure_name,
                measure_code=action.measure_code,
                campaign_name=req.campaign_name,
                status=status,
                provider_sid=detail if success else "",
                error_detail="" if success else detail,
                script_body=body,
            )
        except Exception:
            logger.warning("Failed to log outreach for %s", action.display_name)

        return MessageDeliveryResult(
            member_key=action.member_key,
            display_name=action.display_name,
            channel=channel,
            message_body=body,
            message_subject=subject,
            message_source=msg_source,
            delivery_status=status,
            delivery_detail=detail,
            contact_used=contact,
            cost_estimate=action.cost_estimate,
        )

    def _build_generate_request(
        self, action: RecommendedAction, plan_name: str
    ) -> GenerateMessageRequest:
        return GenerateMessageRequest(
            channel=action.recommended_channel,
            measure_code=action.measure_code,
            measure_name=action.measure_name,
            gap_status=action.gap_status,
            days_open=action.days_open,
            member_name=action.display_name,
            age=action.age,
            plan_name=plan_name,
            prior_outreach_count=0,
        )
