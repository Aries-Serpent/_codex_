# Gap 36 — Continuous Learning Pipeline: Implementation Evidence

**Status:** ✅ Implemented  
**Date:** 2025-07-13  
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Summary

Built the `src/codex_ml/continuous_learning/` package — a drift-triggered
retraining loop that bridges the existing drift monitors (Gap 17 / Gap 18)
with an evaluation gate and model registry promotion step.

---

## Files Created

| File | Purpose |
|------|---------|
| `src/codex_ml/continuous_learning/__init__.py` | Package init — exports `ContinuousLearningPipeline`, `RetrainingTrigger`, `EvalGate`, `EvalGateResult`, `RetrainingJob` |
| `src/codex_ml/continuous_learning/pipeline.py` | `ContinuousLearningPipeline` + `RetrainingJob` |
| `src/codex_ml/continuous_learning/trigger.py` | `RetrainingTrigger` dataclass |
| `src/codex_ml/continuous_learning/eval_gate.py` | `EvalGate` + `EvalGateResult` |
| `tests/unit/test_continuous_learning.py` | 25 unit tests |

---

## Architecture

```
drift_result (dict or DriftResult object)
     │
     ▼
ContinuousLearningPipeline.should_retrain()
     │  True
     ▼
trigger_retrain(config) → RetrainingJob
     │
     ▼  (external training)
eval_gate(metrics) → bool
     │  True
     ▼
promote(model_path, registry) → bool → registry updated
```

---

## API Surface

### `ContinuousLearningPipeline`

```python
from codex_ml.continuous_learning import ContinuousLearningPipeline

pipeline = ContinuousLearningPipeline(
    drift_threshold=0.2,
    eval_gate_min_accuracy=0.80,
    eval_gate_max_loss=0.5,
    eval_gate_min_improvement_pct=1.0,
)

# Accepts both dict and DriftResult objects from Gap 17 / Gap 18
if pipeline.should_retrain({"score": 0.35, "drifted": True}):
    job = pipeline.trigger_retrain({"epochs": 5, "lr": 1e-4})
    # ... run training externally ...
    metrics = {"accuracy": 0.87, "loss": 0.38, "baseline_accuracy": 0.83}
    pipeline.promote("/models/v2.pt", registry={}, metrics=metrics)
```

### `RetrainingTrigger`

```python
from codex_ml.continuous_learning import RetrainingTrigger

trigger = RetrainingTrigger(
    reason="data_drift_psi",
    drift_score=0.32,
    config_snapshot={"epochs": 5},
)
d = trigger.to_dict()                    # serialise
t2 = RetrainingTrigger.from_dict(d)     # deserialise
```

### `EvalGate`

```python
from codex_ml.continuous_learning import EvalGate

gate = EvalGate(min_accuracy=0.80, max_loss=0.5, min_improvement_pct=1.0)
result = gate.evaluate({"accuracy": 0.85, "loss": 0.42, "baseline_accuracy": 0.83})
# result.passed → True / False
# result.reasons → list of failure explanations
```

---

## Integration with Gap 17 / Gap 18

The pipeline's `should_retrain()` accepts both `dict` and objects with
`.score` / `.drifted` attributes, making it directly compatible with
`DataDriftDetector.detect_psi()` / `ModelDriftDetector.check()` outputs:

```python
from codex_ml.monitoring.data_drift import DataDriftDetector
from codex_ml.continuous_learning import ContinuousLearningPipeline

detector = DataDriftDetector(psi_threshold=0.2)
pipeline = ContinuousLearningPipeline(drift_threshold=0.2)

result = detector.detect_psi(reference, current)  # returns DriftResult
if pipeline.should_retrain(result):               # accepts DriftResult directly
    pipeline.trigger_retrain(config)
```

---

## Test Results

```
tests/unit/test_continuous_learning.py  25 passed in 0.50s
```

### Test Coverage Matrix

| # | Test | Class | Status |
|---|------|-------|--------|
| 1 | score above threshold → True | `TestShouldRetrain` | ✅ |
| 2 | score below threshold → False | `TestShouldRetrain` | ✅ |
| 3 | drifted=True overrides low score | `TestShouldRetrain` | ✅ |
| 4 | drifted=False + score 0 → False | `TestShouldRetrain` | ✅ |
| 5 | object with .score attribute | `TestShouldRetrain` | ✅ |
| 6 | extra: object below threshold | `TestShouldRetrain` | ✅ |
| 7 | extra: score == threshold → False | `TestShouldRetrain` | ✅ |
| 8 | trigger_retrain returns RetrainingJob | `TestTriggerRetrain` | ✅ |
| 9 | config snapshot propagated | `TestTriggerRetrain` | ✅ |
| 10 | trigger round-trip serialisation | `TestTriggerRetrain` | ✅ |
| 11 | all thresholds met → passes | `TestEvalGate` | ✅ |
| 12 | accuracy below min → fails | `TestEvalGate` | ✅ |
| 13 | loss above max → fails | `TestEvalGate` | ✅ |
| 14 | improvement below min_pct → fails | `TestEvalGate` | ✅ |
| 15 | missing accuracy key → failure reason | `TestEvalGate` | ✅ |
| 16 | returns EvalGateResult type | `TestEvalGate` | ✅ |
| 17 | no thresholds → always passes | `TestEvalGate` | ✅ |
| 18 | promote succeeds with passing metrics | `TestPromote` | ✅ |
| 19 | promote blocked when gate fails | `TestPromote` | ✅ |
| 20 | registry updated in-place | `TestPromote` | ✅ |
| 21 | promote without metrics skips gate | `TestPromote` | ✅ |
| 22 | end-to-end with dict drift result | `TestPipelineEndToEnd` | ✅ |
| 23 | end-to-end with object drift result | `TestPipelineEndToEnd` | ✅ |
| 24 | RetrainingJob.to_dict serialisation | `TestPipelineEndToEnd` | ✅ |
| 25 | last_trigger populated after trigger | `TestPipelineEndToEnd` | ✅ |

---

## Done Criteria Checklist

- [x] `src/codex_ml/continuous_learning/` package importable
- [x] ≥10 unit tests all pass (25 pass)
- [x] Evidence file at `workbench/evidence/gap36_continuous_learning.md`
- [x] `workbench/gap_backlog_prioritized.md` gap 36 → `✅ Implemented`
