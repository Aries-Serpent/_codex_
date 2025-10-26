# Local Gates: Evaluator & Fence Integrity

These checks are **local-only**. They do not create or activate any GitHub Actions.

## Prerequisites
- Python 3.10+ available on PATH.
- `pre-commit` installed (`pip install pre-commit`).

## Quick Start
```bash
pre-commit install
pre-commit run --all-files
```

## Manual run
```bash
# 1) Fence integrity
python tools/validate_fences.py

# 2) Evaluator (adjust --input as needed)
python tools/codex_evaluator.py \
  --rules manifests/codex_eval_rules.v3.json \
  --input samples/assistant_message_summary.sample.json

# (Alternatively, point --input to your own message file or summary JSON.)
```

## Convenience wrapper
```bash
./scripts/run_local_gates.sh
# uses samples/assistant_message_summary.sample.json by default
```

## Exit codes
- `0` = success
- `1` = hard fail condition (fences broken, CI activation cues, etc.)

## Typical inputs
- **Rules**: `manifests/codex_eval_rules.v3.json`
- **Input**: a raw message or a JSON summary containing candidate messages. If the file is JSON, the evaluator will try to read `message_text` or fall back to entire file text.

## Notes
- Hooks are added to `.pre-commit-config.yaml` with `stages: [commit]` (fence) and `stages: [manual]` (evaluator).
- No network calls are required; all checks run locally.
