# Mitra Orchestrator

Mitra Orchestrator is a self-hosted control plane for durable AI software-engineering jobs. Clients such as Slack, ChatGPT, and Hermes submit work to a controller; isolated, disposable Docker containers run Codex against explicitly assigned repositories.

Mitra—not a client, adapter, or worker—is authoritative for job state, worker lifecycle, repository assignments, plans, approvals, permission escalation, credentials, branches, pull requests, artifacts, events, audit history, recovery, and retries.

## Status

Phase 0 (architecture and decisions) and Phase 1 (repository bootstrap) are the current scope. The service skeleton exposes health/readiness endpoints and establishes package boundaries; it does **not** yet dispatch real Codex workers or implement production integrations.

## Architecture at a glance

```text
Slack / Hermes / ChatGPT / future clients
                 |
         REST API / adapters
                 |
       Mitra Controller API
    +------------+-------------+
    | jobs, policy, approvals  |
    | repositories, artifacts  |
    | worker manager, events   |
    +------------+-------------+
                 |
              PostgreSQL
                 |
        disposable Docker workers
                 |
       GitHub / Jira / Confluence
```

See [architecture](docs/architecture.md), [security model](docs/security-model.md), and the [ADR index](docs/adr/README.md).

## Prerequisites

- Python 3.11+
- Docker Engine with Compose v2 (for local PostgreSQL and service deployment)
- `make` (optional convenience)

## Local development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
pytest
uvicorn mitra_orchestrator.api.app:create_app --factory --reload
```

The API listens on `http://127.0.0.1:8000`. Check:

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
```

## Docker Compose

```bash
cp .env.example .env
docker compose -f deploy/compose/compose.yaml up --build
```

The Compose deployment is for initial single-host operation, not a claim of high availability. Pin image digests and use an external secret manager before production.

## Quality gates

```bash
make check
```

This runs formatting checks, linting, type checking, tests, and Docker Compose configuration validation. See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions.

## Repository map

- `src/mitra_orchestrator/` — controller packages
- `tests/unit/`, `tests/integration/` — automated tests
- `migrations/` — Alembic database migrations
- `deploy/compose/`, `deploy/systemd/` — initial deployment assets
- `workers/` — worker image definitions and runtime contract assets
- `config/` — checked-in non-secret configuration examples
- `docs/` — architecture, security, lifecycle, plans, and ADRs
- `scripts/` — development and operational helpers

## Security posture

Mitra treats every external text source—including issues, pull-request comments, repository files, application logs, and database content—as untrusted data, never as controller instructions. Workers start read-only, receive short-lived scoped credentials, and require durable policy-backed approvals for escalation. See [docs/security-model.md](docs/security-model.md).

## License

No license has been selected yet. All rights are reserved until the repository owner adds one.
