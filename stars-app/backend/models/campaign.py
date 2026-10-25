from pydantic import BaseModel


class CampaignRow(BaseModel):
    campaign_name: str
    measure_code: str
    channel: str
    member_count: int
    projected_closures: int
    actual_closures: int | None = None
    lift_pct: str
    cost_str: str
    roi_str: str
    status: str


class ROISummary(BaseModel):
    total_members: int
    total_closures: int
    avg_roi: str
    total_cost: str


class CampaignResponse(BaseModel):
    items: list[CampaignRow]
    summary: ROISummary
