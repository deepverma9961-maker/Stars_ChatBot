from pydantic import BaseModel, Field
from typing import Literal, Optional


class GenerateMessageRequest(BaseModel):
    channel: Literal["SMS", "Email", "Call"]
    measure_code: str = ""
    measure_name: str = ""
    gap_status: str = "Open"
    days_open: int = 0
    member_name: str = ""
    age: int = 0
    plan_name: str = "your health plan"
    prior_outreach_count: int = 0
    # When true, the LLM is asked to produce [Name] and [Measure] tokens so the
    # body can be reused across many recipients (batch SMS / Email path).
    use_placeholders: bool = False


class GenerateMessageResponse(BaseModel):
    body: str
    subject: Optional[str] = None
    source: Literal["ai", "fallback"]
    model: Optional[str] = None
