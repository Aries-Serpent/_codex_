# 🚀 CVE Remediation Sprint Plan — 2–3 Day Timeline

**Document ID**: PHASE_3_TASK_3.1  
**Created**: 2026-01-23  
**Based On**: Phase 1 Assessment Reports (Security, CI/CD, Coverage)  
**Status**: Ready for Execution  

---

## ⚠️ CRITICAL ASSESSMENT: Current State & Constraints

### Blocking Issues (MUST RESOLVE FIRST)

From **CI_STABILITY_ASSESSMENT.json**:
- **CI Failure Rate**: 66.7% (20 failures in last 30 runs)
- **9 Critical Blockers** (TOP 4 fixable in 1.5 hours):
  1. **Missing sentence-transformers** → RAG tests fail (~5 min fix)
  2. **isinstance() TypeError with union types** → Model registry (~15 min fix)
  3. **PyTorch FloatStorage pickling error** → Checkpoint tests (~30 min fix)
  4. **Missing LICENSE metadata in pyproject.toml** (~2 min fix)

From **ORCHESTRATOR_SECURITY_ASSESSMENT.json**:
- **92 Total Security Findings**:
  - 3 ERROR-severity (unsafe code execution)
  - 35 HIGH-severity (CVEs, credential exposure, deserialization)
  - 53 MEDIUM-severity (weak crypto, unsafe operations)
  - 1 LOW-severity

From **COVERAGE_READINESS_ASSESSMENT.json**:
- **3.61% Coverage** (vs baseline 10.7%)
- **795 zero-coverage files** (20 critical high-priority)
- **2253 skipped tests** (9% of all tests)
- ⚠️ **RECOMMENDATION**: Cannot safely validate security fixes without coverage

### Sprint Viability Assessment

| Constraint | Status | Impact | Mitigation |
|-----------|--------|--------|-----------|
| CI Stability | ⚠️ CRITICAL | May block agent execution | Fix Top 4 blockers first (1.5h) |
| Test Coverage | ⚠️ INSUFFICIENT | Cannot validate fixes | Run coverage validation in parallel |
| Agent Availability | ✅ READY | All agents available | Use distributed delegation |
| Time Window | ✅ ADEQUATE | 2–3 days = 48–72 hours | Aggressive time-boxing required |

**DECISION**: Proceed with **HYBRID APPROACH**:
- **Hour 0–1.5**: Stabilize CI (prerequisite gate)
- **Hour 1.5+**: Parallel tracks (CVE remediation + coverage stabilization)

---

## 📅 DAY 0: PREREQUISITE (1.5 Hours)

**GATE: CI Must Reach >95% Pass Rate Before Day 1 Starts**

### 0a: Dependency Upgrades (15 minutes)
- **Task**: Upgrade critical CVE dependencies
- **Agent**: Use inline bash commands
- **Action Items**:
  - [ ] Upgrade `diskcache` 5.6.3 → 5.6.4+ (CVE-2025-69872)
  - [ ] Upgrade `sqlitedict` 2.1.0 → 2.1.1+ (CVE-2024-35515)
  - [ ] Verify no transitive dependency conflicts
- **Expected Outcome**: Zero critical CVEs from dependencies

### 0b: Fix Top 4 CI Blockers (1 hour)
- **Agent**: `ci-auto-healer-agent` (autonomous mode)
- **Action Items**:

| Blocker | Pattern ID | Fix | Time |
|---------|-----------|-----|------|
| Missing sentence-transformers | fp002 | Add to pyproject.toml optional deps | 5 min |
| isinstance() TypeError | fp003 | Update type checking in model registry | 15 min |
| PyTorch pickling error | fp001 | Fix checkpoint serialization | 30 min |
| Missing LICENSE metadata | fp004 | Add license field to pyproject.toml | 2 min |

**Command**:
```bash
# ci-auto-healer-agent in --quick-fix mode
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 2
```

### 0c: Verify CI Gate (15 minutes)
- **Task**: Validate all critical tests pass
- **Expected Outcome**:
  - [ ] Top 9 blockers resolved
  - [ ] CI failure rate <10%
  - [ ] All pre-merge validation tests pass (>95%)
- **Checkpoint**: MUST STOP if any tests still fail; escalate to `ci-emergency-response-agent`

**✅ Day 0 Complete**: Proceed to Day 1 only if gate passes

---

## 📅 DAY 1: ERROR & HIGH PRIORITY (8–10 Hours)

**GOAL**: 0 ERROR findings, <10 HIGH findings remaining, NO REGRESSIONS

### 1a: Fix ERROR-Severity Findings (2–3 hours)
- **Findings**: 3 ERROR-level issues from Semgrep/CodeQL
  - [ ] `exec()` detected in src/codex_ml/plugins/registry.py:90
  - [ ] Dynamic `eval()` usage (code injection risk)
  - [ ] Unsafe deserialization pattern

- **Agent**: `codeql-alert-resolution-agent`
- **Mode**: Autonomous fix mode
- **Actions**:
  1. Replace `exec()` with safe alternatives (AST parsing, limited scope)
  2. Remove `eval()` calls; refactor to data-driven dispatch
  3. Replace `pickle` with `json` serialization where possible
  4. Add `# nosec B102` comments with justification

- **Timeline**: 2–3 hours
- **Test Validation**:
  ```bash
  python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
  ```
- **Exit Criteria**:
  - [ ] 0 ERROR-severity findings (verified with `semgrep` re-scan)
  - [ ] No new HIGH findings introduced
  - [ ] All tests pass

### 1b: Suppress/Remediate HIGH-Severity Findings (3–4 hours)
- **Findings**: 35 HIGH-level issues:
  - 22 insecure deserialization (pickle, unsafe obj instantiation)
  - 6 critical injection vulnerabilities (XXE, SQL injection)
  - 4 unsafe file operations
  - 3 sensitive data exposure (hardcoded credentials)

- **Agent**: `code-scanning-remediation-agent`
- **Mode**: Hybrid (fix + suppress)
- **Actions**:
  1. **For legitimate issues** (70%): Implement proper fixes
     - SQL injection → Use parameterized queries (SQLAlchemy ORM)
     - XXE → Disable external entities in XML parsers
     - Pickle → Use JSON/MessagePack + validation
  2. **For false positives** (30%): Add suppression with justification
     - `# lgtm[py/XXX]` for GitHub CodeQL
     - `<!-- pragma: allowlist secret -->` for secrets
     - `# noqa: E501` for safe cases

- **Timeline**: 3–4 hours
- **Test Validation**:
  ```bash
  python scripts/ci/rvs_preflight.py --group quick --workers 4
  ```
- **Exit Criteria**:
  - [ ] <10 HIGH findings remaining
  - [ ] All fixes verified with unit tests
  - [ ] No legitimate false positives suppressed

### 1c: Re-Run Security Suite & Validate (1–2 hours)
- **Tools**:
  - CodeQL: `codeql database analyze ...`
  - Semgrep: `semgrep --config=p/security-audit ...`
  - Bandit: `bandit -r src/`
  
- **Agent**: `unified-security-scanner`
- **Actions**:
  1. Run full security scan
  2. Compare against Day 0 baseline
  3. Verify no regression in ERROR/HIGH findings
  4. Generate SARIF report

- **Timeline**: 1–2 hours
- **Exit Criteria**:
  - [ ] SARIF report generated
  - [ ] No findings > HIGH severity
  - [ ] All pre-merge checks pass

### 1d: Test Coverage Validation (1 hour)
- **Agent**: `unified-coverage-agent` (measure mode)
- **Actions**:
  1. Re-measure coverage on Day 1 fixes
  2. Target: Coverage ≥ 5% (up from 3.61%)
  3. Identify critical zero-coverage modules
  
- **Timeline**: 1 hour
- **Exit Criteria**:
  - [ ] Coverage measurement baseline established
  - [ ] At least 1–2% improvement from Day 0 fixes
  - [ ] Top 10 zero-coverage files identified

---

## 📅 DAY 2: MEDIUM PRIORITY + VALIDATION (8–10 Hours)

**GOAL**: <5 MEDIUM findings remaining, coverage at baseline (10.7%), all critical paths tested

### 2a: Weak Cryptography Migration (2–3 hours)
- **Findings**: 8 MEDIUM issues with weak crypto
  - MD5 usage (non-cryptographic hashing)
  - SHA1 usage (deprecated)
  - Hardcoded crypto keys/salts
  
- **Agent**: `security-audit-agent`
- **Mode**: Auto-remediation
- **Actions**:
  1. Replace MD5 → SHA256 (for checksums)
  2. Replace SHA1 → SHA256
  3. Migrate hardcoded keys → environment variables
  4. Use `secrets` module for random salt generation
  5. Update pyproject.toml with pinned crypto library versions

- **Affected Files**:
  ```
  src/codex/security/hash_utils.py
  src/codex/auth/crypto.py
  src/codex_ml/utils/checksum.py
  ```

- **Timeline**: 2–3 hours
- **Test Validation**:
  ```bash
  pytest tests/security/ tests/auth/ -v --tb=short
  ```
- **Exit Criteria**:
  - [ ] 0 MD5/SHA1 usage in security paths
  - [ ] All crypto keys from environment
  - [ ] Unit tests pass

### 2b: Pickle Deserialization Audit & Hardening (3–4 hours)
- **Findings**: 20 MEDIUM/HIGH issues
  - Unsafe pickle.loads() without validation
  - Custom unpickler objects
  - Cached pickle objects from untrusted sources
  
- **Agent**: `unified-security-scanner` (pickle-specific mode)
- **Mode**: Audit + remediation
- **Actions**:
  1. Audit all `pickle.loads()` calls
  2. Identify data source for each (file, network, database)
  3. For untrusted sources:
     - Switch to JSON + validation
     - Or use `pickle.loads(..., restricted=True)` (if available)
     - Or implement whitelist-only object restoration
  4. For trusted internal caches:
     - Add validation hash (HMAC-SHA256)
     - Document threat model
     - Add `# nosec B301 <justification>` comment

- **Specific CVEs Addressed**:
  - CVE-2025-69872 (diskcache pickle vuln)
  - CVE-2024-35515 (sqlitedict pickle vuln)

- **Timeline**: 3–4 hours
- **Test Validation**:
  ```bash
  pytest tests/cache/ tests/serialization/ -v --tb=short
  ```
- **Exit Criteria**:
  - [ ] All untrusted pickle sources converted to JSON
  - [ ] Trusted caches have HMAC validation
  - [ ] Unit tests for deserialization pass

### 2c: Dynamic URL Hardening (2–3 hours)
- **Findings**: 20 MEDIUM issues
  - String concatenation in URLs (urllib, requests)
  - Unvalidated URL construction from user input
  - SSRF risks in internal service communication
  
- **Agent**: `code-scanning-remediation-agent`
- **Mode**: Safe refactoring
- **Actions**:
  1. Audit all URL construction patterns
  2. Replace string concat with `urllib.parse.urljoin()`
  3. Validate URL scheme (allow http/https only)
  4. Implement URL whitelist for internal services
  5. Add input validation for user-provided URLs

- **Affected Patterns**:
  ```python
  # Before (UNSAFE)
  url = f"https://api.example.com/users/{user_id}"
  
  # After (SAFE)
  url = urllib.parse.urljoin(
    base_url="https://api.example.com/",
    url=f"users/{user_id}"
  )
  # Then validate: assert url.startswith("https://api.example.com/")
  ```

- **Timeline**: 2–3 hours
- **Test Validation**:
  ```bash
  pytest tests/network/ tests/http_client/ -v -k "url"
  ```
- **Exit Criteria**:
  - [ ] All dynamic URLs use safe construction
  - [ ] URL whitelist implemented for sensitive endpoints
  - [ ] SSRF tests pass

### 2d: Final Security Scan + Coverage Validation (2 hours)
- **Agent**: `unified-security-scanner` + `unified-coverage-agent`
- **Mode**: Full validation sweep
- **Actions**:
  1. Run complete security suite (CodeQL + Semgrep)
  2. Generate final SARIF report
  3. Re-measure test coverage
  4. Verify coverage ≥ 10.7% baseline
  5. Identify remaining gaps

- **Timeline**: 2 hours
- **Exit Criteria**:
  - [ ] <5 MEDIUM findings remaining
  - [ ] Coverage ≥ 10.7% (or documented remediation plan)
  - [ ] All pre-merge checks pass
  - [ ] SARIF report generated

---

## 📅 DAY 3 (OPTIONAL): CLEANUP & DOCUMENTATION (4–6 Hours)

**GOAL**: <2 MEDIUM findings remaining, full documentation, sign-off ready

### 3a: Address Remaining Issues + Documentation (4–6 hours)
- **Agent**: `test-enhancement-agent` + agent-specific documenters
- **Actions**:
  1. Triage remaining MEDIUM findings
  2. For critical ones: implement fixes with full test coverage
  3. For acceptable risks: document threat model + controls
  4. Create security audit report (markdown)
  5. Update SECURITY.md with remediation summary
  6. Add CVE tracking to CHANGELOG.md

- **Deliverables**:
  - [ ] CVE_REMEDIATION_EXECUTION_REPORT.md (what was fixed)
  - [ ] SECURITY_AUDIT_DAY3_FINAL.md (findings summary)
  - [ ] OUTSTANDING_FINDINGS_WITH_MITIGATIONS.md (remaining issues)
  - [ ] Updated SECURITY.md with lessons learned

- **Timeline**: 4–6 hours

### 3b: Final Audit & Sign-Off (2 hours)
- **Agent**: `qa-walkthrough-agent`
- **Mode**: Comprehensive validation
- **Actions**:
  1. Final security scan (full codebase)
  2. Verify all Day 1 + Day 2 fixes still pass
  3. Coverage final measurement
  4. Pre-merge checklist validation
  5. Generate executive summary

- **Timeline**: 2 hours
- **Exit Criteria**:
  - [ ] All blockers from original sprint goal addressed
  - [ ] Documentation complete
  - [ ] Ready for deployment/merge to main

---

## 📊 Agent Delegation Matrix

| Task | Agent | Mode | Timeline | Success Criteria |
|------|-------|------|----------|------------------|
| **Day 0a**: Dependency upgrades | Manual bash | Direct | 15 min | CVE-2025-69872 & CVE-2024-35515 fixed |
| **Day 0b**: Fix CI blockers | `ci-auto-healer-agent` | Autonomous | 1 hour | <10% CI failure rate |
| **Day 0c**: Verify gate | Manual testing | Direct | 15 min | All pre-merge checks pass |
| **Day 1a**: Fix ERROR findings | `codeql-alert-resolution-agent` | Autonomous | 2–3 hours | 0 ERROR-severity findings |
| **Day 1b**: Suppress HIGH findings | `code-scanning-remediation-agent` | Hybrid | 3–4 hours | <10 HIGH findings |
| **Day 1c**: Security re-scan | `unified-security-scanner` | Full scan | 1–2 hours | SARIF report generated |
| **Day 1d**: Coverage validation | `unified-coverage-agent` | Measure | 1 hour | Baseline established |
| **Day 2a**: Crypto migration | `security-audit-agent` | Auto-remediate | 2–3 hours | 0 weak crypto findings |
| **Day 2b**: Pickle hardening | `unified-security-scanner` | Audit + fix | 3–4 hours | Deserialization safe |
| **Day 2c**: URL hardening | `code-scanning-remediation-agent` | Refactor | 2–3 hours | SSRF/URL injection fixed |
| **Day 2d**: Final validation | `unified-security-scanner` + `unified-coverage-agent` | Full sweep | 2 hours | Coverage ≥ 10.7% |
| **Day 3a**: Cleanup + docs | `test-enhancement-agent` + writers | Hybrid | 4–6 hours | All reports generated |
| **Day 3b**: Final sign-off | `qa-walkthrough-agent` | Comprehensive | 2 hours | Ready for production |

---

## 🎯 Success Criteria by Phase

### ✅ Day 0 (Prerequisite Gate)
- [ ] Diskcache & sqlitedict upgraded (CVE fixed)
- [ ] Top 4 CI blockers resolved
- [ ] CI failure rate <10%
- [ ] Pre-merge validation >95% pass rate

### ✅ Day 1 (ERROR & HIGH Priority)
- [ ] 0 ERROR-severity findings (0/3)
- [ ] <10 HIGH-severity findings remaining (<10/35)
- [ ] No regressions in finding count
- [ ] Coverage baseline re-measured (≥5%)
- [ ] All tests pass

### ✅ Day 2 (MEDIUM Priority + Validation)
- [ ] <5 MEDIUM findings remaining (<5/53)
- [ ] Coverage at baseline minimum (≥10.7%)
- [ ] All critical cryptography issues fixed
- [ ] All deserialization patterns safe
- [ ] All dynamic URL construction hardened
- [ ] Pre-merge checks pass

### ✅ Day 3 (Optional: Cleanup)
- [ ] <2 MEDIUM findings remaining
- [ ] All documentation complete
- [ ] Threat models documented for accepted risks
- [ ] Ready for deployment

---

## 📋 Pre-Sprint Checklist

- [ ] All assessment reports reviewed (Security, CI, Coverage)
- [ ] Agent credentials/permissions verified
- [ ] CI test environment stable (Day 0 prerequisite)
- [ ] Backup branch created (for rollback)
- [ ] Stakeholder notifications sent
- [ ] Success metrics documented
- [ ] Escalation path defined

---

## 🚨 Checkpoint Validation Strategy

### Daily Gating

**Day 0 → Day 1 Gate**:
```python
assert ci_failure_rate < 0.10, "CI not stable; escalate to ci-emergency-response-agent"
assert error_finding_count == 0, "No ERROR findings; safe to proceed"
assert coverage_measured == True, "Coverage baseline established"
```

**Day 1 → Day 2 Gate**:
```python
assert error_finding_count == 0, "All ERROR findings fixed"
assert high_finding_count < 10, "HIGH findings reduced to <10"
assert no_new_failures == True, "No regressions introduced"
assert coverage >= 5.0, "Coverage improved from 3.61%"
```

**Day 2 → Day 3 Gate** (optional):
```python
assert medium_finding_count < 5, "MEDIUM findings reduced to <5"
assert coverage >= 10.7, "Coverage at baseline minimum"
assert all_tests_pass == True, "All pre-merge checks pass"
```

### Failure Escalation

| Condition | Action | Escalation |
|-----------|--------|-----------|
| Day 0 gate fails | Stop sprint | `ci-emergency-response-agent` |
| Day 1 regressions | Halt; revert last changes | `code-review` + team leads |
| Day 2 coverage drops | Investigate; add tests | `coverage-maintenance-agent` |
| Day 3 unfinished | Extend sprint; document scope | Product management |

---

## 📈 Progress Tracking Template

```markdown
## Sprint Progress Report

**Sprint Date**: [Start] → [End]
**Current Phase**: [Day X, Task XY]
**Overall Progress**: [X/92 findings] = [X%] complete

### Daily Summary

**Day 0**: ✅ Complete
- [x] Deps upgraded (CVE-2025-69872, CVE-2024-35515)
- [x] Top 4 CI blockers fixed (1h10m)
- [x] CI gate passed (66.7% → 5.2% failure rate)

**Day 1**: 🔄 In Progress (6/8 hours used)
- [x] ERROR findings fixed (0/3)
- [ ] HIGH findings remediated (5/35 suppressed)
- [ ] Security re-scan pending
- [ ] Coverage validation pending

**Day 2**: ⏳ Not Started
- [ ] Crypto migration (0/8 issues)
- [ ] Pickle hardening (0/20 issues)
- [ ] URL construction (0/20 issues)
- [ ] Final validation

**Day 3**: ⏳ Optional
- [ ] Cleanup & documentation

### Risk Assessment
- **Green** ✅: On track, no blockers
- **Yellow** ⚠️: Minor delays, mitigating
- **Red** 🔴: Blocker encountered, escalated

### Outstanding Issues
- None yet

### Next Checkpoint
- Day 1 → Day 2 gate: [Expected Time]
```

---

## �� Rollback Plan

If sprint fails at any checkpoint:

1. **Identify failure point** (which gate failed)
2. **Preserve current state** (git commit)
3. **Escalate to appropriate agent**:
   - CI failures → `ci-emergency-response-agent`
   - Security regressions → `codeql-alert-resolution-agent`
   - Coverage issues → `coverage-maintenance-agent`
4. **Hold sprint** until root cause identified
5. **Retry** with modified plan or **extend timeline**

---

## 📚 Related Documents

- **Phase 1 Assessment Reports**:
  - `.codex/reports/ORCHESTRATOR_SECURITY_ASSESSMENT.json` (92 findings)
  - `.codex/reports/CI_STABILITY_ASSESSMENT.json` (66.7% failure rate)
  - `.codex/reports/COVERAGE_READINESS_ASSESSMENT.json` (3.61% coverage)

- **Phase 2 Artifacts**:
  - `.codex/reports/CVE_REMEDIATION_TRIAGE_REPORT.md` (prioritization)
  - `.codex/reports/AGENT_COORDINATION_PLAN.md` (agent orchestration)

- **Phase 4 Deliverable**:
  - Discussion #4872 (consolidated update with sprint results)

---

## 🎬 Execution Checklist

Before starting the sprint:

- [ ] Assess all prerequisite constraints (this document § "Critical Assessment")
- [ ] Confirm Day 0 can be completed in 1.5 hours
- [ ] Brief all assigned agents on their tasks
- [ ] Set up daily monitoring dashboard
- [ ] Establish communication channel for blockers
- [ ] Schedule 15-min daily standup
- [ ] Plan post-sprint retrospective

---

## 📝 Sprint Execution Notes

**Created**: 2026-01-23  
**Last Updated**: 2026-01-23  
**Prepared By**: PHASE_3_TASK_3.1 Planning  
**Ready for Execution**: Phase 4, Day 1  

---

## ✨ Key Insights

1. **CI Stability is a Prerequisite**: Cannot safely validate CVE fixes with 66.7% CI failure rate. Day 0 (1.5h) MUST complete before Day 1 starts.

2. **Hybrid Approach Required**: Cannot address all 92 findings in 2 days. Focus on ERROR/HIGH (38 findings) in Day 1, MEDIUM (53) in Day 2. Day 3 is cleanup/documentation.

3. **Coverage Validation Critical**: At 3.61% coverage, cannot safely validate security fixes. Run coverage stabilization in parallel with CVE remediation.

4. **Agent Delegation is Key**: Distribute work across specialized agents:
   - `codeql-alert-resolution-agent` → ERROR fixes
   - `code-scanning-remediation-agent` → HIGH remediation
   - `security-audit-agent` → Crypto migration
   - `unified-security-scanner` → Full scans
   - `ci-auto-healer-agent` → CI blocker fixes

5. **Time-Boxing is Critical**: Each task has explicit duration. Overruns trigger escalation, not extension.

6. **Checkpoint Gates are Hard**: No proceeding past a gate failure. Escalate or extend sprint.

---

**This plan is designed for autonomous agent execution with human oversight at checkpoints.**
