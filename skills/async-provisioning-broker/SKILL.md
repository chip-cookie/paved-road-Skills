---
name: async-provisioning-broker
description: Use when building a self-service provisioning API where requests trigger slow or failure-prone infrastructure work (DNS records, CDN distributions, load balancers, external API calls). Implements the API, queue, worker, state store, and status-polling pattern with idempotency, retries, and dead-letter handling.
---

# Async Provisioning Broker

## Overview

A provisioning API must never do slow infrastructure work inside the HTTP request.
The API validates, records intent, enqueues a job, and returns immediately. Workers do
the work and write status. Clients poll (or subscribe) for the result.

```
client --POST--> API --(validate, write PENDING)--> state store
                  |--enqueue job--> queue --> worker --(provision DNS/CDN/LB...)
client <--202 + id--|                                   |
client --GET /id--> API --read--> state store <--write SUCCEEDED/FAILED--
```

Reference stack from the source talk: FastAPI + AWS SQS + DynamoDB. The pattern is
stack-agnostic (Postgres + a job table, Redis streams, Pub/Sub + Firestore, etc.).

## When to Use

- Provisioning takes more than ~1s, calls third-party APIs, or can partially fail
- You need developers to self-serve infra without tickets
- You are replacing a synchronous "create" endpoint that times out

## Process

1. **Define the contract first.** Write the OpenAPI spec for `POST /instances`,
   `GET /instances/{id}`, `DELETE /instances/{id}`. Generating routes from the spec
   (connexion-style) or generating the spec from code (FastAPI) are both fine; pick one
   source of truth.
2. **Model status as a state machine.** Minimum states:
   `PENDING -> IN_PROGRESS -> SUCCEEDED | FAILED`, plus `DELETING -> DELETED`.
   Only workers move a record out of `PENDING`. Store `last_error`, `attempts`,
   `updated_at`, and the normalized request.
3. **Validate synchronously, provision asynchronously.** The API runs all guardrails
   (see `guardrail-validation`) before enqueuing. Reject bad input with 4xx; never
   enqueue a job you already know will fail.
4. **Make every step idempotent.** Require a client-supplied idempotency key or derive
   one from the resource name. Workers must tolerate duplicate delivery (at-least-once
   queues): "create DNS record" becomes "ensure DNS record exists with value X".
5. **Write intent before enqueue.** Persist the `PENDING` record, then enqueue. If
   enqueue fails, a sweeper re-enqueues stale `PENDING` records.
6. **Bound retries; dead-letter the rest.** Exponential backoff with jitter, max N
   attempts, then move to a DLQ and mark `FAILED` with a human-readable error.
7. **Return 202 + a status URL.** Include `Retry-After` on `GET` while not terminal.
8. **Instrument.** Queue depth, job age, success/failure rate per provider,
   time-to-SUCCEEDED percentiles.

See `references/fastapi-sqs-dynamodb.md` for a minimal reference implementation.

## Red Flags

- The `POST` handler calls the DNS/CDN/cloud API directly
- Workers use "create" semantics and crash on "already exists"
- Status is inferred by querying the cloud provider instead of read from the state store
- No DLQ, or a DLQ nobody alerts on
- Clients poll in a tight loop with no `Retry-After`

## Common Mistakes

- Enqueuing before persisting, so a fast worker cannot find the record
- Putting the entire mutable request in the queue message instead of an ID + version
- Forgetting the delete path: deprovisioning needs the same async treatment
