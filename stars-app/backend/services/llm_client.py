"""Databricks Foundation Model API client (OpenAI-compatible)."""

from openai import OpenAI
from ..config import settings

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        host = settings.databricks_host.rstrip("/")
        _client = OpenAI(
            api_key=settings.databricks_token,
            base_url=f"{host}/serving-endpoints",
        )
    return _client


DEFAULT_MODEL = "databricks-meta-llama-3-3-70b-instruct"


def chat_completion(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.1,
    max_tokens: int = 2048,
) -> dict:
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    choice = resp.choices[0]
    return {
        "content": choice.message.content,
        "usage": {
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
            "total_tokens": resp.usage.total_tokens,
        },
    }
