from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class CohortRequest(BaseModel):
    contract_id: str = "H3312"
    measure_code: Optional[str] = None
    gap_statuses: list[str] = Field(default=["Open", "Partial", "Borderline"])
    propensity_tiers: list[str] = Field(default=["high", "medium", "low"])
    max_members: int = Field(default=200, ge=1, le=1000)
    measurement_year: int = 2025


class ScoringFactors(BaseModel):
    propensity_component: float
    urgency_component: float
    measure_weight_component: float
    gap_severity_component: float


class PrioritizedMember(BaseModel):
    member_key: str
    display_name: str
    age: int
    measure_code: str
    measure_name: str
    gap_status: str
    propensity_score: float
    days_open: int
    priority_score: float
    priority_rank: int
    recommended_channel: str
    pcp_name: str
    scoring_factors: ScoringFactors


class CohortResponse(BaseModel):
    members: list[PrioritizedMember]
    total_eligible: int
    total_scored: int
    measure_weights_used: dict[str, int]
    source: str
    generated_at: str
