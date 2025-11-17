# Agent Harness

Run selected jobs from PR checkboxes by exporting env flags and calling:

```bash
./scripts/agent/run_selected_jobs.sh
```text

## Produces

- `audit_artifacts/agent_env.json` - Agent environment snapshot
- `artifacts/docs/**` - Generated documentation
- `audit_artifacts/**` and `reports/**` - Audit artifacts and reports

## Environment Variables

Set these before running the harness:

- `ACCELERATE_TEST=1` - Run distributed tests
- `RUN_LORA_TESTS=1` - Run LoRA tests
- `RUN_PERF_SMOKE=1` - Run performance smoke tests
- `SKIP_OPTIONAL=1` - Skip optional dependencies (default: 1)
- `FAIL_ON_MISSING=1` - Strict mode for docs build (default: 0)
- `RUN_AUDIT=1` - Run full audit pipeline (default: 1)

## Example Usage

```bash
# Run with multiple options
ACCELERATE_TEST=1 RUN_LORA_TESTS=1 SKIP_OPTIONAL=1 ./scripts/agent/run_selected_jobs.sh

# Run only docs build
SKIP_OPTIONAL=1 RUN_AUDIT=0 ./scripts/agent/run_selected_jobs.sh
```text
