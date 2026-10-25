"""Chat API router for StarPulse AI Assistant."""

import uuid
import time
import logging
from datetime import datetime, timezone
from fastapi import APIRouter

from ..models.chat import ChatRequest, ChatResponse
from ..services.chat_agent import run_pipeline

logger = logging.getLogger("chat")
router = APIRouter(tags=["chat"])

# In-memory conversation store (replace with DB for production)
_conversations: dict[str, list[dict]] = {}
_analytics: dict = {
    "total_queries": 0,
    "total_tokens": 0,
    "total_cost": 0.0,
    "total_response_time_ms": 0,
    "queries_by_date": {},
    "agent_usage": {},
}

# Databricks Foundation Model pricing (approx $/1M tokens)
_PRICE_INPUT = 0.75
_PRICE_OUTPUT = 2.10


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    conv_id = req.conversation_id or str(uuid.uuid4())
    if conv_id not in _conversations:
        _conversations[conv_id] = []

    history = _conversations[conv_id]
    history.append({
        "role": "user",
        "content": req.message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    result = run_pipeline(req.message, history)

    history.append({
        "role": "assistant",
        "content": result["response"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "orchestration": result["orchestration"],
        "sql": result.get("sql"),
    })

    # Update analytics
    usage = result.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    cost = (input_tokens * _PRICE_INPUT + output_tokens * _PRICE_OUTPUT) / 1_000_000

    _analytics["total_queries"] += 1
    _analytics["total_tokens"] += usage.get("total_tokens", 0)
    _analytics["total_cost"] += cost
    _analytics["total_response_time_ms"] += result.get("total_duration_ms", 0)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    _analytics["queries_by_date"][today] = _analytics["queries_by_date"].get(today, 0) + 1

    for step in result.get("orchestration", []):
        agent = step.get("step", "unknown")
        _analytics["agent_usage"][agent] = _analytics["agent_usage"].get(agent, 0) + 1

    return ChatResponse(
        conversation_id=conv_id,
        response=result["response"],
        orchestration=result["orchestration"],
        sql=result.get("sql"),
        data=result.get("data", []),
        data_count=result.get("data_count", 0),
        usage=usage,
        total_duration_ms=result.get("total_duration_ms", 0),
    )


@router.get("/chat/history")
def get_conversations():
    convs = []
    for conv_id, messages in _conversations.items():
        if messages:
            first_user = next((m["content"][:80] for m in messages if m["role"] == "user"), "New Chat")
            convs.append({
                "id": conv_id,
                "title": first_user,
                "message_count": len(messages),
                "last_updated": messages[-1].get("timestamp", ""),
            })
    convs.sort(key=lambda c: c["last_updated"], reverse=True)
    return convs


@router.get("/chat/history/{conversation_id}")
def get_conversation(conversation_id: str):
    messages = _conversations.get(conversation_id, [])
    return {"conversation_id": conversation_id, "messages": messages}


@router.delete("/chat/history/{conversation_id}")
def delete_conversation(conversation_id: str):
    _conversations.pop(conversation_id, None)
    return {"deleted": True}


@router.get("/chat/analytics")
def get_analytics():
    total_q = _analytics["total_queries"] or 1
    avg_response = _analytics["total_response_time_ms"] / total_q
    return {
        "tokens_used": _analytics["total_tokens"],
        "est_cost": round(_analytics["total_cost"], 4),
        "queries": _analytics["total_queries"],
        "avg_response_ms": round(avg_response),
        "cost_per_query": round(_analytics["total_cost"] / total_q, 4),
        "queries_by_date": _analytics["queries_by_date"],
        "agent_usage": _analytics["agent_usage"],
        "input_cost": round(_analytics["total_tokens"] * _PRICE_INPUT / 1_000_000, 4),
        "output_cost": round(_analytics["total_tokens"] * _PRICE_OUTPUT / 1_000_000, 4),
    }
