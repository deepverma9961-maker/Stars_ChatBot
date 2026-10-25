# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Bronze Layer: CAHPS Survey Data
# MAGIC Generates `bronze_cahps_survey_raw` — 10k synthetic CAHPS survey responses.

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
# CAHPS composites and question mapping
COMPOSITES = [
    ("GNC", "Getting Needed Care",    ["GNC_Q1", "GNC_Q2"], "likert"),
    ("GCQ", "Getting Care Quickly",   ["GCQ_Q1", "GCQ_Q2"], "likert"),
    ("DC",  "Doctor Communication",   ["DC_Q1",  "DC_Q2", "DC_Q3"], "likert"),
    ("CS",  "Customer Service",       ["CS_Q1",  "CS_Q2"], "likert"),
    ("HPR", "Health Plan Rating",     ["HPR_Q1"], "rating_10"),
    ("CC",  "Care Coordination",      ["CC_Q1",  "CC_Q2"], "likert"),
]

# CMS CAHPS sampling: ~12% of eligible members surveyed
N_RESPONDENTS = 10_000
N_ELIGIBLE = 83_000  # approx

rows = []
for i in range(N_RESPONDENTS):
    r = random.Random(SEED + 2000 + i)
    # Pick a random member from the member pool
    member_id = f"MBR-{r.randint(0, 99999):07d}"
    survey_date = date(2025, r.randint(2, 5), r.randint(1, 28))
    # Each respondent answers all composites
    for comp_code, comp_name, questions, scale in COMPOSITES:
        for q in questions:
            if scale == "likert":
                # 1=Never, 2=Sometimes, 3=Usually, 4=Always
                # Skew toward 3-4 for realistic ~75-82% top-box scores
                val = r.choices([1, 2, 3, 4], weights=[5, 15, 35, 45])[0]
            else:
                # 0-10 health plan rating — skew toward 7-10
                val = r.choices(range(11), weights=[1, 1, 2, 3, 4, 6, 10, 15, 20, 22, 16])[0]
            rows.append(Row(
                response_id=f"CAHPS-{len(rows):08d}",
                member_id=member_id,
                survey_date=str(survey_date),
                composite_code=comp_code,
                composite_name=comp_name,
                question_code=q,
                response_value=val,
                scale_type=scale,
                raw_source="synthetic_cahps_v1",
                ingestion_ts="2025-01-01",
            ))

# COMMAND ----------
df = spark.createDataFrame(rows)
df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_bronze.bronze_cahps_survey_raw")
print(f"Written {df.count():,} rows to {CATALOG}.stars_bronze.bronze_cahps_survey_raw")
display(df.groupBy("composite_code").agg({"response_value": "avg"}).orderBy("composite_code"))
