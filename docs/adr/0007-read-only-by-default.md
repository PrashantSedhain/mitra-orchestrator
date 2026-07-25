# ADR 0007: Read-only permissions by default

- Status: Accepted
- Date: 2026-07-25

## Context

AI workers process untrusted content and generated actions. Broad write, network, secret, or deployment access turns prompt injection and model error into immediate impact.

## Decision

Start every actor/job/worker with a minimal read-only capability set. Read-only permits controller-defined, non-shell inspection operations (`tool.execute.trusted`) whose implementations and arguments are allow-listed, have no network or secret access, and cannot invoke repository-controlled code. It does **not** permit an arbitrary process, repository build script, test suite, dependency hook, or executable from the worktree.

Grant `repository_code.execute`, `dependency.install`, network, credentials, worktree writes, push, PR, database, and deployment capabilities separately through versioned policy and, where required, action-bound approval. Deny unspecified capabilities. A granted execution capability never implies network, credentials, writes, or another capability.

Capabilities govern job-directed operations, not the worker entrypoint and controller-owned runtime protocol required to start and supervise the sandbox. Operations must satisfy every applicable capability: invoking a repository script through a shell requires both `repository_code.execute` and `shell.execute`; installing dependencies with lifecycle hooks requires `dependency.install` and `repository_code.execute`; fetching packages additionally requires `network.egress`. Directly invoking an installed test runner against repository code requires `repository_code.execute` but not `shell.execute`.

## Consequences

The blast radius is reduced and escalation is auditable. Workflows require more policy design and may pause for approval. Even trusted inspection needs sandboxing because parsers can be vulnerable. Plans that run tests or builds must explicitly request `repository_code.execute`; calling such work “read-only” refers only to repository mutation and is therefore prohibited in Mitra terminology.

## Alternatives considered

Broad default credentials maximize convenience but are unacceptable; role-wide static permissions are too coarse and difficult to revoke per attempt.
