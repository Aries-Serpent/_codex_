# 🎯 PR Follow-Up Tasks — #3388 (Pre-Merge Validation Fix)

**PR**: #3388 — Fix failing CI workflow Pre-Merge Validation run #1212
**Branch**: `copilot/fix-pre-merge-validation-workflow`
**Session**: S78
**Date**: 2026-02-27
**Status**: ✅ CORE FIX COMPLETE — Follow-up items documented

---

## 📋 SESSION S78 SUMMARY

### Completed Work
- [x] Root cause analysis: Pattern 8 ("CodeQL Alerts") misclassified as auto-fixable in `auto_fix_common_issues.py`
- [x] Fix: Moved "CodeQL Alerts" from `auto_fixable_patterns` to `manual_review_patterns`
- [x] Enhancement: Workflow updated to show specific file:line issues when failing
- [x] Cognitive brain status created: `COGNITIVE_BRAIN_STATUS_S78.md`
- [x] CI agent updated with pre-merge validation pattern knowledge
- [x] Change log entry added
- [x] 5-pass self-review completed
- [x] Code review + CodeQL scan passed

### Root Cause Documented
Pattern 8 ("CodeQL Alerts") detected F401+F841 but had no fix logic.
With it labeled "auto-fixable", `has_auto_fixable_issues()` returned True
for F841-only issues (not actually auto-fixable), causing false CI failures.

**Fix location**: `scripts/ci/auto_fix_common_issues.py` lines 44-60

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: HOTFIX Items from post-PR3375 🔴 CRITICAL

The following items remain in `.github/copilot-prompts/active/HOTFIX-post-PR3375-infra-failures.md`:

**Sub-task A**: Art_RAG CPU guards (`tests/rag/`)
- Fix: Add `@pytest.mark.skipif(not torch.cuda.is_available(), ...)` guards
- Or: CPU-only mock for SentenceTransformer in `tests/rag/conftest.py`

**Sub-task B**: cognitive_brain API mismatches (`tests/cognitive_brain/test_integration.py`)
- `ImportError: TestExecutionMetrics` from uncertainty.py
- `AttributeError: assess_entangled` on EntangledComplianceSecurityAssessor  
- `AttributeError: save_metric` on QuantumMetricRepository (now FIXED in main)
- `sqlite3.OperationalError: metric_name column missing` (now FIXED in main)

**Sub-task C**: Training assertion
- `test_training_mode_toggle`: `assert not True` (model starts in train mode)
- Fix: Change assertion to `assert model.training` (nn.Module default is .train())

**Sub-task D**: peft/evaluate_cli failures
- `resume_path` KeyError, `metric_key` KeyError, `epochs>=1` ValueError

**Sub-task E**: CodeQL 5 configurations not found

**Validation**:
```bash
python -m pytest tests/cognitive_brain/test_integration.py -v --timeout=60
python -m pytest tests/training/test_train_loop_coverage.py::TestBasicTrainingIteration::test_training_mode_toggle -v
CUDA_VISIBLE_DEVICES="" python -m pytest tests/rag/ -v --timeout=120
```

### Priority 2: Pre-Merge Validation on this PR 🟡 HIGH
- [ ] Convert PR #3388 from draft to ready-for-review
- [ ] Verify new CI run passes after script + workflow changes
- [ ] Check run result via `github-mcp-server-actions_list`

### Priority 3: DRQ Entry 🟢 MEDIUM
- [ ] Add DRQ entry for "CodeQL auto-fixable pattern classification" recurring issue
- [ ] File: `docs/tech_debt/research_queue/questions_for_research.md`
- [ ] Pattern has appeared in 2+ sessions → qualifies for DRQ

---

## ✅ EXECUTION CHECKLIST

- [x] Pattern 8 classification bug fixed in auto_fix_common_issues.py
- [x] Workflow improved with JSON output for better error messages
- [x] Cognitive brain status S78 created
- [x] Change log updated
- [x] Follow-up prompt created (this file)
- [ ] PR #3388 moved to ready-for-review
- [ ] New CI run triggered and verified green
- [ ] HOTFIX items addressed (see sub-tasks above)
- [ ] DRQ entry added

---

## 🔍 MANDATORY SELF-REVIEW PROTOCOL

### Pass 1: Code Quality ✅
- auto_fix_common_issues.py: Pattern 8 correctly moved, comment added
- Workflow: JSON output flag added, error step shows specific issues
- No linting warnings introduced

### Pass 2: Testing ✅
- `python scripts/ci/auto_fix_common_issues.py --check-only` → exit 0
- `python -m ruff check --select F401,F841 tests/ src/` → "All checks passed!"

### Pass 3: Documentation ✅
- Cognitive brain status S78 created
- Change log updated with S78 entry
- Follow-up prompt created (this file)

### Pass 4: Security ✅
- No secrets, credentials, or security-sensitive changes
- Workflow JSON output uses stdlib json only

### Pass 5: Integration ✅
- Pattern 1 (F401 auto-fix) unaffected — still blocks correctly
- Pattern 4 (Coverage Thresholds) unaffected
- Pattern 2 (F841 informational) behavior now consistent with Pattern 8

---

## 🤖 COPILOT AGENT INSTRUCTIONS

**When activating for continuation of this PR:**

1. Load this prompt from `.github/copilot-prompts/active/PR-3388-followup.md`
2. Check current CI status: `github-mcp-server-actions_list` for branch `copilot/fix-pre-merge-validation-workflow`
3. If CI passes → convert PR to ready-for-review
4. If CI fails → diagnose and fix
5. Then address HOTFIX Priority 1 items (separate PR or same PR if low risk)
6. Update this file with ✅ for completed items
7. Post status comment on PR #3388

**Activation command**:
```
@copilot Continue work on PR #3388. Load .github/copilot-prompts/active/PR-3388-followup.md.
Check CI status, address Priority 1 HOTFIX items (Art_RAG CPU guards, cognitive_brain API),
and ensure all checks pass. Follow .codex/CODEBASE_AGENCY_POLICY.md.
```

---

**Generated**: 2026-02-27
**Template Version**: 2.1.0
**Session**: S78
**Source PR**: #3388
