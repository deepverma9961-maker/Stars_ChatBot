-- GET /api/cahps
SELECT
    p.contract_id,
    c.current_cahps_rating              AS current_rating,
    c.projected_cahps_rating            AS projected_rating,
    GREATEST(0, 4.0 - c.projected_cahps_rating) AS gap_to_4_star,
    c.days_remaining,
    c.qbp_at_stake_amount               AS qbp_at_stake
FROM {gold}.gold_cahps_overview c
JOIN {silver}.silver_plan p ON c.plan_key = p.plan_key
WHERE c.measurement_year = 2025
  AND p.contract_id = '{contract_id}'
LIMIT 1
