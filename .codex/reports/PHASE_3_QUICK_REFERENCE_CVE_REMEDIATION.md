# 🎬 PHASE 3 QUICK REFERENCE - CVE Remediation Campaign

**Report:** `.codex/reports/UNIFIED_ORCHESTRATOR_ASSESSMENT_2026-06-15.md`
**Status:** READY FOR PHASE 0.1 EXECUTION
**Timeline:** 4-6 days to production readiness

---

## 🎯 Three Critical Blockers (Must Fix FIRST)

### BLOCKER #1: CI Failure Rate 66.7% → 95%+ target
**Agents Assigned:** `ci-testing-agent`
- **Root Causes:** 
  * Missing `sentence-transformers` (5 failures)
  * `isinstance()` TypeError (3 failures)
  * PyTorch pickling error (1 failure)
  * LICENSE/CLI args issues (7 failures)
  * Flaky tests (6 tests)
- **Timeline:** 1-2 days
- **Success:** Pre-merge validation ≥ 95% for 24 hours
- **Blocking:** All security validation, regression testing

### BLOCKER #2: Zero Coverage in Security Modules → 15%+ baseline
**Agents Assigned:** `test-enhancement-agent`, `unified-coverage-agent`
- **Root Causes:**
  * agents/ directory: 3,500 statements @ 0%
  * src/codex_ml/train_loop.py: 1,330 statements @ 0%
  * src/codex/cli.py: 896 statements @ 0%
  * Total: 795 zero-coverage files
- **Timeline:** 2-3 days
- **Success:** agents/ ≥ 25%, src/codex_ml ≥ 18%
- **Blocking:** CVE validation in untested modules

### BLOCKER #3: 2,253 Skipped Tests → < 500 skipped
**Agents Assigned:** `autonomous-test-healer-agent`, `ci-testing-agent`
- **Root Causes:** Environment-dependent tests, missing resources
- **Timeline:** 1-2 days
- **Success:** Skipped tests < 500 (4%), all critical paths runnable
- **Blocking:** Integration test validation, regression detection

---

## 📅 PHASE 0: Pre-Campaign Stabilization (2-3 Days)

**MUST COMPLETE BEFORE PHASE 1**

### Phase 0.1: Fix CI Blockers (1-2 days)
```
Agent: ci-testing-agent

Immediate (< 4 hours):
  [ ] Add `sentence-transformers` to pyproject.toml → fixes 5 failures
  [ ] Fix LICENSE metadata → fixes 1 failure
  [ ] Fix CLI `--paths` argument → fixes 1 failure

Short-term (< 6 hours):
  [ ] Fix `isinstance()` TypeError for union types → fixes 3 failures
  [ ] Fix PyTorch FloatStorage pickling → fixes 1 failure
  [ ] Add `audit_artifacts` directory → fixes 1 failure

Medium-term (< 8 hours):
  [ ] Fix missing checkpoint module → fixes 1 failure
  [ ] Fix FastAPI middleware → fixes 1 failure
  [ ] Stabilize flaky tests (6 tests)

Validation (24 hours):
  [ ] Monitor pre-merge validation ≥ 95% pass rate
```

**Success Metrics:**
- Pre-merge pass rate ≥ 95%
- CI stability score ≥ 50% (up from 33.3%)
- Failure rate ≤ 5% (down from 66.7%)

---

### Phase 0.2: Baseline Coverage (2-3 days in parallel)
```
Agents: test-enhancement-agent, unified-coverage-agent

Day 1 - Stabilization (4-6 hours):
  [ ] Reconcile coverage measurement (3.61% vs 10.7% discrepancy)
  [ ] Add smoke tests to agents/ (50-75 tests)
  [ ] Re-enable top 10 most-skipped test modules
  Target: 8%+, agents/ ≥ 10%, skipped < 2,000

Day 2 - Critical Module Coverage (8-10 hours):
  [ ] Add 35+ tests to src/codex_ml/train_loop.py (1,330 statements)
  [ ] Add 20+ tests to src/codex/cli.py (896 statements)
  [ ] Target src/codex_ml to 18%+
  Target: 15%+, src/codex_ml ≥ 18%

Day 3 - Exception Handling (4-6 hours):
  [ ] Add tests for broad exception handlers (225 patterns)
  [ ] Reduce skipped tests to < 1,500
  Target: 18%+, stability ≥ 95%
```

**Success Metrics:**
- Overall coverage ≥ 15%
- agents/ ≥ 15%, src/codex_ml ≥ 18%
- Skipped tests < 1,500
- Test stability ≥ 95%

---

## 📋 PHASE 1: CVE Remediation (1-2 Days)

**Only execute AFTER Phase 0 gates passed**

### Phase 1.1: HIGH-Severity CVEs
```
Agent: codeql-alert-resolution-agent

CVE-2025-69872 (diskcache 5.6.3 → 5.6.4+):
  Affected: src/codex_ml/utils/checkpoint_core.py
           src/caching/disk_cache_wrapper.py
  Actions: Upgrade, test checkpoint save/load
  Timeline: 2-4 hours

CVE-2024-35515 (sqlitedict 2.1.0 → 2.1.1+):
  Affected: src/db/persistence.py
           src/codex_ml/utils/data_cache.py
  Actions: Upgrade, validate deserialization paths
  Timeline: 2-4 hours
```

### Phase 1.2: ERROR-Level Findings (3 critical)
```
Code injection (exec) - 2 locations:
  Timeline: 2-4 hours

Log injection vulnerabilities - 6 occurrences:
  Timeline: 3-5 hours
```

### Phase 1.3: HIGH-Severity Findings (35 total)
```
Priority order:
  1. Credential logging (8+) → 2-3 hours
  2. Unsafe operations → 4-6 hours
  3. Remaining HIGH findings → 3-5 hours
```

---

## ✅ PHASE 2: Comprehensive Validation (1 Day)

**Execute AFTER Phase 1 complete**

```
Agent: security-audit-agent

[ ] Run full test suite (25,074 tests)
[ ] Run security scanning (CodeQL, Semgrep, pip-audit)
[ ] Validate patched modules ≥ 20% coverage
[ ] Verify no new failures
[ ] Generate CVE remediation proof report
```

---

## 🎬 Agent Task Assignments

| Agent | Phase | Role | Key Tasks |
|:---|:---|:---|:---|
| **ci-testing-agent** | 0.1 | Fix CI blockers | Add dependencies, fix types, stabilize flaky tests |
| **test-enhancement-agent** | 0.2 | Add smoke tests | agents/ smoke tests, exception handler tests |
| **autonomous-test-healer-agent** | 0.2 | Re-enable tests | Audit skipped tests, re-enable where possible |
| **unified-coverage-agent** | 0.2 + 1 | Drive coverage | Roadmap to 20%, gap-fill critical modules |
| **codeql-alert-resolution-agent** | 1 | Patch CVEs | Patch 2 CVEs, fix ERROR/HIGH findings |
| **security-audit-agent** | 2 | Validate | Full scan, proof report, regression check |

---

## 📊 Critical Path Metrics

### GATE 1: CI Stabilization (Day 1)
- [ ] Pre-merge validation ≥ 95%
- [ ] All 9 blockers fixed
- [ ] CI stability ≥ 50%
- [ ] Failure rate ≤ 5%

### GATE 2: Coverage Baseline (Day 2-3)
- [ ] Overall coverage ≥ 15%
- [ ] agents/ ≥ 15%, src/codex_ml ≥ 18%
- [ ] Skipped tests < 1,500
- [ ] Zero-coverage files < 200

### GATE 3: CVE Complete (Day 4-5)
- [ ] All ERROR/HIGH patched
- [ ] 2 CVEs upgraded with tests
- [ ] Test pass rate ≥ 95%
- [ ] Coverage ≥ 20%

### FINAL: Campaign Success (Day 5)
- [ ] Security findings: 92 → < 10
- [ ] CI failure: 66.7% → < 5%
- [ ] Coverage: 3.61% → ≥ 20%
- [ ] Skipped tests: 2,253 → < 500
- [ ] Zero regressions

---

## ⚠️ Risk Factors

**High Impact if Phase 0 Skipped:**
- Cannot validate CVE patches safely
- 795 untested files hide vulnerabilities
- 2,253 skipped tests prevent integration validation
- Overall campaign risk = HIGH 🔴

**Critical Path Dependency:**
```
Phase 0 (stabilization) 
  ↓ MUST COMPLETE
Phase 1 (CVE remediation)
  ↓ MUST COMPLETE
Phase 2 (validation)
```

---

## 📞 Escalation Contacts

**Issues during Phase 0.1:** → ci-testing-agent lead
**Issues during Phase 0.2:** → test-enhancement-agent + unified-coverage-agent leads
**Issues during Phase 1:** → codeql-alert-resolution-agent lead
**Issues during Phase 2:** → security-audit-agent lead

---

**Report:** `.codex/reports/UNIFIED_ORCHESTRATOR_ASSESSMENT_2026-06-15.md`
**Status:** PHASE 0.1 READY TO START
**Timeline:** 4-6 days to production readiness
**Risk Level:** 🔴 HIGH (Pre-Phase 0 startup)

