# PHASE 7 LANE 4: CVE REMEDIATION PLAN
## Dependency Security Updates (Priority Tier)

**Created:** 2026-06-22T13:45Z  
**Authority:** Phase 7 Production Readiness  
**Timeline Target:** 2 weeks (non-blocking)

---

## CRITICAL VULNERABILITIES REMEDIATION

### 1. PyJWT RFC 7515 Compliance Bypass (PYSEC-2026-120)

**Current State:**
```
Package: pyjwt==2.7.0
Severity: HIGH (CVSS: 7.5)
CVE: PYSEC-2026-120
```

**Issue Summary:**
PyJWT fails to validate the `crit` (Critical) Header Parameter per RFC 7515 §4.1.11. This allows attackers to include unknown critical extensions that should cause token rejection but are silently ignored instead.

**Affected Code Pattern:**
```python
# Current vulnerable behavior:
import jwt
token = "******"
decoded = jwt.decode(token, secret, algorithms=["HS256"])  # ACCEPTS despite unknown crit
```

**Fix:**
```bash
pip install --upgrade pyjwt==2.13.0
```

**Verification:**
```bash
# After upgrade, verify RFC compliance:
python -c "import jwt; print(jwt.__version__)"  # Should be 2.13.0+
```

**Testing Required:**
- [ ] Unit tests for crit header validation
- [ ] Integration tests with token validation
- [ ] Regression tests on existing token flows

**Estimated Effort:** 4 hours (including testing)

---

### 2. PyJWT Algorithm Confusion Attack (PYSEC-2026-179)

**Current State:**
```
Package: pyjwt==2.7.0
Severity: HIGH (CVSS: 6.5)
CVE: PYSEC-2026-179
```

**Issue Summary:**
When a verifier supports both symmetric (HS256) and asymmetric (RS256) algorithms, an attacker can specify HS256 in the token header and use the issuer's public key as the HMAC secret, effectively forging tokens.

**Vulnerable Pattern:**
```python
# VULNERABLE: Mixing algorithm families
import jwt

issuer_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""

# Attacker-crafted token with HS256 + issuer's public key as secret
def verify_token(token):
    return jwt.decode(
        token,
        key=issuer_public_key,  # Public key used as secret
        algorithms=["HS256", "RS256"]  # MISTAKE: mixing symmetric + asymmetric
    )
```

**Fix:**
```python
# FIXED: Separate verification by expected algorithm
def verify_token_rs256(token):
    """Only RS256 verification"""
    return jwt.decode(
        token,
        key=issuer_public_key,
        algorithms=["RS256"]  # ONLY asymmetric
    )

def verify_token_symmetric(token, symmetric_key):
    """Symmetric verification with separate key"""
    return jwt.decode(
        token,
        key=symmetric_key,  # Separate, non-public key
        algorithms=["HS256"]
    )
```

**Upgrade Path:**
```bash
pip install --upgrade pyjwt==2.13.0
```

**Code Review Checklist:**
- [ ] Audit all jwt.decode() calls for algorithm mixing
- [ ] Ensure asymmetric algorithms only use public keys in documented contexts
- [ ] Add algorithm separation tests
- [ ] Document JWT verification best practices

**Affected Code Locations:**
```
src/auth/*.py                    (search for jwt.decode with mixed algorithms)
src/security/token_verification.py  (primary JWT verification)
tests/security/test_jwt*.py      (test all decode patterns)
```

**Estimated Effort:** 6 hours (code review + fixes + tests)

---

### 3. Wheel Path Traversal (CVE-2026-24049)

**Current State:**
```
Package: wheel==0.42.0
Severity: HIGH (CVSS: 7.2)
CVE: CVE-2026-24049
```

**Issue Summary:**
The wheel package's unpack function allows attackers to craft malicious wheel files that traverse outside the extraction directory using `../` paths, potentially modifying system file permissions.

**Attack Vector:**
```python
# Attacker crafts malicious wheel with:
# - Filename: "../../etc/passwd"
# - Permissions: 0o777 (world-writable)
# When unpacked, unpack() blindly applies chmod to the traversed path
```

**Fix:**
```bash
pip install --upgrade wheel==0.46.2
```

**Import Verification:**
```bash
# Ensure no direct setuptools._vendor.wheel.cli.unpack imports
grep -r "from setuptools._vendor.wheel" src/
grep -r "from wheel.cli.unpack import unpack" src/
```

**Estimated Effort:** 2 hours (verification + minimal code changes)

---

### 4. urllib3 Multiple Vulnerabilities (6 CVEs)

**Current State:**
```
Package: urllib3==2.0.7
Vulnerabilities: 6 (proxy bypass, redirect issues, HTTPS bypass)
Recommended: urllib3==2.7.0+
```

**Key Vulnerabilities:**
- CVE-2024-37891: Proxy authentication bypass
- CVE-2025-50181: Redirect following security issue

**Fix:**
```bash
pip install --upgrade urllib3==2.7.0
```

**Compatibility Check:**
```bash
# urllib3 2.7.0 is a minor version bump (backward compatible)
pip install requests==2.31.0  # Already compatible with urllib3 2.7.0+
```

**Estimated Effort:** 1 hour (dependency upgrade + integration test)

---

### 5. Jinja2 Template Injection & Sandbox Escape (5 CVEs)

**Current State:**
```
Package: jinja2~3.1.6
CVE-2024-56326: Sandbox escape via template injection
Other CVEs: Template expression handling
```

**Fix:**
```bash
# Verify current version and upgrade if needed
pip show jinja2 | grep Version
pip install --upgrade "jinja2>=3.1.6"
```

**Security Review Required:**
- [ ] Audit all template rendering with user input
- [ ] Ensure autoescape is enabled for all HTML templates
- [ ] Review sandbox restrictions on custom filters
- [ ] Test RCE prevention scenarios

**Estimated Effort:** 3 hours (code audit + tests)

---

## UNIFIED REMEDIATION SCHEDULE

### Week 1: Phase 1 (Immediate)
```
Priority: P1 (PyJWT + urllib3)
Duration: 3 days
Tasks:
  [ ] Create feature branch: feature/security-dep-updates-phase1
  [ ] Update requirements.txt:
      - pyjwt: 2.7.0 → 2.13.0
      - urllib3: 2.0.7 → 2.7.0
  [ ] Run full test suite
  [ ] Security regression tests
  [ ] Code review by security team
  [ ] Merge to main branch
```

### Week 1-2: Phase 2 (High Priority)
```
Priority: P2 (wheel + jinja2)
Duration: 3 days
Tasks:
  [ ] Create feature branch: feature/security-dep-updates-phase2
  [ ] Update requirements.txt:
      - wheel: 0.42.0 → 0.46.2
      - jinja2: ~3.1.6 → verify/upgrade
  [ ] Security-focused code review
  [ ] Template injection testing
  [ ] Merge to main branch
```

### Week 2: Phase 3 (Integration)
```
Priority: P3 (Validation)
Duration: 2 days
Tasks:
  [ ] Full security audit post-upgrades
  [ ] Re-run pip-audit (expect <5 CVEs max)
  [ ] Performance regression testing
  [ ] Release notes documentation
```

---

## UPGRADE IMPLEMENTATION GUIDE

### Step 1: Dependency Update

**File: requirements.txt**

```diff
- pyjwt==2.7.0
+ pyjwt==2.13.0

- urllib3==2.0.7
+ urllib3==2.7.0

- wheel==0.42.0
+ wheel==0.46.2
```

**File: pyproject.toml** (if using)
```toml
[project]
dependencies = [
    "pyjwt>=2.13.0",          # RFC 7515 compliance
    "urllib3>=2.7.0",          # Proxy/redirect fixes
    "wheel>=0.46.2",           # Path traversal fix
    # ... rest of dependencies
]
```

### Step 2: Test Execution

```bash
# Create clean environment
python -m venv test_env
source test_env/bin/activate

# Install updated dependencies
pip install -r requirements.txt

# Run security tests
pytest tests/security/ -v

# Run full test suite
pytest tests/ -x

# Re-run vulnerability audit
pip-audit --desc > audit_post_update.txt
```

### Step 3: Verification

```bash
# Check versions
python -c "import jwt; print(f'PyJWT: {jwt.__version__}')"
python -c "import urllib3; print(f'urllib3: {urllib3.__version__}')"
python -c "import wheel; print(f'wheel: {wheel.__version__}')"

# Verify no new issues
pip-audit
```

### Step 4: Documentation

**CHANGELOG.md Entry:**
```markdown
## Security Updates (2026-06-22)

### Dependency Upgrades
- **pyjwt**: 2.7.0 → 2.13.0 (fixes RFC 7515 compliance bypass, algorithm confusion)
- **urllib3**: 2.0.7 → 2.7.0 (fixes proxy/redirect security issues)
- **wheel**: 0.42.0 → 0.46.2 (fixes path traversal vulnerability)
- **jinja2**: Verified ≥3.1.6 (sandbox escape patches)

### Security Impact
- Fixes 14 HIGH severity vulnerabilities
- Maintains backward compatibility
- No API changes to public interface
```

---

## TESTING STRATEGY

### Unit Tests

**JWT Verification Tests** (new):
```python
def test_jwt_crit_header_validation():
    """RFC 7515: Reject unknown critical headers"""
    token_with_unknown_crit = create_token_with_crit(["x-custom"])
    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(token_with_unknown_crit, secret, algorithms=["HS256"])

def test_jwt_algorithm_confusion_prevention():
    """Prevent using public key as HMAC secret"""
    public_key = load_rsa_public_key()
    attacker_token = create_forged_token_with_hs256(public_key)
    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(attacker_token, public_key, algorithms=["HS256", "RS256"])

def test_uri3_redirect_validation():
    """urllib3: Validate redirect hosts"""
    # Tests for proxy bypass and redirect following
```

### Integration Tests

```python
def test_authentication_flow_with_new_pyjwt():
    """Full auth flow works with PyJWT 2.13.0"""
    # Login → token generation → token validation

def test_api_requests_with_new_urllib3():
    """API calls work with urllib3 2.7.0"""
    # HTTP requests, redirects, proxy handling
```

### Regression Tests

```bash
# Ensure existing functionality preserved
pytest tests/security/test_jwt_validation.py
pytest tests/security/test_api_calls.py
pytest tests/security/test_file_handling.py
```

---

## ROLLBACK PLAN

If issues arise post-upgrade:

```bash
# Immediate rollback
pip install -r requirements-stable.txt

# Analyze issue
pip-audit
pytest tests/ -v

# Document issue and escalate to security team
```

**Rollback Timeline:** < 30 minutes

---

## SIGN-OFF CHECKLIST

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Security regression tests pass
- [ ] pip-audit shows ≤5 remaining CVEs (acceptable level)
- [ ] Code review approved by security team
- [ ] Documentation updated
- [ ] Performance benchmarks unchanged
- [ ] Release notes prepared
- [ ] Team notified of changes

---

## SUCCESS CRITERIA

**Post-Upgrade Metrics:**
- ✅ PyJWT HIGH CVEs: 8 → 0
- ✅ urllib3 HIGH CVEs: 6 → 0
- ✅ wheel HIGH CVEs: 1 → 0
- ✅ jinja2 HIGH CVEs: 5 → 0
- ✅ Total project CVEs: 14 → <5
- ✅ No new security regressions
- ✅ All tests passing

---

## CONTACT & ESCALATION

**Security Team Lead:** @security-team  
**Release Manager:** @release-mgr  
**Emergency Escalation:** @mbaetiong (COPILOT_AGENT_AUTH_ENABLED=true)

---

**Document ID:** REMEDIATION_PLAN_SECURITY_UPDATES_2026-06-22  
**Status:** APPROVED FOR EXECUTION  
**Expected Completion:** 2026-07-06
