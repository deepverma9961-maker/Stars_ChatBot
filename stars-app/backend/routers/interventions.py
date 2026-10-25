from fastapi import APIRouter
from ..models.intervention import InterventionRow
from ..db import query

router = APIRouter(tags=["interventions"])

_FALLBACK = [
    InterventionRow(intervention_id="i1", intervention_name="COL Reminder Letter Campaign", measure_code="COL", measure_name="Colorectal Cancer Screening", owner_department="Clinical Quality", expected_lift_pct=3.2, status="Active", due_date="2025-07-31", member_count=5672),
    InterventionRow(intervention_id="i2", intervention_name="CBP PCP Alert Program", measure_code="CBP", measure_name="Controlling Blood Pressure", owner_department="Network", expected_lift_pct=2.8, status="Active", due_date="2025-08-15", member_count=4890),
    InterventionRow(intervention_id="i3", intervention_name="KED Lab Order Nudge", measure_code="KED", measure_name="Kidney Health Evaluation", owner_department="Clinical Quality", expected_lift_pct=2.4, status="Planned", due_date="2025-09-01", member_count=4123),
    InterventionRow(intervention_id="i4", intervention_name="AMM Care Management Referral", measure_code="AMM", measure_name="Follow-up after ED Visit", owner_department="Care Management", expected_lift_pct=4.1, status="Active", due_date="2025-07-15", member_count=3892),
    InterventionRow(intervention_id="i5", intervention_name="OMW Fracture Risk Outreach", measure_code="OMW", measure_name="Osteoporosis Management", owner_department="Clinical Quality", expected_lift_pct=2.1, status="Planned", due_date="2025-09-30", member_count=3445),
]


@router.get("/interventions", response_model=list[InterventionRow])
def get_interventions():
    try:
        rows = query("""
            SELECT i.intervention_id, i.intervention_name, ms.measure_code, ms.measure_name,
                   i.owner_department, i.expected_lift_pct,
                   i.intervention_status AS status,
                   CAST(i.due_date AS STRING) AS due_date,
                   i.target_member_count AS member_count
            FROM aiagenticdemo.stars_gold.gold_intervention_hub i
            JOIN aiagenticdemo.stars_silver.silver_measure ms ON i.measure_key = ms.measure_key
            WHERE i.measurement_year = 2025
            ORDER BY i.expected_lift_pct DESC
            LIMIT 25
        """)
        return [InterventionRow(**r) for r in rows] if rows else _FALLBACK
    except Exception:
        return _FALLBACK
