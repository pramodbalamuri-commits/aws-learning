# Databricks Certified Data Engineer Associate — Practice Test (45 Q)

Exam-style multiple choice. Give yourself **90 minutes**, answer all 45, then check the **Answer
Key** at the end. Passing ≈ 70% (≈ 32/45). Questions are grouped by domain but mixed in difficulty.

---

## Questions

**1.** The Databricks Lakehouse combines:
A) OLTP + NoSQL  B) Data lake storage + data warehouse reliability/performance  C) Only Spark  D) Only SQL

**2.** In the Databricks architecture, where do the clusters (compute) that process your data run?
A) Databricks control plane  B) Your cloud account (data plane)  C) On your laptop  D) In DBFS

**3.** You drop an **external** table (created with `LOCATION`). What happens to the files?
A) Deleted  B) Kept in the storage location  C) Moved to trash  D) Corrupted

**4.** Delta Lake adds which capability on top of Parquet?
A) Only compression  B) ACID transactions, time travel, schema enforcement  C) OLTP indexing  D) Nothing

**5.** Which cluster type is most cost-effective for a scheduled batch job?
A) All-purpose cluster  B) SQL warehouse  C) Job cluster  D) Cluster pool only

**6.** What is DBFS?
A) A database engine  B) A filesystem abstraction over cloud object storage  C) A cluster type  D) A governance tool

**7.** Which best reduces cluster cost from idle clusters?
A) Larger nodes  B) Auto-termination  C) More workers  D) Caching

**8.** A **global temp view** is accessible:
A) Only in the current notebook  B) Across all notebooks on the same cluster  C) Across all workspaces  D) Forever

**9.** Which command creates a table from a query result?
A) `INSERT INTO`  B) `COPY INTO`  C) `CREATE TABLE ... AS SELECT`  D) `MERGE`

**10.** To read a JSON file directly with Spark SQL:
A) `` SELECT * FROM json.`/path/` ``  B) `LOAD json`  C) `IMPORT json`  D) `READ json`

**11.** Repos in Databricks provide:
A) Cluster management  B) Git version control integration  C) Secret storage  D) SQL dashboards

**12.** Which write mode replaces all existing data in a Delta table?
A) `append`  B) `overwrite`  C) `ignore`  D) `merge`

**13.** You must upsert (update matching rows, insert new ones) into a Delta table. Use:
A) `INSERT INTO`  B) `MERGE INTO`  C) `COPY INTO`  D) `UPDATE`

**14.** `COPY INTO` is best described as:
A) A streaming source  B) An idempotent, retriable bulk file load into a Delta table  C) A cluster policy  D) A view type

**15.** Auto Loader (`cloudFiles`) is used to:
A) Compact files  B) Incrementally ingest new files as a stream with checkpointing  C) Grant permissions  D) Schedule jobs

**16.** In Structured Streaming, exactly-once processing requires:
A) `cache()`  B) A checkpoint location  C) `OPTIMIZE`  D) `overwrite` mode

**17.** `OPTIMIZE ... ZORDER BY (col)` does what?
A) Deletes old files  B) Compacts small files and co-locates data for skipping  C) Grants access  D) Creates a view

**18.** `VACUUM` on a Delta table:
A) Compacts files  B) Removes data files no longer referenced (default 7-day retention)  C) Rebuilds indexes  D) Refreshes stats

**19.** Query a Delta table as of version 5:
A) `SELECT * FROM t@5`  B) `SELECT * FROM t VERSION AS OF 5`  C) `ROLLBACK 5`  D) `RESTORE 5`

**20.** Which is NOT a Delta Lake benefit?
A) ACID  B) Time travel  C) Schema enforcement  D) Sub-millisecond single-row OLTP lookups

**21.** To avoid shuffling a large table when joining a small dimension:
A) `repartition`  B) `coalesce`  C) Broadcast the small table  D) `cache` the large table

**22.** A transformation in Spark is:
A) Executed immediately  B) Lazy — builds the plan; runs on an action  C) Always a shuffle  D) A cluster setting

**23.** Which is an **action** (triggers execution)?
A) `filter`  B) `select`  C) `count`  D) `withColumn`

**24.** Deduplicate keeping the latest row per key — best approach:
A) `DISTINCT`  B) `ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC)` = 1  C) `GROUP BY key`  D) `LIMIT 1`

**25.** A temp view created with `CREATE OR REPLACE TEMP VIEW` is:
A) Permanent  B) Session-scoped  C) Cluster-scoped  D) Cross-workspace

**26.** `INSERT OVERWRITE` on a partitioned table (dynamic) affects:
A) All partitions always  B) Only the partitions present in the new data (with dynamic overwrite)  C) No partitions  D) Metadata only

**27.** To flatten an array column into rows:
A) `split()`  B) `explode()`  C) `collect_list()`  D) `flatten()` only

**28.** Extract a field from a JSON string column `payload`:
A) `payload->field`  B) `payload:field` / `from_json`  C) `payload.field()`  D) `get(payload)`

**29.** Which statement about **managed** tables is true?
A) Dropping keeps the data  B) Dropping deletes both metadata and data  C) You must specify LOCATION  D) They can't be Delta

**30.** Delta Live Tables (DLT) `@dlt.expect_or_drop("r","amount>0")` will:
A) Fail the pipeline on violation  B) Drop rows violating the rule, keep running  C) Only log a warning  D) Ignore the rule

**31.** DLT `@dlt.expect_or_fail(...)` on violation:
A) Drops rows  B) Warns only  C) Fails the pipeline/update  D) Auto-fixes data

**32.** A Databricks **Job** can:
A) Only run one task  B) Chain multiple tasks with dependencies, schedule, and retries  C) Not use clusters  D) Only run SQL

**33.** Best way to alert on a failed scheduled job:
A) Poll manually  B) Configure email/webhook notifications on failure  C) Cache results  D) Increase workers

**34.** In DLT, a `STREAMING LIVE TABLE` is used for:
A) Static lookups  B) Incrementally processed streaming sources  C) Governance  D) Cluster config

**35.** Unity Catalog's namespace is:
A) `schema.table`  B) `catalog.schema.table`  C) `database.table`  D) `table` only

**36.** Grant read on a table to a group in Unity Catalog:
A) `GRANT SELECT ON TABLE cat.sch.t TO group`  B) `ALLOW READ`  C) `USE TABLE`  D) `SHOW GRANTS`

**37.** Column masking / row filtering for non-privileged users is typically done with:
A) A cluster policy  B) A dynamic view (`is_account_group_member`)  C) VACUUM  D) A secret scope

**38.** Where should database passwords be stored?
A) In the notebook code  B) In a Databricks secret scope, read via `dbutils.secrets.get`  C) In DBFS as text  D) In a table

**39.** Which reduces Spark job time by skipping data at read?
A) `collect()`  B) Partition pruning + ZORDER data skipping  C) More UDFs  D) `orderBy`

**40.** A cluster **policy** is used to:
A) Grant table access  B) Constrain cluster config (size, node type, auto-termination) for standardization/cost  C) Schedule jobs  D) Store secrets

**41.** Which format does Delta store data files in?
A) CSV  B) Parquet  C) Avro  D) ORC

**42.** The Delta transaction log directory is:
A) `/_checkpoints`  B) `/_delta_log`  C) `/_metadata`  D) `/_history`

**43.** `DESCRIBE HISTORY table` shows:
A) The schema  B) The version/operation history (for time travel/audit)  C) Row counts only  D) Grants

**44.** To incrementally load only new files repeatedly and idempotently in batch, prefer:
A) `spark.read` full reload each run  B) `COPY INTO` (or Auto Loader)  C) `DISTINCT`  D) `OPTIMIZE`

**45.** Which is true about SQL Warehouses?
A) They run notebooks  B) They provide SQL compute for BI/dashboards (serverless/pro/classic)  C) They are governance objects  D) They replace Delta

---

## ANSWER KEY (with one-line why)

1. **B** — lakehouse = lake storage + warehouse reliability.
2. **B** — clusters run in the customer's data plane; control plane is managed by Databricks.
3. **B** — external tables keep files on drop; managed delete data.
4. **B** — Delta adds ACID, time travel, schema enforcement.
5. **C** — job clusters spin up per run, cheapest for scheduled work.
6. **B** — DBFS is a filesystem over cloud storage.
7. **B** — auto-termination stops idle clusters.
8. **B** — global temp view = cluster-scoped; temp view = session.
9. **C** — CTAS creates a table from a query.
10. **A** — file-source SQL: `` json.`/path` ``.
11. **B** — Repos = Git integration.
12. **B** — `overwrite` replaces data.
13. **B** — MERGE = upsert.
14. **B** — COPY INTO = idempotent bulk file load.
15. **B** — Auto Loader = incremental streaming file ingestion.
16. **B** — checkpoint gives exactly-once.
17. **B** — OPTIMIZE compacts; ZORDER co-locates for skipping.
18. **B** — VACUUM removes unreferenced files (7-day default).
19. **B** — `VERSION AS OF`.
20. **D** — Delta is analytics, not OLTP.
21. **C** — broadcast the small table.
22. **B** — transformations are lazy.
23. **C** — `count` is an action.
24. **B** — ROW_NUMBER window dedup.
25. **B** — temp view is session-scoped.
26. **B** — dynamic partition overwrite affects only present partitions.
27. **B** — `explode()` array → rows.
28. **B** — `payload:field` / `from_json`.
29. **B** — managed drop deletes data.
30. **B** — expect_or_drop drops bad rows, keeps running.
31. **C** — expect_or_fail fails the pipeline.
32. **B** — Jobs chain tasks with deps/schedule/retries.
33. **B** — configure failure notifications.
34. **B** — streaming live table = incremental streaming source.
35. **B** — three-level `catalog.schema.table`.
36. **A** — `GRANT SELECT ON TABLE ... TO group`.
37. **B** — dynamic view with group checks.
38. **B** — secret scope + `dbutils.secrets.get`.
39. **B** — pruning + ZORDER skip data.
40. **B** — cluster policy constrains config/cost.
41. **B** — Delta stores Parquet files.
42. **B** — `_delta_log`.
43. **B** — DESCRIBE HISTORY = version/operation history.
44. **B** — COPY INTO / Auto Loader for idempotent incremental loads.
45. **B** — SQL Warehouses = SQL compute for BI.

**Score:** /45. **~32+ = passing range.** Review every miss and re-read that topic in the prep sheet.
```
