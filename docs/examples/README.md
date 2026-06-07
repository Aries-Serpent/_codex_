# Runnable Examples — Codex ML

Interactive, standalone Python scripts demonstrating key modules in this
repository. Each script can be run directly with no extra `pip install`
steps beyond what is already in the repository.

---

## Quick Start

```bash
# from the repo root
python docs/examples/drift_detection_demo.py
python docs/examples/ab_test_demo.py
python docs/examples/continuous_learning_demo.py
python docs/examples/resilience_demo.py
```

> **Tip:** Add `src/` to `PYTHONPATH` if you run from outside the repo root:
> ```bash
> PYTHONPATH=src python docs/examples/<script>.py
> ```

---

## Examples

### 1. `drift_detection_demo.py` — Data & Model Drift Detection

**Modules:** `codex_ml.monitoring.data_drift`, `codex_ml.monitoring.model_drift`

Demonstrates:
- Generating synthetic reference and drifted distributions
- Running `DataDriftDetector` with PSI and KL-divergence checks
- Running `ModelDriftDetector` with Jensen-Shannon divergence and confidence monitoring
- Printing a formatted drift report with scores, thresholds, and decisions

```bash
python docs/examples/drift_detection_demo.py
```

**Key classes:** `DataDriftDetector`, `DriftResult`, `ModelDriftDetector`, `ConfidenceStats`

---

### 2. `ab_test_demo.py` — A/B Testing

**Module:** `codex_ml.experiments.ab_testing`

Demonstrates:
- Single-metric Welch's t-test via `run_ab_test()`
- Multi-metric test suite via `ABTestSuite`
- Formatted comparison table with winner, p-value, Cohen's d, and 95% CI

```bash
python docs/examples/ab_test_demo.py
```

**Key classes:** `ABTest`, `ABTestResult`, `ABTestSuite`, `run_ab_test`

---

### 3. `continuous_learning_demo.py` — Continuous Learning & Feedback Loop

**Modules:** `codex_ml.continuous_learning`, `codex_ml.feedback`

Demonstrates:
- Full `ContinuousLearningPipeline` cycle: drift → trigger → eval gate → promote
- `FeedbackLoop` ingesting monitoring alerts and drift signals
- `should_adapt()` decision predicate
- `EvalGate` standalone threshold evaluation

```bash
python docs/examples/continuous_learning_demo.py
```

**Key classes:** `ContinuousLearningPipeline`, `EvalGate`, `EvalGateResult`,
`RetrainingJob`, `RetrainingTrigger`, `FeedbackLoop`, `FeedbackCollector`, `FeedbackEvent`

---

### 4. `resilience_demo.py` — Resilience Primitives

**Module:** `codex.resilience`

Demonstrates:
- `CircuitBreaker`: CLOSED → OPEN on failures → HALF_OPEN → CLOSED recovery
- `retry_with_backoff`: exponential backoff with jitter, flaky call recovery, and exhaustion
- `GracefulDegradation`: decorator and context-manager fallback patterns, no-fallback `DegradationError`

```bash
python docs/examples/resilience_demo.py
```

**Key classes:** `CircuitBreaker`, `CircuitOpenError`, `retry_with_backoff`,
`RetryExhausted`, `GracefulDegradation`, `DegradationError`

---

## Dependencies

All examples use **only the Python standard library plus modules from this
repository**. No additional `pip install` is required.

Each script includes a [PEP 723](https://peps.python.org/pep-0723/) metadata
block at the top (`# /// script`) documenting this explicitly.

---

## Adding New Examples

1. Create `docs/examples/<feature>_demo.py`
2. Add the PEP 723 `# /// script` header
3. Use `if __name__ == "__main__":` guard
4. Print clearly labelled output sections separated by `print("=" * 60)`
5. Add an entry to this README
6. Run the script and paste sample output into `workbench/evidence/`
