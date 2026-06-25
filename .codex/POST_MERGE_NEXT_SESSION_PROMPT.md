# Post-Merge Next Session Prompt — Entry Point for Continuation

**Created**: 2026-06-25T22:33Z  
**Merge Status**: PR #5084 merged to main (expected)  
**Next Session Objective**: Validate post-merge stability and continue pending work

---

## 🚀 CRITICAL: DO THIS FIRST (Next Session)

### Minute 0-2: Pre-Load Mandatory Files
Before making ANY changes, read these in order:

1. ✅ `.codex/CODEBASE_AGENCY_POLICY.md` — Mandatory operating policy
2. ✅ `.codex/AGENTIC_REPO_STATE.md` — Auth and autonomy status
3. ✅ `.codex/POST_MERGE_ENVIRONMENT_BASELINE.md` — Pre-existing issues
4. ✅ `.codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md` — 6-gate framework
5. ✅ This file — Next session entry point

### Minute 2-12: Run 6 Validation Gates

Execute these commands in order from `.codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md`:

```bash
# Gate 1: YAML Syntax Check
yamllint .github/workflows/copilot-setup-steps.yml

# Gate 2: Block Scalar Verification
grep -A 10 "run: |" .github/workflows/copilot-setup-steps.yml | head -20

# Gate 3: Environment Variables
grep -E "COPILOT_AGENT_CCA_VERSION_LOCK|COPILOT_AGENT_DEDUPLICATION_ENABLED|COPILOT_AGENT_TURN_ISOLATION_ENABLED" .github/workflows/copilot-setup-steps.yml

# Gate 4: LFS Policy
grep "GIT_LFS_SKIP_SMUDGE" .github/workflows/copilot-setup-steps.yml

# Gate 5: Python Environment
python --version && pip list | grep -E "setuptools|hydra-core|omegaconf"

# Gate 6: Test Collection Baseline
pytest --collect-only 2>&1 | tee .codex/post-merge-test-collection-actual.txt
```

**Expected Results**:
- ✅ Gate 1 (YAML): No syntax errors
- ✅ Gate 2 (Block Scalar): Lines 141-147 using `run: |` format
- ✅ Gate 3 (Env Vars): All 3 CCA version lock vars present
- ✅ Gate 4 (LFS): `GIT_LFS_SKIP_SMUDGE=1` in workflow
- ✅ Gate 5 (Python): 3.12+, setuptools<82, hydra-core present
- ⚠️ Gate 6 (Tests): 20 collection errors expected (pre-existing zstandard import failures)

### Minute 12-15: Decision Point

Based on Gate Results:

**✅ ALL GATES PASS** (or only pre-existing zstandard errors):
```
→ Document results in AGENT_ACCOUNTABILITY_REPORT.md
→ Update .codex/POST_MERGE_VALIDATION_CHECKLIST.md with pass status
→ PROCEED to post-merge work phase
```

**❌ YAML SYNTAX FAILS** (Gate 1 or 2):
```
→ DO NOT PROCEED
→ Review .codex/POST_MERGE_REVERSION_PROTOCOL.md immediately
→ Execute REVERT decision tree — this is terminal
→ Contact @mbaetiong with exact error details
```

**⚠️ OTHER GATES FAIL** (3, 4, 5, 6 — but not 1/2):
```
→ If 10+ NEW test collection errors (vs 20 baseline):
   → Review root cause in pytest output
   → Investigate whether related to post-merge changes
   → May need reversion if caused by merge
→ If env var or LFS failure:
   → Check external GitHub Actions secret injection (not our control)
   → Document as infrastructure gap, proceed
→ Otherwise proceed with caution and document
```

---

## 📋 Expected Environment State (Post-Merge)

### What WILL Be Present ✅
- Python 3.12+
- setuptools<82, wheel
- hydra-core, omegaconf
- torch, transformers
- All base dependencies from requirements/base.txt

### What WON'T Be Present ⚠️
- `zstandard` (optional, causes 20 test collection errors — PRE-EXISTING)
- `sqlalchemy` (transitive dependency issue — PRE-EXISTING)
- Some optional ML/testing packages (skip gracefully with markers)

### What Changed Post-Merge 🔄
- ✅ PR #5084 merged: Campaign groundwork + auth backward compatibility
- ✅ `.codex/` contains 8 campaign documentation files (fully tracked)
- ✅ `src/codex/auth/` contains backward compatibility wrappers
- ✅ AGENT_ACCOUNTABILITY_REPORT.md updated with campaign context
- ✅ CHANGELOG.md reflects all changes

---

## 🎯 Post-Merge Work Phases (After Validation)

### Phase 1: Validation Documentation (30 min)
If all gates pass:
```
1. Create .codex/POST_MERGE_VALIDATION_RESULTS.md with:
   - Timestamp of validation run
   - Pass/fail status for each gate
   - Any warnings or pre-existing issues noted
   - Time taken to validate
2. Update docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md:
   - Add "POST_MERGE_SESSION_VALIDATION" section
   - Document gate results
   - Record that copilot-setup-steps.yml stability confirmed
```

### Phase 2: Optional Dependency Resolution (1-2 hours)
If zstandard/sqlalchemy imports are blocking critical tests:
```
1. Read .codex/POST_MERGE_MISSING_DEPS_INSTALL.md (7-step playbook)
2. Install missing optional deps:
   pip install zstandard sqlalchemy
3. Re-run test collection and verify improvement
4. Document results
```

### Phase 3: Continue Pending Work
After validation passes, proceed with:
- [ ] Addressing any remaining review comments from pre-merge (if any)
- [ ] Implementing next campaign phase objectives
- [ ] Running full test suite to establish baseline
- [ ] Creating campaign completion summary

---

## ⚠️ When to ESCALATE (Terminal Decisions)

### REVERT (Terminal — No Retry)
- ❌ YAML parse error in copilot-setup-steps.yml (Gate 1 fails)
- ❌ Block scalar syntax broken (Gate 2 fails — lines 141-147)
- ❌ Python version incompatibility (3.11 or lower in Gate 5)
- ❌ 10+ NEW test collection errors not related to zstandard

**If Revert Triggered**:
```
1. Document exact error in .codex/POST_MERGE_REVERSION_LOG.md
2. Execute reversion per .codex/POST_MERGE_REVERSION_PROTOCOL.md
3. Create escalation issue with @mbaetiong tagged
4. STOP all other work
5. Wait for human review before re-merge attempt
```

### ESCALATE (Requires Human Judgment)
- ⚠️ Environment variables missing (external GitHub Actions issue)
- ⚠️ LFS policy failure (git configuration issue)
- ⚠️ Ambiguous test failures (could be merge-related or pre-existing)

**If Escalation Needed**:
```
1. Document findings in AGENT_ACCOUNTABILITY_REPORT.md
2. Create GitHub issue with detailed investigation
3. Assign to @mbaetiong with decision recommendation
4. Wait for guidance before proceeding
```

---

## 📊 Success Indicators (You'll Know It's Working)

✅ **Validation Complete**:
- All 6 gates execute without fatal errors
- YAML syntax validation passes
- Python environment correct (3.12+)
- Test collection shows expected baseline (20 pre-existing errors acceptable)

✅ **Post-Merge Stability Confirmed**:
- `copilot-setup-steps.yml` runs without errors
- Session preload step (lines 141-147) executes successfully
- No NEW regressions introduced by merge
- Campaign groundwork files are intact and tracked

✅ **Ready for Continuation**:
- All documentation updated
- AGENT_ACCOUNTABILITY_REPORT.md reflects post-merge state
- Campaign objectives tracked and next steps clear
- No blocking issues preventing forward progress

---

## 🔗 Related Documents

| Document | Purpose | When to Use |
|----------|---------|------------|
| `.codex/POST_MERGE_ENVIRONMENT_BASELINE.md` | Pre-existing issues catalog | Reference during Gate 6 (test collection) |
| `.codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md` | 6-gate validation details | Execute gates step-by-step |
| `.codex/POST_MERGE_REVERSION_PROTOCOL.md` | Reversion decision tree | If YAML fails or 10+ new test errors |
| `.codex/POST_MERGE_MISSING_DEPS_INSTALL.md` | Dependency installation playbook | If optional deps blocking critical tests |
| `.codex/CAMPAIGN_ARTIFACT_INDEX.md` | Quick navigation flowchart | Quick reference for all campaign docs |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | Session accountability | Update with post-merge validation results |

---

## 🚨 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **YAML Parse Error** | → REVERT (read POST_MERGE_REVERSION_PROTOCOL.md) |
| **Python 3.11 Detected** | → REVERT (incompatible environment) |
| **zstandard Import Fails** | → PRE-EXISTING (install optional deps or skip tests) |
| **20+ Test Errors** | → Check if 10+ are NEW; if yes → investigate reversion |
| **LFS Not Working** | → External issue (secrets/config); escalate to @mbaetiong |
| **Unsure If Error Is Pre-Existing** | → Compare against .codex/PRE_MERGE_TEST_COLLECTION_STATUS.json |

---

## ✅ Sign-Off Template (For Next Session)

When validation completes, update AGENT_ACCOUNTABILITY_REPORT.md with:

```markdown
## SESSION SUMMARY — 2026-06-26T[TIME]Z [POST-MERGE SESSION VALIDATION]

**Session**: copilot-post-merge-validation-5084 | **Date**: 2026-06-26

Post-merge validation of PR #5084 (Campaign Groundwork) completed successfully.

**Validation Results**:
- Gate 1 (YAML Syntax): ✅ PASS
- Gate 2 (Block Scalar): ✅ PASS
- Gate 3 (Env Vars): ✅ PASS
- Gate 4 (LFS Policy): ✅ PASS
- Gate 5 (Python Environment): ✅ PASS
- Gate 6 (Test Collection): ✅ PASS (20 pre-existing errors documented)

**Post-Merge Stability**: ✅ CONFIRMED

**Next Phase**: [Describe next work phase or campaign objectives]

**Status**: ✅ READY TO PROCEED
```

---

**Last Updated**: 2026-06-25T22:33Z  
**Entry Point Ready**: ✅ YES — Execute validation gates immediately upon merge
