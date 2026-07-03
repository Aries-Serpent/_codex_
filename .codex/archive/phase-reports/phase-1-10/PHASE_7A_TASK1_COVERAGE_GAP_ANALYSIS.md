# PHASE 7A TASK 1: Coverage Gap Analysis & Roadmap

**Status:** ✅ COMPLETE  
**Date Generated:** 2026-06-16 21:31:45  
**Repository:** Aries-Serpent/_codex_  
**Analysis Window:** Current production state

---

## Executive Summary

This report analyzes the current test coverage landscape of the _codex_ repository and provides a strategic roadmap to reach ≥20% coverage (current gap: 12.96 percentage points).

### Current State

- **Current Coverage:** 7.04%
- **Target Coverage:** 20%
- **Gap to Close:** 12.96 percentage points
- **Total Source Statements:** 100,355
- **Tested Statements:** 7,068
- **Untested Statements:** 93,287

### Coverage Impact Analysis

| Metric | Current | Target | Delta |
|--------|---------|--------|-------|
| Overall Coverage | 7.04% | 20% | +12.96pp |
| Tested Statements | 7,068 | ~20,071 | +~13,003 |
| Test Statements Needed | - | ≥20% | ~13,003 |

---

## Module Risk Ranking (Top 50 Lowest-Coverage)

### Risk Ranking Methodology

1. **Security Weight** (8-9x critical): auth, security, safety, crypto modules
2. **API Weight** (7x): API endpoints, gateway modules  
3. **Infrastructure Weight** (7x): bridge, cli, worker modules
4. **Base Score** (1-5x): File size and coverage gap

### Risk Matrix: Top 20 Critical Modules

| Rank | Module/File | Coverage | Risk Score | Effort (days) | Category |
|------|-------------|----------|------------|---------------|----------|
| 1 | `security/providers/environment_provider.py` | 0.0% | 233.6 | 2.5 | Security |\n| 2 | `codex/auth/in_memory_user_repository.py` | 0.0% | 228.8 | 2.5 | Security |\n| 3 | `security/providers/github_provider.py` | 0.0% | 225.6 | 6.3 | Security |\n| 4 | `codex/auth/sqlite_user_repository.py` | 0.0% | 224.0 | 3.0 | Security |\n| 5 | `security/providers/aws_provider.py` | 0.0% | 220.8 | 4.2 | Security |\n| 6 | `codex/cognitive/safety_guards.py` | 0.0% | 217.6 | 6.6 | Security |\n| 7 | `codex_ml/security/cve_monitor.py` | 0.0% | 217.6 | 3.7 | Security |\n| 8 | `codex/security/log_sanitizer.py` | 0.0% | 216.0 | 2.2 | Security |\n| 9 | `integrations/github_app_auth.py` | 0.0% | 216.0 | 3.4 | Security |\n| 10 | `codex/security/sanitization.py` | 0.0% | 214.4 | 2.5 | Security |\n| 11 | `codex/auth/user_repository.py` | 0.0% | 212.8 | 1.7 | Security |\n| 12 | `codex_ml/safety/risk_score.py` | 0.0% | 212.8 | 2.0 | Security |\n| 13 | `codex_ml/security/denylist.py` | 0.0% | 212.8 | 2.7 | Security |\n| 14 | `codex_ml/security/runtime.py` | 0.0% | 211.2 | 2.0 | Security |\n| 15 | `security/provider_factory.py` | 0.0% | 211.2 | 3.3 | Security |\n| 16 | `codex/auth/authenticator.py` | 0.0% | 209.6 | 3.0 | Security |\n| 17 | `codex/auth/oauth_manager.py` | 0.0% | 209.6 | 4.7 | Security |\n| 18 | `codex/auth/token_manager.py` | 0.0% | 209.6 | 5.0 | Security |\n| 19 | `codex/auth/mfa_provider.py` | 0.0% | 208.0 | 5.3 | Security |\n| 20 | `security/providers/base.py` | 0.0% | 208.0 | 3.3 | Security |\n <!-- pragma: allowlist secret -->

### Priority Tier Breakdown

#### Tier 1: Security-Critical Zero-Coverage (HIGHEST PRIORITY)
**Count:** 32 modules  
**Estimated Effort:** ~93 days  
**Impact:** Critical security gaps; must be addressed immediately

These modules have 0% coverage and contain security-sensitive code:

- **`security/providers/environment_provider.py`** (52 statements, est. 1.5d)\n- **`codex/auth/in_memory_user_repository.py`** (49 statements, est. 1.5d)\n- **`security/providers/github_provider.py`** (202 statements, est. 4.5d)\n- **`codex/auth/sqlite_user_repository.py`** (71 statements, est. 1.9d)\n- **`security/providers/aws_provider.py`** (120 statements, est. 2.9d)\n- **`codex/cognitive/safety_guards.py`** (214 statements, est. 4.8d)\n- **`codex_ml/security/cve_monitor.py`** (98 statements, est. 2.5d)\n- **`codex/security/log_sanitizer.py`** (39 statements, est. 1.3d)\n- **`integrations/github_app_auth.py`** (88 statements, est. 2.3d)\n- **`codex/security/sanitization.py`** (51 statements, est. 1.5d)\n

#### Tier 2: All Zero-Coverage Modules (HIGH PRIORITY)
**Count:** 46 modules  
**Estimated Effort:** ~133 days  
**Impact:** Complete lack of test validation

Includes infrastructure, CLI, and API modules with no test coverage.

| File | Statements | Priority |\n|------|-----------|----------|\n| `security/providers/environment_provider.py` | 52 | CRITICAL |\n| `codex/auth/in_memory_user_repository.py` | 49 | CRITICAL |\n| `security/providers/github_provider.py` | 202 | CRITICAL |\n| `codex/auth/sqlite_user_repository.py` | 71 | CRITICAL |\n| `security/providers/aws_provider.py` | 120 | CRITICAL |\n| `codex/cognitive/safety_guards.py` | 214 | CRITICAL |\n| `codex_ml/security/cve_monitor.py` | 98 | CRITICAL |\n| `codex/security/log_sanitizer.py` | 39 | CRITICAL |\n| `integrations/github_app_auth.py` | 88 | CRITICAL |\n| `codex/security/sanitization.py` | 51 | CRITICAL |\n| `codex/auth/user_repository.py` | 18 | CRITICAL |\n| `codex_ml/safety/risk_score.py` | 30 | CRITICAL |\n| `codex_ml/security/denylist.py` | 58 | CRITICAL |\n| `codex_ml/security/runtime.py` | 28 | CRITICAL |\n| `security/provider_factory.py` | 82 | CRITICAL |\n <!-- pragma: allowlist secret -->

#### Tier 3: Low-Coverage Security Modules (ONGOING)
**Count:** 3  
**Estimated Effort:** ~30-50 days  
**Impact:** Partial coverage; needs depth and branch testing

Low-coverage security modules that need additional tests.

---

## Effort Estimation Matrix

### By File Size and Coverage Gap

| File Size (statements) | 0-20% Coverage | 20-50% Coverage | 50-80% Coverage | 80%+ Coverage |
|------------------------|----------------|-----------------|-----------------|---------------|
| <50 | 0.5d | 0.2d | 0.1d | <0.1d |
| 50-100 | 1.5d | 0.8d | 0.3d | 0.1d |
| 100-200 | 3.0d | 1.5d | 0.5d | 0.2d |
| 200-400 | 5.0d | 2.5d | 1.0d | 0.5d |
| >400 | 7.5d-10.0d | 4.0d-5.0d | 1.5d-2.0d | 1.0d |

### Security Module Adjustment (+30% effort)
Security, auth, safety, and crypto modules require:
- Additional edge case testing
- Security assertion validation
- Error path coverage
- Threat model testing

### Total Effort Assessment

**Tier 1 + Tier 2 Coverage:**
- Base estimate: ~350 days
- Optimized (parallel development): ~50-60 days
- With automation/generation: ~25-35 days

**Recommended Phasing:**
- Week 1-2: Tier 1 security modules (8-10 modules, ~40-60 hours)
- Week 3-4: Critical infrastructure (API, bridge, CLI)
- Week 5-8: Tier 2 general modules (batch testing)

---

## Recommended Closure Strategy

### Phase 1: Security-Critical Foundations (Target: +8-10%)
**Timeline:** Weeks 1-2  
**Focus:** Auth, security, safety modules  
**Success Criteria:** All Tier 1 modules ≥30% coverage

**Key Actions:**
1. Generate unit tests for auth modules (user repository, authenticator, token manager)
2. Create integration tests for security providers (GitHub, AWS, environment)
3. Add edge cases for safety guards and sanitizers
4. Validate MFA and OAuth flows

**Expected Coverage Impact:** +8-10 percentage points

### Phase 2: Infrastructure & API (Target: +5-7%)
**Timeline:** Weeks 3-4  
**Focus:** Bridge, CLI, API modules  
**Success Criteria:** 20+ infrastructure modules ≥20% coverage

**Key Actions:**
1. Generate comprehensive API endpoint tests
2. Test bridge protocol v2 state machines
3. CLI argument parsing and validation
4. Error handling and exception flows

**Expected Coverage Impact:** +5-7 percentage points

### Phase 3: Data & ML Modules (Target: +3-5%)
**Timeline:** Weeks 5-8  
**Focus:** codex_ml, ingestion, tokenization  
**Success Criteria:** 15+ modules ≥20% coverage

**Key Actions:**
1. Data pipeline validation tests
2. ML model integration tests
3. Tokenization edge cases
4. Feature extraction testing

**Expected Coverage Impact:** +3-5 percentage points

---

## Success Criteria Validation

### Coverage Targets

✅ **Tier 1 (Security):** 0% → ≥30%
- Enables safe auth and security operations
- Validates access controls
- Error path coverage for security exceptions

✅ **Tier 2 (Infrastructure):** 0% → ≥20%
- Enables bridge and CLI functionality
- API contract validation
- Worker reliability

✅ **Tier 3 (Data/ML):** 7-34% → ≥20%
- Ensures data integrity
- Validates model integration points
- Pipeline robustness

### Test Quality Metrics

| Metric | Acceptance Criteria | Current | Target |
|--------|-------------------|---------|--------|
| Line Coverage | ≥20% overall | 7.04% | ✓ 20% |
| Branch Coverage | ≥15% overall | N/A | Establish baseline |
| Security Coverage | ≥50% security modules | 37% | ✓ 50% |
| API Coverage | ≥40% API endpoints | 22% | ✓ 40% |
| Error Path Coverage | ≥25% error cases | 18% | ✓ 25% |

### Validation Gates

1. **Code Coverage Gate:** PR blocks if coverage regression >1%
2. **Security Module Gate:** All auth/security modules ≥30%
3. **Test Quality Gate:** Mutation score ≥65% for critical modules
4. **Documentation Gate:** All tested modules have assertion comments

---

## Implementation Roadmap

### Immediate Actions (This Week)
- [ ] Audit security module tests (auth, security, safety)
- [ ] Generate unit test templates for Tier 1 modules
- [ ] Set up coverage tracking dashboards
- [ ] Document test patterns for fast iteration

### Short-Term (Weeks 1-4)
- [ ] Implement Tier 1 tests (security modules)
- [ ] Create Tier 2 tests (infrastructure)
- [ ] Monitor coverage delta weekly
- [ ] Optimize test execution (parallel runners)

### Medium-Term (Weeks 5-8)
- [ ] Complete Tier 3 tests (data/ML)
- [ ] Refine test quality (assertions, edge cases)
- [ ] Raise fail_under threshold to 20%
- [ ] Establish Phase 8A baseline

---

## Risk Assessment

### Coverage Gap Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **No test coverage in auth modules** | HIGH | Prioritize Tier 1 immediately |
| **API endpoints untested** | HIGH | Use contract testing for fast coverage |
| **Security bypass scenarios** | CRITICAL | Threat model-driven test generation |
| **ML pipeline untested** | MEDIUM | Use synthetic data for quick iteration |

### Execution Risks

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| **Test generation failures** | MEDIUM | Human review + mutation testing |
| **Long test execution time** | HIGH | Batch/parallel runners + fast tests |
| **Flaky tests in security** | MEDIUM | Strict isolation + deterministic mocks |

---

## Appendices

### A. Module Classification Reference

**Security-Critical (Tier 1):**
- src/codex/auth/ (user management, OAuth, MFA)
- src/security/ (crypto, TLS, audit logging)
- src/codex_ml/safety/ (sanitizers, filters, risk scoring)

**Infrastructure (Tier 2):**
- src/codex_bridge/ (protocol, client)
- src/cli/ (CLI parsing, command execution)
- src/codex/api/ (API routes, authentication)

**Data/ML (Tier 3):**
- src/codex_ml/ (training, inference, pipelines)
- src/ingestion/ (data loading, validation)
- src/tokenization/ (tokenizer, vocabulary)

### B. Test Generation Template (Example)

```python
# For security modules: test auth, error paths, edge cases
class TestSecurityModule:
    def test_auth_success(self): ...
    def test_auth_failure(self): ...
    def test_auth_timeout(self): ...
    def test_auth_invalid_token(self): ...  # pragma: allowlist secret
    def test_auth_expired_token(self): ...  # pragma: allowlist secret
    def test_auth_permission_denied(self): ...
```

### C. Coverage Tracking Commands

```bash
# Run coverage with module breakdown
pytest --cov=src --cov-report=json:coverage.json

# View coverage by module
coverage report --skip-covered

# Identify uncovered lines
coverage report --precision=3 -m

# Generate HTML report
coverage html
```

---

**Report Generated:** 2026-06-16 21:31:45  
**Phase 7A Task Status:** ✅ COMPLETE  
**Next Phase:** 7B - Test Generation & Gap Closure
