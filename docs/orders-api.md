# Orders API — Serverless REST API over DynamoDB

A read + write API for the `Orders` table, two ways:
- **Local** — a FastAPI app (`orders-api` repo) you run on your machine (dev/prototyping).
- **Serverless on AWS** — `modules/orders_api` (API Gateway + Lambda), deployed by Terraform.

```
Client ──HTTPS──▶ API Gateway (HTTP API)
                     │  (x-api-key checked by a Lambda authorizer)
                     ▼
                 Lambda (Python)  ──boto3──▶  DynamoDB (Orders + GSI)
```

## Why this design
- **API Gateway** = the managed HTTPS front door (routing, auth, throttling) — you
  don't run a web server.
- **Lambda** = the code, runs only per request, scales automatically, pay-per-use.
- **DynamoDB** = the data store.
- **Lambda authorizer** = checks the `x-api-key` header before the request reaches
  the app Lambda. (HTTP APIs don't have REST-API-style API keys/usage plans, so a
  request authorizer is the lightweight way to do key auth.)
- **Least-privilege IAM** = the app Lambda's role can only Get/Query/Scan/Put on this
  one table + its indexes.

## Endpoints

| Method | Path | Auth | What it does |
|--------|------|------|--------------|
| GET | `/` | key | health check |
| GET | `/orders?limit=25` | key | list orders (Scan) |
| GET | `/orders/{order_id}` | key | one order by partition key (Query) |
| GET | `/customers/{customer_id}/orders` | key | a customer's orders (GSI Query) |
| POST | `/orders` | key | create an order (PutItem) |

`POST /orders` body — `order_id` and `order_date` are required:
```json
{ "order_id": "ord-777", "order_date": "2026-08-05",
  "customer_id": "cust-9", "amount": 88.88, "restaurant": "New Diner" }
```

## Auth behaviour (tested)

| Request | Result |
|---------|--------|
| no `x-api-key` header | **401 Unauthorized** |
| wrong key | **403 Forbidden** |
| correct key | request proceeds |

The expected key is the module's `api_key` variable (sensitive) — **override the
default**. Pass it as `-var="api_key=..."`, a `*.tfvars`, or a `TF_VAR_api_key` env var.

## Deploy (Terraform)

```bash
cd terraform-aws-practice
terraform init
terraform apply -var="enable_orders_api=true" -var="api_key=YOUR_SECRET"
terraform output orders_api_url        # -> https://xxxx.execute-api.us-west-2.amazonaws.com
```

### Try it
```bash
URL=$(terraform output -raw orders_api_url)
KEY=YOUR_SECRET

curl -H "x-api-key: $KEY" "$URL/orders"
curl -H "x-api-key: $KEY" "$URL/orders/ord-101"
curl -H "x-api-key: $KEY" "$URL/customers/cust-1/orders"
curl -X POST -H "x-api-key: $KEY" -H "Content-Type: application/json" \
  -d '{"order_id":"ord-900","order_date":"2026-08-06","customer_id":"cust-5","amount":25.0}' \
  "$URL/orders"
```

### Tear down
```bash
terraform destroy -var="enable_orders_api=true" -var="api_key=YOUR_SECRET"
```

## Cost
API Gateway HTTP API + Lambda are Free Tier for light use (≈ $0). DynamoDB on-demand
is a few cents at most. Destroy when done.

## Interview talking point
> "I prototyped a read/write orders API locally with FastAPI, then productionized it
> as **API Gateway HTTP API + Lambda + DynamoDB**, all in Terraform. I added key auth
> with a **Lambda request authorizer** (401 without a key, 403 on a bad key), scoped
> the Lambda's IAM role to just that table (read + PutItem), and validated the write
> path returns 400 on missing required fields. It's serverless — no servers to
> manage, scales automatically, pay-per-request."

## Common errors (and fixes)
| Symptom | Cause | Fix |
|---------|-------|-----|
| every request 401 | missing/misnamed header | send `x-api-key` (lowercase) |
| every request 403 | key mismatch | the `api_key` var must equal the header you send |
| `AccessDenied` in logs | role missing an action | ensure the role allows `dynamodb:PutItem` for writes |
| `ResourceNotFoundException` | Orders table doesn't exist | create/seed it first (see the `orders-api` repo's `seed_data.py`) |
| 500 with "Float types are not supported" | put a float into DynamoDB | convert numbers to `Decimal(str(x))` (the code does this) |
| authorizer not invoked | identity source header absent | HTTP API returns 401 before the authorizer if `x-api-key` is missing |
