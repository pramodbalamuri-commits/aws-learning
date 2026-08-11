# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks Data Engineering — Hands-On Practice
# MAGIC
# MAGIC Step-by-step: **generate Parquet → explore → clean (Bronze→Silver) → model (Gold star schema)
# MAGIC → Delta tables → MERGE/upsert → window functions → analytics → Delta features (time travel,
# MAGIC OPTIMIZE, Z-ORDER)**.
# MAGIC
# MAGIC **How to use:** import this file into Databricks (Workspace → Import → File), attach a cluster,
# MAGIC and run cell by cell. Works on **Databricks Community Edition (free)**. Each `# COMMAND` block is
# MAGIC one cell.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 0 — Setup: paths in DBFS

# COMMAND ----------
from pyspark.sql import functions as F, Window
from pyspark.sql.types import *

BASE   = "/tmp/de_practice"          # DBFS path
RAW    = f"{BASE}/raw"               # bronze (raw Parquet)
SILVER = f"{BASE}/silver"            # cleaned
GOLD   = f"{BASE}/gold"              # star schema (Delta)
dbutils.fs.rm(BASE, recurse=True)    # clean slate
print("Working under:", BASE)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1 — Generate sample data and WRITE PARQUET (this creates your practice files)
# MAGIC We build 3 datasets (orders/customers/products) as Spark DataFrames and save them as Parquet.
# MAGIC The orders are intentionally *messy* (duplicates, null amounts, cancelled/pending, bad refs).

# COMMAND ----------
import random
random.seed(7)
REGIONS=["West","East","South","Central"]; CATS=["Electronics","Home","Toys","Sports","Books"]

customers = [(i, f"Customer {i}", random.choice(REGIONS) if random.random()>0.05 else None) for i in range(1,201)]
products  = [(i, f"Product {i}", random.choice(CATS), round(random.uniform(5,500),2)) for i in range(1,51)]

orders=[]; oid=100000
for _ in range(10000):
    oid+=1; day=random.randint(1,40); qty=random.randint(1,5); price=round(random.uniform(5,500),2)
    status=random.choices(["completed","cancelled","pending"],weights=[78,14,8])[0]
    amount=round(qty*price,2) if random.random()>0.03 else None
    ts=f"2026-07-{day:02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00"
    orders.append((oid, random.randint(1,210), random.randint(1,50), qty, amount, status, ts))
orders += random.sample(orders, 150)   # inject duplicates

cust_df = spark.createDataFrame(customers, ["customer_id","name","region"])
prod_df = spark.createDataFrame(products, ["product_id","product_name","category","unit_price"])
ord_df  = spark.createDataFrame(orders, ["order_id","customer_id","product_id","quantity","amount","status","order_ts"])

cust_df.write.mode("overwrite").parquet(f"{RAW}/customers")
prod_df.write.mode("overwrite").parquet(f"{RAW}/products")
ord_df.write.mode("overwrite").parquet(f"{RAW}/orders")
print("Parquet written. Files:")
display(dbutils.fs.ls(f"{RAW}/orders"))   # <-- your .parquet files

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2 — Read the Parquet and explore
# MAGIC The essentials you do first with any dataset.

# COMMAND ----------
orders = spark.read.parquet(f"{RAW}/orders")
customers = spark.read.parquet(f"{RAW}/customers")
products = spark.read.parquet(f"{RAW}/products")

orders.printSchema()
print("row count:", orders.count())
display(orders.limit(10))
display(orders.groupBy("status").count())        # see the mess: completed/cancelled/pending
print("null amounts:", orders.filter(F.col("amount").isNull()).count())

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3 — Bronze → Silver: clean the data
# MAGIC Rules: keep **completed** orders with a **positive amount**, **dedupe** by order_id (latest),
# MAGIC and keep only rows with **valid** customer & product (referential integrity).

# COMMAND ----------
w = Window.partitionBy("order_id").orderBy(F.col("order_ts").desc())
silver = (orders
    .withColumn("amount", F.col("amount").cast("double"))
    .filter((F.col("status")=="completed") & (F.col("amount") > 0))
    .withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")   # dedup latest
    .join(F.broadcast(customers.select("customer_id")), "customer_id")      # valid customer
    .join(F.broadcast(products.select("product_id")), "product_id")         # valid product
    .withColumn("order_date", F.to_date("order_ts")))

print("raw:", orders.count(), " -> clean:", silver.count())
silver.write.mode("overwrite").partitionBy("order_date").parquet(f"{SILVER}/orders")
display(silver.limit(5))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4 — Gold: dimensional model (star schema)
# MAGIC fact_orders + dim_customer / dim_product / dim_date.

# COMMAND ----------
silver = spark.read.parquet(f"{SILVER}/orders")

dim_customer = customers.withColumn("region", F.coalesce("region", F.lit("Unknown")))
dim_product  = products
dim_date = (silver.select("order_date").distinct()
            .withColumn("year", F.year("order_date"))
            .withColumn("month", F.month("order_date"))
            .withColumn("day", F.dayofmonth("order_date")))
fact_orders = silver.select("order_id","customer_id","product_id","order_date","quantity","amount")

for name, df in [("dim_customer",dim_customer),("dim_product",dim_product),
                 ("dim_date",dim_date),("fact_orders",fact_orders)]:
    df.write.format("delta").mode("overwrite").save(f"{GOLD}/{name}")   # <-- Delta!
print("Gold star schema written as Delta.")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 5 — Why Delta? Register tables and query with SQL
# MAGIC Delta adds ACID, MERGE/upserts, time travel, and OPTIMIZE on top of Parquet.

# COMMAND ----------
spark.sql("CREATE DATABASE IF NOT EXISTS de_practice")
for name in ["dim_customer","dim_product","dim_date","fact_orders"]:
    spark.sql(f"CREATE TABLE IF NOT EXISTS de_practice.{name} USING DELTA LOCATION '{GOLD}/{name}'")
display(spark.sql("""
  SELECT c.region, ROUND(SUM(f.amount),2) revenue, COUNT(*) orders
  FROM de_practice.fact_orders f JOIN de_practice.dim_customer c ON c.customer_id=f.customer_id
  GROUP BY c.region ORDER BY revenue DESC"""))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 6 — MERGE (upsert) — the core incremental/CDC pattern
# MAGIC Simulate a batch of updated + new orders and MERGE them into the fact table.

# COMMAND ----------
from delta.tables import DeltaTable
updates = spark.createDataFrame([
    (100001, 1, 1, "2026-07-20", 2, 999.99),    # existing order_id -> update
    (999999, 5, 5, "2026-07-25", 1, 123.45),    # brand new order   -> insert
], ["order_id","customer_id","product_id","order_date","quantity","amount"]) \
  .withColumn("order_date", F.to_date("order_date"))

fact = DeltaTable.forPath(spark, f"{GOLD}/fact_orders")
(fact.alias("t").merge(updates.alias("s"), "t.order_id = s.order_id")
   .whenMatchedUpdateAll()
   .whenNotMatchedInsertAll()
   .execute())
display(spark.sql("SELECT * FROM de_practice.fact_orders WHERE order_id IN (100001, 999999)"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 7 — Window functions (top-N per group, running total)

# COMMAND ----------
fact = spark.read.format("delta").load(f"{GOLD}/fact_orders")
# top 3 orders per customer by amount
w1 = Window.partitionBy("customer_id").orderBy(F.col("amount").desc())
display(fact.withColumn("rn", F.row_number().over(w1)).filter("rn <= 3")
            .orderBy("customer_id","rn").limit(15))
# running total of spend per customer over time
w2 = Window.partitionBy("customer_id").orderBy("order_date") \
           .rowsBetween(Window.unboundedPreceding, Window.currentRow)
display(fact.withColumn("running_total", F.sum("amount").over(w2))
            .orderBy("customer_id","order_date").limit(15))

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 8 — Analytics (joins + aggregation)

# COMMAND ----------
top_products = (fact.join(F.broadcast(spark.read.format("delta").load(f"{GOLD}/dim_product")), "product_id")
    .groupBy("product_name","category")
    .agg(F.round(F.sum("amount"),2).alias("revenue"), F.sum("quantity").alias("units"))
    .orderBy(F.col("revenue").desc()))
display(top_products.limit(10))

daily = fact.groupBy("order_date").agg(F.round(F.sum("amount"),2).alias("revenue")).orderBy("order_date")
display(daily)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 9 — Delta features: time travel, OPTIMIZE, Z-ORDER, VACUUM

# COMMAND ----------
# time travel: read a previous version (before the MERGE)
display(spark.sql("DESCRIBE HISTORY de_practice.fact_orders").select("version","timestamp","operation"))
v0 = spark.read.format("delta").option("versionAsOf", 0).load(f"{GOLD}/fact_orders")
print("rows at version 0:", v0.count())

# OPTIMIZE (compact small files) + Z-ORDER (data skipping on a common filter column)
spark.sql(f"OPTIMIZE delta.`{GOLD}/fact_orders` ZORDER BY (customer_id)")
# VACUUM removes old files (default retains 7 days). Do NOT lower retention in prod without care.
# spark.sql(f"VACUUM delta.`{GOLD}/fact_orders` RETAIN 168 HOURS")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 10 — What you practiced (talk about this in interviews)
# MAGIC - Wrote & read **Parquet**; explored a messy dataset.
# MAGIC - **Medallion**: Bronze (raw) → Silver (clean: dedup, nulls, referential integrity) → Gold (star schema).
# MAGIC - **Delta Lake**: ACID tables, **MERGE/upsert** (incremental/CDC), **time travel**, **OPTIMIZE / Z-ORDER**.
# MAGIC - **Window functions** (top-N, running total), joins with **broadcast**, partitioned writes.
# MAGIC
# MAGIC **Next practice ideas:** add an **SCD Type 2** dimension (merge with effective/expiry dates),
# MAGIC try **Auto Loader** (`cloudFiles`) for incremental file ingestion, and build a **Delta Live
# MAGIC Tables** pipeline with quality expectations.
