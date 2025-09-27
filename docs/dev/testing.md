# Testing Guide

This project uses [nox](https://nox.thea.codes/) for local automation. The most
useful sessions are:

```bash
nox -s lint typecheck tests_min        # fast checks
nox -s tests                           # full unit suite with coverage
nox -s perf_smoke                      # quick performance sentinel
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
