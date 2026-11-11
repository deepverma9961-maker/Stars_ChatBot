from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from .cohort import PrioritizedMember


class NBARequest(BaseModel):
    members: list[PrioritizedMember]
    contract_id: str = "H3312"
    budget_per_member: Optional[float] = None
    measurement_year: int = 2025


class ActionAlternative(BaseModel):
    channel: str
    incentive: str
    predicted_closure_prob: float
    cost: float


class RecommendedAction(BaseModel):
    member_key: str
    display_name: str
    measure_code: str
    measure_name: str
    gap_status: str
    age: int
    days_open: int
    propensity_score: float
    recommended_channel: str
    recommended_incentive: str
    recommended_timing: str
    predicted_closure_prob: float
    cost_estimate: float
    roi_score: float
    reasoning: str
    alternatives: list[ActionAlternative] = Field(default_factory=list)


class NBAResponse(BaseModel):
    actions: list[RecommendedAction]
    total_budget_estimate: float
    avg_predicted_closure: float
    source: str
    generated_at: str
