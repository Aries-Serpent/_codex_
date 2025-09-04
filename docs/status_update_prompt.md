# Codex Status Update Prompt & Templates

## Prompt
Use the following prompt when generating a daily status update for the `_codex_` repository:

```
You are preparing a _codex_ repository status update. Include:
1. Title `📍_codex_: Status Update (YYYY-MM-DD)`.
2. Repo map: bullet list of key directories and files; note stubs or placeholders.
3. Capability audit table with columns (Capability, Status, Existing Artifacts, Gaps, Risks, Minimal Patch Plan, Rollback Plan).
4. High-Signal Findings summarizing major observations and recent enhancements.
5. Testing summary with the exact commands run and their outcomes.
Write in markdown, using tables and bullet lists. Expand on any enhanced aspects and ensure completeness.
```

## Template: Daily Status Update
```markdown
# 📍_codex_: Status Update ({{date}})

## 1. Repo Map
- Key directories: {{directories}}
- Key files: {{files}}
- Stubs & placeholders:
  - {{stub1}}
  - {{stub2}}
- Recent additions:
  - {{addition1}}
  - {{addition2}}

## 2. Capability Audit Table
| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
|-----------|--------|-------------------|------|-------|--------------------|---------------|
| {{cap1}} | {{status1}} | {{artifacts1}} | {{gaps1}} | {{risks1}} | {{patch1}} | {{rollback1}} |
| {{cap2}} | {{status2}} | {{artifacts2}} | {{gaps2}} | {{risks2}} | {{patch2}} | {{rollback2}} |

## 3. High-Signal Findings
- {{finding1}}
- {{finding2}}

## 4. Testing
- `pre-commit run --files {{files}}` – {{result_precommit}}
- `nox -s tests` – {{result_tests}}
```

## Template: Incremental Diff Report
```markdown
# 📍_codex_: Status Diff ({{date}})

## Enhancements
- {{enhancement1}}
- {{enhancement2}}

## Regressions / Gaps
- {{gap1}}

## Testing
- `pre-commit run --files {{files}}` – {{result_precommit}}
- `nox -s tests` – {{result_tests}}
```

## Template: Weekly Summary
```markdown
# 📍_codex_: Weekly Summary (Week of {{date}})

## Completed
- {{completed1}}
- {{completed2}}

## In Progress
- {{inprogress1}}

## Blockers
- {{blocker1}}

## Next Steps
- {{next1}}
```
