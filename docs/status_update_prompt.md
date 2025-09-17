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
6. Outstanding Codex automation question log copied from `docs/status_update_outstanding_questions.md`, updated with any disposition changes.
Write in markdown, using tables and bullet lists. Expand on any enhanced aspects and ensure completeness.
```

## Template: Daily Status Update
Always append the outstanding question log using the canonical table stored in [`docs/status_update_outstanding_questions.md`](status_update_outstanding_questions.md). Update dispositions inline if anything changes between reports.
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

## 5. Outstanding Codex Automation Questions
<!-- Copy the canonical table from docs/status_update_outstanding_questions.md -->
{{outstanding_questions_table}}
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

## Outstanding Codex Automation Questions
<!-- Copy the canonical table from docs/status_update_outstanding_questions.md -->
{{outstanding_questions_table}}
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

## Outstanding Codex Automation Questions
<!-- Copy the canonical table from docs/status_update_outstanding_questions.md -->
{{outstanding_questions_table}}
```

## Template: Capability Snapshot
```markdown
# 📍_codex_: Capability Snapshot ({{date}})

| Capability | Maturity (1-5) | Status | Key Artifacts | Owner | Last Updated |
|------------|----------------|--------|---------------|-------|--------------|
| {{cap1}} | {{maturity1}} | {{status1}} | {{artifacts1}} | {{owner1}} | {{updated1}} |
| {{cap2}} | {{maturity2}} | {{status2}} | {{artifacts2}} | {{owner2}} | {{updated2}} |

## Outstanding Codex Automation Questions
<!-- Copy the canonical table from docs/status_update_outstanding_questions.md -->
{{outstanding_questions_table}}
```

## Template: Risk & Mitigation Log
```markdown
# 📍_codex_: Risk & Mitigation Log ({{date}})

| Risk | Impact | Likelihood | Mitigation | Status | Owner |
|------|--------|------------|------------|--------|-------|
| {{risk1}} | {{impact1}} | {{likelihood1}} | {{mitigation1}} | {{status1}} | {{owner1}} |
| {{risk2}} | {{impact2}} | {{likelihood2}} | {{mitigation2}} | {{status2}} | {{owner2}} |

## Outstanding Codex Automation Questions
<!-- Copy the canonical table from docs/status_update_outstanding_questions.md -->
{{outstanding_questions_table}}
```

## Template: Release Readiness Checklist
```markdown
# 📍_codex_: Release Readiness Checklist ({{date}})

## Checklist
- [ ] Tests passing (`nox -s tests`): {{tests_status}}
- [ ] Pre-commit (`pre-commit run`): {{precommit_status}}
- [ ] Coverage >= {{coverage_target}}: {{coverage_status}}
- [ ] Docs updated: {{docs_status}}
- [ ] Dependencies pinned: {{deps_status}}
- [ ] Smoke tests: {{smoke_status}}

## Notes
- {{note1}}
- {{note2}}

## Outstanding Codex Automation Questions
<!-- Copy the canonical table from docs/status_update_outstanding_questions.md -->
{{outstanding_questions_table}}
```

## Template: Testing Matrix
```markdown
# 📍_codex_: Testing Matrix ({{date}})

| Command | Purpose | Result |
|---------|---------|--------|
| `pre-commit run --files {{files}}` | Lint/format | {{result_precommit}} |
| `nox -s tests` | Unit tests | {{result_tests}} |
| `nox -s typecheck` | Static type checks | {{result_typecheck}} |
| `nox -s lint` | Lint suite | {{result_lint}} |

## Outstanding Codex Automation Questions
<!-- Copy the canonical table from docs/status_update_outstanding_questions.md -->
{{outstanding_questions_table}}
```
