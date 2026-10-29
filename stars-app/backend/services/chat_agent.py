"""Agent orchestration pipeline for StarPulse AI Assistant."""
from __future__ import annotations

import json
import time
import logging
import traceback
from typing import Optional, List, Dict

try:
    from .llm_client import chat_completion, DEFAULT_MODEL
except ImportError:
    chat_completion = None
    DEFAULT_MODEL = "databricks-meta-llama-3-3-70b-instruct"

try:
    from ..db import query as db_query
except ImportError:
    db_query = None

from ..config import settings

logger = logging.getLogger("chat_agent")

TABLE_SCHEMAS = f"""
Available tables in Databricks catalog '{settings.catalog}':

1. {settings.gold}.gold_star_rating_summary
   - contract_id (string): CMS contract ID e.g. H0001
   - organization_name (string): Health plan organization name
   - measurement_year (int): Year of measurement (2022-2027)
   - overall_star_rating (float): Overall CMS star rating (1-5)
   - part_c_star_rating (float): Part C star rating
   - part_d_star_rating (float): Part D star rating
   - domain_scores (string): JSON with domain-level scores
   - total_enrollment (int): Total enrolled members

2. {settings.gold}.gold_measure_scorecard
   - contract_id (string): CMS contract ID
   - measure_id (string): HEDIS measure ID e.g. C01, D01
   - measure_name (string): Full measure name
   - measurement_year (int): Year
   - star_rating (int): Star rating for this measure (1-5)
   - numerator (int): Numerator count
   - denominator (int): Denominator count
   - rate (float): Performance rate (0-100)
   - domain (string): CMS domain category
   - part (string): 'C' or 'D'
   - weight (float): CMS weight for star calculation

3. {settings.gold}.gold_member_gap
   - member_id (string): Member ID
   - contract_id (string): CMS contract ID
   - measure_id (string): HEDIS measure ID
   - measure_name (string): Full measure name
   - gap_status (string): 'open' or 'closed'
   - days_remaining (int): Days remaining to close gap
   - last_service_date (string): Date of last relevant service
   - provider_name (string): Assigned provider

4. {settings.gold}.gold_cahps_overview
   - contract_id (string): CMS contract ID
   - survey_category (string): CAHPS survey category
   - score (float): Survey score (0-100)
   - measurement_year (int): Year
   - benchmark (float): National benchmark
   - status (string): 'above', 'at', 'below' benchmark

5. {settings.gold}.gold_alert_priority
   - contract_id (string): CMS contract ID
   - alert_type (string): Type of alert
   - severity (string): 'critical', 'warning', 'info'
   - message (string): Alert description
   - created_date (string): When alert was created

6. {settings.silver}.silver_plan
   - contract_id (string): CMS contract ID
   - plan_name (string): Plan name
   - organization_name (string): Organization name
   - state (string): State abbreviation
   - plan_type (string): HMO, PPO, etc.
   - snp_type (string): Special Needs Plan type

7. {settings.silver}.silver_member
   - member_id (string): Member ID
   - contract_id (string): CMS contract ID
   - first_name (string): First name
   - last_name (string): Last name
   - age (int): Member age
   - gender (string): M/F
   - risk_score (float): HCC risk score

8. {settings.silver}.silver_measure
   - measure_id (string): Measure ID
   - measure_name (string): Full measure name
   - domain (string): CMS domain
   - part (string): 'C' or 'D'
   - description (string): Measure description
"""

ROUTER_SYSTEM = """You are a query router for StarPulse Medicare Stars platform.
Classify the user's question into exactly one category:
- "nl2sql" — needs data from Databricks tables (member lookups, measure rates, star ratings, enrollment, gaps, CAHPS scores, alerts)
- "general" — general Medicare Stars knowledge, platform usage, or conversational

Respond with ONLY a JSON object: {"category": "nl2sql"} or {"category": "general"}"""

NL2SQL_SYSTEM = f"""You are an expert SQL analyst for Medicare Stars data.
Given a natural language question, generate a Databricks SQL query.

{TABLE_SCHEMAS}

Rules:
- Use ONLY the tables and columns listed above.
- Always qualify table names with full catalog.schema.table path.
- Use measurement_year filters when the question mentions a specific year; default to the latest available year (2026) if none specified.
- LIMIT results to 50 rows max unless the user asks for more.
- For aggregations, include meaningful column aliases.
- Return ONLY a JSON object: {{"sql": "SELECT ...", "explanation": "Brief explanation of what the query does"}}
- If the question cannot be answered from these tables, return: {{"sql": null, "explanation": "Reason it cannot be answered"}}"""

RESPONSE_SYSTEM = """You are StarPulse AI Assistant, an expert in Medicare Stars quality measures, HEDIS, CAHPS, and CMS star ratings.

Given the user's question and the SQL query results, provide a clear, professional answer.

Format your response as:
1. A direct answer to the question
2. Key Insights (bulleted list of 3-5 important observations)
3. If relevant, suggest 2-3 follow-up questions the user might want to ask

Keep responses concise and data-driven. Use specific numbers from the results.
If no data was returned, explain what that means and suggest alternatives."""

JUDGE_SYSTEM = """You are an LLM quality judge evaluating an AI assistant's response about Medicare Stars data.

Score the response on these 8 dimensions (1-5 scale each):
1. Groundedness — Is the response supported by the provided data?
2. Accuracy — Are the numbers and facts correct?
3. Completeness — Does it fully answer the question?
4. Clarity — Is it easy to understand?
5. Clinical Relevance — Is it relevant to healthcare quality?
6. Actionability — Does it suggest useful next steps?
7. Conciseness — Is it appropriately brief?
8. SQL Correctness — Was the SQL query correct? (5 if no SQL needed)

Also provide 1-3 brief improvement suggestions.

Return ONLY a JSON object:
{"scores": {"groundedness": N, "accuracy": N, "completeness": N, "clarity": N, "clinical_relevance": N, "actionability": N, "conciseness": N, "sql_correctness": N}, "suggestions": ["...", "..."], "overall": N.N}"""


def _safe_json_parse(text: str) -> Optional[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                return None
    return None


def run_router(user_message: str, history: list[dict]) -> dict:
    t0 = time.time()
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM},
        {"role": "user", "content": user_message},
    ]
    result = chat_completion(messages, temperature=0.0, max_tokens=64)
    parsed = _safe_json_parse(result["content"]) or {"category": "general"}
    elapsed = round((time.time() - t0) * 1000)
    return {
        "step": "router",
        "status": "done",
        "category": parsed.get("category", "general"),
        "duration_ms": elapsed,
        "usage": result["usage"],
        "model": DEFAULT_MODEL,
    }


def run_nl2sql(user_message: str, history: list[dict]) -> dict:
    t0 = time.time()
    context_messages = []
    for msg in history[-4:]:
        context_messages.append({"role": msg["role"], "content": msg["content"]})
    messages = [
        {"role": "system", "content": NL2SQL_SYSTEM},
        *context_messages,
        {"role": "user", "content": user_message},
    ]
    result = chat_completion(messages, temperature=0.0, max_tokens=1024)
    parsed = _safe_json_parse(result["content"])
    elapsed = round((time.time() - t0) * 1000)

    sql_text = parsed.get("sql") if parsed else None
    explanation = parsed.get("explanation", "") if parsed else result["content"]

    return {
        "step": "nl2sql",
        "status": "done",
        "sql": sql_text,
        "explanation": explanation,
        "duration_ms": elapsed,
        "usage": result["usage"],
        "model": DEFAULT_MODEL,
    }


def run_databricks_query(sql_text: str) -> dict:
    t0 = time.time()
    try:
        rows = db_query(sql_text)
        elapsed = round((time.time() - t0) * 1000)
        return {
            "step": "databricks",
            "status": "done",
            "rows": rows,
            "row_count": len(rows),
            "duration_ms": elapsed,
        }
    except Exception as e:
        elapsed = round((time.time() - t0) * 1000)
        return {
            "step": "databricks",
            "status": "error",
            "error": str(e)[:300],
            "rows": [],
            "row_count": 0,
            "duration_ms": elapsed,
        }


def run_response(user_message: str, sql_result: dict, sql_text: str | None, history: list[dict]) -> dict:
    t0 = time.time()
    data_context = ""
    if sql_text:
        data_context += f"\nSQL Query executed:\n```sql\n{sql_text}\n```\n"
    if sql_result.get("rows"):
        rows_preview = sql_result["rows"][:20]
        data_context += f"\nQuery Results ({sql_result['row_count']} rows):\n```json\n{json.dumps(rows_preview, default=str, indent=2)}\n```"
    elif sql_result.get("error"):
        data_context += f"\nQuery Error: {sql_result['error']}"
    else:
        data_context += "\nNo data returned from query."

    messages = [
        {"role": "system", "content": RESPONSE_SYSTEM},
        {"role": "user", "content": f"User Question: {user_message}\n\nData Context:{data_context}"},
    ]
    result = chat_completion(messages, temperature=0.3, max_tokens=2048)
    elapsed = round((time.time() - t0) * 1000)
    return {
        "step": "response",
        "status": "done",
        "content": result["content"],
        "duration_ms": elapsed,
        "usage": result["usage"],
        "model": DEFAULT_MODEL,
    }


def run_general_response(user_message: str, history: list[dict]) -> dict:
    t0 = time.time()
    context_messages = []
    for msg in history[-6:]:
        context_messages.append({"role": msg["role"], "content": msg["content"]})
    messages = [
        {"role": "system", "content": RESPONSE_SYSTEM},
        *context_messages,
        {"role": "user", "content": user_message},
    ]
    result = chat_completion(messages, temperature=0.3, max_tokens=2048)
    elapsed = round((time.time() - t0) * 1000)
    return {
        "step": "response",
        "status": "done",
        "content": result["content"],
        "duration_ms": elapsed,
        "usage": result["usage"],
        "model": DEFAULT_MODEL,
    }


def run_judge(user_message: str, response_content: str, sql_text: str | None, rows: list) -> dict:
    t0 = time.time()
    eval_input = f"""User Question: {user_message}

AI Response: {response_content}

SQL Used: {sql_text or 'None'}

Data Returned: {json.dumps(rows[:10], default=str) if rows else 'None'}"""

    messages = [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": eval_input},
    ]
    try:
        result = chat_completion(messages, temperature=0.0, max_tokens=512)
        parsed = _safe_json_parse(result["content"])
        elapsed = round((time.time() - t0) * 1000)
        if parsed and "scores" in parsed:
            return {
                "step": "judge",
                "status": "done",
                "scores": parsed["scores"],
                "suggestions": parsed.get("suggestions", []),
                "overall": parsed.get("overall", 0),
                "duration_ms": elapsed,
                "usage": result["usage"],
                "model": DEFAULT_MODEL,
            }
        return {
            "step": "judge",
            "status": "done",
            "scores": {},
            "suggestions": [],
            "overall": 0,
            "duration_ms": elapsed,
            "usage": result["usage"],
            "model": DEFAULT_MODEL,
        }
    except Exception as e:
        logger.warning("Judge failed: %s", e)
        return {
            "step": "judge",
            "status": "error",
            "error": str(e)[:200],
            "scores": {},
            "suggestions": [],
            "overall": 0,
            "duration_ms": round((time.time() - t0) * 1000),
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": DEFAULT_MODEL,
        }


def run_pipeline(user_message: str, history: list[dict]) -> dict:
    """Run the full agent orchestration pipeline."""
    if chat_completion is None:
        raise RuntimeError("LLM client not available — openai package may not be installed")
    total_start = time.time()
    orchestration = []
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _add_usage(step_result):
        u = step_result.get("usage", {})
        total_usage["prompt_tokens"] += u.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += u.get("completion_tokens", 0)
        total_usage["total_tokens"] += u.get("total_tokens", 0)

    # Step 1: Router
    try:
        router_result = run_router(user_message, history)
    except Exception as e:
        logger.error("Router failed: %s\n%s", e, traceback.format_exc())
        router_result = {"step": "router", "status": "error", "category": "general", "duration_ms": 0, "usage": {}, "model": DEFAULT_MODEL}
    orchestration.append(router_result)
    _add_usage(router_result)
    category = router_result["category"]

    sql_text = None
    sql_result = {"rows": [], "row_count": 0}
    response_content = ""

    if category == "nl2sql":
        # Step 2: NL2SQL
        try:
            nl2sql_result = run_nl2sql(user_message, history)
        except Exception as e:
            logger.error("NL2SQL failed: %s", e)
            nl2sql_result = {"step": "nl2sql", "status": "error", "sql": None, "explanation": str(e), "duration_ms": 0, "usage": {}, "model": DEFAULT_MODEL}
        orchestration.append(nl2sql_result)
        _add_usage(nl2sql_result)
        sql_text = nl2sql_result.get("sql")

        # Step 3: Execute SQL
        if sql_text:
            sql_result = run_databricks_query(sql_text)
            orchestration.append(sql_result)

        # Step 4: Response
        try:
            resp_result = run_response(user_message, sql_result, sql_text, history)
        except Exception as e:
            logger.error("Response agent failed: %s", e)
            resp_result = {"step": "response", "status": "error", "content": "I encountered an error generating the response. Please try again.", "duration_ms": 0, "usage": {}, "model": DEFAULT_MODEL}
        orchestration.append(resp_result)
        _add_usage(resp_result)
        response_content = resp_result["content"]
    else:
        # General response (no SQL)
        try:
            resp_result = run_general_response(user_message, history)
        except Exception as e:
            logger.error("General response failed: %s", e)
            resp_result = {"step": "response", "status": "error", "content": "I encountered an error. Please try again.", "duration_ms": 0, "usage": {}, "model": DEFAULT_MODEL}
        orchestration.append(resp_result)
        _add_usage(resp_result)
        response_content = resp_result["content"]

    # Step 5: LLM Judge
    try:
        judge_result = run_judge(user_message, response_content, sql_text, sql_result.get("rows", []))
    except Exception as e:
        logger.error("Judge failed: %s", e)
        judge_result = {"step": "judge", "status": "error", "scores": {}, "suggestions": [], "overall": 0, "duration_ms": 0, "usage": {}, "model": DEFAULT_MODEL}
    orchestration.append(judge_result)
    _add_usage(judge_result)

    total_ms = round((time.time() - total_start) * 1000)

    return {
        "response": response_content,
        "orchestration": orchestration,
        "sql": sql_text,
        "data": sql_result.get("rows", [])[:50],
        "data_count": sql_result.get("row_count", 0),
        "usage": total_usage,
        "total_duration_ms": total_ms,
    }
