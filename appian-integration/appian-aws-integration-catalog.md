# AWS + Appian — All Integration Points (Catalog)

Where and how AWS services can be used in an Appian BPM application. Companion to
[appian-integration.md](appian-integration.md) (Appian → AWS) and
[aws-to-appian-integration.md](aws-to-appian-integration.md) (AWS → Appian).

---

## The 4 ways Appian integrates with AWS

Almost every AWS↔Appian integration uses one of these mechanisms:

| # | Mechanism | Best for |
|---|-----------|----------|
| 1 | **Connected System + Integration (REST)** | calling an HTTPS endpoint — an API Gateway+Lambda wrapper, or a service exposed as REST |
| 2 | **Appian AWS plugins** (from AppMarket) | services that need AWS **SigV4 signing** (e.g., the Amazon S3 plugin) done for you |
| 3 | **JDBC Data Source** | direct relational access to **RDS / Aurora / Redshift** (Record Types, `a!queryEntity`, stored procedures) |
| 4 | **Appian Web API** (inbound) | AWS **calls into** Appian to push data / start a process |

> ⚠️ **Key limitation to remember:** Appian's HTTP Connected System **cannot natively
> sign AWS SigV4** requests. So to call a *raw* AWS service API you either (a) use an
> **Appian AWS plugin** that signs it, or (b) **wrap the service behind API Gateway +
> Lambda** with simple auth (API key) — the portable pattern in this repo. Databases use
> JDBC directly (no signing needed).

---

## The catalog — by category

### Storage & documents
| Service | What you do with it in Appian | How |
|---------|-------------------------------|-----|
| **S3** | store/retrieve Appian documents, exchange files, archive, offload large uploads/downloads | Amazon S3 **plugin** (SigV4) or API Gateway+Lambda with **presigned URLs** |
| **KMS** | encryption of that data (at rest) | transparent (e.g., S3 SSE-KMS) — Appian doesn't call KMS directly |

### Compute & logic
| Service | Use in Appian | How |
|---------|---------------|-----|
| **Lambda** | run custom code — heavy calculations, transformations, calling other systems | expose via **API Gateway**, call from a Connected System |
| **Step Functions** | orchestrate a multi-step AWS workflow that Appian kicks off (or that calls Appian at the end) | API Gateway → Step Functions; callback via Web API |

### Data
| Service | Use in Appian | How |
|---------|---------------|-----|
| **RDS / Aurora** | shared relational data (orders, customers) read/written by Appian | **JDBC Data Source** → Record Types / `a!queryEntity` / stored procedures |
| **DynamoDB** | high-scale key-value data (live order state) | via **API Gateway + Lambda** (this repo's `orders-api`) |
| **Redshift** | data-warehouse reporting/dashboards in Appian | **JDBC** (Redshift driver) |
| **Athena** | SQL over S3 data for reports | API Gateway + Lambda (run query → return results) |
| **Glue** | ETL that *prepares* data Appian then reads | Appian reads the output (RDS / S3 / Athena) |

### Messaging & events
| Service | Use in Appian | How |
|---------|---------------|-----|
| **SQS** | decoupled async work between Appian and AWS | send via API/plugin; consume via Lambda → Appian Web API |
| **SNS** | broadcast/notify on events | Appian publishes (API GW) or receives (SNS → Lambda → Web API) |
| **EventBridge** | route AWS events to trigger Appian processes | rule → Lambda → Appian Web API |
| **Kinesis** | high-volume streaming ingestion | process the stream, then push summaries to Appian |

### AI / ML (very high value with Appian)
| Service | Use in Appian | How |
|---------|---------------|-----|
| **Textract** | extract text/fields from documents (invoices, forms) → intelligent document processing | API Gateway + Lambda (or plugin) → feed the process |
| **Comprehend** | NLP — sentiment, entities, **PII detection**, classification | API Gateway + Lambda |
| **Rekognition** | image/video analysis (ID verification, object/face detection) | API Gateway + Lambda |
| **Transcribe / Translate / Polly** | speech-to-text, translation, text-to-speech | API Gateway + Lambda |
| **Bedrock** | generative AI (LLMs) — summarize, draft, extract, chat | API Gateway + Lambda (Appian also has native AI features) |

### Security & identity
| Service | Use in Appian | How |
|---------|---------------|-----|
| **Cognito** | user authentication / **SSO** for Appian | Appian **SAML / OIDC** with Cognito as the identity provider |
| **Secrets Manager** | securely store the credential AWS uses to call Appian (or other secrets) | Lambda reads it at runtime (see the reverse guide) |
| **IAM** | scope what the AWS side of each integration can do | least-privilege roles on the Lambdas/services |

### Communication & monitoring
| Service | Use in Appian | How |
|---------|---------------|-----|
| **SES** | high-volume transactional email | API Gateway + Lambda or SMTP (Appian also has native email) |
| **CloudWatch** | logs/metrics/alarms for the AWS side of the integration | monitor the Lambdas/API; alarm on errors |

---

## Decision guide — pick the method

| What you want to do | Use |
|---------------------|-----|
| Read/write a **relational** DB shared with other apps | **JDBC Data Source** (RDS/Aurora/Redshift) |
| Store/fetch **files/documents** | **S3** (plugin or presigned URLs via Lambda) |
| Call a **custom** AWS capability or a raw AWS service | **API Gateway + Lambda** wrapper, call via Connected System |
| **Single sign-on** for Appian users | **Cognito** (SAML/OIDC) |
| **AWS event** should start an Appian process | **Lambda → Appian Web API** (SQS+DLQ for durability) |
| **Async / decoupled** processing | **SQS/SNS** |
| **Document extraction / AI** | **Textract / Comprehend / Bedrock** via API Gateway + Lambda |
| **Reporting** over big data | **Redshift (JDBC)** or **Athena (via Lambda)** |

---

## Summary

Most AWS-in-Appian integration boils down to four patterns:
1. **JDBC** for relational databases (RDS/Aurora/Redshift) — direct.
2. **Connected System REST** for everything else — via an **API Gateway + Lambda
   wrapper** (portable, simple auth) or an **AWS plugin** (SigV4).
3. **Web API** for AWS pushing *into* Appian.
4. **Cognito SSO** for identity.

**Interview one-liner:** *"Appian integrates with AWS four ways — JDBC to RDS/Aurora/
Redshift, REST Connected Systems to API-Gateway-wrapped services (S3, DynamoDB, Lambda,
AI like Textract/Comprehend/Bedrock), inbound Appian Web APIs for AWS-triggered
processes, and Cognito for SSO — with the SigV4-signing caveat handled by plugins or the
API Gateway wrapper."*
