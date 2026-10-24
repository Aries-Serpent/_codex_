# Guide findings — 2026-10-23

Inspected source: `/home/runner/work/_codex_/_codex_/docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md`.
This record does not change the guide, GitHub settings, governance values, or secrets.

| Location | Finding | Bounded decision |
|---|---|---|
| Lines 1, 4, 7, 9–11 | Last synced is 2026-07-13; Last Updated is both 2026-07-11 and 2026-06-22; the embedded status says current as of 2026-03-07. Versions v0.2.0 and 1.7.0 coexist. Line 7 has an unclosed bold delimiter. | Treat these as conflicting editorial metadata, not current hosted state. |
| Issue 2, line 499 | The resolution ends at `CODEX_ENV_PYTHON_VERSION updated 2026-07-13`, without the value or closing Markdown table delimiter. | Record truncation; do not reconstruct the missing text from memory. |
| Issue 5, line 527 | The resolution ends at `CODEX_ADMIN_KEY was added as an org secret (updated 2026-07-13`, with an unclosed parenthesis and table cell. | Record truncation; no inference of current secret existence or scope. |
| Lines 388, 490–491 | Node version `18` appears in a struck-through historical problem statement; the active table and resolution say `22`. | This is not an unresolved active 18-versus-22 setting conflict: the resolution explicitly labels 18 historical. Keep historical and current documentation separate. |
| Line 741 | The Issue 2 checklist text is also truncated at `Update 2026-07-13`. | Include in a future documentation-only repair; not repaired by this reconciliation. |

Follow-up: the documentation maintainer should restore the incomplete prose from
version history and consolidate header metadata. Do not change governance values
to make the documentation agree. Live repository variables were read separately
for this reconciliation; a guide's cached values do not grant authorization.
