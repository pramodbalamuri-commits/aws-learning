"""Generate messy raw sample data for the take-home pipeline (orders, customers, products).
Deliberately includes nulls, duplicates, cancelled orders, and bad amounts so the pipeline
has real cleaning to do. Pure standard library."""
import csv, os, random
from datetime import date, timedelta

random.seed(42)
RAW = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(RAW, exist_ok=True)

REGIONS = ["West", "East", "South", "Central"]
CATEGORIES = ["Electronics", "Home", "Toys", "Sports", "Books"]

# customers.csv
customers = []
for i in range(1, 51):
    customers.append({
        "customer_id": i,
        "name": f"Customer {i}",
        "region": random.choice(REGIONS) if random.random() > 0.05 else "",  # some blanks
    })
with open(os.path.join(RAW, "customers.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["customer_id", "name", "region"]); w.writeheader(); w.writerows(customers)

# products.csv
products = []
for i in range(1, 21):
    products.append({
        "product_id": i,
        "product_name": f"Product {i}",
        "category": random.choice(CATEGORIES),
        "unit_price": round(random.uniform(5, 500), 2),
    })
with open(os.path.join(RAW, "products.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category", "unit_price"]); w.writeheader(); w.writerows(products)

# orders.csv — the messy fact source
start = date(2026, 7, 1)
rows = []
oid = 1000
for _ in range(2000):
    oid += 1
    d = start + timedelta(days=random.randint(0, 39))
    qty = random.randint(1, 5)
    price = round(random.uniform(5, 500), 2)
    status = random.choices(["completed", "cancelled", "pending"], weights=[75, 15, 10])[0]
    rows.append({
        "order_id": oid,
        "customer_id": random.randint(1, 55),          # a few point to non-existent customers (bad refs)
        "product_id": random.randint(1, 20),
        "quantity": qty,
        "amount": round(qty * price, 2) if random.random() > 0.03 else "",  # some blank amounts
        "status": status,
        "order_ts": f"{d.isoformat()} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00",
    })
# inject ~30 duplicate rows (same order_id appearing twice)
for r in random.sample(rows, 30):
    dup = dict(r); rows.append(dup)

with open(os.path.join(RAW, "orders.csv"), "w", newline="") as f:
    cols = ["order_id", "customer_id", "product_id", "quantity", "amount", "status", "order_ts"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

print(f"Generated raw data in {RAW}: {len(customers)} customers, {len(products)} products, {len(rows)} order rows (with dupes/nulls/bad refs).")
