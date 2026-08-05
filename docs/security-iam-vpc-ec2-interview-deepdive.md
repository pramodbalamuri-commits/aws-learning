# Security, IAM, VPC & EC2 — Interview Deep Dive

Everything you need to explain **networking, subnets, EC2, IAM, and security** in an
interview — in plain language, with examples you can say out loud, interview Q&A, and
real-world exceptions with resolutions.

## Contents
1. [VPC & Networking (incl. public/private subnets)](#part-1--vpc--networking)
2. [EC2](#part-2--ec2)
3. [IAM](#part-3--iam)
4. [Security (encryption, secrets, WAF)](#part-4--security)
5. *(covered above)*
6. [The other core services — S3, RDS, DynamoDB, Lambda, API Gateway, SQS/SNS, Glue/Athena, CloudWatch](#part-6--the-other-core-services-deep-dive)
7. [Interview "tell me about…" answers](#part-7--interview-tell-me-about-answers)

---

# Part 1 — VPC & Networking

## 1.1 VPC — your private network
A **VPC** is your own isolated network inside AWS. Think of it as a **private office
building** with its own address range (`10.0.0.0/16`). Nothing inside is reachable from
the internet unless you deliberately open a door.

*Say it in an interview:* "A VPC is a logically isolated network where I control the IP
range, subnets, routing, and what's exposed to the internet."

## 1.2 CIDR — the address range
`10.0.0.0/16` means the first 16 bits are fixed → **65,536 IP addresses** (`10.0.0.0` to
`10.0.255.255`). A `/24` subnet = 256 addresses (AWS reserves 5, so 251 usable). Smaller
number after `/` = bigger network.

## 1.3 Public vs Private Subnets — THE key concept

A subnet is just a slice of the VPC's IPs in **one Availability Zone**. What makes it
"public" or "private" is **one thing: its route table.**

| | Public subnet | Private subnet |
|--|---------------|----------------|
| Route for `0.0.0.0/0` | → **Internet Gateway** | → **NAT Gateway** (or none) |
| Reachable from internet? | yes (if it has a public IP) | **no** |
| What goes here | load balancer, NAT gateway, bastion | app servers, databases |

**The mental model:** public subnet = building **lobby** (street access); private subnet
= **back offices** (no street access, but staff can still go out the back via the NAT).

**Why put app servers and databases in private subnets?**
- **Security:** they can't be reached from the internet at all — even if someone knows
  the IP, there's no route to them. Only the load balancer (public) is exposed.
- **Defense in depth:** if the app tier is compromised, the attacker still can't reach
  the database directly from the internet.
- **This is the #1 tested design principle:** *only load balancers, NAT gateways, and
  bastion hosts go in public subnets; app servers and databases go in private.*

*Say it in an interview:* "I keep the load balancer in a public subnet and the app
servers and database in private subnets. Users hit the load balancer; it forwards to
private app servers, which talk to a private database. The database is never exposed to
the internet — that's the core of a secure, well-architected VPC."

## 1.4 Route tables — the signposts
A route table decides where traffic goes. Public route table says "internet →
Internet Gateway"; private route table says "internet → NAT Gateway." You **associate**
subnets to route tables — that association is what makes a subnet public or private.

## 1.5 Internet Gateway vs NAT Gateway
- **Internet Gateway (IGW):** the **front door** — two-way internet for resources with
  public IPs (in public subnets).
- **NAT Gateway:** a **one-way exit** — lets private resources reach *out* (patches,
  APIs) but the internet **cannot** initiate a connection *in*. It sits in a public
  subnet and forwards to the IGW.

*Example:* "My private EC2 instances download OS updates through the NAT gateway, but
nothing on the internet can start a connection to them."

## 1.6 Security Groups vs NACLs — know this cold

| | **Security Group** | **Network ACL (NACL)** |
|--|--------------------|------------------------|
| Attached to | instance / ENI | the whole subnet |
| Stateful? | **Yes** (reply traffic auto-allowed) | **No** (must allow return traffic explicitly) |
| Rules | **allow only** | allow **and deny** |
| Evaluation | all rules together | in **number order**, first match wins |
| Typical use | primary firewall (per tier) | coarse subnet-level allow/deny |

**Best practice:** reference **other security groups** as the source, not IP ranges. E.g.
the DB security group allows the database port **from the app security group** — so only
the app tier can reach the DB, and it survives IP changes.

*Say it in an interview:* "Security groups are my main firewall — stateful, instance-level,
allow-only. I chain them: the app SG allows traffic only from the ALB SG, and the DB SG
allows the database port only from the app SG. NACLs are a stateless, subnet-level second
layer I use for coarse deny rules."

## 1.7 VPC Endpoints — private access to AWS services
Normally reaching S3/DynamoDB from a private subnet goes out via the NAT. A **Gateway VPC
Endpoint** creates a **private path** to S3/DynamoDB over the AWS backbone — cheaper (no
NAT data charge) and more secure. Other services use **Interface Endpoints** (PrivateLink).

## 1.8 VPC Peering & Transit Gateway
- **Peering:** connect two VPCs privately. Gotcha: **not transitive** (A–B and B–C does
  not give A–C) and CIDRs can't overlap.
- **Transit Gateway:** a hub that connects many VPCs (and on-prem) — use it instead of a
  mesh of peerings.

## 1.9 Bastion host & SSM
- **Bastion host:** a hardened EC2 in a public subnet, the single controlled way to SSH
  into private instances (SSH allowed only from your IP).
- **SSM Session Manager (modern):** connect to private instances **without** a bastion or
  any open SSH port — more secure, audited. Prefer this.

## Interview Q&A — Networking

**Q: What's the difference between a public and private subnet?**
A: The route table. Public routes internet traffic to an Internet Gateway; private routes
it to a NAT gateway (or nowhere). Public holds the load balancer/NAT/bastion; private
holds app servers and databases.

**Q: How does a private EC2 instance get internet access?**
A: Through a NAT gateway (outbound-only). The private route table sends `0.0.0.0/0` to the
NAT, which forwards to the Internet Gateway. The internet can't start a connection inbound.

**Q: Security Group vs NACL?**
A: SG = stateful, instance-level, allow-only, all rules evaluated. NACL = stateless,
subnet-level, allow+deny, ordered rules. SGs are the primary firewall; NACLs a secondary
subnet layer.

**Q: How do you let the app tier talk to the DB but nothing else?**
A: The DB security group allows the database port **only from the app tier's security
group** (referencing the SG, not an IP). RDS stays in a private subnet, not publicly
accessible.

**Q: How do you connect to a private instance securely without a bastion?**
A: AWS Systems Manager **Session Manager** — no open SSH port, no public IP, fully audited
in CloudTrail.

## Real-World Exceptions & Resolutions — Networking

| Problem | Cause | Resolution |
|---------|-------|------------|
| Private instance can't reach the internet | no NAT route | private route table needs `0.0.0.0/0 → NAT`; NAT must be in a public subnet with a route to the IGW |
| Can't SSH to an instance | SG doesn't allow port 22 from your IP, or no public IP/route | open 22 from your IP in the SG; ensure public subnet + IGW, or use SSM |
| App can't reach RDS | DB SG doesn't allow the app SG on the DB port | add an inbound rule on DB-SG: port 3306/5432 from the app SG |
| "Route already exists" | duplicate `0.0.0.0/0` in the route table | remove/replace the existing default route |
| NAT create fails | no Elastic IP | allocate an EIP first, then the NAT |
| Can't reach S3 from private subnet | traffic has no path | add an S3 Gateway Endpoint to the private route table (or verify NAT) |
| Two VPCs can't talk through a third | peering isn't transitive | peer them directly or use a Transit Gateway |

---

# Part 2 — EC2

## 2.1 What is EC2
A **rented virtual server** in the cloud. You choose the OS (via an AMI), the size
(instance type), and manage it. *Example:* "We host our application on EC2 instances
behind a load balancer."

## 2.2 Instance types & purchasing options
- **Types:** families for general (t/m), compute (c), memory (r), etc. `t3.micro` is a
  small burstable/Free-Tier type.
- **Purchasing:**
  - **On-Demand** — pay per second, no commitment → spiky/unknown workloads.
  - **Reserved / Savings Plans** — 1–3 yr commit, big discount → steady workloads.
  - **Spot** — up to 90% off, can be reclaimed with 2-min notice → fault-tolerant/batch.
  - **Dedicated** — compliance/licensing.

*Say it in an interview:* "I use On-Demand for variable load, Reserved/Savings Plans for
steady baseline, and Spot for fault-tolerant batch to cut cost up to 90%."

## 2.3 AMI, launch template, user data
- **AMI** = the image (OS + config) an instance boots from; region-specific — look up the
  latest rather than hardcoding.
- **Launch Template** = the reusable blueprint (AMI, type, SG, IAM role, user data) —
  newer than launch configs; use it.
- **User data** = a script that runs once at first boot (e.g., install a web server).

## 2.4 Auto Scaling & Load Balancing
- **Auto Scaling Group (ASG):** keeps the desired number of instances, replaces failed
  ones, scales in/out on metrics or schedule, across multiple AZs.
- **ALB (Application Load Balancer):** Layer-7 (HTTP), path/host routing, health checks —
  the public entry point that forwards to private instances.
- **Health-check type = ELB** (not just EC2) so a running-but-unhealthy app gets replaced.

*Example:* "On Black Friday the ASG scales from 2 to 10 instances on CPU, and the ALB
routes only to healthy targets. If an instance dies, the ASG replaces it automatically."

## 2.5 Storage
- **EBS** = a network-attached virtual disk for one instance; **persistent** (survives
  stop/start), snapshot to S3.
- **Instance store** = physically attached, **ephemeral** (lost on stop), very fast.
- **EFS** = shared file system many instances mount at once.

## 2.6 Access & permissions
- **Key pair** = SSH login (a `.pem` private key). Lock SSH to your IP.
- **SSM Session Manager** = connect with no SSH port open (preferred).
- **Instance profile (IAM role)** = lets the instance call AWS APIs (e.g., read S3)
  **without stored keys** — it assumes a role for temporary credentials.

## Interview Q&A — EC2

**Q: On-Demand vs Reserved vs Spot?**
A: On-Demand = flexible, pay-as-you-go (variable load). Reserved/Savings Plans = commit
1–3 yrs for a discount (steady load). Spot = cheapest, interruptible (fault-tolerant/batch).

**Q: How does EC2 access S3 without storing credentials?**
A: It has an **instance profile** — an IAM role it assumes for temporary credentials, so
no access keys are stored on the box.

**Q: How do you make EC2 highly available?**
A: An Auto Scaling Group across multiple AZs behind an ALB, with ELB health checks, so a
failed instance or a whole-AZ failure doesn't take the app down.

**Q: Difference between EBS and instance store?**
A: EBS is persistent network storage (survives stop, snapshot-able); instance store is
ephemeral local disk (lost on stop) but faster.

## Real-World Exceptions & Resolutions — EC2

| Problem | Cause | Resolution |
|---------|-------|------------|
| `InvalidBlockDeviceMapping: volume smaller than snapshot` | root volume < AMI's snapshot size | set root volume ≥ the AMI size (AL2023 needs ≥ 30 GB) |
| `instance type not eligible for Free Tier` | wrong type | use `t3.micro` (verify with `describe-instance-types --filters free-tier-eligible=true`) |
| ALB returns 502/503 | targets unhealthy | check target-group health, app listening on the health-check port/path, App-SG allows ALB-SG |
| ASG launches then kills instances | failing health checks | fix user-data/bootstrap; raise health-check grace period |
| `InsufficientInstanceCapacity` | AZ out of that type | try another AZ/type or retry |
| Can't SSH | SG/keys/subnet | open 22 from your IP, use the right key, ensure public subnet — or use SSM |
| EC2 can't read S3 | no/insufficient instance role | attach an instance profile with `s3:GetObject` scoped to the bucket |

---

# Part 3 — IAM

## 3.1 The four building blocks
- **Policy** — a JSON document listing **allowed/denied actions on resources**. Grants
  nothing until attached.
- **User** — a long-lived identity for a person/app.
- **Group** — a collection of users; **attach policies here**, users inherit.
- **Role** — an identity **assumed temporarily** by a service or another account (gets
  short-lived credentials).

## 3.2 User vs Role (the classic question)
A **user** = permanent identity you log in as (long-lived keys/password). A **role** =
assumed temporarily for short-lived credentials. **Prefer roles for anything non-human**
(EC2, Lambda) and for cross-account access — no stored keys.

## 3.3 Trust policy vs permission policy (roles)
A role has **two** policies:
- **Trust policy** (`assume_role_policy`) — **who may assume** the role (e.g.,
  `ec2.amazonaws.com`).
- **Permission policies** — **what** the role can do once assumed.

*Debugging tip:* "Can't assume role" → the **trust policy** is wrong. "Assumed but access
denied" → the **permission policy** is wrong. Naming which half is the issue impresses
interviewers.

## 3.4 Identity-based vs resource-based policies
- **Identity-based** — attached to a user/group/role (what *they* can do).
- **Resource-based** — attached to a resource (S3 bucket policy, SQS queue policy) — says
  *who* can access it. **Required for cross-account access** (both sides must allow).

## 3.5 Policy evaluation logic
- Default = **deny**. An **Allow** grants access. An **explicit Deny always wins** over
  any Allow. So: explicit Deny > Allow > default Deny.

## 3.6 MFA, root, least privilege
- **Root user:** unlimited, can't be restricted by IAM. Lock it with **MFA**, use it
  almost never; do daily work as an admin IAM user.
- **MFA:** a second login factor — enable on root and privileged users.
- **Least privilege:** grant only what's needed; scope to specific resources, not `*`.

## 3.7 Cross-account access
Account A's role has a **trust policy** allowing Account B; Account B's user has
permission to assume it. B calls `sts:AssumeRole` → gets temporary credentials in A.

## Interview Q&A — IAM

**Q: User vs role?**
A: User = permanent identity you log in as; role = assumed temporarily for short-lived
credentials. Use roles for services and cross-account — no static keys.

**Q: A Lambda gets AccessDenied writing to DynamoDB. Where do you look?**
A: First confirm it's assuming its execution role (trust policy allows `lambda.amazonaws.com`),
then check the permission policy allows `dynamodb:PutItem` on that table ARN. Trust = who
can assume; permissions = what they can do.

**Q: How does policy evaluation resolve conflicts?**
A: Default deny; an Allow grants; an **explicit Deny overrides everything**.

**Q: How do you give an app cross-account access to an S3 bucket?**
A: A resource-based policy (bucket policy) in the owning account allowing the other
account's role, plus an identity-based policy on that role allowing the S3 action. Both
sides required.

## Real-World Exceptions & Resolutions — IAM

| Problem | Cause | Resolution |
|---------|-------|------------|
| `is not authorized to perform: sts:AssumeRole` | trust policy doesn't allow the principal | fix the role's trust policy to include the service/account |
| Assumed the role but `AccessDenied` on an action | permission policy missing the action/resource | add the action + scope the resource ARN |
| `InvalidClientTokenId` (403) | bad/expired access key | new key + `aws configure`; verify `aws sts get-caller-identity` |
| User can log in but sees nothing | not in the right group / policy | add the user to the group that has the needed policy |
| Cross-account call denied | only one side allows | need both the resource policy AND the identity policy |
| Over-broad permissions in audit | wildcard `*` policies | use Access Analyzer to right-size to observed usage |

---

# Part 4 — Security

## 4.1 Shared Responsibility Model
AWS secures the **cloud** (hardware, facilities, managed-service internals). **You** secure
what's **in** the cloud (IAM, encryption, network config, data). Nearly every security
question tests **your** side.

## 4.2 Encryption
- **At rest:** encrypt stored data — S3 (SSE-S3 or SSE-KMS), EBS, RDS. **KMS** manages the
  keys.
- **In transit:** TLS/HTTPS everywhere.
- **SSE-S3 vs SSE-KMS:** S3-managed key vs a KMS key you control (with an audit trail and
  a second `kms:Decrypt` permission gate).

## 4.3 Secrets Manager vs Parameter Store
- **Secrets Manager** — stores secrets (DB passwords, API keys) with **automatic rotation**.
- **SSM Parameter Store** — config + secrets (SecureString), cheaper, no built-in rotation.
Never hardcode secrets in code, env vars in plaintext, or Terraform state.

## 4.4 WAF & Shield
- **WAF** — web-app firewall: block SQL injection, XSS, bad bots (in front of ALB/CloudFront).
- **Shield** — DDoS protection (Standard is automatic; Advanced is paid).

## 4.5 Security best-practices checklist
- Block public access on S3; encrypt at rest + in transit.
- Only load balancers/NAT/bastion in public subnets; app + DB private.
- IAM roles (no static keys); least privilege; MFA; lock away root.
- Secrets in Secrets Manager; monitor with CloudWatch; audit with CloudTrail.
- Tiered security groups referencing each other; VPC endpoints for private AWS access.

## Interview Q&A — Security

**Q: What is the Shared Responsibility Model?**
A: AWS secures the cloud (infrastructure); the customer secures what's in it (IAM,
encryption, network, data).

**Q: How do you secure an S3 bucket?**
A: Block public access, encrypt at rest (SSE-S3/KMS) and in transit (TLS), disable ACLs so
access is IAM-driven, least-privilege policies scoped to the bucket, versioning + logging.

**Q: How do you handle database credentials for an app?**
A: Store them in Secrets Manager (auto-rotated) and fetch at runtime — never hardcode; or
let RDS manage the master password in Secrets Manager.

**Q: SSE-S3 vs SSE-KMS?**
A: Both encrypt at rest; SSE-S3 = AWS-managed key, SSE-KMS = a key you control with an
audit trail and a second decrypt-permission gate.

## Real-World Exceptions & Resolutions — Security

| Problem | Cause | Resolution |
|---------|-------|------------|
| S3 `AccessDenied` even with S3 permission | SSE-KMS key not allowed | grant `kms:Decrypt` on the key to the caller |
| Secret exposed in Terraform state | secret created in TF | use RDS-managed passwords / Secrets Manager; never put secrets in state |
| Bucket accidentally public | public access not blocked | enable Block Public Access at account + bucket level |
| Credentials leaked in git | committed keys | rotate/delete immediately; use roles/Secrets Manager; add to `.gitignore` |
| DDoS / injection attempts | no edge protection | put WAF (rules) + Shield in front of CloudFront/ALB |

---

# Part 5 — Interview "tell me about…" answers

Use these as ready templates (tie to a real project where you can).

**"Describe a secure AWS architecture you'd design."**
> "I put everything in a VPC across two Availability Zones. The only public-facing piece
> is an Application Load Balancer in the public subnets. App servers run in private
> subnets in an Auto Scaling Group, and the database is a Multi-AZ RDS in private subnets,
> not publicly accessible. Traffic flows internet → ALB → private app servers → private
> DB. Private servers get outbound internet through a NAT gateway, and reach S3/DynamoDB
> through VPC endpoints. Security groups are tiered — the app SG only accepts traffic from
> the ALB SG, and the DB SG only from the app SG. Services use IAM roles instead of keys,
> data is encrypted with KMS, secrets live in Secrets Manager, and I monitor with
> CloudWatch and audit with CloudTrail."

**"How do you secure access to your AWS account?"**
> "Lock the root user behind MFA and don't use it day-to-day. Create IAM users/roles with
> least-privilege policies attached to groups, require MFA, and use roles (temporary
> credentials) for services and cross-account access instead of long-lived keys."

**"Why private subnets for the database?"**
> "A database should never be reachable from the internet. In a private subnet there's no
> route from the internet to it — it's only reachable from the app tier via a security
> group rule. Even if the app tier were compromised, the DB isn't directly exposed. That's
> defense in depth, and it's the core of a well-architected VPC."

**"How do you troubleshoot 'app can't reach the database'?"**
> "I work by layer: is the DB in the same VPC and a private subnet? Does the DB security
> group allow the app's security group on the DB port? Is the app using the right endpoint
> and credentials (from Secrets Manager)? I check the security group rule first — it's the
> most common cause — then connectivity, then credentials."

---

---

# Part 6 — The Other Core Services (deep dive)

Same interview format for every service we built: what it is + an example + key Q&A +
real-world exceptions with fixes.

## 6.1 S3 (object storage)
**What:** unlimited object storage — files in buckets, accessed by API. Foundation of
data lakes, backups, static assets. *Example:* "We store raw order files in S3 as the
bronze layer of our data lake, and app documents/images in a separate bucket."

**Q: How do you secure an S3 bucket?** Block Public Access, encrypt (SSE-S3/KMS) + TLS,
disable ACLs (bucket-owner-enforced), least-privilege bucket/IAM policies, versioning +
logging.
**Q: Why is a bucket name globally unique but the data lives in one region?** The name is
a global namespace claim; the data physically sits in the region you choose.
**Q: How do you serve S3 content fast worldwide but keep the bucket private?** CloudFront
with Origin Access Control — only CloudFront can read the bucket.

| Exception | Cause | Fix |
|-----------|-------|-----|
| `BucketAlreadyExists` | name taken globally | make it unique (append account ID) |
| `AccessDenied` on GetObject | policy or KMS | check bucket policy + IAM + `kms:Decrypt` |
| bucket won't delete | it has objects/versions | empty all versions + delete markers first |

## 6.2 RDS (relational database)
**What:** managed relational DB (MySQL/PostgreSQL/etc.) — AWS handles backups, patching,
failover. *Example:* "Our transactional orders/customers data is in a Multi-AZ RDS in
private subnets, not publicly accessible."

**Q: Multi-AZ vs Read Replica?** Multi-AZ = a **standby** in another AZ for **availability**
(auto-failover, you don't read it). Read Replica = extra copies for **read scaling** (you
do read them). One is for HA, the other for performance.
**Q: How do you keep the DB password out of code?** `manage_master_user_password` → RDS
stores/rotates it in Secrets Manager; the app fetches at runtime.

| Exception | Cause | Fix |
|-----------|-------|-----|
| app can't connect | DB-SG doesn't allow app-SG | allow the DB port from the app SG |
| `DBSubnetGroupDoesNotCoverEnoughAZs` | subnet group in 1 AZ | span ≥ 2 private subnets (needed for Multi-AZ) |
| apply "hangs" | provisioning is slow | RDS takes ~8–10 min — normal |

## 6.3 DynamoDB (NoSQL)
**What:** key-value/document DB, single-digit-ms latency at any scale. *Example:* "Live
order status and shopping carts live in DynamoDB — a partition key `order_id`, sort key
`order_date`, and a GSI on `customer_id` to query a customer's orders."

**Q: How do you avoid a hot partition?** Pick a high-cardinality, evenly-distributed
partition key so traffic spreads (not something like `status`).
**Q: GSI vs LSI?** GSI = different partition+sort key, added anytime, own capacity (new
query patterns). LSI = same partition key, different sort key, created at table creation.
**Q: Why did numbers cause an error in Python?** DynamoDB needs `Decimal`, not `float` —
convert with `Decimal(str(x))`.

| Exception | Cause | Fix |
|-----------|-------|-----|
| `Float types are not supported` | put a float | convert to `Decimal(str(x))` |
| `ResourceNotFoundException` | table doesn't exist / wrong region | create it / set the right region |
| throttling | hot partition or low capacity | better key design or on-demand billing |

## 6.4 Lambda (serverless functions)
**What:** run code on a trigger, no servers, pay per use, 15-min max. *Example:* "When an
order file lands in S3, a Lambda reads it and writes to DynamoDB — fully event-driven, no
servers."

**Q: What does an S3 event actually contain?** Only the bucket name + object **key**
(metadata) — not the file contents. The Lambda must call `s3:GetObject` to read it (so its
role needs that permission).
**Q: Lambda vs EC2 vs Glue?** Lambda = short event-driven (<15 min); EC2 = long-running
general compute; Glue = large distributed Spark ETL.
**Q: When does a Lambda go in a VPC?** When it must reach private resources like RDS —
it gets an ENI in the private subnets.

| Exception | Cause | Fix |
|-----------|-------|-----|
| `AccessDenied` to S3/DynamoDB | role missing permission | add the scoped action to the execution role |
| stores junk from an S3 event | treated the event as the data | `GetObject` the file the event points to |
| VPC Lambda times out to internet | no NAT / endpoints | add NAT for internet, endpoints for S3/DynamoDB |

## 6.5 API Gateway
**What:** managed HTTPS front door for APIs — routing, auth, throttling — usually in front
of Lambda. *Example:* "Our Orders REST API is API Gateway → Lambda → DynamoDB, with an
`x-api-key` checked by a Lambda authorizer."

**Q: REST API vs HTTP API?** HTTP API = cheaper, faster, fewer features (good default).
REST API = more features (API keys/usage plans, request validation, WAF integration).
**Q: How do you secure an API Gateway endpoint?** API keys / Lambda authorizer / JWT
(Cognito) / IAM auth; throttling + usage plans; WAF for the edge.

| Exception | Cause | Fix |
|-----------|-------|-----|
| 401 on every call | missing auth header | send the `x-api-key`/token the authorizer expects |
| 403 | wrong key / no access | fix the key or the authorizer/IAM |
| 5xx | Lambda error | check the Lambda's CloudWatch logs |

## 6.6 SQS & SNS (messaging)
**What:** **SQS** = a queue (buffer, one consumer group pulls). **SNS** = pub/sub (one
message fans out to many). *Example:* "Order placed → SNS notifies customer + warehouse +
analytics; SQS buffers fulfillment work so a spike doesn't crash the consumer; a DLQ holds
poison messages."

**Q: SQS vs SNS?** Queue (pull, buffer) vs pub/sub (push, fan-out). Common combo:
SNS → many SQS queues.
**Q: What's a DLQ?** Dead-Letter Queue — holds messages that fail after N attempts so they
don't block the queue and can be inspected/replayed.
**Q: Standard vs FIFO?** Standard = high throughput, at-least-once, best-effort order.
FIFO = exactly-once, strict order, lower throughput.

| Exception | Cause | Fix |
|-----------|-------|-----|
| SNS can't deliver to SQS | missing queue policy | allow `sns.amazonaws.com` to `SendMessage`, scoped to the topic ARN |
| messages reprocessed | visibility timeout < processing time | raise the visibility timeout |
| messages "disappear" | went to the DLQ | inspect the DLQ; fix the consumer |

## 6.7 Glue & Athena (analytics)
**What:** **Glue** = managed Spark ETL + Data Catalog; **Athena** = serverless SQL over
S3. *Example:* "A Glue job cleans raw JSON into partitioned Parquet (bronze→silver);
Athena queries it with SQL over the Glue Catalog — no database to load."

**Q: How do you make Athena cheap/fast?** Partition the data, use columnar Parquet, filter
on the partition column — it charges per TB scanned, so scan less.
**Q: Why does Athena need the Glue Catalog?** Athena has no storage — the Catalog supplies
the schema so it knows how to read the S3 files.

| Exception | Cause | Fix |
|-----------|-------|-----|
| Athena returns nothing | wrong location / no partitions | point the table at the right S3 prefix; add/repair partitions |
| Glue job slow | data skew / small files / few workers | salt skew, compact files, add DPUs |
| high Athena cost | scanning everything | partition + Parquet + filter on partition key |

## 6.8 CloudWatch (monitoring)
**What:** metrics, logs, alarms, dashboards. *Example:* "We alarm on EC2 CPU >80%, RDS
connections, SQS queue depth, and Lambda errors — the alarm publishes to an SNS topic that
emails on-call."

**Q: CloudWatch vs CloudTrail?** CloudWatch = performance monitoring (metrics/logs/alarms —
"is it healthy?"). CloudTrail = API audit log ("who did what?").
**Q: How do you get notified on an alarm?** The alarm's action publishes to an SNS topic;
subscribers (email/SMS/Lambda) are notified.

| Exception | Cause | Fix |
|-----------|-------|-----|
| alarm never fires | wrong metric/dimension | verify namespace + dimensions match the resource |
| no Lambda logs | role can't write logs | attach `AWSLambdaBasicExecutionRole` |
| too many false alarms | threshold/period too tight | tune threshold + evaluation periods |

---

# Part 7 — Interview "tell me about…" answers

Use these as ready templates (tie to a real project where you can).

**"Describe a secure AWS architecture you'd design."**
> "I put everything in a VPC across two Availability Zones. The only public-facing piece
> is an Application Load Balancer in the public subnets. App servers run in private
> subnets in an Auto Scaling Group, and the database is a Multi-AZ RDS in private subnets,
> not publicly accessible. Traffic flows internet → ALB → private app servers → private
> DB. Private servers get outbound internet through a NAT gateway, and reach S3/DynamoDB
> through VPC endpoints. Security groups are tiered — the app SG only accepts traffic from
> the ALB SG, and the DB SG only from the app SG. Services use IAM roles instead of keys,
> data is encrypted with KMS, secrets live in Secrets Manager, and I monitor with
> CloudWatch and audit with CloudTrail."

**"How do you secure access to your AWS account?"**
> "Lock the root user behind MFA and don't use it day-to-day. Create IAM users/roles with
> least-privilege policies attached to groups, require MFA, and use roles (temporary
> credentials) for services and cross-account access instead of long-lived keys."

**"Why private subnets for the database?"**
> "A database should never be reachable from the internet. In a private subnet there's no
> route from the internet to it — it's only reachable from the app tier via a security
> group rule. Even if the app tier were compromised, the DB isn't directly exposed. That's
> defense in depth, and it's the core of a well-architected VPC."

**"How do you troubleshoot 'app can't reach the database'?"**
> "I work by layer: is the DB in the same VPC and a private subnet? Does the DB security
> group allow the app's security group on the DB port? Is the app using the right endpoint
> and credentials (from Secrets Manager)? I check the security group rule first — it's the
> most common cause — then connectivity, then credentials."

**"Walk me through a serverless API you built."**
> "API Gateway → Lambda → DynamoDB. The Lambda reads/writes the Orders table; its IAM role
> is scoped to just that table. I added `x-api-key` auth via a Lambda authorizer — 401
> without a key, 403 on a bad key — and made writes idempotent using the natural key so a
> retry can't duplicate. It's serverless: no servers, scales automatically, pay per request."

---

*Pair with [aws-certification-qa.md](aws-certification-qa.md) and
[aws-services-and-architectures.md](aws-services-and-architectures.md).*
