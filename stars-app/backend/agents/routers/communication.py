from fastapi import APIRouter
from ..models.communication import CommunicationRequest, CommunicationResponse
from ..services.communication_agent import CommunicationAgent

router = APIRouter(prefix="/agents/communication", tags=["agents"])

_agent = CommunicationAgent()


@router.post("/execute", response_model=CommunicationResponse)
def execute(req: CommunicationRequest):
    return _agent.execute(req)


@router.post("/preview", response_model=CommunicationResponse)
def preview(req: CommunicationRequest):
    req.dry_run = True
    return _agent.execute(req)


@router.get("/status")
def status():
    from ...services.message_ai import is_live as ai_live
    from ...config import settings
    return {
        "agent": "communication",
        "ai_messaging": "live" if ai_live() else "fallback",
        "twilio_configured": bool(settings.twilio_account_sid),
        "sendgrid_configured": bool(settings.sendgrid_api_key),
    }
