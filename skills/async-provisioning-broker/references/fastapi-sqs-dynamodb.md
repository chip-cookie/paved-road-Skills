# Reference: FastAPI + SQS + DynamoDB broker

Minimal, illustrative. Adapt names, auth, and error handling to your codebase.

## API (`api.py`)

```python
import json, os, time, uuid
import boto3
from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel, Field

app = FastAPI()
sqs = boto3.client("sqs")
table = boto3.resource("dynamodb").Table(os.environ["TABLE"])
QUEUE_URL = os.environ["QUEUE_URL"]

class ProvisionRequest(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9-]{3,40}$")
    origin: str            # validated further by guardrails
    regions: list[str]

@app.post("/instances", status_code=202)
def create(req: ProvisionRequest, idempotency_key: str = Header(...)):
    validate_or_400(req)                       # see guardrail-validation skill
    instance_id = str(uuid.uuid5(uuid.NAMESPACE_URL, idempotency_key))
    now = int(time.time())
    try:
        table.put_item(
            Item={"id": instance_id, "status": "PENDING", "request": req.model_dump(),
                  "attempts": 0, "created_at": now, "updated_at": now},
            ConditionExpression="attribute_not_exists(id)",   # idempotent create
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return {"id": instance_id, "status_url": f"/instances/{instance_id}"}
    sqs.send_message(QueueUrl=QUEUE_URL,
                     MessageBody=json.dumps({"id": instance_id, "op": "provision"}))
    return {"id": instance_id, "status_url": f"/instances/{instance_id}"}

@app.get("/instances/{instance_id}")
def status(instance_id: str, response: Response):
    item = table.get_item(Key={"id": instance_id}).get("Item")
    if not item:
        raise HTTPException(404)
    if item["status"] not in ("SUCCEEDED", "FAILED", "DELETED"):
        response.headers["Retry-After"] = "5"
    return {k: item.get(k) for k in ("id", "status", "last_error", "updated_at")}
```

## Worker (`worker.py`)

```python
MAX_ATTEMPTS = 5

def handle(msg):
    job = json.loads(msg["Body"])
    item = table.get_item(Key={"id": job["id"]})["Item"]
    if item["status"] in ("SUCCEEDED", "DELETED"):
        return  # duplicate delivery; already done
    set_status(job["id"], "IN_PROGRESS")
    try:
        ensure_dns_record(item["request"])        # each step is "ensure", not "create"
        ensure_cdn_distribution(item["request"])
        set_status(job["id"], "SUCCEEDED")
    except RetryableError as e:
        attempts = incr_attempts(job["id"])
        if attempts >= MAX_ATTEMPTS:
            set_status(job["id"], "FAILED", last_error=str(e))
            return  # let the message go; it is recorded as FAILED
        raise  # message becomes visible again -> retried with SQS redrive/backoff
    except PermanentError as e:
        set_status(job["id"], "FAILED", last_error=str(e))
```

Configure the SQS queue with a redrive policy (`maxReceiveCount`) to a DLQ and alarm
on DLQ depth > 0.

## Sweeper

Every few minutes: find records in `PENDING` older than 2x the normal enqueue latency
and re-send their message. This covers "persisted but enqueue failed".
