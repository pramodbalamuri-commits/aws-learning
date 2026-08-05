# Public vs Private Subnets — and the `enable_vpc` toggle

Two questions answered here:
1. Why did we put EC2/RDS in **private** subnets instead of public?
2. What does "the VPC cert blueprint is enabled" actually mean (the `enable_*` toggles)?

---

## 1. Public vs private subnet — what's the difference?

The **only** technical difference is the **route table**:

| Subnet type | Route to `0.0.0.0/0` (the internet) | Result |
|-------------|--------------------------------------|--------|
| **Public**  | → **Internet Gateway (IGW)** | resources can be reached *from* the internet and reach *out* directly |
| **Private** | → **NAT Gateway** (or no internet route) | resources are hidden; they can only reach *out* (via NAT), never be reached *in* from the internet |

That's it — a subnet is "public" simply because its route table points `0.0.0.0/0` at the Internet Gateway.

---

## 2. Why each resource went where it did

### Public subnets (kept minimal — only what MUST face the internet)
| Resource | Why it's public |
|----------|-----------------|
| **ALB (load balancer)** | It has to receive traffic from users on the public internet, so it must be reachable from outside. |
| **NAT Gateway** | It has to reach the Internet Gateway to give private instances outbound internet. |
| **Bastion host** | It's the controlled SSH entry point (locked to *your* IP), so it needs a public IP. |

### Private subnets (everything valuable / that shouldn't be exposed)
| Resource | Why it's private |
|----------|------------------|
| **EC2 app servers** | Users reach them **only through the ALB** — never directly. Even if someone learns the instance IP, there's no internet route to it, so they can't connect. |
| **RDS database** | You **never** put a database in a public subnet. It holds your data and should only be reachable from the app tier. We also set `publicly_accessible = false`. |
| **Lambda (VPC-attached)** | Placed in private subnets so it can reach RDS privately over the internal network. |

---

## 3. Why NOT just use public subnets for everything?

It would "work" — but it's **insecure and fails the exam's core principle**:

- **Bigger attack surface.** Anything in a public subnet with a public IP is directly reachable from the internet (subject only to its security group). One misconfigured security-group rule = your app server or database exposed to the world.
- **Defense in depth.** The secure pattern is: expose **only the load balancer**; hide the app and database behind it. If the app tier is compromised, the attacker still can't reach the DB directly from the internet.
- **Real-world breaches.** Publicly-exposed databases and servers are one of the top causes of data leaks. Keeping them private removes that entire class of mistake.
- **This is heavily tested.** AWS Solutions Architect Associate repeatedly asks "where should the database / app server / load balancer go?" — the answer is almost always: **load balancer + NAT + bastion in public; app servers + database in private.**

> **Rule of thumb:** *Public subnet = only load balancers, NAT gateways, and bastion hosts. Everything else (app servers, databases, cache, internal services) goes in private subnets.*

---

## 4. The trade-off (why private costs a little more)

Private resources still need **outbound** internet (OS patches, package installs, calling external APIs). They get it through the **NAT Gateway** — which is a **paid** resource (~$0.045/hr + data). That's the price of the security.

We reduce NAT usage with **VPC Gateway Endpoints** for S3 and DynamoDB, so that traffic to those two services stays on the AWS backbone and never touches the NAT/internet — cheaper *and* more secure.

---

## 5. "Is the VPC cert blueprint enabled?" — the `enable_*` toggles

In this project, **every blueprint module is behind an `enable_*` variable that defaults to `false`**, so you never create paid resources (like the NAT Gateway or ALB) by accident.

| Toggle | Builds | Default |
|--------|--------|---------|
| `enable_vpc` | VPC, subnets, IGW, NAT, route tables, S3/DynamoDB endpoints | `false` |
| `enable_security_groups` | the 5 tiered security groups (needs VPC) | `false` |
| `enable_rds` | RDS in private subnets (needs VPC + SGs) | `false` |
| `enable_ec2_asg` | EC2 + ALB + Auto Scaling (needs VPC + SGs) | `false` |
| `enable_messaging` | SNS + SQS + DLQ | `false` |
| `enable_iam`, `enable_cloudwatch` | roles / alarms | `false` |

**So "enabled" means: you passed the flag at apply time.** To actually build the VPC environment:

```bash
terraform apply \
  -var="enable_vpc=true" \
  -var="enable_security_groups=true" \
  -var="enable_rds=true" \
  -var="enable_ec2_asg=true" \
  -var="enable_messaging=true"
```

> ⚠️ If you run a plain `terraform apply` **without** the flags, the VPC/subnets/RDS/ALB are **not** built — only the data-engineering stack (which is on by default). That's why an earlier apply showed `security_group_ids = null` and no `vpc_id`. See [`../EXECUTION_GUIDE.md`](../EXECUTION_GUIDE.md).

---

## 6. Summary table

| Resource | Subnet | Reason |
|----------|--------|--------|
| ALB | **public** | receives internet traffic |
| NAT Gateway | **public** | needs the IGW for outbound |
| Bastion host | **public** | controlled SSH entry point |
| EC2 app servers | **private** | reached only via the ALB |
| RDS database | **private** | never expose a database |
| Lambda (in VPC) | **private** | private access to RDS |
| S3 / DynamoDB | (not in a subnet) | reached from private subnets via VPC endpoints |

**One line:** *Only put in a public subnet what truly must face the internet (load balancer, NAT, bastion); everything else — especially the database — goes private.*
