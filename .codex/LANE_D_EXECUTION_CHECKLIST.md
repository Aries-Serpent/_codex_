# Lane D: Phase 5.3 Execution Checklist

**Generated:** 2026-07-13T13:14:45Z  
**Total Items:** 302 findings + verification tasks  
**Status Tracking:** Update status column after each finding is fixed

---

## PRIORITY 1: CRITICAL FINDINGS (69 items)

### Category 1: Clear-Text Logging (30 items)

| ID | File | Lines | Issue | Status | Verified | Notes |
|---|------|-------|-------|--------|----------|-------|
| C1.1 | scripts/decode_workflow_secrets.py | 166-172 | Secret logging | ⬜ | ⬜ | Implement masking |
| C1.2 | .github/agents/admin-automation-agent/src/agent.py | 166-172 | Secret logging | ⬜ | ⬜ | Implement masking |
| C1.3 | scripts/ci/aggregate_security_findings.py | 281,287 | Sensitive logging | ⬜ | ⬜ | |
| C1.4 | scripts/fix_security_issues.py | Various | Sensitive logging | ⬜ | ⬜ | |
| C1.5 | scripts/github_secrets_sync.py | Multiple | Secret logging | ⬜ | ⬜ | |
| C1.6 | scripts/analyze_workflows.py | 319 | Log injection | ⬜ | ⬜ | |
| C1.7 | .github/scripts/ci_failure_crossref.py | 169 | Log injection | ⬜ | ⬜ | |
| C1.8 | scripts/ops/codex_mint_tokens_per_run.py | 401 | Secret logging | ⬜ | ⬜ | |
| C1.9 | scripts/ops/codex_repo_admin_bootstrap.py | 575 | Secret logging | ⬜ | ⬜ | |
| C1.10 | scripts/ci/copilot_security_agent_handoff.py | Multiple | Log injection | ⬜ | ⬜ | |
| C1.11 | scripts/observability/core_telemetry_collector.py | Multiple | Secret logging | ⬜ | ⬜ | |
| C1.12 | src/security/logging.py | Various | Configuration | ⬜ | ⬜ | |
| C1.13-C1.30 | Additional 18 files | Multiple | Clear-text logging | ⬜ | ⬜ | See LANE_D_COMPREHENSIVE_FINDINGS_CONSOLIDATION.md |

**Sub-total:** 30 findings  
**Effort Estimate:** 8.5 hours  
**Phase:** Week 1 (Days 1-2)  
**PR:** `phase-5.3-critical-logging-fixes`

**Testing Checklist:**
- [ ] Unit tests created for token masking
- [ ] All logging statements reviewed
- [ ] No secrets appear in test logs
- [ ] Pre-commit hook prevents secret logging
- [ ] Integration tests pass

---

### Category 2: Dynamic URL Handling (33 items)

| ID | File | Instances | Issue | Status | Verified | Notes |
|---|------|-----------|-------|--------|----------|-------|
| C2.1 | .github/agents/codex_reviewer/github_client.py | 4 | OWASP A01 | ⬜ | ⬜ | Create URLValidator first |
| C2.2 | .github/agents/github-guru-agent/github_client.py | 3 | OWASP A01 | ⬜ | ⬜ | |
| C2.3 | src/aries_serpent_core/autonomy/token_broker.py | 2 | OWASP A01 | ⬜ | ⬜ | |
| C2.4 | utils/safe_pickle.py | 1 | OWASP A01 | ⬜ | ⬜ | |
| C2.5 | services/msp_gateway/middleware/tenant_context.py | 1 | OWASP A01 | ⬜ | ⬜ | |
| C2.6-C2.22 | Additional 17 locations | 22 | OWASP A01 | ⬜ | ⬜ | See detailed list |

**Sub-total:** 33 findings  
**Effort Estimate:** 5.5 hours  
**Phase:** Week 1 (Days 3-4)  
**PR:** `phase-5.3-critical-url-validation`

**Testing Checklist:**
- [ ] URLValidator class created and tested
- [ ] file:// scheme rejected
- [ ] gopher:// scheme rejected
- [ ] ftp:// scheme rejected
- [ ] Unwhitelisted hosts rejected
- [ ] Valid HTTPS URLs pass
- [ ] Integration tests pass

---

### Category 3: Exec/Code Injection (2 items)

| ID | File | Issue | Status | Verified | Notes |
|---|------|-------|--------|----------|-------|
| C3.1 | Multiple | exec() with user input | ⬜ | ⬜ | Implement code sandbox |
| C3.2 | Multiple | eval() with user input | ⬜ | ⬜ | Implement code sandbox |

**Sub-total:** 2 findings  
**Effort Estimate:** 3.5 hours  
**Phase:** Week 1 (Days 5-6)  
**PR:** `phase-5.3-critical-code-injection`

**Testing Checklist:**
- [ ] Code sandbox implementation complete
- [ ] Arbitrary imports blocked
- [ ] Dangerous functions blocked
- [ ] Legitimate code paths work
- [ ] AST validation tests pass

---

## PRIORITY 2: HIGH FINDINGS (51 items)

### Category 4: Pickle Deserialization (23 items)

| ID | File | Instances | Issue | Status | Verified | Notes |
|---|------|-----------|-------|--------|----------|-------|
| H1.1 | mutants/tests/test_cache_management.py | 5 | OWASP A08 | ⬜ | ⬜ | Migrate to JSON |
| H1.2 | tests/test_cache_management.py | 5 | OWASP A08 | ⬜ | ⬜ | Migrate to JSON |
| H1.3 | mutants/src/codex_ml/utils/safe_pickle.py | 3 | OWASP A08 | ⬜ | ⬜ | Migrate to JSON |
| H1.4 | src/codex_ml/utils/safe_pickle.py | 3 | OWASP A08 | ⬜ | ⬜ | Migrate to JSON |
| H1.5 | utils/safe_pickle.py | 3 | OWASP A08 | ⬜ | ⬜ | Migrate to JSON |
| H1.6-H1.9 | Additional files | 4 | OWASP A08 | ⬜ | ⬜ | See detailed list |

**Sub-total:** 23 findings  
**Effort Estimate:** 8.5 hours  
**Phase:** Week 2 (Days 8-12)  
**PR:** `phase-5.3-high-pickle-migration`

**Testing Checklist:**
- [ ] JSON serialization helpers created
- [ ] All pickle.loads() replaced
- [ ] Test data converted to JSON
- [ ] Deserialized objects match original
- [ ] Performance acceptable
- [ ] Tests pass

---

### Category 5: Log Injection (11 items)

| ID | File | Count | Status | Verified | Notes |
|---|------|-------|--------|----------|-------|
| H2.1-H2.11 | Multiple files | 11 | ⬜ | ⬜ | Sanitize newlines/carriage returns |

**Sub-total:** 11 findings  
**Effort Estimate:** 2 hours  
**Phase:** Week 2 (Days 8-10)  
**PR:** `phase-5.3-high-log-injection`

---

### Category 6: Weak Password Hashing (6 items)

| ID | File | Count | Status | Verified | Notes |
|---|------|-------|--------|----------|-------|
| H3.1-H3.6 | Multiple files | 6 | ⬜ | ⬜ | Replace SHA256 with bcrypt |

**Sub-total:** 6 findings  
**Effort Estimate:** 1.5 hours  
**Phase:** Week 2  
**PR:** `phase-5.3-high-hashing`

---

### Category 7: Clear-Text Secret Storage (6 items)

| ID | File | Count | Status | Verified | Notes |
|---|------|-------|--------|----------|-------|
| H4.1-H4.6 | Multiple files | 6 | ⬜ | ⬜ | Use cryptography.Fernet |

**Sub-total:** 6 findings  
**Effort Estimate:** 2 hours  
**Phase:** Week 2  
**PR:** `phase-5.3-high-secret-storage`

---

### Category 8: Token Broker Security (5 items)

| ID | File | Count | Status | Verified | Notes |
|---|------|-------|--------|----------|-------|
| H5.1 | src/aries_serpent_core/autonomy/token_broker.py | - | ⬜ | ⬜ | Fix token handling |
| H5.2 | mutants/src/codex/autonomy/token_broker.py | - | ⬜ | ⬜ | Fix token handling |
| H5.3-H5.5 | Additional locations | - | ⬜ | ⬜ | Token security hardening |

**Sub-total:** 5 findings  
**Effort Estimate:** 2-3 hours  
**Phase:** Week 2 (Days 11-14)  
**PR:** `phase-5.3-high-token-security`

---

## PRIORITY 3: MEDIUM FINDINGS (155 items)

### Category 9: MD5 Weak Cryptography (18 items)

| ID | Issue | Count | Status | Verified | Notes |
|---|-------|-------|--------|----------|-------|
| M1 | MD5 hashing | 18 | ⬜ | ⬜ | Replace with SHA256 |

**Effort Estimate:** 4-6 hours  
**Phase:** Week 3 (Days 15-16)  
**PR:** `phase-5.3-medium-crypto`

**Testing:**
- [ ] All MD5 replaced
- [ ] SHA256 produces correct hashes
- [ ] No performance regression

---

### Category 10: Credential Disclosure in Logs (19 items)

| ID | Issue | Count | Status | Verified | Notes |
|---|-------|-------|--------|----------|-------|
| M2 | Credential logging | 19 | ⬜ | ⬜ | Add log filter |

**Effort Estimate:** 3-4 hours  
**Phase:** Week 3 (Days 15-17)  
**PR:** `phase-5.3-medium-log-sanitization`

---

### Category 11: File Permission Issues (5 items)

| ID | Issue | Count | Status | Verified | Notes |
|---|-------|-------|--------|----------|-------|
| M3 | Insecure file perms | 5 | ⬜ | ⬜ | Use umask(0o077) |

**Effort Estimate:** 1 hour  
**Phase:** Week 3 (Days 17-18)  
**PR:** `phase-5.3-medium-permissions`

---

### Category 12: Stack Trace Exposure (5 items)

| ID | Issue | Count | Status | Verified | Notes |
|---|-------|-------|--------|----------|-------|
| M4 | Stack trace exposure | 5 | ⬜ | ⬜ | Log internally only |

**Effort Estimate:** 2-3 hours  
**Phase:** Week 3 (Days 18-19)  
**PR:** `phase-5.3-medium-error-handling`

---

### Category 13: Additional MEDIUM Issues (108 items)

| ID | Issue | Count | Status | Verified | Notes |
|---|-------|-------|--------|----------|-------|
| M5-M113 | Various MEDIUM findings | 108 | ⬜ | ⬜ | See detailed categorization |

**Effort Estimate:** 3-5 hours  
**Phase:** Week 3  
**PR:** `phase-5.3-medium-misc`

---

## PRIORITY 4: LOW FINDINGS (42 items)

### Category 14: Code Quality Issues (42 items)

| ID | Issue | Count | Automation | Status | Notes |
|---|-------|-------|------------|--------|-------|
| L1 | Unused variables | 20 | ESLint | ⬜ | Auto-fixable |
| L2 | Semicolon insertion | 5 | Prettier | ⬜ | Auto-fixable |
| L3 | Trivial conditionals | 3 | Manual | ⬜ | 1-2h effort |
| L4 | Code formatting | 14 | ESLint/Prettier | ⬜ | Auto-fixable |

**Total Effort:** 1 hour (0.5h manual + 0.5h automation)  
**Phase:** Week 3 (Days 19-20)  
**PR:** `phase-5.3-low-code-cleanup`

**Automation Commands:**
```bash
eslint site/assets/javascripts/lunr/ --fix
prettier site/assets/javascripts/lunr/ --write
```

---

## VERIFICATION & TESTING

### Pre-Release Testing (Day 21)

**Full Test Suite:**
- [ ] `pytest tests/ -v --cov --cov-report=term-missing`
- [ ] Coverage: Minimum 85%
- [ ] All tests pass (0 failures)

**Security Scanning:**
- [ ] `semgrep --config p/owasp-top-ten --error`
- [ ] Result: 0 CRITICAL findings
- [ ] Result: 0-5 HIGH findings (only post-migration acceptables)
- [ ] Result: MEDIUM findings tracked

**Code Quality:**
- [ ] `codeql analyze --format sarif`
- [ ] Result: 0 CRITICAL, 0 HIGH

**Manual Review:**
- [ ] All PRs reviewed
- [ ] Design patterns verified
- [ ] Documentation updated

---

## STATUS TRACKING LEGEND

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not Started |
| 🟨 | In Progress |
| ✅ | Complete |
| ⚠️ | Blocked/Issue |
| 🔴 | Failed - Needs Rework |

---

## PROGRESS SUMMARY

### Week 1: CRITICAL Findings
- [ ] Status: All PRs merged and tested
- [ ] CRITICAL findings: 0 remaining
- [ ] Tests passing: YES
- [ ] Ready for Week 2: YES

### Week 2: HIGH Findings
- [ ] Status: All PRs merged and tested
- [ ] HIGH findings: 0 remaining
- [ ] Tests passing: YES
- [ ] Ready for Week 3: YES

### Week 3: MEDIUM/LOW Findings
- [ ] Status: All PRs merged and tested
- [ ] MEDIUM findings: <20 remaining
- [ ] LOW findings: Automated or accepted
- [ ] Documentation: Updated
- [ ] Ready for Release: YES

### Final Metrics
- [ ] Total findings fixed: 280+
- [ ] Test coverage: 85%+
- [ ] Security scan results: PASS
- [ ] Documentation: Complete
- [ ] Sign-off: Approved

---

## ADDITIONAL RESOURCES

**Related Documents:**
- LANE_D_COMPREHENSIVE_FINDINGS_CONSOLIDATION.md - Master consolidation report
- LANE_D_PRIORITY_MATRIX.md - Priority-ranked findings
- LANE_D_PHASE_5_3_ROADMAP.md - Detailed implementation steps
- Issue #5299 - Original security vulnerabilities
- LANE_A_DETAILED_FINDINGS.md - Python CodeQL findings
- LANE_B_DETAILED_FINDINGS.md - JavaScript CodeQL findings
- LANE_C_SEMGREP_PATTERN_ANALYSIS.md - OWASP pattern analysis

**Support Tools:**
- GitHub Security Scanning: https://github.com/Aries-Serpent/_codex_/security
- CodeQL Documentation: https://codeql.github.com
- Semgrep OWASP: https://semgrep.dev/r/p/owasp-top-ten
- Security Guidelines: SECURITY.md

---

**Checklist Version:** 1.0  
**Generated:** 2026-07-13T13:14:45Z  
**Status:** Ready for Phase 5.3 Execution  
**Authority:** D-tier autonomous
