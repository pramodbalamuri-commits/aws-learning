# Reverse Direction — AWS Calling *into* Appian (Web API)

The companion to [appian-integration.md](appian-integration.md). That guide covered
**Appian → AWS** (Appian calls the AWS API). This one covers **AWS → Appian**: an AWS
event (S3 upload, DynamoDB stream, SNS/SQS message) triggers a Lambda that calls an
**Appian Web API** to push data in or start a process.

```
S3 / DynamoDB Stream / SNS / SQS  ──▶  Lambda  ──HTTPS+auth──▶  Appian Web API
                                                                   │
                                                                   ▼
                                                start a process  /  write a record
```

**Use it when:** something happens in AWS and Appian needs to react — e.g., a new
order file lands in S3 → start an "Order Fulfillment" process in Appian; or a payment
event → update a case.

---

## 1. Step 1 — Create the Appian Web API (the endpoint AWS calls)

In Appian Designer: **New → Web API**.

- **HTTP Method:** `POST`
- **URL Alias:** e.g. `orders/ingest` → full URL becomes
  `https://<your-site>.appiancloud.com/suite/webapi/orders/ingest`
- **Expression:** read the incoming request, do something, return a response:

```
a!localVariables(
  /* http!request holds what AWS sent */
  local!order: a!fromJson(http!request.body),

  /* basic validation */
  if(
    or(a!isNullOrEmpty(local!order.order_id), a!isNullOrEmpty(local!order.order_date)),
    http!response(
      statusCode: 400,
      body: a!toJson(a!map(error: "order_id and order_date are required"))
    ),
    a!localVariables(
      /* start a process (or write a record / data store) */
      local!pid: a!startProcess(
        processModel: cons!ORDER_FULFILLMENT_PM,
        processParameters: a!map(
          orderId:    local!order.order_id,
          orderDate:  local!order.order_date,
          customerId: local!order.customer_id,
          amount:     local!order.amount
        )
      ),
      http!response(
        statusCode: 201,
        headers: { a!httpHeader(name: "Content-Type", value: "application/json") },
        body: a!toJson(a!map(status: "accepted", order_id: local!order.order_id))
      )
    )
  )
)
```

- `http!request` gives you `.body`, `.headers`, `.queryParameters`, `.pathSegments`.
- Inside a Web API you can **`a!startProcess(...)`** to kick off a process model, and/or
  **`a!writeToDataStore` / write records** to persist data.
- Always return an **`http!response`** with an appropriate status code.

---

## 2. Step 2 — Security (AWS → Appian)

Appian requires the caller to authenticate **as an Appian user**. For machine-to-machine
from AWS, use a **service account + API key**.

| Concern | How to handle it |
|---------|------------------|
| **Who is the caller** | Create a dedicated **service account user** in Appian (not a person). Put it in a group with **only** the access the Web API needs (least privilege). |
| **The credential** | In the Appian **Admin Console → API Keys**, generate an **API Key** for that service account. AWS sends it in the **`Appian-API-Key`** header. |
| **Object security** | The Web API object *and* everything it touches (the process model, record type, data store) must be visible/startable by the service account's group. |
| **Store the key on AWS** | Put the Appian URL + API key in **AWS Secrets Manager** (never in the Lambda's plaintext env vars or code). The Lambda reads it at runtime. |
| **IAM least privilege** | The Lambda's role may only `secretsmanager:GetSecretValue` on *that one secret* — nothing broader. |
| **Transport** | Appian Cloud is HTTPS-only (TLS). |
| **Network restriction** | Appian Cloud supports an **API client allowlist / IP restrictions** — restrict inbound to your NAT/known egress IPs so only your AWS account can call it. |
| **Validate input** | Never trust the payload — validate required fields and types in the Web API before acting (the example returns 400 on missing keys). |
| **Idempotency** | Use a natural key (`order_id`+`order_date`) so a retried call doesn't start a duplicate process / create a duplicate record. |
| **Rotate** | Rotate the Appian API key on a schedule; update the value in Secrets Manager (one place). |

---

## 3. Step 3 — The AWS Lambda that calls Appian

Triggered by S3 `ObjectCreated`, a DynamoDB Stream, SNS, SQS, or EventBridge. It reads
the Appian URL + key from Secrets Manager and POSTs the payload.

```python
import json
import os
import urllib.request
import urllib.error

import boto3

sm = boto3.client("secretsmanager")
SECRET_ID = os.environ["APPIAN_SECRET_ID"]   # e.g. "appian/orders-webapi"


def _config():
    # secret is JSON: {"url": "...", "api_key": "..."}
    return json.loads(sm.get_secret_value(SecretId=SECRET_ID)["SecretString"])


def handler(event, context):
    cfg = _config()
    order = {  # build from the triggering event (S3 file, stream record, etc.)
        "order_id": "ord-101",
        "order_date": "2026-08-01",
        "customer_id": "cust-1",
        "amount": 29.99,
    }
    req = urllib.request.Request(
        cfg["url"],
        data=json.dumps(order).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Appian-API-Key": cfg["api_key"],   # <-- Appian service-account key
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return {"statusCode": r.status, "body": r.read().decode()}
    except urllib.error.HTTPError as e:            # 4xx / 5xx from Appian
        body = e.read().decode()
        print(f"Appian returned {e.code}: {body}")
        # let it raise so SQS retries / DLQ catches it (see below)
        raise
    except urllib.error.URLError as e:             # timeout / network
        print(f"network error calling Appian: {e}")
        raise
```

---

## 4. Step 4 — Exception handling (both sides)

### On the AWS side (the caller)
| Appian returns | Meaning | Lambda handling |
|----------------|---------|-----------------|
| 201 / 200 | accepted | done |
| 400 | bad payload | log + send to DLQ (don't retry — it won't fix itself) |
| 401 | bad/missing API key | config error — fix the secret; alert |
| 403 | key valid but no access | the service account lacks group access — fix in Appian |
| 404 | wrong URL alias | fix the URL in the secret |
| 429 / 500 / 503 | throttled / Appian error | **retry** with backoff |
| timeout | slow/unreachable | **retry** with backoff |

**Make retries durable:** put an **SQS queue (+ DLQ)** between the event and the Lambda.
SQS re-drives failed messages automatically and moves poison messages to the DLQ after N
attempts — so a transient Appian outage doesn't lose events. (This is the same
SNS→SQS→Lambda pattern from the blueprint, just calling Appian at the end.)

### On the Appian side (the receiver)
- **Validate** the body first; return **400** on bad input (don't start a process with
  junk data).
- Wrap risky logic so an internal failure returns **500** with a clear message rather
  than a raw error.
- **Log** each call (who/when/what) to a record for audit and troubleshooting.
- Keep the process start **idempotent** — check for an existing order by natural key
  before starting a new process, so a retried call doesn't duplicate work.

---

## 5. Both directions at a glance

| | Appian → AWS | AWS → Appian |
|--|--------------|--------------|
| Who initiates | Appian (user action / process) | AWS event (S3/stream/SNS…) |
| Appian object | **Connected System + Integration** | **Web API** |
| AWS object | API Gateway + Lambda | Lambda (calls Appian) |
| Auth | Appian sends `x-api-key` to AWS | AWS sends `Appian-API-Key` to Appian |
| Secret stored in | Appian Connected System (encrypted) | AWS Secrets Manager |
| Retry/buffer | process-model retry + timer | SQS + DLQ in front of the Lambda |
| Idempotency key | `order_id`+`order_date` | `order_id`+`order_date` |

**Interview one-liner:** *"I integrated Appian and AWS both ways — Appian calls an AWS
API Gateway + Lambda via a Connected System with API-key auth, and AWS events call back
into an Appian Web API (service-account API key stored in Secrets Manager) to start
processes — both secured with least privilege, HTTPS, and idempotent, retried, DLQ-backed
error handling."*

---

## 6. Common gotchas (AWS → Appian)

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 from Appian | missing/typo `Appian-API-Key` header | send the exact header; check the secret |
| 403 from Appian | service account can't see/start the target | add the service account's group to the Web API + process/record security |
| 404 | wrong Web API URL alias | correct the URL in Secrets Manager |
| process starts twice | non-idempotent retry | check by natural key before `a!startProcess` |
| key leaked in logs | printed the header/secret | never log the key; log only status codes |
| works from console test, fails from Lambda | IP allowlist blocks the Lambda | add the NAT/egress IP to Appian's API client allowlist |
