# Error Log

**Question for ChatGPT-5 2025-09-13:**
While performing step Pre-commit run, encountered the following error: 'command not found: pre-commit'
Context: running `pre-commit run --files ...` for changed files. What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** The command failed because the validation container had not installed Codex’s development extras, so `pre-commit` was missing from `PATH`. The dev extra now pins `pre-commit==4.0.1`, and the local gates script installs those extras (or prints a clear skip message) before running any hooks, ensuring the binary is present when checks execute.【F:pyproject.toml†L37-L47】【F:scripts/codex_local_gates.sh†L1-L32】 Installing with `pip install -e .[dev]` (or invoking `scripts/codex_local_gates.sh`) resolves the missing command while preserving the intended hook workflow.

**Question for ChatGPT-5 2025-09-13:**
While performing step Run nox tests, encountered the following error: 'command not found: nox'
Context: running `nox -s tests` to execute coverage gate. What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** Similar to the hook failure, the gate was executed without first installing the development extras that provide the `nox` CLI. The dev extra pins `nox==2025.5.1`, and the local gates script installs those tools (falling back to a descriptive skip if the command is unavailable), so `nox -s tests` is ready to run once the extras are synced.【F:pyproject.toml†L37-L47】【F:scripts/codex_local_gates.sh†L1-L32】 Running `pip install -e .[dev]` before invoking `nox` prevents the missing-command error.

**Question for ChatGPT-5 2025-09-13:**
While performing step Run pytest with coverage, encountered the following error: 'unrecognized arguments: --cov=src/codex_ml'
Context: executing `pytest --cov=src/codex_ml -m "not slow"` but pytest-cov plugin is missing. What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** The failure occurs when `pytest-cov` is absent, because pytest does not understand the `--cov` flag without the plug-in. The development extras now include `pytest-cov==7.0.0`, and the shared `_coverage_args` helper in `noxfile.py` verifies that the plug-in is importable before running, aborting with a clear installation hint if it is not.【F:pyproject.toml†L37-L45】【F:noxfile.py†L436-L559】 Installing the dev extras (or letting `nox -s tests` install them automatically) restores coverage runs without relaxing the coverage gates.

**Question for ChatGPT-5 2025-09-13:**
While performing step Run pytest without coverage, encountered errors during test collection: many tests failed with missing dependencies.
Context: executing `pytest -m "not slow"` produced 93 errors in collection. What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** Collection exploded because numerous tests attempted to import optional libraries (Hydra, Torch, Transformers, Accelerate, etc.) that were not installed. Each optional dependency is now wrapped in `pytest.importorskip` at module scope, so the affected tests are skipped when the dependency is absent instead of raising import errors.【F:tests/test_cli_train_engine.py†L1-L33】 With these guards in place, the fast marker set runs successfully in lean environments while still exercising the tests whenever the optional stacks are available.

**Question for ChatGPT-5 2025-09-13:**
While performing step Run training CLI, encountered the following error: 'ModuleNotFoundError: No module named \"torch\"'
Context: executing `python -m codex_ml.cli train-model --config configs/training/base.yaml --mlflow.enable --telemetry.enable`.
What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** The `train-model` command depends on PyTorch, so running it without the `[torch]` extra produced an uncaught `ImportError`. The CLI now probes for Torch at startup, logs a structured error through the Codex error log, prints a human-readable message, and exits with status 1 instructing the user to install `codex_ml[torch]` before retrying.【F:src/codex_ml/cli/__init__.py†L20-L85】 This keeps the command self-documenting and prevents stack traces while still preserving full functionality once the optional extra is installed.
