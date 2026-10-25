from fastapi import APIRouter, Query
from ..models.plan import PlanSummary, PlanDetail, DomainScore, HistoricalRating
from ..db import query

router = APIRouter(tags=["plans"])

# Reference data from stars_v2.html for fallback
_CONTRACTS = [
    {"contract_id": "H3312", "plan_name": "Health Plan Advantage Premier", "state": "FL", "enrollment": 112_500, "py_rating": 4.0, "projected_rating": 4.0, "hedis_rating": 3.8, "cahps_rating": 4.2, "hos_rating": 4.0, "partd_rating": 4.1},
    {"contract_id": "H5521", "plan_name": "Lone Star Medicare Complete", "state": "TX", "enrollment": 98_200, "py_rating": 3.5, "projected_rating": 3.5, "hedis_rating": 3.4, "cahps_rating": 3.6, "hos_rating": 3.5, "partd_rating": 3.7},
    {"contract_id": "H2213", "plan_name": "Pacific Care Advantage Gold", "state": "CA", "enrollment": 134_800, "py_rating": 4.5, "projected_rating": 4.5, "hedis_rating": 4.6, "cahps_rating": 4.4, "hos_rating": 4.5, "partd_rating": 4.3},
    {"contract_id": "H6614", "plan_name": "Keystone Senior Plus", "state": "PA", "enrollment": 67_300, "py_rating": 4.0, "projected_rating": 4.0, "hedis_rating": 3.9, "cahps_rating": 4.1, "hos_rating": 4.0, "partd_rating": 3.8},
    {"contract_id": "H7723", "plan_name": "Empire Blue Medicare", "state": "NY", "enrollment": 89_100, "py_rating": 3.5, "projected_rating": 4.0, "hedis_rating": 3.7, "cahps_rating": 3.8, "hos_rating": 3.5, "partd_rating": 3.9},
    {"contract_id": "H8812", "plan_name": "Buckeye Health Advantage", "state": "OH", "enrollment": 54_600, "py_rating": 4.0, "projected_rating": 4.0, "hedis_rating": 4.0, "cahps_rating": 3.9, "hos_rating": 4.0, "partd_rating": 4.2},
    {"contract_id": "H9914", "plan_name": "Desert Sun Medicare Plus", "state": "AZ", "enrollment": 72_400, "py_rating": 3.5, "projected_rating": 3.5, "hedis_rating": 3.3, "cahps_rating": 3.7, "hos_rating": 3.5, "partd_rating": 3.4},
    {"contract_id": "H1045", "plan_name": "Peach State Senior Care", "state": "GA", "enrollment": 43_200, "py_rating": 3.0, "projected_rating": 3.5, "hedis_rating": 3.2, "cahps_rating": 3.3, "hos_rating": 3.0, "partd_rating": 3.1},
    {"contract_id": "H2156", "plan_name": "Prairie Medicare Select", "state": "IL", "enrollment": 61_800, "py_rating": 4.0, "projected_rating": 4.0, "hedis_rating": 4.1, "cahps_rating": 3.8, "hos_rating": 4.0, "partd_rating": 4.0},
    {"contract_id": "H3267", "plan_name": "Carolina Blue Medicare", "state": "NC", "enrollment": 48_900, "py_rating": 4.0, "projected_rating": 4.5, "hedis_rating": 4.2, "cahps_rating": 4.3, "hos_rating": 4.0, "partd_rating": 4.1},
    {"contract_id": "H4378", "plan_name": "Great Lakes Senior Advantage", "state": "MI", "enrollment": 55_700, "py_rating": 3.5, "projected_rating": 3.5, "hedis_rating": 3.6, "cahps_rating": 3.4, "hos_rating": 3.5, "partd_rating": 3.3},
    {"contract_id": "H5489", "plan_name": "Cascade Medicare Choice", "state": "WA", "enrollment": 38_400, "py_rating": 4.5, "projected_rating": 4.5, "hedis_rating": 4.7, "cahps_rating": 4.3, "hos_rating": 4.5, "partd_rating": 4.4},
    {"contract_id": "H6590", "plan_name": "Blue Ridge Senior Select", "state": "VA", "enrollment": 44_100, "py_rating": 4.0, "projected_rating": 4.0, "hedis_rating": 3.9, "cahps_rating": 4.0, "hos_rating": 4.0, "partd_rating": 3.9},
    {"contract_id": "H7601", "plan_name": "Rocky Mountain Medicare Plus", "state": "CO", "enrollment": 59_000, "py_rating": 4.0, "projected_rating": 4.0, "hedis_rating": 4.0, "cahps_rating": 4.1, "hos_rating": 4.0, "partd_rating": 3.8},
]


def _fallback_plans(state: str | None, py_rating: float | None, proj_rating: float | None, search: str | None) -> list[PlanSummary]:
    results = []
    for c in _CONTRACTS:
        if state and c["state"] != state:
            continue
        if py_rating and c["py_rating"] != py_rating:
            continue
        if proj_rating and c["projected_rating"] != proj_rating:
            continue
        if search and search.lower() not in c["plan_name"].lower() and search.upper() not in c["contract_id"]:
            continue
        gap = max(0.0, 4.0 - c["projected_rating"])
        results.append(PlanSummary(
            **c,
            star_gap_to_4=gap,
            bonus_eligible=c["projected_rating"] >= 4.0,
        ))
    return results


@router.get("/plans", response_model=list[PlanSummary])
def get_plans(
    state: str | None = Query(None),
    py_rating: float | None = Query(None),
    proj_rating: float | None = Query(None),
    search: str | None = Query(None),
):
    try:
        sql = """
            SELECT p.contract_id, p.plan_name, p.state, p.enrollment_count AS enrollment,
                   COALESCE(s.prior_year_star_rating, 0.0) AS py_rating,
                   COALESCE(s.projected_star_rating, 0.0) AS projected_rating,
                   COALESCE(s.hedis_domain_rating, 0.0) AS hedis_rating,
                   COALESCE(s.cahps_domain_rating, 0.0) AS cahps_rating,
                   COALESCE(s.hos_domain_rating, 0.0) AS hos_rating,
                   COALESCE(s.partd_domain_rating, 0.0) AS partd_rating,
                   GREATEST(0, COALESCE(4.0 - s.projected_star_rating, 4.0)) AS star_gap_to_4,
                   COALESCE(s.bonus_eligible_flag, false) AS bonus_eligible
            FROM aiagenticdemo.stars_silver.silver_plan p
            LEFT JOIN (
                SELECT * FROM aiagenticdemo.stars_gold.gold_star_rating_summary
                WHERE measurement_year = (
                    SELECT MAX(measurement_year) FROM aiagenticdemo.stars_gold.gold_star_rating_summary
                )
            ) s ON s.plan_key = p.plan_key
            ORDER BY p.enrollment_count DESC
        """
        rows = query(sql)
        if not rows:
            return _fallback_plans(state, py_rating, proj_rating, search)
        plans = [PlanSummary(**r) for r in rows]
        if state:
            plans = [p for p in plans if p.state == state]
        if py_rating:
            plans = [p for p in plans if p.py_rating == py_rating]
        if proj_rating:
            plans = [p for p in plans if p.projected_rating == proj_rating]
        if search:
            s = search.lower()
            plans = [p for p in plans if s in p.plan_name.lower() or s in p.contract_id.lower()]
        return plans
    except Exception:
        return _fallback_plans(state, py_rating, proj_rating, search)


@router.get("/plans/{contract_id}", response_model=PlanDetail)
def get_plan_detail(contract_id: str):
    base = next((c for c in _CONTRACTS if c["contract_id"] == contract_id), _CONTRACTS[0])
    gap = max(0.0, 4.0 - base["projected_rating"])
    historical = [
        HistoricalRating(year="2021", rating=base["py_rating"] - 0.5),
        HistoricalRating(year="2022", rating=base["py_rating"] - 0.5),
        HistoricalRating(year="2023", rating=base["py_rating"]),
        HistoricalRating(year="2024", rating=base["py_rating"]),
        HistoricalRating(year="2025", rating=base["projected_rating"]),
    ]
    domains = [
        DomainScore(domain="HEDIS", rating=base["hedis_rating"], on_track_count=8, total_count=14, critical_count=3),
        DomainScore(domain="CAHPS", rating=base["cahps_rating"], on_track_count=5, total_count=9, critical_count=1),
        DomainScore(domain="HOS", rating=base["hos_rating"], on_track_count=4, total_count=5, critical_count=0),
        DomainScore(domain="Medical Adherence", rating=base["partd_rating"], on_track_count=3, total_count=5, critical_count=1),
    ]
    return PlanDetail(
        **base,
        star_gap_to_4=gap,
        bonus_eligible=base["projected_rating"] >= 4.0,
        historical_ratings=historical,
        domain_scores=domains,
    )
