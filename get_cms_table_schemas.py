# Run in Databricks to get CMS table schemas used by market.py

cms_tables = [
    "aiagenticdemo.stars_gold.cms_plan_enrollment_history",
    "aiagenticdemo.stars_gold.cms_plan_star_history",
    "aiagenticdemo.stars_gold.cms_measure_star_history",
]

for t in cms_tables:
    print(f"\n{'='*60}")
    print(f"TABLE: {t}")
    print(f"{'='*60}")
    try:
        df = spark.sql(f"DESCRIBE TABLE {t}")
        df.show(100, truncate=False)
        cnt = spark.sql(f"SELECT COUNT(*) as cnt FROM {t}").collect()[0]["cnt"]
        print(f"ROW COUNT: {cnt}")
        print(f"\nSAMPLE ROW:")
        spark.sql(f"SELECT * FROM {t} LIMIT 1").show(truncate=False)
    except Exception as e:
        print(f"ERROR: {e}")
