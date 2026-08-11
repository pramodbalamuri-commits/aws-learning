"""Lightweight tests for the pipeline (run after pipeline.py). Pure stdlib — run:
   python3 test_pipeline.py
Exits non-zero if any assertion fails (so it can gate a CI job)."""
import os, sqlite3, sys

DB = os.path.join(os.path.dirname(__file__), "warehouse.db")
assert os.path.exists(DB), "Run pipeline.py first."
conn = sqlite3.connect(DB); cur = conn.cursor()
fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond: fails.append(name)


print("=== TESTS ===")
# fact has rows
n = cur.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0]
check("fact_orders has rows", n > 0)

# only completed orders survived
bad_status = cur.execute("""SELECT COUNT(*) FROM fact_orders f JOIN cleaned_orders c
                            ON c.order_id=f.order_id WHERE c.status <> 'completed'""").fetchone()[0]
check("only completed orders in fact", bad_status == 0)

# no duplicate order_ids
dupes = cur.execute("SELECT COUNT(*) FROM (SELECT order_id FROM fact_orders GROUP BY order_id HAVING COUNT(*)>1)").fetchone()[0]
check("no duplicate order_ids", dupes == 0)

# revenue reconciles: fact total == sum over cleaned
f_total = cur.execute("SELECT ROUND(SUM(amount),2) FROM fact_orders").fetchone()[0]
c_total = cur.execute("SELECT ROUND(SUM(amount),2) FROM cleaned_orders").fetchone()[0]
check("fact revenue reconciles with cleaned", f_total == c_total)

# every fact row has a valid date_key in dim_date
orphan_d = cur.execute("""SELECT COUNT(*) FROM fact_orders f LEFT JOIN dim_date d
                          ON d.date_key=f.date_key WHERE d.date_key IS NULL""").fetchone()[0]
check("fact -> dim_date integrity", orphan_d == 0)

conn.close()
if fails:
    print(f"\n{len(fails)} test(s) FAILED: {fails}"); sys.exit(1)
print("\nAll tests passed.")
