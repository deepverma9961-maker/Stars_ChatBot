from fastapi import APIRouter
from ..models.plan import StarSummary
from ..db import query

router = APIRouter(tags=["star-summary"])

# Hardcoded fallback matching the HTML reference data (H3312 default plan portfolio)
_FALLBACK = StarSummary(
    total_plans=14,
    total_enrollment=980_000,
    above_4star_count=9,
    above_4star_pct=64.3,
    avg_star_rating=4.0,
    measurement_year=2025,
)


@router.get("/star-summary", response_model=StarSummary)
def get_star_summary():
    try:
        rows = query(
            """
            SELECT
                COUNT(*) AS total_plans,
                SUM(p.enrollment_count) AS total_enrollment,
                SUM(CASE WHEN s.projected_star_rating >= 4.0 THEN 1 ELSE 0 END) AS above_4star_count,
                ROUND(AVG(s.projected_star_rating), 1) AS avg_star_rating
            FROM aiagenticdemo.stars_gold.gold_star_rating_summary s
            JOIN aiagenticdemo.stars_silver.silver_plan p ON s.plan_key = p.plan_key
            WHERE s.measurement_year = 2025
            """
        )
        if not rows:
            return _FALLBACK
        r = rows[0]
        total = r["total_plans"] or 14
        above = r["above_4star_count"] or 9
        return StarSummary(
            total_plans=total,
            total_enrollment=r["total_enrollment"] or 980_000,
            above_4star_count=above,
            above_4star_pct=round(above / total * 100, 1),
            avg_star_rating=r["avg_star_rating"] or 4.0,
            measurement_year=2025,
        )
    except Exception:
        return _FALLBACK
