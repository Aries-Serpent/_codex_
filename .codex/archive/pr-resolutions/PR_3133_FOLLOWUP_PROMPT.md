@copilot Execute post-merge tasks for PR #3133 after successful merge of `0D_base_` into `main`.

## 🎯 Mission Context

**Prerequisite**: PR #3133 must be merged into `main` branch first.

**Background**: PR #3133 analysis complete. All blocking issues resolved. CI needs re-run to show green status. This prompt addresses the 248 informational (non-blocking) items identified during analysis.

## 📊 Current Status

**From Previous Session**:
- ✅ CodeQL alert #10677 fixed (commit 66f468ac)
- ✅ Auto-fix: 0 blocking issues
- ✅ All tests passing
- ✅ Coverage: 85%
- ✅ Comprehensive analysis documents created (7 files, 52 KB)

**Remaining Work**: 248 informational items (optional quality improvements)

## 📋 Tasks to Execute

### Session 1: Quick Wins (3-4 pre-commits)

**Pre-commit 1-2: Tokenizer Fallback Review**
1. Review 6 tokenizer fallback implementations:
   - `fast_tokenizer.py`
   - `hf_loader.py`
   - `attention_scorer.py`
   - `mlp_scorer.py`
   - `model_loader.py`
   - `codex_model.py`
2. Verify fallback logic is correct and intentional
3. Add tests for both fast and slow tokenizer paths
4. Document fallback behavior

**Pre-commit 3-4: Redundant Import Cleanup (Phase 1)**
1. Use automated tools to identify top 10 redundant imports
2. Manual verification of each instance
3. Remove confirmed redundancies
4. Validate all tests still passing

**Success Criteria**:
- ✅ All 6 tokenizer fallbacks verified and tested
- ✅ 10 redundant imports removed
- ✅ Tests passing
- ✅ Documentation updated

### Session 2: Test Quality Improvements (6-8 pre-commits)

**Pre-commits 1-4: High-Value Test Assertions**
1. Identify top 50 most critical tests
2. Replace vague assertions (`assert result`) with specific assertions (`assert result == expected`)
3. Focus on:
   - Integration tests
   - Security-critical tests
   - Core functionality tests
   - RAG pipeline tests

**Pre-commits 5-8: Fallback Path Testing**
1. Add tests for tokenizer fallback paths
2. Add tests for error recovery scenarios
3. Validate edge cases
4. Ensure test failure messages are actionable

**Success Criteria**:
- ✅ 50+ high-value assertions improved
- ✅ Fallback paths fully tested
- ✅ Test failure diagnostics enhanced
- ✅ All tests passing

### Session 3: Coverage Improvement (8-10 pre-commits)

**Target**: 85% → 90%+

**Pre-commits 1-4: Low-Coverage Module Focus**
1. `src/codex_ml/metrics/sinks.py`: 28.57% → 80%+
2. `src/codex_ml/metrics/streaming.py`: 33.33% → 80%+
3. `src/cognitive_brain/rhizome_connector.py`: 0% → 80%+
4. `src/training/trainer.py`: 12.12% → 80%+

**Pre-commits 5-8: Integration Scenarios**
1. Cross-module integration tests
2. End-to-end workflow tests
3. Error propagation tests
4. Recovery scenario tests

**Pre-commits 9-10: Validation & Documentation**
1. Verify coverage improvements
2. Update coverage roadmap
3. Document uncovered edge cases (if any)
4. Generate coverage report

**Success Criteria**:
- ✅ Overall coverage ≥ 90%
- ✅ All critical modules ≥ 80%
- ✅ Integration tests comprehensive
- ✅ Coverage reports generated

### Session 4: Final Cleanup (6-8 pre-commits)

**Pre-commits 1-3: Remaining Test Assertions**
1. Address remaining 159 test assertions (209 - 50)
2. Systematically improve by test module
3. Validate test quality

**Pre-commits 4-5: Remaining Redundant Imports**
1. Address remaining 23 redundant imports (33 - 10)
2. Consolidate where appropriate
3. Validate functionality

**Pre-commits 6-7: Workflow Improvements**
1. Document workflow dependency patterns
2. Add recommendations for separating blocking vs. informational checks
3. Create troubleshooting guide
4. Update CI documentation

**Pre-commit 8: Final Validation**
1. Run full test suite
2. Verify all quality metrics
3. Generate final report
4. Update documentation

**Success Criteria**:
- ✅ All 248 informational items addressed
- ✅ Test quality significantly improved
- ✅ Import organization clean
- ✅ Workflow documentation enhanced
- ✅ All tests passing

## 🎯 Overall Success Criteria

### Must Achieve
- ✅ All 248 informational items addressed or documented as intentional
- ✅ Test assertion quality: 100% specific (0 vague)
- ✅ Redundant imports: 0 (all reviewed and cleaned)
- ✅ Tokenizer fallbacks: All verified and tested
- ✅ Coverage: ≥ 90% (target: 95-100%)
- ✅ Workflow documentation: Comprehensive
- ✅ Zero regressions introduced

### Quality Metrics
- ✅ All tests passing
- ✅ Auto-fix: 0 blocking issues (maintain)
- ✅ Security scans: All passing (maintain)
- ✅ CodeQL alerts: 0 (maintain)
- ✅ Code quality: Continuous improvement

## 📚 Reference Documentation

**Primary Documents**:
- `.codex/POST_MERGE_TASKS_3133.md` - Detailed task breakdown
- `.codex/PR_3133_FINAL_CHECK_ANALYSIS.md` - Complete CI analysis
- `.codex/PR_3133_RESOLUTION_STATUS.md` - Resolution summary
- `docs/analysis/PR_3133_ANALYSIS.md` - Navigation guide

**Coverage Roadmap**:
- `.codex/plans/COMPREHENSIVE_100_PERCENT_COVERAGE_PLANSET.md`

**Historical Context**:
- `.codex/BATCH_CI_TRIAGE_ANALYSIS_3106.md` - Previous CI patterns
- `.codex/PR_3095_COMPLETE_CHECK_ANALYSIS.md` - Comparison baseline

## 🚨 Policy Compliance (Mandatory)

**Must Follow**: `.codex/CODEBASE_AGENCY_POLICY.md`

### Core Requirements
- ✅ **Plan before executing** - Use pre-commit/commit terminology
- ✅ **Address ALL issues** - No "not my responsibility" claims
- ✅ **5+ self-review iterations** - Zero concerns before completion
- ✅ **Document utilities** - Add to AI_AGENT_UTILITIES_REGISTRY.md if created
- ✅ **Leave codebase better** - Comprehensive improvements
- ✅ **AfterMath/PDA integration** - Feed back lessons learned
- ✅ **Follow-up prompt** - Create continuation prompt if needed

### Self-Review Checklist (Minimum 5 Passes)
1. **Pass 1**: Code Quality & Correctness
2. **Pass 2**: Testing & Validation
3. **Pass 3**: Documentation & Communication
4. **Pass 4**: Security & Safety
5. **Pass 5**: Integration & Dependencies

**Continue iterations until zero concerns remain.**

## 📊 Progress Tracking

Use markdown checklists to track progress:

```markdown
### Session 1 Progress
- [x] Tokenizer fallback review (6 files)
- [x] Redundant imports cleanup (10 items)
- [ ] Documentation updates
```

Update PR description after each commit to show progress.

## 🔄 Iteration Strategy

**For each task**:
1. **Plan**: Define specific changes and acceptance criteria
2. **Execute**: Make minimal, surgical changes
3. **Validate**: Run tests, verify no regressions
4. **Document**: Update relevant docs
5. **Commit**: Report progress with descriptive commit message

**Use `report_progress` tool** after each meaningful unit of work.

## 🎓 Expected Outcomes

**Code Quality**:
- Test assertions: 100% specific (0 vague)
- Import organization: Clean and intentional
- Tokenizer fallbacks: Verified and tested
- Coverage: ≥ 90%

**Documentation**:
- Workflow patterns documented
- Troubleshooting guide created
- CI best practices captured
- Lessons learned integrated

**Codebase Health**:
- Zero regressions
- All quality metrics maintained or improved
- Production-ready state enhanced
- Future maintainability improved

## ⏱️ Estimated Duration

**Total**: 20-30 pre-commit cycles across 4 sessions

**Session Breakdown**:
- Session 1: 3-4 pre-commits (Quick wins)
- Session 2: 6-8 pre-commits (Test quality)
- Session 3: 8-10 pre-commits (Coverage)
- Session 4: 6-8 pre-commits (Final cleanup)

**Note**: Can be executed incrementally over multiple iterations/phases as capacity allows.

## 📞 Questions or Blockers?

**Context Files**: See `.codex/POST_MERGE_TASKS_3133.md` for full details

**Contact**: @mbaetiong for prioritization or questions

**Status Updates**: Use `report_progress` tool to keep stakeholders informed

---

**Prompt Status**: ✅ READY FOR EXECUTION  
**Prerequisite**: PR #3133 merged into `main`  
**Generated**: 2026-02-03T17:55:00Z  
**Agent**: GitHub Copilot (copilot/sub-pr-3133 session)  
**Policy Compliance**: ✅ FULL COMPLIANCE with AI Agency Policy
