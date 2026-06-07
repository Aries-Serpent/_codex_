# Tutorials

Practical, hands-on guides for using the `_codex_` ML platform.  Each tutorial
walks through a concrete use-case with working Python code you can paste
straight into a script or Jupyter notebook.

| # | Tutorial | Description |
|---|----------|-------------|
| 01 | [Monitoring Data and Model Drift](01_drift_monitoring.md) | Detect distribution shift in feature data and model predictions using `DataDriftDetector` and `ModelDriftDetector`. |
| 02 | [Running A/B Tests on Model Outputs](02_ab_testing.md) | Compare two model variants statistically with Welch's t-test via `run_ab_test` and `ABTestSuite`. |
| 03 | [Setting Up Continuous Learning](03_continuous_learning.md) | Wire drift detection to automated retraining using `ContinuousLearningPipeline`, `EvalGate`, and `FeedbackLoop`. |
| 04 | [Building Resilient ML Services](04_resilience.md) | Protect external service calls with `CircuitBreaker`, `retry_with_backoff`, and `GracefulDegradation`. |

## Prerequisites

- Python 3.10+
- `_codex_` installed (or the `src/` directory on your `PYTHONPATH`)
- `scipy` is optional but recommended for the A/B testing tutorial

## Quick Install

```bash
# from the repository root
pip install -e ".[dev]"
# or with minimal deps
pip install -e ".[minimal]"
```

## Suggested Learning Path

If you are new to the platform, read the tutorials in order:

```
01 → understand what drift looks like
02 → compare model versions with statistics
03 → automate the detect → retrain → promote cycle
04 → harden your service for production
```

Each tutorial links to the next one so you can follow the chain naturally.

---

> **Found an issue?** Open an issue or pull request — see
> [CONTRIBUTING.md](../../CONTRIBUTING.md).
