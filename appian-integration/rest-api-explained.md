# Understanding This API — REST APIs in Simple Language

A beginner-friendly explanation of what this project is, using a real use case, and
how building REST APIs compares between **Java** and **Python**.

---

## 1. What is an API? (in plain English)

An **API** is a messenger between two programs. Think of a **waiter in a restaurant**:

- You (the customer) don't walk into the kitchen — you tell the **waiter** what you want.
- The waiter takes your order to the **kitchen** and brings back your food.

An API is that waiter. Your app tells the API what it wants, the API talks to the
database, and brings back the answer. You never touch the database directly.

## 2. What does "REST" mean?

**REST** is just the most common *style* for web APIs. A RESTful API follows a few
simple rules:

- **Everything is a "resource" with a web address (URL).**
  `/orders` = all orders, `/orders/ord-101` = one specific order.
- **You use HTTP "verbs" to say what you want:**
  | Verb | Meaning | Example |
  |------|---------|---------|
  | `GET` | read | get an order |
  | `POST` | create | add a new order |
  | `PUT`/`PATCH` | update | change an order |
  | `DELETE` | remove | delete an order |
- **It talks in JSON** (easy-to-read text data).
- **It's stateless** — each request stands on its own.

> REST is a *concept*, not a language. You can build a REST API in Java, Python,
> JavaScript, Go — anything. This project builds one in **Python**.

---

## 3. The use case (why this API exists)

Imagine a **food-delivery company**. Every order is stored in a database (DynamoDB).
Lots of different programs need to **read** that order data:

- the **customer's mobile app** ("show me my past orders"),
- the **customer-support tool** ("look up order ord-101"),
- an **internal dashboard** ("how many orders did this customer place?").

We do **not** want each of those connecting to the database directly — that's messy
and insecure. Instead we put **one REST API in front of the database**. Everyone asks
the API, and the API is the single, controlled door to the data.

```
 Mobile app  ┐
 Support tool ├──▶  Orders REST API  ──▶  DynamoDB (orders)
 Dashboard   ┘
```

That "Orders REST API" is exactly this project.

---

## 4. Java vs Python — same idea, different tools

REST APIs work the same way in both languages; only the framework differs.

| In Java you'd use… | In Python you'd use… |
|--------------------|----------------------|
| **Spring Boot** (most common) | **FastAPI** (modern, what we used) |
| JAX-RS / Jersey | Flask (lightweight) |
| | Django REST Framework (full-featured) |
| Runs on Tomcat | Runs on **uvicorn** |

### The same endpoint, side by side

**Java — Spring Boot:**
```java
@RestController
@RequestMapping("/orders")
public class OrderController {

    @GetMapping("/{orderId}")
    public Order getOrder(@PathVariable String orderId) {
        return service.findById(orderId);
    }
}
```

**Python — FastAPI (this project):**
```python
@app.get("/orders/{order_id}")
def get_order(order_id: str):
    return get_order_from_dynamodb(order_id)
```

The ideas are **identical** — only the words change:

| Concept | Spring Boot (Java) | FastAPI (Python) |
|---------|--------------------|------------------|
| Mark a REST endpoint | `@RestController` + `@GetMapping` | `@app.get(...)` |
| Path variable | `@PathVariable String orderId` | `order_id: str` |
| Query parameter | `@RequestParam int limit` | `limit: int = Query(25)` |
| Request body | `@RequestBody Order order` | a Pydantic model |
| Auto JSON | Jackson | built in (return a dict) |
| API docs page | add Springdoc | **built in** at `/docs` |

**Why FastAPI is often called "the Spring Boot of Python":** decorator-based routing
(like annotations), automatic input validation, and a free interactive docs page.

---

## 5. This API's endpoints (in simple terms)

| Method | URL | What it does | Use-case example |
|--------|-----|--------------|------------------|
| GET | `/` | health check | "is the API up?" |
| GET | `/orders` | list orders | dashboard shows recent orders |
| GET | `/orders/{order_id}` | one order | support looks up `ord-101` |
| GET | `/customers/{customer_id}/orders` | a customer's orders | app shows "my order history" |

*(The serverless version of this API also has `POST /orders` to create an order.)*

Behind the scenes:
- `/orders` uses a DynamoDB **Scan** (reads the table).
- `/orders/{order_id}` uses a **Query** on the main key (fast, targeted).
- `/customers/{customer_id}/orders` uses a **Query on a secondary index (GSI)** —
  because the table's main key is `order_id`, we need an index to look up by customer.

---

## 6. How one request flows (with the use case)

A customer opens the app and taps **"My Orders"**:

1. The app sends `GET /customers/cust-1/orders` to the API.
2. FastAPI receives it and reads `customer_id = "cust-1"` from the URL.
3. The code asks DynamoDB (via `boto3`) for that customer's orders (using the index).
4. DynamoDB returns the matching orders.
5. The API converts them to JSON and sends them back.
6. The app shows the customer their order list.

The customer never sees the database — just clean JSON from the API. That's the whole
point of putting a REST API in front.

---

## 7. Run it yourself

```bash
cd orders-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed_data.py                 # create the table + sample data (once)
uvicorn app.main:app --reload       # start the API
```

Then open **http://127.0.0.1:8000/docs** in your browser — a friendly page where you
can click "Try it out" on each endpoint and see live responses. Or:

```bash
curl http://127.0.0.1:8000/orders
curl http://127.0.0.1:8000/customers/cust-1/orders
```

---

**In one sentence:** *This project is a REST API — the same kind you'd build with
Spring Boot in Java — written in Python with FastAPI, acting as the single, safe door
between apps and the orders database.*
