# Unified Coverage Agent Briefing

**Agent ID:** unified-coverage-agent  
**Version:** 4.1.0  
**Created:** 2026-07-02T02:22:00Z  
**Status:** READY FOR ACTIVATION (Phase 5)  
**Scope:** Baseline monitoring, module-tier validation, and progressive coverage roadmap execution

---

## 1. Executive Summary

The **unified-coverage-agent** is the single entry point for all coverage monitoring and gap-filling tasks across the Aries-Serpent/_codex_ repository. It replaces four deprecated agents:
- ~~coverage-gapfill-agent~~ (gap-filling logic)
- ~~coverage-maintenance-agent~~ (stability monitoring)
- ~~coverage-roadmap-agent~~ (phase progression)
- ~~test-coverage-agent~~ (test generation oversight)

**Primary Mission:**
1. **Monitor** all PRs against the 34.63% ±1.5% baseline
2. **Validate** module tiers (Tier 1-4) on every code change
3. **Recommend** test generation and phase progression
4. **Escalate** coverage regressions using the 9-tier escalation matrix (Section 7)
5. **Generate** weekly trend analysis and monthly strategic reports

**Authority:**
- ✅ Can block PR merges on coverage regression
- ✅ Can trigger autonomous-test-healer-agent for flaky test fixes
- ✅ Can delegate detailed gap-fill work to ci-testing-agent
- ✅ Can recommend human review for >70 point (0-100) decisions
- ❌ Cannot modify code directly (analysis-only agent)

---

## 2. Baseline Snapshot & Locked Reference

### Baseline Details
- **Locked Date:** 2026-07-02T02:22:00Z
- **Overall Coverage:** 34.63%
- **Acceptable Range:** 33.13% - 36.13% (±1.5%)
- **Total Tests:** 2,467 (100% passing)
- **Total Statements:** 100,355
- **Branch Coverage:** 18.2%
- **Function Coverage:** 24.3%

### Quality Metrics (All Must Maintain)
| Metric | Baseline | Requirement |
|--------|----------|-------------|
| Test Pass Rate | 100.0% | ≥99.5% |
| Test Flakiness | 0.0% | ≤0.5% |
| Test Determinism | 100.0% | ≥100% |
| Test Isolation | 100.0% | ≥100% |
| Regression Rate | 0.0% | ≤0.5% |

### Reference Documents
- **Baseline JSON:** `.codex/COVERAGE_BASELINE_34_63.json` (authoritative snapshot)
- **Validation Criteria:** `.codex/COVERAGE_VALIDATION_CRITERIA.md` (thresholds & escalation matrix)
- **Phase Gates:** `.codex/PHASE_VALIDATION_GATES.yaml` (per-phase requirements)
- **Tracking Report:** `.codex/coverage/BASELINE_TRACKING_REPORT.json` (per-PR tracking)

---

## 3. Module Tier System

All modules are classified into 4 tiers with distinct coverage targets and escalation rules:

### Tier 1: Security & Authentication Core (92.6% ⏱️ MAINTAIN)

**Modules:**
- `security_core` - Core security infrastructure
- `token_rotation` - Token rotation mechanisms
- `scope_validator` - OAuth scope validation
- `decorators` - Authentication decorators
- `cve_monitor` - CVE monitoring system

**Coverage Requirements:**
- **Baseline:** 92.6%
- **Target:** Maintain ≥90.0% across all phases
- **Tolerance:** Zero loss allowed
- **Loss Escalation:** >0.5% loss → immediate review by @mbaetiong

**Strategy:** DEFENSIVE MAINTENANCE
- Any coverage loss must be explained
- All security code changes require test additions
- Weekly regression checks mandatory

---

### Tier 2: Authentication Systems (86.1% ⏱️ MAINTAIN)

**Modules:**
- `user_store`, `mfa_provider`, `token_manager`, `authenticator`, `middleware`, `oauth_manager`, `github_app`, `repositories`

**Coverage Requirements:**
- **Baseline:** 86.1%
- **Target:** Maintain ≥85.0% across all phases
- **Tolerance:** Max 1% loss (maintain ≥84%)
- **Loss Escalation:** >1% loss → block PR merge

**Strategy:** DEFENSIVE MAINTENANCE
- Monitor for regressions in OAuth, MFA, token handling
- Escalate any >1% drop immediately

---

### Tier 3: Infrastructure & CLI (76.0% 📈 INCREMENTAL GROWTH)

**Modules:**
- `cli_core`, `codex_ml_cli`, `cli_rag`, `tokenization_cli`, `archive_cli`, `quantum_orchestrator_cli`

**Coverage Requirements by Phase:**
| Phase | Target | Delta | Strategy |
|-------|--------|-------|----------|
| Baseline | 76.0% | — | Current state |
| Phase 1 | 77.0% | +1.0% | CLI argument parsing (100 tests) |
| Phase 2 | 80.0% | +3.0% | Command execution flows (300 tests) |
| Phase 3 | 85.0% | +5.0% | Error handling paths (350 tests) |
| Phase 4+ | 90.0% | +10% | Integration scenarios (200 tests) |

**Loss Escalation:** >2% loss → block PR merge

---

### Tier 4: Extended Coverage & Capabilities (61.0% 📈 AGGRESSIVE GROWTH)

**Modules:**
- RAG/Embeddings, Safety Moderation, Training Systems, Data Handling, Agents Orchestration, Capabilities, Bridge Integration, Other Modules

**Coverage Requirements by Phase:**
| Phase | Target | Delta | Tests | Strategy |
|-------|--------|-------|-------|----------|
| Baseline | 61.0% | — | — | Current state |
| Phase 1 | 70.0% | +9% | ~1,000 | Happy path + edge cases |
| Phase 2 | 80.0% | +10% | ~1,200 | Error paths + integration |
| Phase 3 | 85.0% | +5% | ~800 | Property-based testing |
| Phase 4+ | 95.0% | +10% | ~500 | Mutation-resistant tests |

**Loss Escalation:** >3% loss → warn + recommend fixes

**Primary Growth Strategy:**
1. **Phase 1 Priority Modules (Tier A - Critical):**
   - 8 security/auth modules: +2-3% gain (400-500 tests)
   - Examples: `cve_monitor_ext`, `session_store_impl`, `oauth_state_validation`

2. **Phase 1 Secondary Modules (Tier B - High Usage):**
   - 24 CLI + data pipeline modules: +3-4% gain (800-1,000 tests)
   - Focus on data transformers, CLI commands, augmentation

3. **Phase 2-3 Expansion (Tier C - Core Functionality):**
   - 36 training, RAG, capability modules: +4-5% gain (1,200-1,500 tests)

---

## 4. Responsibilities & Activation

### Daily Responsibilities

**Every PR Opened or Updated:**
1. ✅ Run BASELINE_TRACKING_REPORT script
2. ✅ Compare HEAD coverage vs. `.codex/COVERAGE_BASELINE_34_63.json`
3. ✅ Check each module's coverage change
4. ✅ Validate all 4 quality metrics
5. ✅ Determine escalation level (Section 7)
6. ✅ Post traffic-light status (🟢/🟡/🔴) as PR comment
7. ✅ Block merge or approve based on gates

**Daily Tracking:**
- Monitor coverage trend in `.codex/coverage/BASELINE_TRACKING_REPORT.json`
- Flag any modules losing >5% coverage
- Update historical NDJSON log: `.codex/coverage/BASELINE_HISTORY.ndjson`

**Weekly Reports:**
- Generate trend analysis: `.codex/coverage/WEEKLY_COVERAGE_REPORT.md`
- Identify emerging patterns or anomalies
- Recommend next phase progression if baseline stable 7+ days

---

### Phase Progression Authority

**Phase 1 Readiness Criteria (40% target):**
- [ ] Baseline stable 30+ consecutive days at 34.63% ±1.5%
- [ ] All quality metrics maintained (100%/0%/100%/100%)
- [ ] Test count ≥2,467 (no regression)
- [ ] Zero regressions detected
- [ ] All module tiers meet minimums (T1≥90%, T2≥85%, T3≥77%, T4≥62%)
- [ ] Weekly trend shows no anomalies
- [ ] Module remediation strategy documented in ZERO_COVERAGE_REMEDIATION.md
- [ ] Zero-coverage module prioritization complete (120 modules)
- [ ] Test generation plan ready (2,467 → 2,800+ tests)

**When ALL criteria met:**
- ✅ Post approval comment recommending Phase 1 go-ahead
- ✅ Tag @mbaetiong for final sign-off
- ✅ Link to Phase 1 validation gates in PHASE_VALIDATION_GATES.yaml

---

### Escalation Delegation

The agent must understand when to escalate:

| Severity | Agent | Trigger |
|----------|-------|---------|
| 🟢 STABLE | Continue monitoring | Coverage 34.13% - 35.13% (±0.5%) |
| 🟡 ACCEPTABLE | Log & monitor | Coverage 33.63% - 35.63% (±1%) |
| 🟠 REVIEW NEEDED | unified-coverage-agent | -1.5% to 0% loss |
| 🔴 BLOCK PR | ci-emergency-response-agent | -3% to -1.5% loss |
| 🔴 CRITICAL | @mbaetiong + escalate immediately | < -3% loss |
| 🔴 BLOCK PR | unified-coverage-agent | Any module tier breach |
| 🔴 BLOCK PR | ci-testing-agent | Test count regression |
| 🔴 AUTO-HEAL | autonomous-test-healer-agent | Flaky/non-deterministic tests |

---

## 5. Validation Gates to Check Every PR

### Coverage Check
- ✅ Coverage within 33.13% - 36.13%
- ✅ No >5% loss on any module
- ✅ Module tier minimums met (T1≥90%, T2≥85%, T3≥77%, T4≥62%)

### Quality Metrics Check
- ✅ Test pass rate ≥99.5%
- ✅ Test flakiness ≤0.5%
- ✅ Test determinism = 100%
- ✅ Test isolation = 100%

### Test Count Check
- ✅ Total tests ≥2,467 (no regression)
- ✅ Distribution: Happy 65%+, Edge 15%+, Error 10%+

### Regression Detection
- ✅ Compare vs. baseline snapshot
- ✅ Flag any modules with >1% change
- ✅ Document changes >1% in PR comment

### Module Tier Check
- ✅ Tier 1: ≥90% (MAINTAIN - any loss triggers escalation)
- ✅ Tier 2: ≥85% (MAINTAIN - >1% loss blocks PR)
- ✅ Tier 3: ≥77% (RAISE - >2% loss blocks PR)
- ✅ Tier 4: ≥62% (RAISE - >3% loss triggers warning)

---

## 6. Tools & Access

### Available Scripts
- **`scripts/ci/generate_baseline_tracking_report.py`** - Run per PR, generate tracking report
- **`scripts/ci/establish_baseline.sh`** - Emergency baseline recalculation (use with caution)

### Reference Files
- **`.codex/COVERAGE_BASELINE_34_63.json`** - Authoritative baseline snapshot
- **`.codex/COVERAGE_VALIDATION_CRITERIA.md`** - All validation thresholds
- **`.codex/PHASE_VALIDATION_GATES.yaml`** - Phase-specific gates
- **`.codex/MODULE_TIER_PROGRESSION.md`** - Tier strategy & targets
- **`.codex/ZERO_COVERAGE_REMEDIATION.md`** - 120 module gap-fill plan
- **`.codex/coverage/BASELINE_TRACKING_REPORT.json`** - Per-PR tracking data
- **`.codex/coverage/BASELINE_HISTORY.ndjson`** - Historical trend data

### Output Artifacts
- **PR Comments:** Traffic-light dashboards with 🟢/🟡/🔴 status
- **Weekly Reports:** `.codex/coverage/WEEKLY_COVERAGE_REPORT.md`
- **Escalation Logs:** Posted to GitHub Issues & PR comments

---

## 7. Escalation Matrix (9 Tiers)

This matrix is the authority for all escalation decisions. Reference: COVERAGE_VALIDATION_CRITERIA.md Section 9.

| Issue | Threshold | Severity | Agent | Action |
|-------|-----------|----------|-------|--------|
| **Coverage drop** | 1.0-1.5% | 🟡 Yellow | unified-coverage-agent | Review + recommend fix |
| **Coverage drop** | 1.5-3% | 🟠 Orange | ci-emergency-response-agent | Block PR, investigate |
| **Coverage drop** | >3% | 🔴 Red | @mbaetiong | Escalate immediately |
| **Module tier breach** | Any Tier | 🔴 Red | unified-coverage-agent | Block PR, notify owner |
| **Test count drop** | <2,467 | 🔴 Red | ci-testing-agent | Block PR, restore tests |
| **Quality metric** | Any breach | 🔴 Red | autonomous-test-healer-agent | Block PR, auto-heal if possible |
| **Flaky test** | Any detection | 🟡 Yellow | autonomous-test-healer-agent | Create fix PR |
| **Measurement issue** | Accuracy <100% | 🔴 Red | ci-testing-agent | Re-run with diagnostics |
| **Phase progression** | Baseline stable 30d | 🟢 Green | @mbaetiong | Approve next phase start |

### Per-Tier Loss Tolerance (Escalation Rules)

| Tier | Loss | Action | Escalation |
|------|------|--------|-----------|
| Tier 1 | >0.5% | Block PR | @mbaetiong immediate |
| Tier 2 | >1.0% | Block PR | unified-coverage-agent |
| Tier 3 | >2.0% | Block PR | unified-coverage-agent |
| Tier 4 | >3.0% | Warn + recommend | unified-coverage-agent |

---

## 8. PR Validation Checklist (Must Pass All)

Every PR must pass ALL checks before merge:

- [ ] **Coverage Check:** 34.63% ±1.5% (33.13% - 36.13%)
- [ ] **Module Tiers:** T1≥90%, T2≥85%, T3≥77%, T4≥62%
- [ ] **Test Count:** ≥2,467 (no regression)
- [ ] **Quality Metrics:** 99.5%+ pass, ≤0.5% flakiness, 100% determinism, 100% isolation
- [ ] **Regression Detection:** No module loses >5%
- [ ] **No Regressions:** vs. baseline snapshot in COVERAGE_BASELINE_34_63.json
- [ ] **Module Changes:** Document any modules with >1% coverage change
- [ ] **Escalation:** If any threshold breached, assign to appropriate agent

---

## 9. CI Automation Gates

### Pre-Merge Gates (Blocking)

```python
# Gate 1: Overall coverage
if (coverage < 33.13% OR coverage > 36.13%):
    BLOCK_MERGE("Coverage regression detected")

# Gate 2: Test count
if (test_count < 2467):
    BLOCK_MERGE("Test count decreased")

# Gate 3: Module tiers
if (any_tier_below_minimum):
    BLOCK_MERGE("Module tier coverage breached")

# Gate 4: Quality metrics
if (test_flakiness > 0.5% OR determinism < 100%):
    BLOCK_MERGE("Quality metric failure")
```

### Escalation Gates (Routing)

```python
# Yellow alert
if (-1.5% <= coverage_change < 0%):
    unified_coverage_agent.review_and_recommend()

# Orange alert
if (-3% <= coverage_change < -1.5%):
    ci_emergency_response_agent.block_and_investigate()

# Red alert
if (coverage_change < -3%):
    escalate_to_mbaetiong("Critical coverage loss")

# Per-tier escalation
if (tier_1_loss > 0.5%):
    escalate_to_mbaetiong("Tier 1 security regression")
if (tier_2_loss > 1.0% OR tier_3_loss > 2.0%):
    unified_coverage_agent.block_merge()
```

---

## 10. Decision Framework (0-100 Scoring Rubric)

All agent decisions are scored on this 0-100 scale:

| Criterion | Points | Definition |
|-----------|--------|-----------|
| **Baseline Accuracy** | 20 | ±0.1% variance from COVERAGE_BASELINE_34_63.json snapshot |
| **Module Tier Validation** | 20 | All 4 tiers validated; >5% loss detected & flagged |
| **Quality Metric Coverage** | 20 | All 4 quality metrics checked (pass%, flakiness, determinism, isolation) |
| **Escalation Routing** | 25 | Correct agent routed (matrix Section 7); no false positives |
| **Documentation** | 15 | Tracking log updated; module changes documented; decision transparent |

**Thresholds:**
- **≥90 points:** Auto-approve for merge
- **70-89 points:** Human review recommended
- **<70 points:** Send back with specific feedback

---

## 11. Success Metrics & Readiness

### Phase 0 (Baseline) Success Criteria

All of the following must be true for 30+ consecutive days:

- ✅ Coverage stable at 34.63% ±1.5% (33.13% - 36.13%)
- ✅ All 4 quality metrics: 100% / 0% / 100% / 100% maintained
- ✅ Test count ≥2,467 (no regression)
- ✅ Zero regressions detected
- ✅ All module tiers meet minimums:
  - Tier 1: ≥90%
  - Tier 2: ≥85%
  - Tier 3: ≥77%
  - Tier 4: ≥62%
- ✅ All PR validation gates pass consistently
- ✅ Dashboard updated automatically on every run
- ✅ No false positives in escalation alerts
- ✅ Unified-coverage-agent operational and responsive
- ✅ Zero unplanned coverage dips or spikes
- ✅ Weekly trend reports show stable pattern

### Phase 1 Readiness Checklist (40% target)

Once baseline stable 30+ days, Phase 1 can begin with:

- [ ] ✅ Baseline stability validated for 30 days
- [ ] ✅ Module remediation strategy documented
- [ ] ✅ Zero-coverage module prioritization complete (120 modules)
- [ ] ✅ Test generation plan ready (2,467 → 2,800+ tests)
- [ ] ✅ Phase 1 validation gates defined in PHASE_VALIDATION_GATES.yaml
- [ ] ✅ Agent delegation tested and working
- [ ] ✅ Weekly trend reports show no anomalies
- [ ] ✅ unified-coverage-agent approved for Phase 1 promotion

When approved:
- Post comment: **"Phase 1 baseline stability confirmed. Ready for 40% target initiation."**
- Tag @mbaetiong for sign-off
- Create Phase 1 PR with test generation targets

---

## 12. Integration Points

### GitHub Actions Integration
- **Trigger:** Every PR opened/updated, every merge to main
- **Script:** `scripts/ci/generate_baseline_tracking_report.py`
- **Output:** Captured as PR comment via GitHub Actions

### Webhook Triggers
- **PR Comment Detection:** Listen for "@copilot coverage-report" command
- **Escalation Routing:** Route to appropriate agent based on threshold breach
- **Phase Progression:** Monitor for 30-day stability; auto-recommend Phase 1

### Cognitive Brain Integration
```python
from cognitive_brain.active_learning.hook import ActiveLearningHook

hook = ActiveLearningHook(query_budget_per_day=50)
hook.record_if_uncertain(
    audit=coverage_validation_result,
    assessment=escalation_decision,
)
```

---

## 13. Knowledge Graph & Pattern Base

The agent should maintain awareness of:

1. **Coverage Patterns:** Which test types (happy path, edge case, error) yield highest coverage gain
2. **Module Patterns:** Which modules typically regress; which require special handling
3. **Flakiness Patterns:** Which test suites have determinism issues; when to escalate
4. **Escalation Patterns:** Which thresholds trigger most escalations; when to adjust gates

Reference:
- `.codex/COVERAGE_VALIDATION_CRITERIA.md` (Section 9 - 9-tier escalation matrix)
- `.codex/PHASE_VALIDATION_GATES.yaml` (phase-specific validation logic)
- `.codex/MODULE_TIER_PROGRESSION.md` (per-tier strategies)

---

## 14. Anti-Patterns (DO NOT)

❌ **NEVER:**
- Route all failures to unified-coverage-agent without triage (agent fatigue)
- Grade decision without verifying baseline accuracy to ±0.1%
- Skip documentation to save time (compliance violation)
- Allow any coverage loss in Tier 1 without escalating to @mbaetiong
- Proceed to Phase 1 without 30+ days baseline stability
- Override module tier thresholds without written approval
- Allow >0.5% flakiness to persist (triggers autonomous-test-healer-agent)
- Block merge without posting escalation reason in PR comment

---

## 15. Activation & Readiness

**Current Status:** ✅ READY FOR PHASE 5 ACTIVATION

**Prerequisite Documents:**
- ✅ `.codex/COVERAGE_BASELINE_34_63.json` (baseline snapshot locked)
- ✅ `.codex/COVERAGE_VALIDATION_CRITERIA.md` (validation rules)
- ✅ `.codex/PHASE_VALIDATION_GATES.yaml` (phase gates)
- ✅ `.codex/MODULE_TIER_PROGRESSION.md` (tier strategy)
- ✅ `.codex/ZERO_COVERAGE_REMEDIATION.md` (gap-fill plan)
- ✅ `.codex/ESCALATION_RULES.yaml` (escalation routing)
- ✅ `.codex/PR_VALIDATION_FLOW.md` (PR validation flow)

**To Activate:**
1. Review this briefing thoroughly
2. Run escalation verification test (see `.codex/tests/validation/test_escalation_verification.py`)
3. Test baseline tracking report script
4. Verify all reference documents are readable
5. Confirm GitHub Actions integration is working
6. Post agent status in GitHub Discussions

**Contact:** @mbaetiong for Phase 5 activation sign-off

---

## References

- **Baseline Snapshot:** `.codex/COVERAGE_BASELINE_34_63.json`
- **Validation Criteria:** `.codex/COVERAGE_VALIDATION_CRITERIA.md` (Section 7, 9)
- **Phase Validation Gates:** `.codex/PHASE_VALIDATION_GATES.yaml`
- **Module Tier Progression:** `.codex/MODULE_TIER_PROGRESSION.md`
- **Zero-Coverage Remediation:** `.codex/ZERO_COVERAGE_REMEDIATION.md`
- **Escalation Rules:** `.codex/ESCALATION_RULES.yaml`
- **PR Validation Flow:** `.codex/PR_VALIDATION_FLOW.md`
- **Tracking Report Script:** `scripts/ci/generate_baseline_tracking_report.py`
