# CodeQL Alert Suppressions — PR #5328

**PR**: 5328  
**Branch**: 0D_base_  
**Date**: 2026-07-17T01:06:46Z

## Suppression Policy

Suppressions are applied **ONLY** when:
1. Alert is in test/mutant code (non-production)
2. Alert represents a false positive (secure implementation)
3. Risk is clearly mitigated by design pattern
4. CWE reference justifies the suppression

---

## Test Code Suppressions (40 alerts)

### CWE-327: Use of a Broken Cryptographic Algorithm

**Files**:
- `tests/security/test_cryptography_coverage_wave2a.py`
- `tests/security/test_pyjwt_coverage_wave2a.py`
- `mutants/tests/security/test_cryptography_coverage_wave2a.py`
- `mutants/tests/security/test_pyjwt_coverage_wave2a.py`

**Justification**: Test fixtures intentionally use weak algorithms to test security controls. Not production code.

**Suppression Type**: Test-only, no risk to production security.

---

### CWE-522: Insufficiently Protected Credentials

**Files**:
- `tests/security/` (various auth test mocks)
- `mutants/tests/security/`

**Justification**: Test authentication mocks with intentionally simplified credentials. Mock data only, never used in production.

**Suppression Type**: Test-only mocks, acceptable for testing authentication flows.

---

### CWE-78: Improper Neutralization of Special Elements

**Files**:
- `tests/test_container_smoke.py`
- `mutants/tests/test_container_smoke.py`

**Justification**: Container smoke tests use controlled shell invocations in test harness. Not production code.

**Suppression Type**: Test harness only, acceptable for integration tests.

---

## Production Code Suppressions (0 alerts)

✅ **No suppressions in production code**

All production code follows secure patterns:
- SQL: Parameterized queries
- Secrets: Environment variables
- XSS: HTML escaping
- Deserialization: No pickle on untrusted data
- Paths: Path.resolve() for normalization

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Production Code | 0 | ✅ Secure |
| Test Code | 40 | ⏸️ Suppressed |
| **CRITICAL Vulnerabilities** | 0 | ✅ Remediated |
| **HIGH Vulnerabilities** | 0 | ✅ Remediated |

**Total Suppressions**: 40 (test code only)  
**Production Suppressions**: 0  
**Expected CodeQL Result**: PASS (0 new HIGH severity)

