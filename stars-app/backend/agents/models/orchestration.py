from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Literal
from .cohort import CohortResponse
from .nba import NBAResponse
from .communication import CommunicationResponse


class PipelineStage(str, Enum):
    prioritization = "prioritization"
    nba = "nba"
    communication = "communication"
    completed = "completed"
    failed = "failed"
    awaiting_approval = "awaiting_approval"


class CampaignConfig(BaseModel):
    campaign_name: str = "Auto Campaign"
    contract_id: str = "H3312"
    measure_code: Optional[str] = None
    gap_statuses: list[str] = Field(default=["Open", "Partial", "Borderline"])
    propensity_tiers: list[str] = Field(default=["high", "medium", "low"])
    max_members: int = Field(default=200, ge=1, le=1000)
    budget_per_member: Optional[float] = None
    channels: list[str] = Field(default=["Call", "SMS", "Email"])
    plan_name: str = "Health Plan Advantage Premier"
    mode: Literal["auto", "human_in_loop"] = "human_in_loop"
    measurement_year: int = 2025


class PipelineState(BaseModel):
    campaign_id: str
    campaign_name: str
    stage: PipelineStage
    config: CampaignConfig
    cohort_result: Optional[CohortResponse] = None
    nba_result: Optional[NBAResponse] = None
    communication_result: Optional[CommunicationResponse] = None
    created_at: str
    updated_at: str
    error: Optional[str] = None


class PipelineSummary(BaseModel):
    campaign_id: str
    campaign_name: str
    stage: str
    total_members: int
    total_actions: int
    total_sent: int
    estimated_closures: int
    estimated_cost: float
    created_at: str


class ApprovalRequest(BaseModel):
    approved: bool
    excluded_member_keys: list[str] = Field(default_factory=list)
