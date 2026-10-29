"""Pydantic models for chat API."""

from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, List, Optional


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
    orchestration: List[Dict[str, Any]]
    sql: Optional[str] = None
    data: List[Dict[str, Any]] = []
    data_count: int = 0
    usage: Dict[str, Any] = {}
    total_duration_ms: int = 0
