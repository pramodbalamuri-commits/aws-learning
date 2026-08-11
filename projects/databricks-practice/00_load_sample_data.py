# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Load Sample Data (one click)
# MAGIC Downloads the sample CSVs from the public repo, saves them to DBFS, and writes **Parquet**
# MAGIC to `/tmp/de/raw/`. Run this first, then open `databricks_de_practice` and start at **Step 2**.
# MAGIC
# MAGIC **How to use:** attach a cluster → **Run All**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Config — where the CSVs come from and where Parquet goes

# COMMAND ----------
BASE_URL = "https://raw.githubusercontent.com/pramodbalamuri-commits/aws-learning/main/projects/databricks-practice/sample_data"
FILES    = ["customers", "products", "orders"]
DBFS_CSV = "dbfs:/tmp/de/csv"      # where the raw CSVs land
RAW      = "/tmp/de/raw"           # where the Parquet is written (bronze)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Download the CSVs from the repo and copy into DBFS

# COMMAND ----------
import urllib.request, os
os.makedirs("/tmp/de_dl", exist_ok=True)
dbutils.fs.mkdirs(DBFS_CSV)

for name in FILES:
    local = f"/tmp/de_dl/{name}.csv"
    urllib.request.urlretrieve(f"{BASE_URL}/{name}.csv", local)          # download to driver
    dbutils.fs.cp(f"file:{local}", f"{DBFS_CSV}/{name}.csv", recurse=False)  # copy into DBFS
    print(f"loaded {name}.csv")

display(dbutils.fs.ls(DBFS_CSV))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Read the CSVs and write Parquet (your bronze/raw files)

# COMMAND ----------
dbutils.fs.rm(RAW, recurse=True)   # clean slate
for name in FILES:
    df = (spark.read.option("header", True).option("inferSchema", True)
                    .csv(f"{DBFS_CSV}/{name}.csv"))
    df.write.mode("overwrite").parquet(f"{RAW}/{name}")
    print(f"{name}: wrote {df.count()} rows to {RAW}/{name}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Verify — your Parquet files are ready

# COMMAND ----------
print("Parquet files under raw/orders:")
display(dbutils.fs.ls(f"{RAW}/orders"))

orders = spark.read.parquet(f"{RAW}/orders")
orders.printSchema()
print("orders rows:", orders.count())
display(orders.limit(10))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Done
# MAGIC Your sample **Parquet** is at `/tmp/de/raw/{customers,products,orders}`.
# MAGIC
# MAGIC Next: open **`databricks_de_practice`** and run from **Step 2** (or change its `RAW` path to
# MAGIC `/tmp/de/raw` and skip its Step 1). Continue with cleaning, star schema, Delta, MERGE, and windows.
