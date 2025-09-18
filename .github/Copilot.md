# Validation Pipeline

This repository ships a lightweight validation harness that mirrors the checks
run in CI so that contributors can iterate quickly while still producing the
artifacts needed by automation. The tooling is intentionally split into three
layers so you can pick the right entry point for the job:

1. `scripts/run_validation.sh` – bash wrapper for local usage and ad-hoc CI jobs.
2. `tools/validate.py` – Python orchestrator that produces machine-readable
   summaries and supports richer workflows (re-run failures, pass pytest args).
3. `.github/workflows/validate.yml` – GitHub Actions workflow that wires the
   harness into PR validation and scheduled full test runs.

## Quick start

Run the fast smoke-test bundle (no heavy dependencies) from the repository root:

```bash
./scripts/run_validation.sh --fast
```

Run the full suite (installs `requirements-dev.txt` inside an isolated virtual
environment and executes all tests):

```bash
./scripts/run_validation.sh --full
```

For programmatic use or when you need JSON output, call the Python orchestrator:

```bash
python tools/validate.py --mode fast --verbose
```

The orchestrator writes its summary to `validation_summary.json` by default and
mirrors it to any custom `--output` path you provide.

## What the runner does

1. Creates/uses a cached virtual environment at `.venv_validation`.
2. Installs minimal dependencies in `--fast` mode (`pytest`, `pre-commit`,
   `ruff`) or the full `requirements-dev.txt` in `--full` mode.
3. Runs pre-commit hooks (set `VALIDATE_SKIP_PRECOMMIT=1` to skip locally).
4. Executes optional repository hooks from `.github/validate-hooks.d/` (drop an
   executable shell script here to add custom steps; skip with
   `VALIDATE_SKIP_HOOKS=1`).
5. Runs pytest with either the curated fast set or the entire `tests/`
   directory, emitting `report.xml` (JUnit) and, when `coverage` is available,
   `coverage.xml`.
6. Stores a human-readable log in `validation.log`.

Environment knobs that the runner understands:

| Variable | Purpose |
|----------|---------|
| `VALIDATE_MODE` | Propagated into the log/summary for debugging |
| `PYTEST_EXTRA` | Extra arguments passed through to pytest |
| `VALIDATE_SKIP_PRECOMMIT` | Set to `1` to skip pre-commit hooks |
| `VALIDATE_SKIP_HOOKS` | Set to `1` to disable `.github/validate-hooks.d/` scripts |

## Python orchestrator features

`tools/validate.py` wraps the shell runner and adds:

- `--files` to target a comma-separated list of test files.
- `--pytest-args "-k expr"` to pass arbitrary pytest flags (stored in the
  summary and handed to coverage runs too).
- `--last-failed` (`pytest --lf`) for quick re-runs of only the failing tests.
- `--no-run` to convert existing artifacts into JSON without executing tests
  again (useful if the shell runner was triggered separately).
- Automatic parsing of `report.xml` and `coverage.xml` into summary statistics
  (`tests`, `failures`, line coverage percent, etc.).
- Tail output from `validation.log` embedded in the JSON for quick triage.

The JSON schema is stable and designed to be consumed by dashboard tooling or
other automation. If you specify a custom `--output` the tool also keeps the
canonical `validation_summary.json` in sync for downstream consumers.

## GitHub Actions workflow

`.github/workflows/validate.yml` wires the orchestrator into CI:

- **fast-check** (pull requests): runs on `ubuntu-latest`, uses Python 3.12,
  executes `python tools/validate.py --mode fast`, and uploads the log, JUnit
  XML, coverage report (if generated), and JSON summary as artifacts.
- **full-suite** (scheduled/nightly or manual dispatch): reuses the same steps
  but runs in `--full` mode to exercise the heavier dependency stack.

Both jobs cache `~/.cache/pip` for speed. Because the orchestrator writes
`validation_summary.json`, downstream automation can read that artifact to make
policy decisions (e.g., gating on coverage).

## Extending the pipeline

- Add repository-specific hooks by dropping executable scripts into
  `.github/validate-hooks.d/`. Each script receives the current mode (`fast` or
  `full`) as the first argument and should exit non-zero on failure.
- Adjust the fast test selection directly inside `scripts/run_validation.sh` or
  use `PYTEST_EXTRA="-k <expr>"` while iterating locally.
- Update `requirements-dev.txt` with any new tooling dependencies; the runner
  will pick them up automatically in `--full` mode.
- If you need to install optional heavy dependencies for fast mode, add a hook
  script or pre-install them in the virtual environment before running the
  validation script.

## Troubleshooting tips

- Missing optional dependencies? Start with `--fast` while coding and rely on
  the scheduled `--full` job (or a local `--full` run) for full coverage.
- Want to rerun only the last failures? Use `python tools/validate.py --last-failed`.
- Need to skip linting temporarily? Run with `VALIDATE_SKIP_PRECOMMIT=1` but be
  sure to re-enable before committing.
- Stale artifacts bothering you? Remove `.venv_validation/`, `validation.log`,
  and `report.xml`; everything will be regenerated on the next run.
