# Lane C: Execution Checklist

**Campaign:** Issue #5299 - Security Vulnerabilities Resolution  
**Lane:** C (Semgrep OWASP Pattern Analysis)  
**Timeline:** 40-56 hours across 3 weeks  
**Authority:** D-tier autonomous

---

## Phase 1: CRITICAL Findings (Week 1)

### ✅ Priority 1.1: Fix Dynamic URL Handling (33 findings - 8-10 hours)

**OWASP:** A01:2024 - Broken Access Control  
**CWE:** CWE-939  
**Rule:** dynamic-urllib-use-detected  
**Severity:** CRITICAL

#### Step 1.1.1: Create URL Validator Module
- [ ] Create `src/aries_serpent_core/security/url_validator.py`
- [ ] Implement `URLValidator` class with scheme and host whitelist
- [ ] Add unit tests in `tests/security/test_url_validator.py`
- [ ] Add to CI gate: `semgrep --config p/owasp-top-ten --error`
- **Time:** 2-3 hours

#### Step 1.1.2: Fix Agent URL Calls
- [ ] Update `.github/agents/codex_reviewer/github_client.py` (4 findings)
  - Line 189: Replace `urllib.request.urlopen(url)` with validated call
  - Line 262: Replace `urllib.request.urlopen(api_url)` with validated call
  - Line 290: Replace `urllib.request.urlopen(gh_url)` with validated call
  - Line 319: Replace `urllib.request.urlopen(webhook_url)` with validated call
- [ ] Update `.github/agents/github-guru-agent/github_client.py` (3 findings)
- [ ] Update `src/aries_serpent_core/autonomy/token_broker.py` (2 findings)
- [ ] Update `mutants/src/codex/autonomy/token_broker.py` (2 findings)
- [ ] Update remaining 22 findings across service middleware
- **Time:** 4-6 hours
- **Testing:** Run security test suite
  ```bash
  pytest tests/security/test_url_validator.py -v
  semgrep --config p/owasp-top-ten .
  ```

#### Step 1.1.3: Audit & Verification
- [ ] Verify all 33 findings resolved
- [ ] Run full SAST scan: `semgrep --config p/owasp-top-ten --sarif-output results.sarif`
- [ ] Confirm 0 CWE-939 findings remain
- **Time:** 1-2 hours

**Definition of Done:**
- ✅ 33 findings fixed and verified
- ✅ URL validator tests passing
- ✅ No new CWE-939 findings in SAST
- ✅ PR merged with clean CI

---

### ✅ Priority 1.2: Fix Code Injection (2 findings - 4-6 hours)

**OWASP:** A03:2024 - Injection  
**CWE:** CWE-95  
**Rule:** exec-detected  
**Severity:** CRITICAL

#### Step 1.2.1: Create Safe Execution Module
- [ ] Create `src/aries_serpent_core/security/safe_exec.py`
- [ ] Implement `safe_exec()` with AST validation
- [ ] Block dangerous imports and function calls
- [ ] Add comprehensive tests
- **Time:** 2-3 hours

#### Step 1.2.2: Fix Injection Points
- [ ] Update `services/msp_gateway/middleware/tenant_context.py:125`
  - Replace `exec(user_code)` with `safe_exec(user_code)`
- [ ] Update `src/codex_ml/utils/safe_pickle.py:210`
  - Replace `exec(pickled_code)` with sandboxed execution
- **Time:** 1-2 hours
- **Testing:**
  ```bash
  pytest tests/security/test_safe_exec.py -v
  # Test that dangerous code is blocked
  ```

#### Step 1.2.3: Verification
- [ ] Verify 0 CWE-95 findings remain
- [ ] Run security tests
- **Time:** 1 hour

**Definition of Done:**
- ✅ 2 findings fixed
- ✅ Safe execution module implemented
- ✅ Tests passing
- ✅ PR merged

---

## Phase 2: HIGH Severity Findings (Week 2)

### ✅ Priority 2.1: Migrate Pickle to JSON (23 findings - 12-16 hours)

**OWASP:** A08:2024 - Data Integrity Failures  
**CWE:** CWE-502  
**Rule:** pickle.avoid-pickle  
**Severity:** HIGH

#### Step 2.1.1: Create JSON Serialization Helpers
- [ ] Create `src/aries_serpent_core/serialization/json_helpers.py`
- [ ] Implement `SafeJSONEncoder` for common types (datetime, bytes, etc.)
- [ ] Implement `safe_loads()` with type validation
- [ ] Add tests: `tests/serialization/test_json_helpers.py`
- **Time:** 3-4 hours

#### Step 2.1.2: Migrate Test Cache
- [ ] Update `mutants/tests/test_cache_management.py` (5 findings)
  - Replace all `pickle.loads()` with `json.loads()`
  - Replace all `pickle.dumps()` with `json.dumps()`
- [ ] Update `tests/test_cache_management.py` (5 findings)
- [ ] Update test fixtures in mutation testing
- **Time:** 4-6 hours

#### Step 2.1.3: Migrate Production Cache
- [ ] Update `mutants/src/codex_ml/utils/safe_pickle.py` (3 findings)
- [ ] Update `src/codex_ml/utils/safe_pickle.py` (3 findings)
- [ ] Update `utils/safe_pickle.py` (3 findings)
- [ ] Create migration script for existing pickled data
- **Time:** 3-4 hours

#### Step 2.1.4: Verification
- [ ] Verify 0 CWE-502 findings remain
- [ ] Run all cache-related tests
- [ ] Performance testing: verify no regression
- **Time:** 1-2 hours

**Definition of Done:**
- ✅ 23 findings fixed
- ✅ JSON serialization helpers implemented
- ✅ All tests passing
- ✅ Performance verified
- ✅ Migration completed

---

### ✅ Priority 2.2: Fix Hardcoded JWT Secrets (2 findings - 2-3 hours)

**OWASP:** A07:2024 - Authentication Failures  
**CWE:** CWE-522  
**Rule:** jwt-hardcode  
**Severity:** HIGH

#### Step 2.2.1: Environment Configuration
- [ ] Update `src/aries_serpent_core/auth/github_app.py:95`
  - Replace hardcoded `SECRET_KEY = "..."` with `os.environ.get('JWT_SECRET_KEY')`
  - Add validation: raise error if not set
- [ ] Update `mutants/src/codex/auth/github_app.py:95` (mirrored)
- **Time:** 1 hour

#### Step 2.2.2: Configuration Documentation
- [ ] Create `.env.example` with JWT_SECRET_KEY placeholder
- [ ] Update deployment docs to set environment variable
- [ ] Add CI validation: check JWT_SECRET_KEY in test environment
- **Time:** 1 hour

#### Step 2.2.3: Verification
- [ ] Verify 0 CWE-522 findings remain
- [ ] Test that error is raised when env var missing
- **Time:** < 1 hour

**Definition of Done:**
- ✅ 2 findings fixed
- ✅ Environment variable properly configured
- ✅ Tests passing
- ✅ Documentation updated

---

## Phase 3: MEDIUM Severity Findings (Week 2-3)

### ✅ Priority 3.1: Replace MD5 with SHA256 (18 findings - 3-4 hours)

**OWASP:** A02:2024 - Cryptographic Failures  
**CWE:** CWE-327  
**Rule:** insecure-hash-algorithms-md5  
**Severity:** MEDIUM

#### Step 3.1.1: Identify All MD5 Usage
- [ ] Run audit:
  ```bash
  grep -r "hashlib.md5" --include="*.py" > /tmp/md5_findings.txt
  grep -r "hashlib.md5" --include="*.py" | wc -l  # Should be 18
  ```
- **Files affected:** 6 primary files with duplicates
- **Time:** < 1 hour

#### Step 3.1.2: Replace MD5 → SHA256
- [ ] `mutants/src/codex/auth/github_app.py` - 3 findings
- [ ] `src/aries_serpent_core/auth/github_app.py` - 3 findings
- [ ] `mutants/src/codex/github/api_client.py` - 3 findings
- [ ] `src/aries_serpent_core/github/api_client.py` - 3 findings
- [ ] `mutants/src/codex_ml/utils/safe_pickle.py` - 2 findings
- [ ] `src/codex_ml/utils/safe_pickle.py` - 2 findings
- [ ] Additional files - 2 findings

**Replacement Pattern:**
```python
# OLD
hashlib.md5(data).hexdigest()

# NEW (for non-password hashes)
hashlib.sha256(data).hexdigest()

# NEW (for passwords - use bcrypt)
bcrypt.hashpw(data.encode(), bcrypt.gensalt()).decode()
```
- **Time:** 2-3 hours

#### Step 3.1.3: Verification
- [ ] Verify 0 MD5 findings remain
- [ ] Verify 0 CWE-327 findings remain
- [ ] Run all authentication tests
- **Time:** 1 hour

**Definition of Done:**
- ✅ 18 findings fixed
- ✅ All tests passing
- ✅ No MD5 usage in codebase

---

### ✅ Priority 3.2: Fix ECB Mode → GCM (4 findings - 2-3 hours)

**OWASP:** A02:2024 - Cryptographic Failures  
**CWE:** CWE-327  
**Rule:** crypto-mode-without-authentication  
**Severity:** MEDIUM

#### Step 3.2.1: Update Encryption Module
- [ ] `src/codex/security/encryption.py` - 2 findings
  - Replace `modes.ECB()` with `modes.GCM(iv)`
  - Generate random IV for each encryption
  - Store IV with ciphertext
- [ ] `tests/security/test_encryption.py` - 2 findings (test fixtures)
- **Time:** 1-2 hours

#### Step 3.2.2: Migration Strategy
- [ ] Create migration script for existing ECB-encrypted data
- [ ] Support reading old ECB format (read-only)
- [ ] Decrypt and re-encrypt on-the-fly
- **Time:** 1 hour

#### Step 3.2.3: Verification
- [ ] Verify 0 CWE-327 findings remain
- [ ] Encryption/decryption tests passing
- [ ] Migration script tested
- **Time:** < 1 hour

**Definition of Done:**
- ✅ 4 findings fixed
- ✅ GCM mode properly implemented
- ✅ Migration script working
- ✅ Tests passing

---

### ✅ Priority 3.3: Sanitize Credential Logging (19 findings - 5-8 hours)

**OWASP:** A09:2024 - Logging and Monitoring Failures  
**CWE:** CWE-532  
**Rule:** logger-credential-disclosure  
**Severity:** MEDIUM

#### Step 3.3.1: Create Logging Filter
- [ ] Create `src/aries_serpent_core/logging/filters.py`
- [ ] Implement `SensitiveDataFilter` logging filter
- [ ] Redact: passwords, tokens, secrets, API keys, credentials
- [ ] Add unit tests
- **Time:** 2 hours

#### Step 3.3.2: Update Logger Configuration
- [ ] Apply filter globally in `src/aries_serpent_core/logging/__init__.py`
- [ ] Update all logger instantiations to use filtered logger
- [ ] Test that sensitive data is redacted in logs
- **Time:** 2-3 hours
- **Testing:**
  ```python
  logger.info(f"Auth with password: {password}")  # Should show [REDACTED]
  ```

#### Step 3.3.3: Audit Logging Statements
- [ ] Review all 19 findings for context-specific redaction
- [ ] Some may need custom redaction logic
- [ ] Update `auth/` module (8 findings)
- [ ] Update `github/` module (5 findings)
- [ ] Update `services/` module (4 findings)
- [ ] Update `utils/` module (2 findings)
- **Time:** 2-3 hours

#### Step 3.3.4: Verification
- [ ] Verify 0 CWE-532 findings remain
- [ ] Audit log output for sensitive data
- [ ] Integration tests with logs
- **Time:** 1 hour

**Definition of Done:**
- ✅ 19 findings fixed
- ✅ Logging filter implemented
- ✅ No sensitive data in logs
- ✅ Tests passing

---

### ✅ Priority 3.4: Fix File Permissions (5 findings - 1-2 hours)

**OWASP:** A04:2024 - Insecure Design  
**CWE:** CWE-276  
**Rule:** insecure-file-permissions  
**Severity:** MEDIUM

#### Step 3.4.1: Create Secure File Writer
- [ ] Create utility function: `write_secure_file(path, content)`
- [ ] Use `os.umask(0o077)` for owner-only access
- [ ] Add to `src/aries_serpent_core/utils/file_utils.py`
- **Time:** < 1 hour

#### Step 3.4.2: Update File Operations
- [ ] `services/msp_gateway/middleware/tenant_context.py:45`
- [ ] `src/codex/config/loader.py:120`
- [ ] Test fixture files (3 locations)
- [ ] Replace direct `open()` with `write_secure_file()`
- **Time:** 1 hour

#### Step 3.4.3: Verification
- [ ] Verify 0 CWE-276 findings remain
- [ ] Check file permissions: `ls -la`
- [ ] Verify readable only by owner
- **Time:** < 1 hour

**Definition of Done:**
- ✅ 5 findings fixed
- ✅ All sensitive files have 0600 permissions
- ✅ Tests passing

---

## Phase 4: LOW Severity Findings (Week 3)

### ✅ Priority 4.1: Fix EKS Public Endpoint (1 finding - <1 hour)

**OWASP:** A05:2024 - Security Misconfiguration  
**CWE:** CWE-200  
**Rule:** eks-public-endpoint-enabled  
**Severity:** LOW

#### Step 4.1.1: Update Terraform
- [ ] `.github/agents/deploy/terraform/main.tf:85`
- [ ] Change `endpoint_public_access = true` → `false`
- [ ] Add `public_access_cidrs = ["10.0.0.0/8"]` if public access needed
- **Time:** < 1 hour

**Definition of Done:**
- ✅ 1 finding fixed
- ✅ Terraform validated
- ✅ Deployment reviewed

---

## Testing & Validation

### Unit Tests
```bash
pytest tests/security/ -v
pytest tests/serialization/ -v
pytest tests/logging/ -v
```

### Integration Tests
```bash
pytest tests/integration/test_security_full.py -v
```

### SAST Scanning
```bash
semgrep --config p/owasp-top-ten --sarif-output results.sarif
# Should show 0 findings after all fixes
```

### Performance Testing
```bash
pytest tests/performance/ -v
# Verify no regression from changes
```

---

## PR Checklist

Each PR should include:
- [ ] Updated code with security fixes
- [ ] Unit tests for changes
- [ ] Updated documentation
- [ ] SAST scan results (0 findings)
- [ ] Performance test results (no regression)
- [ ] Code review approved
- [ ] CI/CD pipeline passing

---

## Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| CRITICAL Findings Fixed | 35/35 | ⬜ |
| HIGH Findings Fixed | 25/25 | ⬜ |
| MEDIUM Findings Fixed | 46/46 | ⬜ |
| LOW Findings Fixed | 1/1 | ⬜ |
| **Total:** | **107/107** | **⬜** |
| SAST Findings Remaining | 0 | ⬜ |
| All Tests Passing | 100% | ⬜ |
| Code Coverage | ≥95% | ⬜ |

---

**Status:** Ready for Phase 1 Execution  
**Timeline:** 40-56 hours across 3 weeks  
**Next:** Begin Priority 1.1 (Dynamic URL Handling)
