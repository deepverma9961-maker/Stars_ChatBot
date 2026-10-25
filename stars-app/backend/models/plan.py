from pydantic import BaseModel


class PlanSummary(BaseModel):
    contract_id: str
    plan_name: str
    state: str
    enrollment: int
    py_rating: float
    projected_rating: float
    hedis_rating: float
    cahps_rating: float
    hos_rating: float
    partd_rating: float
    star_gap_to_4: float
    bonus_eligible: bool


class DomainScore(BaseModel):
    domain: str
    rating: float
    on_track_count: int
    total_count: int
    critical_count: int


class HistoricalRating(BaseModel):
    year: str
    rating: float


class PlanDetail(PlanSummary):
    historical_ratings: list[HistoricalRating]
    domain_scores: list[DomainScore]


class StarSummary(BaseModel):
    total_plans: int
    total_enrollment: int
    above_4star_count: int
    above_4star_pct: float
    avg_star_rating: float
    measurement_year: int
