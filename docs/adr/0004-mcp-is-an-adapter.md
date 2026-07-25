# ADR 0004: MCP is an adapter, not the controller

- Status: Accepted
- Date: 2026-07-25

## Context

MCP is useful for AI clients, but protocol sessions and client tool calls are not a durable workflow authority. Mitra must support non-MCP clients and recover independently.

## Decision

Implement MCP as a stateless/thin adapter over the controller's authenticated REST API. It translates tools/resources and returns durable IDs; it does not own state, workers, policy, credentials, or retries.

## Consequences

All clients share one authorization and lifecycle model, and MCP can evolve independently. There is an additional translation hop and contract-testing burden.

## Alternatives considered

Making the MCP server authoritative couples durability to one client protocol; embedding separate orchestration in each client creates divergent state and security policy.
