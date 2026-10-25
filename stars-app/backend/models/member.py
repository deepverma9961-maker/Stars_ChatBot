from pydantic import BaseModel
from .common import Channel, GapStatus


class MemberGapRow(BaseModel):
    member_key: str
    display_name: str
    age: int
    propensity_score: float
    measure_code: str
    measure_name: str
    gap_status: GapStatus
    last_contact: str
    recommended_channel: Channel
    pcp_name: str
    campaign_name: str | None = None


class MemberGapPage(BaseModel):
    items: list[MemberGapRow]
    total: int
    page: int
    page_size: int


class MemberClinicalEvent(BaseModel):
    event_date: str
    event_type: str
    description: str
    provider: str


class MemberMedication(BaseModel):
    drug_name: str
    ndc: str
    days_supply: int
    last_fill: str
    adherent: bool


class MemberProfile(BaseModel):
    member_key: str
    display_name: str
    age: int
    gender: str
    plan_name: str
    contract_id: str
    dual_eligible: bool
    lis_flag: bool
    utilization_segment: str
    propensity_score: float
    open_gaps: list[MemberGapRow]
    clinical_events: list[MemberClinicalEvent]
    medications: list[MemberMedication]
