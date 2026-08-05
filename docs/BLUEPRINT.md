# AWS Certification Practice — Architecture Blueprint

A complete, buildable AWS reference environment for hands-on certification practice
(**Solutions Architect Associate** core, plus **Cloud Practitioner** and much of
**Developer Associate**). It combines VPC networking, load-balanced auto-scaling
compute, a Multi-AZ database, serverless, and messaging — all secured with IAM and
security groups, and provisioned with **Terraform**.

![AWS architecture blueprint](docs/aws-blueprint.png)

---

## Table of Contents

1. [What you're building](#1-what-youre-building)
2. [How it works — layered walkthrough](#2-how-it-works--layered-walkthrough)
3. [Service inventory](#3-service-inventory)
4. [Network plan (CIDR & routing)](#4-network-plan-cidr--routing)
5. [Every connection explained (1–16)](#5-every-connection-explained-116)
6. [Security groups (tiered firewalls)](#6-security-groups-tiered-firewalls)
7. [IAM roles & policies](#7-iam-roles--policies)
8. [**Build order — A to Z**](#8-build-order--a-to-z)
9. [Terraform module layout](#9-terraform-module-layout)
10. [Cost, cleanup & certification coverage](#10-cost-cleanup--certification-coverage)

---

## 1. What you're building

A **private, isolated network (VPC)** spanning **two Availability Zones** for high
availability, with:

- a **public tier** — load balancer, NAT gateway, bastion host (the "lobby"),
- a **private tier** — application servers and database (the "back office"),
- **serverless & messaging** — Lambda, S3, DynamoDB, SNS, SQS,
- **security everywhere** — tiered security groups, least-privilege IAM,
- **observability** — CloudWatch logs, metrics, alarms, VPC Flow Logs,
- **all as code** — one Terraform project builds and destroys it reproducibly.

**Design principles (what the exam tests):**

| Principle | How it's applied here |
|-----------|----------------------|
| High availability | 2 AZs, Multi-AZ RDS, Auto Scaling Group across subnets |
| Security | Private subnets for app/DB, tiered SGs, no public database, IAM roles (no static keys) |
| Decoupling | SNS/SQS between producers and consumers; event-driven Lambda |
| Least-cost data access | VPC Gateway Endpoints keep S3/DynamoDB traffic off the internet/NAT |
| Reproducibility | Terraform Infrastructure as Code |

---

## 2. How it works — layered walkthrough

Think of the **VPC as a secure office building** with a private address space
(`10.0.0.0/16`), **public rooms** (reachable from the street) and **private rooms**
(no street access), duplicated across **two buildings (AZs)** for resilience.

**Layer 1 — Network foundation.** The **VPC** is the building. **Subnets** are rooms
(2 public + 2 private). The **Internet Gateway (IGW)** is the front door — the only
path to the internet. **Route tables** are the signposts directing traffic.

**Layer 2 — Traffic in (the request path).** A user's DNS query hits **Route 53**,
which points to the **Application Load Balancer (ALB)** in the public subnets. The
ALB is the *only* public-facing component; it forwards requests to **EC2 app
servers hidden in the private subnets**, spreading load across both AZs.

**Layer 3 — Traffic out.** Private servers reach the internet for patches/updates
through a **NAT Gateway** (a one-way exit door): outbound is allowed, inbound from
the internet is not.

**Layer 4 — Data tier.** **RDS** (MySQL/PostgreSQL) lives in the private subnets and
is never publicly accessible. **Multi-AZ** keeps a synchronized standby in the other
AZ with automatic failover.

**Layer 5 — Private access to S3 & DynamoDB.** **VPC Gateway Endpoints** create a
private hallway to S3 and DynamoDB over the AWS backbone — cheaper and more secure
than going through the NAT/internet.

**Layer 6 — Serverless & messaging.** **Lambda** runs only when triggered
(e.g., an **S3 upload → Lambda → DynamoDB**). **SNS → SQS → Lambda** decouples
producers from consumers: SNS announces events, SQS buffers them (with retries and
a dead-letter queue), and Lambda processes them at a safe pace.

**Cross-cutting layers.** **Security groups** are stateful firewalls on each tier
that reference *each other* as sources (a chain of trust). **IAM** grants EC2/Lambda
temporary role-based credentials — no stored keys. **CloudWatch** is the security
camera. **Terraform** is the blueprint + construction crew.

**One-sentence summary:** *A two-AZ VPC where a public load balancer is the only
front door, private auto-scaled EC2 app servers sit behind it and talk to a Multi-AZ
RDS database, reach S3/DynamoDB through private endpoints, offload async work through
SNS→SQS→Lambda, get outbound-only internet via NAT — all locked down with tiered
security groups and IAM roles, watched by CloudWatch, and built with Terraform.*

---

## 3. Service inventory

| Service | Role in the architecture | Where it lives |
|---------|--------------------------|----------------|
| **IAM** | Users, groups, roles, policies, MFA — who/what can do what | Global (account-wide) |
| **VPC** | Isolated private network (`10.0.0.0/16`) | Regional (us-west-2) |
| **Subnets** | 2 public + 2 private, one pair per AZ | Per Availability Zone |
| **Internet Gateway** | The VPC's door to the internet | Attached to the VPC |
| **NAT Gateway** | Outbound-only internet for private subnets | Public subnet (per AZ) |
| **Route Tables** | Direct traffic (public→IGW, private→NAT/endpoints) | Per subnet |
| **Security Groups** | Stateful virtual firewalls, one per tier | Attached to ENIs |
| **ALB (Elastic Load Balancer)** | Distributes inbound traffic to EC2 | Public subnets (multi-AZ) |
| **EC2 + Auto Scaling** | Application compute in the private tier | Private subnets |
| **Bastion host (EC2)** | Controlled SSH entry to private instances | Public subnet |
| **RDS (Multi-AZ)** | Managed relational DB (MySQL/PostgreSQL) | Private subnets |
| **S3** | Object storage / data lake / static assets | Regional service |
| **DynamoDB** | NoSQL key-value table | Regional service |
| **Lambda** | Serverless functions (event-driven + VPC-attached) | Regional (optionally in VPC) |
| **SNS** | Pub/sub topic (fan-out notifications) | Regional service |
| **SQS** | Message queue (buffering, retries, DLQ) | Regional service |
| **VPC Endpoints** | Private access to S3 & DynamoDB | In the VPC route tables |
| **CloudWatch** | Logs, metrics, alarms, VPC Flow Logs | Regional service |
| **Terraform** | Infrastructure as Code — provisions all of the above | Your laptop / CI |

---

## 4. Network plan (CIDR & routing)

| Resource | CIDR / Setting | Notes |
|----------|----------------|-------|
| VPC | `10.0.0.0/16` | 65,536 IPs total |
| Public Subnet A (AZ-a) | `10.0.1.0/24` | ALB node, NAT GW A, Bastion |
| Public Subnet B (AZ-b) | `10.0.2.0/24` | ALB node, NAT GW B |
| Private Subnet A (AZ-a) | `10.0.11.0/24` | EC2 App A, RDS primary, Lambda ENI |
| Private Subnet B (AZ-b) | `10.0.12.0/24` | EC2 App B, RDS standby |
| Public Route Table | `0.0.0.0/0 → Internet Gateway` | Associated to both public subnets |
| Private Route Table | `0.0.0.0/0 → NAT Gateway` (+ S3/DynamoDB endpoint routes) | Associated to both private subnets |

- Enable **auto-assign public IP** on public subnets only.
- Turn on **VPC Flow Logs → CloudWatch** to observe allowed/denied traffic.

---

## 5. Every connection explained (1–16)

Numbers match the diagram.

| # | Connection | What happens |
|---|------------|--------------|
| **1** | Users / Route 53 → Internet Gateway | DNS resolves your domain to the ALB; traffic (80/443) enters the VPC via the IGW — the only path in/out. |
| **2** | Internet Gateway → ALB | Public route table sends `0.0.0.0/0 → IGW`; the ALB (in both public subnets) receives inbound 80/443. |
| **3** | ALB → EC2 app servers (private) | ALB forwards to a Target Group of EC2 in **private** subnets. App-SG allows 80/443 **from ALB-SG only**. |
| **4** | EC2 (private) → NAT → IGW | Outbound-only internet for patches/APIs. Private route table sends `0.0.0.0/0 → NAT`. Internet can't initiate inbound. |
| **5** | EC2 → RDS | App servers connect on 3306/5432. DB-SG allows the DB port **from App-SG only**. RDS is private, never public. |
| **6** | RDS Primary ↔ Standby | Multi-AZ synchronous replication + automatic failover. Requires a DB subnet group spanning both private subnets. |
| **7** | Private tier → S3 (Gateway Endpoint) | A Gateway VPC Endpoint routes S3 traffic over the AWS backbone — no internet/NAT. Cheaper + more secure. |
| **8** | Private tier → DynamoDB (Gateway Endpoint) | Same pattern for DynamoDB — table traffic stays private. |
| **9** | Lambda (in VPC) → RDS | A VPC-attached Lambda gets an ENI in private subnets; Lambda-SG is allowed by DB-SG. Serverless DB access. |
| **10** | SNS → SQS | SNS topic fans out each message to subscribed SQS queue(s), decoupling producers from consumers. |
| **11** | SQS → Lambda | Event source mapping triggers Lambda per batch; SQS buffers spikes and retries; failures go to a DLQ. |
| **12** | Lambda → SNS (publish) | Lambda publishes notifications/events; subscribers (email, SMS, other Lambdas, SQS) receive them. |
| **13** | S3 event → Lambda | S3 `ObjectCreated` triggers a Lambda (event-driven ingestion). Function needs `s3:GetObject`. |
| **14** | Everything → CloudWatch | Lambda/EC2 logs, RDS/ALB metrics, VPC Flow Logs → alarms & dashboards. |
| **15** | IAM roles → EC2 & Lambda | EC2 uses an instance profile, Lambda an execution role — least-privilege, no static keys. |
| **16** | Terraform → all resources | One IaC codebase provisions everything: `init → validate → plan → apply` (and `destroy`). |

---

## 6. Security groups (tiered firewalls)

Security groups are **stateful** (return traffic is auto-allowed). Reference **other
security groups as the source**, not IP ranges — the secure, exam-correct approach.
This creates a **chain of trust**: each tier only accepts traffic from the tier in
front of it.

| Security Group | Inbound (allow) | Source | Outbound |
|----------------|-----------------|--------|----------|
| **ALB-SG** | 80, 443 | `0.0.0.0/0` (internet) | to App-SG |
| **App-SG** (EC2) | 80, 443 | ALB-SG | all (via NAT) + to DB-SG |
| | 22 (SSH) | Bastion-SG | |
| **Bastion-SG** | 22 (SSH) | `YOUR_IP/32` only | to App-SG |
| **DB-SG** (RDS) | 3306 or 5432 | App-SG **and** Lambda-SG | (none needed) |
| **Lambda-SG** | (none inbound) | — | to DB-SG + endpoints |

---

## 7. IAM roles & policies

| Identity / Role | Trusted by | Key permissions (scoped) |
|-----------------|-----------|--------------------------|
| **EC2 Instance Role** | `ec2.amazonaws.com` | `s3:Get/Put` (app bucket), CloudWatch Logs, SSM |
| **Lambda Execution Role** | `lambda.amazonaws.com` | DynamoDB, S3 (scoped), SQS receive/delete, SNS publish, RDS connect, Logs |
| **Admin user (you)** | human + MFA | AdministratorAccess (daily use, **not** root) |
| **Developer group** | human + MFA | scoped dev permissions |

**Rule:** enable MFA on the root user and every human user; never use root keys for
daily work. EC2/Lambda authenticate via **roles**, never hardcoded credentials.

---

## 8. Build order — A to Z

Create resources in this exact order — each depends on the ones above it. In the
**console**, follow it strictly to avoid "resource not found" errors. In
**Terraform**, you declare everything and it auto-orders from the references — but
this is the order to build the *modules*.

> **The logic in one line:** Identity → Network → Firewalls → Data → Compute →
> Messaging → Serverless → Monitoring.

### Phase 1 — Account & identity foundation
- **A.** Secure the **root user**; create an **admin IAM user with MFA** (never build on root).
- **B.** Configure the **AWS CLI** (`aws configure`, region `us-west-2`); verify `aws sts get-caller-identity`.
- **C.** Set a **Billing Budget alarm** (e.g., alert at $5) — before creating anything billable.
- **D.** **IAM policies** (customer-managed, least-privilege). *Depends on: nothing.*
- **E.** **IAM roles** — EC2 instance role + Lambda execution role. *Depends on: D. Created now because EC2/Lambda attach them later.*

### Phase 2 — Networking core
- **F.** **VPC** (`10.0.0.0/16`). *The container for everything network-related.*
- **G.** **Subnets** — 2 public + 2 private across two AZs. *Depends on: F.*
- **H.** **Internet Gateway** — create **and attach to the VPC**. *Depends on: F.*
- **I.** **Elastic IP** — for the NAT Gateway. *Must exist before J.*
- **J.** **NAT Gateway** — in a **public** subnet, using the EIP. *Depends on: G, I.*
- **K.** **Route tables** — Public (`0.0.0.0/0 → IGW`) + associate public subnets; Private (`0.0.0.0/0 → NAT`) + associate private subnets. *Depends on: H, J, G.*
- **L.** **VPC Gateway Endpoints** — S3 + DynamoDB (add routes to private route table). *Depends on: K.*

### Phase 3 — Security groups
- **M.** **Security groups** — create all five (`ALB-SG`, `App-SG`, `Bastion-SG`, `DB-SG`, `Lambda-SG`), then add rules. *Depends on: F. Tip: create them empty first, then add rules — they reference each other (circular), so resolve in a second pass.*

### Phase 4 — Data stores
- **N.** **S3 bucket** (versioning, encryption, block public access). *Referenced by Lambda later.*
- **O.** **DynamoDB table** (partition + sort key, GSI). *Referenced by Lambda later.*
- **P.** **RDS** — (1) **DB Subnet Group** spanning both private subnets, then (2) **RDS instance** (Multi-AZ, private, attached to DB-SG). *Depends on: G, M.*

### Phase 5 — Compute & load balancing
- **Q.** **EC2 Launch Template** — AMI, `t3.micro`, App-SG, IAM instance profile (E), user-data. *Depends on: M, E.*
- **R.** **Target Group** — the pool the ALB routes to (health checks). *Depends on: F. Must exist before the ASG registers.*
- **S.** **Application Load Balancer** — in public subnets, ALB-SG, with a **Listener** (80/443) → Target Group. *Depends on: G, M, R.*
- **T.** **Auto Scaling Group** — launches EC2 from the template (Q) into private subnets, attaches to the Target Group (R). *Depends on: Q, R.*
- **U.** **Bastion host (EC2)** — public subnet, Bastion-SG (SSH from your IP only). *Optional but exam-relevant.*

### Phase 6 — Messaging
- **V.** **SQS queue** + a **Dead-Letter Queue (DLQ)**. *Must exist before X and Y.*
- **W.** **SNS topic.**
- **X.** **SNS → SQS subscription** + a **queue policy** allowing SNS to send. *Depends on: V, W.*

### Phase 7 — Serverless wiring
- **Y.** **Lambda functions** — execution role (E), optional VPC config (private subnets + Lambda-SG for RDS), env vars. Then wire triggers: **SQS event source mapping** (V), **S3 notification** (N) + Lambda invoke permission, **SNS publish** permission. *Depends on: E, N, O, P, V, W — which is why Lambda comes near the end.*

### Phase 8 — Observability
- **Z.** **CloudWatch** — log groups, **alarms** (EC2 CPU, RDS connections, SQS depth, Lambda errors), **dashboards**, **VPC Flow Logs**. *Comes last — it monitors everything above.*

**Three "gotcha" dependencies to remember for the exam:**
1. The **IGW must be *attached*** to the VPC (creating it isn't enough).
2. The **NAT needs an Elastic IP** and lives in a **public** subnet.
3. **Security groups reference each other** — create them empty, then add rules.

---

## 9. Terraform module layout

Extend this `terraform-aws-practice` project with these modules (same `enable_*`
toggle pattern), created in the build order above:

| Module | Builds (phase) |
|--------|----------------|
| `modules/iam/` | roles & policies for EC2 and Lambda (D, E) |
| `modules/vpc/` | VPC, subnets, IGW, NAT, route tables, endpoints, Flow Logs (F–L) |
| `modules/security_groups/` | the five tiered SGs with cross-references (M) |
| `modules/s3_bucket/` *(exists)* | S3 bucket (N) |
| `modules/dynamodb_table/` *(exists)* | DynamoDB table (O) |
| `modules/rds/` | DB subnet group + Multi-AZ instance (P) |
| `modules/ec2_asg/` | launch template, ASG, ALB, target group, listener (Q–U) |
| `modules/messaging/` | SNS topic, SQS queue, DLQ, subscription (V–X) |
| `modules/lambda_function/` *(exists)* | Lambda + triggers (Y) |
| *(root)* CloudWatch alarms/log groups | observability (Z) |

---

## 10. Cost, cleanup & certification coverage

**Cost awareness:**
- The main **paid** items are the **NAT Gateway** (~$0.045/hr + data) and **Multi-AZ
  RDS** (single-AZ `db.t3.micro` is Free Tier; Multi-AZ is not).
- EC2 `t3.micro`, S3, DynamoDB, Lambda, SNS, SQS have generous Free Tiers.
- **Set a Billing Budget alarm before you start**, and **`terraform destroy`** when
  you finish practicing to stop all charges.

**Certification coverage:** this architecture maps directly to **Solutions Architect
Associate (SAA-C03)** — VPC, subnets, IGW/NAT, route tables, security groups, ALB,
EC2/ASG, Multi-AZ RDS, S3, DynamoDB, Lambda, SQS/SNS, IAM, VPC endpoints,
CloudWatch. It also covers **Cloud Practitioner** and much of **Developer
Associate**.

---

*Companion projects in this repo: the data-engineering platform (`README.md`), and
reusable modules under `modules/`. Build the blueprint above module-by-module in the
A→Z order to learn each service hands-on.*
