-- GET /api/hedis-measures
SELECT
    ms.measure_code,
    ms.measure_name,
    CASE WHEN ms.measure_weight = 3 THEN '3x' ELSE '1x' END AS weight,
    sc.current_rate,
    sc.open_gap_count,
    sc.measure_status                   AS status,
    sc.target_rate,
    sc.projected_rate,
    ms.part
FROM {gold}.gold_measure_scorecard sc
JOIN {silver}.silver_measure ms ON sc.measure_key = ms.measure_key
JOIN {silver}.silver_plan p ON sc.plan_key = p.plan_key
WHERE sc.measurement_year = 2025
  AND p.contract_id = '{contract_id}'
  AND ms.measure_category = 'HEDIS'
ORDER BY sc.current_rate ASC
