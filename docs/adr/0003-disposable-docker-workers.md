# ADR 0003: Disposable Docker worker containers

- Status: Accepted
- Date: 2026-07-25

## Context

Codex executes generated commands and repository code with variable toolchains. Reusing environments leaks state and complicates attribution/recovery.

## Decision

Run one disposable Docker container per job attempt from an allow-listed, pinned worker image. Persist only controller records and explicitly uploaded artifacts. Reconciliation cleans up containers and ephemeral volumes.

## Consequences

Isolation, reproducibility, resource limits, and clean retries improve. Image building and cleanup become operational responsibilities. Docker is not a hostile multi-tenant sandbox; stronger isolation may later replace the runtime behind the manager contract.

## Alternatives considered

Host processes have weak containment; long-lived shared workers leak state; VMs/microVMs offer stronger isolation but add initial complexity and startup cost.
