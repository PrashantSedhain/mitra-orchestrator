# ADR 0008: Python as the initial implementation language

- Status: Accepted
- Date: 2026-07-25

## Context

The control plane needs rapid domain/API development, mature PostgreSQL and web libraries, container integration, typing, migrations, and good AI/automation ecosystem support.

## Decision

Implement the initial controller and adapters in Python 3.11 or newer with a modern `src` package layout, FastAPI, Pydantic settings, SQLAlchemy/Alembic boundaries, pytest, Ruff, and mypy.

## Consequences

Python accelerates delivery and integration. We accept runtime performance and typing limitations relative to compiled languages, mitigated with explicit schemas, strict lint/type checks, database constraints, and isolated worker-heavy execution. Components may later be rewritten behind contracts if evidence warrants.

## Alternatives considered

Go offers simple static binaries and concurrency; Rust offers stronger safety; TypeScript offers broad web familiarity. None currently outweigh Python's integration speed for the initial controller.
