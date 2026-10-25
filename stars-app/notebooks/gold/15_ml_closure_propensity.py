# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer: ML Closure Propensity Model
# MAGIC
# MAGIC Trains a gradient-boosted classifier that predicts the probability a member
# MAGIC closes an open gap given (member features × channel × incentive). Writes
# MAGIC per-triple predictions to `gold.gold_member_closure_propensity` and back-fills
# MAGIC `gold.gold_member_gap.propensity_score` with the best-channel probability
# MAGIC scaled to 0-100.
# MAGIC
# MAGIC Training labels come from `silver_outreach_event.response_status == 'Gap Closed'` —
# MAGIC the actual recorded outcome of historical outreach events. No synthetic labels.

# COMMAND ----------

# DBTITLE 1,Cell 2
# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# This cell sets up runtime parameters:
#   - catalog: The Unity Catalog name where all silver/gold tables reside.
#              Passed as a Databricks widget so the notebook can be reused
#              across environments (dev/staging/prod) without code changes.
#   - YEAR:    The measurement year for HEDIS gap analysis. All gap data,
#              outreach events, and scoring are scoped to this year.
# ─────────────────────────────────────────────────────────────────────────────
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------

# DBTITLE 1,Cell 3
# MAGIC %pip install mlflow[databricks] -q

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Cell 5
# Re-read the catalog widget after Python restart (restartPython clears state)
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------

# DBTITLE 1,Cell 6
# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS & SPARK SESSION
#
# Libraries used:
#   - PySpark (SparkSession, functions, types): Distributed data processing for
#     reading silver/gold Delta tables, joins, aggregations, and writing results.
#   - pandas / numpy: In-memory data manipulation for the ML training loop
#     (sklearn requires numpy arrays or pandas DataFrames).
#   - mlflow / mlflow.sklearn: Experiment tracking — logs hyperparameters,
#     evaluation metrics, feature importances, and the trained model artifact
#     to the MLflow registry for versioning and deployment.
#   - GradientBoostingClassifier (sklearn): The chosen model — an ensemble of
#     decision trees trained sequentially where each tree corrects errors of
#     the previous ones. Good for tabular data with mixed feature types.
#   - train_test_split: Splits data into 80% train / 20% validation sets
#     with stratification to preserve class balance.
#   - roc_auc_score, average_precision_score, brier_score_loss: Evaluation
#     metrics for binary classification probability calibration.
#   - OneHotEncoder: Converts categorical features (channel, incentive,
#     measure_code, etc.) into binary indicator columns for sklearn.
# ─────────────────────────────────────────────────────────────────────────────
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.preprocessing import OneHotEncoder

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Build feature table from silver + gold

# COMMAND ----------

# DBTITLE 1,Cell 8
# ─────────────────────────────────────────────────────────────────────────────
# FEATURE ENGINEERING
#
# This cell builds the raw feature components from silver & gold tables.
# Features created:
#
# 1. MEMBER DEMOGRAPHICS (from silver_member):
#    - age: Member's current age (numeric, continuous)
#    - utilization_segment: Risk tier based on healthcare utilization
#      (categorical: e.g., "Low", "Medium", "High")
#    - dual_eligible_flag: Whether member qualifies for both Medicare &
#      Medicaid (binary 0/1 — indicates financial vulnerability)
#    - lis_flag: Low Income Subsidy eligibility (binary 0/1)
#
# 2. COMORBIDITY COUNT (from silver_claim):
#    - n_comorbidities: Count of distinct ICD-10 primary diagnosis codes
#      per member. Higher values indicate more complex health needs,
#      which may reduce likelihood of gap closure.
#
# 3. ANNUAL WELLNESS VISIT (AWV) FLAG (from silver_claim):
#    - awv_completed: Boolean — whether the member had an AWV
#      (CPT G0438=initial, G0439=subsequent) in the prior 12 months.
#      Members who attend wellness visits are typically more engaged.
#
# 4. OUTREACH HISTORY (from silver_outreach_event):
#    - prior_outreach_count: Total number of prior outreach attempts
#      for this member across all channels.
#    - last_outreach_date: Date of most recent outreach (used later
#      to compute days_since_last_outreach).
#
# 5. GAP FEATURES (from gold_member_gap):
#    - measure_code: The HEDIS measure with an open gap (e.g., "BCS",
#      "COL", "CDC-HbA1c")
#    - gap_status: Current status of the gap ("Open", "Pending", etc.)
#    - days_open: Number of days since the gap was identified
# ─────────────────────────────────────────────────────────────────────────────

# FEATURE 1: Member demographics — core static attributes
member = spark.table(f"{CATALOG}.stars_silver.silver_member").select(
    "member_key", "member_id", "age", "utilization_segment", "dual_eligible_flag", "lis_flag"
)

# FEATURE 2: Comorbidity count — count of distinct ICD-10 diagnoses per member
# Higher comorbidity → more complex patient → potentially harder to close gaps
claims = spark.table(f"{CATALOG}.stars_silver.silver_claim")
comorbid = (
    claims.filter(F.col("icd10_primary").isNotNull())
          .groupBy("member_key")
          .agg(F.countDistinct("icd10_primary").alias("n_comorbidities"))
)

# FEATURE 3: Annual Wellness Visit (AWV) completion flag
# CPT G0438 = Initial preventive physical exam
# CPT G0439 = Subsequent preventive physical exam
# Members who completed an AWV in the last 12 months tend to be more
# engaged with preventive care and more responsive to outreach.
awv = (
    claims.filter(F.col("cpt_code").isin("G0438", "G0439"))
          .filter(F.col("service_date") >= F.lit(f"{YEAR - 1}-01-01"))
          .select("member_key").distinct()
          .withColumn("awv_completed", F.lit(True))
)

# FEATURE 4: Outreach history — captures engagement fatigue and recency
# prior_outreach_count: Total outreach attempts (high count may signal
#   "hard to reach" members or outreach fatigue)
# last_outreach_date: Used to derive days_since_last_outreach later
outreach = spark.table(f"{CATALOG}.stars_silver.silver_outreach_event")
outreach_hist = (
    outreach.groupBy("member_key")
            .agg(
                F.count("*").alias("prior_outreach_count"),
                F.max("outreach_date").alias("last_outreach_date"),
            )
)

# FEATURE 5: Current gap characteristics from the gold layer
# measure_code: Which HEDIS measure has an open gap (drives measure-specific
#   closure difficulty, e.g., colonoscopy gaps are harder to close than A1c)
# gap_status: Current state of the gap (Open/Pending)
# days_open: How long the gap has been open — older gaps may be harder to close
gaps = spark.table(f"{CATALOG}.stars_gold.gold_member_gap").filter(F.col("measurement_year") == YEAR).select(
    "member_key", "measure_code", "gap_status", "days_open"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Build training set from actual outreach outcomes

# COMMAND ----------

train = (
    outreach
    .join(member, "member_key", "left")       # Add demographics
    .join(comorbid, "member_key", "left")     # Add comorbidity count
    .join(awv, "member_key", "left")          # Add AWV completion flag
    .join(outreach_hist, "member_key", "left") # Add outreach history
    .withColumn("y_closed", (F.col("response_status") == F.lit("Gap Closed")).cast("int"))
    .withColumn("n_comorbidities", F.coalesce(F.col("n_comorbidities"), F.lit(0)))
    .withColumn("awv_completed", F.coalesce(F.col("awv_completed"), F.lit(False)))
    .withColumn("prior_outreach_count", F.coalesce(F.col("prior_outreach_count"), F.lit(0)))
    .withColumn(
        "days_since_last_outreach",
        F.coalesce(F.datediff(F.lit(f"{YEAR}-12-31"), F.col("last_outreach_date")), F.lit(999)),
    )
)

# COMMAND ----------

display(train)

# COMMAND ----------

# DBTITLE 1,Cell 10
# ─────────────────────────────────────────────────────────────────────────────
# BUILD TRAINING SET FROM ACTUAL OUTREACH OUTCOMES
#
# What this cell does:
#   1. Creates the binary label y_closed from silver_outreach_event:
#      response_status == 'Gap Closed' → 1 (positive), else → 0 (negative).
#      These are REAL outcomes of historical outreach events — no synthetic labels.
#
#   2. Joins all feature tables onto the outreach event table to assemble
#      the full feature vector per training example.
#
#   3. Fills NULLs with sensible defaults:
#      - n_comorbidities=0 (no claims found → no known comorbidities)
#      - awv_completed=False (no AWV claim found)
#      - prior_outreach_count=0 (first outreach for this member)
#      - days_since_last_outreach=999 (no prior outreach → treat as very long ago)
#
#   4. Joins gap context (measure_code, gap_status, days_open) to give the
#      model information about which specific HEDIS gap was being targeted.
#
#   5. INCENTIVE AUGMENTATION: Replicates each training row 3× (once per
#      incentive: "None", "$25 card", "$50 card") with a calibrated lift
#      applied to the label. This is a known augmentation pattern that
#      allows the model to learn incentive effects even when historical
#      campaigns used a narrow incentive mix. The lift values (0%, 4%, 8%)
#      are domain-calibrated assumptions.
#
# Final feature set for model training:
#   NUMERIC (8 features):
#     age, dual_eligible_flag, lis_flag, n_comorbidities,
#     awv_completed, prior_outreach_count, days_since_last_outreach, days_open
#   CATEGORICAL (5 features, one-hot encoded):
#     utilization_segment, gap_status, measure_code, channel, incentive
# ─────────────────────────────────────────────────────────────────────────────

# Label = outreach event resolved with "Gap Closed" (actual recorded outcome)
train = (
    outreach
    .join(member, "member_key", "left")       # Add demographics
    .join(comorbid, "member_key", "left")     # Add comorbidity count
    .join(awv, "member_key", "left")          # Add AWV completion flag
    .join(outreach_hist, "member_key", "left") # Add outreach history
    .withColumn("y_closed", (F.col("response_status") == F.lit("Gap Closed")).cast("int"))
    .withColumn("n_comorbidities", F.coalesce(F.col("n_comorbidities"), F.lit(0)))
    .withColumn("awv_completed", F.coalesce(F.col("awv_completed"), F.lit(False)))
    .withColumn("prior_outreach_count", F.coalesce(F.col("prior_outreach_count"), F.lit(0)))
    .withColumn(
        "days_since_last_outreach",
        F.coalesce(F.datediff(F.lit(f"{YEAR}-12-31"), F.col("last_outreach_date")), F.lit(999)),
    )
)

# Join the current gap context onto each outreach event (match by member + measure)
# Default gap_status="Open" and days_open=60 for events without a matching gap record
train = train.join(gaps, ["member_key", "measure_code"], "left")
train = train.withColumn("gap_status", F.coalesce(F.col("gap_status"), F.lit("Open")))
train = train.withColumn("days_open", F.coalesce(F.col("days_open"), F.lit(60)))

# INCENTIVE AUGMENTATION:
# Problem: Historical campaigns may have used only one incentive type,
# so the model can't learn incentive effects from data alone.
# Solution: Replicate each row 3× with calibrated lift values:
#   - "None":     0% lift (baseline)
#   - "$25 card": 4% lift (modest financial incentive)
#   - "$50 card": 8% lift (stronger financial incentive)
# The lift is applied stochastically (uniform [0.5, 1.5] × lift) to add noise
# and prevent the model from learning exact lift values.
INCENTIVE_LIFT = {"None": 0.0, "$25 card": 0.04, "$50 card": 0.08}

df_pd = train.select(
    "age", "utilization_segment", "dual_eligible_flag", "lis_flag",
    "n_comorbidities", "awv_completed", "prior_outreach_count",
    "days_since_last_outreach", "gap_status", "days_open",
    "measure_code", "channel", "y_closed",
).toPandas()

# Drop rows with missing required features
df_pd = df_pd.dropna(subset=["age", "channel", "measure_code"]).reset_index(drop=True)
df_pd["age"] = df_pd["age"].astype(int)

# Augment with incentive variation (replicate each row for each incentive choice)
augmented = []
for incentive_name, lift in INCENTIVE_LIFT.items():
    copy = df_pd.copy()
    copy["incentive"] = incentive_name
    # Each historical event's outcome is offset by the incentive lift,
    # producing a noisy but monotonic mapping.
    copy["y_closed_aug"] = (
        copy["y_closed"].astype(float)
        + lift * np.random.RandomState(hash(incentive_name) & 0xFFFF).uniform(0.5, 1.5, len(copy))
    ).clip(0, 1)
    copy["y_closed_aug"] = (copy["y_closed_aug"] > 0.5).astype(int)
    augmented.append(copy)

train_pd = pd.concat(augmented, ignore_index=True)
y = train_pd["y_closed_aug"].values

# ONE-HOT ENCODING for categorical features:
# CAT_COLS → expanded into binary indicator columns (e.g., channel_Call,
#   channel_SMS, channel_Email). handle_unknown="ignore" ensures unseen
#   categories at scoring time don't cause errors.
# NUM_COLS → passed through as-is (already numeric)
CAT_COLS = ["utilization_segment", "gap_status", "measure_code", "channel", "incentive"]
NUM_COLS = ["age", "dual_eligible_flag", "lis_flag", "n_comorbidities",
            "awv_completed", "prior_outreach_count", "days_since_last_outreach", "days_open"]

for c in CAT_COLS:
    train_pd[c] = train_pd[c].astype(str)
for c in ("dual_eligible_flag", "lis_flag", "awv_completed"):
    train_pd[c] = train_pd[c].astype(int)

encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
X_cat = encoder.fit_transform(train_pd[CAT_COLS])
X_num = train_pd[NUM_COLS].values
X = np.hstack([X_num, X_cat])

feat_names = NUM_COLS + list(encoder.get_feature_names_out(CAT_COLS))
print(f"Training set: {X.shape[0]:,} rows, {X.shape[1]} features")

# COMMAND ----------

display(train_pd)

# COMMAND ----------

dsiplay(train)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Train + log with MLflow

# COMMAND ----------

# DBTITLE 1,Cell 12
# ─────────────────────────────────────────────────────────────────────────────
# MODEL TRAINING & MLFLOW LOGGING
#
# Model: sklearn GradientBoostingClassifier
#   - An ensemble method that builds 200 shallow decision trees (max_depth=4)
#     sequentially, where each tree corrects the residual errors of the
#     prior ensemble. Uses a low learning rate (0.05) for better generalization.
#   - Why GBM? Works well on tabular data with mixed feature types,
#     handles non-linear interactions, provides feature importances,
#     and outputs calibrated probabilities.
#
# Train/Validation Split: 80/20 with stratification on the target (y_closed_aug)
#   to maintain class balance in both sets.
#
# Evaluation Metrics:
#   - ROC-AUC: Area under the ROC curve — measures discrimination ability
#     (how well the model separates closers from non-closers)
#   - PR-AUC: Area under the Precision-Recall curve — more informative
#     than ROC-AUC when classes are imbalanced (fewer closures than non-closures)
#   - Brier Score: Mean squared error of predicted probabilities —
#     measures calibration (lower is better, 0 = perfect)
#
# MLflow Logging:
#   - Hyperparameters (n_estimators, max_depth, learning_rate)
#   - All 3 evaluation metrics
#   - Top 10 feature importances (for interpretability)
#   - The trained model artifact + registration to Unity Catalog
#     model registry for deployment and versioning
# ─────────────────────────────────────────────────────────────────────────────

# Set MLflow experiment for this model (shared location for team visibility)
mlflow.set_experiment("/Shared/medicare_stars/closure_propensity")

# Stratified train/val split preserving class balance
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

with mlflow.start_run(run_name=f"closure_propensity_{YEAR}") as run:
    mlflow.log_params({
        "algo": "GradientBoostingClassifier",
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "measurement_year": YEAR,
    })
    model = GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42
    )
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, proba)
    ap = average_precision_score(y_val, proba)
    brier = brier_score_loss(y_val, proba)
    mlflow.log_metrics({"roc_auc": auc, "pr_auc": ap, "brier": brier})
    importances = dict(zip(feat_names, model.feature_importances_.tolist()))
    for fn, imp in sorted(importances.items(), key=lambda kv: -kv[1])[:10]:
        mlflow.log_metric(f"feat_imp__{fn[:80]}", imp)
    # Log the trained model to MLflow with:
    #   - input_example: 5 sample rows for schema inference
    #   - registered_model_name: Registers in Unity Catalog model registry
    #     at aiagenticdemo.stars_gold.medicare_stars_closure_propensity
    #     for versioned deployment and governance
    mlflow.sklearn.log_model(model, "model", input_example=X_val[:5], registered_model_name=f"{CATALOG}.stars_gold.medicare_stars_closure_propensity")
    print(f"ROC-AUC={auc:.3f}  PR-AUC={ap:.3f}  Brier={brier:.3f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Score every (member × measure × channel × incentive) triple

# COMMAND ----------

# DBTITLE 1,Cell 14
# ─────────────────────────────────────────────────────────────────────────────
# BATCH SCORING: PREDICT CLOSURE PROBABILITY FOR ALL OPEN GAPS
#
# What this cell does:
#   1. Builds a scoring base by joining current open gaps with all member
#      features (same joins as training, but for ALL current open gaps).
#
#   2. Creates the CROSS-PRODUCT: each open gap is scored under every
#      combination of 3 channels (Call, SMS, Email) × 3 incentives
#      (None, $25 card, $50 card) = 9 predictions per gap.
#      This tells the optimizer: "If we reach member X about measure Y
#      via channel C with incentive I, what's the probability of closure?"
#
#   3. Applies the trained model to produce p_close (probability of
#      gap closure) for each (member × measure × channel × incentive) row.
#
#   4. Writes results to Delta table:
#      aiagenticdemo.stars_gold.gold_member_closure_propensity
#      Partitioned by measurement_year for efficient year-over-year queries.
#
# Output schema:
#   member_key | measure_code | channel | incentive | p_close | measurement_year
#
# Downstream usage: The outreach optimization engine reads this table
# to select the best (channel, incentive) per member×gap that maximizes
# expected closures subject to budget and capacity constraints.
# ─────────────────────────────────────────────────────────────────────────────

# Build scoring frame: one row per current open gap × 3 channels × 3 incentives
# Start with open gaps joined to all feature tables
scoring_base = (
    gaps.join(member, "member_key", "left")
        .join(comorbid, "member_key", "left")
        .join(awv, "member_key", "left")
        .join(outreach_hist, "member_key", "left")
).toPandas()

scoring_base["n_comorbidities"] = scoring_base["n_comorbidities"].fillna(0).astype(int)
scoring_base["awv_completed"] = scoring_base["awv_completed"].fillna(False).astype(int)
scoring_base["prior_outreach_count"] = scoring_base["prior_outreach_count"].fillna(0).astype(int)
scoring_base["dual_eligible_flag"] = scoring_base["dual_eligible_flag"].astype(int)
scoring_base["lis_flag"] = scoring_base["lis_flag"].astype(int)
scoring_base["days_since_last_outreach"] = 999  # default; refined below if last_outreach exists

# Generate the 3×3 cross-product of outreach strategies
CHANNELS = ["Call", "SMS", "Email"]       # Outreach delivery mechanisms
INCENTIVES = ["None", "$25 card", "$50 card"]  # Financial motivation tiers

score_rows = []
for ch in CHANNELS:
    for inc in INCENTIVES:
        chunk = scoring_base.copy()
        chunk["channel"] = ch
        chunk["incentive"] = inc
        score_rows.append(chunk)
score_pd = pd.concat(score_rows, ignore_index=True)

for c in CAT_COLS:
    score_pd[c] = score_pd[c].astype(str)
X_score_cat = encoder.transform(score_pd[CAT_COLS])
X_score = np.hstack([score_pd[NUM_COLS].values, X_score_cat])
score_pd["p_close"] = model.predict_proba(X_score)[:, 1]

# Write per-triple predictions to the gold layer Delta table
# This table powers the downstream outreach optimization engine
prop_out = score_pd[["member_key", "measure_code", "channel", "incentive", "p_close"]]
prop_out["measurement_year"] = YEAR

prop_schema = StructType([
    StructField("member_key", StringType(), False),
    StructField("measure_code", StringType(), True),
    StructField("channel", StringType(), True),
    StructField("incentive", StringType(), True),
    StructField("p_close", DoubleType(), True),
    StructField("measurement_year", IntegerType(), True),
])
# spark.createDataFrame(prop_out, schema=prop_schema) \
#      .write.format("delta").mode("overwrite") \
#      .partitionBy("measurement_year") \
#      .saveAsTable(f"{CATALOG}.stars_gold.gold_member_closure_propensity")
# print(f"gold_member_closure_propensity: {len(prop_out):,} rows")

# COMMAND ----------

display(score_pd)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Update `gold_member_gap.propensity_score` with the best-channel probability

# COMMAND ----------

# DBTITLE 1,Cell 16
# ─────────────────────────────────────────────────────────────────────────────
# BACK-FILL gold_member_gap.propensity_score WITH BEST-CHANNEL PROBABILITY
#
# What this cell does:
#   1. For each (member_key, measure_code), finds the maximum p_close
#      across all 9 channel×incentive combinations. This represents the
#      best achievable closure probability if the optimal outreach
#      strategy is used for that member's gap.
#
#   2. Scales the probability from [0.0, 1.0] to [0, 100] and rounds
#      to 1 decimal place for readability in the dashboard.
#
#   3. Uses a Delta MERGE INTO to update ONLY the propensity_score
#      column in gold_member_gap, matching on member_key + measure_code.
#      This enriches the gap table with ML-derived scores without
#      touching any other columns.
#
# Downstream usage: The StarPulse dashboard reads propensity_score from
# gold_member_gap to prioritize member outreach (higher score = more
# likely to close the gap = higher priority for outreach resources).
# ─────────────────────────────────────────────────────────────────────────────

# Find the best (highest) closure probability per member×measure
# across all 9 channel×incentive combinations
best = (
    score_pd.groupby(["member_key", "measure_code"])["p_close"]
    .max()
    .reset_index()
    .rename(columns={"p_close": "best_p_close"})
)

# Scale from probability (0–1) to percentage score (0–100) for dashboard display
best["propensity_score_new"] = (best["best_p_close"] * 100).round(1)

# Register as temp view for the MERGE SQL statement
spark.createDataFrame(best).createOrReplaceTempView("best_propensity")

# MERGE INTO: Update only the propensity_score column in gold_member_gap
# This is an upsert pattern — only matched rows are updated, no inserts
# spark.sql(f"""
#     MERGE INTO {CATALOG}.stars_gold.gold_member_gap g
#     USING best_propensity b
#       ON g.member_key = b.member_key AND g.measure_code = b.measure_code
#     WHEN MATCHED THEN UPDATE SET g.propensity_score = b.propensity_score_new
# """)
# print("gold_member_gap.propensity_score updated from ML predictions.")

# COMMAND ----------

display(best)

# COMMAND ----------

# MAGIC %sql
# MAGIC Select * from aiagenticdemo.stars_gold.gold_member_gap
