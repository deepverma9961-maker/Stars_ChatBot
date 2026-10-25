-- GET /api/plans
SELECT
    p.contract_id,
    p.plan_name,
    p.state,
    p.enrollment_count                  AS enrollment,
    s.prior_year_star_rating            AS py_rating,
    s.projected_star_rating             AS projected_rating,
    s.hedis_domain_rating               AS hedis_rating,
    s.cahps_domain_rating               AS cahps_rating,
    s.hos_domain_rating                 AS hos_rating,
    s.partd_domain_rating               AS partd_rating,
    GREATEST(0, 4.0 - s.projected_star_rating) AS star_gap_to_4,
    s.bonus_eligible_flag               AS bonus_eligible
FROM {gold}.gold_star_rating_summary s
JOIN {silver}.silver_plan p ON s.plan_key = p.plan_key
WHERE s.measurement_year = 2025
ORDER BY p.enrollment_count DESC
