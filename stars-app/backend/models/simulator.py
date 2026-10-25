from pydantic import BaseModel
from .common import Channel, Incentive, GapStatus


class SimulatorConfig(BaseModel):
    contract_id: str = "H3312"
    measure_code: str | None = None
    gap_statuses: list[GapStatus] = ["Open", "Partial", "Borderline"]
    propensity_tiers: list[str] = ["high", "medium", "low"]
    channels: list[Channel] = ["Call", "SMS", "Email"]
    incentive: Incentive = "None"
    suppressions: dict[str, bool] = {
        "recently_contacted": True,
        "opted_out": True,
        "already_closed": True,
    }


class WaterfallWeek(BaseModel):
    label: str
    outreach_count: int
    estimated_closures: int
    cumulative_compliance: float


class SegmentRow(BaseModel):
    label: str
    members: int
    channel: str
    incentive: str
    estimated_closures: int
    closure_rate_pct: int
    estimated_cost: int


class SimulatorResult(BaseModel):
    net_pool: int
    estimated_closures: int
    projected_rate: float
    lift: float
    eligible_members: int
    measure_name: str
    measure_pct: float
    channel_mix: dict[str, int]
    waterfall: list[WaterfallWeek]
    segments: list[SegmentRow]
