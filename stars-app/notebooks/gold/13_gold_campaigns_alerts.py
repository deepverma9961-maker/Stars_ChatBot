# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Gold Layer: Campaigns, Alerts, Interventions
# MAGIC Creates `gold_campaign_performance`, `gold_alert_priority`, `gold_intervention_hub`.

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, DoubleType, BooleanType
import random, uuid

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# --- gold_campaign_performance ---
# Seed 7 HTML campaigns + expand to 180 total
BASE_CAMPAIGNS = [
    ("COL Outreach Wave 1",   "COL",  "Call",  312, 87,  94,  3.1, 6864,  4.8, "Completed", "2025-03-01", "2025-04-15"),
    ("SPC SMS Blitz",          "SPC",  "SMS",   248, 55,  61,  2.4, 992,   6.2, "Completed", "2025-03-15", "2025-04-30"),
    ("AMM Email + Incentive",  "AMM",  "Email", 189, 23,  None, 1.8, 378,  None,"Active",    "2025-05-01", None),
    ("FLU Rapid Response",     "FLU",  "Call",  445, 124, 118, 4.2, 9790,  3.9, "Completed", "2025-01-15", "2025-03-01"),
    ("CDC Priority Call",      "HBD",  "Call",  167, 47,  None, 2.1, 3674, None,"Active",    "2025-05-15", None),
    ("KED Targeted SMS",       "KED",  "SMS",   203, 45,  48,  2.8, 812,   5.7, "Completed", "2025-02-01", "2025-03-31"),
    ("CBP High-Risk Wave",     "CBP",  "Call",  289, 81,  None, 3.4, 6358, None,"Active",    "2025-05-20", None),
]

MEASURES = ["COL","CBP","KED","AMM","OMW","HBD","SPC","BCS","EED","MRP","TRC","PCR"]
CHANNELS = ["Call","SMS","Email"]
MONTHS = ["2024-07","2024-08","2024-09","2024-10","2024-11","2024-12","2025-01","2025-02","2025-03","2025-04"]

campaign_rows = []
for name, mcode, chan, members, proj, actual, lift, cost, roi, status, start, end in BASE_CAMPAIGNS:
    campaign_rows.append(Row(
        campaign_key=str(uuid.uuid4()),
        campaign_name=name,
        measure_code=mcode,
        primary_channel=chan,
        member_count=members,
        projected_closures=proj,
        actual_closures=actual,
        lift_pct=lift,
        total_cost=float(cost),
        roi_multiplier=roi,
        campaign_status=status,
        campaign_start_date=start,
        campaign_end_date=end,
        measurement_year=YEAR,
    ))

# Generate 173 more historical campaigns
rng = random.Random(42)
for i in range(173):
    mcode = rng.choice(MEASURES)
    chan = rng.choice(CHANNELS)
    members_cnt = rng.randint(80, 500)
    proj = round(members_cnt * rng.uniform(0.18, 0.32))
    actual = round(proj * rng.uniform(0.85, 1.15))
    lift = round(rng.uniform(0.8, 5.5), 1)
    cost = round(members_cnt * {"Call": 22, "SMS": 4, "Email": 2}[chan] * rng.uniform(0.8, 1.2))
    roi = round(cost / max(1, actual * 150) * rng.uniform(2, 8), 1) if actual else None
    month = rng.choice(MONTHS)
    start_date = f"{month}-{rng.randint(1,15):02d}"
    campaign_rows.append(Row(
        campaign_key=str(uuid.uuid4()),
        campaign_name=f"{mcode} {chan} Wave {i+8}",
        measure_code=mcode,
        primary_channel=chan,
        member_count=members_cnt,
        projected_closures=proj,
        actual_closures=actual,
        lift_pct=lift,
        total_cost=float(cost),
        roi_multiplier=roi,
        campaign_status="Completed",
        campaign_start_date=start_date,
        campaign_end_date=f"{month}-{rng.randint(16,28):02d}",
        measurement_year=YEAR,
    ))

_camp_schema = StructType([
    StructField("campaign_key",        StringType(),  False),
    StructField("campaign_name",       StringType(),  True),
    StructField("measure_code",        StringType(),  True),
    StructField("primary_channel",     StringType(),  True),
    StructField("member_count",        LongType(),    True),
    StructField("projected_closures",  LongType(),    True),
    StructField("actual_closures",     LongType(),    True),
    StructField("lift_pct",            DoubleType(),  True),
    StructField("total_cost",          DoubleType(),  True),
    StructField("roi_multiplier",      DoubleType(),  True),
    StructField("campaign_status",     StringType(),  True),
    StructField("campaign_start_date", StringType(),  True),
    StructField("campaign_end_date",   StringType(),  True),
    StructField("measurement_year",    IntegerType(), True),
])
spark.createDataFrame(campaign_rows, _camp_schema).write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.stars_gold.gold_campaign_performance")
print(f"gold_campaign_performance: {len(campaign_rows)} rows")

# COMMAND ----------
# --- gold_alert_priority ---
measures = spark.table(f"{CATALOG}.stars_silver.silver_measure").collect()
scorecard = spark.table(f"{CATALOG}.stars_gold.gold_measure_scorecard").filter(
    "measurement_year = 2025 AND plan_key IN (SELECT plan_key FROM aiagenticdemo.stars_silver.silver_plan WHERE contract_id = 'H3312')"
).collect()

measure_map = {m.measure_key: m for m in measures}
alert_rows = []

for sc in scorecard:
    m = measure_map.get(sc.measure_key)
    if not m or m.measure_category not in ("HEDIS", "CAHPS"):
        continue
    gap = sc.target_rate - sc.current_rate
    if gap > 15:
        severity = "critical"
    elif gap > 5:
        severity = "warning"
    elif gap > 0:
        severity = "info"
    else:
        severity = "info"
        gap = abs(gap)  # overperforming

    if sc.measure_status == "red":
        severity = "critical"
    elif sc.measure_status == "yellow" and severity != "critical":
        severity = "warning"

    body = (
        f"{m.measure_name} at {sc.current_rate:.1f}% — "
        f"{abs(sc.target_rate - sc.current_rate):.1f} pts {'below' if sc.current_rate < sc.target_rate else 'above'} target. "
        f"{sc.open_gap_count:,} gaps open."
    )
    alert_rows.append(Row(
        alert_id=f"ALT-{len(alert_rows):06d}",
        severity=severity,
        alert_title=f"{m.measure_code} {'Below' if sc.current_rate < sc.target_rate else 'Above'} 4-Star Threshold",
        alert_body=body,
        alert_meta=f"{sc.open_gap_count:,} open gaps" if sc.open_gap_count else None,
        measure_code=m.measure_code,
        cta_label="Launch Campaign" if severity == "critical" else ("View HEDIS" if m.measure_category == "HEDIS" else "View CAHPS"),
        cta_page="simulator" if severity == "critical" else ("hedis" if m.measure_category == "HEDIS" else "cahps"),
        priority_score=min(99, round(abs(gap) * 10 + (30 if severity == "critical" else 0))),
        is_active=True,
        measurement_year=YEAR,
    ))

# Add time-based alert
alert_rows.append(Row(
    alert_id="ALT-TIME-001", severity="info",
    alert_title="Q2 Snapshot Window Opens in 83 Days",
    alert_body="Current performance locks in 83 days. Focus outreach on red measures now.",
    alert_meta="83 days remaining", measure_code=None,
    cta_label="Run Simulator", cta_page="simulator",
    priority_score=70, is_active=True, measurement_year=YEAR,
))

_alert_schema = StructType([
    StructField("alert_id",         StringType(),  False),
    StructField("severity",         StringType(),  True),
    StructField("alert_title",      StringType(),  True),
    StructField("alert_body",       StringType(),  True),
    StructField("alert_meta",       StringType(),  True),
    StructField("measure_code",     StringType(),  True),
    StructField("cta_label",        StringType(),  True),
    StructField("cta_page",         StringType(),  True),
    StructField("priority_score",   IntegerType(), True),
    StructField("is_active",        BooleanType(), True),
    StructField("measurement_year", IntegerType(), True),
])
spark.createDataFrame(alert_rows, _alert_schema).write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.stars_gold.gold_alert_priority")
print(f"gold_alert_priority: {len(alert_rows)} rows")

# COMMAND ----------
# --- gold_intervention_hub ---
INTERVENTIONS = [
    ("COL Reminder Letter Campaign",   "COL",  "Clinical Quality",  3.2, "Active",    "2025-07-31", 5672),
    ("CBP PCP Alert Program",          "CBP",  "Network",           2.8, "Active",    "2025-08-15", 4890),
    ("KED Lab Order Nudge",            "KED",  "Clinical Quality",  2.4, "Planned",   "2025-09-01", 4123),
    ("AMM Care Management Referral",   "AMM",  "Care Management",   4.1, "Active",    "2025-07-15", 3892),
    ("OMW Fracture Risk Outreach",     "OMW",  "Clinical Quality",  2.1, "Planned",   "2025-09-30", 3445),
    ("SPC Statin Adherence Coaching",  "SPC",  "Pharmacy",          1.8, "Planned",   "2025-08-01", 2987),
    ("BCS Mobile Mammo Unit",          "BCS",  "Network",           3.5, "Planned",   "2025-08-30", 3210),
    ("HBD Diabetic Care Coordination", "HBD",  "Clinical Quality",  2.2, "Active",    "2025-07-01", 2340),
    ("EED Eye Exam Transport",         "EED",  "Care Management",   1.5, "Planned",   "2025-09-15", 1876),
    ("TRC Transition Coach Program",   "TRC",  "Call Center",       2.9, "Active",    "2025-07-20", 1654),
]

measure_code_map = {m.measure_code: m.measure_key for m in measures}
iv_rows = []
for name, mcode, dept, lift, status, due, cnt in INTERVENTIONS:
    iv_rows.append(Row(
        intervention_id=f"INT-{len(iv_rows):05d}",
        intervention_name=name,
        measure_key=measure_code_map.get(mcode, ""),
        measure_code=mcode,
        owner_department=dept,
        expected_lift_pct=lift,
        intervention_status=status,
        due_date=due,
        target_member_count=cnt,
        measurement_year=YEAR,
    ))

_iv_schema = StructType([
    StructField("intervention_id",      StringType(),  False),
    StructField("intervention_name",    StringType(),  True),
    StructField("measure_key",          StringType(),  True),
    StructField("measure_code",         StringType(),  True),
    StructField("owner_department",     StringType(),  True),
    StructField("expected_lift_pct",    DoubleType(),  True),
    StructField("intervention_status",  StringType(),  True),
    StructField("due_date",             StringType(),  True),
    StructField("target_member_count",  LongType(),    True),
    StructField("measurement_year",     IntegerType(), True),
])
spark.createDataFrame(iv_rows, _iv_schema).write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.stars_gold.gold_intervention_hub")
print(f"gold_intervention_hub: {len(iv_rows)} rows")
