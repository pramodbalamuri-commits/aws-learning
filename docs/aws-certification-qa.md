# AWS Certification — Complete Q&A (SAA-focused)

Exam-style questions and answers across every core AWS domain, tied to the
architecture in this repo where relevant. Use it for self-testing: cover the
answer, say it out loud, then check.

## Contents
1. [VPC & Networking](#1-vpc--networking)
2. [EC2 & Compute](#2-ec2--compute)
3. [Load Balancing & Auto Scaling](#3-load-balancing--auto-scaling)
4. [Storage (S3, EBS, EFS)](#4-storage-s3-ebs-efs)
5. [Databases (RDS, Aurora, DynamoDB)](#5-databases-rds-aurora-dynamodb)
6. [IAM & Security](#6-iam--security)
7. [Serverless (Lambda, API Gateway)](#7-serverless-lambda-api-gateway)
8. [Messaging (SQS, SNS, EventBridge)](#8-messaging-sqs-sns-eventbridge)
9. [Monitoring (CloudWatch, CloudTrail)](#9-monitoring-cloudwatch-cloudtrail)
10. [High Availability, DR & Cost](#10-high-availability-dr--cost)
11. [DNS & Content Delivery (Route 53, CloudFront)](#11-dns--content-delivery-route-53-cloudfront)
12. [Containers (ECS, EKS, Fargate, ECR)](#12-containers-ecs-eks-fargate-ecr)
13. [Which service would you choose? (scenarios)](#13-which-service-would-you-choose-scenarios)

---

## 1. VPC & Networking

**Q: What makes a subnet "public" vs "private"?**
A: The route table. A public subnet has a route `0.0.0.0/0 → Internet Gateway`; a private subnet routes `0.0.0.0/0 → NAT Gateway` (or has no internet route). Nothing else about the subnet is different.

**Q: Internet Gateway vs NAT Gateway — what's the difference?**
A: An **Internet Gateway (IGW)** allows two-way internet access for resources with public IPs (in public subnets). A **NAT Gateway** allows **outbound-only** internet for resources in private subnets — they can reach out (patches, APIs) but the internet cannot initiate a connection to them. NAT lives in a public subnet and forwards to the IGW.

**Q: Security Group vs Network ACL (NACL) — compare them.**
A:
| | Security Group | NACL |
|--|----------------|------|
| Level | instance/ENI | subnet |
| State | **stateful** (return traffic auto-allowed) | **stateless** (must allow return traffic explicitly) |
| Rules | allow only | allow **and** deny |
| Evaluation | all rules evaluated | rules in **number order**, first match wins |
Default: SGs deny all inbound / allow all outbound; the default NACL allows all.

**Q: Why use a VPC Gateway Endpoint for S3/DynamoDB?**
A: It lets private resources reach S3/DynamoDB over the AWS backbone instead of the internet/NAT — cheaper (no NAT data charges) and more secure (traffic never leaves AWS). It's added as a route (prefix list) in the private route table. Gateway endpoints are free and only for S3 & DynamoDB; other services use Interface endpoints (PrivateLink, hourly cost).

**Q: Gateway endpoint vs Interface endpoint?**
A: **Gateway** = route-table target, free, only S3 & DynamoDB. **Interface** = an ENI with a private IP (PrivateLink), works for most services (Glue, Kinesis, Secrets Manager…), costs hourly + per-GB.

**Q: How many IPs does AWS reserve in each subnet?**
A: 5 — network address, VPC router, DNS, future use, and broadcast. So a /24 (256) gives 251 usable IPs.

**Q: Can a security group reference another security group?**
A: Yes — and you should. E.g., the DB-SG allows the DB port *from the App-SG* (not an IP range). This creates a chain of trust and survives IP changes.

**Q: VPC Peering — key limitation?**
A: It's **not transitive** — if A peers with B and B peers with C, A cannot reach C. Also CIDRs must not overlap. For many-VPC topologies use a **Transit Gateway** instead.

**Q: What is a bastion host and why use one?**
A: A hardened EC2 in a public subnet used as the single controlled entry point to SSH into private instances. Its SG allows SSH only from your IP. (Modern alternative: SSM Session Manager — no bastion, no open SSH port.)

**Q: How do private instances get software updates with no inbound internet?**
A: Through the NAT Gateway (outbound-only) — the private route table sends `0.0.0.0/0 → NAT`.

---

## 2. EC2 & Compute

**Q: What are the EC2 purchasing options and when to use each?**
A: **On-Demand** (pay per second, no commitment — spiky/unknown workloads); **Reserved/Savings Plans** (1–3 yr commitment, big discount — steady workloads); **Spot** (up to 90% off, can be reclaimed with 2-min notice — fault-tolerant/batch); **Dedicated Hosts/Instances** (compliance/licensing).

**Q: What's an AMI?**
A: Amazon Machine Image — the template (OS + config) an instance launches from. Region-specific. Best practice: look up the latest via a data source rather than hardcoding an ID (which goes stale).

**Q: Launch Template vs Launch Configuration?**
A: Launch **Template** is the newer, versioned, feature-rich option (supports mixed instances, T2/T3 unlimited, etc.). Launch Configuration is legacy and immutable. Always prefer Launch Templates (this repo uses one).

**Q: What is user data?**
A: A script that runs once at first boot to bootstrap the instance (e.g., install Apache). In this repo the ASG's launch template installs a web server via user data.

**Q: Instance store vs EBS?**
A: **Instance store** = physically attached, ephemeral (lost on stop/terminate), very fast. **EBS** = network-attached, persistent, survives stop/start, can be snapshotted. Use EBS for anything you need to keep.

**Q: What is an instance profile?**
A: The wrapper that attaches an IAM **role** to an EC2 instance, so the instance can call AWS APIs using temporary credentials — no access keys stored on the box.

---

## 3. Load Balancing & Auto Scaling

**Q: ALB vs NLB vs CLB — when to use which?**
A: **ALB** (Layer 7/HTTP-HTTPS) — path/host routing, web apps, containers (this repo). **NLB** (Layer 4/TCP-UDP) — ultra-high throughput, static IP, low latency, non-HTTP. **CLB** (Classic) — legacy, avoid for new work.

**Q: What is a Target Group?**
A: The set of targets (EC2/IP/Lambda) an ALB routes to, with its own health checks. The Auto Scaling Group registers its instances into the target group.

**Q: How does the ALB know an instance is healthy?**
A: Health checks — it hits a path (e.g., `/`) and expects a success code (e.g., 200). Unhealthy targets stop receiving traffic. If you see 502/503, targets are failing health checks.

**Q: What does an Auto Scaling Group give you?**
A: Automatic replacement of failed instances (maintains desired capacity) + scaling in/out on demand or metrics (e.g., CPU). Spread across multiple AZs/subnets for HA.

**Q: Difference between scaling policies?**
A: **Target tracking** (keep a metric at a target, e.g., CPU 50% — simplest); **Step scaling** (add N instances at metric thresholds); **Scheduled** (scale at known times). **Dynamic** reacts to load; **predictive** uses ML on history.

**Q: ASG health check types?**
A: `EC2` (instance status only) or `ELB` (also considers load-balancer health checks — use this when behind an ALB, as this repo does, so a running-but-unhealthy app gets replaced).

---

## 4. Storage (S3, EBS, EFS)

**Q: Walk through the S3 storage classes.**
A: **Standard** (hot, frequent); **Intelligent-Tiering** (auto-moves by access pattern); **Standard-IA / One Zone-IA** (infrequent, cheaper storage, retrieval fee); **Glacier Instant / Flexible / Deep Archive** (archive, retrieval seconds→hours). Lifecycle rules transition objects automatically.

**Q: How do you secure an S3 bucket?**
A: Block Public Access (account + bucket), encrypt at rest (SSE-S3 or SSE-KMS) and in transit (TLS), disable ACLs (bucket-owner-enforced) so access is IAM-driven, apply least-privilege bucket/IAM policies, enable versioning + logging.

**Q: S3 vs EBS vs EFS?**
A: **S3** = object storage, accessed via API, unlimited, for files/data lakes/backups. **EBS** = block storage, one instance at a time (or Multi-Attach for io2), like a virtual disk. **EFS** = shared file storage (NFS) mountable by many instances at once across AZs.

**Q: What is S3 versioning good for?**
A: Recovering from accidental overwrite/delete — every version is kept. Pair with lifecycle rules to expire old versions and control cost.

**Q: EBS volume types?**
A: **gp3/gp2** (general SSD — default), **io1/io2** (provisioned IOPS SSD — high-performance DBs), **st1** (throughput HDD — big sequential), **sc1** (cold HDD — cheapest). gp3 lets you set IOPS/throughput independently of size.

**Q: How do you back up EBS?**
A: **Snapshots** (incremental, stored in S3, region-scoped; copy across regions for DR). Automate with Data Lifecycle Manager.

---

## 5. Databases (RDS, Aurora, DynamoDB)

**Q: Multi-AZ vs Read Replica — don't confuse these.**
A: **Multi-AZ** = a **standby** copy in another AZ for **high availability**; synchronous; automatic failover; you do NOT read from it. **Read Replica** = extra copies for **read scaling**; asynchronous; you DO read from them; can be cross-region. One is for availability, the other for performance.

**Q: Why put RDS in a private subnet with `publicly_accessible = false`?**
A: A database should never be reachable from the internet. It's accessed only from the app tier (DB-SG allows the app SG on the DB port). This is a core security/exam principle.

**Q: What is Aurora and why choose it over RDS?**
A: AWS's cloud-native MySQL/PostgreSQL-compatible engine with a distributed storage layer replicated 6 ways across 3 AZs. Higher throughput, faster failover (<30s), up to 15 low-lag read replicas. Aurora Serverless v2 auto-scales capacity for variable workloads.

**Q: When do you pick DynamoDB over RDS?**
A: DynamoDB (NoSQL) when you have well-known, simple access patterns needing massive scale and single-digit-ms latency (carts, sessions, IoT, the Orders table here). RDS (relational) when you need complex joins, transactions, and flexible ad-hoc queries.

**Q: DynamoDB partition key design — how to avoid a "hot partition"?**
A: Choose a high-cardinality, evenly-distributed partition key so traffic spreads across partitions. A low-cardinality key (e.g., `status`) concentrates load and throttles.

**Q: What's a DynamoDB GSI vs LSI?**
A: **GSI** = different partition + sort key, added anytime, own capacity — supports new query patterns (e.g., query orders by `customer_id`). **LSI** = same partition key, different sort key, must be created at table creation.

**Q: How does RDS handle the master password securely here?**
A: `manage_master_user_password = true` — RDS creates and rotates the password in **Secrets Manager**, so it never appears in Terraform state.

---

## 6. IAM & Security

**Q: User vs Role — the one-line difference?**
A: A **user** is a permanent identity you log in as (long-lived credentials); a **role** is assumed temporarily by a service or another account for short-lived credentials. Prefer roles for anything non-human.

**Q: The four IAM building blocks?**
A: **Policy** (JSON of allowed/denied actions), **User** (a person/app), **Group** (a set of users; attach policies here), **Role** (assumed temporarily). Attach policies to groups/roles, not individual users.

**Q: Identity-based vs resource-based policy?**
A: **Identity-based** attaches to a user/group/role (what *they* can do). **Resource-based** attaches to a resource (e.g., S3 bucket policy, SQS queue policy) and says *who* can access it — required for cross-account access.

**Q: What is a role's "trust policy"?**
A: The `assume_role_policy` that says **who may assume the role** (e.g., `ec2.amazonaws.com` or `lambda.amazonaws.com`). Separate from the permission policies (what the role can do once assumed). Debug tip: "can't assume role" = trust policy issue; "assumed but access denied" = permission policy issue.

**Q: SSE-S3 vs SSE-KMS?**
A: Both encrypt at rest. **SSE-S3** = AWS manages the key entirely. **SSE-KMS** = you manage the key in KMS, get an audit trail (CloudTrail) and can control who can decrypt (`kms:Decrypt`) — a second access-control layer beyond S3 permissions.

**Q: What is the principle of least privilege?**
A: Grant every identity only the permissions it actually needs. This repo's roles are scoped to specific buckets/tables/queues rather than `*`.

**Q: KMS vs Secrets Manager vs Parameter Store?**
A: **KMS** = manages encryption keys. **Secrets Manager** = stores secrets (DB passwords, API keys) with **automatic rotation**. **SSM Parameter Store** = config + secrets (SecureString), cheaper, no built-in rotation.

**Q: Why should you not use the root user day-to-day?**
A: Root has unrestricted power and can't be limited by IAM policies. Lock it with MFA, use it only for the few root-only tasks, and do daily work as an admin IAM user.

---

## 7. Serverless (Lambda, API Gateway)

**Q: What is AWS Lambda and its key limits?**
A: Serverless functions that run on triggers; you pay per invocation + duration. Max **15-minute** timeout, up to 10 GB memory, 512 MB–10 GB `/tmp`. For longer/bigger work use ECS/Fargate/EMR.

**Q: How does an S3 upload trigger a Lambda? What does the event contain?**
A: S3 sends an `ObjectCreated` event notification. The event contains **only the bucket name + object key** (metadata) — *not* the file contents — so the Lambda must call `s3:GetObject` to read the file. That's why the function's role needs `s3:GetObject` (the exact pattern in this repo's order-processor).

**Q: Lambda vs EC2 vs Glue for processing?**
A: **Lambda** = short, event-driven tasks (<15 min, no server). **EC2** = long-running general compute you manage. **Glue** = large distributed Spark ETL. Right tool per job.

**Q: How does Lambda get permission to write to DynamoDB?**
A: It assumes an **execution role** whose policy allows `dynamodb:PutItem` on that table — no keys.

**Q: When would you put a Lambda inside a VPC?**
A: When it must reach private resources like RDS. It gets an ENI in your private subnets. Note: a VPC Lambda reaches S3/DynamoDB via endpoints and the internet only via NAT.

**Q: What does API Gateway add in front of Lambda?**
A: A managed HTTP entry point — auth (IAM/Cognito/keys), throttling/usage plans, request validation, stages. Turns a Lambda into a real REST/HTTP API.

---

## 8. Messaging (SQS, SNS, EventBridge)

**Q: SQS vs SNS?**
A: **SQS** = a **queue** (pull); one consumer group processes each message; buffers load. **SNS** = **pub/sub** (push); fans a message out to many subscribers at once. Common combo: SNS → multiple SQS queues (fan-out), each processed independently.

**Q: Standard vs FIFO queue?**
A: **Standard** = near-unlimited throughput, at-least-once delivery, best-effort ordering. **FIFO** = exactly-once, strict ordering, lower throughput. Use FIFO only when order/dedup matters.

**Q: What is a Dead-Letter Queue (DLQ)?**
A: A queue that receives messages which fail processing after N attempts (`maxReceiveCount`), so bad messages don't block the main queue and can be inspected/replayed. This repo wires a DLQ via the redrive policy.

**Q: What is visibility timeout?**
A: When a consumer receives a message, it's hidden from others for the visibility timeout; if not deleted in time it reappears (retry). Set it a bit longer than your processing time to avoid duplicate processing.

**Q: Why decouple with SQS between producer and consumer?**
A: Resilience + scale — if the consumer is slow/down, messages wait safely in the queue instead of being lost, and you can process a spike (e.g., 10,000 orders) at a controlled pace.

**Q: EventBridge vs SNS?**
A: **EventBridge** = event bus with rich content-based routing/filtering, schema registry, many SaaS/AWS event sources, scheduling. **SNS** = simpler high-throughput pub/sub. Use EventBridge for event-driven app integration and routing rules.

**Q: How do you let SNS send to an SQS queue?**
A: A **queue policy** (resource-based) that allows `sns.amazonaws.com` to `SendMessage`, scoped with a condition `aws:SourceArn = <topic ARN>` (this repo does exactly that).

---

## 9. Monitoring (CloudWatch, CloudTrail)

**Q: CloudWatch vs CloudTrail?**
A: **CloudWatch** = performance monitoring — metrics, logs, alarms, dashboards ("is it healthy?"). **CloudTrail** = audit log of API calls — who did what, when ("who deleted this?"). Different jobs; you usually enable both.

**Q: What are the CloudWatch pieces?**
A: **Metrics** (numeric time series), **Alarms** (fire when a metric crosses a threshold → notify/act), **Logs** (log groups/streams), **Dashboards**, **Events/EventBridge** (react to events). This repo alarms on ASG CPU, RDS connections, SQS depth, Lambda errors.

**Q: What are VPC Flow Logs?**
A: Records of accepted/rejected traffic in your VPC (to CloudWatch/S3) — great for security analysis and debugging "why can't X reach Y?". Optional in this repo's VPC module.

**Q: How do you get notified when an alarm fires?**
A: The alarm's `alarm_actions` publish to an **SNS topic**; subscribers (email/SMS/Lambda) get notified. This repo creates an alarm SNS topic with an optional email subscription.

**Q: Custom metrics — how?**
A: Push with the CloudWatch agent or `PutMetricData` (e.g., app-level business metrics). Standard resolution 1-min; high-resolution down to 1-sec.

---

## 10. High Availability, DR & Cost

**Q: Region vs Availability Zone vs Edge Location?**
A: **Region** = geographic area (e.g., us-west-2). **AZ** = one or more isolated data centers within a region (design across ≥2 for HA). **Edge Location** = CloudFront CDN/caching point of presence, closer to users.

**Q: How do you make an app highly available in this architecture?**
A: Two AZs, subnets in each, Auto Scaling Group spread across them, Multi-AZ RDS, and an ALB that health-checks and routes only to healthy targets. Losing one AZ doesn't take the app down.

**Q: The four DR strategies (increasing cost/speed)?**
A: **Backup & Restore** (cheapest, slowest RTO) → **Pilot Light** (core running, scale up on failover) → **Warm Standby** (scaled-down full copy running) → **Multi-Site Active/Active** (fastest, most expensive). Choose based on RTO/RPO.

**Q: RTO vs RPO?**
A: **RTO** = Recovery Time Objective — how long until you're back up. **RPO** = Recovery Point Objective — how much data you can afford to lose (how far back the last good backup is).

**Q: Biggest cost levers in this architecture?**
A: **NAT Gateway** and **Multi-AZ RDS** and the **ALB** are the paid items. Use a single NAT for learning, single-AZ RDS for Free Tier, VPC endpoints to cut NAT data cost, Spot for ASG batch, and **destroy** when done. Always set a Billing Budget alarm.

**Q: How do you reduce data-transfer cost to S3/DynamoDB from a VPC?**
A: Use **Gateway VPC Endpoints** — traffic skips the NAT (no per-GB NAT charge) and stays on the AWS backbone.

**Q: Scaling up vs scaling out?**
A: **Up (vertical)** = bigger instance — simple, has a ceiling, usually needs downtime. **Out (horizontal)** = more instances behind a load balancer — resilient and near-limitless; the cloud-preferred approach (what the ASG does here).

---

---

## 11. DNS & Content Delivery (Route 53, CloudFront)

**Q: What is Route 53?**
A: AWS's managed DNS + domain registration + health-checking service. It maps domain
names to resources (like an ALB or CloudFront) and can route traffic intelligently.

**Q: Alias record vs CNAME — when to use which?**
A: An **Alias** is an AWS-specific record that points a name at an AWS resource (ALB,
CloudFront, S3 website) — it works at the **zone apex** (e.g., `example.com`) and is
**free**. A **CNAME** points one name at another name, but **cannot** be used at the
apex. Rule: use Alias for AWS targets, especially the apex.

**Q: Route 53 routing policies — name them and when to use each.**
A:
| Policy | Use when |
|--------|----------|
| **Simple** | one resource, no logic |
| **Weighted** | split traffic by % (A/B tests, canary) |
| **Latency** | send users to the lowest-latency region |
| **Failover** | active/passive DR (primary → standby on health-check fail) |
| **Geolocation** | route by user's country/continent (compliance, localization) |
| **Geoproximity** | route by geographic distance, with a bias to shift traffic |
| **Multivalue answer** | return several healthy IPs (simple client-side balancing) |

**Q: What is CloudFront?**
A: A global CDN (content delivery network). It caches your content at **edge
locations** near users, so a viewer in Tokyo is served from a nearby edge instead of
your origin in Virginia — lower latency, less origin load, DDoS protection (Shield).

**Q: What can be a CloudFront origin?**
A: S3 (static sites/assets), an ALB/EC2 (dynamic apps), or any custom HTTP origin.

**Q: How do you keep an S3 bucket private but still serve it via CloudFront?**
A: Use **Origin Access Control (OAC)** (the modern replacement for OAI) — CloudFront is
the only thing allowed to read the bucket; the bucket stays fully private (block public
access on). Viewers hit CloudFront, never S3 directly.

**Q: CloudFront vs S3 Transfer Acceleration?**
A: **CloudFront** caches content close to users for downloads/reads. **S3 Transfer
Acceleration** speeds **uploads** to S3 by routing through the nearest edge to the
bucket's region. Different directions.

**Q: How do you serve private/paid content through CloudFront?**
A: **Signed URLs** (single file) or **signed cookies** (multiple files) — time-limited,
optionally IP-restricted access.

**Q: CloudFront vs Global Accelerator?**
A: **CloudFront** caches HTTP(S) content at the edge (web/media). **Global Accelerator**
gives you 2 static anycast IPs and routes **any TCP/UDP** traffic over the AWS backbone
to the nearest healthy endpoint (non-HTTP apps, fast failover, gaming/VoIP). No caching.

**Q: What TTL controls in CloudFront?**
A: How long an object stays cached at the edge before CloudFront re-checks the origin.
Longer TTL = fewer origin hits but staler content; use cache invalidations or versioned
object names to push updates.

---

## 12. Containers (ECS, EKS, Fargate, ECR)

**Q: ECS vs EKS?**
A: Both run Docker containers. **ECS** = AWS's own simpler container orchestrator (less
to learn, tightly integrated). **EKS** = managed **Kubernetes** (industry-standard,
portable across clouds, more complex). Pick ECS for simplicity on AWS; EKS if you want
Kubernetes/portability or already use it.

**Q: What is Fargate?**
A: A **serverless** compute engine for containers — you run containers **without
managing EC2 servers**. Works with both ECS and EKS. You define CPU/memory per task and
AWS runs it. Alternative to the "EC2 launch type" where you manage the instances.

**Q: Fargate vs EC2 launch type — when to use each?**
A: **Fargate** = no servers to manage, pay per task, great for variable/bursty
workloads and teams that don't want ops overhead. **EC2 launch type** = you manage the
instances, cheaper at scale, needed for GPU/special instances or fine-grained control.

**Q: What is ECR?**
A: Elastic Container Registry — AWS's private Docker image registry (like Docker Hub).
Your build pipeline pushes images here; ECS/EKS pull from it.

**Q: What is a task definition vs a service (ECS)?**
A: A **task definition** is the blueprint for a container (image, CPU/mem, ports, env,
role). A **service** keeps a desired number of tasks running (like an ASG for
containers) and integrates with an ALB.

**Q: Containers vs Lambda vs EC2 — how to choose?**
A: **Lambda** = short event-driven functions (<15 min), zero servers. **Containers
(Fargate)** = longer-running or existing containerized apps, still serverless-ish.
**EC2** = full control, long-running, special hardware. Move up the list as you need
more control/runtime.

**Q: How does the food-delivery lab (in the other doc) relate to EKS?**
A: That lab runs Airflow/Spark on Kubernetes locally; on AWS the same thing is
**EKS + Fargate** (or EMR-on-EKS). The patterns transfer directly.

---

## 13. Which service would you choose? (scenarios)

Read the scenario, pick the service, then check.

| Scenario | Choose | Why |
|----------|--------|-----|
| Run a container without managing any servers | **Fargate** | serverless containers |
| Store user session / shopping cart, ms latency, huge scale | **DynamoDB** (or ElastiCache) | NoSQL key-value, fast |
| Decouple two microservices so one can be down | **SQS** | queue buffers + retries |
| Notify many systems of one event at once | **SNS** | pub/sub fan-out |
| Route an event to different targets by its content | **EventBridge** | content-based routing rules |
| Relational DB with minimal operational work | **RDS / Aurora** | managed relational |
| Serve a static website globally with low latency | **S3 + CloudFront** | object store + CDN |
| Run a 20-minute batch job | **Fargate / AWS Batch / EC2** | Lambda caps at 15 min |
| Run code on an S3 upload | **Lambda** (S3 trigger) | event-driven, serverless |
| Big distributed Spark ETL over TBs | **Glue / EMR** | managed Spark |
| Query files in S3 with SQL, no DB to load | **Athena** | serverless SQL over S3 |
| Cache DB reads to cut latency | **ElastiCache (Redis/Memcached)** | in-memory cache |
| Central place for secrets with auto-rotation | **Secrets Manager** | rotation built in |
| Give an EC2 app access to S3 without keys | **IAM role (instance profile)** | temp credentials |
| Send app traffic to lowest-latency region | **Route 53 latency routing** | DNS-based |
| Give private instances outbound internet only | **NAT Gateway** | outbound-only |
| Connect a VPC privately to S3 (skip NAT) | **S3 Gateway Endpoint** | private + free |
| Petabyte-scale data warehouse for BI | **Redshift** | columnar MPP warehouse |
| Stream millions of events/sec for real-time processing | **Kinesis / MSK** | streaming ingestion |
| Highly available relational DB with auto failover | **RDS Multi-AZ** (or Aurora) | standby + failover |
| Scale relational reads across many replicas | **Read Replicas** (Aurora up to 15) | read scaling |
| Non-HTTP (TCP) app needing a static IP + fast failover | **NLB** (+ Global Accelerator) | L4, static IP |
| Path/host-based routing for a web app | **ALB** | L7 routing |
| Long-term archive of logs, rarely accessed | **S3 Glacier Deep Archive** | cheapest storage |
| Shared file system mounted by many EC2 at once | **EFS** | multi-attach NFS |
| Audit who made an API call and when | **CloudTrail** | API audit log |
| Alert when CPU/queue-depth crosses a threshold | **CloudWatch Alarm → SNS** | metric monitoring |
| Infrastructure defined as reusable code | **Terraform / CloudFormation / CDK** | IaC |

---

*Keep testing yourself against these. For deeper dives, see the other PDFs in this
folder and [`../BLUEPRINT.md`](../BLUEPRINT.md).*
