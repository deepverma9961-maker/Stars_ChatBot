from __future__ import annotations

import logging
import random
from datetime import datetime, timezone

from ...services.star_calculator import THRESHOLDS
from ...db import query
from ...config import settings
from ..models.cohort import (
    CohortRequest, CohortResponse, PrioritizedMember, ScoringFactors,
)

logger = logging.getLogger("agent.cohort")

_FIRST_NAMES = [
    "James", "Maria", "Robert", "Linda", "William", "Barbara", "David",
    "Patricia", "Richard", "Jennifer", "Charles", "Dorothy", "Joseph",
    "Carol", "Thomas", "Ruth", "Christopher", "Sharon", "Daniel", "Helen",
]
_LAST_INITIALS = list("ABCDEFGHJKLMNOPRSTW")
_MEASURES = [
    ("COL", "Colorectal Cancer Screening"),
    ("CBP", "Controlling Blood Pressure"),
    ("HBD", "Diabetes Care – Blood Sugar Controlled"),
    ("KED", "Kidney Health Evaluation"),
    ("BCS", "Breast Cancer Screening"),
    ("AMM", "Follow-up after ED Visit"),
    ("SPC", "Statin Therapy – Cardiovascular"),
    ("OMW", "Osteoporosis Management"),
]
_PCPS = [
    "Dr. Smith, J.", "Dr. Chen, L.", "Dr. Patel, R.",
    "Dr. Williams, K.", "Dr. Johnson, M.", "Dr. Davis, T.",
]

GAP_SEVERITY = {"Open": 1.0, "Partial": 0.6, "Borderline": 0.3}


class CohortPrioritizationAgent:

    def __init__(self):
        self._thresholds = THRESHOLDS

    def prioritize(self, req: CohortRequest) -> CohortResponse:
        try:
            rows = self._fetch_members_live(req)
            source = "live"
        except Exception as exc:
            logger.warning("Databricks unavailable, using fallback: %s", exc)
            rows = self._generate_fallback_members(req)
            source = "fallback"

        scored = []
        for row in rows:
            score, factors = self._compute_priority(row)
            scored.append((score, factors, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        scored = scored[:req.max_members]

        weights_used = {
            code: t["weight"] for code, t in self._thresholds.items()
        }

        members = []
        for rank, (score, factors, row) in enumerate(scored, 1):
            members.append(PrioritizedMember(
                member_key=row["member_key"],
                display_name=row["display_name"],
                age=row["age"],
                measure_code=row["measure_code"],
                measure_name=row["measure_name"],
                gap_status=row["gap_status"],
                propensity_score=row["propensity_score"],
                days_open=row["days_open"],
                priority_score=round(score, 4),
                priority_rank=rank,
                recommended_channel=row["recommended_channel"],
                pcp_name=row["pcp_name"],
                scoring_factors=factors,
            ))

        return CohortResponse(
            members=members,
            total_eligible=len(rows),
            total_scored=len(members),
            measure_weights_used=weights_used,
            source=source,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _compute_priority(self, row: dict) -> tuple[float, ScoringFactors]:
        prop = row.get("propensity_score", 50.0) / 100.0
        days = row.get("days_open", 0)
        urgency = min(days / 365.0, 1.0)
        code = row.get("measure_code", "")
        weight = self._thresholds.get(code, {}).get("weight", 1)
        measure_w = weight / 3.0
        gap = row.get("gap_status", "Open")
        severity = GAP_SEVERITY.get(gap, 0.5)

        score = 0.35 * prop + 0.25 * urgency + 0.25 * measure_w + 0.15 * severity

        factors = ScoringFactors(
            propensity_component=round(prop, 4),
            urgency_component=round(urgency, 4),
            measure_weight_component=round(measure_w, 4),
            gap_severity_component=round(severity, 4),
        )
        return score, factors

    def _fetch_members_live(self, req: CohortRequest) -> list[dict]:
        gap_list = ", ".join(f"'{g}'" for g in req.gap_statuses)
        prop_clauses = []
        for tier in req.propensity_tiers:
            if tier == "high":
                prop_clauses.append("g.propensity_score > 75")
            elif tier == "medium":
                prop_clauses.append("(g.propensity_score BETWEEN 40 AND 75)")
            elif tier == "low":
                prop_clauses.append("g.propensity_score < 40")
        prop_where = " OR ".join(prop_clauses) if prop_clauses else "1=1"

        measure_filter = ""
        if req.measure_code:
            measure_filter = f"AND ms.measure_code = '{req.measure_code}'"

        sql = f"""
            SELECT
                g.member_key,
                m.display_name,
                m.age,
                ms.measure_code,
                ms.measure_name,
                g.gap_status,
                g.propensity_score,
                g.days_open,
                CASE
                    WHEN g.propensity_score > 75 THEN 'Call'
                    WHEN g.propensity_score > 40 THEN 'SMS'
                    ELSE 'Email'
                END AS recommended_channel,
                COALESCE(m.pcp_name, 'Unassigned') AS pcp_name
            FROM {settings.gold}.gold_member_gap g
            JOIN {settings.silver}.silver_member m ON g.member_key = m.member_key
            JOIN {settings.silver}.silver_measure ms ON g.measure_code = ms.measure_code
            WHERE g.contract_id = '{req.contract_id}'
              AND g.gap_status IN ({gap_list})
              AND ({prop_where})
              {measure_filter}
            LIMIT 2000
        """
        return query(sql)

    def _generate_fallback_members(self, req: CohortRequest) -> list[dict]:
        rng = random.Random(42 + hash(req.contract_id))
        count = 847
        members = []
        for i in range(count):
            rng_i = random.Random(42 + i + hash(req.contract_id))
            name = f"{rng_i.choice(_FIRST_NAMES)} {rng_i.choice(_LAST_INITIALS)}."
            age = rng_i.randint(62, 82)
            prop = round(rng_i.uniform(30, 95), 1)
            measure = rng_i.choice(_MEASURES)
            gap_status = rng_i.choice(list(GAP_SEVERITY.keys()))
            days = rng_i.randint(1, 120)
            channel = "Call" if prop > 75 else ("SMS" if prop > 40 else "Email")
            pcp = rng_i.choice(_PCPS)

            if gap_status not in req.gap_statuses:
                continue
            tier = "high" if prop > 75 else ("medium" if prop >= 40 else "low")
            if tier not in req.propensity_tiers:
                continue
            if req.measure_code and measure[0] != req.measure_code:
                continue

            members.append({
                "member_key": f"MK-{req.contract_id}-{i:05d}",
                "display_name": name,
                "age": age,
                "measure_code": measure[0],
                "measure_name": measure[1],
                "gap_status": gap_status,
                "propensity_score": prop,
                "days_open": days,
                "recommended_channel": channel,
                "pcp_name": pcp,
            })
        return members
