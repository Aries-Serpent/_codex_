# Gap 18 — Model Drift Detection: Implementation Summary

**Status:** ✅ Implemented
**Date:** 2026-06-06
**Branch:** copilot/explore-codebase-and-create-plan

---

## Overview

Gap 18 required detection logic for model/concept drift to complement the
existing `model-drift-retrain.yml` scheduling workflow.  Two complementary
signals are monitored every post-epoch:

| Signal | Method | Threshold |
|---|---|---|
| Output distribution shift | Jensen-Shannon Divergence (JSD) | 0.05 |
| Prediction-confidence drop | Mean confidence < threshold | 0.50 |
| Low-confidence rate | Fraction of predictions below cutoff | 0.30 |

---

## Files Created / Modified

| Path | Change |
|---|---|
| `src/codex_ml/monitoring/model_drift.py` | **Created** — `ModelDriftDetector`, `DriftResult`, `ConfidenceStats`, `jensen_shannon_divergence` |
| `tests/unit/test_model_drift.py` | **Created** — 35 unit tests across 10 test classes |
| `src/codex_ml/train_loop.py` | **Modified** — drift detector wired into post-epoch monitoring block |

---

## Implementation Detail

### `src/codex_ml/monitoring/model_drift.py`

Pure-Python, no hard PyTorch / NumPy dependency (works in CPU-only CI).

**`jensen_shannon_divergence(p, q)`**
- Implements JSD = 0.5 × KL(P‖M) + 0.5 × KL(Q‖M), base-2
- Returns value in [0, 1]; clamped for floating-point edge cases

**`ConfidenceStats.from_scores(scores)`**
- Computes mean/min/max confidence, low-confidence rate, and normalised entropy

**`ModelDriftDetector`**
- `update_baseline(scores)` — stores reference distribution histogram
- `check(scores, epoch)` → `DriftResult` — checks JSD, mean confidence, low-confidence rate
- `history()` / `reset()` / `reset_history()` — history management
- All thresholds configurable at construction time; raises `ValueError` on bad params

### `src/codex_ml/train_loop.py` integration

Wired in the post-epoch monitoring block (lines ~1850 and ~2095), lazily imported
alongside the existing `PerformanceMonitor`:

```python
# Model drift detection (Gap 18) — must never crash training.
if _drift_detector is not None:
    try:
        ...
        if not _drift_detector.has_baseline():
            _drift_detector.update_baseline(_epoch_conf_scores)
        else:
            _drift_result = _drift_detector.check(_epoch_conf_scores, epoch=epoch)
            if _drift_result.drift_detected:
                logger.warning("Model drift detected at epoch %d: %s", ...)
            if state is not None and isinstance(state, dict):
                state["drift_result_epoch"] = _drift_result.to_dict()
    except Exception as _drift_exc:
        logger.debug("Drift detector failed (non-fatal): %s", _drift_exc)
```

The integration:
- Never crashes training (guarded with `except Exception`)
- Uses `exp(-loss)` as a confidence proxy from `synthetic_losses`
- Auto-sets baseline on first epoch; checks drift from second epoch onward
- Writes per-epoch drift result into the training `state` dict for downstream consumers

---

## Test Results

```
platform linux -- Python 3.12.3, pytest-9.0.3
collected 35 items

tests/unit/test_model_drift.py ...................................  [100%]

============ 35 passed, 1 warning in 1.04s ============
```

### Test classes

| Class | Tests | What it covers |
|---|---|---|
| `TestJensenShannonDivergence` | 6 | JSD=0 for identical; JSD=1 for disjoint; bounded [0,1]; error handling |
| `TestJSDDriftDetection` | 2 | Large shift detected; similar distribution not flagged |
| `TestConfidenceDropDetection` | 2 | Low mean triggers alert; high mean does not |
| `TestLowConfidenceRateDetection` | 2 | High low-conf rate triggers; low rate does not |
| `TestNoDriftStableData` | 1 | Stable high-confidence scores produce no drift |
| `TestBaselineManagement` | 6 | has_baseline / update / reset / replace / empty-raises |
| `TestDriftResultShape` | 4 | summary() wording; to_dict() keys and values |
| `TestConfidenceStats` | 5 | statistics correctness; to_dict(); empty-raises |
| `TestFirstEpochBaseline` | 1 | First call has no JSD; after update_baseline JSD is present |
| `TestModelDriftDetectorValidation` | 6 | Constructor ValueError on bad params; check() on empty |

---

## CI Gate

The detector is wired as a **non-blocking** post-epoch hook (failures are
caught and logged at DEBUG level).  A future gap can promote the
`state["drift_result_epoch"]` payload into a hard CI gate threshold.
