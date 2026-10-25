from fastapi import APIRouter, Query
from ..db import query
import random, hashlib

router = APIRouter(tags=["hos"])

# ── Fallback measure data ─────────────────────────────────────
_MEASURES = {
    "fall": {
        "id": "fall", "name": "Fall risk management",
        "type": "Process measure · Survey-based · Fall history members only",
        "badge": "CRITICAL", "rate": 76.0, "cut4": 78.0, "stars": 3.0,
        "needed": 10, "eligible": 1260, "documented": 958, "open_gap": 302,
        "survey": {"sent": 820, "responded": 512, "no": 184, "no_resp": 124},
        "awv": {"pct": 48, "note": "655 members with no AWV — scheduling a visit closes the fall gap at the same appointment via CPT G0438/G0439."},
        "questions": [
            {"q": "In the last 6 months, did your personal doctor talk with you about falling or problems with balance or walking?", "proxy": "Did your doctor discuss fall prevention with you?", "rule": "Yes = top box", "pct": 76},
            {"q": "In the last 6 months, did your personal doctor talk with you about how to prevent falls?", "proxy": "Did your doctor give you fall prevention advice?", "rule": "Yes = top box", "pct": 74},
        ],
        "steps": [
            {"title": "Pull fall-risk eligible population", "desc": "Agent scans claims for ICD-10 codes W00-W19 (fall injuries) and Z91.81 (fall risk history).", "result": "1,260 eligible members"},
            {"title": "Cross-reference claims + EHR for documentation", "desc": "Checks for fall prevention counseling CPT codes (claims) and discussion notes (EHR) in last 12 months.", "result": "302 open gaps identified"},
            {"title": "Score by urgency, route to team", "desc": "Agent scores all 302 by urgency factors. High to care mgmt. Med/Low to outreach. Provider report auto-distributed.", "result": "14 providers notified · 198 reached"},
        ],
        "actions": [
            {"team": "Care mgmt", "txt": "Call members using urgency scores to prioritize. Schedule a provider visit for fall prevention discussion.", "sub": "Week 2-5", "lift": "+2-3pp", "status": "Active"},
            {"team": "Clinical", "txt": "EHR alert set for all 302 — when any visits for any reason, provider is prompted to document fall prevention.", "sub": "Week 1-3", "lift": "+3-5pp", "status": "Active"},
            {"team": "Outreach", "txt": "Pre-survey call to reinforce member recall of fall prevention conversation before the regulatory survey opens.", "sub": "Pre-survey window", "lift": "+1-2pp", "status": "Scheduled"},
        ],
        "urgency_factors": [
            {"factor": "Fall history severity", "weight": 25, "measured": "Recency and number of fall-related claims in last 24 months", "source": "Claims · ICD-10 W00-W19", "trigger": "Fall claim in last 6 months, or 2+ falls in 24 months"},
            {"factor": "AWV status", "weight": 20, "measured": "Whether the member has a completed AWV in the last 12 months", "source": "Claims · CPT G0438/G0439", "trigger": "No AWV in the last 12 months"},
            {"factor": "Age", "weight": 15, "measured": "Member age — older members face exponentially higher fall risk", "source": "Enrollment data", "trigger": "Age 80+ = maximum points; 70-79 = high; <70 = low"},
            {"factor": "Comorbidities", "weight": 15, "measured": "Conditions that increase fall risk: diabetes, osteoporosis, vision issues", "source": "Claims · ICD-10", "trigger": "2+ active comorbidities from risk list"},
            {"factor": "Mock survey response", "weight": 10, "measured": "How the member responded on the pre-regulatory mock survey", "source": "Internal survey data", "trigger": "Answered No = high; No response = medium; Yes = low"},
            {"factor": "Time since last provider visit", "weight": 10, "measured": "Months since last documented visit with any provider", "source": "Claims · EHR", "trigger": "No visit in 6+ months"},
            {"factor": "Homebound status", "weight": 5, "measured": "Whether member is identified as homebound", "source": "Claims · ICD-10 Z74.09", "trigger": "Active homebound status = max points"},
        ],
    },
    "mon": {
        "id": "mon", "name": "Monitoring physical activity",
        "type": "Process measure · Survey-based · Linked to physical activity",
        "badge": "CRITICAL", "rate": 69.0, "cut4": 71.0, "stars": 3.0,
        "needed": 22, "eligible": 3402, "documented": 2348, "open_gap": 1054,
        "survey": {"sent": 2100, "responded": 1380, "no": 487, "no_resp": 233},
        "awv": {"pct": 54, "note": "AWV return visit is the natural moment to discuss physical activity progress and document the follow-up conversation."},
        "questions": [
            {"q": "In the last 6 months, did your personal doctor talk with you about how much exercise or physical activity you get?", "proxy": "Did your doctor discuss your exercise habits?", "rule": "Yes = top box", "pct": 69},
            {"q": "In the last 6 months, did your personal doctor give you a plan or goal for your physical activity?", "proxy": "Did your doctor set activity goals with you?", "rule": "Yes = top box", "pct": 68},
        ],
        "steps": [
            {"title": "Identify members who received activity advice", "desc": "Finds members who got physical activity advice but have no follow-up discussion documented in the last 12 months.", "result": "1,054 open gaps"},
            {"title": "Score by urgency and response likelihood", "desc": "Agent scores each member on urgency + predicted survey response likelihood.", "result": "198 high-value contacts identified first"},
            {"title": "Route and generate provider report", "desc": "22 providers with lowest monitoring conversation rates flagged.", "result": "22 providers notified"},
        ],
        "actions": [
            {"team": "Care team", "txt": "Health coach assigned to high-urgency members — structured follow-up on activity progress.", "sub": "30d post-advice", "lift": "+2-4pp", "status": "Planning"},
            {"team": "Clinical", "txt": "EHR prompt at return visits — flag when physical activity follow-up has not been documented.", "sub": "Week 2-3", "lift": "+3-4pp", "status": "Active"},
            {"team": "Outreach", "txt": "Pre-survey call to remind members of follow-up conversations.", "sub": "Pre-survey", "lift": "+1-2pp", "status": "Scheduled"},
        ],
        "urgency_factors": [],
    },
    "phys": {
        "id": "phys", "name": "Improving / maintaining physical health",
        "type": "Outcome measure · 2-year longitudinal · SF-36 PCS · Returns to full weight 2026",
        "badge": "AT RISK", "rate": 72.0, "cut4": 76.0, "stars": 3.5,
        "needed": 40, "eligible": 3100, "documented": 1786, "open_gap": 694,
        "survey": {"sent": 3200, "responded": 2180, "no": 620, "no_resp": 470},
        "awv": {"pct": 54, "note": "AWV enables chronic disease management, PT/OT referrals, fitness enrollment, depression screening — all in one visit."},
        "questions": [
            {"q": "Compared to 2 years ago, how would you rate your physical health in general?", "proxy": "Has your physical health improved or stayed the same?", "rule": "Better / Same = top box", "pct": 72},
            {"q": "In the last 4 weeks, how much of the time did your physical health limit your daily activities?", "proxy": "Physical health limiting your daily life?", "rule": "None / A little = top box", "pct": 71},
        ],
        "steps": [
            {"title": "Stratify all members by health trajectory", "desc": "Agent uses HOS PCS scores + claims + pulse survey to classify all members.", "result": "Declined: 310 · At-risk: 780 · Non-resp: 470"},
            {"title": "Score non-responders by predicted response likelihood", "desc": "470 non-responders scored by predicted likelihood of completing the HOS survey.", "result": "High: 198 · Medium: 156 · Low: 116 deprioritised"},
            {"title": "Build monthly member health trajectory scorecard", "desc": "Physical health trend per member produced for care team review.", "result": "310 declining · 780 at-risk · care team notified"},
        ],
        "actions": [
            {"team": "Care mgmt", "txt": "Chronic disease management enrollment for declined + at-risk members.", "sub": "Ongoing", "lift": "+2-3pp", "status": "Planning"},
            {"team": "Benefits", "txt": "SilverSneakers / Silver&Fit enrollment for at-risk and maintained members.", "sub": "Week 3-6", "lift": "+1-2pp", "status": "Active"},
            {"team": "Outreach", "txt": "Engage non-responders — high + medium likelihood only.", "sub": "Pre-survey window", "lift": "+5pp response rate", "status": "Scheduled"},
        ],
        "urgency_factors": [],
    },
    "ment": {
        "id": "ment", "name": "Improving / maintaining mental health",
        "type": "Outcome measure · 2-year longitudinal · SF-36 MCS · Returns to full weight 2026",
        "badge": "AT RISK", "rate": 74.0, "cut4": 78.0, "stars": 3.5,
        "needed": 40, "eligible": 3100, "documented": 1837, "open_gap": 643,
        "survey": {"sent": 3200, "responded": 2180, "no": 570, "no_resp": 470},
        "awv": {"pct": 54, "note": "AWV includes PHQ-9 depression screening — key trigger for mental health care navigation."},
        "questions": [
            {"q": "Compared to 2 years ago, how would you rate your mental or emotional health in general?", "proxy": "Has your emotional health improved or stayed the same?", "rule": "Better / Same = top box", "pct": 74},
            {"q": "In the last 4 weeks, how much of the time did you feel calm and peaceful?", "proxy": "Feeling calm and in control lately?", "rule": "Most / All of the time = top box", "pct": 73},
        ],
        "steps": [
            {"title": "Stratify all members by MCS trajectory", "desc": "Agent uses HOS MCS scores + claims + pulse survey to classify members.", "result": "Declined: 280 · At-risk: 760 · Non-resp: 470"},
            {"title": "Identify members with PHQ-9 elevation", "desc": "Cross-references behavioral health claims for members with PHQ-9 elevation in last 12 months.", "result": "312 members with depression risk flag"},
            {"title": "Monthly MCS trajectory scorecard", "desc": "MCS trend per member flagged for rapid decliners (>5pt drop) for immediate outreach priority.", "result": "48 rapid decliners flagged urgent"},
        ],
        "actions": [
            {"team": "Behavioral", "txt": "Mental health screening + care navigation for members with declining MCS scores.", "sub": "Week 4-8", "lift": "+1-2pp", "status": "Planning"},
            {"team": "Care mgmt", "txt": "Chronic disease management for members with comorbidities contributing to mental health decline.", "sub": "Ongoing", "lift": "+1-2pp", "status": "Planning"},
            {"team": "Outreach", "txt": "Engage non-responders — high + medium likelihood only.", "sub": "Pre-survey window", "lift": "+5pp response rate", "status": "Scheduled"},
        ],
        "urgency_factors": [],
    },
    "pact": {
        "id": "pact", "name": "Physical activity",
        "type": "Process measure · Survey-based · Provider conversation at visit",
        "badge": "ON TRACK", "rate": 81.0, "cut4": 79.0, "stars": 4.0,
        "needed": 0, "eligible": 4200, "documented": 3402, "open_gap": 798,
        "survey": {"sent": 3100, "responded": 2340, "no": 390, "no_resp": 370},
        "awv": {"pct": 54, "note": "798 members with no wellness visit = 798 missed physical activity advice opportunities. Closing AWV gaps directly closes this measure."},
        "questions": [
            {"q": "In the last 6 months, did your personal doctor talk with you about exercise or physical activity?", "proxy": "Did your doctor discuss exercise with you?", "rule": "Yes = top box", "pct": 81},
        ],
        "steps": [
            {"title": "Identify members with no physical activity conversation documented", "desc": "Checks claims for physical activity counseling CPT codes and EHR notes.", "result": "798 members with no wellness visit"},
            {"title": "Provider scorecard — % of patients receiving advice", "desc": "28 providers scored. 6 below 75% rate flagged.", "result": "6 providers below 75% target"},
        ],
        "actions": [
            {"team": "Care mgmt", "txt": "Schedule annual wellness visits for 798 no-visit members.", "sub": "Monthly", "lift": "+1-2pp", "status": "Active"},
            {"team": "Outreach", "txt": "Pre-survey reminder to reinforce physical activity conversation recall.", "sub": "Pre-survey", "lift": "+1-2pp", "status": "Scheduled"},
        ],
        "urgency_factors": [],
    },
}

_FIRST_NAMES = ["Dorothy","Harold","Margaret","Robert","Evelyn","James","Shirley","Arthur","Betty","Charles","Patricia","Richard","Helen","Edward","Ruth","William","Frances","George","Martha","Thomas","Barbara","Frank","Virginia","Henry","Eleanor","Donald","Mildred","Kenneth","Gladys","Eugene"]
_LAST_NAMES = ["Simmons","Greene","Fowler","Kline","Torres","Whitfield","Nguyen","Collins","Warren","Mitchell","Reynolds","Cooper","Sanders","Murphy","Brooks","Reed","Bennett","Morgan","Hayes","Graham","Fisher","Powell","Long","Patterson","Hughes","Butler","Foster","Barnes","Ross","Henderson"]
_COMORBIDITIES_LIST = ["Osteoporosis","Type 2 Diabetes","Hypertension","Vision impairment","Vestibular disorder","Depression (mild)","COPD","Heart failure","Neuropathy","Parkinson's"]
_FLAGS = ["Fall ICD W19 · No discussion","Balance issue · No discussion","Fall ICD W01 · No discussion","Multiple falls · No discussion","Fall ICD W18 · No discussion","Fall history · No discussion"]
_CHANNELS = ["Phone","Phone+Mail","Mail","Phone+Email","Email"]
_TEAMS = ["Care mgmt","Outreach"]
_STATUSES = ["In progress","Not started","Complete","Scheduled"]
_ASSIGNED = ["J. Martinez","S. Patel","K. Brown","L. Chen","M. Davis","Unassigned"]

def _generate_members(contract_id: str, measure_id: str, count: int):
    seed = hashlib.md5(f"{contract_id}-{measure_id}".encode()).hexdigest()
    rng = random.Random(seed)
    members = []
    for i in range(count):
        age = rng.randint(65, 92)
        awv = rng.random() < 0.45
        urgency = rng.randint(15, 98)
        risk = "High" if urgency >= 70 else "Medium" if urgency >= 40 else "Low"
        handler = "Care mgmt" if urgency >= 55 else "Outreach"
        n_comorb = rng.randint(0, 3)
        comorbidities = rng.sample(_COMORBIDITIES_LIST, min(n_comorb, len(_COMORBIDITIES_LIST)))
        homebound = rng.random() < 0.05
        mock = rng.choice(["No", "Yes", "No response"])
        attempts = rng.randint(0, 4)
        last_contact = rng.choice(["May 1","May 2","May 3","May 4","May 5","Apr 28","Apr 30","—"])
        last_visit = rng.choice(["Jan 15","Feb 10","Feb 28","Mar 5","Mar 12","Apr 2","Apr 15","Apr 18"])
        fname = _FIRST_NAMES[i % len(_FIRST_NAMES)]
        lname = _LAST_NAMES[i % len(_LAST_NAMES)]
        open_gaps = [_MEASURES[measure_id]["name"]]
        if rng.random() < 0.3:
            extras = ["Fall Risk","Monitoring","Physical Health","Mental Health"]
            open_gaps.append(rng.choice(extras))
        members.append({
            "id": f"M-{10000 + i * 111 + rng.randint(0,50)}",
            "name": f"{fname} {lname}",
            "age": age,
            "awv": awv,
            "risk": risk,
            "urgency": urgency,
            "open_gaps": open_gaps,
            "handler": handler,
            "assigned": rng.choice(_ASSIGNED),
            "status": rng.choice(_STATUSES),
            "flag": rng.choice(_FLAGS),
            "channel": rng.choice(_CHANNELS),
            "attempts": attempts,
            "last_contact": last_contact,
            "mock_survey": mock,
            "last_visit": last_visit,
            "comorbidities": comorbidities,
            "homebound": homebound,
        })
    members.sort(key=lambda m: -m["urgency"])
    return members

def _generate_providers(contract_id: str, measure_id: str, members: list):
    seed = hashlib.md5(f"prov-{contract_id}-{measure_id}".encode()).hexdigest()
    rng = random.Random(seed)
    provider_names = [
        "Dr. Rachel Kim","Dr. Samuel Okonkwo","Dr. Linda Marsh","Dr. James Chen",
        "Dr. Maria Garcia","Dr. David Park","Dr. Sarah Wilson","Dr. Michael Brown",
        "Dr. Jennifer Lee","Dr. Robert Taylor","Dr. Amanda White","Dr. Christopher Moore",
        "Dr. Patricia Davis","Dr. Kevin Johnson",
    ]
    providers = []
    idx = 0
    for i, pname in enumerate(provider_names):
        count = rng.randint(15, 55)
        pts = members[idx:idx+min(3, len(members)-idx)] if idx < len(members) else []
        idx += len(pts)
        providers.append({"name": pname, "patient_count": count, "patients": pts})
    return providers


@router.get("/hos/measures")
def get_hos_measures(contract_id: str = Query("H3312")):
    try:
        rows = query(f"""
            SELECT m.measure_id, m.measure_name, m.measure_type, m.badge,
                   s.current_rate, s.cut_4star, s.star_rating, s.members_needed,
                   s.eligible_count, s.documented_count, s.open_gap_count,
                   s.survey_sent, s.survey_responded, s.survey_no, s.survey_no_resp,
                   s.awv_pct, s.awv_note
            FROM aiagenticdemo.stars_gold.gold_hos_measures m
            JOIN aiagenticdemo.stars_gold.gold_hos_scorecard s
              ON m.measure_id = s.measure_id AND s.contract_id = '{contract_id}'
            WHERE s.measurement_year = 2025
            ORDER BY s.current_rate ASC
        """)
        if rows:
            result = {}
            for r in rows:
                mid = r["measure_id"]
                fb = _MEASURES.get(mid, {})
                result[mid] = {
                    "id": mid,
                    "name": r["measure_name"],
                    "type": r["measure_type"],
                    "badge": r["badge"],
                    "rate": float(r["current_rate"]),
                    "cut4": float(r["cut_4star"]),
                    "stars": float(r["star_rating"]),
                    "needed": int(r["members_needed"]),
                    "eligible": int(r["eligible_count"]),
                    "documented": int(r["documented_count"]),
                    "open_gap": int(r["open_gap_count"]),
                    "survey": {"sent": int(r["survey_sent"]), "responded": int(r["survey_responded"]), "no": int(r["survey_no"]), "no_resp": int(r["survey_no_resp"])},
                    "awv": {"pct": int(r["awv_pct"]), "note": r["awv_note"]},
                    "questions": fb.get("questions", []),
                    "steps": fb.get("steps", []),
                    "actions": fb.get("actions", []),
                    "urgency_factors": fb.get("urgency_factors", []),
                }
            return {"source": "live", "measures": result}
    except Exception:
        pass
    return {"source": "fallback", "measures": _MEASURES}


@router.get("/hos/members")
def get_hos_members(
    contract_id: str = Query("H3312"),
    measure_id: str = Query("fall"),
    risk_filter: str = Query("all"),
    handler_filter: str = Query("all"),
    page: int = Query(1),
    page_size: int = Query(25),
):
    m = _MEASURES.get(measure_id)
    count = m["open_gap"] if m else 50
    count = min(count, 200)
    try:
        rows = query(f"""
            SELECT member_id, member_name, age, awv_completed, risk_level,
                   urgency_score, open_gaps, handler, assigned_to, status,
                   flag_reason, channel, contact_attempts, last_contact,
                   mock_survey_response, last_provider_visit,
                   comorbidities, homebound
            FROM aiagenticdemo.stars_gold.gold_hos_members
            WHERE contract_id = '{contract_id}' AND measure_id = '{measure_id}'
              AND measurement_year = 2025
            ORDER BY urgency_score DESC
        """)
        if rows:
            members = []
            for r in rows:
                members.append({
                    "id": r["member_id"], "name": r["member_name"], "age": int(r["age"]),
                    "awv": bool(r["awv_completed"]), "risk": r["risk_level"],
                    "urgency": int(r["urgency_score"]),
                    "open_gaps": r["open_gaps"].split(",") if isinstance(r["open_gaps"], str) else r["open_gaps"],
                    "handler": r["handler"], "assigned": r["assigned_to"],
                    "status": r["status"], "flag": r["flag_reason"],
                    "channel": r["channel"], "attempts": int(r["contact_attempts"]),
                    "last_contact": r["last_contact"], "mock_survey": r["mock_survey_response"],
                    "last_visit": r["last_provider_visit"],
                    "comorbidities": r["comorbidities"].split(",") if isinstance(r["comorbidities"], str) else (r["comorbidities"] or []),
                    "homebound": bool(r["homebound"]),
                })
            filtered = members
            if risk_filter != "all":
                filtered = [m for m in filtered if m["risk"].lower() == risk_filter.lower()]
            if handler_filter != "all":
                filtered = [m for m in filtered if handler_filter.lower() in m["handler"].lower()]
            total = len(filtered)
            start = (page - 1) * page_size
            sliced = filtered[start:start + page_size]
            return {"source": "live", "members": sliced, "total": total, "page": page, "page_size": page_size}
    except Exception:
        pass

    members = _generate_members(contract_id, measure_id, count)
    if risk_filter != "all":
        members = [m for m in members if m["risk"].lower() == risk_filter.lower()]
    if handler_filter != "all":
        members = [m for m in members if handler_filter.lower() in m["handler"].lower()]
    total = len(members)
    start = (page - 1) * page_size
    sliced = members[start:start + page_size]
    return {"source": "fallback", "members": sliced, "total": total, "page": page, "page_size": page_size}


@router.get("/hos/providers")
def get_hos_providers(contract_id: str = Query("H3312"), measure_id: str = Query("fall")):
    try:
        rows = query(f"""
            SELECT provider_name, open_gap_count
            FROM aiagenticdemo.stars_gold.gold_hos_provider_scorecard
            WHERE contract_id = '{contract_id}' AND measure_id = '{measure_id}'
              AND measurement_year = 2025
            ORDER BY open_gap_count DESC
        """)
        if rows:
            return {"source": "live", "providers": [{"name": r["provider_name"], "patient_count": int(r["open_gap_count"]), "patients": []} for r in rows]}
    except Exception:
        pass
    m = _MEASURES.get(measure_id)
    count = min(m["open_gap"] if m else 50, 200)
    members = _generate_members(contract_id, measure_id, count)
    providers = _generate_providers(contract_id, measure_id, members)
    return {"source": "fallback", "providers": providers}


@router.get("/hos/summary")
def get_hos_summary(contract_id: str = Query("H3312")):
    try:
        rows = query(f"""
            SELECT AVG(s.star_rating) as avg_star,
                   SUM(CASE WHEN s.current_rate < s.cut_4star THEN 1 ELSE 0 END) as below_cut,
                   COUNT(*) as total_measures,
                   SUM(s.open_gap_count) as total_gaps,
                   AVG(s.awv_pct) as avg_awv
            FROM aiagenticdemo.stars_gold.gold_hos_scorecard s
            WHERE s.contract_id = '{contract_id}' AND s.measurement_year = 2025
        """)
        if rows and rows[0].get("avg_star"):
            r = rows[0]
            avg_awv_val = int(r["avg_awv"])
            avg_star_val = round(float(r["avg_star"]), 1)
            return {
                "source": "live",
                "avg_star": avg_star_val,
                "below_cut": int(r["below_cut"]),
                "total_measures": int(r["total_measures"]),
                "total_gaps": int(r["total_gaps"]),
                "avg_awv": avg_awv_val,
                "awv_completion": avg_awv_val,
                "no_awv": max(0, int(round((100 - avg_awv_val) * int(r["total_gaps"]) / 100))) if r.get("total_gaps") else 945,
                "projected_star": round(min(5.0, avg_star_val + 0.6), 1),
                "survey_window_weeks": 10,
            }
    except Exception:
        pass
    total_gaps = sum(m["open_gap"] for m in _MEASURES.values())
    below = sum(1 for m in _MEASURES.values() if m["rate"] < m["cut4"])
    avg_star = round(sum(m["stars"] for m in _MEASURES.values()) / len(_MEASURES), 1)
    return {
        "source": "fallback",
        "avg_star": avg_star,
        "below_cut": below,
        "total_measures": len(_MEASURES),
        "total_gaps": total_gaps,
        "avg_awv": 54,
        "awv_completion": 54,
        "no_awv": 945,
        "projected_star": round(min(5.0, avg_star + 0.6), 1),
        "survey_window_weeks": 10,
    }
