from pydantic import BaseModel


class CahpsComposite(BaseModel):
    composite_code: str
    composite_name: str
    current_pct: float
    status: str
    weight: str = "2x"
    part: str = "C"


class CahpsOverviewResponse(BaseModel):
    contract_id: str
    current_rating: float
    projected_rating: float
    gap_to_4_star: float
    days_remaining: int
    qbp_at_stake: float
    composites: list[CahpsComposite]
