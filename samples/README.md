# Samples

This folder contains minimal inputs you can use to exercise local gates.

## Files
- `assistant_message_summary.sample.json` — JSON suitable for `tools/codex_evaluator.py`.
- `broken_fence.sample.md` — Intentionally invalid fenced block (should fail fence validator).

## Quick Start
```bash
python tools/validate_fences.py
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json
```text

## Notes
- These samples are safe to commit and reference in docs.
- Do not convert them into CI jobs; keep execution local-only.
