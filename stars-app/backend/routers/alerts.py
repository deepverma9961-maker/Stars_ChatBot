from fastapi import APIRouter
from ..models.alert import AlertItem, AlertsResponse, PriorityItem
from ..db import query

router = APIRouter(tags=["alerts"])

_ALERTS_FALLBACK = [
    AlertItem(alert_id="a1", severity="critical", title="COL Below 4-Star Threshold", body="Colorectal Cancer Screening at 66.3% — 1.7 pts below 4-star cutoff. 5,672 gaps open.", meta="5,672 open gaps", measure_code="COL", cta_label="Launch Campaign", cta_page="simulator"),
    AlertItem(alert_id="a2", severity="critical", title="KED Critical Gap Volume", body="Kidney Health Evaluation at 63.7% with 4,123 open gaps. Requires immediate outreach.", meta="4,123 open gaps", measure_code="KED", cta_label="View Members", cta_page="members"),
    AlertItem(alert_id="a3", severity="critical", title="AMM Trending Downward", body="Follow-up after ED Visit dropped 1.2% this quarter. 3,892 gaps remain open.", meta="↓ 1.2% QoQ", measure_code="AMM", cta_label="Launch Campaign", cta_page="simulator"),
    AlertItem(alert_id="a4", severity="warning", title="CBP Near 4-Star Threshold", body="Controlling Blood Pressure at 67.8% — 2.2 pts from 4-star cutoff.", meta="67.8% current rate", measure_code="CBP", cta_label="View HEDIS", cta_page="hedis"),
    AlertItem(alert_id="a5", severity="warning", title="CAHPS Customer Service Score Declining", body="Customer Service composite at 74.6%, below plan benchmark of 78%.", meta="74.6% composite", measure_code=None, cta_label="View CAHPS", cta_page="cahps"),
    AlertItem(alert_id="a6", severity="info", title="MRP Outperforming Target", body="Medication Reconciliation Post-Discharge at 88.4% — 2.4 pts above target.", meta="88.4% current rate", measure_code="MRP", cta_label=None, cta_page=None),
    AlertItem(alert_id="a7", severity="info", title="Q2 Snapshot Window Opens in 83 Days", body="Current performance locks in 83 days. Focus outreach on red measures now.", meta="83 days remaining", measure_code=None, cta_label="Run Simulator", cta_page="simulator"),
]

_PRIORITY_FALLBACK = [
    PriorityItem(measure_code="COL", measure_name="Colorectal Cancer Screening", current_rate=66.3, target_rate=68.0, gap=1.7, priority_score=95, owner="Clinical Quality"),
    PriorityItem(measure_code="KED", measure_name="Kidney Health Evaluation", current_rate=63.7, target_rate=65.0, gap=1.3, priority_score=91, owner="Clinical Quality"),
    PriorityItem(measure_code="AMM", measure_name="Follow-up after ED Visit", current_rate=61.4, target_rate=64.0, gap=2.6, priority_score=88, owner="Care Management"),
    PriorityItem(measure_code="OMW", measure_name="Osteoporosis Management", current_rate=58.9, target_rate=62.0, gap=3.1, priority_score=82, owner="Clinical Quality"),
    PriorityItem(measure_code="CBP", measure_name="Controlling Blood Pressure", current_rate=67.8, target_rate=70.0, gap=2.2, priority_score=78, owner="Clinical Quality"),
]


@router.get("/alerts", response_model=AlertsResponse)
def get_alerts():
    try:
        rows = query("""
            SELECT a.alert_id, a.severity, a.alert_title AS title, a.alert_body AS body,
                   a.alert_meta AS meta, a.measure_code, a.cta_label, a.cta_page
            FROM aiagenticdemo.stars_gold.gold_alert_priority a
            WHERE a.is_active = true
            ORDER BY CASE a.severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END,
                     a.priority_score DESC
            LIMIT 20
        """)
        alerts = [AlertItem(**r) for r in rows] if rows else _ALERTS_FALLBACK
    except Exception:
        alerts = _ALERTS_FALLBACK

    return AlertsResponse(alerts=alerts, priority_board=_PRIORITY_FALLBACK)
