from pydantic import BaseModel
from .common import Status


class HedisMeasure(BaseModel):
    measure_code: str
    measure_name: str
    weight: str
    current_rate: float
    open_gap_count: int
    status: Status
    target_rate: float
    projected_rate: float
    part: str = "C"
