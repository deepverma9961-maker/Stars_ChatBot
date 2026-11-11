from fastapi import APIRouter, HTTPException
from ..models.orchestration import (
    CampaignConfig, PipelineState, PipelineSummary, ApprovalRequest,
)
from ..services.orchestration_agent import OrchestrationAgent

router = APIRouter(prefix="/agents/orchestration", tags=["agents"])

_agent = OrchestrationAgent()


@router.post("/campaigns", response_model=PipelineState)
def create_campaign(config: CampaignConfig):
    return _agent.create_campaign(config)


@router.get("/campaigns", response_model=list[PipelineSummary])
def list_campaigns():
    return _agent.list_pipelines()


@router.get("/campaigns/{campaign_id}", response_model=PipelineState)
def get_campaign(campaign_id: str):
    state = _agent.get_pipeline(campaign_id)
    if not state:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return state


@router.post("/campaigns/{campaign_id}/approve", response_model=PipelineState)
def approve_campaign(campaign_id: str, req: ApprovalRequest):
    try:
        return _agent.approve_campaign(campaign_id, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaigns/{campaign_id}/retry", response_model=PipelineState)
def retry_campaign(campaign_id: str):
    try:
        return _agent.retry_campaign(campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
def status():
    pipelines = _agent.list_pipelines()
    active = sum(
        1 for p in pipelines
        if p.stage not in ("completed", "failed")
    )
    return {
        "agent": "orchestration",
        "total_campaigns": len(pipelines),
        "active_campaigns": active,
    }
