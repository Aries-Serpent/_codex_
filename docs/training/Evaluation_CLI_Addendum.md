# Evaluation CLI — Contracts & Overrides (Addendum)
> Generated: 2025-10-17 21:05:18 UTC | Author: mbaetiong

Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## Entrypoints
- codex-eval -> codex_ml.cli.entrypoints:eval_main
- python -m codex_ml.cli.evaluate (Hydra variant)

## Behavior Contracts
- JSON/text outputs: stdout only for machine-readable output.
- stderr: reserved for warnings/errors; must remain empty in JSON mode.
- --dry-run: validates configuration without executing heavy workloads.
- Environment override: CODEX_EVAL_ENTRY to switch dispatcher target.

## Artifacts
- NDJSON: .codex/metrics.ndjson
- CSV summary: outputs/<run>/summary.csv
- Errors: .codex/errors.ndjson (on failure with reason codes)

## Quick Checks
```bash
codex-eval --dry-run
python -m codex_ml.cli.list_plugins --format json  # stderr must be empty
```

## Tests Reference
- tests/test_evaluate_cli.py
- tests/test_run_eval_cli.py
- tests/eval/test_eval_runner_smoke.py
