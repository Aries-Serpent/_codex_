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

# 3) Reasoning regression suite (ensures theorem/math/tool probes stay green)
python -m codex_ml.eval.evaluator reasoning-suite \
  --config configs/evaluation/reasoning/proof.yaml \
  --config configs/evaluation/reasoning/math.yaml \
  --config configs/evaluation/reasoning/tools.yaml \
  --threshold reasoning/theorem_accuracy>=1.0 \
  --threshold reasoning/math_verification>=1.0 \
  --threshold reasoning/tool_audit>=1.0

# 4) Manifest schema checks (optional; local-only)
python tools/schema_validate.py \
  --data manifests/selection_guard_rules.json --schema schemas/selection_guard_rules.schema.json \
  --data manifests/codex_eval_rules.v3.json --schema schemas/codex_eval_rules.v3.schema.json
```text

The Hydra-ready configs for these probes live under `configs/evaluation/reasoning/` and
produce NDJSON metrics alongside JSON summaries in `artifacts/reasoning/`.

## Convenience wrapper

```bash
./scripts/run_local_gates.sh

# uses samples/assistant_message_summary.sample.json by default

# runs reasoning suite + evaluator + schemas when available

# runs schema checks if jsonschema is installed
```text

## Using nox (optional)

Install dev tools:

```bash
pip install -r requirements-dev.txt
```text

Run gates and tests:

```bash
nox -s gates
nox -s tests
nox -s precommit
```text

## Exit codes
- `0`: All local gates passed.
- Non-zero: Check the command output for details.
