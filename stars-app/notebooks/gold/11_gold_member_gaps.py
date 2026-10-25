# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Gold Layer: Member Gaps
# MAGIC Creates `gold_member_gap` — ~260k rows. Member × measure gap registry
# MAGIC with propensity scores, recommended channel/incentive, outreach history.

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
import random

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
HEDIS_MEASURES = ["HBD","CBP","PCR","BCS","COL","COA_MR","COA_PA","OMW","EED","KED","MRP","SPC","TRC","AMM"]
GAP_STATUSES = ["Open", "Partial", "Borderline"]
GAP_STATUS_WEIGHTS = [55, 30, 15]

# Target distribution: 0 gaps 25%, 1 gap 30%, 2 gaps 25%, 3-4 gaps 15%, 5+ gaps 5%
GAP_COUNTS_WEIGHTS = [25, 30, 25, 10, 5, 5]
GAP_COUNTS = [0, 1, 2, 3, 4, 5]

members = spark.table(f"{CATALOG}.stars_silver.silver_member").select(
    "member_key", "member_id", "contract_id", "utilization_segment"
).collect()

measures = {r.measure_code: r.measure_key for r in spark.table(f"{CATALOG}.stars_silver.silver_measure").collect()}
plans = {r.contract_id: r.plan_key for r in spark.table(f"{CATALOG}.stars_silver.silver_plan").collect()}

# Get last outreach dates from silver_outreach_event
outreach_dates = {
    r.member_key: r.last_date
    for r in spark.table(f"{CATALOG}.stars_silver.silver_outreach_event")
    .groupBy("member_key")
    .agg({"outreach_date": "max"})
    .withColumnRenamed("max(outreach_date)", "last_date")
    .collect()
}

rows = []
for member in members:
    r = random.Random(hash(member.member_key) & 0xFFFFFFFF)
    # Assign number of gaps based on distribution
    n_gaps = r.choices(GAP_COUNTS, weights=GAP_COUNTS_WEIGHTS)[0]
    if n_gaps == 0:
        continue

    # Higher risk segment = more complex gaps
    if member.utilization_segment in ("Chronic", "Very High Risk"):
        n_gaps = min(5, n_gaps + r.randint(0, 2))

    selected_measures = r.sample(HEDIS_MEASURES, min(n_gaps, len(HEDIS_MEASURES)))
    plan_key = plans.get(member.contract_id)
    if not plan_key:
        # Try without suffix
        base_cid = member.contract_id.replace("B", "")
        plan_key = plans.get(base_cid)
    if not plan_key:
        continue

    last_out = outreach_dates.get(member.member_key)
    for measure_code in selected_measures:
        measure_key = measures.get(measure_code)
        if not measure_key:
            continue

        # propensity_score is a placeholder here; notebook
        # `15_ml_closure_propensity.py` overwrites it with the trained
        # GradientBoostingClassifier's best-channel probability.
        propensity = 50.0
        gap_status = r.choices(GAP_STATUSES, weights=GAP_STATUS_WEIGHTS)[0]

        # Channel and incentive recommendations
        if propensity > 75:
            channel = "Call"
        elif propensity > 40:
            channel = "SMS"
        else:
            channel = "Email"

        if propensity > 80:
            incentive = "None"
        elif propensity > 60:
            incentive = "$25 card"
        else:
            incentive = "$50 card"

        days_open = r.randint(15, 280)
        gap_open_date = f"2025-{max(1, min(10, (10 - days_open // 30))):02d}-{r.randint(1,28):02d}"

        rows.append(Row(
            member_gap_key=f"GAP-{len(rows):09d}",
            member_key=member.member_key,
            plan_key=plan_key,
            measure_key=measure_key,
            measure_code=measure_code,
            measurement_year=YEAR,
            gap_status=gap_status,
            propensity_score=propensity,
            recommended_channel=channel,
            recommended_incentive=incentive,
            gap_open_date=gap_open_date,
            last_outreach_date=last_out,
            campaign_name=r.choice(["COL Wave 1", "CBP SMS Blitz", "KED Outreach", None, None, None]),
            is_suppressed=r.random() < 0.10,
            days_open=days_open,
        ))

# COMMAND ----------
_schema = StructType([
    StructField("member_gap_key",        StringType(),  False),
    StructField("member_key",            StringType(),  True),
    StructField("plan_key",              StringType(),  True),
    StructField("measure_key",           StringType(),  True),
    StructField("measure_code",          StringType(),  True),
    StructField("measurement_year",      IntegerType(), True),
    StructField("gap_status",            StringType(),  True),
    StructField("propensity_score",      DoubleType(),  True),
    StructField("recommended_channel",   StringType(),  True),
    StructField("recommended_incentive", StringType(),  True),
    StructField("gap_open_date",         StringType(),  True),
    StructField("last_outreach_date",    StringType(),  True),
    StructField("campaign_name",         StringType(),  True),
    StructField("is_suppressed",         BooleanType(), True),
    StructField("days_open",             IntegerType(), True),
])

print(f"Generating {len(rows):,} gap rows...")
CHUNK = 100_000
for i in range(0, len(rows), CHUNK):
    chunk_df = spark.createDataFrame(rows[i:i + CHUNK], _schema)
    mode = "overwrite" if i == 0 else "append"
    opts = {"overwriteSchema": "true"} if mode == "overwrite" else {}
    chunk_df.write.format("delta").mode(mode).options(**opts).saveAsTable(f"{CATALOG}.stars_gold.gold_member_gap")

total = spark.table(f"{CATALOG}.stars_gold.gold_member_gap").count()
print(f"gold_member_gap: {total:,} rows")
display(spark.table(f"{CATALOG}.stars_gold.gold_member_gap").groupBy("gap_status").count().orderBy("gap_status"))
