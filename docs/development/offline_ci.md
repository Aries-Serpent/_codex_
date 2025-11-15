# Offline CI Runner

The GitHub Actions workflow `ci.yml` is intentionally disabled for base
branches. Use `tools/offline_ci_runner.py` to reproduce the pipeline locally
without enabling hosted runners.

```bash
python tools/offline_ci_runner.py
```

This executes, in order:

1. `nox -s security`
2. `nox -s coverage`
3. `nox -s typecheck`
4. `nox -s env-snapshot`

All logs are written to `artifacts/offline_ci/`. Pass `--dry-run` to print the
commands without executing them, or `--steps security coverage` to run a subset.

The runner mirrors the job structure defined in `.github/workflows/ci.yml`
while keeping execution entirely offline.

