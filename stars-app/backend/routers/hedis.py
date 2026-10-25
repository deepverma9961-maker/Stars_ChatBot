from fastapi import APIRouter, Query
from ..models.hedis import HedisMeasure
from ..models.common import Status
from ..db import query

router = APIRouter(tags=["hedis"])

# Reference data from stars_v2.html hedisData array
_HEDIS_H3312 = [
    {"measure_code": "HBD", "measure_name": "Diabetes Care – Blood Sugar Controlled", "weight": "3x", "current_rate": 81.2, "open_gap_count": 2340, "status": "green", "target_rate": 80.0, "projected_rate": 83.1, "part": "C"},
    {"measure_code": "CBP", "measure_name": "Controlling Blood Pressure", "weight": "3x", "current_rate": 67.8, "open_gap_count": 4890, "status": "yellow", "target_rate": 70.0, "projected_rate": 70.2, "part": "C"},
    {"measure_code": "PCR", "measure_name": "Plan All‑Cause Readmissions", "weight": "3x", "current_rate": 79.1, "open_gap_count": 1124, "status": "green", "target_rate": 75.0, "projected_rate": 80.4, "part": "C"},
    {"measure_code": "BCS", "measure_name": "Breast Cancer Screening", "weight": "1x", "current_rate": 73.4, "open_gap_count": 3210, "status": "yellow", "target_rate": 72.0, "projected_rate": 75.8, "part": "C"},
    {"measure_code": "COL", "measure_name": "Colorectal Cancer Screening", "weight": "1x", "current_rate": 66.3, "open_gap_count": 5672, "status": "red", "target_rate": 68.0, "projected_rate": 68.9, "part": "C"},
    {"measure_code": "COA_MR", "measure_name": "Care for Older Adults – Medication Review", "weight": "1x", "current_rate": 84.5, "open_gap_count": 890, "status": "green", "target_rate": 82.0, "projected_rate": 86.2, "part": "C"},
    {"measure_code": "COA_PA", "measure_name": "Care for Older Adults – Pain Assessment", "weight": "1x", "current_rate": 76.2, "open_gap_count": 2156, "status": "yellow", "target_rate": 74.0, "projected_rate": 78.1, "part": "C"},
    {"measure_code": "OMW", "measure_name": "Osteoporosis Management in Women", "weight": "1x", "current_rate": 58.9, "open_gap_count": 3445, "status": "red", "target_rate": 62.0, "projected_rate": 61.7, "part": "C"},
    {"measure_code": "EED", "measure_name": "Diabetes Care – Eye Exam", "weight": "1x", "current_rate": 71.3, "open_gap_count": 1876, "status": "yellow", "target_rate": 70.0, "projected_rate": 73.5, "part": "C"},
    {"measure_code": "KED", "measure_name": "Kidney Health Evaluation for Patients with Diabetes", "weight": "1x", "current_rate": 63.7, "open_gap_count": 4123, "status": "red", "target_rate": 65.0, "projected_rate": 66.4, "part": "C"},
    {"measure_code": "MRP", "measure_name": "Medication Reconciliation Post-Discharge", "weight": "1x", "current_rate": 88.4, "open_gap_count": 678, "status": "green", "target_rate": 86.0, "projected_rate": 89.7, "part": "C"},
    {"measure_code": "SPC", "measure_name": "Statin Therapy for Patients with Cardiovascular Disease", "weight": "1x", "current_rate": 69.8, "open_gap_count": 2987, "status": "yellow", "target_rate": 68.0, "projected_rate": 72.1, "part": "C"},
    {"measure_code": "TRC", "measure_name": "Transitions of Care", "weight": "1x", "current_rate": 72.1, "open_gap_count": 1654, "status": "yellow", "target_rate": 70.0, "projected_rate": 74.3, "part": "C"},
    {"measure_code": "AMM", "measure_name": "Follow‑up after ED Visit for People with Multiple High‑Risk Chronic Conditions", "weight": "1x", "current_rate": 61.4, "open_gap_count": 3892, "status": "red", "target_rate": 64.0, "projected_rate": 64.2, "part": "C"},
]


@router.get("/hedis-measures", response_model=list[HedisMeasure])
def get_hedis_measures(
    contract_id: str = Query("H3312"),
    color_filter: str = Query("all"),
    sort: str = Query("rate_asc"),
):
    try:
        rows = query(
            f"""
            SELECT ms.measure_code, ms.measure_name,
                   CASE WHEN ms.measure_weight = 3 THEN '3x' ELSE '1x' END AS weight,
                   sc.current_rate, sc.open_gap_count, sc.measure_status AS status,
                   sc.target_rate, sc.projected_rate, ms.part
            FROM aiagenticdemo.stars_gold.gold_measure_scorecard sc
            JOIN aiagenticdemo.stars_silver.silver_measure ms ON sc.measure_key = ms.measure_key
            JOIN aiagenticdemo.stars_silver.silver_plan p ON sc.plan_key = p.plan_key
            WHERE sc.measurement_year = 2025
              AND p.contract_id = '{contract_id}'
              AND ms.measure_category = 'HEDIS'
            ORDER BY sc.current_rate {'ASC' if sort == 'rate_asc' else 'DESC'}
            """
        )
        data = rows if rows else _HEDIS_H3312
    except Exception:
        data = _HEDIS_H3312

    measures = [HedisMeasure(**r) for r in data]
    if color_filter != "all":
        measures = [m for m in measures if m.status == color_filter]
    if sort == "rate_asc":
        measures.sort(key=lambda m: m.current_rate)
    elif sort == "rate_desc":
        measures.sort(key=lambda m: m.current_rate, reverse=True)
    return measures
