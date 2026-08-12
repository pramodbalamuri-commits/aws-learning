import json, os, boto3
from datetime import datetime, timezone

bedrock  = boto3.client("bedrock-runtime")
ddb      = boto3.resource("dynamodb")
table    = ddb.Table(os.environ.get("USERS_TABLE", "FitnessCoachUsers"))
MODEL_ID = os.environ["MODEL_ID"]   # e.g. us.anthropic.claude-... (from Bedrock console)

SYSTEM = (
    "You are an expert, encouraging personal fitness coach. "
    "Given a user's profile, produce a safe, specific, actionable plan. "
    "Respect injuries and time constraints. Never give medical advice; "
    "add a one-line disclaimer to consult a doctor before starting."
)


def build_prompt(u):
    return (
        f"Create a personalized weekly fitness and nutrition plan.\n\n"
        f"Name: {u.get('name')}\nAge: {u.get('age')}\nWeight: {u.get('weightKg')} kg\n"
        f"Fitness level: {u.get('level')}\nGoal: {u.get('goal')}\n"
        f"Constraints: {u.get('constraints')}\n\n"
        f"Return: (1) a 4-week overview, (2) a day-by-day week-1 workout split, "
        f"(3) simple nutrition guidance, (4) one motivational tip. Use clear headings."
    )


def ask_claude(prompt):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(body))
    payload = json.loads(resp["body"].read())
    return "".join(
        b.get("text", "") for b in payload.get("content", []) if b.get("type") == "text"
    )


def handler(event, context):
    body = json.loads(event["body"]) if isinstance(event.get("body"), str) else event
    user_id = body.get("userId", "u123")

    item = table.get_item(Key={"userId": user_id}).get("Item")
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "user not found"})}

    plan = ask_claude(build_prompt(item))

    table.update_item(
        Key={"userId": user_id},
        UpdateExpression="SET lastPlan = :p, updatedAt = :t",
        ExpressionAttributeValues={":p": plan, ":t": datetime.now(timezone.utc).isoformat()},
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"userId": user_id, "plan": plan}),
    }
