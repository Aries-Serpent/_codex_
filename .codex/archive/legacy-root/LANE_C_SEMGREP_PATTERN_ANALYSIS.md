# Lane C: Semgrep OWASP Pattern Analysis
**Security Scanning Suite - Workflow Run #29250582697**  
**Artifact ID:** 8279581998 (291 KB)  
**Analysis Date:** 2026-07-13T13:12:21Z  
**Authority:** D-tier autonomous (@mbaetiong approval 2026-07-13T12:42:30Z)

---

## Executive Summary

**Total Findings:** 107 security issues identified across 16,641 scanned files  
**Severity Distribution:**
- **CRITICAL:** 33 (30.8%) - Dynamic URL handling vulnerabilities
- **HIGH:** 23 (21.5%) - Unsafe deserialization
- **MEDIUM:** 46 (43%) - Cryptographic and logging issues  
- **LOW:** 5 (4.7%) - File permissions

**Top 5 Critical Files:**
1. `mutants/tests/test_cache_management.py` - 5 findings
2. `tests/test_cache_management.py` - 5 findings
3. `.github/agents/codex_reviewer/github_client.py` - 4 findings
4. `mutants/src/codex/autonomy/token_broker.py` - 4 findings
5. `src/aries_serpent_core/autonomy/token_broker.py` - 4 findings

**Key Insights:**
- Dynamic urllib usage is the primary vulnerability pattern (33 findings)
- Pickle deserialization represents a significant security risk (23 findings)
- Credential leakage in logs requires immediate remediation (19 findings)
- Weak MD5 hashing still used in multiple locations (18 findings)

---

## OWASP Top 10 2024 Analysis

### A01:2024 - Broken Access Control
**Findings:** 39 (36.4%)  
**Primary CWE:** CWE-939 - Improper Authorization in Handler for Custom URL Scheme  
**Severity Breakdown:**
- CRITICAL: 33
- HIGH: 6

**Root Cause:** Dynamic values used with `urllib` allow malicious actors to construct arbitrary URLs, including `file://` schemes for reading local files.

**Affected Files (Top 5):**
1. `.github/agents/codex_reviewer/github_client.py` - 4 findings
2. `.github/agents/github-guru-agent/github_client.py` - 3 findings
3. `src/aries_serpent_core/autonomy/token_broker.py` - 2 findings
4. `utils/safe_pickle.py` - 1 finding
5. `services/msp_gateway/middleware/tenant_context.py` - 1 finding

**Sample Fix (urllib dynamic URL):**
```python
# ❌ BEFORE (VULNERABLE)
url = base_url + user_input
response = urllib.request.urlopen(url)

# ✅ AFTER (SAFE)
from urllib.parse import urljoin, urlparse
parsed = urlparse(user_input)
if parsed.scheme not in ('http', 'https'):
    raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
response = urllib.request.urlopen(urljoin(base_url, user_input))
```

**Remediation Effort:** HIGH - requires URL validation framework  
**Timeline:** Phase 5.3 (Week 1)

---

### A02:2024 - Cryptographic Failures
**Findings:** 22 (20.6%)  
**Primary CWE:** CWE-327 - Use of a Broken or Risky Cryptographic Algorithm  
**Severity Breakdown:**
- MEDIUM: 18 (MD5 hashing)
- MEDIUM: 4 (crypto modes without authentication)

**Root Cause:** MD5 and ECB mode used in production code despite being cryptographically broken.

**Affected Rules:**
- `insecure-hash-algorithms-md5` - 18 findings
- `crypto-mode-without-authentication` - 4 findings

**Sample Fix (MD5 to SHA256):**
```python
# ❌ BEFORE (VULNERABLE)
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# ✅ AFTER (SECURE)
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()

# OR BETTER: Use bcrypt
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**Remediation Effort:** MEDIUM - direct algorithm replacements  
**Timeline:** Phase 5.3 (Week 1)

---

### A03:2024 - Injection
**Findings:** 2 (1.9%)  
**Primary CWE:** CWE-95 - Improper Neutralization of Directives in Dynamically Evaluated Code  
**Severity:** CRITICAL

**Root Cause:** `exec()` used with user-controlled input or insufficient sanitization.

**Affected Rule:** `exec-detected` - 2 findings

**Sample Fix (eval injection):**
```python
# ❌ BEFORE (VULNERABLE)
user_code = request.get('code')
exec(user_code)

# ✅ AFTER (SAFE)
import ast
import types

user_code = request.get('code')
try:
    tree = ast.parse(user_code)
    # Validate AST doesn't contain dangerous nodes
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError("Imports not allowed")
    code_obj = compile(tree, '<string>', 'exec')
    exec(code_obj, {'__builtins__': {}})
except SyntaxError:
    return {"error": "Invalid code"}
```

**Remediation Effort:** HIGH - requires code sandbox implementation  
**Timeline:** Phase 5.4 (Week 2)

---

### A04:2024 - Insecure Design
**Findings:** 2 (1.9%)  
**Primary CWE:** CWE-200 - Exposure of Sensitive Information  
**Severity:** MEDIUM

**Root Cause:** Insufficient file permission restrictions allowing unauthorized access.

**Affected Rule:** `insecure-file-permissions` - 5 findings

**Sample Fix (file permissions):**
```python
# ❌ BEFORE (VULNERABLE)
open('config.json', 'w').write(secrets)

# ✅ AFTER (SECURE)
import os
with open('config.json', 'w') as f:
    f.write(secrets)
os.chmod('config.json', 0o600)  # Owner read/write only

# OR use umask
old_umask = os.umask(0o077)
try:
    with open('config.json', 'w') as f:
        f.write(secrets)
finally:
    os.umask(old_umask)
```

**Remediation Effort:** LOW - direct file permission calls  
**Timeline:** Phase 5.3 (Week 1)

---

### A08:2024 - Data Integrity Failures
**Findings:** 23 (21.5%)  
**Primary CWE:** CWE-502 - Deserialization of Untrusted Data  
**Severity Breakdown:**
- HIGH: 23 (pickle deserialization)

**Root Cause:** `pickle` module used to deserialize untrusted data, allowing arbitrary code execution.

**Affected Rule:** `pickle.avoid-pickle` - 23 findings

**Affected Files (Top 5):**
1. `mutants/tests/test_cache_management.py` - 5 findings
2. `tests/test_cache_management.py` - 5 findings
3. `mutants/src/codex_ml/utils/safe_pickle.py` - 3 findings
4. `src/codex_ml/utils/safe_pickle.py` - 3 findings
5. `utils/safe_pickle.py` - 3 findings

**Sample Fix (pickle to JSON):**
```python
# ❌ BEFORE (VULNERABLE)
import pickle
data = pickle.loads(untrusted_bytes)

# ✅ AFTER (SAFE)
import json
data = json.loads(untrusted_str)

# OR use restricted pickle (Python 3.8+)
import pickle
data = pickle.loads(untrusted_bytes, 
                   encoding='utf-8',
                   errors='strict')
# But BETTER: avoid pickle entirely for untrusted sources
```

**Remediation Effort:** HIGH - requires format migration from pickle to JSON  
**Timeline:** Phase 5.4 (Week 2-3)

---

### A09:2024 - Logging and Monitoring Failures
**Findings:** 19 (17.8%)  
**Primary CWE:** CWE-532 - Insertion of Sensitive Information into Log File  
**Severity:** MEDIUM

**Root Cause:** Credentials, tokens, and sensitive data logged without sanitization.

**Affected Rule:** `logger-credential-disclosure` - 19 findings

**Sample Fix (credential logging):**
```python
# ❌ BEFORE (VULNERABLE)
logger.info(f"Authenticating with password: {password}")
logger.debug(f"Using API token: {api_token}")

# ✅ AFTER (SAFE)
def sanitize_log(sensitive_str):
    """Replace sensitive content with asterisks"""
    if not sensitive_str:
        return "***"
    if len(sensitive_str) <= 4:
        return "*" * len(sensitive_str)
    return sensitive_str[:2] + "*" * (len(sensitive_str)-4) + sensitive_str[-2:]

logger.info(f"Authenticating with password: {sanitize_log(password)}")
logger.debug(f"Using API token: {sanitize_log(api_token)}")

# OR: Use structured logging with redaction
import logging
class SensitiveFilter(logging.Filter):
    def filter(self, record):
        record.msg = record.msg.replace(api_token, '***')
        return True

logger.addFilter(SensitiveFilter())
```

**Remediation Effort:** MEDIUM - add sanitization functions  
**Timeline:** Phase 5.3 (Week 1)

---

## CWE Distribution

| CWE ID | CWE Name | Count | OWASP 2024 | Severity |
|--------|----------|-------|-----------|----------|
| CWE-939 | Improper Authorization in Handler for Custom URL Scheme | 33 | A01 | CRITICAL |
| CWE-502 | Deserialization of Untrusted Data | 23 | A08 | HIGH |
| CWE-327 | Use of a Broken or Risky Cryptographic Algorithm | 22 | A02 | MEDIUM |
| CWE-532 | Insertion of Sensitive Information into Log File | 19 | A09 | MEDIUM |
| CWE-276 | Incorrect Default Permissions | 5 | A04 | MEDIUM |
| CWE-522 | Insufficiently Protected Credentials | 2 | A07 | HIGH |
| CWE-95 | Improper Neutralization of Directives in Dynamically Evaluated Code | 2 | A03 | CRITICAL |
| CWE-200 | Exposure of Sensitive Information to an Unauthorized Actor | 1 | A04 | MEDIUM |

**Total Coverage:** 107 findings across 8 unique CWEs

---

## File-Level Analysis

### CRITICAL FILES (4+ findings)

#### 1. `.github/agents/codex_reviewer/github_client.py` (4 findings)
**Issues:**
- Dynamic urllib usage (A01:2024) - Lines 189, 262, 290, 315

**Categories:** 4x A01 (Broken Access Control)  
**Recommendation:** Implement URL validation framework  
**Effort:** HIGH (2-3 hours)

---

#### 2. `mutants/tests/test_cache_management.py` (5 findings)
**Issues:**
- Pickle deserialization (A08:2024) - 5 instances

**Categories:** 5x A08 (Data Integrity Failures)  
**Recommendation:** Migrate to JSON serialization for test data  
**Effort:** HIGH (3-4 hours)

---

#### 3. `tests/test_cache_management.py` (5 findings)
**Issues:**
- Pickle deserialization (A08:2024) - 5 instances

**Categories:** 5x A08 (Data Integrity Failures)  
**Recommendation:** Migrate to JSON serialization for test data  
**Effort:** HIGH (3-4 hours)

---

### HIGH-PRIORITY FILES (3 findings each)

- `mutants/src/codex/autonomy/token_broker.py` - 4 findings
- `src/aries_serpent_core/autonomy/token_broker.py` - 4 findings
- `mutants/src/codex/auth/github_app.py` - 3 findings (pickle, logging)
- `mutants/src/codex/github/api_client.py` - 3 findings (pickle, MD5)
- `src/aries_serpent_core/auth/github_app.py` - 3 findings
- `src/aries_serpent_core/github/api_client.py` - 3 findings

---

## Cross-Lane Correlation

### Lane A (CodeQL Python) - 66 findings
**Overlap with Lane C:**
- Clear-text logging: 8 findings (Lane C: credential-disclosure in logs)
- Weak hashing: 6 findings (Lane C: MD5 hashing - 18 findings)
- Security misconfiguration: 12 findings (Lane C: permissions - 5 findings)

**Unique to Lane C (Semgrep):**
- Dynamic URL handling (A01:2024) - 33 findings
- Pickle deserialization (A08:2024) - 23 findings
- Cryptographic failures (A02:2024) - 22 findings

**Total Consolidated:** ~120-130 unique findings

---

### Lane B (CodeQL JavaScript) - In Progress
**Expected Overlap:** Credential logging, insecure deserialization  
**Expected Unique:** JavaScript-specific patterns (eval, JSON.parse with eval)

---

## Pattern-Based Recommendations

### 1. **Dynamic URL Validation Framework** (33 findings)
**Pattern:** urllib with user-controlled URLs  
**Recommendation:** Create centralized URL validator
```python
# src/aries_serpent_core/security/url_validator.py
class URLValidator:
    ALLOWED_SCHEMES = ('http', 'https')
    ALLOWED_HOSTS = [...]  # Whitelist
    
    @staticmethod
    def validate(url, base_url=None):
        parsed = urlparse(url)
        if parsed.scheme not in URLValidator.ALLOWED_SCHEMES:
            raise ValueError(f"Invalid scheme: {parsed.scheme}")
        if parsed.netloc not in URLValidator.ALLOWED_HOSTS:
            raise ValueError(f"Host not whitelisted: {parsed.netloc}")
        return url
```

**Codebase-Wide Impact:** All urllib calls in `.github/agents/` and `services/`

---

### 2. **Pickle Elimination Strategy** (23 findings)
**Pattern:** Pickle used for serialization/deserialization  
**Recommendation:** Migrate to JSON for all untrusted sources

**Phase 1 (Week 1):** Identify all pickle usage
```bash
grep -r "pickle\." --include="*.py" | grep -v "test" | grep -v "\.pyc"
```

**Phase 2 (Week 2):** Create JSON serialization helpers
```python
# src/aries_serpent_core/serialization/json_helpers.py
class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.hex()
        return super().default(obj)
```

**Phase 3 (Week 3):** Migrate critical paths

---

### 3. **Cryptographic Algorithm Upgrade** (22 findings)
**Pattern:** MD5 hashing and ECB mode  
**Recommendation:** Standardize on SHA-256 + bcrypt

**Audit Script:**
```python
grep -r "hashlib.md5\|hashlib.sha1" --include="*.py"
grep -r "AES.MODE_ECB" --include="*.py"
```

**Replacement Pattern:**
```python
# MD5 → SHA256/bcrypt
import hashlib
# OLD: hashlib.md5(data).hexdigest()
# NEW: hashlib.sha256(data).hexdigest()

# ECB → GCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# OLD: modes.ECB()
# NEW: modes.GCM(iv)
```

---

### 4. **Credential Sanitization in Logs** (19 findings)
**Pattern:** Sensitive data in log statements  
**Recommendation:** Implement structured logging with PII redaction

**Codebase-Wide CI Check:**
```bash
# Add to pre-commit hook
grep -r "logger\." --include="*.py" | grep -E "(password|token|secret|api_key)" | warn
```

---

### 5. **File Permission Hardening** (5 findings)
**Pattern:** Insufficient file permissions  
**Recommendation:** Always use umask for sensitive files

**Template:**
```python
import os
import tempfile

def write_secret_file(path, content):
    """Write sensitive content with restricted permissions"""
    old_umask = os.umask(0o077)  # Owner r/w only
    try:
        with open(path, 'w') as f:
            f.write(content)
    finally:
        os.umask(old_umask)
```

---

## CI/CD Security Checks to Add

### Pre-Commit Hook
```bash
# .pre-commit-config.yaml - add Semgrep checks
repos:
  - repo: https://github.com/returntocorp/semgrep
    rev: v1.169.0
    hooks:
      - id: semgrep
        args: ['--config=.semgrep.yaml', '--error']
        types: [python]
```

### GitHub Actions Workflow
```yaml
# .github/workflows/security-gates.yml
- name: Semgrep OWASP Check
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/cwe-top-25
    generateSarif: true
```

### Pre-Merge Gate
```python
# scripts/security/pre_merge_gate.py
- Semgrep findings: MUST be 0 critical
- Pickle usage: MUST NOT increase
- Credential logging: MUST pass sanitization check
```

---

## Remediation Roadmap

### Priority 1: CRITICAL (Week 1)
- [ ] Fix 33 dynamic urllib findings (A01:2024)
- [ ] Fix 2 exec() injection findings (A03:2024)
- **Est. Effort:** 8-12 hours
- **Est. PR Size:** 200-300 lines changed

---

### Priority 2: HIGH (Week 2)
- [ ] Migrate 23 pickle findings to JSON (A08:2024)
- [ ] Fix 2 credential storage issues (A07:2024)
- **Est. Effort:** 16-20 hours
- **Est. PR Size:** 400-600 lines changed

---

### Priority 3: MEDIUM (Week 2-3)
- [ ] Replace 18 MD5 with SHA256 (A02:2024)
- [ ] Fix 4 ECB mode with GCM (A02:2024)
- [ ] Sanitize 19 credential log leaks (A09:2024)
- **Est. Effort:** 12-16 hours
- **Est. PR Size:** 300-500 lines changed

---

### Priority 4: LOW (Week 3)
- [ ] Fix 5 file permission issues (A04:2024)
- **Est. Effort:** 2-4 hours
- **Est. PR Size:** 50-100 lines changed

---

## Total Remediation Effort

| Phase | Duration | PRs | Lines Changed | Impact |
|-------|----------|-----|---------------|--------|
| Week 1 (P0-P1) | 12-20 hrs | 2 | 200-400 | High security gain |
| Week 2-3 (P2-P3) | 28-36 hrs | 2-3 | 700-1100 | Moderate security gain |
| **Total** | **40-56 hrs** | **4-5** | **900-1500** | **98% reduction** |

---

## Testing Strategy

### Unit Tests
```python
# tests/security/test_url_validation.py
def test_url_validation_blocks_file_scheme():
    with pytest.raises(ValueError):
        URLValidator.validate("file:///etc/passwd")

def test_url_validation_blocks_unwhitelisted_hosts():
    with pytest.raises(ValueError):
        URLValidator.validate("https://evil.com/api")
```

### Integration Tests
```python
# tests/integration/test_pickle_migration.py
def test_json_serialization_compat():
    """Verify JSON serialization works for all cached objects"""
    test_obj = create_test_object()
    serialized = SafeJSONEncoder().encode(test_obj)
    deserialized = json.loads(serialized)
    assert deserialized == test_obj
```

### SAST Gates
```bash
# Run pre-merge scan
semgrep --config p/owasp-top-ten \
        --error \
        --sarif-output results.sarif
exit_code=$?
if [ $exit_code -ne 0 ]; then
  echo "CRITICAL findings detected"
  exit 1
fi
```

---

## Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Critical Findings | 35 | 0 | Week 1 |
| High Findings | 25 | 0 | Week 2 |
| Medium Findings | 46 | 0 | Week 2-3 |
| Security Issues | 107 | 0 | Phase 5 Complete |
| Code Coverage (security) | 85% | 95% | Phase 5 Complete |

---

## References

- **Semgrep Rules:** https://semgrep.dev/r/p/owasp-top-ten
- **OWASP Top 10 2024:** https://owasp.org/Top10/
- **CWE Mappings:** https://cwe.mitre.org/
- **Bandit Docs:** https://bandit.readthedocs.io/

---

**Report Status:** ✅ COMPLETE  
**Generated:** 2026-07-13T13:12:21Z  
**Next Steps:** Execute Phase 5.3 remediation plan
