# AI Fitness Coach Dispatch

A serverless **AI fitness coach** on AWS. Users submit their profile & goals; **Claude on Amazon
Bedrock** generates a personalized workout + nutrition plan; an event-driven **"dispatch"** delivers
coaching on demand (API) and on a daily schedule (EventBridge → SNS).

> Based on the NextWork project *"Build a Fitness Coach with Claude"*.

## Architecture
```
User ──▶ API Gateway ──▶ Lambda (coach) ──▶ Amazon Bedrock (Claude)
                              │
                              ▼
                          DynamoDB (users + plans)
                              │
EventBridge Scheduler ─▶ Lambda (dispatch) ─▶ SNS ─▶ user (email/SMS)
```

**Services:** IAM · Amazon Bedrock (Claude) · Lambda · API Gateway · DynamoDB · EventBridge
Scheduler · SNS · CloudWatch.

## Contents
| File | What it is |
|---|---|
| `AI_Fitness_Coach_Dispatch_Guide.pdf` / `.md` | Full step-by-step build guide (IAM → Bedrock → Lambda → API → dispatch), issues & fixes, design rationale |
| `template.yaml` | AWS SAM template — one-command deploy of the whole stack |
| `src/lambda_coach.py` | On-demand coach: builds the prompt, calls Claude via Bedrock, stores the plan |
| `src/lambda_dispatch.py` | Scheduled dispatch: generates & sends today's coaching via SNS |

## Quick start (SAM)
```bash
# 1. Enable Claude model access in the Bedrock console (one-time).
# 2. Get your Bedrock model / inference-profile ID (e.g. us.anthropic.claude-...).
sam build
sam deploy --guided \
  --parameter-overrides ModelId=<YOUR_MODEL_ID> NotifyEmail=you@example.com
# 3. Confirm the SNS email subscription, seed a user in DynamoDB, then:
curl -s -X POST <ApiEndpoint> -H 'Content-Type: application/json' \
  -d '{"userId":"u123"}' | jq -r .plan
```

## Manual (CLI) build
Follow **`AI_Fitness_Coach_Dispatch_Guide.pdf`** — it walks the IAM role, DynamoDB table, both
Lambdas, API Gateway, SNS topic, and the EventBridge daily schedule step by step, with test commands
and a cleanup section.

## Cost
Fully serverless — you pay per request + per Bedrock token. Nothing runs when idle.
Run the **Cleanup** section (or `sam delete`) when done.
