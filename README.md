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
