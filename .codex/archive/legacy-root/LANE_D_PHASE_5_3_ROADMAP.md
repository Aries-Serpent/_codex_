# Lane D: Phase 5.3 Implementation Roadmap

**Document Version:** 1.0  
**Generated:** 2026-07-13T13:14:45Z  
**Authority:** D-tier autonomous  
**Timeline:** 3 weeks (21 days)  
**Total Effort:** 46.5 hours  
**Wall Time:** 18-23 hours (with parallelization)

---

## PHASE 5.3 OVERVIEW

### Objectives
1. Remediate 69 CRITICAL findings
2. Resolve 51 HIGH findings
3. Address 155 MEDIUM findings
4. Document 42 LOW findings for automation

### Success Criteria
- ✅ All CRITICAL findings fixed and tested
- ✅ All HIGH findings fixed and verified
- ✅ MEDIUM findings resolved or scheduled
- ✅ Code passing security gates (CodeQL, Semgrep)
- ✅ 100% test coverage for remediated code
- ✅ Documentation updated

### Risk Level During Implementation
- **Week 1:** 🔴 HIGH (CRITICAL issues being fixed)
- **Week 2:** 🟠 MEDIUM (HIGH issues being fixed)
- **Week 3:** 🟡 LOW (MEDIUM issues being fixed)
- **After Phase 5.3:** 🟢 LOW-MEDIUM (residual non-critical items)

---

## WEEK 1: CRITICAL ISSUES (Days 1-7)

**Deliverable Goal:** Zero CRITICAL findings  
**Estimated Effort:** 17.5 hours (~2.5 hours/day)  
**Wall Time:** 4-5 hours (parallel tracks)

### Monday-Tuesday: Secret Logging & Token Masking (Track 1)

**Objective:** Remove all clear-text sensitive data logging  
**Effort:** 3-4 hours  
**Files:** 18 files

#### Step 1: Create Masking Utility (0.5h)
- Create: `src/security/token_masking.py`
- Implement: `mask_token()`, `mask_secret()`, `mask_credentials()`
- Add unit tests in `tests/security/test_token_masking.py`

#### Step 2: Identify All Logging Sites (1h)
```bash
grep -r "logger\.\|print\(" --include="*.py" scripts/ .github/ | \
  grep -E "(secret|token|password|key|credential)" | tee /tmp/logging_audit.txt
```

#### Step 3: Apply Masking (2-3h)
- **File 1:** `scripts/decode_workflow_secrets.py` (7 instances)
  - Lines: 166, 168, 170, 172
  - Fix: Replace `print(secret)` with masked version
  
- **File 2:** `.github/agents/admin-automation-agent/src/agent.py` (4 instances)
  - Fix: Wrap token logging with masking
  
- **Files 3-18:** Apply same pattern to remaining files

**Testing:**
- Unit tests for masking function (100% code paths)
- Integration test: Run affected scripts, verify no secrets in logs
- Pre-commit: Add hook to detect unmasked secrets

**Verification Checklist:**
- [ ] No plain tokens in logs from test runs
- [ ] All instances of logger.info/debug checked
- [ ] Print statements for secrets removed
- [ ] Tests pass

---

### Wednesday-Thursday: Dynamic URL Validation Framework (Track 2)

**Objective:** Prevent arbitrary URL scheme attacks  
**Effort:** 4-5 hours  
**Files:** 10+ files

#### Step 1: Create URL Validator (1.5h)
- Create: `src/security/url_validator.py`
- Implement class:
  ```python
  class URLValidator:
      ALLOWED_SCHEMES = ('http', 'https')
      ALLOWED_HOSTS = [whitelist]  # Configure per service
      
      @staticmethod
      def validate(url, base_url=None):
          parsed = urlparse(url)
          if parsed.scheme not in URLValidator.ALLOWED_SCHEMES:
              raise ValueError(f"Invalid scheme: {parsed.scheme}")
          # Additional checks for host, path...
          return url
  ```

#### Step 2: Identify All urllib Calls (1h)
```bash
grep -r "urllib\|requests.get\|requests.post" --include="*.py" \
  .github/agents/ src/ | tee /tmp/urllib_audit.txt
```

#### Step 3: Apply URL Validation (2-3h)
- **File 1:** `.github/agents/codex_reviewer/github_client.py` (4 instances)
  - Lines: 189, 262, 290, 315
  - Pattern: Wrap all urllib calls with URLValidator.validate()
  
- **File 2:** `.github/agents/github-guru-agent/github_client.py` (3 instances)
  
- **Files 3-10:** Apply same pattern

**Testing:**
- Unit tests for URL validation (allow good, reject bad)
  ```python
  def test_reject_file_scheme():
      with pytest.raises(ValueError):
          URLValidator.validate("file:///etc/passwd")
  
  def test_reject_unwhitelisted():
      with pytest.raises(ValueError):
          URLValidator.validate("https://attacker.com")
  
  def test_allow_valid_urls():
      assert URLValidator.validate("https://github.com/api") is not None
  ```

**Verification Checklist:**
- [ ] file:// scheme blocked
- [ ] gopher://, ftp:// schemes blocked
- [ ] Unwhitelisted hosts blocked
- [ ] Valid URLs pass
- [ ] Tests pass

---

### Thursday-Friday: Exec/Code Injection Fixes (Track 3)

**Objective:** Eliminate arbitrary code execution  
**Effort:** 3-4 hours  
**Files:** 2 files

#### Step 1: Audit exec() Usage (0.5h)
```bash
grep -r "exec(\|eval(\|compile(" --include="*.py" | grep -v "test" | grep -v "\.pyc"
```

#### Step 2: Implement Code Sandbox (2-3h)
Option A: Use RestrictedPython (if available)
Option B: Use AST parsing with whitelist

```python
import ast

def safe_exec(code_str, allowed_imports=None):
    """Execute code with restrictions"""
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            # Block dangerous operations
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if allowed_imports:
                    # Check if import is whitelisted
                    pass
                else:
                    raise ValueError("Imports not allowed")
            if isinstance(node, (ast.Call,)):
                if hasattr(node.func, 'id') and node.func.id in ['__import__', 'eval', 'exec']:
                    raise ValueError("Dangerous function call")
        
        # Safe execution with restricted builtins
        safe_globals = {'__builtins__': {}}
        exec(compile(tree, '<string>', 'exec'), safe_globals)
    except SyntaxError as e:
        raise ValueError(f"Invalid code: {e}")
```

#### Step 3: Apply Sandboxing
- Identify where exec() is used
- Evaluate if it's necessary
- Replace with safer alternatives where possible

**Testing:**
- Unit tests for sandbox
- Ensure legitimate code paths work
- Verify dangerous operations are blocked

**Verification Checklist:**
- [ ] No unguarded exec() calls
- [ ] All user input validated before exec()
- [ ] Sandbox tests pass
- [ ] No legitimate functionality broken

---

### Friday-Saturday: Testing & Validation (All Tracks)

**Objective:** Verify all CRITICAL fixes work correctly  
**Effort:** 2-3 hours

#### Full Test Suite Run
```bash
pytest tests/ -k "security" --cov=src --cov-report=term-missing
```

#### Security Scanning
```bash
semgrep --config p/owasp-top-ten --error --sarif-output results.sarif
codeql analyze --format sarif --output codeql-results.sarif
```

#### Manual Verification
- [ ] Run scripts with sensitive data, verify masking works
- [ ] Test URL validator with edge cases
- [ ] Run code with potentially malicious input
- [ ] Check logs contain no secrets

#### Documentation
- Update security guidelines with new patterns
- Document URL whitelist maintenance
- Add token masking examples to code

---

## WEEK 2: HIGH-PRIORITY ISSUES (Days 8-14)

**Deliverable Goal:** Zero HIGH findings  
**Estimated Effort:** 16 hours (~2.3 hours/day)  
**Wall Time:** 8-10 hours (parallel tracks)

### Monday-Tuesday: Pickle to JSON Migration (Track 1)

**Objective:** Eliminate pickle deserialization risk  
**Effort:** 8-10 hours  
**Files:** 8 files

#### Phase 1: Create JSON Serialization Helpers (1.5h)
- Create: `src/codex_ml/serialization/json_helpers.py`
- Implement:
  ```python
  class SafeJSONEncoder(json.JSONEncoder):
      def default(self, obj):
          if isinstance(obj, datetime):
              return obj.isoformat()
          if isinstance(obj, bytes):
              return obj.hex()
          if isinstance(obj, set):
              return list(obj)
          return super().default(obj)
  
  class SafeJSONDecoder(json.JSONDecoder):
      def __init__(self, *args, **kwargs):
          super().__init__(object_hook=self.object_hook, *args, **kwargs)
      
      def object_hook(self, dct):
          # Reconstruct complex types if needed
          return dct
  ```

#### Phase 2: Identify Pickle Usage (1h)
```bash
grep -r "pickle\." --include="*.py" | grep -v "__pycache__" | tee /tmp/pickle_audit.txt
```

#### Phase 3: Migrate Test Data (3-4h)
- **File 1:** `mutants/tests/test_cache_management.py`
  - 5 instances of pickle.loads()
  - Convert test fixtures to JSON
  - Update deserialization calls
  
- **File 2:** `tests/test_cache_management.py`
  - 5 instances
  - Same migration pattern

- **Files 3-8:** Apply to utility files

#### Phase 4: Verify Compatibility (2-3h)
- Unit tests for JSON serialization
- Ensure test data loads correctly
- Compare pickled vs JSON data structures
- Performance comparison

**Testing:**
```python
def test_json_serialization_compat():
    test_obj = create_test_object()
    json_str = json.dumps(test_obj, cls=SafeJSONEncoder)
    restored = json.loads(json_str, cls=SafeJSONDecoder)
    assert restored == test_obj
```

**Verification Checklist:**
- [ ] All pickle.loads() replaced with json.loads()
- [ ] Test data serializes to JSON
- [ ] Deserialized objects match originals
- [ ] Performance acceptable
- [ ] Tests pass

---

### Wednesday: Log Injection & Weak Hashing (Track 2)

**Objective:** Fix injection and weak cryptography  
**Effort:** 5-6 hours  
**Files:** 16+ files

#### Log Injection Fixes (2-3h)
- Identify user input flowing to logs
- Apply sanitization: `.replace('\n', '\\n').replace('\r', '\\r')`
- Test with injection payloads

#### Weak Hashing Replacement (3h)
- Find all `hashlib.sha256()` used for passwords → Replace with bcrypt
- Find all `hashlib.md5()` → Replace with SHA256
- Add bcrypt to requirements if not present
- Update password verification logic

**Verification Checklist:**
- [ ] No newline characters escape logs
- [ ] Log injection tests pass
- [ ] All passwords use bcrypt
- [ ] MD5 usage eliminated
- [ ] Password verification still works

---

### Thursday-Friday: Secret Storage & Token Security (Track 3)

**Objective:** Encrypt sensitive stored data  
**Effort:** 5-6 hours  
**Files:** 6+ files

#### Secret Storage Encryption (2-3h)
- Implement encryption wrapper using cryptography.Fernet
- Replace all clear-text secret storage
- Add key management documentation

#### Token Broker Security (3h)
- Fix token handling in broker implementations
- Add token expiration checks
- Implement token refresh logic
- Update tests

**Testing:**
- [ ] Stored secrets encrypted with Fernet
- [ ] Decryption works for legitimate cases
- [ ] Token expiration prevents use of old tokens
- [ ] Token refresh works correctly

---

### Friday-Saturday: Integration Testing (All Tracks)

**Effort:** 2-3 hours

#### Full Test Suite
```bash
pytest tests/ -v --tb=short --cov
```

#### Security Scanning
```bash
semgrep --config p/owasp-top-ten --error
codeql analyze --format sarif
```

#### Code Review
- Review all changes
- Verify patterns applied consistently
- Check documentation

---

## WEEK 3: MEDIUM-PRIORITY ISSUES (Days 15-21)

**Deliverable Goal:** MEDIUM findings resolved  
**Estimated Effort:** 12 hours (~1.7 hours/day)  
**Wall Time:** 6-8 hours (parallel tracks)

### Monday: Cryptographic Algorithm Upgrade (Track 1)

**Effort:** 4-6 hours  
**Files:** 15+ files

#### Audit MD5/Weak Crypto
```bash
grep -r "hashlib.md5\|hashlib.sha1\|AES.MODE_ECB" --include="*.py"
```

#### MD5 → SHA256 Migration
- Find all MD5 usage
- Replace with SHA256
- Add comments about why SHA256 for non-password hashing
- Note: For passwords, use bcrypt (already done in Week 2)

#### ECB → GCM Migration (if applicable)
- Find all AES ECB mode usage
- Replace with GCM mode for authenticated encryption

**Fix Pattern:**
```python
# OLD: import hashlib; hashlib.md5(data).hexdigest()
# NEW: import hashlib; hashlib.sha256(data).hexdigest()

# OLD: from cryptography.hazmat.primitives.ciphers import modes; modes.ECB()
# NEW: from cryptography.hazmat.primitives.ciphers import modes; modes.GCM(iv)
```

---

### Tuesday: Credential Log Sanitization (Track 2)

**Effort:** 3-4 hours  
**Files:** 10+ files

#### Implement Log Filter
```python
import logging
import re

class CredentialFilter(logging.Filter):
    PATTERNS = [
        r'(password|passwd|pwd)\s*=\s*["\']([^"\']+)["\']',
        r'(api_key|apikey|api-key)\s*=\s*["\']([^"\']+)["\']',
        r'(token|auth|authorization)\s*[:=]\s*["\']([^"\']+)["\']',
    ]
    
    def filter(self, record):
        message = record.getMessage()
        for pattern in self.PATTERNS:
            message = re.sub(pattern, r'\1=***', message, flags=re.IGNORECASE)
        record.msg = message
        return True

logger = logging.getLogger()
logger.addFilter(CredentialFilter())
```

#### Apply to All Loggers
- Add filter to root logger
- Verify filtering works
- Test with sensitive data

---

### Wednesday: File Permissions & Stack Traces (Track 3)

**Effort:** 2-3 hours  
**Files:** 5+ files

#### File Permission Hardening
```python
import os

def write_sensitive_file(path, content):
    old_umask = os.umask(0o077)  # Owner r/w only
    try:
        with open(path, 'w') as f:
            f.write(content)
        os.chmod(path, 0o600)
    finally:
        os.umask(old_umask)
```

#### Stack Trace Handling
- Find all error handlers that expose stack traces
- Log full trace internally only
- Return generic error messages to users
- Example:
  ```python
  try:
      dangerous_operation()
  except Exception as e:
      logger.exception("Internal error occurred")  # Includes stack trace
      raise ValueError("An error occurred") from None  # Generic to user
  ```

---

### Thursday: Code Cleanup & Automation (Track 4)

**Effort:** 1-2 hours  
**Files:** 37 LOW findings

#### Automated Fixes
```bash
# ESLint fix (unused variables, formatting)
eslint site/assets/javascripts/lunr/ --fix

# Prettier (semicolons, formatting)
prettier site/assets/javascripts/lunr/ --write
```

#### Manual Fixes
- Trivial conditionals: 3 findings (~1h)
- Dead code elimination (~0.5h)

---

### Friday-Saturday: Final Validation & Documentation

**Effort:** 2-3 hours

#### Comprehensive Testing
```bash
# Full test suite
pytest tests/ -v --cov --cov-report=html

# Security scanning
semgrep --config p/owasp-top-ten --sarif-output findings.sarif
codeql analyze --format sarif

# Manual review of changes
git diff main...phase-5.3 | review
```

#### Documentation Update
- Update SECURITY.md with new patterns
- Document URL whitelist maintenance
- Add examples for secret storage
- Update developer guide

#### Final Checklist
- [ ] All CRITICAL findings fixed
- [ ] All HIGH findings resolved
- [ ] MEDIUM findings addressed
- [ ] LOW findings automated/documented
- [ ] Tests passing (90%+ coverage)
- [ ] Security scans clean
- [ ] Documentation updated
- [ ] Ready for merge

---

## PARALLEL EXECUTION STRATEGY

### Recommended Parallelization

**Week 1:**
- Track 1 (Token masking): Days 1-2
- Track 2 (URL validation): Days 3-4 **[PARALLEL with Track 1]**
- Track 3 (Exec injection): Days 5-6 **[PARALLEL with Tracks 1-2]**

**Week 2:**
- Track 1 (Pickle migration): Days 8-12 **[Primary]**
- Track 2 (Log injection/hashing): Days 8-10 **[PARALLEL]**
- Track 3 (Token security): Days 11-14 **[PARALLEL]**

**Week 3:**
- Track 1 (Crypto upgrade): Days 15-16
- Track 2 (Log sanitization): Days 15-17 **[PARALLEL]**
- Track 3 (Permissions): Days 17-18 **[PARALLEL]**
- Track 4 (Cleanup): Days 19-20 **[PARALLEL]**

### Resource Allocation

- **Developer 1:** Token masking + URL validation (Week 1)
- **Developer 2:** Exec injection + Pickle migration (Week 1-2)
- **Developer 3:** Log injection + Crypto (Week 2-3)
- **DevOps:** Testing, scanning, validation (throughout)

---

## RISK MITIGATION

### Testing Strategy
- 100% test coverage for new security code
- Integration tests for each major fix
- Security scanning at each phase

### Rollback Plan
- Keep previous version tagged as `phase-5.2-final`
- Use feature branches: `phase-5.3-critical`, etc.
- Merge to `phase-5.3` branch, then to main

### Monitoring During Implementation
- Run security scans after each major change
- Track test coverage (maintain 85%+ minimum)
- Document any discovered issues

---

## SUCCESS METRICS

| Metric | Target | Phase |
|--------|--------|-------|
| CRITICAL findings | 0 | End of Week 1 |
| HIGH findings | 0 | End of Week 2 |
| MEDIUM findings | <20 | End of Week 3 |
| Test coverage | 85%+ | End of Week 3 |
| Security scan results | No critical | End of Week 3 |
| Documentation | 100% updated | End of Week 3 |

---

## DELIVERABLES

### Week 1
- ✅ PR: Token masking & logging fixes
- ✅ PR: URL validation framework
- ✅ PR: Exec injection fixes
- ✅ Updated LANE_D reports

### Week 2
- ✅ PR: Pickle to JSON migration
- ✅ PR: Log injection & hashing fixes
- ✅ PR: Token security hardening
- ✅ Security scan reports

### Week 3
- ✅ PR: Cryptographic upgrades
- ✅ PR: Log sanitization
- ✅ PR: File permissions & stack traces
- ✅ PR: Code cleanup
- ✅ Updated documentation
- ✅ Final security report

---

**Roadmap Status:** Ready for Execution  
**Generated:** 2026-07-13T13:14:45Z  
**Authority:** D-tier autonomous
