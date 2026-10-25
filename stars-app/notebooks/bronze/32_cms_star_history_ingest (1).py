# Databricks notebook source
# Medicare Stars - CMS Public Data Layer
# Step 32: Ingest CMS Star Ratings from CMS_StarRatings_REAL_2021_2025 (1).xlsx
#
# Reads a single Excel workbook uploaded to the Unity Catalog Volume:
#   /Volumes/workspace/stars_tables/data/CMS_StarRatings_REAL_2021_2025 (1).xlsx
#
# The workbook contains 8 sheets. This notebook reads three of them:
#   - "📊 All Contracts (Stars)"  — measure-level star ratings per contract per year
#   - "🏢 Company Directory"      — plan-level overall star ratings per year
#   - "📈 Part C Measure Trends"  — measure code → domain lookup (Part C)
#   - "💊 Part D Measure Trends"  — measure code → domain lookup (Part D)
#
# Produces two gold tables:
#
#   1. medicare_stars.gold.cms_plan_star_history
#      One row per (measurement_year, contract_id)
#      Fields: org_name, plan_name, plan_type, overall_star_rating
#
#   2. medicare_stars.gold.cms_measure_star_history
#      One row per (measurement_year, contract_id, measure_id)
#      Fields: org_name, measure_name, domain, star_rating

# COMMAND ----------

import re
import pandas as pd
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType
)

CATALOG          = "aiagenticdemo"
MEASUREMENT_YEAR = "2027"

# ─── Volume path ─────────────────────────────────────────────────────────────
VOLUME_FILE = "/Volumes/aiagenticdemo/stars_bronze/data/CMS_StarRatings_REAL_2021_2027.xlsx"

YEARS = [2021, 2022, 2023, 2024, 2025,2026,2027]

# ─── Sheet name constants ─────────────────────────────────────────────────────
SHEET_STARS     = "\U0001f4ca All Contracts (Stars)"   # 📊
SHEET_DIRECTORY = "\U0001f3e2 Company Directory"        # 🏢
SHEET_PARTC     = "\U0001f4c8 Part C Measure Trends"   # 📈
SHEET_PARTD     = "\U0001f4ca Part D Measure Trends"   # 💊 (same emoji, different sheet)

# ─── Schemas ─────────────────────────────────────────────────────────────────

PLAN_SCHEMA = StructType([
    StructField("measurement_year",    IntegerType(), False),
    StructField("contract_id",         StringType(),  False),
    StructField("plan_id",             StringType(),  True),
    StructField("org_name",            StringType(),  True),
    StructField("plan_name",           StringType(),  True),
    StructField("plan_type",           StringType(),  True),
    StructField("state",               StringType(),  True),
    StructField("overall_star_rating", DoubleType(),  True),
    StructField("part_c_star_rating",  DoubleType(),  True),
    StructField("part_d_star_rating",  DoubleType(),  True),
    StructField("total_enrollment",    IntegerType(), True),
])

MEASURE_SCHEMA = StructType([
    StructField("measurement_year", IntegerType(), False),
    StructField("contract_id",      StringType(),  False),
    StructField("plan_id",          StringType(),  True),
    StructField("org_name",         StringType(),  True),
    StructField("measure_id",       StringType(),  False),
    StructField("measure_name",     StringType(),  True),
    StructField("domain",           StringType(),  True),
    StructField("score",            DoubleType(),  True),
    StructField("star_rating",      DoubleType(),  True),
])

# COMMAND ----------

# ─── Helper: coerce a CMS value to float ─────────────────────────────────────
# CMS uses "—", "*", "Plan not required to report measure", blanks, etc.
_MISSING_VALS = {
    "—", "-", "*", "na", "n/a", "nan", "none", "",
    "plan not required to report measure",
    "not applicable", "not available", "suppressed",
}

def _to_float(val) -> float | None:
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in _MISSING_VALS:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _clean_str(val) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    if s.lower() in ("nan", "none", ""):
        return None
    return s


# COMMAND ----------

# ─── Parse domain lookup from Part C and Part D Measure Trends ───────────────

def parse_domain_lookup(xl: pd.ExcelFile) -> dict:
    """Return {measure_code: domain} from Part C and Part D Measure Trends sheets."""
    lookup = {}
    sheets_to_try = []
    for name in xl.sheet_names:
        if "Measure Trends" in name or "Part C" in name or "Part D" in name:
            sheets_to_try.append(name)

    for sheet in sheets_to_try:
        try:
            df = xl.parse(sheet, header=1)
            # Normalize column names
            df.columns = [str(c).strip() for c in df.columns]
            code_col   = next((c for c in df.columns if "Measure Code" in c or "Code" in c), None)
            domain_col = next((c for c in df.columns if "Domain" in c), None)
            if code_col and domain_col:
                for _, row in df.iterrows():
                    code   = _clean_str(row.get(code_col))
                    domain = _clean_str(row.get(domain_col))
                    if code:
                        lookup[code] = domain
        except Exception as e:
            print(f"  Warning: could not parse domain sheet '{sheet}': {e}")

    print(f"  Domain lookup: {len(lookup)} entries from {len(sheets_to_try)} sheets")
    return lookup


# COMMAND ----------

# ─── Parse plan-level overall star ratings from Company Directory ─────────────

def parse_plan_directory(xl: pd.ExcelFile) -> pd.DataFrame:
    """
    Read the Company Directory sheet and return a long-format DataFrame:
    (contract_id, org_name, plan_name, plan_type, measurement_year, overall_star_rating)
    """
    # Find the sheet
    dir_sheet = next(
        (s for s in xl.sheet_names if "Company Directory" in s or "Directory" in s),
        None
    )
    if not dir_sheet:
        print("  Warning: Company Directory sheet not found — plan history will be empty")
        return pd.DataFrame()

    df = xl.parse(dir_sheet, header=1)
    df.columns = [str(c).strip() for c in df.columns]

    # Identify year columns
    year_cols = {y: f"{y} Stars" for y in YEARS if f"{y} Stars" in df.columns}
    if not year_cols:
        print(f"  Warning: No year columns found in Company Directory. Cols: {list(df.columns)}")
        return pd.DataFrame()

    # Identify ID/name columns (flexible lookup)
    def _find_col(hints):
        for h in hints:
            m = next((c for c in df.columns if h.lower() in c.lower()), None)
            if m:
                return m
        return None

    cid_col   = _find_col(["Contract ID", "ContractID"])
    org_col   = _find_col(["Parent Organization", "Parent Org", "Organization"])
    name_col  = _find_col(["Contract Name", "ContractName", "Marketing Name"])
    type_col  = _find_col(["Organization Type", "Org Type", "Type"])

    if not cid_col:
        raise ValueError(f"Contract ID column not found in Company Directory. Cols: {list(df.columns)}")

    rows = []
    for _, row in df.iterrows():
        cid = _clean_str(row.get(cid_col))
        if not cid or not re.match(r"^[A-Z]\d+$", cid):
            continue
        for year, col in year_cols.items():
            rows.append({
                "measurement_year":    year,
                "contract_id":         cid,
                "plan_id":             "000",
                "org_name":            _clean_str(row.get(org_col))   if org_col  else None,
                "plan_name":           _clean_str(row.get(name_col))  if name_col else None,
                "plan_type":           _clean_str(row.get(type_col))  if type_col else None,
                "state":               None,
                "overall_star_rating": _to_float(row.get(col)),
                "part_c_star_rating":  None,
                "part_d_star_rating":  None,
                "total_enrollment":    None,
            })

    result = pd.DataFrame(rows)
    print(f"  Company Directory: {len(result):,} plan-year rows ({result['measurement_year'].nunique()} years, {result['contract_id'].nunique()} contracts)")
    return result


# COMMAND ----------

# ─── Parse measure-level star ratings from All Contracts (Stars) ──────────────

def parse_stars_sheet(xl: pd.ExcelFile) -> pd.DataFrame:
    """
    Read the wide-format Stars sheet and return a long-format DataFrame:
    (contract_id, org_name, measurement_year, measure_id, measure_name, star_rating)

    Sheet layout (header=None):
      Row 0: title (skip)
      Row 1: CONTRACT_ID ... then year-group labels "2021 STAR RATINGS (46 measures)", ...
      Row 2: measure labels "C01: Breast Cancer Screening", ...
      Row 3+: contract data
    """
    stars_sheet = next(
        (s for s in xl.sheet_names if "All Contracts" in s and "Stars" in s),
        None
    )
    if not stars_sheet:
        print("  Warning: All Contracts (Stars) sheet not found")
        return pd.DataFrame()

    df_raw = xl.parse(stars_sheet, header=None)
    row1   = df_raw.iloc[1, :]   # year-group headers
    row2   = df_raw.iloc[2, :]   # measure labels
    data   = df_raw.iloc[3:, :].reset_index(drop=True)

    # ── Identify ID columns (cols 0-4) ──
    # CONTRACT_ID is always col 0; ORG TYPE col 1; CONTRACT NAME col 2;
    # MARKETING NAME col 3; PARENT ORGANIZATION col 4
    # ── Find year group start columns ──
    year_starts = {}
    for idx, val in enumerate(row1):
        if pd.notna(val):
            m = re.search(r"(20\d{2})\s+STAR RATINGS", str(val), re.IGNORECASE)
            if m:
                year_starts[int(m.group(1))] = idx

    if not year_starts:
        raise ValueError("No year-group columns found in Stars sheet.")

    print(f"  Stars sheet year starts: { {y: c for y, c in sorted(year_starts.items())} }")

    # ── Build sorted year boundaries ──
    sorted_years = sorted(year_starts.keys())
    year_bounds  = {}
    for i, yr in enumerate(sorted_years):
        start = year_starts[yr]
        end   = year_starts[sorted_years[i + 1]] if i + 1 < len(sorted_years) else len(row1)
        year_bounds[yr] = (start, end)

    # ── Extract measure codes and names from row 2 ──
    def _parse_measure_label(label: str):
        """Split 'C01: Breast Cancer Screening' → ('C01', 'Breast Cancer Screening')"""
        label = str(label).strip()
        m = re.match(r"^([A-Z]\d+):\s*(.+)$", label)
        if m:
            return m.group(1), m.group(2).strip()
        return label[:10], label   # fallback

    # ── Melt each year block into long rows ──
    all_rows = []
    for yr, (start, end) in year_bounds.items():
        measure_cols = list(range(start, end))
        for col_idx in measure_cols:
            measure_label = row2.iloc[col_idx]
            if pd.isna(measure_label):
                continue
            measure_id, measure_name = _parse_measure_label(str(measure_label))

            for row_idx in range(len(data)):
                row  = data.iloc[row_idx, :]
                cid  = _clean_str(row.iloc[0])
                if not cid or not re.match(r"^[A-Z]\d+$", cid):
                    continue
                org  = _clean_str(row.iloc[4])   # PARENT ORGANIZATION
                star = _to_float(row.iloc[col_idx])

                all_rows.append({
                    "measurement_year": yr,
                    "contract_id":      cid,
                    "plan_id":          "000",
                    "org_name":         org,
                    "measure_id":       measure_id,
                    "measure_name":     measure_name,
                    "star_rating":      star,
                })

    result = pd.DataFrame(all_rows)
    print(f"  Stars sheet: {len(result):,} measure-contract-year rows")
    return result


# COMMAND ----------

# DBTITLE 1,Install openpyxl for Excel file reading
# MAGIC %pip install openpyxl

# COMMAND ----------

# ─── Main ingestion ───────────────────────────────────────────────────────────

print(f"Opening: {VOLUME_FILE}")
xl = pd.ExcelFile(VOLUME_FILE)
print(f"Sheets found: {xl.sheet_names}")

# COMMAND ----------

print("\n── Step 1: Domain lookup ──")
domain_lookup = parse_domain_lookup(xl)

# COMMAND ----------

print("\n── Step 2: Plan-level star history ──")
plan_pdf = parse_plan_directory(xl)

# COMMAND ----------

print("\n── Step 3: Measure-level star history ──")
measure_pdf = parse_stars_sheet(xl)

# COMMAND ----------

CATALOG_1 = "aiagenticdemo"

# COMMAND ----------

plan_pdf.display()

# COMMAND ----------

# ─── Write plan history table ─────────────────────────────────────────────────

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_1}.stars_gold")

plan_sdf = spark.createDataFrame(plan_pdf, schema=PLAN_SCHEMA)
plan_sdf.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    f"{CATALOG_1}.stars_gold.cms_plan_star_history"
)
print(f"Wrote {plan_sdf.count():,} rows → {CATALOG_1}.stars_gold.cms_plan_star_history")

# COMMAND ----------

# DBTITLE 1,Cell 14
# ─── Write measure history table ──────────────────────────────────────────────

# Attach domain from lookup
measure_pdf["domain"] = measure_pdf["measure_id"].map(domain_lookup)
measure_pdf["score"]  = None   # raw performance data not ingested here

# Reorder columns to match MEASURE_SCHEMA field order
measure_pdf = measure_pdf[[
    "measurement_year", "contract_id", "plan_id", "org_name",
    "measure_id", "measure_name", "domain", "score", "star_rating"
]]

measure_sdf = spark.createDataFrame(measure_pdf, schema=MEASURE_SCHEMA)
measure_sdf.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    f"{CATALOG_1}.stars_gold.cms_measure_star_history"
)
print(f"Wrote {measure_sdf.count():,} rows → {CATALOG_1}.stars_gold.cms_measure_star_history")

# COMMAND ----------

# ─── Optimize ─────────────────────────────────────────────────────────────────

spark.sql(f"""
    OPTIMIZE {CATALOG_1}.stars_gold.cms_plan_star_history
    ZORDER BY (measurement_year, overall_star_rating)
""")

spark.sql(f"""
    OPTIMIZE {CATALOG_1}.stars_gold.cms_measure_star_history
    ZORDER BY (measurement_year, contract_id, measure_id)
""")

print("Optimization complete.")

# COMMAND ----------

# ─── Validation summary ───────────────────────────────────────────────────────

plan_counts = spark.sql(f"""
    SELECT measurement_year,
           COUNT(*)                                          AS total_contracts,
           COUNT(CASE WHEN overall_star_rating IS NOT NULL THEN 1 END) AS rated_contracts,
           ROUND(AVG(overall_star_rating), 2)               AS avg_rating
    FROM {CATALOG_1}.stars_gold.cms_plan_star_history
    GROUP BY measurement_year
    ORDER BY measurement_year
""")
print("\n=== Plan Star History Summary ===")
plan_counts.show()

measure_counts = spark.sql(f"""
    SELECT measurement_year,
           COUNT(DISTINCT measure_id) AS distinct_measures,
           COUNT(*)                   AS total_rows,
           COUNT(CASE WHEN star_rating IS NOT NULL THEN 1 END) AS rated_rows
    FROM {CATALOG_1}.stars_gold.cms_measure_star_history
    GROUP BY measurement_year
    ORDER BY measurement_year
""")
print("\n=== Measure Star History Summary ===")
measure_counts.show()
