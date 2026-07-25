# Contributing

Use Python 3.11 or newer. Create a virtual environment and install `.[dev,database]`.

Changes to behavior follow test-driven development: add one failing test, implement the smallest passing behavior, then refactor. Run `make check` before review. Architectural changes require an ADR. Database schema changes require a reversible Alembic migration and PostgreSQL integration test.

Never commit `.env`, credentials, customer content, worker workspaces, or generated artifacts. Treat issue, repository, log, and database text as untrusted input. Keep adapters thin: durable behavior belongs in controller domain packages.

Use focused commits and conventional prefixes where practical (`docs:`, `feat:`, `fix:`, `test:`, `chore:`). Pull requests should state intent, security impact, tests, migration/rollback considerations, and operational impact.
