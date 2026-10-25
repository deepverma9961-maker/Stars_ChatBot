from ..models.simulator import (
    SimulatorConfig, SimulatorResult, WaterfallWeek, SegmentRow,
)
from . import ml_propensity

CLOSURE_RATES: dict[str, float] = {"Call": 0.28, "SMS": 0.22, "Email": 0.12}
INCENTIVE_BOOST: dict[str, float] = {"None": 0.0, "$25 card": 0.04, "$50 card": 0.08}
COST_BASE: dict[str, int] = {"Call": 22, "SMS": 4, "Email": 2}
INCENTIVE_COST: dict[str, int] = {"None": 0, "$25 card": 25, "$50 card": 50}
WATERFALL_DIST = [0.4, 0.3, 0.2, 0.1]

# Gap status and propensity tier member distribution weights
GAP_WEIGHT = {"Open": 0.55, "Partial": 0.30, "Borderline": 0.15}
PROP_WEIGHT = {"high": 0.25, "medium": 0.42, "low": 0.33}

# Suppression counts (realistic defaults for a 847-member net pool equivalent)
SUPPRESSION_COUNTS = {"recently_contacted": 83, "opted_out": 29, "already_closed": 41}


def _closure_rate(channel: str, incentive: str, measure_code: str = "ALL") -> float:
    """Return the predicted closure rate. Uses the ML model when the
    `gold_member_closure_propensity` table is live, otherwise falls back to
    the static lookup CLOSURE_RATES + INCENTIVE_BOOST.
    """
    p = ml_propensity.mean_closure_rate(measure_code, channel, incentive)
    if p is not None and 0.01 <= p <= 0.99:
        return p
    return CLOSURE_RATES.get(channel, 0.22) + INCENTIVE_BOOST.get(incentive, 0.0)


def _cost_per_member(channel: str, incentive: str) -> int:
    return COST_BASE.get(channel, 4) + INCENTIVE_COST.get(incentive, 0)


def _compute_eligible(open_gaps: int, current_rate_pct: float) -> int:
    denominator = max(0.01, 1.0 - current_rate_pct / 100.0)
    return round(open_gaps / denominator)


def _build_waterfall(
    net_pool: int,
    total_closures: int,
    eligible: int,
    start_rate: float,
) -> list[WaterfallWeek]:
    cumulative = start_rate
    weeks = []
    for i, fraction in enumerate(WATERFALL_DIST):
        week_outreach = round(net_pool * fraction)
        week_closures = round(total_closures * fraction)
        cumulative += (week_closures / eligible * 100) if eligible > 0 else 0
        weeks.append(
            WaterfallWeek(
                label=f"Week {i + 1}",
                outreach_count=week_outreach,
                estimated_closures=week_closures,
                cumulative_compliance=round(cumulative, 1),
            )
        )
    return weeks


def run_simulation(config: SimulatorConfig, measure_data: dict) -> SimulatorResult:
    open_gaps: int = measure_data.get("open_gap_count", 5000)
    current_rate: float = measure_data.get("current_rate", 65.0)
    measure_name: str = measure_data.get("measure_name", "All HEDIS")

    # Scale gap pool by active filters
    gap_scale = sum(GAP_WEIGHT.get(g, 0.0) for g in config.gap_statuses)
    prop_scale = sum(PROP_WEIGHT.get(p, 0.0) for p in config.propensity_tiers)
    gross_pool = round(open_gaps * gap_scale * prop_scale)

    # Apply suppressions
    suppression_total = sum(
        v for k, v in SUPPRESSION_COUNTS.items() if config.suppressions.get(k, False)
    )
    # Scale suppressions proportionally
    suppression_scaled = round(suppression_total * (gross_pool / max(1, open_gaps)))
    net_pool = max(0, gross_pool - suppression_scaled)

    # Primary channel for cost/rate calculation (first in list)
    primary_channel = config.channels[0] if config.channels else "Call"
    rate = _closure_rate(primary_channel, config.incentive, config.measure_code or "ALL")
    total_closures = round(net_pool * rate)

    eligible = _compute_eligible(open_gaps, current_rate)
    projected_rate = round(
        current_rate + (total_closures / eligible * 100) if eligible > 0 else current_rate,
        1,
    )
    lift = round(projected_rate - current_rate, 1)

    # Channel mix distribution
    n_channels = len(config.channels) or 1
    channel_mix = {ch: round(net_pool / n_channels) for ch in config.channels}

    waterfall = _build_waterfall(net_pool, total_closures, eligible, current_rate)

    # Build segment table (gap status × propensity tier)
    segments: list[SegmentRow] = []
    for gap in config.gap_statuses:
        for prop in config.propensity_tiers:
            seg_members = round(net_pool * GAP_WEIGHT.get(gap, 0.1) * PROP_WEIGHT.get(prop, 0.1))
            if seg_members == 0:
                continue
            # Propensity affects channel preference
            seg_channel = (
                "Call" if prop == "high" else ("SMS" if prop == "medium" else "Email")
            )
            if seg_channel not in config.channels:
                seg_channel = primary_channel
            seg_rate = _closure_rate(seg_channel, config.incentive, config.measure_code or "ALL")
            seg_closures = round(seg_members * seg_rate)
            seg_cost = round(seg_members * _cost_per_member(seg_channel, config.incentive))
            segments.append(
                SegmentRow(
                    label=f"{gap} · {prop.capitalize()} prop",
                    members=seg_members,
                    channel=seg_channel,
                    incentive=config.incentive,
                    estimated_closures=seg_closures,
                    closure_rate_pct=round(seg_rate * 100),
                    estimated_cost=seg_cost,
                )
            )

    return SimulatorResult(
        net_pool=net_pool,
        estimated_closures=total_closures,
        projected_rate=projected_rate,
        lift=lift,
        eligible_members=eligible,
        measure_name=measure_name,
        measure_pct=current_rate,
        channel_mix=channel_mix,
        waterfall=waterfall,
        segments=segments,
    )
