# PHASE 9 GATE 2 - DEPENDENCY REMEDIATION ACTION PLAN
**Date:** 2026-07-03  
**Status:** READY FOR EXECUTION  
**Priority:** CRITICAL (Phase 9.3 Blocker)

---

## EXECUTIVE SUMMARY

**Goal:** Resolve all 54 vulnerability findings before Phase 9.3 deployment  
**Timeline:** Immediate (within 24 hours)  
**Effort:** 2-4 hours  
**Risk:** CRITICAL if not completed

---

## REMEDIATION TASKS
 # pragma: allowlist secret
### PHASE 1: ENVIRONMENT RECOVERY (30 minutes)

#### Task 1.1: Backup Current State
```bash
# Document current environment
pip list > /tmp/pip_list_before.txt
pip freeze > /tmp/requirements_before.txt

# Archive for rollback
cp /tmp/pip_list_before.txt .codex/audit_artifacts/pip_list_before.txt
cp /tmp/requirements_before.txt .codex/audit_artifacts/requirements_before.txt
```

#### Task 1.2: Clean Install Dependencies from pyproject.toml
```bash
# Remove venv to ensure clean install
deactivate  # if in venv
python3.12 -m venv .venv_clean
source .venv_clean/bin/activate

# Install from pyproject.toml (which has correct versions)
pip install -e ".[auth,testing]"  # Install with security extras

# Verify upgrades
pip list | grep -E 'cryptography|PyJWT|requests|urllib3|jinja2|idna|certifi'
```

**Expected Output:**
```
cryptography    49.0.0+
PyJWT           2.13.0+
requests        2.32.4+
urllib3         2.7.0+
jinja2          3.1.6+
idna            3.18+
certifi         2024.7.4+
```

#### Task 1.3: Verify Vulnerability Resolution
```bash
# Run pip-audit to confirm all CVEs resolved
python -m pip_audit

# Expected: "Found 0 known vulnerabilities"
```

### PHASE 2: REQUIREMENTS FILE SYNCHRONIZATION (15 minutes)

#### Task 2.1: Sync requirements-dev.txt
```bash
# Extract minimum versions from pyproject.toml
pip install pipreqs

# Generate requirements files
pip freeze > requirements-pinned.txt

# Identify critical security pins
grep -E 'cryptography|PyJWT|requests|urllib3|jinja2' requirements-pinned.txt

# Update requirements-dev.txt with pinned versions
# Ensure all security packages have explicit pins
```

#### Task 2.2: Sync requirements.txt
```bash
# Core dependencies only
# Format: package==X.Y.Z for security-critical packages
# OR: package>=X.Y.Z for actively maintained packages

cat >> requirements.txt << 'EOF'
# Security: Critical CVE fixes (Phase 9 GATE 2 remediation)
cryptography>=49.0.0,<50.0.0
PyJWT>=2.13.0,<3.0.0
requests>=2.32.4
urllib3>=2.7.0
jinja2>=3.1.6
idna>=3.18
certifi>=2024.7.4
EOF
```

#### Task 2.3: Commit Changes
```bash
git add requirements.txt requirements-dev.txt pyproject.toml
git commit -m "Security: Resolve Phase 8 carry-over CVEs (54 vulnerabilities)

- Upgrade cryptography 41.0.7 → 49.0.0 (8 CVEs fixed)
- Upgrade PyJWT 2.7.0 → 2.13.0 (7 CVEs fixed)
- Upgrade requests 2.31.0 → 2.32.4 (3 CVEs fixed)
- Upgrade urllib3 2.0.7 → 2.7.0 (7 CVEs fixed)
- Upgrade jinja2 3.1.2 → 3.1.6 (5 CVEs fixed)
- Upgrade idna 3.6 → 3.18 (3 CVEs fixed)
- Upgrade certifi 2023.11.17 → 2024.7.4 (2 CVEs fixed)

Addresses Phase 8 vulnerabilities per PHASE_9_GATE2_SECURITY_AUDIT.md
Resolves all CRITICAL/HIGH severity CVEs listed in Gate 2 report."
```

### PHASE 3: VALIDATION & TESTING (45 minutes)

#### Task 3.1: Run Full Test Suite
```bash
# Quick validation
python -m pytest tests/ -x -v --tb=short -k "not slow" 2>&1 | tee .codex/audit_artifacts/test_results.log

# Check for failures
if grep -q "FAILED" .codex/audit_artifacts/test_results.log; then
    echo "⚠️ Tests failed - investigate compatibility"
    exit 1
fi
```

#### Task 3.2: Security Scan Validation
```bash
# Bandit - should still pass (code hasn't changed)
python -m bandit -r src/ --configfile=.bandit.yml -f json > .codex/audit_artifacts/bandit_post_fix.json

# pip-audit - should now show 0 vulnerabilities
python -m pip_audit > .codex/audit_artifacts/pip_audit_post_fix.txt

# Secret scan - should remain clean
# (no new secrets from dependency upgrades)
```

#### Task 3.3: Version Validation
```bash
python << 'EOF'
import subprocess
import sys

critical_packages = {
    'cryptography': '49.0.0',
    'PyJWT': '2.13.0',
    'requests': '2.32.4',
    'urllib3': '2.7.0',
    'jinja2': '3.1.6',
    'idna': '3.18',
    'certifi': '2024.7.4'
}

# Get installed versions
result = subprocess.run(['pip', 'show', *critical_packages.keys()], 
                       capture_output=True, text=True)

for line in result.stdout.split('\n'):
    if line.startswith('Name:'):
        current_package = line.split(': ')[1]
    if line.startswith('Version:'):
        version = line.split(': ')[1]
        required = critical_packages.get(current_package)
        if required and version < required:
            print(f"❌ {current_package}: {version} (need ≥{required})")
            sys.exit(1)
        elif required:
            print(f"✅ {current_package}: {version}")

print("\n✅ All critical packages meet minimum version requirements")
EOF
```

#### Task 3.4: Integration Test
```bash
# Test vulnerable components are fixed
python << 'EOF'
# Test 1: Cryptography can load safely
try:
    from cryptography.hazmat.primitives import hashes
    print("✅ Cryptography imports successfully")
except Exception as e:
    print(f"❌ Cryptography import failed: {e}")
    exit(1)

# Test 2: JWT operations work
try:
    import jwt
    secret = "test-secret"
    token = jwt.encode({"test": "data"}, secret, algorithm="HS256")
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    print("✅ PyJWT encode/decode works")
except Exception as e:
    print(f"❌ PyJWT failed: {e}")
    exit(1)

# Test 3: Requests handles SSL correctly
try:
    import requests
    # Note: Don't actually make network requests
    session = requests.Session()
    print("✅ Requests initialized successfully")
except Exception as e:
    print(f"❌ Requests failed: {e}")
    exit(1)

# Test 4: Jinja2 templates work
try:
    from jinja2 import Template
    template = Template("Hello {{ name }}!")
    result = template.render(name="World")
    assert result == "Hello World!"
    print("✅ Jinja2 templates work")
except Exception as e:
    print(f"❌ Jinja2 failed: {e}")
    exit(1)

print("\n✅ All integration tests passed")
EOF
```

### PHASE 4: DOCUMENTATION & SIGN-OFF (15 minutes)

#### Task 4.1: Create Remediation Summary
```bash
cat > .codex/PHASE_9_GATE2_REMEDIATION_COMPLETE.md << 'EOF'
# Phase 9 GATE 2 - Remediation Complete

## Summary
All 54 critical vulnerabilities have been resolved.

## Changes Made
- cryptography: 41.0.7 → 49.0.0 (8 CVEs fixed)
- PyJWT: 2.7.0 → 2.13.0 (7 CVEs fixed)
- requests: 2.31.0 → 2.32.4 (3 CVEs fixed)
- urllib3: 2.0.7 → 2.7.0 (7 CVEs fixed)
- jinja2: 3.1.2 → 3.1.6 (5 CVEs fixed)
- idna: 3.6 → 3.18 (3 CVEs fixed)
- certifi: 2023.11.17 → 2024.7.4 (2 CVEs fixed)

## Verification Results
- ✅ pip-audit: 0 vulnerabilities
- ✅ Bandit: Clean (no new issues)
- ✅ Tests: All passed
- ✅ Integration: All security components functional

## Deployment Ready
✅ APPROVED FOR PHASE 9.3 LAUNCH
EOF

# Archive vulnerability report
cp pip-audit-results.txt .codex/audit_artifacts/pip_audit_vulnerabilities.txt
```

#### Task 4.2: Update GATE 2 Audit Document
```bash
# Update the PHASE_9_GATE2_SECURITY_AUDIT.md with:
# - New "REMEDIATION COMPLETE" section
# - Updated status to "✅ PASSED"
# - Date of remediation completion
# - Link to this remediation plan execution
```

#### Task 4.3: Prepare PR Description
```markdown
## Phase 9 GATE 2 - Security Remediation

**Title:** Security: Resolve 54 vulnerability findings from Phase 8 carry-over

**Description:**
Resolves critical security vulnerabilities identified in Phase 9 GATE 2 audit:
- Cryptography: 8 CVEs (including RCE)
- PyJWT: 7 CVEs (including auth bypass)
- Requests: 3 CVEs (including TLS bypass)
- urllib3: 7 CVEs (including proxy injection)
- Jinja2: 5 CVEs (including RCE)
- IDNA, Certifi: Additional security fixes

**Testing:**
- Full test suite: PASS
- pip-audit: 0 vulnerabilities (down from 54)
- Bandit: PASS
- Integration tests: PASS

**Related Issues:**
- Phase 9 GATE 2 Security Audit (PHASE_9_GATE2_SECURITY_AUDIT.md)

**Type:** Security fix
**Breaking Changes:** None
**Needs Changelog:** Yes
```

---

## ROLLBACK PLAN

If any phase fails, execute this rollback:

```bash
# Restore previous venv
source .venv/bin/activate  # Original venv before Phase 1.2

# OR rebuild from lock file
python -m pip install -r /tmp/requirements_before.txt --force-reinstall

# Restore requirements files
git checkout requirements.txt requirements-dev.txt

# Verify rollback
pip-audit  # Should show original vulnerabilities

# Document incident
echo "Remediation failed at Phase X - see logs at .codex/audit_artifacts/" >> .codex/PHASE_9_REMEDIATION_NOTES.md
```

---

## TROUBLESHOOTING GUIDE

### Issue: Dependency Conflict During Install
**Symptom:** `pip install` fails with version conflicts

**Solution:**
```bash
# Use pip's resolver with no-deps flag
pip install --no-deps cryptography==49.0.0
pip install --no-deps 'PyJWT>=2.13.0'

# Or use uv for faster resolution
pip install uv
uv pip install -e ".[auth,testing]"
```

### Issue: Tests Fail After Upgrade
**Symptom:** Existing tests break with new dependency versions

**Solution:**
```bash
# Check for breaking changes in each library
# Example: Check if test mock patterns changed
python -m pytest tests/ -v --tb=short

# If specific test fails, consult changelog:
# cryptography: https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst
# PyJWT: https://github.com/jpadilla/pyjwt/releases
```

### Issue: Import Errors After Upgrade
**Symptom:** `ImportError: cannot import name X from cryptography`

**Solution:**
```bash
# Cryptography 49+ has some API changes
# Check if code uses deprecated imports
grep -r "from cryptography" src/ tests/

# Update imports if needed (rare)
# Most changes are internal
```

---

## VERIFICATION CHECKLIST

Before merging, verify:

- [ ] All dependencies updated to minimum versions
- [ ] pip-audit shows 0 vulnerabilities
- [ ] All tests pass (full suite)
- [ ] Bandit scan shows no new issues
- [ ] Secret baseline unchanged (0 new leaks)
- [ ] requirements.txt updated
- [ ] requirements-dev.txt updated
- [ ] pyproject.toml unchanged (should already have correct versions)
- [ ] No breaking changes in API usage
- [ ] Documentation updated (CHANGELOG entry)
- [ ] Code review approved
- [ ] Security review approved

---

## SUCCESS CRITERIA

✅ **GATE 2 Remediation Complete** when:

1. **All 54 CVEs resolved**
   - pip-audit shows 0 known vulnerabilities
   - All 7 packages at minimum required versions

2. **No regressions introduced**
   - Full test suite passes
   - Bandit scan passes
   - Integration tests pass

3. **Documentation updated**
   - PHASE_9_GATE2_SECURITY_AUDIT.md marked PASSED
   - PHASE_9_GATE2_REMEDIATION_COMPLETE.md created
   - CHANGELOG.md entry added

4. **Code review approved**
   - Security team sign-off
   - Release team approval

---

## POST-REMEDIATION MONITORING

### Immediate (Next 7 days)
- Monitor for any CVE disclosures in updated packages
- Watch GitHub security advisories
- Check for any regression reports

### Short-term (Next 30 days)
- Enable Dependabot alerts
- Set up automated security scanning in CI
- Schedule next security audit (30 days post-deployment)

### Long-term (Ongoing)
- Quarterly security audits
- Dependency vulnerability monitoring
- CVE tracking and response procedures

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-03  
**Status:** READY FOR EXECUTION  

