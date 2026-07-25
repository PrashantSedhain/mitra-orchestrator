# ADR 0002: Docker Compose for initial deployment

- Status: Accepted
- Date: 2026-07-25

## Context

The initial target is one dedicated self-hosted Linux machine. The team needs reproducible local and early deployment without prematurely operating a cluster scheduler.

## Decision

Package controller and PostgreSQL for Docker Compose. Keep service boundaries/configuration portable and provide systemd examples for supervising Compose on boot.

## Consequences

Compose is accessible and adequate for a single host, but does not provide multi-host scheduling or PostgreSQL HA. Production hardening, external secrets, backups, monitoring, and pinned digests remain required. A later scheduler change must preserve controller contracts.

## Alternatives considered

Kubernetes adds operational cost too early; bare systemd processes reduce container parity; managed platforms conflict with initial self-hosting goals.
