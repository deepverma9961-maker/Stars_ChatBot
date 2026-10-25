# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Gold Layer: HOS (Health Outcomes Survey) Tables
# MAGIC Creates four tables for the HOS Measures page:
# MAGIC - `gold_hos_measures` — 5 HOS measure definitions
# MAGIC - `gold_hos_scorecard` — measure-level rates, gaps, and survey stats per contract
# MAGIC - `gold_hos_members` — member-level gap registry with urgency scores
# MAGIC - `gold_hos_provider_scorecard` — provider-level gap counts per measure

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, LongType, BooleanType
)
import random, hashlib

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. HOS Measure Definitions

# COMMAND ----------
MEASURES = {
    "fall": {
        "name": "Fall risk management",
        "type": "Process measure · Survey-based · Fall history members only",
    },
    "mon": {
        "name": "Monitoring physical activity",
        "type": "Process measure · Survey-based · Linked to physical activity",
    },
    "phys": {
        "name": "Improving / maintaining physical health",
        "type": "Outcome measure · 2-year longitudinal · SF-36 PCS · Returns to full weight 2026",
    },
    "ment": {
        "name": "Improving / maintaining mental health",
        "type": "Outcome measure · 2-year longitudinal · SF-36 MCS · Returns to full weight 2026",
    },
    "pact": {
        "name": "Physical activity",
        "type": "Process measure · Survey-based · Provider conversation at visit",
    },
}

measure_rows = []
for mid, mdef in MEASURES.items():
    badge = "CRITICAL" if mid in ("fall", "mon") else ("ON TRACK" if mid == "pact" else "AT RISK")
    measure_rows.append(Row(
        measure_id=mid,
        measure_name=mdef["name"],
        measure_type=mdef["type"],
        badge=badge,
    ))

measure_schema = StructType([
    StructField("measure_id", StringType(), False),
    StructField("measure_name", StringType(), True),
    StructField("measure_type", StringType(), True),
    StructField("badge", StringType(), True),
])

spark.createDataFrame(measure_rows, measure_schema) \
    .write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.stars_gold.gold_hos_measures")

print(f"gold_hos_measures: {len(measure_rows)} rows")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. HOS Scorecard (per contract × measure)

# COMMAND ----------
# H3312 reference values (match hos_v2.html exactly)
H3312_REF = {
    "fall": {"rate": 76.0, "cut4": 78.0, "stars": 3.0, "needed": 10, "eligible": 1260, "documented": 958, "open_gap": 302,
             "survey_sent": 820, "survey_responded": 512, "survey_no": 184, "survey_no_resp": 124,
             "awv_pct": 48, "awv_note": "655 members with no AWV — scheduling a visit closes the fall gap at the same appointment via CPT G0438/G0439."},
    "mon":  {"rate": 69.0, "cut4": 71.0, "stars": 3.0, "needed": 22, "eligible": 3402, "documented": 2348, "open_gap": 1054,
             "survey_sent": 2100, "survey_responded": 1380, "survey_no": 487, "survey_no_resp": 233,
             "awv_pct": 54, "awv_note": "AWV return visit is the natural moment to discuss physical activity progress and document the follow-up conversation."},
    "phys": {"rate": 72.0, "cut4": 76.0, "stars": 3.5, "needed": 40, "eligible": 3100, "documented": 1786, "open_gap": 694,
             "survey_sent": 3200, "survey_responded": 2180, "survey_no": 620, "survey_no_resp": 470,
             "awv_pct": 54, "awv_note": "AWV enables chronic disease management, PT/OT referrals, fitness enrollment, depression screening — all in one visit."},
    "ment": {"rate": 74.0, "cut4": 78.0, "stars": 3.5, "needed": 40, "eligible": 3100, "documented": 1837, "open_gap": 643,
             "survey_sent": 3200, "survey_responded": 2180, "survey_no": 570, "survey_no_resp": 470,
             "awv_pct": 54, "awv_note": "AWV includes PHQ-9 depression screening — key trigger for mental health care navigation."},
    "pact": {"rate": 81.0, "cut4": 79.0, "stars": 4.0, "needed": 0, "eligible": 4200, "documented": 3402, "open_gap": 798,
             "survey_sent": 3100, "survey_responded": 2340, "survey_no": 390, "survey_no_resp": 370,
             "awv_pct": 54, "awv_note": "798 members with no wellness visit = 798 missed physical activity advice opportunities."},
}

# Contract offsets for variation (same as gold_measure_scorecard)
STAR_OFFSET = {
    "H3312": 0.0, "H5521": -7.0, "H2213": 6.0, "H6614": 2.0,
    "H7723": -3.0, "H8812": 1.0, "H9914": -8.0, "H1045": -12.0,
    "H2156": 2.5, "H3267": 5.0, "H4378": -5.0, "H5489": 8.0,
    "H6590": 1.0, "H7601": 1.5,
}

# Load plans from silver
plans = spark.table(f"{CATALOG}.stars_silver.silver_plan").collect()
contract_ids = [p.contract_id for p in plans if not p.contract_id.endswith("B")]

scorecard_rows = []
for cid in contract_ids:
    offset = STAR_OFFSET.get(cid, 0.0)
    rng = random.Random(hash(cid) + 777)
    for mid, ref in H3312_REF.items():
        if cid == "H3312":
            r = ref
            rate = r["rate"]
            cut4 = r["cut4"]
            stars = r["stars"]
            needed = r["needed"]
            eligible = r["eligible"]
            documented = r["documented"]
            open_gap = r["open_gap"]
            sv_sent = r["survey_sent"]
            sv_resp = r["survey_responded"]
            sv_no = r["survey_no"]
            sv_noresp = r["survey_no_resp"]
            awv_pct = r["awv_pct"]
            awv_note = r["awv_note"]
        else:
            rate = round(min(98, max(40, ref["rate"] + offset * 0.6 + rng.gauss(0, 2))), 1)
            cut4 = ref["cut4"]
            stars = 4.0 if rate >= cut4 else (3.5 if rate >= cut4 - 4 else 3.0)
            gap_pp = max(0, cut4 - rate)
            eligible = max(500, int(ref["eligible"] * (1 + rng.uniform(-0.3, 0.3))))
            documented = int(eligible * rate / 100)
            open_gap = eligible - documented
            needed = max(0, int(gap_pp / 100 * eligible)) if gap_pp > 0 else 0
            ratio = eligible / max(1, ref["eligible"])
            sv_sent = int(ref["survey_sent"] * ratio * rng.uniform(0.85, 1.15))
            sv_resp = int(sv_sent * rng.uniform(0.55, 0.7))
            sv_no = int(sv_resp * rng.uniform(0.2, 0.4))
            sv_noresp = int(sv_sent * rng.uniform(0.1, 0.2))
            awv_pct = max(30, min(80, int(ref["awv_pct"] + offset * 0.8 + rng.gauss(0, 3))))
            awv_note = ref["awv_note"]

        badge = "CRITICAL" if rate < cut4 - 1 and mid in ("fall", "mon") else (
            "ON TRACK" if rate >= cut4 else "AT RISK"
        )

        scorecard_rows.append(Row(
            scorecard_key=f"HOS-{cid}-{mid}-{YEAR}",
            contract_id=cid,
            measure_id=mid,
            measurement_year=YEAR,
            current_rate=float(rate),
            cut_4star=float(cut4),
            star_rating=float(stars),
            members_needed=int(needed),
            eligible_count=int(eligible),
            documented_count=int(documented),
            open_gap_count=int(open_gap),
            survey_sent=int(sv_sent),
            survey_responded=int(sv_resp),
            survey_no=int(sv_no),
            survey_no_resp=int(sv_noresp),
            awv_pct=int(awv_pct),
            awv_note=str(awv_note),
            badge=str(badge),
            last_updated="2025-06-10",
        ))

scorecard_schema = StructType([
    StructField("scorecard_key", StringType(), False),
    StructField("contract_id", StringType(), True),
    StructField("measure_id", StringType(), True),
    StructField("measurement_year", IntegerType(), True),
    StructField("current_rate", DoubleType(), True),
    StructField("cut_4star", DoubleType(), True),
    StructField("star_rating", DoubleType(), True),
    StructField("members_needed", IntegerType(), True),
    StructField("eligible_count", IntegerType(), True),
    StructField("documented_count", IntegerType(), True),
    StructField("open_gap_count", IntegerType(), True),
    StructField("survey_sent", IntegerType(), True),
    StructField("survey_responded", IntegerType(), True),
    StructField("survey_no", IntegerType(), True),
    StructField("survey_no_resp", IntegerType(), True),
    StructField("awv_pct", IntegerType(), True),
    StructField("awv_note", StringType(), True),
    StructField("badge", StringType(), True),
    StructField("last_updated", StringType(), True),
])

spark.createDataFrame(scorecard_rows, scorecard_schema) \
    .write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.stars_gold.gold_hos_scorecard")

print(f"gold_hos_scorecard: {len(scorecard_rows)} rows")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. HOS Members (member-level gap registry with urgency scores)

# COMMAND ----------
FIRST_NAMES = [
    "Dorothy","Harold","Margaret","Robert","Evelyn","James","Shirley","Arthur",
    "Betty","Charles","Patricia","Richard","Helen","Edward","Ruth","William",
    "Frances","George","Martha","Thomas","Barbara","Frank","Virginia","Henry",
    "Eleanor","Donald","Mildred","Kenneth","Gladys","Eugene","Alice","Raymond",
    "Josephine","Walter","Marie","Carl","Rose","Ernest","Lucille","Lawrence",
    "Edna","Herbert","Lillian","Fred","Ethel","Ralph","Gertrude","Howard",
    "Florence","Louis",
]
LAST_NAMES = [
    "Simmons","Greene","Fowler","Kline","Torres","Whitfield","Nguyen","Collins",
    "Warren","Mitchell","Reynolds","Cooper","Sanders","Murphy","Brooks","Reed",
    "Bennett","Morgan","Hayes","Graham","Fisher","Powell","Long","Patterson",
    "Hughes","Butler","Foster","Barnes","Ross","Henderson","Coleman","Perry",
    "Russell","Griffin","Diaz","Price","Rivera","Campbell","Parker","Evans",
    "Stewart","Adams","Turner","Hernandez","Lopez","Gonzalez","Nelson","Carter",
    "Robinson","Clark",
]
COMORBIDITIES = ["Osteoporosis","Type 2 Diabetes","Hypertension","Vision impairment",
                 "Vestibular disorder","Depression (mild)","COPD","Heart failure",
                 "Neuropathy","Parkinson's"]
FLAGS = ["Fall ICD W19 · No discussion","Balance issue · No discussion",
         "Fall ICD W01 · No discussion","Multiple falls · No discussion",
         "Fall ICD W18 · No discussion","Fall history · No discussion",
         "No follow-up documented","Activity advice not documented",
         "PCS declining · No intervention","MCS declining · No screening",
         "No wellness visit in 12m"]
CHANNELS = ["Phone","Phone+Mail","Mail","Phone+Email","Email"]
ASSIGNED = ["J. Martinez","S. Patel","K. Brown","L. Chen","M. Davis",
            "R. Johnson","A. Williams","T. Garcia","N. Lee","Unassigned"]
STATUSES = ["In progress","Not started","Complete","Scheduled"]
MOCK_RESPONSES = ["No","Yes","No response"]

member_rows = []
for cid in contract_ids:
    for mid in H3312_REF:
        ref = H3312_REF[mid]
        if cid == "H3312":
            member_count = min(ref["open_gap"], 200)
        else:
            rng_count = random.Random(hash(f"{cid}-{mid}") + 333)
            base_gap = ref["open_gap"]
            offset_c = STAR_OFFSET.get(cid, 0.0)
            member_count = min(200, max(30, int(base_gap * (1 + offset_c * 0.02) * rng_count.uniform(0.6, 1.4))))

        seed = hashlib.md5(f"{cid}-{mid}".encode()).hexdigest()
        rng = random.Random(seed)

        for i in range(member_count):
            age = rng.randint(65, 92)
            awv = rng.random() < 0.45
            # urgency_score is a placeholder here; notebook
            # `16_ml_hos_urgency.py` overwrites it (and risk_level / handler)
            # with the trained RandomForestRegressor's prediction.
            urgency = 50
            risk = "Medium"
            handler = "Outreach"
            n_comorb = rng.randint(0, 3)
            comorbidities = ",".join(rng.sample(COMORBIDITIES, min(n_comorb, len(COMORBIDITIES))))
            homebound = rng.random() < 0.05
            mock = rng.choice(MOCK_RESPONSES)
            attempts = rng.randint(0, 4)
            last_contact = rng.choice(["May 1","May 2","May 3","May 4","May 5","Apr 28","Apr 30","—"])
            last_visit = rng.choice(["Jan 15","Feb 10","Feb 28","Mar 5","Mar 12","Apr 2","Apr 15","Apr 18"])
            fname = FIRST_NAMES[i % len(FIRST_NAMES)]
            lname = LAST_NAMES[i % len(LAST_NAMES)]
            mid_val = f"{mid.upper()[:3]}"
            open_gaps = MEASURES[mid]["name"]
            if rng.random() < 0.25:
                extras = ["Fall Risk","Monitoring","Physical Health","Mental Health"]
                open_gaps += "," + rng.choice(extras)
            flag = rng.choice(FLAGS)

            member_rows.append(Row(
                member_key=f"HM-{cid}-{mid}-{i:05d}",
                member_id=f"M-{10000 + i * 111 + rng.randint(0, 50)}",
                member_name=f"{fname} {lname}",
                contract_id=cid,
                measure_id=mid,
                measurement_year=YEAR,
                age=age,
                awv_completed=awv,
                risk_level=risk,
                urgency_score=urgency,
                open_gaps=open_gaps,
                handler=handler,
                assigned_to=rng.choice(ASSIGNED),
                status=rng.choice(STATUSES),
                flag_reason=flag,
                channel=rng.choice(CHANNELS),
                contact_attempts=attempts,
                last_contact=last_contact,
                mock_survey_response=mock,
                last_provider_visit=last_visit,
                comorbidities=comorbidities,
                homebound=homebound,
            ))

member_schema = StructType([
    StructField("member_key", StringType(), False),
    StructField("member_id", StringType(), True),
    StructField("member_name", StringType(), True),
    StructField("contract_id", StringType(), True),
    StructField("measure_id", StringType(), True),
    StructField("measurement_year", IntegerType(), True),
    StructField("age", IntegerType(), True),
    StructField("awv_completed", BooleanType(), True),
    StructField("risk_level", StringType(), True),
    StructField("urgency_score", IntegerType(), True),
    StructField("open_gaps", StringType(), True),
    StructField("handler", StringType(), True),
    StructField("assigned_to", StringType(), True),
    StructField("status", StringType(), True),
    StructField("flag_reason", StringType(), True),
    StructField("channel", StringType(), True),
    StructField("contact_attempts", IntegerType(), True),
    StructField("last_contact", StringType(), True),
    StructField("mock_survey_response", StringType(), True),
    StructField("last_provider_visit", StringType(), True),
    StructField("comorbidities", StringType(), True),
    StructField("homebound", BooleanType(), True),
])

spark.createDataFrame(member_rows, member_schema) \
    .write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.stars_gold.gold_hos_members")

print(f"gold_hos_members: {len(member_rows)} rows")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. HOS Provider Scorecard

# COMMAND ----------
PROVIDER_NAMES = [
    "Dr. Rachel Kim","Dr. Samuel Okonkwo","Dr. Linda Marsh","Dr. James Chen",
    "Dr. Maria Garcia","Dr. David Park","Dr. Sarah Wilson","Dr. Michael Brown",
    "Dr. Jennifer Lee","Dr. Robert Taylor","Dr. Amanda White","Dr. Christopher Moore",
    "Dr. Patricia Davis","Dr. Kevin Johnson","Dr. Nancy Clark","Dr. Steven Hall",
    "Dr. Karen Allen","Dr. Brian Young","Dr. Laura King","Dr. Daniel Wright",
]

provider_rows = []
for cid in contract_ids:
    for mid in H3312_REF:
        seed = hashlib.md5(f"prov-{cid}-{mid}".encode()).hexdigest()
        rng = random.Random(seed)
        n_providers = rng.randint(8, 20)
        for pidx in range(n_providers):
            pname = PROVIDER_NAMES[pidx % len(PROVIDER_NAMES)]
            gap_count = rng.randint(10, 60)
            provider_rows.append(Row(
                provider_key=f"HP-{cid}-{mid}-{pidx:03d}",
                provider_name=pname,
                contract_id=cid,
                measure_id=mid,
                measurement_year=YEAR,
                open_gap_count=gap_count,
            ))

provider_schema = StructType([
    StructField("provider_key", StringType(), False),
    StructField("provider_name", StringType(), True),
    StructField("contract_id", StringType(), True),
    StructField("measure_id", StringType(), True),
    StructField("measurement_year", IntegerType(), True),
    StructField("open_gap_count", IntegerType(), True),
])

spark.createDataFrame(provider_rows, provider_schema) \
    .write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.stars_gold.gold_hos_provider_scorecard")

print(f"gold_hos_provider_scorecard: {len(provider_rows)} rows")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Summary
# MAGIC Tables created:
# MAGIC - `gold_hos_measures` — 5 HOS measure definitions
# MAGIC - `gold_hos_scorecard` — measure rates/gaps per contract (14 contracts × 5 measures = 70 rows)
# MAGIC - `gold_hos_members` — member-level urgency-scored gap registry (~14k rows)
# MAGIC - `gold_hos_provider_scorecard` — provider gap counts (~1k rows)

# COMMAND ----------
for tbl in ["gold_hos_measures", "gold_hos_scorecard", "gold_hos_members", "gold_hos_provider_scorecard"]:
    cnt = spark.table(f"{CATALOG}.stars_gold.{tbl}").count()
    print(f"  {tbl}: {cnt:,} rows")
