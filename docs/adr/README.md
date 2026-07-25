# Architecture Decision Records

ADRs capture durable architectural choices and their trade-offs. Status values are `Proposed`, `Accepted`, `Superseded`, or `Deprecated`. To change an accepted decision, add a new ADR and link both records; do not rewrite history except for typographical corrections.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-postgresql-durable-state.md) | PostgreSQL as durable state store | Accepted |
| [0002](0002-docker-compose-initial-deployment.md) | Docker Compose for initial deployment | Accepted |
| [0003](0003-disposable-docker-workers.md) | Disposable Docker worker containers | Accepted |
| [0004](0004-mcp-is-an-adapter.md) | MCP as an adapter rather than controller | Accepted |
| [0005](0005-rest-primary-controller-interface.md) | HTTP REST as primary controller interface | Accepted |
| [0006](0006-private-knowledge-outside-repositories.md) | Private project knowledge outside customer repositories | Accepted |
| [0007](0007-read-only-by-default.md) | Read-only permissions by default | Accepted |
| [0008](0008-python-initial-language.md) | Python as initial implementation language | Accepted |

## Template

```markdown
# ADR NNNN: Title

- Status: Proposed
- Date: YYYY-MM-DD

## Context
## Decision
## Consequences
## Alternatives considered
```
