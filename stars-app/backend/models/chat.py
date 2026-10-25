"""Pydantic models for chat API."""

from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class OrchestrationStep(BaseModel):
    step: str
    status: str
    duration_ms: int = 0
    model: str = ""


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    orchestration: list[dict]
    sql: Optional[str] = None
    data: list[dict] = []
    data_count: int = 0
    usage: dict = {}
    total_duration_ms: int = 0
