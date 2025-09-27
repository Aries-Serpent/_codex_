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
