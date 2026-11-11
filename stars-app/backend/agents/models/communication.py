from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from .nba import RecommendedAction


class CommunicationRequest(BaseModel):
    actions: list[RecommendedAction]
    campaign_name: str = ""
    plan_name: str = "Health Plan Advantage Premier"
    dry_run: bool = False
    batch_size: int = Field(default=25, ge=1, le=100)


class MessageDeliveryResult(BaseModel):
    member_key: str
    display_name: str
    channel: str
    message_body: str
    message_subject: Optional[str] = None
    message_source: str
    delivery_status: str
    delivery_detail: str
    contact_used: str
    cost_estimate: float


class CommunicationResponse(BaseModel):
    results: list[MessageDeliveryResult]
    total_sent: int
    total_failed: int
    total_dry_run: int
    campaign_name: str
    source: str
    generated_at: str
