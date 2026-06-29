# Phase 5 Execution Plan — Master Campaign Document

**Date:** 2026-06-25T23:56:00Z  
**Status:** ✅ **KICKOFF ACTIVE**  
**Authority:** Phase 5 Execution Mandate  
**Campaign Duration:** 2026-06-26 through 2026-07-23 (4 weeks)

---

## Executive Summary

Phase 5 launches three parallel work streams to achieve coverage (+1.5pp), CI automation (+2.5pp), and documentation maintenance objectives. All work delegated to specialized custom agents with aggressive parallelization.

**Campaign Targets:**
- Coverage: 23.0% → 24.5%+ (CLI modules quick wins)
- CI Auto-Fix: 37.5% → 40%+ (RP-031/032/033 patterns)
- Documentation: Maintain 95%+ link validity (scheduled maintenance)

**Total Effort:** ~71 hours across 3 streams  
**Execution Model:** Parallel delegation to 3 custom agents  
**Progress Tracking:** Weekly checkpoints in `.codex/PHASE_5_*.md`

---

## 🎯 Work Stream 1: Coverage Quick Wins (CLI Modules, +1.5pp)

**Agent:** `unified-coverage-agent`  
**Priority Focus:** CLI module zero-coverage gap-fill tests  
**Target:** 23.0% → 24.5% | **Effort:** 40 hours | **Timeline:** 2026-06-26 to 2026-07-16

### Top 6 Quick-Win Modules (Phase 4 Identified)

| # | Module | Lines | Category | Est. Hours | Coverage Goal |
|---|--------|-------|----------|------------|---------------|
| 1 | `src/cli.py` | 191 | CLI | 2.5h | >60% |
| 2 | `src/codex_ml/cli/repo_map.py` | 190 | ML CLI | 2.5h | >60% |
| 3 | `src/codex_ml/cli/hydra_audit.py` | 259 | Hydra | 3.5h | >50% |
| 4 | `src/codex_ml/cli/feature_store.py` | 165 | Feature Store | 2.0h | >55% |
| 5 | `src/codex_cli/app.py` | 156 | CLI App | 2.0h | >60% |
| 6 | `src/codex/utils/hash_table.py` | 233 | Utilities | 3.5h | >50% |
| **SUBTOTAL** | | **1,194** | | **16h** | **~1.0pp gain** |

### Additional 4-6 Modules (Weeks 2-3)

- `src/codex_ml/plugins/plugin_sandbox.py` (208 lines, 3h)
- `src/codex_ml/integrations/har_integration.py` (230 lines, 3h)
- `src/codex/campaigns/orchestrator.py` (178 lines, 2.5h)
- `src/codex_ml/cli/repo_map.py` edge cases (2.5h)
- Other high-value zero-coverage modules (6h)

**Expected Total Gain:** ~1.5pp (24,572 → 26,100+ covered lines)

### Success Criteria
- ✅ All 6+ target modules >50% coverage
- ✅ Coverage increases to 24.5%+
- ✅ Zero new zero-coverage modules in CLI category
- ✅ Test fixtures documented and reusable
- ✅ Pytest reports generated (.codex/PHASE_5_COVERAGE_RESULTS.json)

---

## 🔧 Work Stream 2: CI Pattern Implementation (RP-031/032/033, +2.5pp)

**Agent:** `ci-auto-healer-agent`  
**Priority Focus:** Implement 3 new CI auto-fix patterns  
**Target:** 37.5% → 40%+ auto-fix coverage | **Effort:** 25 hours | **Timeline:** 2026-06-26 to 2026-07-16

### 3 New Patterns for Implementation

#### RP-031: Assert Messages Without Context
- **Occurrences:** 216 across test suite
- **Auto-Fix Rate:** 75% automatically fixable
- **Effort:** 8 hours
- **Coverage Gain:** +0.5pp
- **Strategy:** 
  1. Pattern detection: `assert <condition>` without explanation
  2. Auto-fix: Add descriptive message from context
  3. Manual review: 54 edge cases requiring developer input

#### RP-032: Async Tests Without Timeout ⭐
- **Occurrences:** 72 across test suite
- **Auto-Fix Rate:** 90% automatically fixable
- **Effort:** 6 hours
- **Coverage Gain:** +0.2pp
- **Strategy:**
  1. Pattern detection: Async test without pytest timeout fixture
  2. Auto-fix: Inject `@pytest.mark.timeout(30)` decorator
  3. Manual review: 7 cases requiring custom timeout calculation

#### RP-033: Mock Object Cleanup Missing ⭐
- **Occurrences:** 293 across test suite
- **Auto-Fix Rate:** 65% automatically fixable
- **Effort:** 11 hours
- **Coverage Gain:** +0.66pp
- **Strategy:**
  1. Pattern detection: Mock objects created but not cleaned up
  2. Auto-fix: Add `.reset_mock()` / `cleanup()` calls in teardown
  3. Manual review: 103 cases requiring custom cleanup logic

### Implementation Timeline

**Week 1 (Jun 26 - Jul 02):**
- RP-031 design and initial implementation (8h)
- Add pattern to `scripts/ci/auto_fix_common_issues.py`
- Create test cases and validation

**Week 2 (Jul 03 - Jul 09):**
- RP-032 implementation and testing (6h)
- Verify pytest fixture injection works across async test types
- Integration testing

**Week 3 (Jul 10 - Jul 16):**
- RP-033 implementation and hardening (11h)
- Complex mock cleanup patterns handling
- Final validation and documentation

### Success Criteria
- ✅ All 3 patterns implemented in auto_fix_common_issues.py
- ✅ Auto-fix coverage reaches 38.9%+ (from 37.5%)
- ✅ 581 total occurrences handled (77% auto-fixed = ~447 automatic fixes)
- ✅ Test cases for each pattern (100% pass rate)
- ✅ Documentation + code examples for each pattern
- ✅ CI pipeline integration verified

---

## 📚 Work Stream 3: Documentation Maintenance (Scheduled Tasks, Ongoing)

**Agent:** `unified-doc-agent`  
**Priority Focus:** Link validation, broken path fixes, archive audit  
**Target:** Maintain 95%+ link validity | **Effort:** ~5-10 hours (ongoing) | **Timeline:** Ongoing throughout Phase 5

### Priority Issues (From Phase 4 Audit)

**HIGH (1-2 hours) — Week 1:**
- Fix 388 broken script paths (script location consolidation)
  - Locate script references in documentation
  - Verify actual paths in repository
  - Update all broken references
- Verify all .codex/ paths reference correct locations

**MEDIUM (1 hour) — Week 2:**
- Document 6 template archive references (intentional, existing)
- Establish archival policy documentation for Phase 6+
- Create template for future archived docs

**LOW (Q3 2026 follow-up):**
- Convert 24 absolute path references to relative paths
- Link resolution for new Phase 6 documentation

### Quarterly Maintenance Schedule

**Q2 2026 (June-Jul):** 
- Critical path fixes (H-1)
- Archive cleanup and policy documentation
- GitHub Pages readiness verification

**Q3 2026 (Aug-Sep):**
- Comprehensive link audit
- Broken-link reduction (target: <3%)
- Relative path migration

**Q4 2026 (Oct-Dec):**
- Full refresh cycle
- Pages sync and optimization
- Archival cleanup

### Success Criteria
- ✅ Maintain 95%+ link validity (current: 95.5%)
- ✅ Fix 388 script path references (H-1)
- ✅ Archive policy documented
- ✅ GitHub Pages deployment ready
- ✅ Zero critical path broken links

---

## 📊 Phase 5 Execution Timeline

### Week 1: Kickoff & Initial Implementation (Jun 26 - Jul 02)

| Task | Agent | Duration | Deliverables |
|------|-------|----------|--------------|
| CLI modules 1-4 coverage tests | unified-coverage-agent | 10h | 4 test suites, .codex/PHASE_5_WEEK1_COVERAGE.md |
| RP-031 design & initial impl | ci-auto-healer-agent | 8h | Pattern detection + 50% auto-fix impl |
| Path fixes audit & validation | unified-doc-agent | 2h | .codex/PHASE_5_SCRIPT_PATH_AUDIT.md |
| **Daily checkpoint** | — | — | .codex/PHASE_5_WEEK1_CHECKPOINT.md |

### Week 2: Consolidation & Extension (Jul 03 - Jul 09)

| Task | Agent | Duration | Deliverables |
|------|-------|----------|--------------|
| CLI modules 5-8 coverage tests | unified-coverage-agent | 10h | 4 more test suites, coverage report |
| RP-032 implementation & testing | ci-auto-healer-agent | 6h | Pattern detection + auto-fix + tests |
| Archive review & policy doc | unified-doc-agent | 1h | .codex/ARCHIVE_POLICY.md |
| **Weekly checkpoint** | — | — | .codex/PHASE_5_WEEK2_CHECKPOINT.md |

### Week 3: Validation & Hardening (Jul 10 - Jul 16)

| Task | Agent | Duration | Deliverables |
|------|-------|----------|--------------|
| Coverage validation & refinement | unified-coverage-agent | 3h | .codex/PHASE_5_COVERAGE_VALIDATION.md |
| RP-033 implementation & integration | ci-auto-healer-agent | 11h | Full pattern impl + pipeline integration |
| Documentation maintenance ongoing | unified-doc-agent | 1h | Maintenance summary |
| **Weekly checkpoint** | — | — | .codex/PHASE_5_WEEK3_CHECKPOINT.md |

### Week 4: Phase Completion (Jul 17 - Jul 23)

| Task | Agent | Duration | Deliverables |
|------|-------|----------|--------------|
| Coverage review & final metrics | unified-coverage-agent | 2h | Final coverage report |
| Pattern testing & hardening | ci-auto-healer-agent | — | Final validation suite |
| Quarterly summary & next roadmap | unified-doc-agent | 1h | Q3 2026 roadmap |
| **Phase completion report** | — | — | .codex/PHASE_5_COMPLETION_REPORT.md |

---

## 🚀 Agent Delegation Strategy

### Agent Delegation Model

All three work streams delegated to specialized custom agents with clear briefs and success criteria:

1. **unified-coverage-agent**: Gap-fill tests for CLI modules (1,194+ lines → target >1pp coverage gain)
2. **ci-auto-healer-agent**: Implement 3 new CI auto-fix patterns (25h effort → 2.5pp CI coverage gain)
3. **unified-doc-agent**: Link validation + maintenance (ongoing → 95%+ link validity maintained)

### Parallel Execution

- **Start Date:** 2026-06-26
- **Synchronization:** Weekly checkpoints on Mondays (if running continuously)
- **Blocker Escalation:** Direct to @mbaetiong if critical issues found
- **Progress Tracking:** All artifacts in `.codex/PHASE_5_*.md` (repository-tracked, NOT /tmp/)

---

## 📋 Success Criteria — All Work Streams

### Coverage Work Stream (unified-coverage-agent)
- ✅ All 6+ CLI target modules have test coverage >50%
- ✅ Overall coverage increases from 23.0% to 24.5%+
- ✅ Zero new zero-coverage modules introduced
- ✅ Test fixtures documented and reusable for future modules
- ✅ Pytest coverage reports generated and committed

### CI Patterns Work Stream (ci-auto-healer-agent)
- ✅ RP-031, RP-032, RP-033 all implemented and tested
- ✅ Auto-fix coverage reaches 38.9%+ (from 37.5%)
- ✅ All 581 pattern occurrences handled (77% auto-fixed)
- ✅ All 3 patterns integrated into CI pipeline
- ✅ Documentation + code examples for each pattern

### Documentation Work Stream (unified-doc-agent)
- ✅ Maintain 95%+ link validity (current: 95.5%)
- ✅ Fix 388 script path references (H-1 priority)
- ✅ Archive policy documented for Phase 6+
- ✅ GitHub Pages deployment ready
- ✅ Zero critical path broken links

### Overall Campaign
- ✅ No critical blockers
- ✅ All agents report clean results
- ✅ Phase 5 completion report created
- ✅ Ready for Phase 6 transition
- ✅ **REQ-4/REQ-5 compliance:** AGENT_ACCOUNTABILITY_REPORT.md and CHANGELOG.md updated

---

## 📁 Artifact Storage Policy

**ALL Phase 5 working files and checkpoints stored in `.codex/` directory:**
- `.codex/PHASE_5_MASTER_PLAN.md` — This document
- `.codex/PHASE_5_COVERAGE_AGENT_BRIEF.md` — Coverage agent instructions
- `.codex/PHASE_5_CI_AGENT_BRIEF.md` — CI patterns agent instructions
- `.codex/PHASE_5_DOC_AGENT_BRIEF.md` — Documentation agent instructions
- `.codex/PHASE_5_WEEK1_CHECKPOINT.md` — Week 1 progress
- `.codex/PHASE_5_WEEK2_CHECKPOINT.md` — Week 2 progress
- `.codex/PHASE_5_WEEK3_CHECKPOINT.md` — Week 3 progress
- `.codex/PHASE_5_COMPLETION_REPORT.md` — Final phase summary

**⚠️ CRITICAL:** All files kept in `.codex/` (repository-tracked), **NEVER in `/tmp/`**

---

## 🎯 Next Immediate Actions

1. ✅ Create PHASE_5_MASTER_PLAN.md (this document)
2. ⏳ Create 3 agent briefs (following)
3. ⏳ Launch 3 parallel agent campaigns (via task tool)
4. ⏳ Establish weekly checkpoint schedule
5. ⏳ Monitor progress and escalate blockers

---

## 📞 Authority & Escalation

**Campaign Authority:** @mbaetiong (Phase 5 Execution Mandate)  
**Autonomy Level:** Full (D - All 3 agents authorized for independent execution)  
**Escalation:** Any critical blockers → @mbaetiong  
**Status:** ✅ **READY FOR AGENT DELEGATION**

---

**Document Created:** 2026-06-25T23:56:00Z  
**Status:** PHASE 5 KICKOFF — AGENT BRIEFS PENDING
