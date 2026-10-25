# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Silver Layer: Clinical Events
# MAGIC Creates `silver_claim`, `silver_pharmacy_fill`, `silver_enrollment`,
# MAGIC `silver_outreach_event`, `silver_call_event` from bronze sources.

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")

# COMMAND ----------
from pyspark.sql import SparkSession, functions as F, Row
from pyspark.sql.functions import col
import random

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# --- silver_claim ---
bronze_claims = spark.table(f"{CATALOG}.stars_bronze.bronze_claims_raw")
member_map = spark.table(f"{CATALOG}.stars_silver.silver_member").select("member_id", "member_key")

silver_claim = (
    bronze_claims
    .join(member_map, "member_id", "left")
    .withColumn("claim_key", F.expr("uuid()"))
    .withColumn("service_month", F.trunc(col("service_date").cast("date"), "month"))
    .select(
        "claim_key", "claim_id", "member_key", "member_id",
        "service_date", "service_month", "icd10_primary", "icd10_secondary",
        "cpt_code", "claim_type", "plan_paid_amount", "member_paid_amount",
    )
)
silver_claim.write.format("delta").mode("overwrite").partitionBy("service_month").saveAsTable(f"{CATALOG}.stars_silver.silver_claim")
print(f"silver_claim: {silver_claim.count():,} rows")

# COMMAND ----------
# --- silver_pharmacy_fill ---
bronze_rx = spark.table(f"{CATALOG}.stars_bronze.bronze_pharmacy_raw")

silver_rx = (
    bronze_rx
    .join(member_map, "member_id", "left")
    .withColumn("rx_key", F.expr("uuid()"))
    .withColumn("fill_month", F.trunc(col("fill_date").cast("date"), "month"))
    .withColumn("pdc_compliant",
        F.when(col("days_supply") >= 80, True).otherwise(F.rand(42) > 0.25))
    .select(
        "rx_key", "rx_id", "member_key", "member_id",
        "fill_date", "fill_month", "ndc_code", "drug_name", "drug_class",
        "days_supply", "quantity", "plan_paid_amount", "member_paid_amount",
        "generic_flag", "pdc_compliant",
    )
)
silver_rx.write.format("delta").mode("overwrite").partitionBy("fill_month").saveAsTable(f"{CATALOG}.stars_silver.silver_pharmacy_fill")
print(f"silver_pharmacy_fill: {silver_rx.count():,} rows")

# COMMAND ----------
# --- silver_enrollment ---
bronze_enroll = spark.table(f"{CATALOG}.stars_bronze.bronze_enrollment_raw")
silver_enroll = (
    bronze_enroll
    .join(member_map, "member_id", "left")
    .withColumn("enrollment_key", F.expr("uuid()"))
    .select(
        "enrollment_key", "member_key", "member_id", "contract_id",
        "product_type", "dual_eligible_flag", "lis_flag",
        "effective_date", "termination_date",
    )
)
silver_enroll.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_silver.silver_enrollment")
print(f"silver_enrollment: {silver_enroll.count():,} rows")

# COMMAND ----------
# --- silver_outreach_event ---
RESPONSE_STATUSES = ["Reached - Scheduled", "No Answer", "Voicemail Left", "Opted Out", "Gap Closed"]
CHANNELS = ["Call", "SMS", "Email", "Portal"]
MEASURES = ["COL", "CBP", "KED", "AMM", "OMW", "HBD", "SPC", "BCS", "EED", "MRP", "TRC"]

outreach_rows = []
members_sample = spark.table(f"{CATALOG}.stars_silver.silver_member").select("member_key", "member_id").limit(60_000).collect()

for row in members_sample:
    r = random.Random(hash(row.member_key) & 0xFFFFFFFF)
    n_events = r.choices([0, 1, 2, 3, 4, 5], weights=[30, 25, 20, 12, 8, 5])[0]
    for _ in range(n_events):
        outreach_rows.append(Row(
            outreach_key=f"OUT-{len(outreach_rows):09d}",
            member_key=row.member_key,
            member_id=row.member_id,
            outreach_date=f"2025-{r.randint(1,10):02d}-{r.randint(1,28):02d}",
            channel=r.choice(CHANNELS),
            measure_code=r.choice(MEASURES),
            response_status=r.choices(RESPONSE_STATUSES, weights=[20, 35, 20, 5, 20])[0],
            agent_id=f"AGT-{r.randint(1,120):04d}",
            campaign_name=r.choice(["COL Wave 1", "CBP SMS Blitz", "KED Outreach", None, None]),
        ))

CHUNK = 100_000
for i in range(0, len(outreach_rows), CHUNK):
    chunk_df = spark.createDataFrame(outreach_rows[i:i + CHUNK])
    mode = "overwrite" if i == 0 else "append"
    chunk_df.write.format("delta").mode(mode).saveAsTable(f"{CATALOG}.stars_silver.silver_outreach_event")

total = spark.table(f"{CATALOG}.stars_silver.silver_outreach_event").count()
print(f"silver_outreach_event: {total:,} rows")

# COMMAND ----------
# --- silver_call_event ---
bronze_calls = spark.table(f"{CATALOG}.stars_bronze.bronze_call_center_raw")
silver_calls = (
    bronze_calls
    .join(member_map, "member_id", "left")
    .withColumn("call_event_key", F.expr("uuid()"))
    .select(
        "call_event_key", "call_id", "member_key", "member_id",
        "call_date", "call_type", "call_duration_min", "disposition",
        "sentiment_score", "agent_id", "queue_name", "measure_code",
    )
)
silver_calls.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_silver.silver_call_event")
print(f"silver_call_event: {silver_calls.count():,} rows")
