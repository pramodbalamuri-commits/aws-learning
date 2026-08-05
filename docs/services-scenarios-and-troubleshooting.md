# Services, Real-Time Scenarios & Troubleshooting

Three things in one place:
- **Part 1** — Public vs private subnets, made crystal clear with a real request flow.
- **Part 2** — Every service we built, with a real-world scenario for each.
- **Part 3** — The exceptions/errors we actually hit (and common ones), with fixes.

---

# Part 1 — Public vs Private Subnets (clear + real scenario)

## The core idea in one sentence
A subnet is **public** if its route table sends internet traffic (`0.0.0.0/0`) to the
**Internet Gateway**; it's **private** if it sends that traffic to a **NAT Gateway**
(or has no internet route at all). That single routing choice is the whole difference.

## The mental model
- **Public subnet = the building lobby.** Reachable from the street (internet). You
  only put things here that *must* face the public: the load balancer, the NAT
  gateway, and a bastion host.
- **Private subnet = the back offices.** No street access. Everything valuable lives
  here: app servers, databases, internal services. They can *reach out* (via NAT) but
  can't be *reached in* from the internet.

## Real scenario: a user loads your website (follow the hops)

> A customer in London opens `https://shop.example.com` and sees the product page.

| Hop | Where | Public or private? | Why |
|-----|-------|--------------------|-----|
| 1. DNS lookup (Route 53) | global | — | resolves the name to the ALB |
| 2. Request enters the VPC | Internet Gateway | edge of VPC | the only door in |
| 3. Hits the load balancer | **ALB** | **public subnet** | must receive internet traffic |
| 4. ALB forwards to an app server | **EC2** | **private subnet** | never exposed directly; only the ALB can reach it |
| 5. App queries the database | **RDS** | **private subnet** | a database must never be public |
| 6. App needs to call a 3rd-party API | out via **NAT Gateway** | NAT in public subnet | outbound only; the internet can't call back in |
| 7. App reads a file from S3 | via **VPC Gateway Endpoint** | stays on AWS backbone | cheaper + private, skips the NAT |
| 8. Response goes back to the user | ALB → IGW → user | | stateful — return path is automatic |

**Key takeaways:**
- The user only ever talks to the **ALB** (public). They can't see or reach the EC2
  instances or the database at all.
- The app servers and DB are in **private** subnets — even if an attacker learned
  their IPs, there is **no internet route** to them.
- Private servers still get outbound internet through the **NAT** for updates/APIs,
  but that path is one-way.

## Second scenario: the data pipeline (mostly no subnets needed)
> An order JSON file is uploaded to S3 and ends up queryable with SQL.

S3, Lambda, DynamoDB, Glue, and Athena are **regional managed services** — they don't
live *in* your subnets. A Lambda only needs to be *in* the VPC (private subnet) if it
must reach something private like RDS. The order-processor Lambda here isn't in the
VPC because it only touches S3 and DynamoDB (both reachable without a VPC).

**Rule of thumb:** *Public subnet = only load balancers, NAT, and bastion hosts.
Everything else — app servers, databases — goes private. Managed services (S3,
DynamoDB, Lambda, SNS, SQS) aren't in subnets at all unless a Lambda needs private
network access.*

---

# Part 2 — Every Service We Built (with real-time scenarios)

## Data platform (default ON)

### S3 (`modules/s3_bucket`)
- **What:** object storage — files in buckets, at unlimited scale.
- **Where:** regional (not in a subnet).
- **Real scenario:** an online store keeps every product image and every raw sales
  file in S3. Analysts later build reports directly off those raw files (the "data
  lake"). Here, uploaded order JSON lands in S3 as the bronze layer.

### DynamoDB (`modules/dynamodb_table`)
- **What:** NoSQL key-value database, single-digit-ms latency at any scale.
- **Real scenario:** a food-delivery app shows your order status changing
  "Preparing → Out for delivery" in real time — that live state is a DynamoDB item.
  Our `Orders` table (partition `order_id`, sort `order_date`, GSI on `customer_id`)
  is exactly that.

### Lambda (`modules/lambda_function`)
- **What:** serverless function that runs only when triggered.
- **Real scenario:** the moment a customer uploads a receipt to S3, a Lambda fires,
  reads it, and records it — no server sitting idle. Our `order-processor` reads the
  uploaded order file (`s3:GetObject`) and writes it to DynamoDB.

### Glue ETL (`modules/glue_etl`)
- **What:** managed Apache Spark for large-scale ETL.
- **Real scenario:** every night a retailer cleans millions of messy raw sales rows
  into tidy, partitioned Parquet for reporting. Our Glue job does bronze → silver:
  dedupe on `order_id`, cast types, partition by `order_date`.

### Athena + Glue Catalog (`modules/analytics`)
- **What:** serverless SQL directly over S3 files; the Catalog holds the schema.
- **Real scenario:** an analyst answers "revenue by restaurant last month" by running
  plain SQL on the S3 data — no database to load, pay per query.
  `SELECT restaurant, SUM(amount) FROM orders_db.orders GROUP BY restaurant`.

## Cloud infrastructure — VPC blueprint (toggle on)

### VPC (`modules/vpc`)
- **What:** your private, isolated network (subnets, IGW, NAT, route tables, endpoints).
- **Real scenario:** a bank runs its app inside a VPC so nothing is on the public
  internet except a tightly controlled load balancer. Our VPC spans 2 AZs with public
  + private subnets.

### Security Groups (`modules/security_groups`)
- **What:** stateful virtual firewalls, one per tier.
- **Real scenario:** the web tier may talk to the app tier, and only the app tier may
  talk to the database — enforced by SGs that reference each other. Chain of trust:
  internet → ALB-SG → App-SG → DB-SG.

### RDS (`modules/rds`)
- **What:** managed relational database (MySQL/PostgreSQL), Multi-AZ capable.
- **Where:** **private subnets**, `publicly_accessible = false`.
- **Real scenario:** the transactional database behind an e-commerce app — orders,
  customers, inventory. Multi-AZ keeps a standby so a hardware failure doesn't cause
  an outage.

### EC2 + ALB + Auto Scaling (`modules/ec2_asg`)
- **What:** launch template + Auto Scaling Group behind an Application Load Balancer.
- **Real scenario:** on Black Friday, traffic spikes 10×. The ASG automatically adds
  app servers (and removes them after), while the ALB spreads load and replaces any
  unhealthy instance. App servers are private; only the ALB is public.

### Messaging — SNS + SQS + DLQ (`modules/messaging`)
- **What:** pub/sub topic + queue + dead-letter queue.
- **Real scenario:** when an order is placed, one event fans out: notify the customer
  (SNS) **and** drop a job on a queue for the fulfillment service (SQS). If 10,000
  orders arrive at once, SQS buffers them; anything that keeps failing lands in the DLQ
  for inspection instead of blocking the line.

### IAM (`modules/iam`)
- **What:** dedicated EC2 and Lambda roles (least privilege).
- **Real scenario:** a payment Lambda gets a role that can *only* write to the payments
  table — if it's ever compromised, the damage is contained. EC2 gets an instance
  profile so it can read S3 without any stored keys.

### CloudWatch (`modules/cloudwatch`)
- **What:** metric alarms + a notification topic.
- **Real scenario:** at 2 a.m. the database connection count spikes; a CloudWatch alarm
  emails the on-call engineer before customers notice. We alarm on ASG CPU, RDS
  connections, SQS backlog, and Lambda errors.

---

# Part 3 — Exceptions / Errors & How to Resolve Them

## A. The errors we actually hit this project (real)

### 1. `Error: Module not installed`
- **When:** ran `terraform plan/apply` right after adding new modules.
- **Cause:** Terraform hasn't registered the new local modules.
- **Fix:** `terraform init`. **Rule:** run `init` any time you add a module or provider.

### 2. `InvalidClientTokenId: The security token included in the request is invalid` (403)
- **When:** `terraform plan` / any `aws` command.
- **Cause:** the configured access key is wrong, expired, or deleted.
- **Fix:** create a fresh access key (IAM → your user → Security credentials), run
  `aws configure`, verify with `aws sts get-caller-identity`.

### 3. `InvalidBlockDeviceMapping: Volume of size 8GB is smaller than snapshot, expect >= 30GB`
- **When:** launching EC2 from the Amazon Linux 2023 AMI.
- **Cause:** the AMI's base snapshot is 30 GB; the root volume can't be smaller.
- **Fix:** set root volume to **≥ 30 GB** (30 is also the Free-Tier limit).

### 4. `InvalidParameterCombination: The specified instance type is not eligible for Free Tier`
- **When:** launching `t2.micro`.
- **Cause:** this account/region's Free-Tier x86 type is `t3.micro`, not `t2.micro`.
- **Fix:** use `t3.micro`. Confirm with
  `aws ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true`.

### 5. `BucketAlreadyExists` (409)
- **When:** creating an S3 bucket.
- **Cause:** S3 bucket names are **globally unique** across all AWS accounts — the name
  was taken by someone else.
- **Fix:** make it unique — we append the **account ID** via `aws_caller_identity`
  (`dataengineer-practice-bucket-<account-id>`).

### 6. Apply "worked" but `security_group_ids = null` and no `vpc_id`
- **When:** ran `terraform apply` without the toggle flags.
- **Cause:** blueprint modules default to `enable_* = false`, so they were skipped —
  only the data-eng stack built.
- **Fix:** pass the flags: `terraform apply -var="enable_vpc=true" -var=... ` (or a
  `dev.tfvars`). See EXECUTION_GUIDE.

### 7. `git push` → `RPC failed; HTTP 400` / `send-pack: unexpected disconnect`
- **When:** pushing several MB of PDFs at once.
- **Cause:** git's default HTTP post buffer is too small for a large push.
- **Fix:** `git config http.postBuffer 524288000` (500 MB), then push again.

### 8. MFA / "You do not have permission... authenticate with an MFA device"
- **When:** trying to add MFA in the console.
- **Cause / fix:** the **root user** needs no permissions to add its own MFA (IAM never
  restricts root) — if it's refused, you're not actually signed in as root. Sign out,
  sign in as root, then Security credentials → Assign MFA device.

## B. Common AWS errors by service (good to know)

### VPC / Networking
- **`Route already exists` / overlapping routes** → a route table already has a
  `0.0.0.0/0`; remove/replace it before adding another.
- **Instance in private subnet can't reach the internet** → no NAT route. Check the
  private route table has `0.0.0.0/0 → NAT`, and the NAT is in a **public** subnet with
  a route to the IGW.
- **NAT creation fails: no Elastic IP** → allocate an EIP first (the module does this).
- **Can't reach S3 from a private instance** → add the **S3 Gateway Endpoint** to the
  private route table (or ensure NAT works).

### Security Groups
- **`AccessDenied` / connection refused between tiers** → the SG rule is missing or
  references the wrong source. Reference the **source SG**, not an IP. Remember SGs are
  stateful (no need for a return rule) but NACLs are not.
- **Circular reference error creating SGs** → create the SGs first, then add rules as
  separate `aws_security_group_rule` resources (the module does this).

### EC2 / ALB / ASG
- **ALB returns 502 / 503** → targets are unhealthy. Check the target group health,
  the app is actually listening on the health-check port/path, and App-SG allows the
  ALB-SG on that port. Give it ~2 min after launch.
- **`InsufficientInstanceCapacity`** → the AZ is out of that type temporarily; try
  another AZ/type or retry.
- **ASG launches then terminates instances repeatedly** → failing health checks;
  check `health_check_type=ELB` grace period and the app bootstrap (user data).

### RDS
- **App can't connect to RDS** → DB-SG must allow the app's SG on the DB port
  (3306/5432); RDS must be in the same VPC; `publicly_accessible=false` is fine
  because the app is inside the VPC.
- **`DBSubnetGroupDoesNotCoverEnoughAZs`** → the DB subnet group needs subnets in ≥2
  AZs (required for Multi-AZ). The module spans both private subnets.
- **Apply seems to hang on RDS** → provisioning normally takes ~8–10 min; not stuck.

### Lambda
- **`AccessDenied` reading S3 / writing DynamoDB** → the execution role is missing the
  permission (`s3:GetObject` / `dynamodb:PutItem`) scoped to that resource.
- **S3-triggered Lambda stores junk / doesn't read the file** → the code treated the
  S3 event as the order. Remember the event only has bucket+key; you must
  `s3:GetObject` to read the file (we fixed exactly this).
- **`Float types are not supported` (DynamoDB)** → convert numbers to `Decimal`
  (`Decimal(str(x))`) before `put_item`.
- **Lambda in VPC times out reaching the internet** → VPC Lambdas need a NAT for
  internet and endpoints for S3/DynamoDB.

### S3
- **`AccessDenied` on GetObject** → check the bucket policy + the caller's IAM + (for
  SSE-KMS) `kms:Decrypt` on the key.
- **`BucketAlreadyOwnedByYou`** → you already made a bucket with that name; reuse it or
  pick another.

### SNS / SQS
- **SNS can't deliver to SQS** → add a **queue policy** allowing `sns.amazonaws.com` to
  `SendMessage`, scoped with `aws:SourceArn = <topic ARN>` (the module does this).
- **Messages reprocessed / duplicated** → visibility timeout is shorter than
  processing time; raise it. Persistent failures → they go to the **DLQ**.

### IAM
- **`is not authorized to perform: sts:AssumeRole`** → the role's **trust policy**
  doesn't allow that principal (service/account). Fix the `assume_role_policy`.
- **Assumed the role but still `AccessDenied`** → the **permission policy** is missing
  the action/resource. (Trust = who can assume; permissions = what they can do.)

### General Terraform
- **`Error acquiring the state lock`** → a previous run didn't release the lock;
  `terraform force-unlock <ID>` (only if you're sure no other run is active).
- **Resource "already exists"** on apply → it exists in AWS but not in state; `terraform
  import` it, or delete the manual resource.
- **Drift (someone changed it in the console)** → `terraform plan` shows the diff;
  re-`apply` to reconcile, or `terraform refresh`/import.

---

*General debugging method: read the error to find the layer it belongs to
(credentials → resource config → service limit → networking), query AWS for the ground
truth (`sts get-caller-identity`, `describe-*`), fix that one thing, and re-run `plan`
before `apply`.*
