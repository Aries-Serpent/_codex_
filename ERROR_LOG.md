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

**Question for ChatGPT-5 2025-09-15:**
While performing step Best-Effort:TaskA:import_yaml, encountered the following error: 'ModuleNotFoundError: No module named "yaml"'.
Context: Attempting to import PyYAML for safe_dump while creating `configs/training/base.yaml`. What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-24):** The repository relied on importing PyYAML at module import time, so lean environments without that optional dependency crashed before reaching any fallbacks. We added `codex_ml.utils.yaml_support` to wrap `safe_load`/`safe_dump` with a descriptive `MissingPyYAMLError`, then updated every YAML consumer (config loaders, tokenizer pipeline, trainer, and registry) to call those wrappers and surface actionable guidance instead of failing.【F:src/codex_ml/utils/yaml_support.py†L1-L71】【F:src/codex_ml/utils/config_loader.py†L11-L105】【F:src/codex_ml/tokenization/pipeline.py†L11-L39】 With these guards in place the code now skips YAML-specific paths or emits a clear reinstall hint when PyYAML is absent, preserving the intended workflows once the package is installed.

**Question for ChatGPT-5 2025-09-15:**
While performing step Finalisation:pytest, encountered the following error: 'pytest failed due to missing optional dependencies (torch, numpy, pydantic, transformers)'.
Context: Running `pytest -q` for training CLI additions. What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-24):** Pytest was collecting modules that require heavy optional libraries, and the absence of `pydantic` caused `tests/config/test_validate_config.py` to raise before pytest could mark the test as skipped. The shared `tests/conftest.py` already tags entire suites behind optional dependency checks, and we extended the config tests to call `pytest.importorskip("pydantic")` so they now skip cleanly when the package is missing.【F:tests/conftest.py†L9-L133】【F:tests/config/test_validate_config.py†L1-L48】 This keeps the fast, offline gate green while still exercising the tests whenever the ML stack is present.

**Question for ChatGPT-5 2025-09-23:**
While performing step coverage (Run pytest coverage gate), encountered the following error: 'nox -s coverage fails: torch stub lacks utils.data.Dataset'.
Context: Running `nox -s tests -> coverage`; `AttributeError: module 'torch' has no attribute 'utils'`. What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-24):** The container had a stub `torch` package that imported but lacked `torch.utils`, so coverage runs crashed inside test collection. The local gates script now fails fast when `inspect_torch` detects a stub and prints the official CPU reinstall command, and pytest treats a stub exactly like a missing dependency so Torch-specific suites are skipped instead of exploding.【F:scripts/codex_local_gates.sh†L74-L88】【F:tests/conftest.py†L21-L133】 Installing the official PyTorch wheels satisfies the check; otherwise the suite skips Torch-bound tests and documents the remediation path.
