THRESHOLDS: dict[str, dict] = {
    "HBD": {"weight": 3, "4star": 80.0, "5star": 90.0},
    "CBP": {"weight": 3, "4star": 70.0, "5star": 80.0},
    "PCR": {"weight": 3, "4star": 75.0, "5star": 85.0},
    "BCS": {"weight": 1, "4star": 72.0, "5star": 82.0},
    "COL": {"weight": 1, "4star": 68.0, "5star": 78.0},
    "COA_MR": {"weight": 1, "4star": 82.0, "5star": 90.0},
    "COA_PA": {"weight": 1, "4star": 74.0, "5star": 84.0},
    "OMW": {"weight": 1, "4star": 62.0, "5star": 72.0},
    "EED": {"weight": 1, "4star": 70.0, "5star": 80.0},
    "KED": {"weight": 1, "4star": 65.0, "5star": 75.0},
    "MRP": {"weight": 1, "4star": 86.0, "5star": 94.0},
    "SPC": {"weight": 1, "4star": 68.0, "5star": 78.0},
    "TRC": {"weight": 1, "4star": 70.0, "5star": 80.0},
    "AMM": {"weight": 1, "4star": 64.0, "5star": 74.0},
}


def rate_to_status(rate: float, measure_code: str) -> str:
    t = THRESHOLDS.get(measure_code, {"4star": 70.0})
    four_star = t.get("4star", 70.0)
    if rate >= four_star + 5:
        return "green"
    if rate >= four_star - 8:
        return "yellow"
    return "red"


def compute_overall_star_rating(measure_scores: list[dict]) -> float:
    total_weight = 0
    weighted_sum = 0.0
    for m in measure_scores:
        code = m.get("measure_code", "")
        rate = m.get("current_rate", 0.0)
        w = THRESHOLDS.get(code, {}).get("weight", 1)
        # Convert rate to 0-5 star scale roughly
        t = THRESHOLDS.get(code, {"4star": 70.0, "5star": 80.0})
        stars = _rate_to_stars(rate, t)
        weighted_sum += stars * w
        total_weight += w
    if total_weight == 0:
        return 0.0
    return round(weighted_sum / total_weight * 2) / 2  # round to nearest 0.5


def _rate_to_stars(rate: float, t: dict) -> float:
    four = t.get("4star", 70.0)
    five = t.get("5star", 80.0)
    if rate >= five:
        return 5.0
    if rate >= four:
        return 4.0
    if rate >= four - 8:
        return 3.0
    if rate >= four - 16:
        return 2.0
    return 1.0
