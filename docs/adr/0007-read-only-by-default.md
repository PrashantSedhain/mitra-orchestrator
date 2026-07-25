# ADR 0007: Read-only permissions by default

- Status: Accepted
- Date: 2026-07-25

## Context

AI workers process untrusted content and generated actions. Broad write, network, secret, or deployment access turns prompt injection and model error into immediate impact.

## Decision

Start every actor/job/worker with a minimal read-only capability set. Grant write, execution, network, credentials, push, PR, database, and deployment capabilities separately through versioned policy and, where required, action-bound approval. Deny unspecified capabilities.

## Consequences

The blast radius is reduced and escalation is auditable. Workflows require more policy design and may pause for approval. Read-only still needs sandboxing because parsing and builds can be dangerous.

## Alternatives considered

Broad default credentials maximize convenience but are unacceptable; role-wide static permissions are too coarse and difficult to revoke per attempt.
