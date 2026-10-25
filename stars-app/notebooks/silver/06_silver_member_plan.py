# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer: Member, Plan, Provider
# MAGIC Transforms bronze enrollment into `silver_member`, `silver_plan`, `silver_provider`.
# MAGIC All PII (MBI, phone, email) is SHA-256 hashed. `display_name` is first name + last initial only.

# COMMAND ----------

dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")

# COMMAND ----------

# MAGIC %pip install faker

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import udf, col, sha2, concat_ws, lit, rand, when, expr
from pyspark.sql.types import StringType, IntegerType
from faker import Faker
import random

spark = SparkSession.builder.getOrCreate()
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.stars_silver")

# COMMAND ----------

# --- silver_member ---
bronze = spark.table(f"{CATALOG}.stars_bronze.bronze_enrollment_raw")

silver_member = (
    bronze
    .withColumn("member_key", F.expr("uuid()"))
    .withColumn("display_name",
        F.concat(col("first_name"), lit(" "), F.substring(col("last_name"), 1, 1), lit(".")))
    .withColumn("member_mbi_hash", sha2(col("synthetic_mbi"), 256))
    .withColumn("phone_hash", sha2(F.concat(col("member_id"), lit("_phone")), 256))
    .withColumn("email_hash", sha2(F.concat(col("member_id"), lit("_email")), 256))
    .withColumn("age", (2025 - F.year(col("date_of_birth").cast("date"))).cast(IntegerType()))
    .withColumn("utilization_segment",
        when(rand(42) < 0.35, "Low")
        .when(rand(43) < 0.75, "Moderate")
        .when(rand(44) < 0.95, "Chronic")
        .otherwise("Very High Risk"))
    .withColumn("pcp_provider_key", F.expr("uuid()"))
    .select(
        "member_key", "member_id", "display_name", "member_mbi_hash",
        "phone_hash", "email_hash", "age", "gender", "state",
        "contract_id", "product_type", "dual_eligible_flag", "lis_flag",
        "utilization_segment", "pcp_provider_key", "effective_date",
    )
)
silver_member.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_silver.silver_member")
print(f"silver_member: {silver_member.count():,} rows")

# COMMAND ----------

# --- silver_plan ---
CONTRACTS = [
    ("H3312", "Health Plan Advantage Premier",     "FL", 112_500, "HMO"),
    ("H3312B","Health Plan Advantage Premier SNP", "FL",  12_500, "D-SNP"),
    ("H5521", "Lone Star Medicare Complete",       "TX",  98_200, "HMO"),
    ("H5521B","Lone Star Medicare SNP",            "TX",   9_800, "D-SNP"),
    ("H2213", "Pacific Care Advantage Gold",       "CA", 134_800, "PPO"),
    ("H2213B","Pacific Care SNP Select",           "CA",  13_400, "D-SNP"),
    ("H6614", "Keystone Senior Plus",              "PA",  67_300, "HMO"),
    ("H6614B","Keystone Senior SNP",               "PA",   6_700, "D-SNP"),
    ("H7723", "Empire Blue Medicare",              "NY",  89_100, "PPO"),
    ("H7723B","Empire Blue Medicare SNP",          "NY",   8_900, "D-SNP"),
    ("H8812", "Buckeye Health Advantage",          "OH",  54_600, "HMO"),
    ("H8812B","Buckeye Health SNP",                "OH",   5_400, "D-SNP"),
    ("H9914", "Desert Sun Medicare Plus",          "AZ",  72_400, "HMO"),
    ("H9914B","Desert Sun SNP",                    "AZ",   7_200, "D-SNP"),
    ("H1045", "Peach State Senior Care",           "GA",  43_200, "HMO"),
    ("H1045B","Peach State SNP",                   "GA",   4_300, "D-SNP"),
    ("H2156", "Prairie Medicare Select",           "IL",  61_800, "HMO"),
    ("H2156B","Prairie Medicare SNP",              "IL",   6_100, "D-SNP"),
    ("H3267", "Carolina Blue Medicare",            "NC",  48_900, "PPO"),
    ("H3267B","Carolina Blue SNP",                 "NC",   4_900, "D-SNP"),
    ("H4378", "Great Lakes Senior Advantage",      "MI",  55_700, "HMO"),
    ("H4378B","Great Lakes SNP",                   "MI",   5_600, "D-SNP"),
    ("H5489", "Cascade Medicare Choice",           "WA",  38_400, "HMO-POS"),
    ("H5489B","Cascade Medicare SNP",              "WA",   3_800, "D-SNP"),
    ("H6590", "Blue Ridge Senior Select",          "VA",  44_100, "HMO"),
    ("H6590B","Blue Ridge SNP",                    "VA",   4_400, "D-SNP"),
    ("H7601", "Rocky Mountain Medicare Plus",      "CO",  59_000, "PPO"),
    ("H7601B","Rocky Mountain Medicare SNP",       "CO",   5_900, "D-SNP"),
]

plan_rows = [{"plan_key": f"PLN-{i:04d}", "contract_id": c[0], "plan_name": c[1], "state": c[2],
              "enrollment_count": c[3], "product_type": c[4]} for i, c in enumerate(CONTRACTS)]
spark.createDataFrame(plan_rows).write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_silver.silver_plan")
print(f"silver_plan: {len(plan_rows)} rows")

# COMMAND ----------

# --- silver_provider ---
import random
from pyspark.sql import Row

SPECIALTIES = ["Internal Medicine", "Family Medicine", "Cardiology", "Endocrinology",
               "Nephrology", "Oncology", "Orthopedics", "Ophthalmology", "Gastroenterology"]
NETWORK_TIERS = ["Tier 1 - Preferred", "Tier 2 - In-Network", "Tier 3 - Out-of-Network"]

provider_rows = []
for i in range(12_000):
    r = random.Random(42 + i + 5000)
    provider_rows.append(Row(
        provider_key=f"PRV-{i:06d}",
        npi=f"1{r.randint(100_000_000, 999_999_999)}",
        provider_name=f"Dr. {['Smith', 'Chen', 'Patel', 'Johnson', 'Williams', 'Davis', 'Kim', 'Torres'][r.randint(0,7)]}, {chr(65 + r.randint(0,25))}.",
        specialty=r.choice(SPECIALTIES),
        network_tier=r.choices(NETWORK_TIERS, weights=[60, 30, 10])[0],
        tin_hash=f"TIN-{r.randint(100_000_000, 999_999_999)}",
        state=r.choice(["FL","TX","CA","PA","NY","OH","AZ","GA","IL","NC","MI","WA","VA","CO"]),
    ))

spark.createDataFrame(provider_rows).write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_silver.silver_provider")
print(f"silver_provider: {len(provider_rows)} rows")
