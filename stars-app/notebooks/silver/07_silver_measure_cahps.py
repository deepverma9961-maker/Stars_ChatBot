# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Silver Layer: Measure Catalog & CAHPS Responses
# MAGIC Creates `silver_measure` (45 measures) and `silver_cahps_response` (12k top-box flagged).

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")

# COMMAND ----------
from pyspark.sql import SparkSession, Row
spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# --- silver_measure ---
MEASURES = [
    # HEDIS Part C (14 measures)
    ("HBD",    "Diabetes Care – Blood Sugar Controlled",                      "HEDIS", "C", 3),
    ("CBP",    "Controlling Blood Pressure",                                  "HEDIS", "C", 3),
    ("PCR",    "Plan All-Cause Readmissions",                                 "HEDIS", "C", 3),
    ("BCS",    "Breast Cancer Screening",                                     "HEDIS", "C", 1),
    ("COL",    "Colorectal Cancer Screening",                                 "HEDIS", "C", 1),
    ("COA_MR", "Care for Older Adults – Medication Review",                   "HEDIS", "C", 1),
    ("COA_PA", "Care for Older Adults – Pain Assessment",                     "HEDIS", "C", 1),
    ("OMW",    "Osteoporosis Management in Women who had a Fracture",         "HEDIS", "C", 1),
    ("EED",    "Diabetes Care – Eye Exam",                                    "HEDIS", "C", 1),
    ("KED",    "Kidney Health Evaluation for Patients with Diabetes",         "HEDIS", "C", 1),
    ("MRP",    "Medication Reconciliation Post-Discharge",                    "HEDIS", "C", 1),
    ("SPC",    "Statin Therapy for Patients with Cardiovascular Disease",     "HEDIS", "C", 1),
    ("TRC",    "Transitions of Care",                                         "HEDIS", "C", 1),
    ("AMM",    "Follow-up after ED Visit for People with Multiple High-Risk Chronic Conditions", "HEDIS", "C", 1),
    # CAHPS Part C (6 composites)
    ("GNC",    "Getting Needed Care",                                         "CAHPS", "C", 2),
    ("GCQ",    "Getting Care Quickly",                                        "CAHPS", "C", 2),
    ("DC",     "Doctor Communication",                                        "CAHPS", "C", 2),
    ("CS",     "Customer Service",                                            "CAHPS", "C", 2),
    ("HPR",    "Health Plan Rating",                                          "CAHPS", "C", 2),
    ("CC",     "Care Coordination",                                           "CAHPS", "C", 2),
    # CAHPS Part D (2 measures)
    ("RDP",    "Rating of Drug Plan",                                         "CAHPS", "D", 2),
    ("GNP",    "Getting Needed Prescription Drugs",                           "CAHPS", "D", 2),
    # HOS (5 measures)
    ("HOS_MI", "HOS – Monitoring Physical Activity",                         "HOS",   "C", 1),
    ("HOS_BP", "HOS – Reducing the Risk of Falling",                         "HOS",   "C", 1),
    ("HOS_PA", "HOS – Management of Urinary Incontinence",                   "HOS",   "C", 1),
    ("HOS_IV", "HOS – Improving or Maintaining Physical Health",              "HOS",   "C", 1),
    ("HOS_MH", "HOS – Improving or Maintaining Mental Health",               "HOS",   "C", 1),
    # Part D (5 measures)
    ("MTM",    "MTM Program Completion Rate for CMR",                        "PARTD", "D", 1),
    ("DAH",    "Medication Adherence for Hypertension (RAS Antagonists)",    "PARTD", "D", 3),
    ("DAC",    "Medication Adherence for Cholesterol (Statins)",              "PARTD", "D", 3),
    ("DAD",    "Medication Adherence for Diabetes Medications",               "PARTD", "D", 3),
    ("MPM",    "Medication Monitoring for People with Certain Chronic Conditions", "PARTD", "D", 1),
    # Operational (13 measures)
    ("CAR",    "Call Answer Rate",                                            "OPS",   "C", 1),
    ("ABT",    "Average Hold Time",                                           "OPS",   "C", 1),
    ("FCR",    "First Contact Resolution",                                    "OPS",   "C", 1),
    ("PAD",    "Prior Auth Decision Timeliness",                              "OPS",   "C", 1),
    ("GRI",    "Grievances Rate",                                             "OPS",   "C", 1),
    ("APL",    "Appeals Rate",                                                "OPS",   "C", 1),
    ("NWA",    "Network Adequacy Score",                                      "OPS",   "C", 1),
    ("FLU",    "Annual Flu Vaccine",                                          "CAHPS", "C", 1),
    ("AWV",    "Annual Wellness Visit Rate",                                  "OPS",   "C", 1),
    ("SNP",    "SNP Care Management",                                         "OPS",   "C", 1),
    ("COV",    "COVID-19 Vaccine",                                            "OPS",   "C", 1),
    ("SCP",    "Statin Prescribing Rate",                                     "OPS",   "C", 1),
    ("OBP",    "Optimizing BP Control",                                       "OPS",   "C", 1),
]

measure_rows = [
    Row(measure_key=f"MSR-{i:04d}", measure_code=m[0], measure_name=m[1],
        measure_category=m[2], part=m[3], measure_weight=m[4])
    for i, m in enumerate(MEASURES)
]
spark.createDataFrame(measure_rows).write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_silver.silver_measure")
print(f"silver_measure: {len(measure_rows)} rows")

# COMMAND ----------
# --- silver_cahps_response ---
from pyspark.sql import functions as F
from pyspark.sql.functions import col

bronze_cahps = spark.table(f"{CATALOG}.stars_bronze.bronze_cahps_survey_raw")

silver_cahps = (
    bronze_cahps
    .withColumn("cahps_response_key", F.expr("uuid()"))
    .withColumn("top_box_flag",
        F.when(
            (col("scale_type") == "likert") & (col("response_value") >= 4), True
        ).when(
            (col("scale_type") == "rating_10") & (col("response_value") >= 9), True
        ).otherwise(False)
    )
    .select(
        "cahps_response_key", "member_id", "survey_date",
        "composite_code", "composite_name", "question_code",
        "response_value", "scale_type", "top_box_flag",
    )
)
silver_cahps.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.stars_silver.silver_cahps_response")
print(f"silver_cahps_response: {silver_cahps.count():,} rows")

# Validate top-box rates by composite
display(
    silver_cahps.groupBy("composite_code")
    .agg(F.avg(col("top_box_flag").cast("double")).alias("top_box_rate"))
    .orderBy("composite_code")
)
