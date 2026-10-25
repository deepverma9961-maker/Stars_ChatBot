# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Gold Layer: Star Rating Summary
# MAGIC Creates `gold_star_rating_summary` — one row per plan with overall star ratings.

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
dbutils.widgets.text("measurement_year", "2025")

CATALOG = dbutils.widgets.get("catalog")
YEAR = int(dbutils.widgets.get("measurement_year"))

# COMMAND ----------
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
spark = SparkSession.builder.getOrCreate()
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.stars_gold")

# COMMAND ----------
# Reference star ratings from stars_v2.html for all 14 contracts
STAR_DATA = [
    ("H3312", 4.0, 4.0, 3.8, 4.2, 4.0, 4.1, True,  2_250_000),
    ("H5521", 3.5, 3.5, 3.4, 3.6, 3.5, 3.7, False, 0),
    ("H2213", 4.5, 4.5, 4.6, 4.4, 4.5, 4.3, True,  6_740_000),
    ("H6614", 4.0, 4.0, 3.9, 4.1, 4.0, 3.8, True,  3_365_000),
    ("H7723", 3.5, 4.0, 3.7, 3.8, 3.5, 3.9, True,  4_455_000),
    ("H8812", 4.0, 4.0, 4.0, 3.9, 4.0, 4.2, True,  2_730_000),
    ("H9914", 3.5, 3.5, 3.3, 3.7, 3.5, 3.4, False, 0),
    ("H1045", 3.0, 3.5, 3.2, 3.3, 3.0, 3.1, False, 0),
    ("H2156", 4.0, 4.0, 4.1, 3.8, 4.0, 4.0, True,  3_090_000),
    ("H3267", 4.0, 4.5, 4.2, 4.3, 4.0, 4.1, True,  2_445_000),
    ("H4378", 3.5, 3.5, 3.6, 3.4, 3.5, 3.3, False, 0),
    ("H5489", 4.5, 4.5, 4.7, 4.3, 4.5, 4.4, True,  1_920_000),
    ("H6590", 4.0, 4.0, 3.9, 4.0, 4.0, 3.9, True,  2_205_000),
    ("H7601", 4.0, 4.0, 4.0, 4.1, 4.0, 3.8, True,  2_950_000),
]

plans = spark.table(f"{CATALOG}.stars_silver.silver_plan") \
    .filter("contract_id NOT LIKE '%B'") \
    .select("plan_key", "contract_id").collect()
plan_map = {r.contract_id: r.plan_key for r in plans}

rows = []
for cid, py, proj, hedis, cahps, hos, partd, bonus, bonus_amt in STAR_DATA:
    plan_key = plan_map.get(cid)
    if not plan_key:
        continue
    rows.append(Row(
        star_summary_key=f"SS-{cid}-{YEAR}",
        plan_key=plan_key,
        contract_id=cid,
        measurement_year=YEAR,
        prior_year_star_rating=py,
        projected_star_rating=proj,
        hedis_domain_rating=hedis,
        cahps_domain_rating=cahps,
        hos_domain_rating=hos,
        partd_domain_rating=partd,
        bonus_eligible_flag=bonus,
        estimated_bonus_amount=float(bonus_amt),
        last_updated="2025-06-10",
    ))

_schema = StructType([
    StructField("star_summary_key",       StringType(),  False),
    StructField("plan_key",               StringType(),  True),
    StructField("contract_id",            StringType(),  True),
    StructField("measurement_year",       IntegerType(), True),
    StructField("prior_year_star_rating", DoubleType(),  True),
    StructField("projected_star_rating",  DoubleType(),  True),
    StructField("hedis_domain_rating",    DoubleType(),  True),
    StructField("cahps_domain_rating",    DoubleType(),  True),
    StructField("hos_domain_rating",      DoubleType(),  True),
    StructField("partd_domain_rating",    DoubleType(),  True),
    StructField("bonus_eligible_flag",    BooleanType(), True),
    StructField("estimated_bonus_amount", DoubleType(),  True),
    StructField("last_updated",           StringType(),  True),
])
spark.createDataFrame(rows, _schema).write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.stars_gold.gold_star_rating_summary")
print(f"gold_star_rating_summary: {len(rows)} rows written")
display(spark.table(f"{CATALOG}.stars_gold.gold_star_rating_summary").select("contract_id", "projected_star_rating", "bonus_eligible_flag"))
