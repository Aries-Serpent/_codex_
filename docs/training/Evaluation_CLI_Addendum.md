# Evaluation CLI — Contracts & Overrides (Addendum)
> Generated: Previous Cycle-10-17 21:05:18 UTC | Author: mbaetiong

Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## Entrypoints
- codex-eval -> codex_ml.cli.entrypoints:eval_main
- python -m codex_ml.cli.evaluate (Hydra variant)

## Behavior Contracts
- JSON/text outputs: stdout only for machine-readable output.
- stderr: reserved for warnings/errors; must remain empty in JSON mode.
- --dry-run: validates configuration without executing heavy workloads.
- --metrics-sink: comma-separated sinks (choices: ndjson,csv). Defaults to `ndjson`.
- Environment override: CODEX_EVAL_ENTRY to switch dispatcher target.

## Artifacts
- NDJSON metrics log: `<output>/metrics.ndjson` (default sink)
- CSV metrics log: `<output>/metrics.csv` (when `--metrics-sink` includes `csv`)
- Summary JSON: `<output>/summary.json`
- NDJSON records: `<output>/records.ndjson`
- Errors: .codex/errors.ndjson (on failure with reason codes)

## Quick Checks
```bash
codex-eval --dry-run
python -m codex_ml.cli.list_plugins --format json  # stderr must be empty
```text

## Tests Reference
- tests/test_evaluate_cli.py
- tests/test_run_eval_cli.py
- tests/eval/test_eval_runner_smoke.py
