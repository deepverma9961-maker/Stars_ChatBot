-- GET /api/members/gaps (paginated)
SELECT
    g.member_gap_key,
    m.display_name,
    m.age,
    g.propensity_score,
    ms.measure_code,
    ms.measure_name,
    g.gap_status,
    CASE
        WHEN g.last_outreach_date IS NULL THEN 'Never'
        WHEN DATEDIFF(CURRENT_DATE, g.last_outreach_date) = 0 THEN 'Today'
        WHEN DATEDIFF(CURRENT_DATE, g.last_outreach_date) = 1 THEN '1 day ago'
        ELSE CAST(DATEDIFF(CURRENT_DATE, g.last_outreach_date) AS STRING) || ' days ago'
    END AS last_contact,
    g.recommended_channel,
    prov.provider_name                  AS pcp_name,
    g.campaign_name
FROM {gold}.gold_member_gap g
JOIN {silver}.silver_member m ON g.member_key = m.member_key
JOIN {silver}.silver_measure ms ON g.measure_key = ms.measure_key
JOIN {silver}.silver_plan p ON g.plan_key = p.plan_key
LEFT JOIN {silver}.silver_provider prov ON m.pcp_provider_key = prov.provider_key
WHERE p.contract_id = '{contract_id}'
ORDER BY g.propensity_score DESC
LIMIT {page_size} OFFSET {offset}
