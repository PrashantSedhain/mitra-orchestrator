# ADR 0006: Private project knowledge outside customer repositories

- Status: Accepted
- Date: 2026-07-25

## Context

Plans need organization-specific context, but committing private operational knowledge or model instructions into customer repositories creates leakage, ownership, and prompt-injection risks.

## Decision

Store private project knowledge in a Mitra-controlled system outside customer repositories. Retrieval enforces tenant/project ACLs and returns provenance, timestamps, and untrusted-content labels. Repositories may contain customer-owned documentation but are never the private control-plane policy store.

## Consequences

Knowledge can be updated and access-controlled independently and avoids repository pollution. This introduces another backed-up, secured subsystem and requires provenance-aware retrieval and deletion.

## Alternatives considered

Committing all knowledge to repositories is simple but leaks private context and conflates customer code with controller policy; keeping knowledge only in model conversations is non-durable and unauditable.
