# Local Gates

These checks are **local-only**. They do not create or activate any GitHub Actions workflows.
For one-command runs, a `nox` session is provided (optional).

## Prerequisites
- Python 3.10+ available on PATH.
- `pre-commit` installed (`pip install pre-commit`).
- (Optional) `jsonschema` for schema validation (`pip install jsonschema`).

## Quick Start
```bash
# 1) Fence validator
python tools/validate_fences.py

# 2) Evaluator (adjust --input as needed)
python tools/codex_evaluator.py \
  --rules manifests/codex_eval_rules.v3.json \
  --input samples/assistant_message_summary.sample.json

# 3) Manifest schema checks (optional; local-only)
python tools/schema_validate.py \
  --data manifests/selection_guard_rules.json --schema schemas/selection_guard_rules.schema.json \
  --data manifests/codex_eval_rules.v3.json --schema schemas/codex_eval_rules.v3.schema.json
```

## Convenience wrapper

```bash
./scripts/run_local_gates.sh

# uses samples/assistant_message_summary.sample.json by default

# runs schema checks if jsonschema is installed
```

## Using nox (optional)

Install dev tools:

```bash
pip install -r requirements-dev.txt
```

Run gates and tests:

```bash
nox -s gates
nox -s tests
nox -s precommit
```

## Exit codes
- `0`: All local gates passed.
- Non-zero: Check the command output for details.
