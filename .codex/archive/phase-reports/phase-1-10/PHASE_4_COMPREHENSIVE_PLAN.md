# Phase 4: Continuous Improvement Campaign Plan
**Date:** 2026-06-25T23:08:10Z
**Campaign:** Post-Merge Phase 4 (Coverage, CI, Docs)
**Authority:** CAD-Mandate Phase 4 (User: @mbaetiong)
**Status:** 🚀 KICKOFF

---

## Executive Summary

Phase 4 executes three concurrent work streams focused on continuous improvement of code quality, CI/CD automation, and documentation freshness post-merge. This phase builds on Phase 1-3 validation completion and establishes foundational improvements for Phase 5-6 ongoing work.

**Campaign Objective:** Improve from validated post-merge baseline to 22%+ coverage, 40%+ CI auto-fix, and 100% doc freshness in 60-90 minutes.

---

## Phase 4 Work Streams

### Stream 1: Continuous Coverage Improvement (35% effort)

**Goal:** Increase test coverage from 21.5% to 22%+ while identifying zero-coverage critical modules for future gap-fill work.

**Current State:**
- Coverage: 21.5% (validated in post-merge campaign)
- Improvement: +10.8pp from pre-merge (BASELINE_10.7%)
- Target: 22%+ for Phase 4 (modest +0.5pp increase)

**Tasks:**
1. **Coverage Baseline Report**
   - Run: `pytest --cov=src --cov-report=term-missing --cov-report=json --cov-report=html`
   - Save to: `.codex/PHASE_4_COVERAGE_REPORT.txt`
   - Output: Full coverage summary, per-module breakdown, HTML report

2. **Zero-Coverage Module Analysis**
   - Identify top 5 modules with <5% coverage
   - Focus areas: src/codex/utils/, src/codex_ml/, src/tokenization/
   - For each: estimate criticality (high/medium/low), risk, test effort

3. **Coverage Roadmap Creation**
   - Path 1: 21.5% → 22% (quick wins, 1-2 hours)
   - Path 2: 22% → 25% (medium modules, 4-6 hours)
   - Path 3: 25% → 30% (long-term vision, 8-12 hours)
   - Document effort, risks, dependencies for each

4. **Gap-Fill Recommendations**
   - Identify top 10 uncovered code paths
   - Suggest test cases needed for coverage
   - Estimate effort per path
   - Prioritize by impact (critical bugs likely, easy test wins, etc.)

5. **Deliverable:** `.codex/COVERAGE_GAP_REPORT.md` (updated with Phase 4 data)

**Success Criteria:**
- ✅ Coverage report generated (HTML + JSON + text)
- ✅ Top 5 zero-coverage modules identified
- ✅ Roadmap created (21.5% → 25%+)
- ✅ 10 gap-fill recommendations documented
- ✅ COVERAGE_GAP_REPORT.md updated

---

### Stream 2: CI Automation Enhancement (40% effort)

**Goal:** Increase CI auto-fix coverage from 37.5% to 40%+ by identifying and assessing new failure patterns.

**Current State:**
- Auto-fix coverage: 37.5%
- CI failure rate: 6.5% (healthy)
- Patterns implemented: RP-001 (unused imports), RP-002 (unused vars detect), RP-003 (YAML), RP-004+

**Tasks:**
1. **Pattern Audit**
   - Run: `python scripts/ci/auto_fix_common_issues.py --check-only --json-output .codex/PHASE_4_CI_AUDIT.json`
   - Review current coverage: which patterns auto-fixable vs. detect-only
   - Assess fixability of detect-only patterns

2. **New Pattern Discovery**
   - Parse recent CI failures (last 30 workflow runs)
   - Categorize failures not covered by RP-001 through RP-004
   - For each new pattern: estimate recurrence, severity, fix effort
   - Recommend top 2-3 patterns with ROI analysis

3. **Pattern-to-Fix Validation**
   - Ensure all detectable patterns have fix templates
   - Test fix logic on sample failures
   - Document edge cases and limitations

4. **Enhancement Roadmap**
   - Current: 37.5% → Phase 4 Target: 40%+ (new patterns)
   - Future: 40% → 50%+ (enhancement roadmap)
   - Document phased approach, dependencies, risks

5. **Deliverable:** `.codex/PHASE_4_CI_PATTERN_ENHANCEMENT.md` (new)

**Success Criteria:**
- ✅ Pattern audit complete (RP-001 through RP-004+ analyzed)
- ✅ 2-3 new patterns identified with ROI estimates
- ✅ Pattern-to-fix mappings validated
- ✅ Enhancement roadmap created (37.5% → 50%+)
- ✅ PHASE_4_CI_PATTERN_ENHANCEMENT.md created

---

### Stream 3: Documentation Alignment (25% effort)

**Goal:** Ensure 100% documentation freshness, compliance with REQ-4/REQ-5, and GitHub Pages sync.

**Current State:**
- Documentation files: ~138 verified post-merge
- GitHub Pages: Configured
- Compliance status: REQ-4/REQ-5 gates active on merge

**Tasks:**
1. **Compliance Audit (REQ-4 + REQ-5)**
   - Run: `python scripts/ci/session_wrapup_autofix.py --check --pr-number 5084`
   - Verify: AGENT_ACCOUNTABILITY_REPORT.md in last commit
   - Verify: CHANGELOG.md in last commit
   - Document pass/fail for each requirement

2. **Link Validation**
   - Scan docs/ and .codex/ for all internal/external links
   - Test GitHub URLs (issues, PRs, releases)
   - Test internal file references (do files exist?)
   - Test anchor links (do headers exist?)
   - Generate list of broken links with fix suggestions

3. **GitHub Pages Freshness**
   - Compare published site vs. main branch docs
   - Check: API reference accuracy, getting started guide, architecture docs
   - Identify out-of-date content (>30 days without refresh)
   - Verify navigation structure, search functionality

4. **Documentation Maintenance Plan**
   - Identify docs needing refresh (by age, importance, accuracy)
   - Categorize: critical (immediate), high (1 week), medium (1 month)
   - Estimate effort for each category
   - Create maintenance schedule/roadmap

5. **Deliverables:**
   - `.codex/PHASE_4_LINK_VALIDATION_REPORT.md` (new)
   - `.codex/PHASE_4_DOC_MAINTENANCE_ROADMAP.md` (new)
   - AGENT_ACCOUNTABILITY_REPORT.md (Phase 4 status update)
   - CHANGELOG.md (Phase 4 entry with compliance note)

**Success Criteria:**
- ✅ REQ-4/REQ-5 compliance verified (gates passing)
- ✅ Link validation complete (all critical links working)
- ✅ GitHub Pages sync status documented
- ✅ Doc maintenance roadmap created (priorities + effort estimates)
- ✅ Compliance gates will pass before merge

---

## Agent Delegation Strategy

**Authority:** CAD-Mandate Phase 4 (User preference: aggressive custom agent delegation)

| Stream | Agent | Type | Mode | Expected Duration |
|--------|-------|------|------|-------------------|
| Coverage | unified-coverage-agent | Analysis + Roadmap | Background | 15-20 min |
| CI | ci-auto-healer-agent | Audit + Enhancement | Background | 10-15 min |
| Docs | unified-doc-agent | Audit + Maintenance | Background | 12-18 min |

**Coordination:**
- All three streams run in parallel (independent)
- Results consolidated in Phase 4 Summary (this document updated)
- No inter-stream blocking (can proceed independently)

---

## Implementation Timeline

### Phase 4A: Agent Delegations (0-20 min)
- [🔄] Launch 3 agents in parallel
- [⏳] Agents execute analysis & recommendations
- [🕐] Estimated: 15-20 min

### Phase 4B: Results Integration (20-40 min)
- [⏳] Receive agent results
- [⏳] Consolidate findings
- [⏳] Assess recommendations for implementation
- [🕐] Estimated: 15-20 min

### Phase 4C: Implementation Planning (40-60 min)
- [⏳] Coverage: Prioritize gap-fill work (Phase 5 candidate)
- [⏳] CI: Assess new patterns for implementation (effort vs. benefit)
- [⏳] Docs: Fix compliance issues (if any), schedule maintenance
- [🕐] Estimated: 15-20 min

### Phase 4D: Documentation & Sign-Off (60-90 min)
- [⏳] Create Phase 4 Campaign Summary
- [⏳] Update AGENT_ACCOUNTABILITY_REPORT.md with Phase 4 completion
- [⏳] Verify compliance gates (REQ-4/REQ-5)
- [⏳] Decide: Phase 5 Ready? Escalate? Continue Phase 4?
- [🕐] Estimated: 10-15 min

**Total Estimated:** 60-90 minutes

---

## Success Criteria

### Must Achieve (100% required)
- ✅ Coverage gap analysis complete with roadmap (21.5% → 22%+)
- ✅ CI pattern enhancement plan created (37.5% → 40%+)
- ✅ Documentation audit complete with compliance verification
- ✅ All three agent delegations complete with clean results
- ✅ COVERAGE_GAP_REPORT.md, PHASE_4_CI_PATTERN_ENHANCEMENT.md created
- ✅ PHASE_4_LINK_VALIDATION_REPORT.md, PHASE_4_DOC_MAINTENANCE_ROADMAP.md created
- ✅ Phase 4 Campaign Summary documented
- ✅ Compliance gates (REQ-4/REQ-5) verified passing

### Should Achieve (high priority)
- ✅ New CI patterns identified with ROI analysis
- ✅ Coverage gap-fill candidates prioritized
- ✅ Doc maintenance roadmap phased (immediate / 1-week / 1-month)
- ✅ GitHub Pages sync issues identified (if any)

### Nice to Have
- 🎁 Draft implementation PR for new CI patterns
- 🎁 Sample test cases for top 3 coverage gaps
- 🎁 Link validator script created for continuous checking

---

## Decision Points

### After Agent Results
**Decision: Proceed to Phase 4B or Escalate?**
- If all agents return clean results → **Proceed to 4B (Integration)**
- If any agent encounters issues → **Review issue, attempt recovery, escalate if needed**

### After Implementation Planning
**Decision: Proceed to Phase 5 or Continue Phase 4?**
- If all streams ready + metrics improved → **Proceed to Phase 5**
- If critical gaps remain → **Continue Phase 4 iterations (with specific focus)**
- If blockers found → **Escalate to @mbaetiong**

---

## References

**Baseline Documentation:**
- `.codex/AGENTIC_REPO_STATE.md` — Auth status, variables
- `.codex/POST_MERGE_SESSION_ENTRY_POINT.md` — Campaign context
- `.codex/CODEBASE_AGENCY_POLICY.md` — Mandatory policies

**Coverage:**
- `.codex/COVERAGE_GAP_REPORT.md` — Existing roadmap (to update)
- `pyproject.toml` — Test configuration, coverage settings

**CI:**
- `scripts/ci/auto_fix_common_issues.py` — Pattern implementation
- `.codex/CI_AUTO_FIX_SYSTEM.md` — CI automation docs
- `.codex/archive/pr-resolutions/PR_3095_RESOLUTION_PATTERNS.md` — Pattern library

**Documentation:**
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` — Compliance tracking
- `CHANGELOG.md` — Change log (to update)
- `GitHub Pages`: https://aries-serpent.github.io/_codex_/

---

## Authority & Compliance

**Authority:** CAD-Mandate Phase 4  
**Autonomy Level:** D (Full Autonomy)  
**Compliance Gates:** REQ-1 through REQ-5 (tracking via AGENT_ACCOUNTABILITY_REPORT.md)  
**Escalation:** Issues requiring human decision → @mbaetiong  

---

**Document Status:** ✅ COMPLETE & ACTIVE  
**Created:** 2026-06-25T23:08:10Z  
**Next Review:** After Agent Delegations Complete  
