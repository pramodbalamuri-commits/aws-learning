"""
Take-home reference solution — an ELT pipeline in pure Python + SQLite.

Flow (medallion-style):
  RAW csv  --load-->  staging (bronze)  --clean-->  cleaned (silver)
           --model--> star schema: dim_customer, dim_product, dim_date, fact_orders (gold)
  then: data-quality checks + analytics.

Run:  python3 pipeline.py
"""
import csv, os, sqlite3, sys
from datetime import datetime

HERE = os.path.dirname(__file__)
RAW = os.path.join(HERE, "data", "raw")
CURATED = os.path.join(HERE, "data", "curated")
DB = os.path.join(HERE, "warehouse.db")
os.makedirs(CURATED, exist_ok=True)


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def build(conn):
    cur = conn.cursor()

    # ---------- BRONZE: load raw as-is into staging tables ----------
    cust = load_csv(os.path.join(RAW, "customers.csv"))
    prod = load_csv(os.path.join(RAW, "products.csv"))
    orders = load_csv(os.path.join(RAW, "orders.csv"))

    cur.executescript("""
        DROP TABLE IF EXISTS stg_customers; DROP TABLE IF EXISTS stg_products; DROP TABLE IF EXISTS stg_orders;
        CREATE TABLE stg_customers(customer_id INT, name TEXT, region TEXT);
        CREATE TABLE stg_products(product_id INT, product_name TEXT, category TEXT, unit_price REAL);
        CREATE TABLE stg_orders(order_id INT, customer_id INT, product_id INT, quantity INT,
                                amount TEXT, status TEXT, order_ts TEXT);
    """)
    cur.executemany("INSERT INTO stg_customers VALUES (?,?,?)",
                    [(c["customer_id"], c["name"], c["region"]) for c in cust])
    cur.executemany("INSERT INTO stg_products VALUES (?,?,?,?)",
                    [(p["product_id"], p["product_name"], p["category"], p["unit_price"]) for p in prod])
    cur.executemany("INSERT INTO stg_orders VALUES (?,?,?,?,?,?,?)",
                    [(o["order_id"], o["customer_id"], o["product_id"], o["quantity"],
                      o["amount"], o["status"], o["order_ts"]) for o in orders])

    # ---------- SILVER: clean orders ----------
    # rules: keep completed only, drop blank/<=0 amounts, DEDUPE by order_id (keep latest ts),
    #        keep only orders whose customer & product exist (referential integrity).
    cur.executescript("""
        DROP TABLE IF EXISTS cleaned_orders;
        CREATE TABLE cleaned_orders AS
        WITH typed AS (
            SELECT order_id, customer_id, product_id, quantity,
                   CAST(NULLIF(amount,'') AS REAL) AS amount,
                   lower(status) AS status, order_ts
            FROM stg_orders
        ),
        deduped AS (            -- keep one row per order_id (latest timestamp)
            SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_ts DESC) rn
            FROM typed
        )
        SELECT d.order_id, d.customer_id, d.product_id, d.quantity, d.amount, d.status, d.order_ts
        FROM deduped d
        JOIN stg_customers c ON c.customer_id = d.customer_id     -- valid customer
        JOIN stg_products  p ON p.product_id  = d.product_id      -- valid product
        WHERE d.rn = 1
          AND d.status = 'completed'
          AND d.amount IS NOT NULL AND d.amount > 0;
    """)

    # ---------- GOLD: star schema ----------
    cur.executescript("""
        DROP TABLE IF EXISTS dim_customer; DROP TABLE IF EXISTS dim_product;
        DROP TABLE IF EXISTS dim_date;     DROP TABLE IF EXISTS fact_orders;

        CREATE TABLE dim_customer AS
          SELECT customer_id, name, COALESCE(NULLIF(region,''),'Unknown') AS region FROM stg_customers;

        CREATE TABLE dim_product AS
          SELECT product_id, product_name, category, unit_price FROM stg_products;

        CREATE TABLE dim_date AS
          SELECT DISTINCT date(order_ts) AS date_key,
                 CAST(strftime('%Y', order_ts) AS INT) AS year,
                 CAST(strftime('%m', order_ts) AS INT) AS month,
                 CAST(strftime('%d', order_ts) AS INT) AS day
          FROM cleaned_orders;

        CREATE TABLE fact_orders AS
          SELECT order_id, customer_id, product_id, date(order_ts) AS date_key,
                 quantity, amount
          FROM cleaned_orders;
    """)
    conn.commit()

    # export gold to curated CSVs (like writing Parquet to the curated zone)
    for t in ["dim_customer", "dim_product", "dim_date", "fact_orders"]:
        rows = cur.execute(f"SELECT * FROM {t}").fetchall()
        headers = [d[0] for d in cur.description]
        with open(os.path.join(CURATED, f"{t}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(headers); w.writerows(rows)


def data_quality(conn):
    """Fail the pipeline if any check fails (like dbt/GE tests)."""
    cur = conn.cursor()
    checks = []

    def add(name, ok, detail=""):
        checks.append((name, ok, detail))

    # 1. primary key unique in fact
    dup = cur.execute("SELECT order_id, COUNT(*) c FROM fact_orders GROUP BY order_id HAVING c>1").fetchall()
    add("fact_orders.order_id is unique", len(dup) == 0, f"{len(dup)} dupes")

    # 2. no nulls in keys/measures
    nulls = cur.execute("SELECT COUNT(*) FROM fact_orders WHERE order_id IS NULL OR amount IS NULL").fetchone()[0]
    add("no null keys/amounts in fact", nulls == 0, f"{nulls} nulls")

    # 3. all amounts positive
    neg = cur.execute("SELECT COUNT(*) FROM fact_orders WHERE amount <= 0").fetchone()[0]
    add("all amounts > 0", neg == 0, f"{neg} bad")

    # 4. referential integrity: every fact customer/product exists in its dim
    orphan_c = cur.execute("""SELECT COUNT(*) FROM fact_orders f
                              LEFT JOIN dim_customer d ON d.customer_id=f.customer_id
                              WHERE d.customer_id IS NULL""").fetchone()[0]
    orphan_p = cur.execute("""SELECT COUNT(*) FROM fact_orders f
                              LEFT JOIN dim_product d ON d.product_id=f.product_id
                              WHERE d.product_id IS NULL""").fetchone()[0]
    add("fact -> dim_customer integrity", orphan_c == 0, f"{orphan_c} orphans")
    add("fact -> dim_product integrity", orphan_p == 0, f"{orphan_p} orphans")

    print("\n=== DATA QUALITY CHECKS ===")
    all_ok = True
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if not ok else ""))
        all_ok = all_ok and ok
    if not all_ok:
        print("Data quality FAILED — stopping pipeline.")
        sys.exit(1)
    return all_ok


def analytics(conn):
    cur = conn.cursor()
    print("\n=== ANALYTICS ===")

    print("\nRevenue by region:")
    for r in cur.execute("""
        SELECT c.region, ROUND(SUM(f.amount),2) revenue, COUNT(*) orders
        FROM fact_orders f JOIN dim_customer c ON c.customer_id=f.customer_id
        GROUP BY c.region ORDER BY revenue DESC"""):
        print(f"  {r[0]:<10} revenue={r[1]:>10}  orders={r[2]}")

    print("\nTop 5 products by revenue:")
    for r in cur.execute("""
        SELECT p.product_name, p.category, ROUND(SUM(f.amount),2) revenue
        FROM fact_orders f JOIN dim_product p ON p.product_id=f.product_id
        GROUP BY p.product_id ORDER BY revenue DESC LIMIT 5"""):
        print(f"  {r[0]:<12} {r[1]:<12} revenue={r[2]}")

    print("\nDaily revenue (first 5 days):")
    for r in cur.execute("""
        SELECT date_key, ROUND(SUM(amount),2) revenue
        FROM fact_orders GROUP BY date_key ORDER BY date_key LIMIT 5"""):
        print(f"  {r[0]}  revenue={r[1]}")

    total = cur.execute("SELECT ROUND(SUM(amount),2), COUNT(*) FROM fact_orders").fetchone()
    print(f"\nTOTAL curated revenue = {total[0]} across {total[1]} clean orders")


def main():
    if not os.path.exists(os.path.join(RAW, "orders.csv")):
        print("Raw data missing — run `python3 generate_data.py` first."); sys.exit(1)
    conn = sqlite3.connect(DB)
    build(conn)
    data_quality(conn)
    analytics(conn)
    conn.close()
    print(f"\nDone. Curated star-schema tables written to {CURATED}/")


if __name__ == "__main__":
    main()
