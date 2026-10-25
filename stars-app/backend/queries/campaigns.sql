-- GET /api/campaigns
SELECT
    c.campaign_name,
    c.measure_code,
    c.primary_channel                   AS channel,
    c.member_count,
    c.projected_closures,
    c.actual_closures,
    CONCAT('+', CAST(ROUND(c.lift_pct, 1) AS STRING), '%') AS lift_pct,
    CONCAT('$', FORMAT_NUMBER(c.total_cost, 0)) AS cost_str,
    CASE
        WHEN c.roi_multiplier IS NULL THEN '—'
        ELSE CONCAT(CAST(ROUND(c.roi_multiplier, 1) AS STRING), 'x')
    END AS roi_str,
    c.campaign_status                   AS status
FROM {gold}.gold_campaign_performance c
WHERE c.measurement_year = 2025
ORDER BY c.campaign_start_date DESC
