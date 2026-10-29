"""Databricks Foundation Model API client (OpenAI-compatible)."""

import logging
from ..config import settings

logger = logging.getLogger("llm_client")
_client = None


def get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        host = settings.databricks_host.rstrip("/")
        _client = OpenAI(
            api_key=settings.databricks_token,
            base_url=f"{host}/serving-endpoints",
        )
    return _client


DEFAULT_MODEL = "databricks-meta-llama-3-3-70b-instruct"
FALLBACK_MODEL = "databricks-llama-4-maverick"


def chat_completion(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.1,
    max_tokens: int = 2048,
) -> dict:
    client = get_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        logger.warning("LLM call failed with model %s: %s — trying fallback", model, e)
        if model != FALLBACK_MODEL:
            try:
                resp = client.chat.completions.create(
                    model=FALLBACK_MODEL,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as e2:
                logger.error("Fallback model also failed: %s", e2)
                raise RuntimeError(f"LLM API error: {str(e)[:200]}") from e2
        else:
            raise RuntimeError(f"LLM API error: {str(e)[:200]}") from e
    choice = resp.choices[0]
    return {
        "content": choice.message.content,
        "usage": {
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
            "total_tokens": resp.usage.total_tokens,
        },
    }
