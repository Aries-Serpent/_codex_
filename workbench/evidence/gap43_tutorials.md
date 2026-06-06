# Gap 43 — Tutorial Documentation: Evidence

**Gap:** 43 — Create tutorial documentation for key workflows  
**Status:** ✅ Implemented  
**Date:** 2025-01-15  
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Deliverables

### Files Created

| File | Words (approx.) | Description |
|------|-----------------|-------------|
| `docs/tutorials/README.md` | ~230 | Index of all tutorials with one-line descriptions and learning path |
| `docs/tutorials/01_drift_monitoring.md` | ~680 | Data + model drift monitoring using `DataDriftDetector` and `ModelDriftDetector` |
| `docs/tutorials/02_ab_testing.md` | ~820 | A/B testing with `run_ab_test` and `ABTestSuite` |
| `docs/tutorials/03_continuous_learning.md` | ~900 | End-to-end pipeline: drift → trigger → eval gate → promote → feedback loop |
| `docs/tutorials/04_resilience.md` | ~890 | `CircuitBreaker`, `retry_with_backoff`, `GracefulDegradation` |

Total: **5 files**, all under `docs/tutorials/`.

---

## Import Path Verification

All code snippets use canonical import paths verified against source:

| Import used in tutorial | Source file |
|-------------------------|-------------|
| `from codex_ml.monitoring.data_drift import DataDriftDetector, DriftResult` | `src/codex_ml/monitoring/data_drift.py` |
| `from codex_ml.monitoring.model_drift import ModelDriftDetector` | `src/codex_ml/monitoring/model_drift.py` |
| `from codex_ml.experiments.ab_testing import run_ab_test, ABTest, ABTestSuite, ABTestResult` | `src/codex_ml/experiments/ab_testing.py` |
| `from codex_ml.continuous_learning import ContinuousLearningPipeline` | `src/codex_ml/continuous_learning/pipeline.py` |
| `from codex_ml.continuous_learning.eval_gate import EvalGate` | `src/codex_ml/continuous_learning/eval_gate.py` |
| `from codex_ml.continuous_learning.trigger import RetrainingTrigger` | `src/codex_ml/continuous_learning/trigger.py` |
| `from codex_ml.feedback.loop import FeedbackLoop` | `src/codex_ml/feedback/loop.py` |
| `from codex_ml.feedback.events import FeedbackEvent` | `src/codex_ml/feedback/events.py` |
| `from codex_ml.training.auto_retrain import AutoRetrainPipeline` | `src/codex_ml/training/auto_retrain.py` |
| `from codex.resilience import CircuitBreaker, CircuitOpenError, CircuitState` | `src/codex/resilience/__init__.py` |
| `from codex.resilience import GracefulDegradation, DegradationError` | `src/codex/resilience/__init__.py` |
| `from codex.resilience import retry_with_backoff, RetryExhausted` | `src/codex/resilience/__init__.py` |

---

## Done Criteria Checklist

- [x] `docs/tutorials/` directory contains ≥ 5 markdown files (5 created)
- [x] All code snippets use correct import paths matching actual module locations
- [x] Each tutorial is 300–600+ words with realistic, runnable code examples
- [x] Evidence file at `workbench/evidence/gap43_tutorials.md`
- [x] `workbench/gap_backlog_prioritized.md` gap 43 → `✅ Implemented`

---

## Tutorial Content Summary

### 01 — Drift Monitoring
- Explains data vs. model drift with a comparison table
- Step-by-step `DataDriftDetector` usage: instantiation, preparing distributions,
  running `detect_psi` / `detect_kl`, interpreting `DriftResult` with severity table
- `check_epoch` convenience wrapper for training loops
- Step-by-step `ModelDriftDetector`: `update_baseline` + `check` per epoch
- Links to Tutorial 03 (continuous learning)

### 02 — A/B Testing
- When to use A/B testing (vs. ad-hoc comparison)
- Quick-start with `run_ab_test`
- Full `ABTestSuite` example with 3 metrics (accuracy, F1, latency)
- Detailed interpretation of `winner`, `p_value`, `effect_size`, `confidence_interval`
- Best practices: minimum sample sizes, alpha selection, multiple comparisons / Bonferroni

### 03 — Continuous Learning
- Architecture diagram (drift → trigger → eval gate → promote)
- `ContinuousLearningPipeline` setup with all parameters documented
- `should_retrain` with both `DriftResult` objects and plain dicts
- `trigger_retrain` → `RetrainingJob` descriptor
- `EvalGate` standalone usage
- `promote` with registry integration
- `FeedbackLoop` wiring: `on_drift`, `on_alert`, `should_adapt`
- Full end-to-end loop pseudocode
- `AutoRetrainPipeline` high-level integration

### 04 — Resilience
- Three-state circuit breaker diagram (CLOSED/OPEN/HALF_OPEN)
- `CircuitBreaker.call` pattern with `CircuitOpenError` fallback
- `CircuitState` inspection and manual `reset`
- `retry_with_backoff` as decorator and direct wrapper
- `GracefulDegradation` as decorator, context manager, and DegradationError mode
- Production composite pattern: all three primitives layered
- Unit testing resilience patterns with `pytest` + `unittest.mock`
- Summary table: which tool for which situation
