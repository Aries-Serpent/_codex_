# codex-contracts

Dependency-free interoperability contracts for the federated Codex package ecosystem.
This alpha package contains versioned event envelopes, content-addressed artifact
references, structured errors, and the minimum event-plugin protocol.

## Installation

```console
pip install codex-contracts
```

The package deliberately has no runtime dependencies and does not import the
`codex_ml`, `codex`, `cognitive_brain`, or `aries_serpent_core` implementations.

See `docs/adr/ADR-009-federated-package-boundaries.md` for versioning and dependency rules.
