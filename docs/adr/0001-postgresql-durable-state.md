# ADR 0001: PostgreSQL as the durable state store

- Status: Accepted
- Date: 2026-07-25

## Context

Mitra requires transactional state machines, concurrency control, relational integrity, idempotency, auditability, and restart recovery across jobs, attempts, approvals, leases, artifacts, and external effects.

## Decision

Use PostgreSQL as the authoritative durable store. Current-state tables, append-only events/audit, and a transactional outbox share database transactions. In-memory data and queues are non-authoritative.

## Consequences

Strong transactions, constraints, locking, JSON support, and mature backup tooling fit the initial control plane. We accept schema/migration discipline and operational responsibility. Large artifact bodies remain outside PostgreSQL with durable metadata in it.

## Alternatives considered

SQLite lacks the intended concurrency/operations model; a document database weakens relational invariants; an event broker alone cannot provide current authoritative state; full event sourcing adds unnecessary initial complexity.
