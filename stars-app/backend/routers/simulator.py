from fastapi import APIRouter
from ..models.simulator import SimulatorConfig, SimulatorResult
from ..services.simulator_engine import run_simulation
from ..db import query

router = APIRouter(tags=["simulator"])

_MEASURE_DEFAULTS = {
    "COL": {"measure_name": "Colorectal Cancer Screening", "current_rate": 66.3, "open_gap_count": 5672},
    "CBP": {"measure_name": "Controlling Blood Pressure", "current_rate": 67.8, "open_gap_count": 4890},
    "KED": {"measure_name": "Kidney Health Evaluation", "current_rate": 63.7, "open_gap_count": 4123},
    "AMM": {"measure_name": "Follow-up after ED Visit", "current_rate": 61.4, "open_gap_count": 3892},
    "OMW": {"measure_name": "Osteoporosis Management", "current_rate": 58.9, "open_gap_count": 3445},
    "SPC": {"measure_name": "Statin Therapy – Cardiovascular", "current_rate": 69.8, "open_gap_count": 2987},
    "BCS": {"measure_name": "Breast Cancer Screening", "current_rate": 73.4, "open_gap_count": 3210},
    "HBD": {"measure_name": "Diabetes Care – Blood Sugar Controlled", "current_rate": 81.2, "open_gap_count": 2340},
    "ALL": {"measure_name": "All HEDIS Measures", "current_rate": 72.6, "open_gap_count": 34873},
}


def _get_measure_data(contract_id: str, measure_code: str | None) -> dict:
    key = measure_code or "ALL"
    fallback = _MEASURE_DEFAULTS.get(key, _MEASURE_DEFAULTS["ALL"])
    try:
        if measure_code:
            rows = query(f"""
                SELECT sc.current_rate, sc.open_gap_count, ms.measure_name
                FROM aiagenticdemo.stars_gold.gold_measure_scorecard sc
                JOIN aiagenticdemo.stars_silver.silver_measure ms ON sc.measure_key = ms.measure_key
                JOIN aiagenticdemo.stars_silver.silver_plan p ON sc.plan_key = p.plan_key
                WHERE sc.measurement_year = 2025
                  AND p.contract_id = '{contract_id}'
                  AND ms.measure_code = '{measure_code}'
                LIMIT 1
            """)
        else:
            rows = query(f"""
                SELECT AVG(sc.current_rate) AS current_rate,
                       SUM(sc.open_gap_count) AS open_gap_count,
                       'All HEDIS Measures' AS measure_name
                FROM aiagenticdemo.stars_gold.gold_measure_scorecard sc
                JOIN aiagenticdemo.stars_silver.silver_measure ms ON sc.measure_key = ms.measure_key
                JOIN aiagenticdemo.stars_silver.silver_plan p ON sc.plan_key = p.plan_key
                WHERE sc.measurement_year = 2025
                  AND p.contract_id = '{contract_id}'
                  AND ms.measure_category = 'HEDIS'
            """)
        return rows[0] if rows else fallback
    except Exception:
        return fallback


@router.post("/simulator/run", response_model=SimulatorResult)
def run_simulator(config: SimulatorConfig) -> SimulatorResult:
    measure_data = _get_measure_data(config.contract_id, config.measure_code)
    return run_simulation(config, measure_data)
