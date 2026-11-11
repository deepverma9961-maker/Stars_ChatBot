from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta

from ...services.ml_propensity import _FALLBACK_RATES
from ...services.simulator_engine import COST_BASE, INCENTIVE_COST
from ...db import query
from ...config import settings
from ..models.cohort import PrioritizedMember
from ..models.nba import (
    NBARequest, NBAResponse, RecommendedAction, ActionAlternative,
)

logger = logging.getLogger("agent.nba")

_CHANNELS = ["Call", "SMS", "Email"]
_INCENTIVES = ["None", "$25 card", "$50 card"]


class NextBestActionAgent:

    def recommend(self, req: NBARequest) -> NBAResponse:
        recent_outreach = self._fetch_recent_outreach_batch(
            [m.member_key for m in req.members]
        )

        actions: list[RecommendedAction] = []
        for member in req.members:
            action = self._recommend_for_member(
                member, recent_outreach.get(member.member_key, []),
                req.budget_per_member,
            )
            actions.append(action)

        total_budget = sum(a.cost_estimate for a in actions)
        avg_closure = (
            sum(a.predicted_closure_prob for a in actions) / len(actions)
            if actions else 0.0
        )

        any_live = any(
            a.predicted_closure_prob != _FALLBACK_RATES.get(
                (a.recommended_channel, a.recommended_incentive), -1
            )
            for a in actions[:5]
        ) if actions else False
        source = "live" if any_live else "fallback"

        return NBAResponse(
            actions=actions,
            total_budget_estimate=round(total_budget, 2),
            avg_predicted_closure=round(avg_closure, 4),
            source=source,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _recommend_for_member(
        self,
        member: PrioritizedMember,
        recent: list[dict],
        budget_cap: float | None,
    ) -> RecommendedAction:
        scores = self._get_propensity_scores(
            member.member_key, member.measure_code
        )

        combos = []
        for ch in _CHANNELS:
            for inc in _INCENTIVES:
                raw_prob = scores.get((ch, inc), 0.22)
                discount = self._compute_fatigue_discount(ch, recent)
                prob = raw_prob * discount
                cost = COST_BASE.get(ch, 4) + INCENTIVE_COST.get(inc, 0)
                if budget_cap and cost > budget_cap:
                    continue
                roi = prob / max(cost, 1)
                combos.append({
                    "channel": ch, "incentive": inc,
                    "prob": prob, "cost": cost, "roi": roi,
                    "raw_prob": raw_prob, "discount": discount,
                })

        combos.sort(key=lambda c: c["roi"], reverse=True)

        best = combos[0] if combos else {
            "channel": "SMS", "incentive": "None",
            "prob": 0.22, "cost": 4, "roi": 0.055,
            "raw_prob": 0.22, "discount": 1.0,
        }

        timing = self._determine_timing(member)

        alts = [
            ActionAlternative(
                channel=c["channel"], incentive=c["incentive"],
                predicted_closure_prob=round(c["prob"], 4),
                cost=c["cost"],
            )
            for c in combos[1:3]
        ]

        reasoning = self._build_reasoning(best, recent, timing)

        return RecommendedAction(
            member_key=member.member_key,
            display_name=member.display_name,
            measure_code=member.measure_code,
            measure_name=member.measure_name,
            gap_status=member.gap_status,
            age=member.age,
            days_open=member.days_open,
            propensity_score=member.propensity_score,
            recommended_channel=best["channel"],
            recommended_incentive=best["incentive"],
            recommended_timing=timing,
            predicted_closure_prob=round(best["prob"], 4),
            cost_estimate=best["cost"],
            roi_score=round(best["roi"], 4),
            reasoning=reasoning,
            alternatives=alts,
        )

    def _get_propensity_scores(
        self, member_key: str, measure_code: str
    ) -> dict[tuple[str, str], float]:
        try:
            rows = query(f"""
                SELECT channel, incentive, p_close
                FROM {settings.gold}.gold_member_closure_propensity
                WHERE member_key = '{member_key}'
                  AND measure_code = '{measure_code}'
                  AND measurement_year = 2025
            """)
            if rows:
                return {
                    (r["channel"], r["incentive"]): float(r["p_close"])
                    for r in rows
                }
        except Exception:
            pass
        return dict(_FALLBACK_RATES)

    def _fetch_recent_outreach_batch(
        self, member_keys: list[str]
    ) -> dict[str, list[dict]]:
        if not member_keys:
            return {}
        try:
            keys_str = ", ".join(f"'{k}'" for k in member_keys[:200])
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).strftime(
                "%Y-%m-%d"
            )
            rows = query(f"""
                SELECT member_name, channel, created_at, status
                FROM {settings.silver}.outreach_activity_log
                WHERE member_name IN ({keys_str})
                  AND created_at >= '{cutoff}'
                ORDER BY created_at DESC
            """)
            result: dict[str, list[dict]] = {}
            for r in rows:
                result.setdefault(r["member_name"], []).append(r)
            return result
        except Exception:
            return {}

    def _compute_fatigue_discount(
        self, channel: str, recent: list[dict]
    ) -> float:
        if not recent:
            return 1.0
        now = datetime.now(timezone.utc)
        for entry in recent:
            if entry.get("channel") != channel:
                continue
            created = entry.get("created_at")
            if not created:
                continue
            if isinstance(created, str):
                try:
                    created = datetime.fromisoformat(created)
                except Exception:
                    continue
            if not hasattr(created, "tzinfo") or created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            days_ago = (now - created).days
            if days_ago <= 7:
                return 0.7
            if days_ago <= 14:
                return 0.85
        return 1.0

    def _determine_timing(self, member: PrioritizedMember) -> str:
        if member.days_open > 14 or member.priority_score > 0.7:
            return "immediate"
        if member.priority_score >= 0.4:
            return "next_week"
        return "end_of_month"

    def _build_reasoning(
        self, best: dict, recent: list[dict], timing: str
    ) -> str:
        prob_pct = round(best["prob"] * 100)
        parts = [
            f"{best['channel']} with {best['incentive']} incentive is optimal: "
            f"{prob_pct}% predicted closure at ${best['cost']}/member "
            f"(ROI {best['roi']:.1f}x)."
        ]
        if best["discount"] < 1.0:
            parts.append(
                f"Score adjusted by {best['discount']:.0%} due to recent "
                f"{best['channel']} contact."
            )
        parts.append(f"Timing: {timing}.")
        return " ".join(parts)
