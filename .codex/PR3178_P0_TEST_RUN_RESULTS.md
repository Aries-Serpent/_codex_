# P0.2 Test Run Results (PR #3178)

Date: 2026-02-09T15:45:44Z

## Environment
- PYENV_VERSION: 3.12.12
- pytest: 9.0.2
- pytest-timeout: 2.4.0 (installed to enable `--timeout`)

## Commands Executed
```bash
PYENV_VERSION=3.12.12 PYTHONPATH=src pytest tests/ -v -m "not slow" \
  --tb=short \
  --timeout=300 \
  --maxfail=0 \
  2>&1 | tee .codex/test_run_complete_20260209_154455.log
```

## Summary
- Collection: 12,843 items
- Selected: 12,732
- Skipped: 226
- Deselected: 111
- Errors: 149 during collection (run interrupted)
- Failures: 0
- Pass rate: N/A (collection errors prevented execution)

## Primary Error Categories Observed
- Missing dependencies: numpy, yaml (PyYAML), hydra, mlflow, torch
- Typer attribute error surfaced during collection

## Log Files
- .codex/test_run_complete_20260209_154455.log (full run output)
- .codex/test_run_complete_.log (initial attempt without pytest-timeout; included for audit)

## Next Actions
1. Install required test dependencies (numpy, PyYAML, hydra-core, mlflow, torch, typer compatibility).
2. Re-run full suite to complete collection and capture pass/fail counts.
3. Proceed to P0.3 failure categorization once collection completes.
