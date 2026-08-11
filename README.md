# AWS Learning & Interview Prep

A free, self-contained study kit for **AWS** — plain-language concept notes, exam-style
Q&A, real-world architectures, an interview deep-dive, and reference PDFs. Great for
anyone prepping for AWS certs, a Cloud/Data-Engineer role, or an architecture interview.

> Share this repo freely 🙂 — it contains **no credentials and no account-specific data**.

---

## 📚 Start here (concept notes — read on GitHub)

| Doc | What it covers |
|-----|----------------|
| [security-iam-vpc-ec2-interview-deepdive.md](docs/security-iam-vpc-ec2-interview-deepdive.md) | **The interview deep-dive.** Security, IAM, VPC, EC2, public/private subnets **and** every core service (S3, RDS, DynamoDB, Lambda, API Gateway, SQS/SNS, Glue/Athena, CloudWatch) — plain-language explanations, examples, Q&A, and real-world errors with fixes. |
| [aws-services-and-architectures.md](docs/aws-services-and-architectures.md) | Every core service with a real-world scenario + 7 reference architectures (how services combine) + how to read/design any architecture. |
| [aws-certification-qa.md](docs/aws-certification-qa.md) | Exam-style **Q&A across all 10 AWS domains** (VPC, EC2, ELB/ASG, storage, databases, IAM, serverless, messaging, monitoring, HA/DR/cost). Self-test format. |
| [services-scenarios-and-troubleshooting.md](docs/services-scenarios-and-troubleshooting.md) | Public vs private subnets with a request-flow scenario, each service with a scenario, and the real errors hit while building (+ fixes). |
| [public-vs-private-subnets.md](docs/public-vs-private-subnets.md) | Focused note: why EC2/RDS go in private subnets vs public. |
| [orders-api.md](docs/orders-api.md) | A serverless Orders API (API Gateway + Lambda + DynamoDB): endpoints, auth, deploy/test, common errors. |
| [dea-c01-15-day-plan.md](docs/dea-c01-15-day-plan.md) | **📅 15-day study plan for the AWS Data Engineer – Associate (DEA-C01) cert** — hour-by-hour daily timetable, detailed concepts per technology, a project you build day-by-day, and the key service comparisons. (PDF in [`pdfs/`](pdfs/DEA-C01_15_Day_Plan.pdf).) |
| [dea-c01-cheat-sheet.md](docs/dea-c01-cheat-sheet.md) | **🃏 One-page printable cheat sheet** — every service comparison, the common "right answer" reflexes, the daily project checklist, and the 15-day map on a single page. (PDF in [`pdfs/`](pdfs/DEA-C01_CheatSheet.pdf).) |

**Build guides**
- [BLUEPRINT.md](docs/BLUEPRINT.md) — a full VPC-based reference architecture (subnets, security groups, IAM) with an A→Z build order.
- [EXECUTION_GUIDE.md](docs/EXECUTION_GUIDE.md) — step-by-step deploy → verify → destroy runbook.

## 🔗 Appian ↔ AWS integration (bonus)

For anyone working with **Appian BPM** alongside AWS:

| Doc | Direction |
|-----|-----------|
| [appian-integration.md](appian-integration/appian-integration.md) | Appian → AWS (call an AWS API from Appian, with security & exceptions) |
| [aws-to-appian-integration.md](appian-integration/aws-to-appian-integration.md) | AWS → Appian (AWS events call into an Appian Web API) |
| [appian-aws-integration-catalog.md](appian-integration/appian-aws-integration-catalog.md) | Every place AWS can plug into Appian |
| [rest-api-explained.md](appian-integration/rest-api-explained.md) | REST APIs explained (Java Spring Boot vs Python FastAPI) |

## 📄 Reference PDFs (in [`pdfs/`](pdfs/))

Longer, formatted versions you can download and read offline:

- `AWS_Beginner_StepByStep_Guide.pdf` — AWS from zero: setup + core concepts + first services
- `AWS_Certification_Architecture_Blueprint.pdf` — full architecture, every connection, A→Z build order
- `AWS_Blueprint_Execution_Guide.pdf` — deploy → verify → destroy runbook
- `AWS_Data_Engineer_30Day_Prep.pdf` — 30-day study plan + Q&A
- `Terraform_AWS_Practice_Architecture.pdf` / `_Playbook.pdf` — Terraform module inventory + real errors & fixes
- `Terraform_with_Claude_Resources.pdf` — writing Terraform safely with Claude Code
- `IAM_Lab_Learning_Guide.pdf`, `S3_Bucket_Learning_Guide.pdf` — focused service labs
- `Order_Pipeline_Architecture.pdf`, `Data_Engineer_Practice_Lab_Food_Delivery_Platform.pdf`, `Food_Delivery_Platform_Interview_Walkthrough.pdf` — an end-to-end data-engineering project + how to present it

Diagram images are in [`diagrams/`](diagrams/).

---

## How to use this

1. New to AWS? Start with the **Beginner PDF**, then `public-vs-private-subnets.md`.
2. Prepping for an interview? Read the **interview deep-dive**, then drill the **cert Q&A**.
3. Want the big picture? `aws-services-and-architectures.md` + the **Blueprint**.

*Educational material — no warranties. Verify anything against the current
[AWS documentation](https://docs.aws.amazon.com/) before using in production.*

## Python Learning (`python/`)
Runnable, hands-on Python practice (functions, built-ins, data structures, OOP).
Each file: explanation → example → exercises → solutions. See `python/README.md`.

## Data Engineer — Glue, Crawler & Redshift
- `docs/aws-glue-crawler-redshift-guide.md` — clear concept guide with real examples & architecture.
- `docs/aws-data-engineer-glue-redshift-interview-guide.md` — interview guide (Q&A, scenarios, design patterns, tuning, troubleshooting).
- PDF versions in `pdfs/`.

## Data Lake Engineering — Real-World Scenarios
`docs/aws-data-lake-realtime-scenarios.md` (PDF in `pdfs/`) — 6 scenarios
(batch, streaming, CDC, IoT, Lake Formation governance, log analytics) with
architecture diagrams, services, data flow, design decisions, and challenges+fixes.

## Snowflake Data Engineering
`docs/snowflake-data-engineering-guide.md` (PDF in `pdfs/`) — complete guide,
beginner→advanced: 3-layer architecture on AWS, warehouses, S3 stages/Snowpipe,
Streams+Tasks/Dynamic Tables, Time Travel/cloning, a full end-to-end scenario,
graded real-time scenarios, Snowflake vs Redshift, and interview Q&A.

## dbt on Snowflake
`docs/dbt-on-snowflake-guide.md` (PDF in `pdfs/`) — the transformation (T) layer:
project structure, models/ref/source, materializations, incremental (MERGE),
snapshots (SCD2), tests, Jinja/macros, docs/lineage, deployment, a RetailCo
scenario, and interview Q&A.

## PySpark — Guide, Scenarios & Interview Prep
`docs/pyspark-guide-scenarios-interview.md` (PDF in `pdfs/`) — PySpark explained simply:
architecture, DataFrames, joins/windows, Spark SQL, UDFs, read/write/partitioning,
performance, why/where/when-NOT to use it, common errors & fixes, real scenarios, and Q&A.

## Data Engineering End-to-End Architecture (with Spark job internals)
`docs/data-engineering-end-to-end-architecture-spark.md` (PDF in `pdfs/`) — the complete
platform (sources → ingestion → lake → Spark → catalog → warehouse → BI/ML → orchestration/
governance/monitoring/IaC), a real-time ShopFast scenario, and a deep dive into what happens
when a Spark job is submitted (driver, cluster manager, executors, DAG, stages, tasks, shuffle,
Scala/JVM/Py4J) with diagrams.

## Data Engineering Architecture (neat, visual)
`pdfs/DataEngineering_Architecture_Neat.pdf` — a clean, color-coded layered diagram of the
full platform (Sources → Ingestion → Data Lake → Spark → Catalog → Warehouse → Consumers)
plus cross-cutting concerns, with a plain-language explanation of every component.

## Spark Job Execution Flow (neat, visual)
`pdfs/Spark_Job_Execution_Flow.pdf` — a clean step-by-step of what happens when a Spark job
is submitted (driver, cluster manager, executors, DAG, stages, shuffle, JVM/Py4J) using a 2 TB
revenue-by-region scenario. Also a live web version.

## Data Engineer Interview Prep (JD-specific, Q&A)
`docs/interview-prep/` + `pdfs/interview-prep/` — three targeted prep guides:
1. Security-focused cloud DE (ETL/ELT, ingestion, IaC, secure coding & data security, AWS, Python/SQL, data lakes).
2. Databricks/Delta Lake/AWS + dimensional & normalized data modeling + CI/CD standards.
3. Oracle warehouse + hybrid lakehouse (Apache Iceberg, OCI Object Storage, Parquet, external tables, shell/Linux, MDM).

### Coding round + mock drill
`interview-prep/DE_CodingRound_SQL_PySpark` — SQL + PySpark problems with solutions for the live round.
`interview-prep/DE_MockDrill_RapidFire` — 56 rapid-fire Q&A across all three JDs to practice aloud.

### Take-home mini-project (runnable)
`projects/de-take-home/` — a realistic ELT take-home + runnable reference solution (Python +
SQLite): ingest → clean (dedup/nulls/bad refs) → star schema → data-quality checks → analytics →
tests, with a PySpark/AWS scale-up section. See `pdfs/interview-prep/DE_TakeHome_Project_Guide.pdf`.

### 45-minute mock interview (with answers)
`interview-prep/DE_Mock_Interview_45min_WithAnswers` — a timed, mixed mock (warm-up → concepts →
SQL/coding → system design → your questions) with model answers and a scoring rubric.

## Databricks hands-on practice (with sample data + Parquet notebook)
`projects/databricks-practice/` — sample CSV data + a Databricks notebook that generates Parquet
and walks the full flow (explore → clean → star schema → Delta → MERGE → windows → time travel/
OPTIMIZE). Guide: `pdfs/Databricks_DE_Practice_Guide.pdf`.

### Databricks: beginner-to-expert (development + administration)
`pdfs/Databricks_Beginner_to_Expert_Dev_and_Admin.pdf` (+ md in projects/databricks-practice/) —
full guide: dev (clusters, Delta, medallion, MERGE, windows, Jobs, Auto Loader, DLT, tuning,
streaming, Unity Catalog, CI/CD) and admin (users/groups/UC governance, cluster policies/pools,
SQL warehouses, secrets, security, cost, monitoring). Pairs with the sample Parquet notebook.
