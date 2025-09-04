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

Question for ChatGPT @codex 2025-08-30T10:14:34Z:
While performing [15:pre-commit run --all-files], encountered the following error:
trim trailing whitespace hook failed; files were modified by the hook
Context: repository-wide pre-commit hooks touch many unrelated files.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT @codex 2025-08-30T10:14:34Z:
While performing [16:pytest], encountered the following error:
19 errors during collection; missing dependencies and configuration issues
Context: running full test suite without project-specific requirements installed.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT @codex 2025-08-30T10:20:22Z:
While performing [17:pytest], encountered the following error:
13 errors during collection; imports unresolved in ingestion and tracking tests
Context: updated modules without adjusting all dependent tests and missing test dependencies.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT @codex 2025-08-30T10:24:10Z:
While performing [18:pytest], encountered the following error:
6 errors during collection; ingestion tests import outdated symbols
Context: legacy tests still reference removed ingestion APIs and cached modules.
What are the possible causes, and how can this be resolved while preserving intended functionality?
Question from ChatGPT @codex 2025-09-04T09:29:11Z: While performing [2.2: dependency reality check], encountered the following error: ModuleNotFoundError: No module named 'hydra' Context: running python - <<'PY'\nimport transformers, accelerate, hydra\nprint(transformers.__version__)\nPY. What are the possible causes, and how can this be resolved while preserving intended functionality?

Question from ChatGPT @codex 2025-09-04T10:40:00Z: While performing [PH6: make gates], encountered the following error: detect-secrets flagged high-entropy strings in tools/ephem_runner.sh and tests/test_git_tag.py. Context: running `make gates` triggered repository-wide secret scanning. What are the possible causes, and how can this be resolved while preserving intended functionality?

Question from ChatGPT @codex 2025-09-04T10:45:00Z: While performing [PH6: make ci-local], encountered the following error: ModuleNotFoundError for 'fastapi', 'click', 'datasets', and other dependencies during test collection. Context: running `nox -s ci_local` with minimal environment. What are the possible causes, and how can this be resolved while preserving intended functionality?
