# Databricks notebook source
# MAGIC %md
# MAGIC # SCD Type 1 & Type 2 — Hands-On with a Yelp-style dataset
# MAGIC
# MAGIC Databricks Free Edition has no built-in Yelp Parquet, so **Step 1 creates a Yelp-style
# MAGIC `business` Parquet file** for you. Then we implement and **validate SCD1 and SCD2** with Delta
# MAGIC `MERGE`, covering every scenario: **new record, changed attribute, unchanged, (and delete)**.
# MAGIC
# MAGIC Run cell by cell. Works on Free Edition (serverless + Unity Catalog + Delta).
# MAGIC
# MAGIC *(To use the REAL Yelp data instead: download the Yelp Open Dataset JSON from yelp.com/dataset,
# MAGIC upload `yelp_academic_dataset_business.json` to a Volume, `spark.read.json(...)`, then `.write.parquet(...)`.)*

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1 — Create a Yelp-style `business` Parquet file (in a UC Volume)

# COMMAND ----------
from pyspark.sql import functions as F
from delta.tables import DeltaTable

catalog = spark.catalog.currentCatalog()
spark.sql("CREATE SCHEMA IF NOT EXISTS yelp")
spark.sql("CREATE VOLUME IF NOT EXISTS yelp.files")      # file storage on Free Edition
VOL = f"/Volumes/{catalog}/yelp/files"
print("catalog:", catalog, "| volume path:", VOL)

# a small, Yelp-like business dataset (attributes that will CHANGE over time: stars, city, review_count)
business = [
    # business_id, name,               city,        state, category,        stars, review_count
    ("B001","Sunrise Diner",           "Phoenix",   "AZ",  "Restaurants",   4.0, 120),
    ("B002","Blue Bottle Coffee",      "Austin",    "TX",  "Coffee",        4.5, 300),
    ("B003","Downtown Gym",            "Denver",    "CO",  "Fitness",        3.5,  80),
    ("B004","Pizza Palace",            "Chicago",   "IL",  "Restaurants",   4.2, 210),
    ("B005","Green Leaf Spa",          "Seattle",   "WA",  "Beauty",        4.8, 150),
]
biz_df = spark.createDataFrame(business,
    ["business_id","name","city","state","category","stars","review_count"])

biz_df.write.mode("overwrite").parquet(f"{VOL}/business")     # <-- your Yelp-style Parquet file
print("Wrote Parquet to", f"{VOL}/business")
display(dbutils.fs.ls(f"{VOL}/business"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2 — Load the Parquet (this is your initial dimension load)

# COMMAND ----------
biz = spark.read.parquet(f"{VOL}/business")
biz.printSchema()
display(biz)

# COMMAND ----------
# MAGIC %md
# MAGIC # ============ SCD TYPE 1 (overwrite — NO history) ============
# MAGIC ## Step 3 — Build the SCD1 dimension table (Delta)

# COMMAND ----------
(biz.write.format("delta").mode("overwrite").saveAsTable("yelp.dim_business_scd1"))
display(spark.table("yelp.dim_business_scd1").orderBy("business_id"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4 — A change batch (the "next load")
# MAGIC Scenarios in one batch:
# MAGIC - **B002** changed: `stars` 4.5 → 4.7, `review_count` 300 → 350  (UPDATE)
# MAGIC - **B003** changed city: Denver → Boulder                        (UPDATE)
# MAGIC - **B006** is brand new                                          (INSERT)
# MAGIC - **B001** unchanged                                             (NO-OP)

# COMMAND ----------
changes = spark.createDataFrame([
    ("B001","Sunrise Diner",      "Phoenix", "AZ","Restaurants", 4.0, 120),   # unchanged
    ("B002","Blue Bottle Coffee", "Austin",  "TX","Coffee",      4.7, 350),   # changed
    ("B003","Downtown Gym",       "Boulder", "CO","Fitness",     3.5,  95),   # changed city + reviews
    ("B006","Taco Fiesta",        "Dallas",  "TX","Restaurants", 4.1,  60),   # NEW
],["business_id","name","city","state","category","stars","review_count"])
display(changes)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 5 — SCD1 MERGE (upsert overwrites in place, no history) + validation

# COMMAND ----------
tgt = DeltaTable.forName(spark, "yelp.dim_business_scd1")
(tgt.alias("t").merge(changes.alias("s"), "t.business_id = s.business_id")
   .whenMatchedUpdateAll()        # overwrite existing attributes
   .whenNotMatchedInsertAll()     # insert new business
   .execute())

print("After SCD1 merge — one row per business, values overwritten, NO history:")
display(spark.table("yelp.dim_business_scd1").orderBy("business_id"))

# COMMAND ----------
# MAGIC %md
# MAGIC ### Validate SCD1
# MAGIC - exactly **one row per business** (no duplicates),
# MAGIC - B002 now shows 4.7/350 and B003 shows Boulder (**old values are gone**),
# MAGIC - B006 exists; total = 6 rows.

# COMMAND ----------
display(spark.sql("""
  SELECT COUNT(*) AS total_rows,
         COUNT(DISTINCT business_id) AS distinct_biz     -- should be equal (one row each)
  FROM yelp.dim_business_scd1"""))
display(spark.sql("SELECT * FROM yelp.dim_business_scd1 WHERE business_id IN ('B002','B003','B006')"))

# COMMAND ----------
# MAGIC %md
# MAGIC # ============ SCD TYPE 2 (keep FULL history) ============
# MAGIC ## Step 6 — Build the SCD2 dimension with history columns
# MAGIC Add `start_date`, `end_date`, `is_current` (and a surrogate key). Initial load effective 2026-01-01.

# COMMAND ----------
scd2_init = (biz
    .withColumn("start_date", F.lit("2026-01-01").cast("date"))
    .withColumn("end_date",   F.lit(None).cast("date"))
    .withColumn("is_current", F.lit(True))
    .withColumn("business_sk", F.sha2(F.concat_ws("||", F.col("business_id"), F.lit("2026-01-01")), 256)))
(scd2_init.write.format("delta").mode("overwrite").saveAsTable("yelp.dim_business_scd2"))
display(spark.table("yelp.dim_business_scd2").orderBy("business_id"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 7 — Same change batch, effective 2026-07-01
# MAGIC We'll treat a row as *changed* if `stars`, `city`, or `review_count` differs from the current version.

# COMMAND ----------
EFF = "2026-07-01"
changes2 = changes.withColumn("effective_date", F.lit(EFF).cast("date"))
display(changes2)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 8 — SCD2 MERGE: expire the old version + insert the new one
# MAGIC Uses the classic **mergeKey** pattern so one MERGE both closes the old row and inserts the new.

# COMMAND ----------
current = spark.table("yelp.dim_business_scd2").filter("is_current = true")

# rows whose tracked attributes actually changed vs the current version
changed = (changes2.alias("s")
    .join(current.alias("c"), "business_id")
    .where("s.stars <> c.stars OR s.city <> c.city OR s.review_count <> c.review_count")
    .select("s.*"))

# staged updates:
#  - mergeKey = NULL  -> will NOT match -> INSERT the new version (for changed rows)
#  - mergeKey = id    -> WILL match current row -> used to EXPIRE it
staged = (changed.withColumn("mergeKey", F.lit(None).cast("string"))
          .unionByName(changes2.withColumn("mergeKey", F.col("business_id"))))

tgt2 = DeltaTable.forName(spark, "yelp.dim_business_scd2")
(tgt2.alias("t").merge(staged.alias("s"), "t.business_id = s.mergeKey AND t.is_current = true")
   # existing row that changed -> expire it
   .whenMatchedUpdate(
       condition="t.stars <> s.stars OR t.city <> s.city OR t.review_count <> s.review_count",
       set={"is_current": "false", "end_date": "s.effective_date"})
   # new business OR the new version of a changed business -> insert as current
   .whenNotMatchedInsert(values={
       "business_id":"s.business_id","name":"s.name","city":"s.city","state":"s.state",
       "category":"s.category","stars":"s.stars","review_count":"s.review_count",
       "start_date":"s.effective_date","end_date":"NULL","is_current":"true",
       "business_sk":"sha2(concat_ws('||', s.business_id, s.effective_date), 256)"})
   .execute())

print("After SCD2 merge:")
display(spark.table("yelp.dim_business_scd2").orderBy("business_id","start_date"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 9 — Validate SCD2 (this is the whole point)

# COMMAND ----------
# MAGIC %md
# MAGIC **9a. History for a changed business (B002) — two rows: old expired + new current**

# COMMAND ----------
display(spark.sql("""
  SELECT business_id, city, stars, review_count, start_date, end_date, is_current
  FROM yelp.dim_business_scd2 WHERE business_id='B002' ORDER BY start_date"""))

# COMMAND ----------
# MAGIC %md
# MAGIC **9b. Current view — exactly one current row per business**

# COMMAND ----------
display(spark.sql("""
  SELECT business_id, COUNT(*) current_rows
  FROM yelp.dim_business_scd2 WHERE is_current = true
  GROUP BY business_id ORDER BY business_id"""))   # every count must be 1

# COMMAND ----------
# MAGIC %md
# MAGIC **9c. Point-in-time query — "what did B003 look like on 2026-03-01?" (should be Denver)**

# COMMAND ----------
display(spark.sql("""
  SELECT business_id, city, stars, start_date, end_date
  FROM yelp.dim_business_scd2
  WHERE business_id='B003'
    AND start_date <= DATE'2026-03-01'
    AND (end_date > DATE'2026-03-01' OR end_date IS NULL)"""))

# COMMAND ----------
# MAGIC %md
# MAGIC **9d. Integrity checks — no overlapping current rows; changed businesses have 2 versions**

# COMMAND ----------
display(spark.sql("""
  SELECT
    (SELECT COUNT(*) FROM (SELECT business_id FROM yelp.dim_business_scd2
        WHERE is_current=true GROUP BY business_id HAVING COUNT(*)>1)) AS bad_multiple_current,
    (SELECT COUNT(*) FROM yelp.dim_business_scd2 WHERE business_id='B002') AS b002_versions,
    (SELECT COUNT(*) FROM yelp.dim_business_scd2 WHERE business_id='B001') AS b001_versions   -- unchanged -> 1
"""))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 10 — All scenarios: SCD1 vs SCD2 side by side
# MAGIC
# MAGIC | Source event | SCD Type 1 | SCD Type 2 |
# MAGIC |---|---|---|
# MAGIC | **New record** (B006) | INSERT new row | INSERT new row, `is_current=true` |
# MAGIC | **Changed attribute** (B002 stars, B003 city) | UPDATE in place (old value lost) | EXPIRE old row (`end_date`, `is_current=false`) + INSERT new version |
# MAGIC | **Unchanged** (B001) | no-op | no-op (still 1 version) |
# MAGIC | **Deleted at source** | delete or flag | keep history; set `is_current=false`/`end_date` (soft delete) |
# MAGIC
# MAGIC **Validation recap**
# MAGIC - **SCD1:** `COUNT(*) == COUNT(DISTINCT business_id)` (one row each); latest values only; no history.
# MAGIC - **SCD2:** each changed business has ≥2 rows; exactly one `is_current=true` per business;
# MAGIC   `end_date` set on expired rows; point-in-time query returns the right version.
# MAGIC
# MAGIC **Bonus scenario — handle a source DELETE for SCD2:**
# MAGIC ```python
# MAGIC # mark deleted businesses as no longer current (soft delete, history preserved)
# MAGIC deleted_ids = ["B004"]
# MAGIC spark.sql(f"""
# MAGIC   UPDATE yelp.dim_business_scd2
# MAGIC   SET is_current=false, end_date=DATE'2026-07-01'
# MAGIC   WHERE business_id IN ('B004') AND is_current=true""")
# MAGIC ```
