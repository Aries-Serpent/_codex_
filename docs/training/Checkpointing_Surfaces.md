# [Guide]: Checkpointing Surfaces — Canonical vs Legacy
> Generated: 2025-10-17 20:25:02 UTC | Author: mbaetiong  


## 1) Purpose
Clarify which APIs are canonical for new code, while preserving backward compatibility with legacy helpers.

## 2) Surfaces
| Layer | Path (canonical) | Purpose | Notes |
|------|-------------------|--------|------|
| Core (integrity/hash) | codex_ml/utils/checkpoint_core.py | Save/verify/load with sha256; top-k pruning | Prefer explicit public functions and manifest fields |
| Manager (Codex ML) | codex_ml/utils/checkpointing.py | Epoch dirs, last/best markers, RNG dump/load | Canonical manager API for training flows |
| Trainer utils | src/training/checkpointing.py | RNG state dataclass; save/load model/optim | Bridge to canonical manager |
| Legacy/simple | src/utils/checkpoint.py; src/utils/checkpointing.py; training/checkpoint_manager.py | Atomic save/load; simple retention | Keep for compatibility; avoid in new code |

## 3) Canonical Usage
```python
from codex_ml.utils.checkpointing import CheckpointManager

mgr = CheckpointManager(root="outputs/run-123")
mgr.save(epoch=3, state={"model": model_state, "optim": optim_state}, is_best=metric_improved)
mgr.verify(epoch=3)  # sha256 integrity
restored = mgr.load(epoch="best", weights_only=True)
```

## 4) RNG Capture/Restore
| Task | API |
|------|-----|
| Capture | codex_ml/utils/checkpoint_core.py: dump_rng_state() |
| Restore | codex_ml/utils/checkpoint_core.py: load_rng_state() |

Tip: Always persist rng.json next to weights and config for reproducibility.

## 5) Migration Guidance
| From | To | Action |
|------|----|--------|
| src/utils/checkpoint.py | codex_ml/utils/checkpointing.py | Wrap legacy calls or re-route via manager |
| training/checkpoint_manager.py | codex_ml/utils/checkpointing.py | Use canonical retention/best-k semantics |

## 6) Deprecation Policy
- No hard removals in this cycle.
- Add DeprecationWarning only when safe and with clear replacement path.

## 7) Validation
- tests/utils/test_checkpointing_core.py
- tests/checkpointing/*
- tests/test_trainer_extended.py

*End of Guide*
