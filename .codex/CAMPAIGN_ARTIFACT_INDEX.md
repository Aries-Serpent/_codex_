# Post-Merge Campaign Artifact Index

**Campaign Date**: 2026-06-25T22:26:00Z
**Pre-Merge State**: Commit 8d0c55b, branch copilot/fix-ci-failure-triage-report
**Status**: COMPLETE - Ready for post-merge validation
**Next Session Entry Point**: `.codex/POST_MERGE_SESSION_CONTINUATION_BRIEF_V2.md`

---

## Quick Navigation Guide

### For Next Session (Start Here)

**READ FIRST** → `.codex/POST_MERGE_SESSION_CONTINUATION_BRIEF_V2.md`
- Critical timeline and decision points
- What to expect post-merge
- Next steps checklist
- Success/failure indicators

**THEN RUN** → `.codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md`
- 6 validation gates with exact commands
- Decision tree for results

**IF VALIDATION FAILS** → `.codex/POST_MERGE_REVERSION_PROTOCOL.md`
- Root cause analysis scenarios
- Reversion procedures
- Escalation guidance

---

## All Campaign Artifacts

### ✅ Environment & Dependency Documentation

| File | Size | Purpose |
|------|------|---------|
| `POST_MERGE_ENVIRONMENT_BASELINE.md` | 5.5K | Pre-existing dependency gaps (zstandard, sqlalchemy), environment separation matrix, known error patterns |
| `PRE_MERGE_TEST_COLLECTION_STATUS.json` | 2.6K | Baseline test collection state for post-merge comparison, environment setup details |

**Action**: Use to understand what's NORMAL (pre-existing) vs. what's REGRESSION (new) post-merge

---

### ✅ Validation Framework

| File | Size | Purpose |
|------|------|---------|
| `POST_MERGE_COPILOT_SETUP_VALIDATION.md` | 7.6K | 6-gate validation checklist (YAML, block scalar, env vars, LFS, Python, test collection) |
| `POST_MERGE_REVERSION_PROTOCOL.md` | 7.8K | Decision tree for failure scenarios, reversion procedures, escalation protocols |
| `PRE_MERGE_COPILOT_SETUP_STATE.yml` | 8.3K | Snapshot of working copilot-setup-steps.yml (first 180 lines) |

**Action**: Run validation gates from POST_MERGE_COPILOT_SETUP_VALIDATION.md immediately post-merge

---

### ✅ Dependency & Test Collection Handling

| File | Size | Purpose |
|------|------|---------|
| `POST_MERGE_MISSING_DEPS_INSTALL.md` | 9.9K | 7-step diagnostic playbook for missing optional deps, decision tree, automation script |

**Action**: Use if test collection reveals zstandard/sqlalchemy import errors (expected pre-existing)

---

### ✅ Session Continuation & Coordination

| File | Size | Purpose |
|------|------|---------|
| `POST_MERGE_SESSION_CONTINUATION_BRIEF_V2.md` | 9.8K | Comprehensive guide to post-merge validation, expected state, known issues, decision tree |
| `POST_MERGE_SESSION_CONTINUATION_BRIEF.md` | 7.0K | Earlier version (simpler) - use BRIEF_V2 instead |

**Action**: BRIEF_V2 is the primary entry point for next session

---

### ℹ️ Existing Campaign Artifacts (For Reference)

These files were created in previous planning/execution phases and provide additional context:

| File | Size | Purpose |
|------|------|---------|
| `POST_MERGE_ACTION_PLAN.md` | 6.0K | Initial post-merge work plan |
| `POST_MERGE_AGENT_SESSION_PROMPT.md` | 12K | Agent execution instructions |
| `POST_MERGE_COPILOT_EXECUTION_PROMPT.md` | 13K | Detailed execution guidance |
| `POST_MERGE_SECURITY_SUMMARY.md` | 7.9K | Security considerations post-merge |
| `POST_MERGE_MONITORING_PLAN.md` | 1.2K | Monitoring strategy |

---

## Campaign Execution Flowchart

```
Session Start (Post-Merge)
│
├─→ Read: POST_MERGE_SESSION_CONTINUATION_BRIEF_V2.md
│   └─ Understand expected state, timeline, decision points
│
├─→ Run: 6 Validation Gates (from POST_MERGE_COPILOT_SETUP_VALIDATION.md)
│   ├─ Gate 1: YAML syntax (yamllint)
│   ├─ Gate 2: Block scalar syntax
│   ├─ Gate 3: Environment variables
│   ├─ Gate 4: LFS policy
│   ├─ Gate 5: Python environment
│   └─ Gate 6: Test collection baseline
│
├─→ Decision Point:
│   ├─ All gates PASS?
│   │  └─→ ✅ Document results, PROCEED to work
│   │
│   ├─ Gates 1 or 2 FAIL (YAML)?
│   │  └─→ ⚠️ Read POST_MERGE_REVERSION_PROTOCOL.md, REVERT
│   │
│   ├─ Gate 6 shows 10+ NEW errors?
│   │  └─→ ⚠️ Read POST_MERGE_REVERSION_PROTOCOL.md, REVERT
│   │
│   └─ Other gates warn/fail?
│      └─→ Investigate, follow decision tree in BRIEF_V2
│
└─→ If All Pass:
    ├─ Update AGENT_ACCOUNTABILITY_REPORT.md
    ├─ Document validation results
    └─→ Proceed with post-merge work
```

---

## Campaign Success Indicators

✅ **This campaign is successful if:**

1. Pre-existing environmental issues (zstandard, sqlalchemy) are clearly documented
2. Post-merge agent knows what's NORMAL vs. what's REGRESSION
3. Validation framework (6 gates) is easy to execute
4. Reversion criteria are unambiguous (no loops)
5. Next session has clear entry point
6. All artifacts are repository-tracked (not /tmp/)

---

## Key Principles (Don't Forget!)

### 1. Reversion is Terminal
- If YAML fails (gates 1-2) → REVERT immediately
- If 10+ NEW test errors → REVERT immediately
- Reversion requires human review before re-merge
- It's NOT a retry mechanism

### 2. Pre-Existing is Normal
- zstandard ImportError → Expected in minimal environments
- sqlalchemy ImportError → Expected (transitive dep)
- These are documented in POST_MERGE_ENVIRONMENT_BASELINE.md
- Don't escalate as regressions

### 3. No Loops
- Run each gate once
- Make a decision (proceed, investigate, revert)
- Don't re-run same validation multiple times
- If unsure, escalate to @mbaetiong

### 4. Validation First, Work Second
- Complete all 6 gates BEFORE starting new work
- Takes ~30 minutes
- Prevents wasted cycles debugging merged code

### 5. Document Everything
- Record validation results in AGENT_ACCOUNTABILITY_REPORT.md
- Log any changes to environment setup
- Keep audit trail of what was tested/passed

---

## Questions? Reference These

| Question | Document |
|----------|----------|
| What errors are pre-existing? | POST_MERGE_ENVIRONMENT_BASELINE.md |
| How do I validate post-merge? | POST_MERGE_COPILOT_SETUP_VALIDATION.md |
| What if validation fails? | POST_MERGE_REVERSION_PROTOCOL.md |
| Missing zstandard/sqlalchemy? | POST_MERGE_MISSING_DEPS_INSTALL.md |
| What's my first action? | POST_MERGE_SESSION_CONTINUATION_BRIEF_V2.md |
| How do I know success? | POST_MERGE_SESSION_CONTINUATION_BRIEF_V2.md (success section) |

---

## Campaign Timeline

**Phase 1** (2026-06-25): Dependency verification ✅
**Phase 2** (2026-06-25): Validation framework creation ✅
**Phase 3** (2026-06-25): Test collection handling ✅
**Phase 4-5** (2026-06-25): Session continuation groundwork ✅
**Phase 6** (2026-06-25): Accountability integration ✅

**Next Phase** (Post-Merge): Execute validation gates and proceed with work

---

## Files Location

All files in `.codex/` directory (repository-tracked, NOT /tmp):
```
.codex/
├── POST_MERGE_*.md (validation, reversion, dependencies, brief)
├── PRE_MERGE_*.* (baseline snapshots)
└── [Other .codex files]
```

Access from any session: `cd /home/runner/work/_codex_/_codex_/.codex/`

---

## Campaign Created By

- **Date**: 2026-06-25T22:26:00Z
- **Status**: COMPLETE & READY FOR MERGE
- **Approval**: Reference artifacts for merge decision
- **Next Session**: Inherit all campaign documentation

---

**Start here for next session**: `.codex/POST_MERGE_SESSION_CONTINUATION_BRIEF_V2.md`
