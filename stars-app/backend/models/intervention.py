from pydantic import BaseModel


class InterventionRow(BaseModel):
    intervention_id: str
    intervention_name: str
    measure_code: str
    measure_name: str
    owner_department: str
    expected_lift_pct: float
    status: str
    due_date: str
    member_count: int


class TeamViewRow(BaseModel):
    department: str
    leader: str
    measures_owned: list[str]
    on_track_count: int
    at_risk_count: int
    critical_count: int
    action_status: str
    next_action: str
