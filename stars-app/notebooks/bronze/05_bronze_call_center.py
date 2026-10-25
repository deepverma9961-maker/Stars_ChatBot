# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Bronze Layer: Call Center Data
# MAGIC Generates `bronze_call_center_raw` — 375k synthetic call center records.

# COMMAND ----------
dbutils.widgets.text("seed", "42")
dbutils.widgets.text("catalog", "aiagenticdemo")

SEED = int(dbutils.widgets.get("seed"))
CATALOG = dbutils.widgets.get("catalog")

# COMMAND ----------
import random
from pyspark.sql import SparkSession, Row
from datetime import date

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
CALL_TYPES = ["inbound", "outbound"]
DISPOSITIONS = [
    "Reached - Scheduled", "Reached - Declined", "Reached - Already Done",
    "No Answer", "Voicemail Left", "Wrong Number", "Opted Out",
]
QUEUES = ["HEDIS_Outreach", "CAHPS_Survey", "Member_Services", "Pharmacy_Support", "Appeals", "General"]
N_AGENTS = 120

rows = []
N_CALLS = 375_000
for i in range(N_CALLS):
    r = random.Random(SEED + 3000 + i)
    member_id = f"MBR-{r.randint(0, 99999):07d}"
    call_date = date(2025, r.randint(1, 10), r.randint(1, 28))
    call_type = r.choices(CALL_TYPES, weights=[40, 60])[0]
    disposition = r.choices(DISPOSITIONS, weights=[25, 10, 8, 30, 15, 3, 9])[0]
    # Sentiment: reached calls more positive; no-answers neutral
    if "Reached" in disposition:
        sentiment = round(r.uniform(0.1, 1.0), 3)
    elif "Opted Out" in disposition:
        sentiment = round(r.uniform(-1.0, -0.2), 3)
    else:
        sentiment = round(r.uniform(-0.3, 0.3), 3)
    rows.append(Row(
        call_id=f"CALL-{i:08d}",
        member_id=member_id,
        call_date=str(call_date),
        call_type=call_type,
        call_duration_min=round(r.uniform(1.5, 18.0), 1) if "No Answer" not in disposition else 0.0,
        disposition=disposition,
        sentiment_score=sentiment,
        agent_id=f"AGT-{r.randint(1, N_AGENTS):04d}",
        queue_name=r.choice(QUEUES),
        measure_code=r.choice(["COL", "CBP", "KED", "HBD", "AMM", "SPC", None, None]),
        raw_source="synthetic_call_center_v1",
        ingestion_ts="2025-01-01",
    ))

# COMMAND ----------
CHUNK = 100_000
for i in range(0, len(rows), CHUNK):
    chunk_df = spark.createDataFrame(rows[i:i + CHUNK])
    mode = "overwrite" if i == 0 else "append"
    chunk_df.write.format("delta").mode(mode).saveAsTable(f"{CATALOG}.stars_bronze.bronze_call_center_raw")

total = spark.table(f"{CATALOG}.stars_bronze.bronze_call_center_raw").count()
print(f"Total: {total:,} rows in bronze_call_center_raw")
