# Databricks notebook source
# Medicare Stars - CMS Public Data Layer
# Step 33: Build cms_plan_enrollment_history from CMS Monthly Enrollment files
#
# Source files (December snapshot per year, 2021–2025) uploaded to:
#   /Volumes/workspace/stars_tables/data/enrollment/
#
# Download from CMS:
#   https://www.cms.gov/research-statistics-data-systems/medicare-advantagepart-d-contract-and-enrollment-data/monthly-enrollment-contract
#
# Expected filenames (any name containing the 4-digit year is accepted):
#   CPSC_Enrollment_Info_2021_12.csv
#   CPSC_Enrollment_Info_2022_12.csv
#   CPSC_Enrollment_Info_2023_12.csv
#   CPSC_Enrollment_Info_2024_12.csv
#   CPSC_Enrollment_Info_2025_12.csv  (or latest available month for 2025)
#
# Each CMS file has one row per contract/plan/county.
# This notebook sums enrollment across all counties to get total per contract per year.
#
# Produces one gold table:
#
#   medicare_stars.gold.cms_plan_enrollment_history
#     One row per (measurement_year, contract_id)
#     Fields: measurement_year, contract_id, total_enrollment

# COMMAND ----------

# DBTITLE 1,Cell 2
import os
import re
import pandas as pd
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

CATALOG    = "aiagenticdemo"
VOLUME_DIR = "/Volumes/aiagenticdemo/stars_bronze/enrollmentdata"

# ─── Schema ──────────────────────────────────────────────────────────────────

ENROLLMENT_SCHEMA = StructType([
    StructField("measurement_year", IntegerType(), False),
    StructField("contract_id",      StringType(),  False),
    StructField("total_enrollment", IntegerType(),  True),
])

# COMMAND ----------

# ─── Helper: coerce enrollment value to int ───────────────────────────────────

def _to_int(val) -> int:
    if val is None:
        return 0
    try:
        return int(float(str(val).strip().replace(",", "")))
    except (ValueError, TypeError):
        return 0


# COMMAND ----------

# ─── Read all CSV files from the enrollment volume directory ──────────────────

print(f"Scanning: {VOLUME_DIR}")

try:
    all_files = os.listdir(VOLUME_DIR)
except FileNotFoundError:
    raise FileNotFoundError(
        f"Volume directory not found: {VOLUME_DIR}\n"
        "Please upload the CMS monthly enrollment CSV files to this path first.\n"
        "Download from: https://www.cms.gov/research-statistics-data-systems/"
        "medicare-advantagepart-d-contract-and-enrollment-data/monthly-enrollment-contract"
    )

csv_files = [f for f in all_files if f.lower().endswith(".csv")]
print(f"CSV files found: {csv_files}")

if not csv_files:
    raise ValueError(
        f"No CSV files found in {VOLUME_DIR}.\n"
        "Expected files like CPSC_Enrollment_Info_2021_12.csv"
    )

# COMMAND ----------

# ─── Parse each CSV and aggregate enrollment by contract ─────────────────────

all_rows = []

for fname in sorted(csv_files):
    # Extract year from filename
    m = re.search(r"(20\d{2})", fname)
    if not m:
        print(f"  Skipping {fname}: no 4-digit year found in filename")
        continue

    year = int(m.group(1))
    path = f"{VOLUME_DIR}/{fname}"
    print(f"\n── Year {year}: {fname} ──")

    # Read with latin-1 encoding to handle special characters in org names
    df = pd.read_csv(path, dtype=str, encoding="latin-1", low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    print(f"  Columns: {list(df.columns)[:10]}")
    print(f"  Rows: {len(df):,}")

    # ── Flexible column matching ──
    # CMS column names vary slightly across years:
    #   "Contract Number", "Contract_Number", "CONTRACT_NUMBER"
    #   "Enrollment", "Total Enrollment", "ENROLLMENT"
    cid_col = next(
        (c for c in df.columns if "contract" in c.lower() and "number" in c.lower()),
        None
    ) or next(
        (c for c in df.columns if c.lower() in ("contract", "contract_id", "contractid")),
        None
    ) or next(
        (c for c in df.columns if "contract" in c.lower()),
        None
    )

    enr_col = next(
        (c for c in df.columns if c.lower() == "enrollment"),
        None
    ) or next(
        (c for c in df.columns if "enrollment" in c.lower()),
        None
    )

    if not cid_col:
        print(f"  ERROR: Could not find contract ID column. Available: {list(df.columns)}")
        continue
    if not enr_col:
        print(f"  ERROR: Could not find enrollment column. Available: {list(df.columns)}")
        continue

    print(f"  Using contract col: '{cid_col}', enrollment col: '{enr_col}'")

    # ── Aggregate: sum enrollment across all counties per contract ──
    df["_enr"] = df[enr_col].apply(_to_int)
    agg = df.groupby(cid_col)["_enr"].sum().reset_index()
    agg.columns = ["contract_id", "total_enrollment"]

    # Filter to valid CMS contract IDs (letter + digits, e.g. H1234, S1234, R1234)
    valid = agg[agg["contract_id"].str.match(r"^[A-Z]\d+$", na=False)].copy()
    valid["measurement_year"] = year
    valid["total_enrollment"] = valid["total_enrollment"].astype(int)

    count = len(valid)
    total = valid["total_enrollment"].sum()
    print(f"  Contracts: {count:,}  |  Total enrollment: {total:,}")

    all_rows.extend(valid[["measurement_year", "contract_id", "total_enrollment"]].to_dict("records"))

print(f"\nTotal rows across all years: {len(all_rows):,}")

# COMMAND ----------

if not all_rows:
    raise ValueError(
        "No enrollment rows were parsed. Check that the CSV files:\n"
        "  1. Are placed in the correct volume directory\n"
        "  2. Contain columns matching 'contract number' and 'enrollment'\n"
        "  3. Have valid CMS contract IDs (letter + digits, e.g. H1234)"
    )

# ─── Write gold table ─────────────────────────────────────────────────────────



result_pdf = pd.DataFrame(all_rows)

# Show summary before writing
print("\n=== Enrollment Summary by Year ===")
summary = result_pdf.groupby("measurement_year").agg(
    contracts=("contract_id", "count"),
    total_enrollment=("total_enrollment", "sum")
).reset_index()
print(summary.to_string(index=False))

result_sdf = spark.createDataFrame(result_pdf, schema=ENROLLMENT_SCHEMA)

result_sdf.write \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.stars_gold.cms_plan_enrollment_history")

print(f"\nWrote {result_sdf.count():,} rows → {CATALOG}.stars_gold.cms_plan_enrollment_history")

# COMMAND ----------

# ─── Optimize ─────────────────────────────────────────────────────────────────

spark.sql(f"""
    OPTIMIZE {CATALOG}.stars_gold.cms_plan_enrollment_history
    ZORDER BY (measurement_year, contract_id)
""")
print("Optimization complete.")

# COMMAND ----------

# ─── Validation ───────────────────────────────────────────────────────────────

validation = spark.sql(f"""
    SELECT
        measurement_year,
        COUNT(*)                                AS total_contracts,
        SUM(total_enrollment)                   AS total_enrollment,
        ROUND(AVG(total_enrollment), 0)         AS avg_enrollment_per_contract,
        MAX(total_enrollment)                   AS max_contract_enrollment
    FROM {CATALOG}.stars_gold.cms_plan_enrollment_history
    GROUP BY measurement_year
    ORDER BY measurement_year
""")

print("\n=== cms_plan_enrollment_history Validation ===")
validation.show()
