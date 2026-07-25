# Database migrations

Alembic owns schema evolution. No domain tables are introduced in Phase 1. Install the `database` extra, provide the production URL through configuration before Phase 2, and test upgrades and downgrades against disposable PostgreSQL—not SQLite.
