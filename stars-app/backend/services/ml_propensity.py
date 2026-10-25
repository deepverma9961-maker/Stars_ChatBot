"""Thin wrapper around the gold_member_closure_propensity table.

Reads the per-(member × measure × channel × incentive) predicted closure
probability produced by `notebooks/gold/15_ml_closure_propensity.py`. When the
table is missing or Databricks is unreachable, callers fall back to the static
lookup constants in `simulator_engine.py` — no exceptions raised.
"""
from __future__ import annotations

from functools import lru_cache
from ..db import query, table_exists
from ..config import settings

_TABLE = "aiagenticdemo.stars_gold.gold_member_closure_propensity"

# Static fallback (mirrors simulator_engine.py constants)
_FALLBACK_RATES = {
    ("Call",  "None"):     0.28, ("Call",  "$25 card"): 0.32, ("Call",  "$50 card"): 0.36,
    ("SMS",   "None"):     0.22, ("SMS",   "$25 card"): 0.26, ("SMS",   "$50 card"): 0.30,
    ("Email", "None"):     0.12, ("Email", "$25 card"): 0.16, ("Email", "$50 card"): 0.20,
}


def is_live() -> bool:
    """Return True iff the gold propensity table exists and has rows for 2025."""
    if not settings.databricks_host:
        return False
    try:
        if not table_exists(_TABLE):
            return False
        rows = query(f"SELECT COUNT(*) AS n FROM {_TABLE} WHERE measurement_year = 2025")
        return bool(rows and rows[0]["n"] > 0)
    except Exception:
        return False


@lru_cache(maxsize=128)
def mean_closure_rate(measure_code: str, channel: str, incentive: str) -> float:
    """Mean predicted closure probability for the given (measure, channel, incentive).

    Falls back to the static lookup if the table is empty / unreachable.
    Result is a float in [0, 1].
    """
    fallback = _FALLBACK_RATES.get((channel, incentive), 0.22)
    if not is_live():
        return fallback
    try:
        rows = query(
            f"""
            SELECT AVG(p_close) AS p
            FROM {_TABLE}
            WHERE measurement_year = 2025
              AND measure_code = '{measure_code}'
              AND channel      = '{channel}'
              AND incentive    = '{incentive}'
            """
        )
        if rows and rows[0]["p"] is not None:
            return float(rows[0]["p"])
    except Exception:
        pass
    return fallback


def reset_cache() -> None:
    """Clear the in-process cache so the next call reflects a fresh table read."""
    mean_closure_rate.cache_clear()
