# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Gold Layer: CAHPS Overview & Team View
# MAGIC Creates `gold_cahps_overview` (28 rows) and `gold_team_view` (6 departments × ~7 rows).

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, ArrayType
import random

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# --- gold_cahps_overview ---
CAHPS_DATA = {
    "H3312": (4.2, 4.2, 83, 2_250_000),
    "H5521": (3.6, 3.6, 83, 981_000),
    "H2213": (4.4, 4.5, 83, 6_740_000),
    "H6614": (4.1, 4.1, 83, 3_365_000),
    "H7723": (3.8, 3.9, 83, 4_455_000),
    "H8812": (3.9, 4.0, 83, 2_730_000),
    "H9914": (3.7, 3.7, 83, 0),
    "H1045": (3.3, 3.4, 83, 0),
    "H2156": (3.8, 3.9, 83, 3_090_000),
    "H3267": (4.3, 4.4, 83, 2_445_000),
    "H4378": (3.4, 3.5, 83, 0),
    "H5489": (4.3, 4.4, 83, 1_920_000),
    "H6590": (4.0, 4.0, 83, 2_205_000),
    "H7601": (4.1, 4.1, 83, 2_950_000),
}

plans = spark.table(f"{CATALOG}.stars_silver.silver_plan").filter("contract_id NOT LIKE '%B'").collect()
plan_map = {r.contract_id: r.plan_key for r in plans}

cahps_rows = []
for contract_id, plan_key in plan_map.items():
    curr, proj, days, qbp = CAHPS_DATA.get(contract_id, (3.8, 3.9, 83, 0))
    gap = max(0.0, 4.0 - proj)
    cahps_rows.append(Row(
        cahps_key=f"CAHPS-{contract_id}-{YEAR}",
        plan_key=plan_key,
        contract_id=contract_id,
        measurement_year=YEAR,
        current_cahps_rating=curr,
        projected_cahps_rating=proj,
        gap_to_4_star=gap,
        days_remaining=days,
        qbp_at_stake_amount=float(qbp),
        last_updated="2025-06-10",
    ))

_cahps_schema = StructType([
    StructField("cahps_key",               StringType(),  False),
    StructField("plan_key",                StringType(),  True),
    StructField("contract_id",             StringType(),  True),
    StructField("measurement_year",        IntegerType(), True),
    StructField("current_cahps_rating",    DoubleType(),  True),
    StructField("projected_cahps_rating",  DoubleType(),  True),
    StructField("gap_to_4_star",           DoubleType(),  True),
    StructField("days_remaining",          IntegerType(), True),
    StructField("qbp_at_stake_amount",     DoubleType(),  True),
    StructField("last_updated",            StringType(),  True),
])
spark.createDataFrame(cahps_rows, _cahps_schema).write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.stars_gold.gold_cahps_overview")
print(f"gold_cahps_overview: {len(cahps_rows)} rows")

# COMMAND ----------
# --- gold_team_view ---
DEPARTMENTS = [
    ("Clinical Quality",   "Dr. Rachel Kim",    ["COL","CBP","KED","OMW","AMM","HBD"], 2, 2, 4, "In Progress",  "COL reminder letter drop — Jun 12"),
    ("Member Experience",  "Sarah Thompson",    ["GNC","GCQ","DC","CS","HPR","CC"],    3, 3, 0, "In Progress",  "CAHPS pulse survey — Jun 20"),
    ("Call Center",        "Marcus Johnson",    ["MRP","TRC","AMM"],                   2, 0, 1, "In Progress",  "AMM follow-up queue — Jun 10"),
    ("Pharmacy",           "Lisa Chen",         ["SPC","KED"],                         1, 1, 0, "Not Started",  "SPC statin gap review — Jun 15"),
    ("Utilization Mgmt",   "David Park",        ["PCR","COA_MR","COA_PA"],             2, 1, 0, "In Progress",  "PCR readmission audit — Jun 18"),
    ("Network",            "Angela Torres",     ["CBP","BCS","EED"],                   2, 1, 0, "In Progress",  "Mammography provider outreach — Jun 22"),
]

team_rows = []
for dept, leader, measures, on_track, at_risk, critical, action_status, next_action in DEPARTMENTS:
    for year in [2025]:
        team_rows.append(Row(
            team_view_key=f"TV-{dept[:4]}-{year}",
            department=dept,
            team_leader=leader,
            measures_owned=measures,
            measurement_year=year,
            on_track_count=on_track,
            at_risk_count=at_risk,
            critical_count=critical,
            action_status=action_status,
            next_action=next_action,
        ))

_team_schema = StructType([
    StructField("team_view_key",    StringType(),               False),
    StructField("department",       StringType(),               True),
    StructField("team_leader",      StringType(),               True),
    StructField("measures_owned",   ArrayType(StringType()),     True),
    StructField("measurement_year", IntegerType(),               True),
    StructField("on_track_count",   IntegerType(),               True),
    StructField("at_risk_count",    IntegerType(),               True),
    StructField("critical_count",   IntegerType(),               True),
    StructField("action_status",    StringType(),               True),
    StructField("next_action",      StringType(),               True),
])
spark.createDataFrame(team_rows, _team_schema).write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.stars_gold.gold_team_view")
print(f"gold_team_view: {len(team_rows)} rows")
display(spark.table(f"{CATALOG}.stars_gold.gold_team_view").select("department", "on_track_count", "at_risk_count", "critical_count"))
