# Validation pipeline

This repository ships a lightweight validation harness that works consistently
on laptops and in CI. The tooling is made up of four main pieces:

1. `scripts/run_validation.sh` – a shell wrapper that prepares an isolated
   virtualenv, runs linters and tests, and collects artifacts.
2. `tools/validate.py` – a Python orchestration CLI that wraps the shell script
   and emits machine-readable summaries.
3. `.github/workflows/validate.yml` – a GitHub Actions workflow that executes the
   validation pipeline on pull requests and in optional scheduled runs.
4. This document – describes how to use and extend the tooling.

## Quick start

* Fast local smoke checks:

  ```bash
  ./scripts/run_validation.sh --fast
  ```

  Runs pre-commit hooks and a small set of hermetic tests
  (`tests/test_session_logger_log_adapters.py`,
  `tests/test_session_query_cli.py`, `tests/utils/test_error_log.py`, and
  `tests/smoke/test_artifacts_hash.py`) inside `.venv_validation`.

* Full validation (includes dev dependencies and coverage):

  ```bash
  ./scripts/run_validation.sh --full
  ```

  Installs `requirements-dev.txt`, optional heavy dependencies, and runs the
  entire `tests` target with coverage output.

* Programmatic invocation / JSON summary:

  ```bash
  python tools/validate.py --mode fast --output validation_summary.json
  ```

  The CLI prints a short status message, executes the shell runner, and writes a
  summary JSON payload (default `validation_summary.json`).

## Key environment variables

| Variable        | Purpose                                                                 | Default |
|-----------------|-------------------------------------------------------------------------|---------|
| `VALIDATE_MODE` | Overrides the default mode (`fast`/`full`) used by the shell runner.    | `fast`  |
| `VALIDATE_BASE_REF` | Optional base ref used to collect files for pre-commit when the working tree is clean. | `` |
| `PYTEST_OPTS`   | Additional options appended to the pytest command.                      | ``      |
| `TEST_FAST`     | Whitespace-separated pytest selectors used when running in fast mode.   | `tests/test_session_logger_log_adapters.py tests/test_session_query_cli.py tests/utils/test_error_log.py tests/smoke/test_artifacts_hash.py` |
| `HEAVY_DEPS`    | Extra pip packages installed only when running `--full`.                | ``      |

All environment variables are respected by both the shell runner and the Python
CLI. For example, to add a custom pytest expression you can run:

```bash
PYTEST_OPTS='-k "cli and smoke"' ./scripts/run_validation.sh --fast
```

## Selecting tests

* `--files` accepts a comma-separated list of pytest targets (file paths or
  `file::test` selectors) and bypasses the default selection logic.
* `TEST_FAST` controls the fast-mode default. Override it to point to a
  bespoke smoke target (for example
  `TEST_FAST='tests/cli/test_cli_viewer.py tests/smoke/test_artifacts_hash.py'`).
* `tools/validate.py --rerun-failures` reads `validation-junit.xml` and reruns
  only the failing tests from the previous execution.

## Hooks and customization

Any executable scripts placed under `.github/validate-hooks.d/` are executed by
`run_validation.sh` before (`pre`) and after (`post`) the core validation steps.
Hooks receive two positional arguments: the active mode (`fast`/`full`) and the
stage (`pre`/`post`). Use this to add project-specific checks without editing
the main runner.

Common customization points:

* Update `requirements-dev.txt` when new development dependencies are needed.
* Set `HEAVY_DEPS` in CI or locally to install optional wheels (for example
  `HEAVY_DEPS="torch transformers"`).
* Use `PYTEST_OPTS` to add `-m`/`-k` filters or parallelism flags.

## Artifacts

The validation tooling produces the following files at the repository root:

| Artifact                | Source command                                        | Purpose                              |
|-------------------------|--------------------------------------------------------|--------------------------------------|
| `validation.log`        | `run_validation.sh`                                    | Human-readable log of the run        |
| `validation-junit.xml`  | `pytest --junitxml=validation-junit.xml`               | Test results for CI integrations     |
| `coverage.xml`          | `pytest --cov --cov-report=xml` (full mode only)       | Coverage reporting                   |
| `validation_summary.json` | `tools/validate.py --output validation_summary.json` | Machine-readable summary for tooling |

Artifacts are uploaded from CI jobs for later inspection.

## GitHub Actions integration

The workflow defined in `.github/workflows/validate.yml` runs two jobs:

* **Fast validation** – executes on every pull request event. It runs the
  validation CLI in `--mode fast` and uploads the log, JUnit XML, and JSON
  summary artifacts.
* **Full validation** – runs only on the nightly schedule or when dispatched
  manually. It executes `--mode full`, generating coverage as part of the run,
  and uploads the corresponding artifacts.

Because the shell runner is self-contained, the workflow does not need to
pre-install dependencies beyond Python itself. The same commands can be executed
locally for parity with CI.

## Troubleshooting tips

* **Missing optional dependencies** – use `--fast` while iterating locally to
  avoid heavy installs. When full validation is required, set `HEAVY_DEPS` or
  run `--full` so the runner installs everything from `requirements-dev.txt`.
* **Rerunning failures** – after a failing run check `validation_summary.json`
  or `validation-junit.xml` for failing selectors, then rerun via
  `python tools/validate.py --rerun-failures`.
* **Cleaning the environment** – delete `.venv_validation/` if the virtual
  environment becomes inconsistent; the runner will recreate it automatically on
  the next invocation.

With these components in place, developers get a consistent validation command
while CI can surface actionable feedback and structured artifacts.
