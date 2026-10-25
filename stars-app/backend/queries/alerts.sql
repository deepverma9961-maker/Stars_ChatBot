-- GET /api/alerts
SELECT
    a.alert_id,
    a.severity,
    a.alert_title                       AS title,
    a.alert_body                        AS body,
    a.alert_meta                        AS meta,
    a.measure_code,
    a.cta_label,
    a.cta_page
FROM {gold}.gold_alert_priority a
WHERE a.is_active = true
ORDER BY
    CASE a.severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END,
    a.priority_score DESC
