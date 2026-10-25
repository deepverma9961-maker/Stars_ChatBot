# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer: Enrollment Data
# MAGIC Generates `bronze_enrollment_raw` — 100k synthetic HIPAA-safe member enrollment records.

# COMMAND ----------

dbutils.widgets.text("seed", "42")
dbutils.widgets.text("catalog", "aiagenticdemo")
dbutils.widgets.text("n_members", "100000")

SEED = int(dbutils.widgets.get("seed"))
CATALOG = dbutils.widgets.get("catalog")
N = int(dbutils.widgets.get("n_members"))

# COMMAND ----------

# DBTITLE 1,Install faker
# MAGIC %pip install faker -q

# COMMAND ----------

import random
from faker import Faker
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType, BooleanType
from datetime import date, timedelta

fake = Faker("en_US")
Faker.seed(SEED)
rng = random.Random(SEED)
spark = SparkSession.builder.getOrCreate()

# COMMAND ----------

CONTRACTS = [
    ("H3312", "FL", 112_500), ("H5521", "TX", 98_200), ("H2213", "CA", 134_800),
    ("H6614", "PA", 67_300), ("H7723", "NY", 89_100), ("H8812", "OH", 54_600),
    ("H9914", "AZ", 72_400), ("H1045", "GA", 43_200), ("H2156", "IL", 61_800),
    ("H3267", "NC", 48_900), ("H4378", "MI", 55_700), ("H5489", "WA", 38_400),
    ("H6590", "VA", 44_100), ("H7601", "CO", 59_000),
]
total_enroll = sum(c[2] for c in CONTRACTS)
PRODUCT_TYPES = ["HMO"] * 55 + ["PPO"] * 25 + ["D-SNP"] * 15 + ["HMO-POS"] * 5

def make_mbi(r):
    c = "ACDEFGHJKMNPQRTUVWXY"
    return f"{r.choice(c)}{r.randint(1,9)}{r.randint(1,9)}{r.choice(c)}-{r.choice(c)}{r.choice(c)}{r.randint(1,9)}-{r.choice(c)}{r.choice(c)}{r.randint(1,9)}{r.randint(1,9)}"

rows = []
for i in range(N):
    r = random.Random(SEED + i)
    fake_local = Faker("en_US")
    fake_local.seed_instance(SEED + i)
    # Assign contract proportionally
    roll = r.random() * total_enroll
    cumulative = 0
    contract_id, state = CONTRACTS[0][0], CONTRACTS[0][1]
    for cid, st, cnt in CONTRACTS:
        cumulative += cnt
        if roll < cumulative:
            contract_id, state = cid, st
            break
    dob = date(r.randint(1934, 1960), r.randint(1, 12), r.randint(1, 28))
    eff_date = date(2025, r.randint(1, 3), r.randint(1, 28))
    rows.append(Row(
        member_id=f"MBR-{i:07d}",
        synthetic_mbi=make_mbi(r),
        first_name=fake_local.first_name(),
        last_name=fake_local.last_name(),
        date_of_birth=str(dob),
        gender=r.choice(["M", "F"]),
        state=state,
        contract_id=contract_id,
        product_type=r.choice(PRODUCT_TYPES),
        dual_eligible_flag=r.random() < 0.20,
        lis_flag=r.random() < 0.30,
        effective_date=str(eff_date),
        termination_date=None,
        raw_source="synthetic_enrollment_v1",
        ingestion_ts=str(date(2025, 1, 1)),
    ))

# COMMAND ----------

_schema = StructType([
    StructField("member_id",          StringType(),  False),
    StructField("synthetic_mbi",      StringType(),  True),
    StructField("first_name",         StringType(),  True),
    StructField("last_name",          StringType(),  True),
    StructField("date_of_birth",      StringType(),  True),
    StructField("gender",             StringType(),  True),
    StructField("state",              StringType(),  True),
    StructField("contract_id",        StringType(),  True),
    StructField("product_type",       StringType(),  True),
    StructField("dual_eligible_flag", BooleanType(), True),
    StructField("lis_flag",           BooleanType(), True),
    StructField("effective_date",     StringType(),  True),
    StructField("termination_date",   StringType(),  True),
    StructField("raw_source",         StringType(),  True),
    StructField("ingestion_ts",       StringType(),  True),
])
df = spark.createDataFrame(rows, _schema)


df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_bronze.bronze_enrollment_raw")
print(f"Written {df.count():,} rows to {CATALOG}.stars_bronze.bronze_enrollment_raw")
display(df.limit(5))
