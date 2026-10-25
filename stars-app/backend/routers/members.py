import random
from fastapi import APIRouter, Query
from ..models.member import MemberGapRow, MemberGapPage, MemberProfile, MemberClinicalEvent, MemberMedication
from ..models.common import GapStatus, Channel
from ..db import query

router = APIRouter(tags=["members"])

_FIRST_NAMES = ["James", "Maria", "Robert", "Linda", "William", "Barbara", "David", "Patricia", "Richard", "Jennifer", "Charles", "Dorothy", "Joseph", "Carol", "Thomas", "Ruth", "Christopher", "Sharon", "Daniel", "Helen"]
_LAST_INITIALS = list("ABCDEFGHJKLMNOPRSTW")
_MEASURES = [
    ("COL", "Colorectal Cancer Screening"), ("CBP", "Controlling Blood Pressure"),
    ("HBD", "Diabetes Care – Blood Sugar Controlled"), ("KED", "Kidney Health Evaluation"),
    ("BCS", "Breast Cancer Screening"), ("AMM", "Follow-up after ED Visit"),
    ("SPC", "Statin Therapy – Cardiovascular"), ("OMW", "Osteoporosis Management"),
]
_CHANNELS = ["Call", "SMS", "Email", "Portal"]
_GAP_STATUSES = ["Open", "Partial", "Borderline"]
_PCPS = ["Dr. Smith, J.", "Dr. Chen, L.", "Dr. Patel, R.", "Dr. Williams, K.", "Dr. Johnson, M.", "Dr. Davis, T."]


def _synthetic_members(contract_id: str, page: int, page_size: int, seed_offset: int = 0) -> MemberGapPage:
    rng = random.Random(42 + hash(contract_id) + seed_offset)
    total = 847
    start = (page - 1) * page_size
    items = []
    for i in range(start, min(start + page_size, total)):
        rng_i = random.Random(42 + i + hash(contract_id))
        name = f"{rng_i.choice(_FIRST_NAMES)} {rng_i.choice(_LAST_INITIALS)}."
        age = rng_i.randint(62, 82)
        prop = round(rng_i.uniform(30, 95), 1)
        measure = rng_i.choice(_MEASURES)
        gap_status = rng_i.choice(_GAP_STATUSES)
        days = rng_i.randint(0, 30)
        last = "Never" if days > 25 else (f"{days} day{'s' if days != 1 else ''} ago")
        channel = "Call" if prop > 75 else ("SMS" if prop > 40 else "Email")
        pcp = rng_i.choice(_PCPS)
        items.append(MemberGapRow(
            member_key=f"MK-{contract_id}-{i:05d}",
            display_name=name,
            age=age,
            propensity_score=prop,
            measure_code=measure[0],
            measure_name=measure[1],
            gap_status=gap_status,
            last_contact=last,
            recommended_channel=channel,
            pcp_name=pcp,
            campaign_name=None,
        ))
    return MemberGapPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/members/gaps", response_model=MemberGapPage)
def get_member_gaps(
    contract_id: str = Query("H3312"),
    measure_code: str | None = Query(None),
    gap_status: str | None = Query(None),
    propensity: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    try:
        offset = (page - 1) * page_size
        where_clauses = [f"p.contract_id = '{contract_id}'"]
        if measure_code:
            where_clauses.append(f"ms.measure_code = '{measure_code}'")
        if gap_status:
            where_clauses.append(f"g.gap_status = '{gap_status}'")
        if propensity == "high":
            where_clauses.append("g.propensity_score > 75")
        elif propensity == "medium":
            where_clauses.append("g.propensity_score BETWEEN 40 AND 75")
        elif propensity == "low":
            where_clauses.append("g.propensity_score < 40")
        where = " AND ".join(where_clauses)

        count_rows = query(f"""
            SELECT COUNT(*) AS total
            FROM aiagenticdemo.stars_gold.gold_member_gap g
            JOIN aiagenticdemo.stars_silver.silver_member m ON g.member_key = m.member_key
            JOIN aiagenticdemo.stars_silver.silver_measure ms ON g.measure_key = ms.measure_key
            JOIN aiagenticdemo.stars_silver.silver_plan p ON g.plan_key = p.plan_key
            WHERE {where}
        """)
        total = count_rows[0]["total"] if count_rows else 847

        rows = query(f"""
            SELECT g.member_gap_key, m.display_name, m.age, g.propensity_score,
                   ms.measure_code, ms.measure_name, g.gap_status,
                   CASE WHEN g.last_outreach_date IS NULL THEN 'Never'
                        ELSE CAST(DATEDIFF(CURRENT_DATE, g.last_outreach_date) AS STRING) || ' days ago'
                   END AS last_contact,
                   g.recommended_channel, 'Dr. Smith, J.' AS pcp_name, g.campaign_name
            FROM aiagenticdemo.stars_gold.gold_member_gap g
            JOIN aiagenticdemo.stars_silver.silver_member m ON g.member_key = m.member_key
            JOIN aiagenticdemo.stars_silver.silver_measure ms ON g.measure_key = ms.measure_key
            JOIN aiagenticdemo.stars_silver.silver_plan p ON g.plan_key = p.plan_key
            WHERE {where}
            ORDER BY g.propensity_score DESC
            LIMIT {page_size} OFFSET {offset}
        """)
        items = [MemberGapRow(**r) for r in rows]
        return MemberGapPage(items=items, total=total, page=page, page_size=page_size)
    except Exception:
        return _synthetic_members(contract_id, page, page_size)


@router.get("/members/{member_key}", response_model=MemberProfile)
def get_member_profile(member_key: str):
    rng = random.Random(hash(member_key) & 0xFFFFFF)
    name = f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_INITIALS)}."
    age = rng.randint(62, 82)
    prop = round(rng.uniform(30, 95), 1)
    contract_id = member_key.split("-")[1] if "-" in member_key else "H3312"
    gaps = [
        MemberGapRow(
            member_key=member_key,
            display_name=name,
            age=age,
            propensity_score=prop,
            measure_code=m[0],
            measure_name=m[1],
            gap_status=rng.choice(_GAP_STATUSES),
            last_contact="Never",
            recommended_channel=rng.choice(_CHANNELS),
            pcp_name=rng.choice(_PCPS),
        )
        for m in rng.sample(_MEASURES, rng.randint(1, 3))
    ]
    events = [
        MemberClinicalEvent(
            event_date=f"2025-{rng.randint(1,4):02d}-{rng.randint(1,28):02d}",
            event_type=rng.choice(["Office Visit", "Lab", "ER Visit", "Telehealth"]),
            description=rng.choice(["Annual Wellness Visit", "HbA1c Test", "Blood Pressure Check", "Telehealth Consult"]),
            provider=rng.choice(_PCPS),
        )
        for _ in range(rng.randint(2, 5))
    ]
    meds = [
        MemberMedication(
            drug_name=rng.choice(["Atorvastatin 40mg", "Metformin 500mg", "Lisinopril 10mg", "Sertraline 50mg"]),
            ndc=f"00093-{rng.randint(1000,9999)}-01",
            days_supply=rng.choice([30, 90]),
            last_fill=f"2025-{rng.randint(1,4):02d}-{rng.randint(1,28):02d}",
            adherent=rng.random() > 0.25,
        )
        for _ in range(rng.randint(1, 4))
    ]
    return MemberProfile(
        member_key=member_key,
        display_name=name,
        age=age,
        gender=rng.choice(["M", "F"]),
        plan_name="Health Plan Advantage Premier",
        contract_id=contract_id,
        dual_eligible=rng.random() < 0.2,
        lis_flag=rng.random() < 0.3,
        utilization_segment=rng.choice(["Low", "Moderate", "Chronic", "Very High Risk"]),
        propensity_score=prop,
        open_gaps=gaps,
        clinical_events=events,
        medications=meds,
    )
