# Worker images

These directories reserve the image hierarchy for disposable, one-attempt Codex runtimes. Phase 1 contains hardened scaffolds only; the runtime protocol and Codex installation are deliberately not implemented yet.

Build base first with `docker build -t mitra-worker-base:dev workers/base`, then build a language image from the repository root. Production images must be pinned by digest, scanned, publish an SBOM, run non-root, and satisfy `docs/worker-lifecycle.md`.
