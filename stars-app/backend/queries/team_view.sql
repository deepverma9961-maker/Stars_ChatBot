-- GET /api/team-view
SELECT
    t.department,
    t.team_leader                       AS leader,
    t.measures_owned,
    t.on_track_count,
    t.at_risk_count,
    t.critical_count,
    t.action_status,
    t.next_action
FROM {gold}.gold_team_view t
WHERE t.measurement_year = 2025
ORDER BY t.critical_count DESC, t.at_risk_count DESC
