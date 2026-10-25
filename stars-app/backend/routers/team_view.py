from fastapi import APIRouter
from ..models.intervention import TeamViewRow
from ..db import query

router = APIRouter(tags=["team-view"])

_FALLBACK = [
    TeamViewRow(department="Clinical Quality", leader="Dr. Rachel Kim", measures_owned=["COL", "CBP", "KED", "OMW", "AMM", "HBD"], on_track_count=2, at_risk_count=2, critical_count=4, action_status="In Progress", next_action="COL reminder letter drop — Jun 12"),
    TeamViewRow(department="Member Experience", leader="Sarah Thompson", measures_owned=["GNC", "GCQ", "DC", "CS", "HPR", "CC"], on_track_count=3, at_risk_count=3, critical_count=0, action_status="In Progress", next_action="CAHPS pulse survey — Jun 20"),
    TeamViewRow(department="Call Center", leader="Marcus Johnson", measures_owned=["MRP", "TRC", "AMM"], on_track_count=2, at_risk_count=0, critical_count=1, action_status="In Progress", next_action="AMM follow-up queue — Jun 10"),
    TeamViewRow(department="Pharmacy", leader="Lisa Chen", measures_owned=["SPC", "KED"], on_track_count=1, at_risk_count=1, critical_count=0, action_status="Not Started", next_action="SPC statin gap review — Jun 15"),
    TeamViewRow(department="Utilization Management", leader="David Park", measures_owned=["PCR", "COA_MR", "COA_PA"], on_track_count=2, at_risk_count=1, critical_count=0, action_status="In Progress", next_action="PCR readmission audit — Jun 18"),
    TeamViewRow(department="Network", leader="Angela Torres", measures_owned=["CBP", "BCS", "EED"], on_track_count=2, at_risk_count=1, critical_count=0, action_status="In Progress", next_action="Mammography provider outreach — Jun 22"),
]


@router.get("/team-view", response_model=list[TeamViewRow])
def get_team_view():
    try:
        rows = query("""
            SELECT t.department, t.team_leader AS leader, t.measures_owned,
                   t.on_track_count, t.at_risk_count, t.critical_count,
                   t.action_status, t.next_action
            FROM aiagenticdemo.stars_gold.gold_team_view t
            WHERE t.measurement_year = 2025
            ORDER BY t.critical_count DESC, t.at_risk_count DESC
        """)
        return [TeamViewRow(**r) for r in rows] if rows else _FALLBACK
    except Exception:
        return _FALLBACK
