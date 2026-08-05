# AWS Services Explained — Architecture & Real-World Scenarios

Understand the core AWS services, then see how they **combine into real architectures**.
Part 1 is a service catalog (what it is + a real scenario). Part 2 is reference
architectures (how services work together). Part 3 is how to read/design any
architecture.

## Contents
1. [How to think about AWS (the categories)](#1-how-to-think-about-aws)
2. [The services, by category](#2-the-services-by-category)
3. [Reference architectures (real scenarios)](#3-reference-architectures)
4. [How to read & design any architecture](#4-how-to-read--design-any-architecture)

---

## 1. How to think about AWS

AWS has ~200 services, but you only need a core set. Group them into **buckets** — every
architecture is a mix of these:

| Bucket | Question it answers | Key services |
|--------|---------------------|--------------|
| **Compute** | where does my code run? | EC2, Lambda, ECS/EKS/Fargate |
| **Storage** | where do files live? | S3, EBS, EFS |
| **Database** | where does structured data live? | RDS, Aurora, DynamoDB, Redshift, ElastiCache |
| **Networking** | how do things connect / reach users? | VPC, Route 53, CloudFront, ELB, API Gateway |
| **Integration** | how do services talk asynchronously? | SQS, SNS, EventBridge, Step Functions, Kinesis |
| **Security** | who can do what? | IAM, Cognito, KMS, Secrets Manager, WAF |
| **Analytics** | how do I get insight from data? | Athena, Glue, EMR, Redshift, QuickSight |
| **AI/ML** | can it be intelligent? | Textract, Comprehend, Rekognition, Bedrock, SageMaker |
| **Monitoring** | is it healthy / who did what? | CloudWatch, CloudTrail |
| **IaC/DevOps** | how do I build it repeatably? | CloudFormation, Terraform, CodePipeline |

---

## 2. The services, by category

Each: **what it is** → **a real scenario**.

### Compute
- **EC2** — a rented virtual server. *Scenario:* a company hosts its web application on
  EC2 instances it manages (OS, scaling).
- **Lambda** — serverless functions; run only on a trigger, no servers. *Scenario:* the
  instant a photo is uploaded to S3, a Lambda makes a thumbnail. Max 15 min.
- **ECS / EKS / Fargate** — run Docker containers. ECS = AWS's orchestrator, EKS =
  managed Kubernetes, **Fargate** = serverless containers (no servers to manage).
  *Scenario:* a microservices app packaged as containers runs on Fargate so the team
  doesn't manage EC2.
- **Auto Scaling Group (ASG)** — automatically adds/removes EC2 based on load and
  replaces failed ones. *Scenario:* on Black Friday, traffic 10×'s and the ASG adds
  servers, then removes them after.
- **Elastic Load Balancer (ALB/NLB)** — spreads incoming traffic across many servers.
  *Scenario:* the ALB sends users to whichever app server is healthy and least busy.

### Storage
- **S3** — object storage for files, unlimited scale. *Scenario:* Netflix stores video
  files in S3; a data team keeps raw data there as a "data lake."
- **EBS** — a virtual hard disk attached to one EC2 instance; persistent. *Scenario:* the
  database files on an EC2-hosted DB live on an EBS volume.
- **EFS** — shared file storage many EC2 instances mount at once (NFS). *Scenario:* a
  fleet of app servers all read/write the same shared files.
- **Glacier (S3 storage class)** — cheap cold archive. *Scenario:* 7-year compliance log
  retention, rarely accessed.

### Database
- **RDS** — managed relational DB (MySQL/PostgreSQL/etc.); AWS handles backups/patching.
  *Scenario:* the orders/customers database behind an e-commerce app.
- **Aurora** — AWS's high-performance MySQL/PostgreSQL-compatible engine, auto-replicated
  across 3 AZs. *Scenario:* a fast-growing app needing more throughput than plain RDS.
- **DynamoDB** — NoSQL key-value, millisecond latency at any scale. *Scenario:* a
  shopping cart, a game leaderboard, live order status.
- **ElastiCache (Redis/Memcached)** — in-memory cache. *Scenario:* cache DB query
  results so the app is fast and the DB isn't hammered.
- **Redshift** — petabyte-scale data warehouse for analytics. *Scenario:* BI dashboards
  over years of sales data.

### Networking
- **VPC** — your private network (subnets, routing). *Scenario:* a bank isolates its app
  so only a load balancer faces the internet.
- **Subnets (public/private)** — public = internet-facing (load balancer); private =
  hidden (app servers, DB). *Scenario:* app servers and database in private subnets,
  reachable only through the load balancer.
- **Internet Gateway / NAT Gateway** — IGW = the door to the internet; NAT = outbound-only
  internet for private servers. *Scenario:* private servers download patches via NAT but
  can't be reached from outside.
- **Route 53** — DNS + traffic routing. *Scenario:* send European users to the EU region
  (latency routing); fail over to a backup region if the primary is down.
- **CloudFront** — global CDN, caches content at edge locations near users. *Scenario:* a
  static site loads fast worldwide because it's cached near each user.
- **API Gateway** — managed HTTPS front door for APIs (auth, throttling). *Scenario:* the
  entry point for a serverless REST API in front of Lambda.

### Integration & messaging
- **SQS** — a message queue (buffer). *Scenario:* orders drop into a queue and a consumer
  processes them at a safe pace; a spike doesn't crash anything.
- **SNS** — pub/sub; one message fans out to many subscribers. *Scenario:* "order placed"
  notifies the customer, the warehouse, and analytics at once.
- **EventBridge** — event bus with content-based routing. *Scenario:* route different
  event types to different targets automatically.
- **Step Functions** — visual workflow orchestrator for multi-step processes. *Scenario:*
  an order pipeline: validate → charge → ship → notify, with retries per step.
- **Kinesis** — real-time streaming ingestion. *Scenario:* millions of clickstream/IoT
  events per second processed in near real time.

### Security & identity
- **IAM** — who/what can do what (users, groups, roles, policies). *Scenario:* an EC2
  instance assumes a role to read one S3 bucket — no stored keys.
- **Cognito** — user sign-up/sign-in and SSO for your apps. *Scenario:* mobile app user
  login with social/enterprise identity.
- **KMS** — manages encryption keys. *Scenario:* encrypt S3 objects / RDS at rest.
- **Secrets Manager** — stores secrets with rotation. *Scenario:* the DB password,
  fetched at runtime, rotated automatically.
- **WAF / Shield** — web-app firewall + DDoS protection. *Scenario:* block SQL-injection
  and absorb DDoS in front of the ALB/CloudFront.

### Analytics
- **Athena** — serverless SQL over files in S3. *Scenario:* analysts query raw S3 data
  with SQL, pay per query, no DB to load.
- **Glue** — managed Spark ETL + Data Catalog. *Scenario:* nightly job cleans raw data
  into query-ready Parquet (bronze→silver→gold).
- **EMR** — managed Hadoop/Spark clusters for heavy processing. *Scenario:* very large
  custom Spark jobs.
- **QuickSight** — BI dashboards. *Scenario:* business dashboards over Redshift/Athena.

### AI / ML
- **Textract** — extract text/fields from documents. *Scenario:* pull data off scanned
  invoices automatically.
- **Comprehend** — NLP (sentiment, entities, PII). *Scenario:* detect the sentiment of
  customer reviews.
- **Rekognition** — image/video analysis. *Scenario:* verify a photo ID.
- **Bedrock** — generative AI (LLMs). *Scenario:* summarize documents, draft replies,
  build a chatbot.
- **SageMaker** — build/train/deploy custom ML models. *Scenario:* a custom fraud model.

### Monitoring & governance
- **CloudWatch** — metrics, logs, alarms, dashboards. *Scenario:* alarm when CPU >80% or
  the SQS queue backs up.
- **CloudTrail** — audit log of every API call. *Scenario:* "who deleted this bucket?"
- **Config** — tracks resource configuration/compliance over time.

### Infrastructure as Code
- **CloudFormation / CDK / Terraform** — define infrastructure as version-controlled
  code. *Scenario:* one command builds (or destroys) an entire environment reproducibly.

---

## 3. Reference architectures

How the services above combine into real systems. Each shows the flow + when to use it.

### A. Serverless REST API (this repo's Orders API)
```
User ─▶ API Gateway ─▶ Lambda ─▶ DynamoDB
                          └─▶ CloudWatch (logs)
```
**Use when:** you want an API with no servers to manage, pay-per-request, auto-scaling.
**Real scenario:** a mobile app's backend that reads/writes orders.

### B. Classic 3-tier web app (the cert blueprint)
```
User ─▶ Route 53 ─▶ CloudFront ─▶ ALB (public subnet)
                                     └─▶ EC2 Auto Scaling (private) ─▶ RDS Multi-AZ (private)
                                                                        NAT ─▶ internet (outbound)
```
**Use when:** a traditional web application with a relational database.
**Real scenario:** an e-commerce site — load-balanced app servers, private database,
scales on demand, survives an AZ failure.

### C. Event-driven processing (order pipeline)
```
File/Event ─▶ S3 (ObjectCreated) ─▶ Lambda ─▶ DynamoDB
Order event ─▶ SNS ─▶ SQS ─▶ Lambda ─▶ (fulfillment)  [DLQ for failures]
```
**Use when:** react to events, decouple producers/consumers, absorb spikes.
**Real scenario:** an order lands → process it, notify systems, queue fulfillment; a
10,000-order burst is buffered in SQS instead of crashing.

### D. Data lake + analytics (medallion)
```
Raw data ─▶ S3 (bronze) ─▶ Glue Spark ETL ─▶ S3 (silver/gold, Parquet)
                                              └─▶ Glue Catalog ─▶ Athena (SQL)  ─▶ QuickSight
                                                                  Redshift (warehouse)
```
**Use when:** analytics/reporting over large data.
**Real scenario:** clean raw sales files nightly, then let analysts run SQL and dashboards.

### E. Real-time streaming
```
Producers ─▶ Kinesis (stream) ─▶ Lambda / Kinesis Analytics ─▶ DynamoDB / S3
```
**Use when:** high-volume, low-latency event processing.
**Real scenario:** live clickstream or IoT sensor data aggregated in near real time.

### F. Static website + CDN
```
User ─▶ Route 53 ─▶ CloudFront ─▶ S3 (static files)
```
**Use when:** a static site/SPA served fast globally, cheaply.
**Real scenario:** a marketing site or React app, cached at edge locations worldwide.

### G. Intelligent document processing
```
Upload ─▶ S3 ─▶ Lambda ─▶ Textract (extract) ─▶ Comprehend (classify) ─▶ DynamoDB/RDS
```
**Use when:** turn documents into structured data automatically.
**Real scenario:** scanned invoices → extracted fields → stored + routed for approval.

---

## 4. How to read & design any architecture

### The 5-box mental model
Every system, at its core, is:
```
GENERATE ─▶ MOVE ─▶ STORE ─▶ PROCESS ─▶ SERVE
```
When you see (or design) an architecture, drop each service into a box:
- **Generate:** users, apps, IoT, uploads.
- **Move:** API Gateway, Kinesis, SQS/SNS, EventBridge.
- **Store:** S3, RDS, DynamoDB, Redshift.
- **Process:** Lambda, EC2, ECS/Fargate, Glue, EMR, Step Functions.
- **Serve:** ALB/CloudFront to users; Athena/QuickSight to analysts; an API to apps.

### Questions to pick the right service
| Question | If yes → |
|----------|----------|
| Short, event-driven, <15 min? | **Lambda** |
| Long-running / need OS control? | **EC2** (or **Fargate** for containers) |
| Relational data with joins/transactions? | **RDS / Aurora** |
| Simple key lookups at huge scale? | **DynamoDB** |
| Files/objects? | **S3** |
| Query files with SQL, no DB? | **Athena** |
| Petabyte reporting? | **Redshift** |
| Decouple / buffer / retry? | **SQS** (+ **SNS** to fan out) |
| Serve globally & fast? | **CloudFront** |
| Must not be public? | **private subnet** + no public IP |

### The security defaults to always apply
- Only load balancers/NAT/bastion in **public** subnets; app + DB in **private**.
- **IAM roles** for services (no static keys); **least privilege**.
- Encrypt at rest (**KMS/SSE**) and in transit (**TLS**).
- Secrets in **Secrets Manager**; monitor with **CloudWatch**; audit with **CloudTrail**.

### The cost instincts
- Paid-by-the-hour (EC2, NAT, ALB, RDS) vs pay-per-use (Lambda, S3, DynamoDB on-demand,
  Athena per-TB). Prefer serverless for spiky/low workloads; destroy what you don't need.

---

*Pair this with [aws-certification-qa.md](aws-certification-qa.md) (Q&A) and
[services-scenarios-and-troubleshooting.md](services-scenarios-and-troubleshooting.md)
for the services you've built hands-on.*
