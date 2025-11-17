# Selection Guard — Docs Surface + Guardrails

This guard ensures the **chosen** assistant message carries the required documentation surface and safety artifacts (rubric overview, ops doc, checklist/example, negative sample, presence-check tests), preventing regressions like “message #4 lacks docs surface while #3 has it”.

## What it checks
- Required paths/signals (configurable in `manifests/selection_guard_rules.json`) are present in the candidate's **diff** or **PR message**.
- Reports a ranked table and (optionally) validates your current selection via `--selected`.

## Run
```bash
python tools/selection_guard.py \
  --rules manifests/selection_guard_rules.json \
  --input summary-02.json \
  --selected 3
```text

Exit codes:
- `0` — pass (selected candidate meets required signals)
- `1` — fail (selected candidate missing signals)
- `2` — no candidate satisfies all required signals (investigate)

## Notes
- This tool is **local-only** (no network).
- It is complementary to the evaluator; use both for robust selection.
- Works with objects shaped like `turn_mapping.task_e_*~*.turn.worklog.messages[*]` and common PR/diff payloads.
