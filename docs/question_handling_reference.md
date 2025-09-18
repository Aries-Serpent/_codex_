# Codex Research Question Handling Reference

This note provides a quick-access guide for ChatGPT Codex sessions to track, answer, and retire outstanding research questions. It consolidates where questions live, how we resolve them, and how to query their status while debugging.

## Canonical sources of truth

- **Primary log:** [`docs/status_update_outstanding_questions.md`](status_update_outstanding_questions.md) — authoritative table mirrored in every Codex status update.
- **Session scratchpad:** [`.codex/notes/Codex_Questions.md`](../.codex/notes/Codex_Questions.md) — ad-hoc capture of Q&A snippets created during automation workflows.
- **Historical error log:** [`ERROR_LOG.md`](../ERROR_LOG.md) — recent failures promoted into the canonical table.
- **Legacy audit artifacts:** e.g., [`CODEBASE_AUDIT_2025-08-26_203612.md`](../CODEBASE_AUDIT_2025-08-26_203612.md) where early unanswered questions were first recorded.

Always reconcile new questions against the canonical table so that status updates remain in sync.

## End-to-end handling workflow

1. **Capture immediately.** When a blocking error occurs, log it using the standard "Question for ChatGPT" template (timestamped, with step, error, and context).
2. **Triage the cause.** Determine whether the issue stems from missing tooling, configuration gaps, or environment drift.
3. **Update the canonical log.** Append or revise the row in `docs/status_update_outstanding_questions.md`, noting the disposition (`Action required`, `Documented resolution`, etc.) and whether follow-up is still needed.
4. **Record the answer.** Document the remediation (install instructions, config changes, or deferral rationale) either directly in the table or in `.codex/notes/Codex_Questions.md` for more narrative answers.
5. **Mirror in status reports.** Ensure the latest status update copies the refreshed table so leadership can see open research items.
6. **Close or defer.** Once a fix lands or the work is intentionally postponed, flip the status (`Retired`, `Deferred`) and explain the reasoning.

## Status taxonomy

| Status | Meaning | When to use |
| --- | --- | --- |
| Action required | Work remains before the blocker is cleared. | Tests still failing, tooling missing, or manual remediation pending. |
| Documented resolution | A workaround or fix is known and documented, but may require discipline to follow. | Environment setup instructions exist; no further code change needed. |
| Mitigated / deferred | The issue is intentionally postponed with safeguards in place. | Strict MkDocs mode disabled until docs are stabilized. |
| Retired | The question is obsolete because the underlying code or process changed. | Legacy CLI flags removed, so the old failure can no longer occur. |

`docs/status_update_outstanding_questions.md` also tracks whether the item is still valid (`Yes`, `No`, or `Deferred`), giving quick visibility into which questions need engineering effort.

## Querying outstanding questions

Use these commands during a session to surface open or historical questions:

```bash
# List every recorded question block in the repo
rg "Question for ChatGPT" -n

# View the canonical outstanding table
sed -n '1,160p' docs/status_update_outstanding_questions.md

# Inspect the scratchpad for narrative answers
sed -n '1,120p' .codex/notes/Codex_Questions.md
```

Because the canonical table is committed to the repository, it can be searched or diffed like any other markdown, providing a "queryable" record without requiring a database.

## Quick response checklist

- [ ] Capture the error in the standard question format (timestamp + step + context).
- [ ] Decide whether the issue is new or already logged; update timestamps on existing rows when repeats occur.
- [ ] Summarize the remediation in the `Current disposition` column so future sessions know the expected fix.
- [ ] Copy the refreshed table into the next status update or summary document.
- [ ] If the blocker is resolved, downgrade the status and mark "Still Valid?" accordingly.

Following this loop ensures unanswered research questions stay visible, their answers remain discoverable, and every session has an immediate reference point for ongoing blockers.

## Recent remediation log

- **2025-09-17:** Validation gate outage (missing `pre-commit`, `nox`, and `pytest-cov`) closed by commit `f0a1d82`. The remediation pins the executables, records CLI availability in `.codex/session_logs.db`, and enforces JSON coverage artifacts for auditability.
