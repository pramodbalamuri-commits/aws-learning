# Connecting the AWS Orders API to an Appian BPM Application

A detailed, practical guide: how to call the AWS API (API Gateway → Lambda →
DynamoDB) from Appian, how to secure it, how to map the data, and how to handle
every exception. Uses the `orders-api` endpoints as the concrete example.

> This is the **Appian → AWS** direction. For the reverse (**AWS events calling into
> an Appian Web API**), see [aws-to-appian-integration.md](aws-to-appian-integration.md).

---

## 0. The two Appian building blocks

Appian calls any external REST API with **two objects**:

1. **Connected System** (type *HTTP*) — holds the **base URL** and the **authentication**
   (our `x-api-key`). Credentials here are stored **encrypted** by Appian — never
   hardcoded in an expression.
2. **Integration** object — built *on* a Connected System. Defines one specific call:
   the relative path, HTTP method, query/path parameters, headers, and body. Returns a
   structured response you check for success/error.

```
Appian Interface / Process  ──▶  Integration object  ──▶  Connected System (base URL + x-api-key)
                                                              │  HTTPS
                                                              ▼
                                              AWS API Gateway ─▶ Lambda ─▶ DynamoDB
```

**Sample values used below**

| Thing | Value |
|-------|-------|
| Base URL | `https://abc123.execute-api.us-west-2.amazonaws.com` |
| Auth header | `x-api-key: <your-secret-key>` |
| Endpoints | `GET /orders`, `GET /orders/{order_id}`, `GET /customers/{customer_id}/orders`, `POST /orders` |

---

## 1. Step 1 — Create the Connected System (HTTP)

In Appian Designer: **New → Connected System → HTTP**.

- **Base URL:** `https://abc123.execute-api.us-west-2.amazonaws.com`
- **Authentication:** choose **API Key**
  - **Key:** `x-api-key`
  - **Value:** *your secret key* (stored encrypted)
  - **Add to:** **Header**
- Save. Give it a name like `AWS Orders API`.

> Why a Connected System (not headers in the integration)? The key is stored securely
> and centrally — change it once here and every integration using it updates. It's also
> the object you lock down with object security so only admins can view/edit the key.

**Environment-specific values:** the base URL and key differ per environment
(dev/test/prod). Use a **per-environment Connected System** (values set at import time)
or drive the base URL from a **Constant** so promotion doesn't leak prod secrets.

---

## 2. Step 2 — Create Integration objects (one per call)

Create a **New → Integration**, pick the `AWS Orders API` Connected System, then:

### 2a. `GET /orders` — list orders
- **Method:** GET
- **Relative Path:** `/orders`
- **Query Parameters:** `limit` = `ri!limit` (optional)
- No body.

### 2b. `GET /orders/{order_id}` — one order
- **Method:** GET
- **Relative Path:** `/orders/{order_id}` — where `{order_id}` is a **path parameter**
  bound to a rule input `ri!orderId`.

### 2c. `GET /customers/{customer_id}/orders` — a customer's orders
- **Method:** GET
- **Relative Path:** `/customers/{customer_id}/orders`, path param `ri!customerId`.

### 2d. `POST /orders` — create an order
- **Method:** POST
- **Relative Path:** `/orders`
- **Body (JSON):** built from rule inputs, e.g.
  ```
  a!toJson(a!map(
    order_id:    ri!orderId,
    order_date:  ri!orderDate,
    customer_id: ri!customerId,
    amount:      ri!amount,
    restaurant:  ri!restaurant
  ))
  ```
- **Header:** `Content-Type: application/json`.

Each integration returns a **dictionary** with these fields you will use everywhere:

| Field | Meaning |
|-------|---------|
| `result` | the parsed JSON body (your orders) |
| `success` | `true` if the call worked (2xx) |
| `statusCode` | the HTTP status (200, 404, 401, 500 …) |
| `error` | present on failure: `{title, message, detail}` |
| `headers` | response headers |

---

## 3. Step 3 — Map the JSON to Appian data

The API returns e.g.:
```json
{ "count": 3, "items": [
    { "order_id": "ord-101", "order_date": "2026-08-01",
      "customer_id": "cust-1", "amount": 29.99, "restaurant": "Pizza Palace" } ] }
```

Two options:
- **Quick:** read fields straight off the dictionary — `local!resp.result.items` is a
  list of maps; `index(item, "amount", 0)`.
- **Clean (recommended):** define a **CDT** (or **Record Type**) `Order` with fields
  `orderId, orderDate, customerId, amount, restaurant`, and map the JSON into it so the
  rest of your app uses typed data. Map `items` → the CDT list in the integration's
  output transformation, or with `a!forEach`.

> Note: field names come back **snake_case** (`order_id`); alias them to your CDT's
> camelCase fields during mapping.

---

## 4. Step 4 — Use it in Appian

### In an Interface (synchronous read)
```
a!localVariables(
  local!resp: rule!AWS_getCustomerOrders(customerId: ri!customerId),
  if(
    local!resp.success,
    a!gridField(
      data: local!resp.result.items,
      columns: {
        a!gridColumn(label: "Order",      value: fv!row.order_id),
        a!gridColumn(label: "Restaurant", value: fv!row.restaurant),
        a!gridColumn(label: "Amount",     value: fv!row.amount)
      }
    ),
    a!richTextDisplayField(value: a!richTextItem(
      text: "Could not load orders: " & local!resp.error.title, color: "NEGATIVE"))
  )
)
```

### In a Process Model (writes / orchestration)
- Drop the **Integration** smart service node (e.g., the `POST /orders` one).
- Map its outputs: save `success` to a process variable `pv!apiSuccess`, `result` to
  `pv!apiResult`, `error` to `pv!apiError`.
- After the node, add an **XOR gateway** on `pv!apiSuccess`:
  - **true →** continue the happy path.
  - **false →** error-handling path (log, notify, retry, or route to a manual task).

---

## 5. Security — in detail

| Concern | How to handle it in Appian |
|---------|----------------------------|
| **Store the API key safely** | In the **Connected System** (encrypted), never in an expression, constant, or process variable. |
| **Who can see/edit the key** | Set **object security** on the Connected System so only admins have Administrator rights; developers get Viewer at most. |
| **Per-environment secrets** | Use environment-specific Connected System values (set on import) so the **prod key never travels in the app package**. |
| **Transport security** | The API is **HTTPS** (TLS) — API Gateway enforces it. Don't call any http:// endpoint. |
| **Least privilege on the AWS side** | The API key (via the Lambda authorizer) and the Lambda's IAM role only allow the intended actions — reads and the specific writes, scoped to the one table. |
| **Don't log secrets** | Never write the key or full auth header to Appian logs / process variables you display. |
| **Rotate keys** | Change the key in the Connected System when rotating on AWS — one place, no redeploy of integrations. |
| **User-level auth (optional)** | If you need *per-user* identity (not a shared key), put **Amazon Cognito** in front and use Appian's **OAuth 2.0** Connected System instead of a static key. |
| **AWS IAM (SigV4) auth** | Appian does **not** natively sign SigV4 requests. So keep the **API-key + Lambda authorizer** approach (what we built), or front the API with a small proxy that handles signing. |
| **Network** | For private/VPC-only access, expose the API through a private API Gateway + VPC endpoint and reach it over a VPN/Direct Connect; otherwise the public HTTPS endpoint + key is fine. |

---

## 6. Exception handling — in detail

Every integration tells you what happened via `success`, `statusCode`, and `error`.
Handle each case deliberately.

### 6a. Map the HTTP status codes

| Status | Meaning | Cause | Appian handling |
|--------|---------|-------|-----------------|
| **200 / 201** | OK / Created | success | read `result` |
| **400** | Bad Request | invalid/missing fields in a POST | show a validation message; fix the payload |
| **401** | Unauthorized | **missing** `x-api-key` | config error — check the Connected System has the header |
| **403** | Forbidden | **wrong** `x-api-key` | key mismatch — rotate/fix the key in the Connected System |
| **404** | Not Found | order/customer doesn't exist | show "not found" to the user (not an error toast) |
| **429** | Too Many Requests | API Gateway throttling | back off and **retry** (see below) |
| **500 / 502 / 503** | Server error | Lambda/DynamoDB issue | retry a few times; if it persists, route to an exception/manual task and alert |
| **timeout** | no response in time | network/Lambda cold start | retry with backoff; raise the Connected System timeout if consistent |

### 6b. Check it in an expression / interface
```
a!localVariables(
  local!resp: rule!AWS_getOrders(),
  a!match(
    value: local!resp.statusCode,
    whenTrue: local!resp.success,      then: /* use local!resp.result.items */ ,
    equals: 404,                       then: "No orders found.",
    equals: 401, then: "Auth not configured.",
    equals: 403, then: "Invalid API key.",
    default: "Service error (" & local!resp.statusCode & "): " & local!resp.error.message
  )
)
```

### 6c. Check it in a Process Model
- **XOR gateway** on `pv!apiSuccess`.
- On the error branch:
  - **Log** the `error` (title/message/detail) to a tracking record or a!writeToDataStore.
  - **Retry** transient failures (429/500/timeout): loop back to the integration node up
    to N times with a **Timer** delay (exponential backoff — 2s, 4s, 8s). Cap the retries.
  - **Escalate** after retries: create a **manual task** for support with the payload +
    error, or send a notification.
- Add a **boundary/timer event** so a hung call can't stall the process forever.

### 6d. Retry + idempotency (important for POST)
- Retrying a **GET** is always safe.
- Retrying a **POST** could create a **duplicate** order. Make it safe by using a stable
  **natural key** (`order_id` + `order_date`) — the API's `put_item` overwrites the same
  key rather than duplicating, so a retry is idempotent. (This is exactly why the table
  uses a composite key.)

### 6e. Observability
- Store each failed call's `statusCode` + `error` in a log/record so you can report on
  API health.
- On the AWS side, CloudWatch already logs the Lambda; correlate by a request id if you
  pass one.

---

## 7. Quick end-to-end recipe

1. **Connected System** `AWS Orders API` — base URL + `x-api-key` (API Key auth, header).
2. **Integrations**: `AWS_getOrders`, `AWS_getOrderById`, `AWS_getCustomerOrders`,
   `AWS_createOrder`.
3. **CDT/Record Type** `Order` to hold the mapped data.
4. **Interface**: call the read integration, check `success`, bind `result.items` to a grid.
5. **Process Model**: call the write integration, XOR on `success`, retry transient
   errors with a timer, escalate on repeated failure.
6. **Security**: key only in the Connected System, object security locked down,
   per-environment values, HTTPS.

---

## 8. Common gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| Every call 401 | header not sent | Connected System auth must add `x-api-key` to **Header** |
| Every call 403 | key mismatch | the value in the Connected System must equal the API's expected key |
| `result` is null but statusCode 200 | response not JSON / mis-mapped | ensure `Content-Type: application/json`; read `result.items` not `result` |
| numbers look odd | JSON numbers vs Appian types | cast `amount` to Decimal/Number when mapping |
| POST duplicates on retry | non-idempotent retry | use the natural key (`order_id`+`order_date`) so re-POST overwrites |
| Works in dev, 403 in prod | wrong per-environment key | set the prod key in the prod Connected System |
| Intermittent timeouts | Lambda cold start / network | raise the Connected System timeout; add retry-with-backoff |
