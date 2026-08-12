import os, json, boto3

lam   = boto3.client("lambda")
sns   = boto3.client("sns")
ddb   = boto3.resource("dynamodb")
table = ddb.Table(os.environ.get("USERS_TABLE", "FitnessCoachUsers"))
TOPIC = os.environ["TOPIC_ARN"]
COACH = os.environ.get("COACH_FUNCTION", "FitnessCoach")


def handler(event, context):
    users = table.scan().get("Items", [])
    sent = 0
    for u in users:
        resp = lam.invoke(FunctionName=COACH, Payload=json.dumps({"userId": u["userId"]}))
        plan = json.loads(resp["Payload"].read()).get("plan", "")
        if not plan:
            continue
        sns.publish(
            TopicArn=TOPIC,
            Subject=f"Your coaching for today, {u.get('name', '')}",
            Message=plan[:2000],
        )
        sent += 1
    return {"sent": sent}
