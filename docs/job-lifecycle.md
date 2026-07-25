# Job lifecycle

## Model

A **job** is the durable user intent. A **plan revision** describes proposed work. An **attempt** is one execution of an approved plan. Retries create attempts; they do not reset or overwrite job history.

## States

```text
RECEIVED -> VALIDATING -> PLANNING -> AWAITING_APPROVAL -> QUEUED
   |            |            |               |              |
   +------------+------------+---------------+--------------+-> CANCELLED
                |            |               |
                +----------> BLOCKED <-------+
                                           QUEUED -> RUNNING
                                                        |
                                         +--------------+-------------+
                                         |              |             |
                                      PAUSED       SUCCEEDED       FAILED
                                         |              |             |
                               AWAITING_APPROVAL         |          RETRY_WAIT
                                         |              |             |
                                         +-> RUNNING     |          QUEUED
                                                        |
                                           COMPLETED / CANCELLED
```

Canonical state names may be refined when persistence is implemented. The essential distinction is between execution success (`SUCCEEDED`) and workflow completion (`COMPLETED`, after required external reconciliation such as recording a PR).

## Transition rules

| From | To | Trigger / guard |
|---|---|---|
| `RECEIVED` | `VALIDATING` | Durable request exists; actor and idempotency established |
| `VALIDATING` | `PLANNING` | Repository/project assignment and request schema valid |
| `PLANNING` | `AWAITING_APPROVAL` | Versioned plan requires one or more approvals |
| `PLANNING` | `QUEUED` | Policy allows the exact plan without human approval |
| `AWAITING_APPROVAL` | `QUEUED` | All required, unexpired action-bound approvals granted |
| `QUEUED` | `RUNNING` | Attempt and fenced worker lease committed |
| `RUNNING` | `PAUSED` | Safe checkpoint reached or operator pause requested |
| `RUNNING`/`PAUSED` | `AWAITING_APPROVAL` | New capability/action requires escalation |
| `RUNNING` | `SUCCEEDED` | Worker result manifest accepted and attempt finalized |
| `RUNNING` | `FAILED` | Non-retryable failure or retry budget exhausted |
| `RUNNING` | `RETRY_WAIT` | Retryable failure; no ambiguous unsafe side effect |
| `RETRY_WAIT` | `QUEUED` | Backoff elapsed and new attempt can be created |
| non-terminal | `BLOCKED` | Required dependency/configuration unavailable; operator action needed |
| eligible non-terminal | `CANCELLED` | Authorized cancellation; worker revoked and reconciled |
| `SUCCEEDED` | `COMPLETED` | Required provider records/artifacts reconciled |

A transition command checks current version, policy, actor, lease/fencing token where applicable, and invariants in one database transaction. It updates current state, appends events/audit, and inserts outbox notifications atomically.

## Plans and approvals

Plans are immutable revisions. Each has a content digest, requested capabilities, repository/base commit, expected outputs, risk notes, and provenance. Approval binds to a specific plan/action digest. Editing a plan creates a new revision and invalidates incompatible approvals.

## Idempotency and duplicate delivery

Create-job accepts a client-scoped idempotency key. Repeating an identical request returns the existing job; reusing a key with a different payload is a conflict. Transition commands and callbacks use command/event IDs. Consumers record processed IDs transactionally.

## Cancellation

Cancellation is a durable request, not merely `docker stop`. The controller marks cancellation intent, revokes grants, signals the worker, waits a bounded grace period, force-removes if needed, finalizes the attempt, and reconciles remote side effects. Terminal history remains immutable.

## Retry policy

Failures are classified: infrastructure transient, provider transient, worker/tool failure, invalid request, policy denial, security violation, timeout/resource limit, or ambiguous external side effect. Only allow-listed classes retry automatically. Backoff is bounded and jittered. Attempts have independent logs/artifacts and an incrementing fencing token. Security violations and ambiguous pushes/deployments require human review.

## Recovery

After restart, a reconciler scans non-terminal jobs and attempts. Expired leases are fenced; actual container/provider state is inspected; stale attempts are failed or recovered according to policy. Outbox delivery resumes. No recovery path rewrites prior events. An operator can replay a safe command or create a retry with attribution and rationale.

## Required event examples

`job.received`, `job.validated`, `plan.created`, `approval.requested`, `approval.decided`, `job.queued`, `attempt.created`, `worker.leased`, `attempt.started`, `capability.requested`, `job.paused`, `artifact.recorded`, `attempt.succeeded`, `attempt.failed`, `job.retry_scheduled`, `job.cancel_requested`, `job.cancelled`, `job.completed`.
