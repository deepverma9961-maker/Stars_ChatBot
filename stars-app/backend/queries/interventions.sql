-- GET /api/interventions
SELECT
    i.intervention_id,
    i.intervention_name,
    ms.measure_code,
    ms.measure_name,
    i.owner_department,
    i.expected_lift_pct,
    i.intervention_status               AS status,
    CAST(i.due_date AS STRING)          AS due_date,
    i.target_member_count               AS member_count
FROM {gold}.gold_intervention_hub i
JOIN {silver}.silver_measure ms ON i.measure_key = ms.measure_key
WHERE i.measurement_year = 2025
ORDER BY i.expected_lift_pct DESC
