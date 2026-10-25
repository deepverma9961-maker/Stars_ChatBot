# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Bronze Layer: Claims Data
# MAGIC Generates `bronze_claims_raw` — 1.8M synthetic medical claims.

# COMMAND ----------
dbutils.widgets.text("seed", "42")
dbutils.widgets.text("catalog", "aiagenticdemo")

SEED = int(dbutils.widgets.get("seed"))
CATALOG = dbutils.widgets.get("catalog")

# COMMAND ----------
import random
from pyspark.sql import SparkSession, Row
from datetime import date, timedelta

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# Utilization tiers with member counts and avg annual claims
TIERS = [
    ("Low",       35_000, 8),
    ("Moderate",  40_000, 18),
    ("Chronic",   20_000, 28),
    ("HighRisk",   5_000, 40),
]

ICD10_POOL = [
    "E11.9", "E11.65", "E11.40",   # Diabetes
    "I10", "I11.9",                 # Hypertension
    "Z12.31",                       # Mammogram screening
    "Z12.11",                       # Colorectal screening
    "F32.9", "F33.0",               # Depression
    "M81.0", "M80.00",              # Osteoporosis
    "N18.3", "N18.4",               # CKD
    "I25.10", "I25.110",            # CAD
    "J44.1", "J45.31",              # COPD/Asthma
    "Z00.00",                       # Well visit
]
CPT_POOL = [
    "G0438",  # Annual Wellness Visit
    "83036",  # HbA1c
    "77067",  # Mammography
    "45378",  # Colonoscopy
    "93000",  # EKG
    "99213", "99214",  # Office visits
    "36415",  # Blood draw
    "82043",  # Urine microalbumin (KED)
    "93306",  # Echo
    "71046",  # Chest X-ray
]
CLAIM_TYPES = ["Professional", "Facility", "Ancillary"]

rows = []
member_offset = 0
for tier_name, n_members, avg_claims in TIERS:
    for m in range(n_members):
        member_id = f"MBR-{(member_offset + m):07d}"
        r = random.Random(SEED + member_offset + m)
        n_claims = max(1, round(r.gauss(avg_claims, avg_claims * 0.3)))
        for c in range(n_claims):
            svc_date = date(2025, r.randint(1, 10), r.randint(1, 28))
            paid = round(r.uniform(15, 850), 2)
            rows.append(Row(
                claim_id=f"CLM-{len(rows):09d}",
                member_id=member_id,
                utilization_tier=tier_name,
                service_date=str(svc_date),
                icd10_primary=r.choice(ICD10_POOL),
                icd10_secondary=r.choice(ICD10_POOL) if r.random() > 0.4 else None,
                cpt_code=r.choice(CPT_POOL),
                revenue_code=str(r.randint(100, 999)),
                rendering_npi=f"1{r.randint(100_000_000, 999_999_999)}",
                facility_npi=f"1{r.randint(100_000_000, 999_999_999)}" if r.random() > 0.5 else None,
                claim_type=r.choice(CLAIM_TYPES),
                plan_paid_amount=paid,
                member_paid_amount=round(r.uniform(0, 45), 2),
                raw_source="synthetic_claims_v1",
                ingestion_ts="2025-01-01",
            ))
    member_offset += n_members

# COMMAND ----------
# Write in chunks to avoid OOM
CHUNK = 200_000
for i in range(0, len(rows), CHUNK):
    chunk_df = spark.createDataFrame(rows[i:i + CHUNK])
    mode = "overwrite" if i == 0 else "append"
    chunk_df.write.format("delta").mode(mode).saveAsTable(f"{CATALOG}.stars_bronze.bronze_claims_raw")
    print(f"Written chunk {i//CHUNK + 1}: {i+len(rows[i:i+CHUNK]):,} rows total")

total = spark.table(f"{CATALOG}.stars_bronze.bronze_claims_raw").count()
print(f"Total rows in bronze_claims_raw: {total:,}")
