# Gap 38 — Automated Model Retraining Pipeline

**Status:** ✅ Implemented  
**Date:** 2025-07-14  
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Files Created

| File | Purpose |
|------|---------|
| `src/codex_ml/training/auto_retrain.py` | `AutoRetrainPipeline` + `RetrainResult` implementation |
| `tests/unit/test_auto_retrain.py` | 16 unit tests (≥6 required) |

---

## Test Results

```
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /tmp/workspace/Aries-Serpent/_codex_
configfile: pytest.ini
plugins: asyncio-1.4.0, anyio-4.9.0
asyncio: mode=Mode.AUTO
collecting ... collected 16 items

tests/unit/test_auto_retrain.py ................                                                         [100%]

============================================ 16 passed, 1 warning in 0.37s =============================================
```

All **16 tests pass** (0 failures, 0 errors).

### Test Coverage Map

| Test ID | Test name | Covers |
|---------|-----------|--------|
| T-01 | `test_should_retrain_true_when_above_threshold` | `should_retrain` → True when drift exceeds threshold |
| T-02 | `test_should_retrain_false_when_below_threshold` | `should_retrain` → False when drift_detected=False |
| T-02b | `test_should_retrain_false_when_drift_detected_but_jsd_at_threshold` | `should_retrain` → False when JSD ≤ threshold |
| T-03 | `test_prepare_retrain_config_valid_dict` | `prepare_retrain_config` produces valid config dict |
| T-04 | `test_run_triggered_true_on_drift` | `run` → `RetrainResult.triggered=True` on drift |
| T-05 | `test_run_triggered_false_on_no_drift` | `run` → `RetrainResult.triggered=False` on no drift |
| T-06 | `test_retrain_result_timestamp_utc_iso` | Timestamp is UTC ISO-8601 format |
| T-07 | `test_should_retrain_false_when_min_samples_not_met` | `min_samples` guard respected |
| T-07b | `test_should_retrain_true_when_min_samples_met` | `min_samples` guard passes when met |
| T-08 | `test_prepare_retrain_config_merges_extra_config` | Config merging: extra_config + base_config |
| T-09 | `test_run_none_base_config_does_not_raise` | `base_config=None` safe default |
| T-10 | `test_retrain_result_to_dict` | `RetrainResult.to_dict()` serialisable |
| Edge-01 | `test_should_retrain_no_js_divergence_but_drift_detected` | Confidence-only drift still triggers |
| Edge-02 | `test_invalid_drift_threshold_raises` | Invalid `drift_threshold=0.0` raises ValueError |
| Edge-03 | `test_invalid_min_samples_raises` | Invalid `min_samples=-1` raises ValueError |
| Edge-04 | `test_dispatch_payload_schema_importable` | `DISPATCH_PAYLOAD_SCHEMA` exportable |

---

## Architecture Overview

```
ModelDriftDetector.check()
        │
        ▼
  DriftResult { drift_detected, js_divergence, reasons, ... }
        │
        ▼
AutoRetrainPipeline.run(drift_result, base_config)
   ├─ should_retrain(drift_result)  ──► bool
   │      • drift_detected must be True
   │      • JSD must exceed drift_threshold (default 0.05)
   │      • samples_available must meet min_samples (default 0 = no guard)
   │
   ├─ prepare_retrain_config(base_config, drift_result)  ──► dict
   │      • merges extra_config + base_config + drift metadata
   │      • emits: drift_score, model_id, triggered_by, reasons,
   │               samples_count, retrain_timestamp, js_divergence
   │
   └─► RetrainResult { triggered, reason, config_snapshot, timestamp }
```

---

## GitHub Actions Workflow Integration

### Workflow: `.github/workflows/model-drift-retrain.yml`

The workflow supports three trigger modes:

| Trigger | Description |
|---------|-------------|
| `schedule` | Runs daily at 02:00 UTC |
| `workflow_dispatch` | Manual trigger with optional overrides |
| `repository_dispatch` | Fired programmatically via GitHub API |

### `repository_dispatch` Event Payload

**Event type:** `drift-detected`

Fire this event to trigger the retrain pipeline from `AutoRetrainPipeline`:

```bash
gh api repos/{owner}/{repo}/dispatches \
    --method POST \
    -F event_type=drift-detected \
    -F client_payload[drift_score]=0.25 \
    -F client_payload[samples_count]=5000 \
    -F client_payload[model_id]=codex-primary \
    -F client_payload[triggered_by]=auto_retrain_pipeline \
    -F client_payload[js_divergence]=0.08 \
    -F 'client_payload[reasons][]=JSD=0.08 exceeds threshold=0.05'
```

### `client_payload` JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "drift-detected repository_dispatch client_payload",
  "properties": {
    "drift_score":    { "type": "number",          "minimum": 0.0, "maximum": 1.0,
                        "description": "Aggregate drift score in [0, 1]" },
    "samples_count":  { "type": "integer",         "minimum": 0,
                        "description": "New samples available for retraining" },
    "model_id":       { "type": "string",
                        "description": "Identifier of the drifted model" },
    "triggered_by":   { "type": "string",
                        "description": "Source that fired the event" },
    "js_divergence":  { "type": ["number", "null"],
                        "description": "Raw Jensen-Shannon divergence from DriftResult" },
    "reasons":        { "type": "array", "items": { "type": "string" },
                        "description": "Human-readable drift reasons" }
  },
  "required": ["drift_score"]
}
```

The schema is also importable from Python:

```python
from codex_ml.training.auto_retrain import DISPATCH_PAYLOAD_SCHEMA
```

### Connecting AutoRetrainPipeline to the Workflow

The pipeline's `prepare_retrain_config` output maps directly to the
`client_payload` for the `repository_dispatch` event:

```python
from codex_ml.monitoring.model_drift import ModelDriftDetector
from codex_ml.training.auto_retrain import AutoRetrainPipeline

detector = ModelDriftDetector(js_threshold=0.05)
detector.update_baseline(reference_probs)
drift = detector.check(current_probs)

pipeline = AutoRetrainPipeline(drift_threshold=0.05, model_id="codex-primary")
result = pipeline.run(drift, base_config={"epochs": 3, "lr": 1e-4})

if result.triggered:
    # Fire repository_dispatch with result.config_snapshot as client_payload
    import subprocess, json
    subprocess.run([
        "gh", "api", "repos/Aries-Serpent/_codex_/dispatches",
        "--method", "POST",
        "-F", "event_type=drift-detected",
        "-F", f"client_payload={json.dumps(result.config_snapshot)}",
    ], check=True)
```

---

## Class Reference

### `RetrainResult` (frozen dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `triggered` | `bool` | Whether retraining was triggered |
| `reason` | `str` | Human-readable explanation |
| `config_snapshot` | `dict` | Prepared retrain config (empty if not triggered) |
| `timestamp` | `str` | UTC ISO-8601 timestamp (`+00:00` suffix) |

### `AutoRetrainPipeline`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `drift_threshold` | `0.05` | Min JSD to trigger retrain |
| `min_samples` | `0` | Min new samples required (0 = disabled) |
| `model_id` | `"codex-primary"` | Model identifier for config/payload |
| `extra_config` | `{}` | Base config additions merged into every config |

| Method | Signature | Returns |
|--------|-----------|---------|
| `should_retrain` | `(drift_result, samples_available=0) → bool` | Trigger decision |
| `prepare_retrain_config` | `(base_config, drift_result, samples_available=0) → dict` | Merged config |
| `run` | `(drift_result, base_config=None, samples_available=0) → RetrainResult` | Full result |
