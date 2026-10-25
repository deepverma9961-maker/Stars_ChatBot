from pydantic import BaseModel


class AlertItem(BaseModel):
    alert_id: str
    severity: str
    title: str
    body: str
    meta: str | None = None
    measure_code: str | None = None
    cta_label: str | None = None
    cta_page: str | None = None


class PriorityItem(BaseModel):
    measure_code: str
    measure_name: str
    current_rate: float
    target_rate: float
    gap: float
    priority_score: int
    owner: str


class AlertsResponse(BaseModel):
    alerts: list[AlertItem]
    priority_board: list[PriorityItem]
