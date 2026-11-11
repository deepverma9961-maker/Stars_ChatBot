from fastapi import APIRouter
from ..models.cohort import CohortRequest, CohortResponse
from ..services.cohort_agent import CohortPrioritizationAgent

router = APIRouter(prefix="/agents/cohort", tags=["agents"])

_agent = CohortPrioritizationAgent()


@router.post("/prioritize", response_model=CohortResponse)
def prioritize(req: CohortRequest):
    return _agent.prioritize(req)


@router.get("/status")
def status():
    from ...db import query
    from ...config import settings
    try:
        if settings.databricks_host:
            query("SELECT 1")
            return {"agent": "cohort_prioritization", "status": "live"}
    except Exception:
        pass
    return {"agent": "cohort_prioritization", "status": "fallback"}
