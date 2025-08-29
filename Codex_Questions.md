# Codex Questions

- 2025-08-29: Running targeted pytest commands failed: `Required test coverage of 70% not reached. Total coverage: 24.01%`. Wider test suite or coverage settings may be needed.

- 2025-08-29: Running full pytest suite failed due to import mismatch in tests/tracking/test_mlflow_utils.py.

## 2025-08-29
- Where should `training_callbacks.py` reside? Module currently missing.
- Multiple copies of `mlflow_utils.py` and `checkpointing.py` found; which is authoritative?

Question for ChatGPT-5 2025-08-29T04:48:40Z:
While performing [14:pre-commit run --all-files], encountered the following error:
Bandit/semgrep commands missing and numerous import/format issues across the repository.
Context: repository-wide pre-commit hooks fail beyond touched files.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT-5 2025-08-29T04:48:40Z:
While performing [14:pytest -q], encountered the following error:
Required test coverage of 70% not reached. Total coverage around 10%.
Context: running limited tests in large project with default coverage thresholds.
What are the possible causes, and how can this be resolved while preserving intended functionality?
