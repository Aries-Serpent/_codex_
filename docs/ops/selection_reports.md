# Local Selection Reports

Produce a local-only **SELECTION_REPORT.md** recommending the best assistant candidate (1–4) given an input summary JSON.

## Quick Start
```bash
python tools/selection_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --out SELECTION_REPORT.md
```text

## What it does
- Validates the input structure and extracts the assistant variants.
- Runs evaluator scoring (rubric fit).
- Enforces selection-guard signals (docs surface & guardrails).
- Applies deterministic tie-breaks with a clear rationale.
- Writes a human-readable `SELECTION_REPORT.md` and exits non-zero only on **hard structural** failures.

## Notes
- This is **local-only** with no network calls.
- If optional evaluator deps are missing, the tool prints install hints and exits with a friendly non-zero.

## See also
- `docs/ops/status_reports.md` for generating a repo `STATUS_REPORT.md`.
- `docs/templates/status_update.md` for the rich status template.
