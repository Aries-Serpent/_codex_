# Testing Guide

This project uses [nox](https://nox.thea.codes/) for local automation. The most
useful sessions are:

```bash
nox -s lint typecheck tests_min        # fast checks
nox -s tests                           # full unit suite with coverage
nox -s perf_smoke                      # quick performance sentinel
```

Tests are deterministic: `tests/conftest.py` seeds `random`, `numpy` and
`torch` so repeated runs produce consistent results. Slow tests are skipped by
default; include `--runslow` to execute them. GPU specific tests are marked
`gpu` and are skipped automatically when CUDA is unavailable.

Example:

```bash
pytest -q -k overfit_smoke            # run a single training smoke test
pytest --runslow                      # opt in to slow tests
```
