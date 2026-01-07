# ADR: Local Status Reporter (STATUS_REPORT.md)

## Status
Accepted — Previous Cycle-10-26

## Context
We need a deterministic, local-only way to summarize repository health and candidate evaluations into a markdown report suitable for PR reviews and audit logs. The solution must not enable CI and should compose existing gates.

## Decision
- Add `tools/status_report.py` to orchestrate existing local gates (fences, schemas, evaluator, selection guard) and emit a human-readable `STATUS_REPORT.md`.
- Provide a manual pre-commit hook (`codex-status`) and docs: `docs/ops/status_reports.md`, with a concise template `docs/templates/status_update.md`.
- Include unit tests validating output presence and key sections.

## Consequences
**Positive**
- One-command status recap for reviewers; consistent signal across PRs.
- Reuses existing local tools; easy to extend.

**Trade-offs**
- Another thin wrapper to maintain; mitigated by minimal surface and tests.

## Rollback
- Delete `tools/status_report.py`, `docs/ops/status_reports.md`, `docs/templates/status_update.md`, tests, and the pre-commit hook entry.

## Testing
- `tests/status/test_status_report.py` verifies markdown generation and core sections.
