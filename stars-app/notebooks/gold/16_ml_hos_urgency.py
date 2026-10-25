# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer: ML  Urgency Score
# MAGIC
# MAGIC Trains a RandomForestRegressor that predicts a 15-98 urgency score for
# MAGIC fall-risk members from the seven factors documented in the StarPulse UI:
# MAGIC fall_history_severity · awv_status · age · comorbidities · mock_survey ·
# MAGIC time_since_visit · homebound (weights 25/20/15/15/10/10/5).
# MAGIC
# MAGIC Overwrites `gold_hos_members.urgency_score` for the current measurement year
# MAGIC with model predictions. The notebook 14 must run first (it produces the row
# MAGIC set; this notebook only replaces one column).

# COMMAND ----------

# DBTITLE 1,Cell 2
# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
#
# Parameters:
#   - catalog: Unity Catalog name where all bronze/silver/gold tables reside.
#              Parameterized via Databricks widget for portability across
#              dev/staging/prod environments.
#   - YEAR:    The CMS measurement year. All HOS gap data, member rosters,
#              and scoring are scoped to this year. HOS measures are evaluated
#              annually per CMS Star Ratings methodology.
# ═══════════════════════════════════════════════════════════════════════════════
dbutils.widgets.text("catalog", "aiagenticdemo")
CATALOG = dbutils.widgets.get("catalog")
YEAR = 2025

# COMMAND ----------

# DBTITLE 1,Install dependencies
# Install MLflow with Databricks extras (includes azure-storage-blob,
# azure-core, etc.) required for registering models to Unity Catalog
# on Azure-backed workspaces.
%pip install "mlflow[databricks]" -q

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Cell 5
# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS & SPARK SESSION
#
# Libraries used:
#   - PySpark (SparkSession, functions, types): Read gold/silver Delta tables,
#     perform aggregations (fall history from claims), and write predictions
#     back via MERGE INTO.
#   - pandas / numpy: In-memory feature engineering and ML training
#     (sklearn requires numpy arrays or pandas DataFrames).
#   - mlflow / mlflow.sklearn: Experiment tracking — logs hyperparameters,
#     evaluation metrics (MAE, RMSE), feature importances, and the trained
#     model artifact to Unity Catalog model registry.
#   - RandomForestRegressor (sklearn): The chosen model — an ensemble of
#     200 decision trees that vote on the urgency score. Chosen for:
#       • Handles non-linear interactions between clinical factors
#       • Robust to outliers and missing feature values
#       • Provides built-in feature importance rankings
#       • Regression output naturally bounded by training data range (15–98)
#   - train_test_split: 80/20 split for model validation.
#   - mean_absolute_error, mean_squared_error: Regression evaluation metrics.
# ═══════════════════════════════════════════════════════════════════════════════
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import DoubleType, IntegerType
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Pull current member roster and member-level features

# COMMAND ----------

# DBTITLE 1,Cell 7
# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
#
# This cell loads the HOS member roster from gold_hos_members (produced by
# notebook ) and engineers 7 features that map to the urgency
# score factors documented in the StarPulse UI.
#
# FEATURES CREATED:
#
# 1. comorbidities_count (numeric, 0–4+)
#    Source: gold_hos_members.comorbidities (comma-separated condition list)
#    Logic: Count of distinct comorbid conditions. Higher count = more
#    complex patient = higher fall risk.
#
# 2. survey_score (numeric, 0–2)
#    Source: gold_hos_members.mock_survey_response
#    Encoding: "Yes"=0 (responded positively, lower risk),
#              "No response"=1 (unknown engagement),
#              "No"=2 (negative response, higher risk)
#    Captures member engagement with health surveys.
#
# 3. months_since_visit (numeric, 0–6)
#    Source: gold_hos_members.last_provider_visit (e.g., "Apr 15")
#    Logic: Months elapsed since last provider visit relative to May 2025.
#    Longer gaps = less clinical monitoring = higher urgency.
#
# 4. fall_history_severity (numeric, 0–4+)
#    Source: silver_claim (ICD-10 codes W00–W19 = fall-related injuries)
#    Logic: Count of fall-related claims in last 24 months for each member.
#    Direct predictor of future fall risk (strongest signal, weight=25).
#
# 5. awv_completed (binary, 0/1)
#    Source: gold_hos_members.awv_completed
#    Whether member completed an Annual Wellness Visit. AWV includes
#    fall risk screening, so completion = better preventive care.
#
# 6. homebound (binary, 0/1)
#    Source: gold_hos_members.homebound
#    Whether member is homebound. Homebound members have higher fall
#    risk due to limited mobility and isolation.
#
# 7. age (numeric, 65–92+)
#    Source: gold_hos_members.age
#    Older members have higher fall risk due to declining balance,
#    muscle weakness, and medication effects.
# ═══════════════════════════════════════════════════════════════════════════════

# Load HOS member roster for the current measurement year
hos_members = spark.table(f"{CATALOG}.stars_gold.gold_hos_members").filter(
    F.col("measurement_year") == YEAR
).toPandas()
print(f"HOS members: {len(hos_members):,}")

# FEATURE 1: Comorbidity count — parse comma-separated condition list
# e.g., "Diabetes,CHF,COPD" → 3
hos_members["comorbidities_count"] = (
    hos_members["comorbidities"].fillna("").apply(lambda s: 0 if not s else len([x for x in s.split(",") if x]))
)

# FEATURE 2: Survey engagement score (ordinal encoding)
# "Yes"=0 (engaged), "No response"=1 (unknown), "No"=2 (disengaged)
SURVEY_MAP = {"Yes": 0, "No response": 1, "No": 2}
hos_members["survey_score"] = hos_members["mock_survey_response"].map(SURVEY_MAP).fillna(1).astype(int)

# FEATURE 3: Months since last provider visit
# Parses strings like "Apr 15" to month number, calculates distance from
# reference month (May 2025). Default = 6 months for missing/unparseable values.
# Higher value = longer gap = higher fall risk due to less clinical oversight.
MONTH_MAP = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
def _months_since_visit(s):
    if not isinstance(s, str) or " " not in s:
        return 6  # Default: assume 6 months if data missing
    mo = MONTH_MAP.get(s.split()[0], 5)
    return max(0, 5 - mo)  # Distance from May (month 5)
hos_members["months_since_visit"] = hos_members["last_provider_visit"].apply(_months_since_visit)

# FEATURE 4: Fall history severity
# Counts fall-related claims (ICD-10 W00–W19: slipping, tripping, falling)
# from silver_claim in last 24 months. This is the STRONGEST predictor
# of future falls (weight=25 in the published scoring schema).
member_ids = hos_members["member_id"].dropna().unique().tolist()
if member_ids:
    claims = spark.table(f"{CATALOG}.stars_silver.silver_claim").filter(
        F.col("member_id").isin(member_ids) &
        F.col("icd10_primary").rlike("^W(0[0-9]|1[0-9])")
    ).groupBy("member_id").agg(F.count("*").alias("fall_history_severity")).toPandas()
    hos_members = hos_members.merge(claims, on="member_id", how="left")
else:
    hos_members["fall_history_severity"] = 0
hos_members["fall_history_severity"] = hos_members["fall_history_severity"].fillna(0).astype(int)

# FEATURES 5, 6, 7: Binary flags and age
# awv_completed: 1 if Annual Wellness Visit done (weight=20 in scoring)
# homebound: 1 if member is homebound (weight=5 in scoring)
# age: Member age, default 75 for missing (weight=15 in scoring)
hos_members["awv_completed"] = hos_members["awv_completed"].fillna(False).astype(int)
hos_members["homebound"] = hos_members["homebound"].fillna(False).astype(int)
hos_members["age"] = hos_members["age"].fillna(75).astype(int)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Build factor-weighted training target (recovers the published schema)

# COMMAND ----------

display(hos_members)

# COMMAND ----------

# DBTITLE 1,Cell 9
# ═══════════════════════════════════════════════════════════════════════════════
# BUILD TRAINING TARGET (FACTOR-WEIGHTED URGENCY SCORE)
#
# Since there is no historical "true" urgency outcome label, this cell
# constructs a synthetic training target using a DOMAIN-EXPERT WEIGHTED
# FORMULA documented in the StarPulse UI. This is a common approach when
# the scoring rubric is well-defined but individual labels don't exist.
#
# PUBLISHED WEIGHTS (sum to 100, define urgency score 15–98):
#   │ Factor                  │ Weight │ Rationale                       │
#   ├─────────────────────────┼────────┼─────────────────────────────────┤
#   │ fall_history_severity   │   25   │ Best predictor of future falls  │
#   │ awv_status (inverted)   │   20   │ No AWV = no fall screening done │
#   │ age                     │   15   │ Older = higher physical risk     │
#   │ comorbidities           │   15   │ More conditions = more fragile   │
#   │ mock_survey             │   10   │ Non-response = disengagement     │
#   │ time_since_visit        │   10   │ Longer gap = less monitoring     │
#   │ homebound               │    5   │ Limited mobility                 │
#
# NORMALIZATION: Each factor is scaled to [0, 1] before applying weights.
# NOISE: Gaussian noise (std=4) is added to prevent the ML model from
#        learning an exact linear formula, forcing it to discover the
#        non-linear interactions between features.
# CLIPPING: Final target clipped to [15, 98] per the published score range.
#
# WHY TRAIN AN ML MODEL ON A FORMULA?
#   The model learns non-linear interactions (e.g., high age + high falls
#   may be super-additive) and can generalize better to new members than
#   the rigid linear formula. It also provides feature importances for
#   clinical explainability.
# ═══════════════════════════════════════════════════════════════════════════════

# Helper: normalize a series to [0, 1] given known min/max bounds
def _norm(s, lo, hi):
    s = s.astype(float).clip(lo, hi)
    return (s - lo) / (hi - lo) if hi > lo else s * 0.0

# Normalize each factor to [0, 1]
age_score = _norm(hos_members["age"], 65, 92)           # 65–92 → 0–1
fall_score = _norm(hos_members["fall_history_severity"], 0, 4)  # 0–4 falls
comorbid_score = _norm(hos_members["comorbidities_count"], 0, 4) # 0–4 conditions
visit_score = _norm(hos_members["months_since_visit"], 0, 6)    # 0–6 months
survey_score = hos_members["survey_score"] / 2.0  # 0–2 → 0–1

# Apply published weights (sum to 100) to produce urgency target score
# Note: awv_completed is INVERTED (1 - awv) because NOT having an AWV
# increases urgency (lack of fall risk screening).
target = (
    25 * fall_score                          # Strongest signal
  + 20 * (1 - hos_members["awv_completed"])  # No AWV = high urgency
  + 15 * age_score                           # Older = higher risk
  + 15 * comorbid_score                      # More conditions = fragile
  + 10 * survey_score                        # Non-response = disengaged
  + 10 * visit_score                         # Long gap = unmonitored
  +  5 * hos_members["homebound"]            # Mobility-limited
)

# Add Gaussian noise to break exact linearity (forces model to learn interactions)
rng = np.random.RandomState(42)
target = (target + rng.normal(0, 4, len(target))).clip(15, 98)
hos_members["urgency_target"] = target

# Define the 7 features used by the RandomForest model
FEATURES = [
    "fall_history_severity",  # Count of W00–W19 claims (weight 25)
    "awv_completed",          # Binary: Annual Wellness Visit done (weight 20)
    "age",                    # Member age in years (weight 15)
    "comorbidities_count",    # Count of comorbid conditions (weight 15)
    "survey_score",           # Ordinal survey engagement 0–2 (weight 10)
    "months_since_visit",     # Months since last provider visit (weight 10)
    "homebound",              # Binary: homebound status (weight 5)
]
X = hos_members[FEATURES].values  # Feature matrix (numpy array)
y = hos_members["urgency_target"].values  # Regression target (15–98)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Train + log

# COMMAND ----------

# DBTITLE 1,Cell 11
# ═══════════════════════════════════════════════════════════════════════════════
# MODEL TRAINING & MLFLOW EXPERIMENT TRACKING
#
# MODEL: sklearn.ensemble.RandomForestRegressor
#   - 200 decision trees (n_estimators=200)
#   - Max depth of 6 per tree (prevents overfitting to noise)
#   - Parallel training (n_jobs=-1, uses all available CPU cores)
#   - Random state fixed at 42 for reproducibility
#
# WHY RANDOM FOREST FOR THIS TASK?
#   • Regression output: naturally produces continuous urgency scores
#   • Ensemble averaging: reduces variance from noisy training targets
#   • Non-linear: captures interactions (e.g., age × falls × comorbidities)
#   • Feature importance: built-in Gini importance for clinical interpretability
#   • Robust: tolerant of outliers and doesn't require feature scaling
#
# TRAIN/VALIDATION SPLIT: 80/20 random split (no stratification needed
#   for regression; random_state=42 for reproducibility)
#
# EVALUATION METRICS:
#   - MAE (Mean Absolute Error): Average absolute prediction error in
#     urgency score points. Interpretable: "on average, predictions are
#     off by X points on the 15–98 scale."
#   - RMSE (Root Mean Squared Error): Penalizes large errors more than MAE.
#     Lower RMSE = fewer catastrophically wrong predictions.
#
# MLFLOW LOGGING:
#   - Hyperparameters: algorithm, n_estimators, max_depth, measurement_year
#   - Metrics: MAE, RMSE
#   - Feature importances: logged per-feature (feat_imp__<feature_name>)
#     for tracking importance drift across model versions
#   - Model artifact: registered to Unity Catalog at
#     aiagenticdemo.stars_gold.medicare_stars_hos_urgency
#     with input_example for schema inference
# ═══════════════════════════════════════════════════════════════════════════════

# Ensure the shared experiment directory exists in the workspace
from databricks.sdk import WorkspaceClient
WorkspaceClient().workspace.mkdirs("/Shared/medicare_stars")

# Set MLflow experiment (shared path for team access)
mlflow.set_experiment("/Shared/medicare_stars/hos_urgency")

# 80/20 train/validation split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run(run_name=f"hos_urgency_{YEAR}") as run:
    # Log hyperparameters for reproducibility
    mlflow.log_params({
        "algo": "RandomForestRegressor",
        "n_estimators": 200,
        "max_depth": 6,
        "measurement_year": YEAR,
    })

    # Train the RandomForest regressor
    model = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Evaluate on validation set
    pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, pred)
    rmse = float(np.sqrt(mean_squared_error(y_val, pred)))
    mlflow.log_metrics({"mae": mae, "rmse": rmse})

    # Log per-feature importance for interpretability tracking
    for fn, imp in zip(FEATURES, model.feature_importances_):
        mlflow.log_metric(f"feat_imp__{fn}", float(imp))

    # Register model to Unity Catalog with input_example for signature inference
    mlflow.sklearn.log_model(model, "model", input_example=X_val[:5], registered_model_name=f"{CATALOG}.stars_gold.medicare_stars_hos_urgency")
    print(f"MAE={mae:.2f}  RMSE={rmse:.2f}")
    print("Feature importances:", dict(zip(FEATURES, model.feature_importances_.round(3).tolist())))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Score every HOS member and overwrite urgency_score

# COMMAND ----------

# DBTITLE 1,Cell 13
# ═══════════════════════════════════════════════════════════════════════════════
# BATCH SCORING & GOLD TABLE UPDATE
#
# What this cell does:
#   1. Scores ALL HOS members using the trained RandomForest model to
#      produce urgency scores (integer, 15–98 range).
#
#   2. Derives two business-rule columns from the urgency score:
#      - risk_level: Tier assignment for clinical prioritization
#          • "High"   (score >= 70): Immediate intervention needed
#          • "Medium" (score 40–69): Monitor closely, preventive outreach
#          • "Low"    (score < 40):  Standard care pathway
#      - handler: Routing assignment for care teams
#          • "Care mgmt" (score >= 55): Assign to care management team
#          • "Outreach"  (score < 55):  Standard outreach coordinator
#
#   3. Uses Delta MERGE INTO to update gold_hos_members with:
#      - urgency_score: ML-predicted score (replaces the rule-based default)
#      - risk_level: Derived tier
#      - handler: Routing assignment
#      Only matched rows are updated (no inserts).
#
# Downstream usage: The StarPulse HOS Measures page reads urgency_score,
# risk_level, and handler from gold_hos_members to display the fall-risk
# member registry with prioritized intervention lists.
# ═══════════════════════════════════════════════════════════════════════════════

# Score every HOS member with the trained model, clip to valid range [15, 98]
preds = model.predict(hos_members[FEATURES].values).clip(15, 98).round().astype(int)

# Assign urgency score and derive business-rule columns
hos_members["urgency_score_new"] = preds
hos_members["risk_level_new"] = np.where(preds >= 70, "High", np.where(preds >= 40, "Medium", "Low"))
hos_members["handler_new"] = np.where(preds >= 55, "Care mgmt", "Outreach")

# Prepare update DataFrame and register as temp view for SQL MERGE
update_df = hos_members[["member_key", "urgency_score_new", "risk_level_new", "handler_new"]]
spark.createDataFrame(update_df).createOrReplaceTempView("hos_urgency_update")

# MERGE INTO: Update only urgency_score, risk_level, and handler columns
# in gold_hos_members. Matches on member_key (no inserts, only updates).
# spark.sql(f"""
#     MERGE INTO {CATALOG}.stars_gold.gold_hos_members h
#     USING hos_urgency_update u
#       ON h.member_key = u.member_key
#     WHEN MATCHED THEN UPDATE SET
#         h.urgency_score = u.urgency_score_new,
#         h.risk_level    = u.risk_level_new,
#         h.handler       = u.handler_new
# """)
# print(f"gold_hos_members.urgency_score updated for {len(update_df):,} rows.")

# COMMAND ----------

display(update_df)

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from aiagenticdemo.stars_gold.gold_hos_members
