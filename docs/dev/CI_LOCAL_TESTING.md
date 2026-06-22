# CI/Local Testing Parity Guide

**Last Updated:** 2026-06-22

> **Goal:** catch CI failures *before* pushing by running the exact same checks
> GitHub Actions runs on every PR.

---

## Why this matters

GitHub Actions spins up a clean Python 3.12 environment, installs dependencies
in a specific order, and runs pytest with specific flags.  Running a slightly
different set of flags locally (e.g., missing `--timeout`, wrong marker
expressions, different plugin versions) means a test can pass locally but fail
in CI — or vice-versa.

`scripts/dev_env_setup.sh` and `scripts/ci_local.sh` reproduce that environment
so failures surface on your machine first.

---

## Quick Start (3 commands)

```bash
# 1. Create the CI-parity virtual environment
bash scripts/dev_env_setup.sh

# 2. Activate it
source .venv_ci/bin/activate

# 3. Run the same checks CI runs on a PR
bash scripts/ci_local.sh all
```

---

## Setup: `dev_env_setup.sh`

```
bash scripts/dev_env_setup.sh [--no-torch] [--no-node]
```

| Flag | Effect |
|------|--------|
| _(none)_ | Full setup: Python check, venv, plugins, package, PyTorch, pre-commit, Node |
| `--no-torch` | Skip the ~1 GB PyTorch CPU wheel (torch-dependent tests will be skipped) |
| `--no-node` | Skip Node.js / `markdown-link-check` (documentation CI group won't run) |
| `--help` | Show usage and exit |

The script:

1. **Warns** if Python ≠ 3.12 (CI targets 3.12).
2. Creates `.venv_ci/` at the repo root (dedicated name avoids polluting your
   default venv).
3. Installs **pytest plugins first** — this is the same order as
   `resilient_validation.yml`.  Installing plugins before the package prevents
   pip from downgrading them while resolving the package's looser constraints.
4. Installs the package with `pip install -e .[dev]`.
5. Installs PyTorch CPU build from `https://download.pytorch.org/whl/cpu`
   (same index as CI).
6. Runs `pre-commit install --install-hooks`.
7. Optionally installs `markdown-link-check` via npm.
8. Verifies all tools are on `PATH` and prints version numbers.

---

## Running CI checks locally

### `ci_local.sh` subcommands

```
bash scripts/ci_local.sh <subcommand>
```

### CI workflow → local subcommand mapping

| CI Workflow | YAML file | Subcommand | When to run |
|---|---|---|---|
| Validation / fast | `validate.yml` | `fast` | Every commit |
| Resilient Suite — quick | `resilient_validation.yml` | `quick` | Every commit |
| Resilient Suite — slow | `resilient_validation.yml` | `slow` | Before opening a PR |
| Resilient Suite — integration | `resilient_validation.yml` | `integration` | Before opening a PR |
| Resilient Suite — docs | `resilient_validation.yml` | `docs` | When editing docs |
| Pre-Merge Validation | `pre-merge-validation.yml` | `premerge` | Before merging |
| Lint only | `validate.yml` + `pre-merge-validation.yml` | `lint` | After every edit |
| All key checks | — | `all` | Before pushing |

### Subcommand details

#### `fast` — Validation Pipeline

```bash
bash scripts/ci_local.sh fast
```

Runs `pre-commit` on changed files, then pytest on the four fast-smoke targets:

```
tests/test_session_logger_log_adapters.py
tests/test_session_query_cli.py
tests/utils/test_error_log.py
tests/smoke/test_artifacts_hash.py
```

Flags: `--junitxml=validation-junit.xml --maxfail=1`

#### `quick` — Resilient Suite (quick group)

```bash
bash scripts/ci_local.sh quick
```

```
pytest tests/ -v -m "not slow and not integration" --timeout=60 --tb=short --maxfail=20
```

#### `slow` — Resilient Suite (slow group)

```bash
bash scripts/ci_local.sh slow
```

```
pytest tests/ -v -m "slow" --timeout=600 --maxfail=5 --tb=short
```

#### `integration` — Resilient Suite (integration group)

```bash
bash scripts/ci_local.sh integration
```

```
pytest tests/ -v -m "integration and not slow" --timeout=300 --tb=short --maxfail=10
```

#### `docs` — Resilient Suite (documentation group)

```bash
bash scripts/ci_local.sh docs
```

Requires Node.js (`npm install -g markdown-link-check`).
Both sub-steps are non-blocking (same as CI).

#### `premerge` — Pre-Merge Validation

```bash
bash scripts/ci_local.sh premerge
```

1. `python scripts/ci/auto_fix_common_issues.py --check-only`
2. `pytest tests/ -v --tb=short -x --maxfail=3 --timeout=300`
3. `python -m ruff check src/ tests/ --output-format=github`

#### `lint` — Lint only

```bash
bash scripts/ci_local.sh lint
```

Ruff + pre-commit on changed files (fast, good for tight inner loops).

#### `all` — Everything at once

```bash
bash scripts/ci_local.sh all
```

Runs `fast → quick → premerge` in sequence and prints a combined summary.

---

## Pre-commit

pre-commit runs a set of hooks (formatting, import sorting, simple lints) on
every commit once you've run `dev_env_setup.sh`.

**Run manually on changed files:**

```bash
pre-commit run --show-diff-on-failure --files <file1> <file2>
```

**Run on all files:**

```bash
pre-commit run --all-files
```

**Auto-fix most issues:**

```bash
# Black + isort auto-format
black <file>
isort <file>

# Ruff auto-fix
python -m ruff check --fix src/ tests/
```

**Skip a hook for one commit** (use sparingly):

```bash
SKIP=ruff git commit -m "wip"
```

---

## Common failure patterns

### `ImportError` / `ModuleNotFoundError`

**Symptom:** test fails with `ModuleNotFoundError: No module named 'X'`

**Cause:** package not installed in the active venv, or optional dependency
missing.

**Fix:**

```bash
source .venv_ci/bin/activate
pip install -e .[dev]
# or for an optional dep:
pip install <package>
```

## pytest marker warning / no tests collected

**Symptom:** `PytestUnknownMarkWarning` or `collected 0 items`

**Cause:** marker not declared in `pytest.ini` / `pyproject.toml`, or marker
expression doesn't match any tests.

**Fix:** check `pytest.ini` for registered markers; add `@pytest.mark.<name>`
to your test.

### Timeout failures (`pytest-timeout`)

**Symptom:** `FAILED ... - Failed: Timeout`

**Cause:** test took longer than `--timeout=N` seconds.

**Debug:**

```bash
# Run without timeout to see the real failure
pytest tests/path/to/test.py -v --timeout=0
```

## `ruff` lint errors

**Symptom:** ruff reports F401 (unused import), E501 (line too long), etc.

**Fix:**

```bash
python -m ruff check --fix src/ tests/
python -m ruff format src/ tests/
```

### `auto_fix_common_issues.py` blocks pre-merge

**Symptom:** `premerge` subcommand fails at the auto-fix check step.

**Fix:**

```bash
python scripts/ci/auto_fix_common_issues.py          # apply auto-fixes
git add -p && git commit -m "fix: apply auto-fixes"
bash scripts/ci_local.sh premerge                   # re-verify
```

### PyTorch not found

**Symptom:** `ModuleNotFoundError: No module named 'torch'` in tests that
require it.

**Fix:** Run setup without `--no-torch`:

```bash
bash scripts/dev_env_setup.sh   # installs torch CPU build
```

---

## Environment variables that affect test behaviour

| Variable | Effect |
|---|---|
| `CODEX_ENV_PYTHON_VERSION` | Selects Python version during environment setup |
| `CODEX_SESSION_ID` | Groups log events; set automatically by CI |
| `CODEX_SESSION_LOG_DIR` | Directory for session log files (default: `.codex/sessions`) |
| `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH` | Path to the SQLite DB used by logging tools |
| `CODEX_SQLITE_POOL` | Set to `1` to enable per-session SQLite connection pooling |
| `CI` | Set to `true` by GitHub Actions; some tests gate behaviour on this |
| `PYTEST_CURRENT_TEST` | Set automatically by pytest; indicates the running test |

To mimic CI most closely, unset `CI` locally unless you specifically want CI-
gated behaviour:

```bash
unset CI
bash scripts/ci_local.sh quick
```

---

## Troubleshooting

### Script exits with "No Python interpreter found"

Install Python 3.12:

```bash
# macOS (Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt-get install python3.12 python3.12-venv

# pyenv (cross-platform)
pyenv install 3.12
pyenv local 3.12
```

## `.venv_ci` is broken / outdated

Delete it and re-run setup:

```bash
rm -rf .venv_ci
bash scripts/dev_env_setup.sh
```

### pre-commit hooks fail on unrelated files

Run only on the files you changed:

```bash
pre-commit run --files $(git diff --name-only HEAD)
```

### `pip install -e .[dev]` fails with resolver conflict

Try installing without extras first:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Then check for conflicting pins with:

```bash
pip check
```

### Tests pass locally but fail in CI

Most common reasons:

1. **Different Python version** — CI uses 3.12; check `python --version`.
2. **Plugin version mismatch** — run `pip list | grep pytest` and compare
   against the pinned versions in `resilient_validation.yml`.
3. **Missing environment variable** — CI sets `CI=true` and `GITHUB_*`
   variables; some tests check for these.
4. **Stale `.venv_ci`** — delete and recreate (see above).

---

## Shared Caching

All CI workflows and local scripts share the same cache strategy so no
package is ever downloaded twice.

### How it works

| Cache | Location | Shared between |
|-------|----------|----------------|
| pip download cache | `~/.cache/pip` | all workflows + local scripts |
| Installed virtualenv | `.venv_ci` | all workflows + local scripts |
| npm packages | `~/.npm` | workflows with `install-npm-tools: 'true'` |

#### CI cache keys

```
pip:  ${{ runner.os }}-pip-py<version>-<hash(pyproject.toml, requirements/lock.txt)>
venv: ${{ runner.os }}-venv-py<version>-<hash(pyproject.toml, requirements/lock.txt)>
```

A **venv cache hit** means the entire `pip install` step is skipped — only the
already-installed `.venv_ci` directory is restored.  A **venv cache miss**
triggers a fresh install and saves the result for the next run.

#### Local cache reuse

`dev_env_setup.sh` computes the same content hash locally:

```bash
LOCK_HASH=$(sha256sum pyproject.toml requirements/lock.txt | sha256sum | cut -c1-16)
```

If `.venv_ci/.install_hash` matches, the install is skipped entirely:

```
✅ .venv_ci is up-to-date (hash abc123def456) — skipping install
```

### Check cache status

```bash
bash scripts/dev_env_setup.sh --check-cache
```

Shows `pip cache info` and the disk usage of `.venv_ci`.

Expected sizes:

| Cache | Typical size |
|-------|-------------|
| `~/.cache/pip` | 200 – 500 MB |
| `.venv_ci` (without torch) | 400 – 800 MB |
| `.venv_ci` (with torch CPU) | 1 – 2 GB |

### Purge stale cache

```bash
bash scripts/dev_env_setup.sh --clean
```

Runs `pip cache purge` and deletes `.venv_ci`.  The next run rebuilds from
scratch (downloading fresh wheels into `~/.cache/pip`).

### Predict CI cache misses

A CI cache miss happens whenever `pyproject.toml` or `requirements/lock.txt`
changes.  You can predict the new key before pushing:

```bash
sha256sum pyproject.toml requirements/lock.txt | sha256sum | cut -c1-16
```

---

## See also

- [`scripts/dev_env_setup.sh`](https://github.com/Aries-Serpent/_codex_/blob/main/scripts/dev_env_setup.sh) — environment setup
- [`scripts/ci_local.sh`](https://github.com/Aries-Serpent/_codex_/blob/main/scripts/ci_local.sh) — CI runner
- [`.github/workflows/validate.yml`](https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/validate.yml)
- [`.github/workflows/resilient_validation.yml`](https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/resilient_validation.yml)
- [`.github/workflows/pre-merge-validation.yml`](https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/pre-merge-validation.yml)
- [`docs/dev/testing.md`](testing.md) — general testing conventions
- [`CONTRIBUTING.md`](https://github.com/Aries-Serpent/_codex_/blob/main/CONTRIBUTING.md)
