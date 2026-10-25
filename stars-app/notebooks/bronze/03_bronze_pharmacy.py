# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Bronze Layer: Pharmacy Data
# MAGIC Generates `bronze_pharmacy_raw` — 1.1M synthetic Rx fill records.

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
DRUGS = [
    # Statins (SPC measure)
    {"ndc": "00093-7465-01", "name": "Atorvastatin 40mg", "class": "statin", "days_supply_opts": [30, 90]},
    {"ndc": "00093-7543-01", "name": "Rosuvastatin 20mg", "class": "statin", "days_supply_opts": [30, 90]},
    {"ndc": "00781-5077-01", "name": "Simvastatin 40mg", "class": "statin", "days_supply_opts": [30, 90]},
    # Antidepressants (AMM measure)
    {"ndc": "00093-1085-01", "name": "Sertraline 50mg", "class": "antidepressant", "days_supply_opts": [30, 90]},
    {"ndc": "00074-2547-13", "name": "Fluoxetine 20mg", "class": "antidepressant", "days_supply_opts": [30, 90]},
    # Antihypertensives (CBP measure)
    {"ndc": "00185-0132-01", "name": "Lisinopril 10mg", "class": "antihypertensive", "days_supply_opts": [30, 90]},
    {"ndc": "00378-1122-01", "name": "Amlodipine 5mg", "class": "antihypertensive", "days_supply_opts": [30, 90]},
    {"ndc": "00093-0073-01", "name": "Losartan 50mg", "class": "antihypertensive", "days_supply_opts": [30, 90]},
    # Diabetes (HBD/KED measures)
    {"ndc": "00093-1048-01", "name": "Metformin 500mg", "class": "diabetes", "days_supply_opts": [30, 90]},
    {"ndc": "00002-8215-01", "name": "Insulin Glargine 100u/mL", "class": "diabetes", "days_supply_opts": [30]},
    {"ndc": "00310-0660-10", "name": "Empagliflozin 10mg", "class": "diabetes", "days_supply_opts": [30, 90]},
    # Osteoporosis (OMW measure)
    {"ndc": "00006-0031-31", "name": "Alendronate 70mg", "class": "osteoporosis", "days_supply_opts": [30, 90]},
]

N_MEMBERS = 100_000
AVG_RX_PER_MEMBER = 11  # ~1.1M total

rows = []
for m in range(N_MEMBERS):
    r = random.Random(SEED + 1000 + m)
    member_id = f"MBR-{m:07d}"
    n_fills = max(1, round(r.gauss(AVG_RX_PER_MEMBER, 4)))
    # Members on more complex drugs tend to have more fills
    drug_pool = r.choices(DRUGS, k=r.randint(1, 4))
    for _ in range(n_fills):
        drug = r.choice(drug_pool)
        fill_date = date(2025, r.randint(1, 10), r.randint(1, 28))
        days_supply = r.choice(drug["days_supply_opts"])
        rows.append(Row(
            rx_id=f"RX-{len(rows):09d}",
            member_id=member_id,
            fill_date=str(fill_date),
            ndc_code=drug["ndc"],
            drug_name=drug["name"],
            drug_class=drug["class"],
            days_supply=days_supply,
            quantity=days_supply,
            pharmacy_npi=f"1{r.randint(100_000_000, 999_999_999)}",
            plan_paid_amount=round(r.uniform(2.50, 180.0), 2),
            member_paid_amount=round(r.uniform(0.0, 15.0), 2),
            generic_flag=r.random() > 0.3,
            raw_source="synthetic_pharmacy_v1",
            ingestion_ts="2025-01-01",
        ))

# COMMAND ----------
CHUNK = 200_000
for i in range(0, len(rows), CHUNK):
    chunk_df = spark.createDataFrame(rows[i:i + CHUNK])
    mode = "overwrite" if i == 0 else "append"
    chunk_df.write.format("delta").mode(mode).saveAsTable(f"{CATALOG}.stars_bronze.bronze_pharmacy_raw")
    print(f"Chunk {i//CHUNK + 1} written")

total = spark.table(f"{CATALOG}.stars_bronze.bronze_pharmacy_raw").count()
print(f"Total: {total:,} rows in bronze_pharmacy_raw")
