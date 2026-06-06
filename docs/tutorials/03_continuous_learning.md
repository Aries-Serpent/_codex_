# Tutorial 03 — Setting Up Continuous Learning

**Estimated time:** 30 minutes  
**Prerequisites:** Tutorials 01 and 02 recommended first

---

## Architecture Overview

Continuous learning closes the loop between monitoring and model improvement.
The `_codex_` pipeline follows a four-stage cycle:

```
┌─────────────────┐     score > threshold
│  Drift Detector  │ ─────────────────────────► RetrainingTrigger
└─────────────────┘                                    │
                                                       ▼
                                              ┌──────────────────┐
                                              │ AutoRetrainPipeline│
                                              └──────────┬───────┘
                                                         │ produces metrics
                                                         ▼
                                              ┌──────────────────┐
                                              │    EvalGate       │
                                              │  (quality bar)    │
                                              └──────────┬───────┘
                                                  pass   │  fail
                                                   ▼     │    ▼
                                              promote  reject (keep old model)
```

Each component is independently configurable and testable.  The
`ContinuousLearningPipeline` class wires them together into a single
callable API.

---

## Step 1 — Set Up the Pipeline

```python
from codex_ml.continuous_learning import ContinuousLearningPipeline

pipeline = ContinuousLearningPipeline(
    drift_threshold=0.2,             # PSI / drift score above which retraining is triggered
    eval_gate_min_accuracy=0.80,     # new model must achieve ≥ 80 % accuracy
    eval_gate_max_loss=0.50,         # new model loss must be ≤ 0.50
    eval_gate_min_improvement_pct=1.0,  # must be ≥ 1 % better than baseline
)
```

**Parameters:**

| Parameter | Meaning |
|-----------|---------|
| `drift_threshold` | Minimum drift score to trigger retraining |
| `eval_gate_min_accuracy` | Minimum accuracy the new model must reach |
| `eval_gate_max_loss` | Maximum loss the new model may have |
| `eval_gate_min_improvement_pct` | Required % improvement over baseline accuracy |

Any of the `eval_gate_*` parameters can be set to `None` to skip that check.

---

## Step 2 — Detect Drift and Decide Whether to Retrain

Feed a drift result (from `DataDriftDetector` or `ModelDriftDetector`) to
`should_retrain`:

```python
from codex_ml.monitoring.data_drift import DataDriftDetector

# Run drift detection (see Tutorial 01 for full details)
drift_detector = DataDriftDetector(psi_threshold=0.2)
reference = [0.05, 0.20, 0.40, 0.25, 0.10]
current   = [0.03, 0.10, 0.30, 0.35, 0.22]   # significant shift

psi_result = drift_detector.detect_psi(reference, current, feature_name="age_bucket")
print(f"PSI score: {psi_result.score:.4f}  drifted: {psi_result.drifted}")
# → PSI score: 0.2741  drifted: True

if pipeline.should_retrain(psi_result):
    print("🔄 Drift threshold exceeded — retraining triggered")
```

`should_retrain` accepts both `DriftResult` objects and plain dicts, so you
can integrate any upstream drift signal:

```python
# From a plain dict (e.g. deserialized from a monitoring alert)
drift_info = {"score": 0.31, "drifted": True, "method": "psi"}
pipeline.should_retrain(drift_info)  # → True
```

---

## Step 3 — Create a Retraining Job

```python
job = pipeline.trigger_retrain(config={
    "epochs": 10,
    "learning_rate": 1e-4,
    "batch_size": 64,
    "dataset_version": "2025-01-15",
})

print(f"Job ID: {job.job_id}")
# → Job ID: retrain_20250115T102341

print(job.trigger.reason)    # "drift_threshold_exceeded"
print(job.trigger.drift_score)  # 0.2
```

The `RetrainingJob` is a lightweight descriptor — it does **not** start
training.  Pass it to your training harness:

```python
# Run your actual training (pseudocode — adapt to your setup)
new_model_path, eval_metrics = my_training_harness.run(job.config)

# eval_metrics must contain at least:
# {"accuracy": float, "loss": float, "baseline_accuracy": float}
eval_metrics = {
    "accuracy": 0.865,
    "loss": 0.38,
    "baseline_accuracy": 0.830,   # old model's accuracy
}
```

---

## Step 4 — Gate with `EvalGate`

Before promoting the new model, run it through the eval gate:

```python
if pipeline.eval_gate(eval_metrics):
    print("✅ New model passed all quality thresholds")
else:
    print("❌ Model rejected — keeping previous version")
    print("   Reasons:", pipeline._gate.evaluate(eval_metrics).reasons)
```

### Using `EvalGate` directly

You can also instantiate `EvalGate` independently for standalone use:

```python
from codex_ml.continuous_learning.eval_gate import EvalGate

gate = EvalGate(
    min_accuracy=0.80,
    max_loss=0.50,
    min_improvement_pct=2.0,
)

result = gate.evaluate({
    "accuracy": 0.865,
    "loss": 0.38,
    "baseline_accuracy": 0.830,
})

print(f"Passed: {result.passed}")
# → Passed: True  (4.2 % improvement, acc=0.865, loss=0.38)
```

---

## Step 5 — Promote the Model

```python
registry = {}   # your real registry (dict, MLflow, Weights & Biases, etc.)

promoted = pipeline.promote(
    model_path="/models/candidate/model_v2.pt",
    registry=registry,
    metrics=eval_metrics,   # re-runs eval gate as a safety check
)

if promoted:
    print(f"🚀 Model promoted: {registry['model_path']}")
    print(f"   Promoted at:   {registry['promoted_at']}")
```

---

## Step 6 — Wire in the `FeedbackLoop`

The `FeedbackLoop` aggregates monitoring signals (alerts, drift events) and
exposes a `should_adapt()` predicate that you can poll from any orchestrator.

```python
from codex_ml.feedback.loop import FeedbackLoop
from codex_ml.feedback.events import FeedbackEvent

loop = FeedbackLoop(
    adapt_threshold=3,   # trigger after 3 "alert" events in the last 10
    adapt_window=10,
)

# Ingest a drift result
loop.on_drift(psi_result)

# Ingest a monitoring alert (dict or arbitrary object)
loop.on_alert({"severity": "warning", "source": "prometheus", "message": "CPU spike"})
loop.on_alert({"severity": "critical", "source": "data_pipeline", "message": "null rate spike"})
loop.on_alert({"severity": "warning", "source": "prometheus", "message": "latency p99 > 2s"})
loop.on_alert({"severity": "warning", "source": "prometheus", "message": "error rate > 5%"})

# Poll the decision predicate
if loop.should_adapt():
    print("📣 Feedback loop recommends adaptation — triggering pipeline")
    if pipeline.should_retrain(psi_result):
        job = pipeline.trigger_retrain()
```

### Full end-to-end loop

```python
from codex_ml.monitoring.data_drift import DataDriftDetector
from codex_ml.continuous_learning import ContinuousLearningPipeline
from codex_ml.feedback.loop import FeedbackLoop

pipeline = ContinuousLearningPipeline(
    drift_threshold=0.2,
    eval_gate_min_accuracy=0.80,
    eval_gate_max_loss=0.50,
    eval_gate_min_improvement_pct=1.0,
)
drift_detector = DataDriftDetector()
feedback = FeedbackLoop()
registry = {}

def on_new_batch(reference, current):
    result = drift_detector.detect_psi(reference, current)
    feedback.on_drift(result)

    if feedback.should_adapt() or pipeline.should_retrain(result):
        job = pipeline.trigger_retrain({"epochs": 5, "lr": 1e-4})
        metrics = run_training(job.config)   # your training harness
        pipeline.promote("/models/new.pt", registry=registry, metrics=metrics)
```

---

## Integration with `AutoRetrainPipeline`

For a higher-level interface that manages training state internally, use
`AutoRetrainPipeline` from `codex_ml.training.auto_retrain`:

```python
from codex_ml.training.auto_retrain import AutoRetrainPipeline

auto = AutoRetrainPipeline(config={"epochs": 10, "lr": 1e-4})

# Trigger a retraining run
result = auto.run(
    drift_score=psi_result.score,
    current_metrics={"accuracy": 0.78, "loss": 0.52},
)

if result.promoted:
    print(f"AutoRetrain promoted model: {result.model_path}")
```

---

## What happens next?

Retraining in production means your service is making real calls to external
APIs, databases, and model servers.  Protect those calls from cascading
failures with `CircuitBreaker` and `retry_with_backoff`.

**[Tutorial 04 — Building Resilient ML Services](04_resilience.md)**

---

> **See also:**  
> `src/codex_ml/continuous_learning/` · `src/codex_ml/feedback/` ·
> `src/codex_ml/training/auto_retrain.py`
