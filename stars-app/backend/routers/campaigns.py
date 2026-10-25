from fastapi import APIRouter, Query
from ..models.campaign import CampaignRow, CampaignResponse, ROISummary
from ..db import query

router = APIRouter(tags=["campaigns"])

_CAMPAIGNS_FALLBACK = [
    {"campaign_name": "COL Outreach Wave 1", "measure_code": "COL", "channel": "Call", "member_count": 312, "projected_closures": 87, "actual_closures": 94, "lift_pct": "+3.1%", "cost_str": "$6,864", "roi_str": "4.8x", "status": "Completed"},
    {"campaign_name": "SPC SMS Blitz", "measure_code": "SPC", "channel": "SMS", "member_count": 248, "projected_closures": 55, "actual_closures": 61, "lift_pct": "+2.4%", "cost_str": "$992", "roi_str": "6.2x", "status": "Completed"},
    {"campaign_name": "AMM Email + Incentive", "measure_code": "AMM", "channel": "Email", "member_count": 189, "projected_closures": 23, "actual_closures": None, "lift_pct": "+1.8%", "cost_str": "$378", "roi_str": "—", "status": "Active"},
    {"campaign_name": "FLU Rapid Response", "measure_code": "FLU", "channel": "Call", "member_count": 445, "projected_closures": 124, "actual_closures": 118, "lift_pct": "+4.2%", "cost_str": "$9,790", "roi_str": "3.9x", "status": "Completed"},
    {"campaign_name": "CDC Priority Call", "measure_code": "HBD", "channel": "Call", "member_count": 167, "projected_closures": 47, "actual_closures": None, "lift_pct": "+2.1%", "cost_str": "$3,674", "roi_str": "—", "status": "Active"},
    {"campaign_name": "KED Targeted SMS", "measure_code": "KED", "channel": "SMS", "member_count": 203, "projected_closures": 45, "actual_closures": 48, "lift_pct": "+2.8%", "cost_str": "$812", "roi_str": "5.7x", "status": "Completed"},
    {"campaign_name": "CBP High-Risk Wave", "measure_code": "CBP", "channel": "Call", "member_count": 289, "projected_closures": 81, "actual_closures": None, "lift_pct": "+3.4%", "cost_str": "$6,358", "roi_str": "—", "status": "Active"},
]


@router.get("/campaigns", response_model=CampaignResponse)
def get_campaigns(
    status: str | None = Query(None),
    measure_code: str | None = Query(None),
):
    try:
        where = "c.measurement_year = 2025"
        if status and status != "all":
            where += f" AND c.campaign_status = '{status}'"
        if measure_code:
            where += f" AND c.measure_code = '{measure_code}'"
        rows = query(f"""
            SELECT c.campaign_name, c.measure_code, c.primary_channel AS channel,
                   c.member_count, c.projected_closures, c.actual_closures,
                   CONCAT('+', CAST(ROUND(c.lift_pct,1) AS STRING), '%') AS lift_pct,
                   CONCAT('$', FORMAT_NUMBER(c.total_cost,0)) AS cost_str,
                   CASE WHEN c.roi_multiplier IS NULL THEN '—'
                        ELSE CONCAT(CAST(ROUND(c.roi_multiplier,1) AS STRING), 'x') END AS roi_str,
                   c.campaign_status AS status
            FROM aiagenticdemo.stars_gold.gold_campaign_performance c
            WHERE {where}
            ORDER BY c.campaign_start_date DESC
            LIMIT 50
        """)
        data = rows if rows else _CAMPAIGNS_FALLBACK
    except Exception:
        data = _CAMPAIGNS_FALLBACK

    items = [CampaignRow(**r) for r in data]
    if status and status != "all":
        items = [i for i in items if i.status == status]
    if measure_code:
        items = [i for i in items if i.measure_code == measure_code]

    completed = [i for i in items if i.status == "Completed" and i.actual_closures]
    total_closures = sum(i.actual_closures or 0 for i in completed)
    total_members = sum(i.member_count for i in items)
    roi_vals = [float(i.roi_str.replace("x", "")) for i in items if i.roi_str != "—"]
    avg_roi = f"{sum(roi_vals)/len(roi_vals):.1f}x" if roi_vals else "—"

    cost_vals = [int(i.cost_str.replace("$", "").replace(",", "")) for i in items if i.cost_str != "—"]
    total_cost = f"${sum(cost_vals):,}"

    summary = ROISummary(
        total_members=total_members,
        total_closures=total_closures,
        avg_roi=avg_roi,
        total_cost=total_cost,
    )
    return CampaignResponse(items=items, summary=summary)
