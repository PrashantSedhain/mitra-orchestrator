# ADR 0005: HTTP REST as the primary controller interface

- Status: Accepted
- Date: 2026-07-25

## Context

Slack, Hermes, ChatGPT, MCP, automation, and future clients need a stable, broadly supported control-plane contract with explicit command/query semantics.

## Decision

Expose a versioned HTTP JSON REST API as the primary interface, described by OpenAPI. Use resource IDs, idempotency keys, request/correlation IDs, consistent errors, and authenticated callbacks. Streaming is supplementary, not authoritative.

## Consequences

REST is interoperable and operationally familiar. We must carefully model long-running commands, versioning, polling/webhooks, and idempotency. Internal Python calls must not become a parallel privileged interface.

## Alternatives considered

gRPC provides strong RPC contracts but weaker universal client ergonomics; GraphQL is flexible for queries but less natural for command workflows; MCP alone is too client-specific.
