# DEA-C01 One-Page Cheat Sheet

**Exam:** 65 Q (50 scored) · 130 min · pass **720/1000** · Domains: Ingest/Transform **34%**, Store **26%**, Ops **22%**, Security **18%**. Read for the *constraint* (cost / latency / durability / least-privilege / min-ops) → pick the service.

## Service comparisons — decide in one line
| Pick between | Use the first when… | Use the second when… |
|---|---|---|
| **Glue ↔ EMR** | serverless ETL, low ops | need full Spark/Hive/Presto cluster control |
| **Athena ↔ Redshift** | ad-hoc SQL on S3, pay-per-scan | fast repeated BI on loaded data (MPP) |
| **RDS/Aurora ↔ DynamoDB** | relational, joins, SQL/OLTP | key-value, massive scale, single-digit-ms |
| **Kinesis Streams ↔ Firehose** | custom real-time consumers | no-code delivery to S3/Redshift/OpenSearch |
| **Kinesis ↔ MSK** | AWS-native streaming | Kafka ecosystem / portability |
| **Step Functions ↔ MWAA** | native, low-ops state machine | complex code-first Airflow DAGs |
| **SQS ↔ SNS ↔ EventBridge** | point-to-point queue | pub/sub fan-out ‖ event routing + filter + schedule |
| **Glue Catalog ↔ Lake Formation** | metadata store | fine-grained row/column permissions |
| **CloudWatch ↔ CloudTrail** | metrics/logs/alarms (performance) | API audit (who did what) |
| **DMS ↔ DataSync** | DB migration + CDC | file/object transfer |
| **CSV/JSON ↔ Parquet/Avro** | interchange / human-readable | columnar analytics (Parquet) ‖ row-stream + schema-evolution (Avro) |
| **Provisioned ↔ Serverless** | steady heavy load, lowest unit cost | spiky/unknown load, no capacity mgmt |

## Reflexes (common right answers)
- Cheaper Athena → **Parquet + partitioning + compression** (cost = data scanned).
- Service needs S3 access → **IAM role**, never access keys.
- On-prem DB → AWS, minimal downtime → **DMS full load + CDC**.
- Incremental Glue runs → **job bookmarks**. Slow Spark → **skew / small files / wrong join**.
- Encrypt everything at rest → **SSE-KMS**; secrets → **Secrets Manager**.
- Fine-grained lake access (row/column) → **Lake Formation**.
- Decouple + don't lose work → **SQS + DLQ**; fan-out → **SNS**; route events → **EventBridge**.
- History in a dimension → **SCD Type 2**. Safe re-runs → **idempotency** (stable natural key).
- HA → **Multi-AZ**; DR → **multi-region**.

## The project (build a slice each day)
```
CSV/JSON → S3 raw → Glue Crawler+Catalog → Glue ETL (clean/dedup/join → Parquet)
        → S3 curated → Athena / Redshift → Step Functions + CloudWatch
```
✅ partition `year/month/day` · ✅ KMS on every zone · ✅ scoped IAM role · ✅ retry + DLQ · ✅ data-quality check · ✅ lifecycle policy · ✅ Lake Formation column perms · ✅ note the streaming variant

## 15-day map
**1** Cloud+IAM · **2** SQL · **3** Python+formats · **4** DE foundations (star/SCD) · **5** S3 lake · **6** Databases · **7** Glue+Athena · **8** Batch/Spark · **9** Streaming · **10** Orchestration · **11** Migration · **12** Ops+monitoring · **13** Security+governance · **14** Mock+repair (aim 75-80%) · **15** Final mock+review

> Every day: **read → build → drill questions → review**. Serverless/on-demand + budget alert; stop provisioned resources after each session.
