-- ============================================================================
-- SCD Type 1 & Type 2 — SQL Queries (Databricks)
-- Tables created by scd1_scd2_yelp_practice.py:
--   yelp.dim_business_scd1  (SCD1 — overwrite, no history)
--   yelp.dim_business_scd2  (SCD2 — start_date/end_date/is_current + business_sk)
-- Run in a Databricks SQL cell (%sql) or the SQL editor.
-- ============================================================================


-- ############################################################################
-- SCD TYPE 1  (overwrite — no history)
-- ############################################################################

-- View the dimension
SELECT * FROM yelp.dim_business_scd1 ORDER BY business_id;

-- Validate: one row per business (these two counts must be EQUAL)
SELECT COUNT(*) AS total, COUNT(DISTINCT business_id) AS distinct_biz
FROM yelp.dim_business_scd1;

-- Look up a single business (shows only the latest values)
SELECT * FROM yelp.dim_business_scd1 WHERE business_id = 'B002';

-- ---- SCD1 upsert (overwrite in place) ----
-- 1) stage a change batch
CREATE OR REPLACE TEMP VIEW business_changes AS
SELECT * FROM VALUES
  ('B002','Blue Bottle Coffee','Austin', 'TX','Coffee',      4.9, 400),  -- changed
  ('B006','Taco Fiesta',       'Dallas', 'TX','Restaurants', 4.1,  60)   -- new
AS t(business_id,name,city,state,category,stars,review_count);

-- 2) MERGE: update existing (old values lost), insert new
MERGE INTO yelp.dim_business_scd1 AS t
USING business_changes AS s
ON t.business_id = s.business_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- 3) verify
SELECT * FROM yelp.dim_business_scd1 ORDER BY business_id;


-- ############################################################################
-- SCD TYPE 2  (keep full history)
-- ############################################################################

-- All versions (expired + current)
SELECT business_id, city, stars, review_count, start_date, end_date, is_current
FROM yelp.dim_business_scd2 ORDER BY business_id, start_date;

-- CURRENT records only (what "today" looks like)
SELECT * FROM yelp.dim_business_scd2 WHERE is_current = true ORDER BY business_id;

-- Full history of ONE business
SELECT business_id, city, stars, start_date, end_date, is_current
FROM yelp.dim_business_scd2 WHERE business_id = 'B002' ORDER BY start_date;

-- POINT-IN-TIME: what did B003 look like on 2026-03-01?
SELECT business_id, city, stars, start_date, end_date
FROM yelp.dim_business_scd2
WHERE business_id = 'B003'
  AND start_date <= DATE'2026-03-01'
  AND (end_date > DATE'2026-03-01' OR end_date IS NULL);

-- Version count per business
SELECT business_id, COUNT(*) AS versions
FROM yelp.dim_business_scd2 GROUP BY business_id ORDER BY versions DESC;

-- ---- Integrity checks (should all pass) ----
-- 1) exactly ONE current row per business (result should be EMPTY)
SELECT business_id, COUNT(*) c
FROM yelp.dim_business_scd2 WHERE is_current = true
GROUP BY business_id HAVING COUNT(*) > 1;

-- 2) end_date consistency: current has none, expired has one (should be 0)
SELECT COUNT(*) AS bad_rows
FROM yelp.dim_business_scd2
WHERE (is_current = true  AND end_date IS NOT NULL)
   OR (is_current = false AND end_date IS NULL);

-- ---- SCD2 load: two-step pattern (expire old, insert new) ----
-- 1) stage the new load (effective 2026-07-01)
CREATE OR REPLACE TEMP VIEW business_changes2 AS
SELECT *, DATE'2026-07-01' AS effective_date FROM VALUES
  ('B002','Blue Bottle Coffee','Austin', 'TX','Coffee',      4.7, 350),  -- changed
  ('B003','Downtown Gym',      'Boulder','CO','Fitness',     3.5,  95),  -- changed city
  ('B006','Taco Fiesta',       'Dallas', 'TX','Restaurants', 4.1,  60)   -- new
AS t(business_id,name,city,state,category,stars,review_count);

-- 2) STEP 1 — expire the current row where a tracked attribute changed
MERGE INTO yelp.dim_business_scd2 AS t
USING business_changes2 AS s
ON t.business_id = s.business_id AND t.is_current = true
WHEN MATCHED AND (t.stars <> s.stars OR t.city <> s.city OR t.review_count <> s.review_count)
THEN UPDATE SET t.is_current = false, t.end_date = s.effective_date;

-- 3) STEP 2 — insert the new current version (for changed rows AND brand-new businesses)
INSERT INTO yelp.dim_business_scd2
SELECT s.business_id, s.name, s.city, s.state, s.category, s.stars, s.review_count,
       s.effective_date AS start_date, CAST(NULL AS DATE) AS end_date, true AS is_current,
       sha2(concat_ws('||', s.business_id, s.effective_date), 256) AS business_sk
FROM business_changes2 s
LEFT JOIN yelp.dim_business_scd2 t
  ON t.business_id = s.business_id AND t.is_current = true
WHERE t.business_id IS NULL;   -- current row was just expired, or business is brand-new

-- 4) verify: B002 now has 2 rows (old expired + new current)
SELECT business_id, city, stars, start_date, end_date, is_current
FROM yelp.dim_business_scd2 WHERE business_id = 'B002' ORDER BY start_date;

-- ---- Soft-delete a source-deleted business (SCD2 keeps history) ----
UPDATE yelp.dim_business_scd2
SET is_current = false, end_date = DATE'2026-07-01'
WHERE business_id = 'B004' AND is_current = true;


-- ############################################################################
-- WHAT EACH PROVES
--   SCD1: COUNT(*) = COUNT(DISTINCT id)  -> one row per key, no history
--   SCD2: changed business has old+new versions; exactly one is_current per key;
--         point-in-time query reconstructs any past state; end_date consistent
-- ############################################################################
