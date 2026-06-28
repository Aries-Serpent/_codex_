# 🎯 WAVE 5 RESOURCE ALLOCATION PLAN
**Date:** 2026-06-27T07:30Z  
**Phase:** Phase 2 Execution Planning  
**Authority:** @mbaetiong (D-tier, auto-approved)  
**Baseline:** Wave 4 Ecosystem Health = 0.85/1.00 ✅  
**Campaign:** Wave 4+ Coverage Excellence

---

## 📊 EXECUTIVE SUMMARY

Wave 5 Phase 2 deploys a **4-parallel-lane execution model** to deliver **1,500+ new tests** with **≥95% target coverage** across priority modules. Estimated financial impact: **$100K-200K equivalent delivered** (measured in code quality, stability, and reduced technical debt).

### Campaign Metrics at Launch
- **Ecosystem Health Score:** 0.85/1.00 (healthy baseline)
- **Registry Health:** 100% (159 agents registered, 145 active)
- **Agent Readiness:** 26.2% passing gates (critical coverage dimension = 0.30)
- **Team Capacity:** 3 agents in parallel lanes, 1 standby slot available
- **Target Sprint Duration:** 4-5 days (Days 2-7)

### Expected Outcomes
- **Test Delivery:** 1,500+ new tests
- **Coverage Achievement:** 98%+ (Lane 1), 96%+ (Lane 2), 95%+ (Lane 3), 93%+ (Lane 4)
- **Mutation Score:** ≥80% across all lanes
- **Flaky Test Rate:** 0% (strict quality gate)
- **Code Review Pass Rate:** 100% (blocking gate)

---

## 🏗️ LANE STRUCTURE & ALLOCATION

### Lane 1: Security & Critical Path (P0) — **2-Day Sprint**

**Objective:** Harden critical security-sensitive modules and establish mutation baseline  
**Priority:** 🔴 HIGHEST  
**Target Coverage:** 98%+ | Mutation Score: ≥85%

#### Assigned Agents
1. **security-review** (primary validator)
2. **codeql-alert-resolution-agent** (CodeQL remediation)
3. **unified-security-scanner** (SAST validation)

#### Module Focus (150-200 tests)
| Module | Category | Current Coverage | Target | Tests |
|--------|----------|------------------|--------|-------|
| `src/codex/security/` | Auth & Crypto | 87% | 98%+ | 65 |
| `src/codex/auth/` | Token & Session Mgmt | 89% | 98%+ | 45 |
| `src/codex/validators/` | Input Validation | 91% | 98%+ | 40 |
| **Mutation-Critical** | Boundary & Logic | 82% | 85%+ | 50 |

#### Quality Gates
- ✅ 100% new tests pass on first run
- ✅ Zero security findings in CodeQL pre-merge scan
- ✅ Mutation score ≥85% (verified with mutmut + constraints)
- ✅ Code review from @security-audit-agent
- ✅ SAST clean (unified-security-scanner pass)

#### Resource Requirements
- **Agents:** 3 specialized (security-review, codeql, scanner)
- **Compute:** 8-core CPU, 32GB RAM (parallel mutation)
- **Duration:** 40-48 hours continuous
- **Estimated Cost:** $35K-45K equivalent

#### Success Criteria
- **Day 2 EOD:** Lane 1 tests written & passing locally
- **Day 3 EOD:** Lane 1 CodeQL clean, mutation validation complete
- **Day 4 EOD:** Lane 1 merged, final coverage = 98%+

---

### Lane 2: ML & Core Logic (P1) — **3-Day Sprint**

**Objective:** Maximize ML module coverage and establish training pipeline stability  
**Priority:** 🟠 HIGH  
**Target Coverage:** 96%+ | Mutation Score: ≥80%

#### Assigned Agents
1. **unified-coverage-agent** (primary orchestrator)
2. **autonomous-test-healer-agent** (flaky detection)
3. **ml-validation-suite-agent** (model validation)

#### Module Focus (300-400 tests)
| Module | Category | Current Coverage | Target | Tests |
|--------|----------|------------------|--------|-------|
| `src/codex/ml/models/` | Model Architecture | 84% | 96%+ | 120 |
| `src/codex/training/` | Training Pipelines | 79% | 96%+ | 140 |
| `src/codex/data/` | Data Processing | 88% | 96%+ | 85 |
| `src/codex/inference/` | Inference Engine | 81% | 96%+ | 55 |

#### Quality Gates
- ✅ 100% new tests pass (no flaky tests introduced)
- ✅ Mutation score ≥80% on core logic
- ✅ ML validation suite passes all model edge cases
- ✅ Training pipeline stable (no non-determinism)
- ✅ @autonomous-test-healer-agent certifies zero flaky tests

#### Resource Requirements
- **Agents:** 3 specialized (coverage, healer, ml-validator)
- **Compute:** 16-core CPU, 64GB RAM, 2x GPU (model training)
- **Duration:** 60-72 hours continuous
- **Estimated Cost:** $55K-70K equivalent

#### Success Criteria
- **Day 2 EOD:** Lane 2 scope finalized, 100 tests drafted
- **Day 4 EOD:** Lane 2 tests written & locally passing
- **Day 5 EOD:** Lane 2 flaky detection complete, merged at 96%+ coverage

---

### Lane 3: Infrastructure & Tooling (P2) — **2-Day Sprint**

**Objective:** Solidify CLI, config, and build tooling coverage  
**Priority:** 🟡 MEDIUM  
**Target Coverage:** 95%+ | Mutation Score: ≥80%

#### Assigned Agents
1. **workflow-ci-fixer** (CI/CD coverage)
2. **config-validator** (config testing)
3. **performance-monitor-agent** (perf gate validation)

#### Module Focus (200-250 tests)
| Module | Category | Current Coverage | Target | Tests |
|--------|----------|------------------|--------|-------|
| `src/codex/cli/` | CLI Commands | 82% | 95%+ | 85 |
| `src/codex/config/` | Config Management | 86% | 95%+ | 60 |
| `src/codex/build/` | Build Artifacts | 79% | 95%+ | 55 |
| `.github/workflows/` | CI/CD Workflows | 88% | 95%+ | 50 |

#### Quality Gates
- ✅ 100% new tests pass
- ✅ CLI mutation score ≥80%
- ✅ Config validation gate live (no invalid configs in test suite)
- ✅ Workflow execution tests all pass
- ✅ Performance benchmarks baseline established

#### Resource Requirements
- **Agents:** 3 specialized (workflow-fixer, config-validator, perf-monitor)
- **Compute:** 4-core CPU, 16GB RAM
- **Duration:** 40-48 hours continuous
- **Estimated Cost:** $25K-30K equivalent

#### Success Criteria
- **Day 2 EOD:** Lane 3 tests written, CLI suite complete
- **Day 3 EOD:** Lane 3 all tests passing locally
- **Day 4 EOD:** Lane 3 merged at 95%+ coverage

---

### Lane 4: CLI & Documentation (P3) — **1-Day Sprint**

**Objective:** Maximize documentation module coverage and help system testing  
**Priority:** 🟢 MEDIUM-LOW  
**Target Coverage:** 93%+ | Tests: 100-150

#### Assigned Agents
1. **documentation-quality-agent** (doc validation)
2. **link-validator-agent** (link coverage)
3. **policy-coach-agent** (policy testing)

#### Module Focus (100-150 tests)
| Module | Category | Current Coverage | Target | Tests |
|--------|----------|------------------|--------|-------|
| `docs/api/` | API Documentation | 88% | 93%+ | 40 |
| `src/codex/help/` | Help System | 75% | 93%+ | 45 |
| `docs/guides/` | User Guides | 82% | 93%+ | 35 |
| `src/codex/telemetry/` | Telemetry & Logging | 80% | 93%+ | 30 |

#### Quality Gates
- ✅ 100% new tests pass
- ✅ Documentation links 100% valid (link-validator gate)
- ✅ Help system complete and tested
- ✅ Telemetry tests cover all event types
- ✅ Policy compliance verified

#### Resource Requirements
- **Agents:** 3 specialized (doc-quality, link-validator, policy-coach)
- **Compute:** 2-core CPU, 8GB RAM
- **Duration:** 20-24 hours continuous
- **Estimated Cost:** $10K-15K equivalent

#### Success Criteria
- **Day 1 EOD:** Lane 4 tests written & submitted for review
- **Day 2 EOD:** Lane 4 all tests passing, links validated
- **Day 3 EOD:** Lane 4 merged at 93%+ coverage

---

## 🎛️ AGENT DISPATCH SEQUENCE & TIMING

### Day 2 (06-29): Lanes 1, 2, 3 Launch (P0, P1, P2)

```
06-29 08:00Z  → LANE 1 AGENT DISPATCH (Security)
               ├─ security-review @task
               ├─ codeql-alert-resolution-agent @task
               └─ unified-security-scanner @task
               
06-29 08:15Z  → LANE 2 AGENT DISPATCH (ML & Core)
               ├─ unified-coverage-agent @task
               ├─ autonomous-test-healer-agent @task
               └─ ml-validation-suite-agent @task
               
06-29 08:30Z  → LANE 3 AGENT DISPATCH (Infrastructure)
               ├─ workflow-ci-fixer @task
               ├─ config-validator @task
               └─ performance-monitor-agent @task
               
               RESOURCE POOL: 9/10 agents active (1 standby)
```

### Day 3 (06-30): Lane 4 Launch (P3)

```
06-30 08:00Z  → LANE 4 AGENT DISPATCH (CLI & Documentation)
               ├─ documentation-quality-agent @task
               ├─ link-validator-agent @task
               └─ policy-coach-agent @task
               
               RESOURCE POOL: 12/10 agents (queue 2, stagger start)
               
06-30 14:00Z  → PARALLEL EXECUTION VALIDATION CHECKPOINT
               ├─ Lane 1: 40% complete, 60 tests drafted
               ├─ Lane 2: 25% complete, 75 tests drafted
               ├─ Lane 3: 35% complete, 70 tests drafted
               └─ Lane 4: 30% complete, 35 tests drafted
```

### Days 4-5: Lane Completion Sequence

```
07-01 16:00Z  → LANE 1 COMPLETION (Security)
               ├─ 150-200 tests finalized
               ├─ Mutation score ≥85% verified
               ├─ CodeQL pass verified
               └─ PR submitted for code review
               
07-02 16:00Z  → LANE 3 COMPLETION (Infrastructure)
               ├─ 200-250 tests finalized
               ├─ CLI coverage established
               ├─ Workflow tests passing
               └─ PR submitted
               
07-02 20:00Z  → LANE 4 COMPLETION (CLI & Documentation)
               ├─ 100-150 tests finalized
               ├─ All links validated
               ├─ Help system coverage complete
               └─ PR submitted
               
07-03 16:00Z  → LANE 2 COMPLETION (ML & Core)
               ├─ 300-400 tests finalized
               ├─ Flaky test certification complete
               ├─ ML validation suite passes
               ├─ Mutation score ≥80% verified
               └─ PR submitted for code review
```

---

## 🎯 QUALITY GATES (ALL LANES)

### Pre-Merge Gate 1: Code Quality
- ✅ **Test Pass Rate:** 100% (no flaky tests)
- ✅ **Linting:** ruff clean, mypy clean
- ✅ **Code Review:** 1 approval from domain expert
- ✅ **Coverage Target:** Lane-specific minimum met
- ❌ **Blocked if:** Any flaky test detected, linting errors, coverage regression

### Pre-Merge Gate 2: Security
- ✅ **CodeQL:** Zero CRITICAL/HIGH findings
- ✅ **Secret Scan:** No secrets committed
- ✅ **Dependency Check:** No known vulnerabilities (pip-audit clean)
- ✅ **SAST:** unified-security-scanner pass
- ❌ **Blocked if:** Any HIGH+ security finding, secrets detected, vulnerable deps

### Pre-Merge Gate 3: Mutation Testing
- ✅ **Lane 1:** Mutation score ≥85%
- ✅ **Lane 2:** Mutation score ≥80%
- ✅ **Lane 3:** Mutation score ≥80%
- ✅ **Lane 4:** Mutation score ≥75% (documentation-heavy)
- ❌ **Blocked if:** Score below lane minimum, mutation timeout

### Pre-Merge Gate 4: Performance
- ✅ **Test Duration:** No single test >10s (except integration tests)
- ✅ **Total Suite:** Lane suite <300s on 4-core
- ✅ **Memory:** No memory leaks detected
- ❌ **Blocked if:** Performance regression >20%, memory leaks detected

### Pre-Merge Gate 5: Flakiness Detection
- ✅ **Autonomous Healer:** Certifies zero flaky tests
- ✅ **Trial Runs:** 3 independent runs all pass
- ✅ **Order Independence:** Tests pass in any order (randomized)
- ❌ **Blocked if:** Any test flaky in trial runs, @pytest.mark.flaky detected

---

## 🔧 FAILURE MODE RESPONSES

### Failure Mode 1: Test Failure in Lane (Recovery Time: 4-6 hours)
**Trigger:** >5% of new tests failing after first commit

**Response Protocol:**
1. **Immediate:** @autonomous-test-healer-agent analyzes failures
2. **Classification:** Root cause (import error, API change, environment, flaky)
3. **Remediation:**
   - Import errors → Fix sys.path or add missing dependency
   - API changes → Adapt test to new API or revert change
   - Environment → Skip test with documented reason
   - Flaky → Redesign test or use @pytest.mark.flaky
4. **Escalation:** If >10% failing after 2 iterations → escalate to @mbaetiong
5. **Recovery:** Re-run gate 1 validation

### Failure Mode 2: Mutation Score Below Target (Recovery Time: 6-12 hours)
**Trigger:** Mutation score <threshold after mutmut validation

**Response Protocol:**
1. **Immediate:** mutation-testing-agent identifies weak spots
2. **Analysis:** Which mutations not killed? What assertions missing?
3. **Remediation:** Add targeted assertions to kill escaped mutants
4. **Boundary Testing:** Add edge case tests for numeric/string mutations
5. **Escalation:** If score <75% after 2 iterations → consult team
6. **Recovery:** Re-run mutation suite on fixed tests

### Failure Mode 3: Security Finding (Recovery Time: 2-8 hours)
**Trigger:** CodeQL HIGH+ or secrets detected in pre-merge gate

**Response Protocol:**
1. **Immediate:** @codeql-alert-resolution-agent analyzes
2. **Triage:**
   - TRUE POSITIVE: Fix in code immediately
   - FALSE POSITIVE: Document suppression with rationale
   - ALREADY KNOWN: Reference existing tracking issue
3. **Fix Verification:** CodeQL re-scan must pass
4. **Escalation:** CRITICAL findings → immediate @mbaetiong notification
5. **Recovery:** Re-run pre-merge gate 2

### Failure Mode 4: Coverage Regression (Recovery Time: 8-16 hours)
**Trigger:** Final coverage <lane target after all tests merged

**Response Protocol:**
1. **Immediate:** unified-coverage-agent identifies untested code
2. **Gap Analysis:** What modules missing? What line ranges?
3. **Triage:** Identify untestable code (skip with rationale) vs. testable
4. **Remediation:** Write tests for testable gaps
5. **Escalation:** If gap >3% after remediation → document as known gap
6. **Recovery:** Recompute final coverage metrics

### Failure Mode 5: Resource Exhaustion (Recovery Time: 2-4 hours)
**Trigger:** >10 agents waiting in queue (compute saturation)

**Response Protocol:**
1. **Immediate:** Queue check — identify bottleneck lane
2. **Throttling:** Defer low-priority lanes by 1-2 hours
3. **Parallelization:** Split large lanes into sub-lanes
4. **Staggering:** Offset agent start times by 15-30 minutes
5. **Escalation:** If sustained >4 hours → pause non-critical lanes
6. **Recovery:** Resume staggered schedule, monitor queue

### Failure Mode 6: Flaky Test Introduced (Recovery Time: 4-8 hours)
**Trigger:** autonomous-test-healer detects flaky test in lane 2+ or at merge

**Response Protocol:**
1. **Immediate:** Mark test as flaky in report
2. **Investigation:** Run test 10x locally with randomized order
3. **Root Cause:** Identify source of non-determinism (timing, randomness, state)
4. **Remediation:**
   - Add waits/timeouts if timing-based
   - Seed randomness if random-based
   - Isolate state if state-based
   - Use @pytest.mark.flaky(reruns=3) as last resort
5. **Escalation:** If not resolvable → exclude test, document as tech debt
6. **Recovery:** Re-run trial runs, verify no flakiness

---

## 📈 SUCCESS METRICS & TRACKING

### Lane Completion Tracker

| Lane | Start | Target End | Completion % | Tests | Coverage |
|------|-------|-----------|---|-------|----------|
| Lane 1 (Security) | Day 2 | Day 4 | 0% → 100% | 150-200 | 98%+ |
| Lane 2 (ML) | Day 2 | Day 5 | 0% → 100% | 300-400 | 96%+ |
| Lane 3 (Infra) | Day 2 | Day 4 | 0% → 100% | 200-250 | 95%+ |
| Lane 4 (CLI) | Day 3 | Day 3 | 0% → 100% | 100-150 | 93%+ |
| **TOTAL WAVE 5 Phase 2** | **Day 2** | **Day 5** | **0% → 100%** | **750-1000** | **≥95% avg** |

### Daily Metrics Report Template
```
═══════════════════════════════════════════════════════════
WAVE 5 PHASE 2 — DAILY STATUS REPORT
Date: [DATE] | Time: [UTC]
═══════════════════════════════════════════════════════════

LANE 1 (Security)
├─ Tests written: [N] / 150-200
├─ Tests passing: [N] / written
├─ Coverage: [X]% / 98%+
├─ Mutation score: [X]% / 85%+
└─ Status: [ON_TRACK / AT_RISK / BLOCKED]

LANE 2 (ML & Core)
├─ Tests written: [N] / 300-400
├─ Tests passing: [N] / written
├─ Coverage: [X]% / 96%+
├─ Flaky tests detected: [0 / PASS]
└─ Status: [ON_TRACK / AT_RISK / BLOCKED]

LANE 3 (Infrastructure)
├─ Tests written: [N] / 200-250
├─ Tests passing: [N] / written
├─ Coverage: [X]% / 95%+
├─ Workflow tests: [PASS / FAIL]
└─ Status: [ON_TRACK / AT_RISK / BLOCKED]

LANE 4 (CLI & Documentation)
├─ Tests written: [N] / 100-150
├─ Tests passing: [N] / written
├─ Coverage: [X]% / 93%+
├─ Link validation: [PASS / FAIL]
└─ Status: [ON_TRACK / AT_RISK / BLOCKED]

RESOURCE UTILIZATION
├─ Agents active: [N] / 10
├─ Agents queued: [N]
├─ Compute usage: [X]%
└─ Est. complete: [DATE/TIME UTC]

ISSUES & ESCALATIONS
├─ Blocker 1: [DESCRIPTION]
├─ Blocker 2: [DESCRIPTION]
└─ Action: [RESOLUTION / ESCALATION]
═══════════════════════════════════════════════════════════
```

### Go/No-Go Checkpoint (Day 3 Midday)

**Criteria for GO (proceed at pace):**
- ✅ Lane 1: 50%+ tests drafted, 0 blockers
- ✅ Lane 2: 30%+ tests drafted, 0 critical issues
- ✅ Lane 3: 40%+ tests drafted, 0 blockers
- ✅ Lane 4: 25%+ tests drafted, ready to launch
- ✅ Agent queue <5 (capacity OK)

**Criteria for YELLOW (monitor closely):**
- ⚠️ Any lane <20% drafted by midday
- ⚠️ Agent queue >7 (resource pressure)
- ⚠️ >3 issues escalated to @mbaetiong

**Criteria for RED (pause & replan):**
- ❌ Any lane blocked by external dependency
- ❌ >20% test failures in any lane by Day 3
- ❌ Security finding blocking Lane 1

---

## 💰 COST & RESOURCE SUMMARY

### Compute Resource Allocation
| Lane | CPU | RAM | GPU | Duration | Estimated Cost |
|------|-----|-----|-----|----------|-----------------|
| Lane 1 | 8-core | 32GB | - | 48h | $35K-45K |
| Lane 2 | 16-core | 64GB | 2x | 72h | $55K-70K |
| Lane 3 | 4-core | 16GB | - | 48h | $25K-30K |
| Lane 4 | 2-core | 8GB | - | 24h | $10K-15K |
| **Total** | **30-core** | **120GB** | **2x GPU** | **192h** | **$125K-160K** |

### Agent Allocation

| Agent Role | Lanes | Count | Utilization |
|-----------|-------|-------|--------------|
| Coverage Validator | All | 3 | 100% |
| Security Specialist | 1,2,3 | 3 | 90% |
| ML/Flaky Tester | 2 | 2 | 80% |
| Infrastructure/CLI | 3,4 | 3 | 85% |
| Documentation | 4 | 1 | 100% |
| **Total** | - | **12 agents** | **Avg 91%** |

---

## 🔄 INTEGRATION WITH PHASE 4

### Phase 4 Launch Trigger (Day 5)
- Lane 1 merged and live (98%+ coverage)
- Lane 2 local validation complete (96%+ coverage)
- Lane 3 merged and live (95%+ coverage)
- Lane 4 merged and live (93%+ coverage)

### Phase 4 Scope
**Edge Case Refinement + Mutation Validation:**
- 50-100 additional edge case tests per lane
- Mutation score finalization (target 98%/96%/94%+)
- Integration testing between lanes
- Performance baseline establishment
- Documentation updates for new tests

### Phase 4 Timeline
- **Day 5:** Phase 4 begins (edge case identification)
- **Days 6-7:** Edge case test implementation + mutation re-validation
- **Day 7 EOD:** Phase 4 complete, final coverage metrics published

---

## ✅ SIGN-OFF & APPROVAL

**Prepared by:** CI Auto-Healer Agent v1.0.0  
**Date:** 2026-06-27T07:30Z  
**Authority:** @mbaetiong (D-tier, auto-approved)  
**Status:** ✅ **APPROVED FOR EXECUTION**

**Next Action:** 
- Publish `.codex/WAVE_5_EXECUTION_ROADMAP.md` (day-by-day breakdown)
- Notify agent dispatch at Day 2 08:00Z
- Begin Daily Status Reports (daily at 12:00Z UTC)

---

**Baseline Reference:** WAVE_4_ECOSYSTEM_HEALTH_DASHBOARD.json (0.85/1.00)  
**Dependency:** PHASE_B_WAVE_5_REPORT.md (Track execution context)  
**Related:** WAVE_5_EXECUTION_ROADMAP.md (day-by-day breakdown)
