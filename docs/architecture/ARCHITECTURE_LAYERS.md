# Architecture Layers

**Domain**: D1 — Architecture & Layer Boundaries  
**Owner**: `code-analysis-agent`  
**Last updated**: 2026-05-27

---

## Layer Definitions

The Codex platform is organised into the following architectural layers, each
with strictly enforced import boundaries enforced by `import-linter`.

| Layer | Package / Path | Allowed Imports |
|-------|---------------|-----------------|
| **Domain** | `src/codex/` | stdlib, third-party only |
| **ML Core** | `src/codex_ml/` | Domain, stdlib, third-party |
| **Training** | `training/`, `src/training/` | ML Core, Domain, stdlib, third-party |
| **Services** | `src/services/` | ML Core, Domain, stdlib, third-party |
| **CLI / Apps** | `cli/`, `apps/` | All layers |
| **Scripts** | `scripts/` | All layers (automation only) |
| **Tests** | `tests/` | All layers (test scope) |

### Prohibited Cross-Layer Imports

- `src/codex_ml/` **must not** import from `training/`
- `src/codex/` **must not** import from `src/codex_ml/` or `training/`
- `src/services/` **must not** import from `cli/` or `apps/`

Import constraints are enforced by `.importlinter` via the `import-linter.yml`
CI workflow on every PR targeting `main`.

---

## D1 Exit Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Architecture doc present (`docs/architecture/ARCHITECTURE_LAYERS.md`) | ✅ |
| 2 | `.importlinter` config present | ✅ |
| 3 | `import-linter.yml` CI workflow present | ✅ |
| 4 | Domain ownership map present (`.codex/DOMAIN_OWNERSHIP.md`) | ✅ |

---

*This document is the D1 architecture reference. Keep in sync with `.importlinter`.*
