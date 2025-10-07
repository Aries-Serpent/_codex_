# Unified Training Orchestrator (Schema v2 Alignment)

The unified orchestrator consolidates legacy and functional loops behind a **single public API**.

| Feature | Description |
|---------|-------------|
| Strategy Backends | `functional` (default), `legacy` (deprecated warning) |
| Resume | Optional `resume_from` path (directory containing `state.pt`) |
| Checkpoints | Emitted per run (schema_version=2), RNG + environment |
| Callbacks | Hook interfaces for future metrics / logging integration |
| Determinism | Central seeding (Python, NumPy, Torch) |
| Deprecation | Legacy loop wrapped with `DeprecationWarning` |

## Quick Start
```python
from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
cfg = UnifiedTrainingConfig(model_name="demo", epochs=1)
result = run_unified_training(cfg)
print(result)
```

## Schema v2 Additions
| Field | Purpose |
|-------|---------|
| schema_version | Forward compatibility |
| digest_sha256 | Integrity of `state.pt` |
| environment | Runtime metadata |
| backend_name | Provenance across strategies |
| rng (_rng) | Deterministic resumption |

## Migration
| Legacy | Replacement |
|--------|-------------|
| `run_training(...)` | Use `UnifiedTrainingConfig(..., backend="legacy")` |
| `run_functional_training(...)` | Unified orchestrator default |

## Roadmap
- Parity metrics callback injection
- Early-stop & best-k metric integration
- Config-driven retention policy

*End*
