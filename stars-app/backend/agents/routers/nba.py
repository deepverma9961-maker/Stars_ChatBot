from fastapi import APIRouter
from ..models.nba import NBARequest, NBAResponse
from ..services.nba_agent import NextBestActionAgent

router = APIRouter(prefix="/agents/nba", tags=["agents"])

_agent = NextBestActionAgent()


@router.post("/recommend", response_model=NBAResponse)
def recommend(req: NBARequest):
    return _agent.recommend(req)


@router.get("/status")
def status():
    from ...services.ml_propensity import is_live
    return {
        "agent": "next_best_action",
        "status": "live" if is_live() else "fallback",
    }
