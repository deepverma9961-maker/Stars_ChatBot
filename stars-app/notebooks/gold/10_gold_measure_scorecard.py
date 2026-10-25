# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # Gold Layer: Measure Scorecard
# MAGIC Creates `gold_measure_scorecard` — 1,260 rows (28 plans × 45 measures).
# MAGIC H3312 values match stars_v2.html `hedisData` exactly.

# COMMAND ----------
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, DoubleType
import random

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# H3312 reference values (must match HTML exactly)
H3312_HEDIS = {
    "HBD":    {"current_rate": 81.2, "open_gap_count": 2340, "status": "green",  "target_rate": 80.0, "projected_rate": 83.1},
    "CBP":    {"current_rate": 67.8, "open_gap_count": 4890, "status": "yellow", "target_rate": 70.0, "projected_rate": 70.2},
    "PCR":    {"current_rate": 79.1, "open_gap_count": 1124, "status": "green",  "target_rate": 75.0, "projected_rate": 80.4},
    "BCS":    {"current_rate": 73.4, "open_gap_count": 3210, "status": "yellow", "target_rate": 72.0, "projected_rate": 75.8},
    "COL":    {"current_rate": 66.3, "open_gap_count": 5672, "status": "red",    "target_rate": 68.0, "projected_rate": 68.9},
    "COA_MR": {"current_rate": 84.5, "open_gap_count": 890,  "status": "green",  "target_rate": 82.0, "projected_rate": 86.2},
    "COA_PA": {"current_rate": 76.2, "open_gap_count": 2156, "status": "yellow", "target_rate": 74.0, "projected_rate": 78.1},
    "OMW":    {"current_rate": 58.9, "open_gap_count": 3445, "status": "red",    "target_rate": 62.0, "projected_rate": 61.7},
    "EED":    {"current_rate": 71.3, "open_gap_count": 1876, "status": "yellow", "target_rate": 70.0, "projected_rate": 73.5},
    "KED":    {"current_rate": 63.7, "open_gap_count": 4123, "status": "red",    "target_rate": 65.0, "projected_rate": 66.4},
    "MRP":    {"current_rate": 88.4, "open_gap_count": 678,  "status": "green",  "target_rate": 86.0, "projected_rate": 89.7},
    "SPC":    {"current_rate": 69.8, "open_gap_count": 2987, "status": "yellow", "target_rate": 68.0, "projected_rate": 72.1},
    "TRC":    {"current_rate": 72.1, "open_gap_count": 1654, "status": "yellow", "target_rate": 70.0, "projected_rate": 74.3},
    "AMM":    {"current_rate": 61.4, "open_gap_count": 3892, "status": "red",    "target_rate": 64.0, "projected_rate": 64.2},
}
H3312_CAHPS = {
    "GNC": {"current_rate": 82.4, "status": "ok"},
    "GCQ": {"current_rate": 78.9, "status": "ok"},
    "DC":  {"current_rate": 91.2, "status": "ok"},
    "CS":  {"current_rate": 74.6, "status": "risk"},
    "HPR": {"current_rate": 68.3, "status": "risk"},
    "CC":  {"current_rate": 71.8, "status": "risk"},
}
THRESHOLDS = {
    "HBD": (80.0, 90.0), "CBP": (70.0, 80.0), "PCR": (75.0, 85.0),
    "BCS": (72.0, 82.0), "COL": (68.0, 78.0), "COA_MR": (82.0, 90.0),
    "COA_PA": (74.0, 84.0), "OMW": (62.0, 72.0), "EED": (70.0, 80.0),
    "KED": (65.0, 75.0), "MRP": (86.0, 94.0), "SPC": (68.0, 78.0),
    "TRC": (70.0, 80.0), "AMM": (64.0, 74.0),
}

def status_from_rate(rate, four_star):
    if rate >= four_star + 5: return "green"
    if rate >= four_star - 8: return "yellow"
    return "red"

# COMMAND ----------
plans = spark.table(f"{CATALOG}.stars_silver.silver_plan").collect()
measures = spark.table(f"{CATALOG}.stars_silver.silver_measure").collect()
plan_map = {r.contract_id: r.plan_key for r in plans if not r.contract_id.endswith("B")}

# Star-level offsets per contract for variation
STAR_OFFSET = {
    "H3312": 0.0, "H5521": -7.0, "H2213": +6.0, "H6614": +2.0,
    "H7723": -3.0, "H8812": +1.0, "H9914": -8.0, "H1045": -12.0,
    "H2156": +2.5, "H3267": +5.0, "H4378": -5.0, "H5489": +8.0,
    "H6590": +1.0, "H7601": +1.5,
}

rows = []
for contract_id, plan_key in plan_map.items():
    offset = STAR_OFFSET.get(contract_id, 0.0)
    rng = random.Random(hash(contract_id) + 99)
    for m in measures:
        if m.measure_category == "HEDIS":
            if contract_id == "H3312" and m.measure_code in H3312_HEDIS:
                ref = H3312_HEDIS[m.measure_code]
                rate = ref["current_rate"]
                gaps = ref["open_gap_count"]
                status = ref["status"]
                target = ref["target_rate"]
                projected = ref["projected_rate"]
            else:
                base_rate = H3312_HEDIS.get(m.measure_code, {}).get("current_rate", 70.0)
                rate = round(min(98, max(40, base_rate + offset + rng.gauss(0, 3))), 1)
                four_star = THRESHOLDS.get(m.measure_code, (70.0, 80.0))[0]
                target = float(four_star)
                eligible = max(1, round(base_rate * 100 / max(1, 100 - rate)))
                gaps = max(0, round(eligible * (1 - rate / 100)))
                status = status_from_rate(rate, four_star)
                projected = round(min(99, rate + rng.uniform(0.5, 3.5)), 1)
        elif m.measure_category == "CAHPS":
            if contract_id == "H3312" and m.measure_code in H3312_CAHPS:
                rate = H3312_CAHPS[m.measure_code]["current_rate"]
                status = H3312_CAHPS[m.measure_code]["status"]
            else:
                base = {"GNC": 82.4, "GCQ": 78.9, "DC": 91.2, "CS": 74.6, "HPR": 68.3, "CC": 71.8}.get(m.measure_code, 75.0)
                rate = round(min(98, max(50, base + offset * 0.5 + rng.gauss(0, 2))), 1)
                status = "ok" if rate >= 80 else ("risk" if rate >= 70 else "crit")
            gaps = 0
            target = 80.0
            projected = round(min(99, rate + rng.uniform(0, 2)), 1)
        else:
            rate = round(min(98, max(50, 75.0 + offset * 0.3 + rng.gauss(0, 4))), 1)
            gaps = 0
            target = 80.0
            status = "green" if rate >= 85 else ("yellow" if rate >= 70 else "red")
            projected = round(min(99, rate + 1.0), 1)

        rows.append(Row(
            scorecard_key=f"SC-{contract_id}-{m.measure_code}-{YEAR}",
            plan_key=plan_key,
            measure_key=m.measure_key,
            measurement_year=int(YEAR),
            current_rate=float(rate),
            open_gap_count=int(gaps),
            measure_status=str(status),
            target_rate=float(target),
            projected_rate=float(projected),
            last_updated="2025-06-10",
        ))

_schema = StructType([
    StructField("scorecard_key",    StringType(),  False),
    StructField("plan_key",         StringType(),  True),
    StructField("measure_key",      StringType(),  True),
    StructField("measurement_year", IntegerType(), True),
    StructField("current_rate",     DoubleType(),  True),
    StructField("open_gap_count",   LongType(),    True),
    StructField("measure_status",   StringType(),  True),
    StructField("target_rate",      DoubleType(),  True),
    StructField("projected_rate",   DoubleType(),  True),
    StructField("last_updated",     StringType(),  True),
])
spark.createDataFrame(rows, _schema).write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.stars_gold.gold_measure_scorecard")
print(f"gold_measure_scorecard: {len(rows)} rows")
