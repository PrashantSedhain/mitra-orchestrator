# Architecture

## Purpose and invariants

Mitra Orchestrator is the authoritative, durable controller for AI software-engineering work. Conversational systems plan and request work; Codex workers execute bounded tasks. Neither may independently mutate durable control-plane truth.

Core invariants:

1. PostgreSQL is the source of truth; in-memory state is a cache only.
2. Every state transition is transactional, validated, attributed, and auditable.
3. One active lease owns a worker attempt; expired leases are recoverable.
4. Workers are disposable and reconstruct context from durable records and artifacts.
5. Untrusted retrieved content is data, not instructions.
6. Permissions are deny-by-default, least-privilege, time-bound, and job-scoped.
7. External side effects use idempotency keys and are reconciled after ambiguity.

## System context

```text
                           TRUSTED OPERATORS
                                  |
 Slack  ChatGPT  Hermes  MCP clients  Future clients
   |       |       |          |             |
   +-------+-------+----------+-------------+
                   adapters / HTTPS
                          |
+-------------------------v------------------------------------+
|                       CONTROL PLANE                           |
| Controller API | Job FSM | Policy/Approvals | Event Log      |
| Repository Registry | Artifacts | Integrations | Worker Mgr  |
+-------------------------+------------------------------------+
                          | SQL/TLS
                    +-----v------+
                    | PostgreSQL |
                    +-----+------+
                          |
                   leased runtime spec
                          |
+-------------------------v------------------------------------+
| disposable Docker worker (untrusted workload boundary)       |
| checked-out repo + Codex + constrained tools + artifact sink |
+---------+----------------------+------------------------------+
          |                      |
     Git provider          Jira/Confluence/log sources
```

## Components

### Controller API

The versioned HTTP REST interface accepts authenticated commands and serves queries. It validates schemas, establishes actor identity and tenant/project scope, supplies idempotency keys, invokes domain services, and returns durable resource identifiers. Command endpoints never declare success before the database transaction commits.

### PostgreSQL database

PostgreSQL stores jobs, attempts, leases, workers, repositories, plans, approvals, grants, credential references, branches, pull requests, artifacts, integration cursors, outbox records, events, and audit records. Row-level constraints and optimistic versions defend invariants. Credentials themselves should live in a secret manager; PostgreSQL stores encrypted references and metadata.

### Job state machine

The job aggregate defines legal transitions and terminal states. State changes occur through named domain commands, never arbitrary updates. A job has one or more attempts; retrying creates a new attempt rather than erasing history. See [job lifecycle](job-lifecycle.md).

### Event log

An append-only event stream records domain facts with event ID, aggregate ID/version, actor, correlation/causation IDs, timestamp, and redacted payload. Phase 1 uses a relational event/audit schema alongside current-state tables; it is not full event sourcing. A transactional outbox enables reliable adapter notifications.

### Worker manager

The worker manager reconciles desired attempts with actual containers. It acquires leases, creates containers from allow-listed image digests, injects a signed runtime specification, renews heartbeats, captures exit status, and cleans up. It must tolerate duplicate reconciliation and controller restarts.

### Worker runtime contract

A worker receives immutable job/attempt IDs, repository and base revision, plan revision, allowed capabilities, resource limits, credential handles, callback endpoint/token, and artifact upload instructions. It emits heartbeats, structured progress/events, a result manifest, logs, and a final status. It cannot directly update control-plane tables.

### Repository registry

The registry maps stable repository IDs to provider coordinates, clone URLs, default branches, allowed base refs, ownership, project scope, credential policy, and workspace rules. Jobs reference registry IDs—not arbitrary clone URLs supplied in prompts.

### Knowledge retrieval layer

The layer retrieves private project knowledge from a store outside customer repositories. It preserves source identity, access labels, timestamps, and provenance, applies project/tenant filtering, and returns explicitly delimited untrusted excerpts. Retrieval never grants execution permission.

### Policy and approval engine

Policy evaluates actor, job, repository, requested capability, risk, environment, and current approvals. Decisions are allow, deny, or require-approval, with reason and policy version recorded. Approvals bind to a precise action digest, scope, expiry, and approver; changing the action invalidates approval.

### MCP adapter

MCP exposes controller tools/resources to compatible clients. It translates MCP calls into authenticated REST commands and queries. It holds no authoritative job state and cannot bypass policy. See ADR 0004.

### Slack adapter

The Slack adapter verifies signatures, maps Slack identities/channels to Mitra actors/projects, normalizes requests, and posts status updates from durable outbox events. Interactive approvals require authorization checks beyond possession of a button URL.

### GitHub integration

GitHub integration uses a GitHub App where possible, verifies webhooks, manages installation-scoped tokens, reconciles branches and pull requests, and records external IDs/URLs. Push and PR creation are explicit capabilities, not implicit worker rights.

### Jira integration

Jira integration retrieves issue context and may update linked issues through scoped service credentials. Ticket descriptions and comments are untrusted input. Integration cursors and request IDs make polling/webhooks idempotent.

### Confluence integration

Confluence integration retrieves access-controlled pages through the knowledge layer with source attribution. Page content is untrusted and cannot change policies, plans, or tool permissions.

### PostgreSQL log-analysis tools

Read-only analysis tools query allow-listed databases/views using dedicated roles, statement timeouts, row limits, redaction, and complete query audit. They do not expose controller PostgreSQL credentials to workers and never execute SQL copied from untrusted content without validation.

### Backup and recovery

Initial operations use encrypted PostgreSQL base backups plus WAL archiving where available, object-storage versioning for artifacts, configuration backups without plaintext secrets, and documented restore drills. Recovery validates checksums, database migrations, event/outbox consistency, worker lease expiry, and reconciliation of ambiguous external side effects. Recovery objectives will be set before production and tested, not assumed.

## Primary flows

### Submit and execute

1. Client authenticates to an adapter or directly to REST.
2. Controller validates repository assignment and creates a job idempotently.
3. Planning produces a versioned plan; policy determines required approvals.
4. An approved job becomes dispatchable; worker manager creates an attempt and lease.
5. A disposable worker checks out the pinned base revision and executes allowed steps.
6. Worker uploads artifacts/events and reports completion.
7. Controller reconciles branch/PR state and commits the terminal transition.
8. Outbox consumers notify clients. All steps retain correlation IDs.

### Permission escalation

1. Worker pauses and requests one named capability with justification and action digest.
2. Policy denies, allows under existing policy, or creates an approval request.
3. Authorized human approves/rejects; the decision is immutable and audited.
4. Controller issues a short-lived scoped grant. The worker never self-grants.

## Consistency and concurrency

- Domain rows carry versions; transitions use compare-and-swap or row locks.
- Job submission and external callbacks require idempotency keys.
- Worker attempts use fencing tokens so a stale worker cannot write after lease loss.
- Database commit plus transactional outbox avoids dual-write loss.
- Reconciliation compares durable intent to Docker and provider reality.

## Deployment evolution

Docker Compose on one dedicated Linux host is the initial deployment. Component boundaries avoid assuming Compose forever: API and reconcilers can later scale separately, PostgreSQL can move to managed/HA infrastructure, and Docker runtime implementations can be replaced behind the worker-manager interface.

## Explicit non-goals for Phases 0–1

- Production worker dispatch
- Autonomous permission escalation
- Multi-host scheduling or Kubernetes
- Full GitHub/Jira/Confluence/Slack behavior
- Storing customer knowledge in source repositories
- A UI beyond API documentation
