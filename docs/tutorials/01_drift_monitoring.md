# Tutorial 01 — Monitoring Data and Model Drift

**Last Updated:** 2026-06-22

**Estimated time:** 20 minutes  
**Prerequisites:** Python 3.10+, `_codex_` on `PYTHONPATH`

---

## What is drift, and why does it matter?

A model trained on historical data silently degrades when the real-world
distribution it sees at inference time diverges from the distribution it was
trained on.  This is called **drift**.

There are two kinds:

| Kind | What shifts | Symptom |
|------|-------------|---------|
| **Data drift** | The *feature* distribution changes | Input statistics no longer match training stats |
| **Model / concept drift** | The *model output* distribution changes | Predictions cluster differently, confidence drops |

Undetected drift leads to silent accuracy loss — the model keeps running but
returns increasingly wrong answers.  The `_codex_` monitoring stack catches
drift early so you can trigger retraining before users are affected.

---

## Part 1 — Data Drift with `DataDriftDetector`

### Step 1: Import and instantiate

```python
from codex_ml.monitoring.data_drift import DataDriftDetector

# PSI > 0.2 or KL > 0.5 → drift flagged
detector = DataDriftDetector(psi_threshold=0.2, kl_threshold=0.5)
```

**Parameters:**

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `psi_threshold` | `0.2` | PSI score above which drift is flagged |
| `kl_threshold` | `0.5` | KL-divergence above which drift is flagged |
| `epsilon` | `1e-8` | Smoothing constant (avoids log(0)) |

## Step 2: Prepare distributions

Both methods accept plain Python lists (or any `Sequence[float]`).  Each list
represents a binned probability distribution — values are **automatically
normalised**, so you can pass raw counts or proportions.

```python
# Suppose your feature "age_bucket" has 5 bins
# (these are proportions from a training reference set)
reference = [0.05, 0.20, 0.40, 0.25, 0.10]

# Current week's production data
current   = [0.03, 0.15, 0.35, 0.32, 0.15]  # older users, slight shift
```

## Step 3: Run PSI and KL checks

```python
psi_result = detector.detect_psi(reference, current, feature_name="age_bucket")
kl_result  = detector.detect_kl(reference, current,  feature_name="age_bucket")

print(f"PSI  score={psi_result.score:.4f}  drifted={psi_result.drifted}  severity={psi_result.severity}")
print(f"KL   score={kl_result.score:.4f}   drifted={kl_result.drifted}   severity={kl_result.severity}")
```

Example output:
```
PSI  score=0.0412  drifted=False  severity=none
KL   score=0.0198  drifted=False  severity=none
```

### Step 4: Interpret `DriftResult`

`detect_psi` and `detect_kl` both return a `DriftResult` dataclass:

```python
from codex_ml.monitoring.data_drift import DriftResult  # already imported above

print(psi_result.to_dict())
# {
# "method": "psi",
# "score": 0.0412,
# "threshold": 0.2,
# "drifted": False,
# "severity": "none",
# "details": {"feature_name": "age_bucket", "num_bins": 5, ...},
# "detected_at": "2025-01-15T10:23:41+00:00"
# }
```

**PSI severity thresholds:**

| PSI | Interpretation |
|-----|----------------|
| < 0.1 | No significant change |
| 0.1 – 0.2 | Slight change — monitor closely |
| > 0.2 | Significant change — consider retraining |

## Step 5: Epoch-level convenience wrapper

In a training loop you can call `check_epoch` to run both checks at once:

```python
results = detector.check_epoch(
    reference=reference,
    current=current,
    epoch=12,
    feature_name="age_bucket",
)

# results is {"psi": DriftResult, "kl": DriftResult}
if results["psi"].drifted or results["kl"].drifted:
    print("Drift detected — consider retraining!")
```

---

## Part 2 — Model Drift with `ModelDriftDetector`

### Step 1: Import and instantiate

```python
from codex_ml.monitoring.model_drift import ModelDriftDetector

detector = ModelDriftDetector(
    js_threshold=0.05,       # Jensen-Shannon divergence threshold
    confidence_threshold=0.4 # flag epoch if mean confidence drops below this
)
```

### Step 2: Set a baseline

Call `update_baseline` once on the reference epoch (e.g. your validation set
before deployment):

```python
import random

# Simulate reference prediction probabilities for a 3-class classifier
# Each inner list is [p_class0, p_class1, p_class2] for one sample
reference_probs = [
    [0.80, 0.15, 0.05],
    [0.10, 0.75, 0.15],
    [0.05, 0.20, 0.75],
    # ... more samples
]

detector.update_baseline(reference_probs)
```

## Step 3: Check each production epoch

```python
# After a week of production traffic
current_probs = [
    [0.55, 0.30, 0.15],   # less confident — model is less certain
    [0.30, 0.45, 0.25],
    [0.20, 0.35, 0.45],
]

result = detector.check(current_probs)

print(f"Drift detected: {result.drift_detected}")
print(f"JS divergence:  {result.js_divergence:.4f}")
print(result.summary())
```

## Step 4: React to the result

```python
if result.drift_detected:
    # Log to your alerting system, trigger a Slack notification, etc.
    print(f"⚠️  Model drift! JS={result.js_divergence:.4f}")
    # → see Tutorial 03 to automate retraining from here
```

---

## What happens next?

When drift is detected you typically want to retrain automatically.
**[Tutorial 03 — Setting Up Continuous Learning](03_continuous_learning.md)**
shows you how to wire `DataDriftDetector` and `ModelDriftDetector` into a
`ContinuousLearningPipeline` that handles the full detect → retrain → evaluate
→ promote loop.

---

> **See also:**  
> `src/codex_ml/monitoring/data_drift.py` · `src/codex_ml/monitoring/model_drift.py`
