# Sample — Intent Validation & Plan of Action (for _codex_)

> This is a worked example showing the gate format filled for a typical “local gates” change.

**Intent Validation**
We will add local-only evaluator & fence checks, plus the approval-gate template and docs. We will not enable any GitHub Actions. Success means deterministic local runs, updated docs, ADRs, and small, reviewable patches.

**Assumptions**
- ✓ Python 3.11+ available locally.
- ✓ `pre-commit` is allowed for local hooks.
- ? New docs should appear in mkdocs nav (confirm).
- ⚠️ License header format for new Python files (needs confirmation).

**Open Questions**
1. Should evaluator weights be versioned in the filename (e.g., `v3`)?  
2. Where should samples live (`samples/` vs `.codex/samples/`)?  
3. Add a manual `nox` session for gates or stick to plain Python invocations?  

**Phases of Action**
1. Docs — add template, ADR, ops guide; link from contributing.  
2. Quality Gates — add rubric, evaluator, fence validator, pre-commit hooks (local).  
3. Self-Management — CLI wrapper and tests for evaluator & fences.

**Risks and Mitigations**
| Risk | Severity | Mitigation |
| --- | --- | --- |
| Strict fences reject PR text | Medium | Provide docs & examples; allow local bypass for emergency with documented follow-up. |
| Weights feel too strict | Low | Centralize in JSON; adjust via small PRs with ADR updates. |

**Deliverables**
- Template, ADRs, ops docs; evaluator + rules; fences validator; CLI wrapper; tests; samples.

**Acceptance Criteria**
- Local commands pass; evaluator enforces env guard & forbidden cues; docs linked in contributing; no Actions created.

**Rollback / Fallback**
Revert added files and pre-commit entries; leave ADR with “Superseded” note for audit trail.
