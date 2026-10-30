# Run this notebook in Databricks to get actual table schemas
# Copy the output and share with Claude

tables = [
    "aiagenticdemo.stars_gold.gold_star_rating_summary",
    "aiagenticdemo.stars_gold.gold_measure_scorecard",
    "aiagenticdemo.stars_gold.gold_member_gap",
    "aiagenticdemo.stars_gold.gold_cahps_overview",
    "aiagenticdemo.stars_gold.gold_alert_priority",
    "aiagenticdemo.stars_silver.silver_plan",
    "aiagenticdemo.stars_silver.silver_member",
    "aiagenticdemo.stars_silver.silver_measure",
]

for t in tables:
    print(f"\n{'='*60}")
    print(f"TABLE: {t}")
    print(f"{'='*60}")
    try:
        df = spark.sql(f"DESCRIBE TABLE {t}")
        df.show(100, truncate=False)
    except Exception as e:
        print(f"ERROR: {e}")

# Also show sample row counts
print(f"\n{'='*60}")
print("ROW COUNTS")
print(f"{'='*60}")
for t in tables:
    try:
        count = spark.sql(f"SELECT COUNT(*) as cnt FROM {t}").collect()[0]["cnt"]
        print(f"{t}: {count} rows")
    except Exception as e:
        print(f"{t}: ERROR - {e}")
