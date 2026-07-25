# Development plan

## Delivery principles

Build vertical, recoverable slices; keep PostgreSQL authoritative; test state-machine and policy invariants first; make every external effect idempotent and reconcilable; and harden worker isolation before enabling write permissions.

## Phase 0 — Architecture and decisions (this change)

- Establish architecture, security/trust boundaries, job/worker lifecycles, and ADR process.
- Record initial technology and control-plane decisions.
- Define non-goals and production security gaps.

Exit: documents reviewed and contradictions resolved.

## Phase 1 — Repository bootstrap (this change)

- Python 3.11+ `src` layout with controller package boundaries.
- FastAPI service factory and liveness/readiness endpoints.
- Typed settings, structured logging baseline, pytest, Ruff, mypy.
- Alembic scaffold, Compose deployment, worker image placeholders/contracts, and systemd examples.
- CI and contributor workflow.

Exit: clean checkout installs; tests/lint/types pass; Compose config validates. No claim of production readiness.

## Phase 2 — Durable job kernel

- PostgreSQL schema for actors/projects/repositories/jobs/plans/attempts/events/audit/outbox/idempotency.
- Explicit domain state machine with optimistic concurrency.
- REST create/get/list/cancel job APIs and transactional outbox.
- Migration and repository tests against real PostgreSQL.

Exit: duplicate requests are safe; illegal transitions cannot commit; restart preserves all state.

## Phase 3 — Policy, approvals, and credentials

- Capability vocabulary and versioned policy evaluator.
- Action-digest approval requests/decisions and escalation flow.
- Secret-manager abstraction, short-lived credential broker, and audit.
- Authorization tests across actors/projects/repositories.

Exit: no write/network/secret capability can occur without a recorded policy decision; approval mutation invalidates grants.

## Phase 4 — Worker manager and runtime

- Docker manager reconciliation loop, leases/fencing, labels, limits, cleanup.
- Signed runtime protocol, heartbeats, events, artifacts, cancellation.
- Hardened base/language images and controlled network egress.
- Crash/restart/duplicate callback/host reboot integration tests.

Exit: a read-only sample job survives controller restart and leaves no stale privileged resources.

## Phase 5 — GitHub engineering loop

- GitHub App auth/webhooks and repository synchronization.
- Controlled clone/branch/commit/push/PR capabilities.
- Codex execution against a test repository.
- Ambiguous-side-effect reconciliation.

Exit: approved job produces an attributable PR; default branch cannot be directly modified.

## Phase 6 — Knowledge and enterprise integrations

- Private project knowledge store/retrieval with ACLs and provenance.
- Jira and Confluence retrieval/adapters; Slack request/status/approval UX.
- Read-only PostgreSQL log-analysis tools with safe query constraints.
- Prompt-injection evaluation corpus and red-team tests.

Exit: cross-project leakage tests pass; external content cannot grant capabilities.

## Phase 7 — MCP and additional clients

- Thin MCP adapter over REST; Hermes and ChatGPT integration guidance.
- Contract tests proving adapters share controller semantics and idempotency.

Exit: disconnecting any adapter loses no job truth; direct REST and MCP observe identical resources.

## Phase 8 — Operations and production readiness

- Metrics, traces, alerts, SLOs, quotas, retention, audit export.
- Encrypted backups/WAL archive and repeated restore exercises with measured RPO/RTO.
- Image/dependency supply-chain controls, threat-model update, penetration test.
- Upgrade/rollback, incident response, key rotation, and disaster-recovery runbooks.

Exit: production readiness review and documented residual risks.

## Testing strategy

- Unit: state transitions, policy, digests, validation, redaction.
- Integration: PostgreSQL transactions/migrations/outbox, Docker runtime, provider sandboxes.
- Contract: REST/OpenAPI, worker protocol, adapter/provider APIs.
- Security: authz matrices, injection corpus, path/SSRF controls, secret leakage, malicious repositories.
- Resilience: process kills, expired leases, duplicate/out-of-order events, network partitions, provider timeouts, backup restores.
- End-to-end: request → approval → isolated execution → artifact/PR → audit.

## Deferred decisions

Authentication/identity provider, secret manager, artifact object store, knowledge index, policy language, runtime hardening beyond Docker, exact RPO/RTO/SLOs, multi-tenancy model, and production hosting topology require ADRs before implementation.
