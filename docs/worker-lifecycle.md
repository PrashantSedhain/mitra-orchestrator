# Worker lifecycle

## Principle

A worker container is a disposable executor for exactly one job attempt. The controller owns desired state and authority; the worker owns no durable lifecycle truth.

## Lifecycle

```text
REQUESTED -> PROVISIONING -> STARTING -> READY -> BUSY -> FINALIZING -> EXITED
                 |             |         |       |          |
                 +-------------+---------+-------+----------+-> FAILED
                                               |
                                          STOPPING -> TERMINATED
```

1. **Requested:** a committed attempt is dispatchable.
2. **Provisioning:** manager allocates an allow-listed image, workspace, limits, network policy, and fenced lease.
3. **Starting:** container starts with a signed/immutable runtime specification.
4. **Ready:** worker validates spec, identity, base revision, and callback connectivity, then heartbeats.
5. **Busy:** worker executes the approved plan and emits structured progress.
6. **Finalizing:** worker uploads bounded artifacts/result manifest and reports final status.
7. **Exited:** manager records exit metadata and removes ephemeral resources.

## Runtime contract

### Controller to worker

- schema version; job, attempt, worker, repository, project, and lease IDs
- monotonically increasing fencing token and lease expiry
- registry-resolved clone endpoint and pinned base commit
- plan revision and digest
- explicit capability set and constraints, including separate trusted-tool, repository-code, shell, dependency, network, write, and credential grants
- image digest, CPU/memory/PID/disk/time limits
- credential handles with expiry (never long-lived plaintext in the spec)
- controller callback and artifact upload endpoints
- correlation ID and output limits

### Worker to controller

Authenticated, idempotent messages: startup/ready, heartbeat, progress event, capability request, artifact metadata, result manifest, and final status. Every message includes job/attempt IDs, sequence or event ID, and fencing token. The controller rejects stale tokens, invalid transitions, oversized payloads, and unknown artifact references.

## Heartbeats and leases

The database lease has owner, fencing token, expiry, and last heartbeat. Heartbeats renew only a current lease. Missing heartbeats move the attempt into reconciliation—not immediate retry—because the container or external action may still exist. A new attempt receives a higher token; stale callbacks become harmless conflicts.

## Workspace and Git contract

The worker starts from a clean ephemeral volume. It verifies the pinned commit, checks out a controller-allocated branch/worktree, and records resulting commit IDs. The controller controls whether worktree write, repository-code execution, shell, dependency installation, commit, push, or PR capabilities are granted. `tool.execute.trusted` is limited to controller-owned, non-shell inspection operations and cannot launch a worktree executable. Artifact collection follows allow-listed paths and rejects symlink/path escapes.

Capabilities are checked cumulatively for each operation. For example, a repository script launched through a shell needs both `repository_code.execute` and `shell.execute`; a package install that downloads dependencies and runs hooks needs `dependency.install`, `network.egress`, and `repository_code.execute`. Worker bootstrap and protocol heartbeats are fixed runtime mechanics, not plan-grantable execution.

## Isolation and resources

Run non-root; drop capabilities; set `no-new-privileges`; avoid host/Docker sockets; use read-only root filesystem and bounded writable mounts; impose CPU, memory, PID, disk, file-size, log, and wall-clock limits. Network defaults off and, when approved, passes through controlled egress. Container images are pinned and role-specific (`base`, `python`, `node`, `go`, `java`).

## Credentials

The manager brokers short-lived attempt-scoped credentials only after policy authorization. Credentials are not placed in prompts or durable worker logs. They expire/revoke when the lease ends and are excluded from artifact paths. Credential use is audited by capability and target.

## Stop and cleanup

Normal cancellation requests graceful checkpoint/exit, then force termination after a deadline. Lease loss revokes credentials before cleanup. Cleanup removes container, networks, temporary volumes, and secret material, but preserves referenced artifacts and structured logs. Cleanup is idempotent and continuously reconciled.

## Failure and recovery

Startup failure, health timeout, resource exhaustion, worker crash, callback failure, host restart, and cleanup failure are separate reason codes. On manager restart, Docker labels (`mitra.job_id`, `mitra.attempt_id`, `mitra.worker_id`, `mitra.fencing_token`) are reconciled against PostgreSQL. Unknown containers are quarantined/stopped; missing containers finalize or retry attempts according to durable state. Never trust container labels alone.

## Image contract

Every worker image provides a fixed non-root user, an entrypoint implementing the runtime protocol, Codex at an approved version, CA certificates, Git, and a minimal toolchain. Language images extend `base`. Images publish an SBOM, vulnerability scan result, and immutable digest. Repository-code execution, shell execution, and dependency installation are separately controlled capabilities; granting one does not grant the others.
