# Testing Guide

This project uses **pytest** as the primary test runner with comprehensive CI/CD integration. Alternative automation is available via [nox](https://nox.thea.codes/).

## Quick Start with Pytest

**Basic test run:**
```bash
pytest                           # Run all tests
pytest -q                        # Quiet mode
pytest -v                        # Verbose mode
```

**With coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
open htmlcov/index.html          # View HTML coverage report
```

**Run specific tests:**
```bash
pytest tests/test_specific.py                    # Single file
pytest tests/test_specific.py::test_function     # Single test
pytest -k "tokenizer"                            # Match test names
```

**Using test markers:**
```bash
pytest -m smoke                  # Quick validation tests
pytest -m "not slow"             # Skip slow tests
pytest -m integration            # Integration tests
pytest -m ml                     # ML/tensor dependent tests
```

See `pytest.ini` for all available markers and `tests/README.md` for comprehensive instructions.

## CI/CD Integration

### Automated Testing

All push and PR events trigger `.github/workflows/ci-pytest.yml`:

**Features:**
- Python 3.11+ on ubuntu-latest
- Full pytest suite with coverage
- 90% coverage threshold (configurable via `COVERAGE_THRESHOLD`)
- Multiple report formats (HTML, XML, JSON)
- Artifact uploads (30-day retention)
- Automatic PR comments with coverage summary and download links

**Manual workflow trigger:**
1. Navigate to Actions → "CI - Pytest with Coverage"
2. Click "Run workflow"
3. Select branch and run

**Viewing results:**
- Check workflow status in PR/commit
- Download coverage artifacts from workflow run summary
- Review PR comment for coverage summary

### Coverage Enforcement

- **Minimum threshold**: 90% (enforced in CI)
- **Configurable**: Set `COVERAGE_THRESHOLD` environment variable in workflow
- **Build fails** if coverage below threshold
- **Local validation**: `pytest --cov=src --cov-fail-under=90`

## Alternative: Nox Sessions

For advanced automation, use nox sessions:

```bash
nox -s lint typecheck tests_min        # fast checks
nox -s tests                           # full unit suite with coverage
nox -s perf_smoke                      # quick performance sentinel
nox -s model-smoke                     # instantiate a CPU model for dtype/device coverage
```

> **Important:** Run `pip install -e '.[test]'` (or `uv sync --extra test`) before invoking
> `nox -s tests` so the Hydra `hydra.extra` pytest plugin is available in offline
> environments.

## Local test gates

The default entry point is deterministic and fully offline:

```bash
# one-shot helpers (Makefile includes these shortcuts)
make -f codex.mk codex-tests           # nox -s tests -- <pytest args>
make -f codex.mk codex-tests-fast      # pytest -q
make -f codex.mk codex-coverage        # coverage report
```

- `nox -s tests` installs the project in editable mode, runs `pytest` with
  `pytest-cov`/`pytest-randomly`, and enforces coverage using
  `.coveragerc` (`fail_under = 80`, `skip_covered = true`).
- When running with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `pytest.ini`
  preloads `pytest-cov` via `-p pytest_cov` so coverage flags continue to
  parse correctly without additional CLI arguments.
- Pass extra flags through to pytest with `nox -s tests -- -k tokenizer`.
- After the run, `coverage report` re-applies the configured threshold; tighten
  locally via `COVERAGE_MIN=90 nox -s tests` or `coverage report --fail-under=90`.

`pytest-randomly` seeds the suite (`randomly_seed = 42` in `pytest.ini`) so reruns
remain reproducible while still surfacing order-dependent failures.

Tests are deterministic: `tests/conftest.py` seeds `random`, `numpy` and
`torch` so repeated runs produce consistent results. Slow tests are skipped by
default; include `--runslow` to execute them. GPU specific tests are marked
`gpu` and are skipped automatically when CUDA is unavailable.

Example:

```bash
pytest -q -k overfit_smoke            # run a single training smoke test
pytest --runslow                      # opt in to slow tests
```

## Security gates

Run the lightweight safety checks before publishing changes:

```bash
make codex-secrets-scan                     # scan git diff for obvious secrets
make codex-test-safety                      # run prompt sanitiser + scanner tests
```

Both commands execute locally (no network calls). The secrets scan exits with a
non-zero status when suspicious patterns are detected so you can review the
lines before pushing.

## Documentation & link audit

Use the documentation audit to ensure navigation entries, inline Markdown
links, and referenced tests stay in sync:

```bash
python -m analysis.tests_docs_links_audit --repo . \
  --out artifacts/docs_link_audit/report.json --fail-on-issues
```

The command prints a JSON summary and records it under
`artifacts/docs_link_audit/`.  The `--fail-on-issues` flag causes the script to
exit with status code `1` when missing navigation targets, dangling Markdown
links, or nonexistent `tests/` references are discovered.
