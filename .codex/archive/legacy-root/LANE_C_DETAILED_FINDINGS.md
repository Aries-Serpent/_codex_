# Lane C: Detailed Findings List

**Total Findings:** 107  
**Report Date:** 2026-07-13T13:12:21Z  
**Artifact:** security-suite-semgrep (291 KB)  
**Scanned Files:** 16,641  
**Scan Duration:** ~120 seconds

---

## Finding Categories

### CRITICAL Severity Findings (35 total)

#### A01:2024 - Broken Access Control (33 findings)

**Issue:** Dynamic URL handling with urllib allows malicious actors to construct arbitrary URLs including `file://` schemes for reading arbitrary files.

**Primary Rule:** `dynamic-urllib-use-detected`  
**CWE:** CWE-939 - Improper Authorization in Handler for Custom URL Scheme  
**Bandit Code:** B310

**Affected Files:**
- `.github/agents/codex_reviewer/github_client.py` - 4 findings (lines: 189, 262, 290, 319)
- `.github/agents/github-guru-agent/github_client.py` - 3 findings
- `src/aries_serpent_core/autonomy/token_broker.py` - 2 findings
- `mutants/src/codex/autonomy/token_broker.py` - 2 findings
- `services/msp_gateway/middleware/tenant_context.py` - 2 findings
- Plus 20+ additional findings across agent infrastructure

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
response = urllib.request.urlopen(user_url)
remote_config = urllib.request.urlopen(base_url + api_path)
```

**Recommended Fix:**
```python
# ✅ SECURE
from urllib.parse import urlparse

def validate_url(url, allowed_schemes=('https',), allowed_hosts=None):
    parsed = urlparse(url)
    if parsed.scheme not in allowed_schemes:
        raise ValueError(f"Invalid scheme: {parsed.scheme}")
    if allowed_hosts and parsed.netloc not in allowed_hosts:
        raise ValueError(f"Host not whitelisted: {parsed.netloc}")
    return url

response = urllib.request.urlopen(validate_url(user_url))
```

**Estimated Fix Time:** 8-10 hours  
**Priority:** IMMEDIATE (P0)

---

#### A03:2024 - Injection (2 findings)

**Issue:** Use of `exec()` function with user-controlled input or insufficient input validation.

**Primary Rule:** `exec-detected`  
**CWE:** CWE-95 - Improper Neutralization of Directives in Dynamically Evaluated Code  
**Severity:** CRITICAL

**Affected Files:**
1. `services/msp_gateway/middleware/tenant_context.py:125` - exec() in middleware
2. `src/codex_ml/utils/safe_pickle.py:210` - exec() in deserialization logic

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
user_script = request.get('script')
exec(user_script)
```

**Recommended Fix:**
```python
# ✅ SECURE (Restricted execution)
import ast

def safe_exec(code_str, whitelist_vars=None):
    try:
        tree = ast.parse(code_str)
        # Validate AST
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Call)):
                if hasattr(node, 'func') and isinstance(node.func, ast.Name):
                    if node.func.id in ('exec', 'eval', '__import__'):
                        raise ValueError("Dangerous function not allowed")
        code_obj = compile(tree, '<string>', 'exec')
        safe_globals = {'__builtins__': {}}
        if whitelist_vars:
            safe_globals.update(whitelist_vars)
        exec(code_obj, safe_globals)
    except SyntaxError as e:
        raise ValueError(f"Invalid syntax: {e}")
```

**Estimated Fix Time:** 4-6 hours  
**Priority:** IMMEDIATE (P0)

---

### HIGH Severity Findings (25 total)

#### A08:2024 - Data Integrity Failures (23 findings)

**Issue:** Unsafe deserialization using Python's `pickle` module allows arbitrary code execution.

**Primary Rule:** `pickle.avoid-pickle`  
**CWE:** CWE-502 - Deserialization of Untrusted Data  
**Severity:** HIGH

**Affected Files:**
- `mutants/tests/test_cache_management.py` - 5 findings
- `tests/test_cache_management.py` - 5 findings
- `mutants/src/codex_ml/utils/safe_pickle.py` - 3 findings
- `src/codex_ml/utils/safe_pickle.py` - 3 findings
- `utils/safe_pickle.py` - 3 findings
- Various mutation test fixtures - 4 findings

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
import pickle
data = pickle.loads(untrusted_bytes)
cache_data = pickle.load(open('cache.pkl', 'rb'))
```

**Recommended Fix:**
```python
# ✅ SECURE (JSON serialization)
import json

def safe_deserialize(data_str):
    """Safely deserialize using JSON instead of pickle"""
    try:
        return json.loads(data_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid data format: {e}")

# For backward compatibility if needed
import pickle
import pickletools
import io

def restricted_pickle_loads(data):
    """Pickle with restricted types - use with caution"""
    # Only allow safe types
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            # Restrict to safe modules
            if module not in ('datetime', '__builtin__', 'builtins'):
                raise pickle.UnpicklingError(f"Module {module} not allowed")
            return super().find_class(module, name)
    
    return RestrictedUnpickler(io.BytesIO(data)).load()
```

**Estimated Fix Time:** 12-16 hours  
**Priority:** HIGH (P1)

---

#### A07:2024 - Authentication Failures (2 findings)

**Issue:** JWT secrets hardcoded in source code.

**Primary Rule:** `jwt-hardcode`  
**CWE:** CWE-522 - Insufficiently Protected Credentials  
**Severity:** HIGH

**Affected Files:**
1. `src/aries_serpent_core/auth/github_app.py:95`
2. `mutants/src/codex/auth/github_app.py:95`

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
SECRET_KEY = "my-secret-key-12345"
jwt_token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
```

**Recommended Fix:**
```python
# ✅ SECURE (Environment variables)
import os
from pathlib import Path

SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set")

# OR use .env file with python-dotenv
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')

jwt_token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
```

**Estimated Fix Time:** 2-3 hours  
**Priority:** HIGH (P1)

---

### MEDIUM Severity Findings (46 total)

#### A02:2024 - Cryptographic Failures (22 findings)

**Issue 1: MD5 Hashing (18 findings)**

**Rule:** `insecure-hash-algorithms-md5`  
**CWE:** CWE-327 - Use of a Broken or Risky Cryptographic Algorithm  
**Status:** MD5 is cryptographically broken and should not be used

**Affected Files:**
- `mutants/src/codex/auth/github_app.py` - 3 findings
- `src/aries_serpent_core/auth/github_app.py` - 3 findings
- `mutants/src/codex/github/api_client.py` - 3 findings
- `src/aries_serpent_core/github/api_client.py` - 3 findings
- `mutants/src/codex_ml/utils/safe_pickle.py` - 2 findings
- `src/codex_ml/utils/safe_pickle.py` - 2 findings
- Plus 2 additional findings

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
file_checksum = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
```

**Recommended Fix:**
```python
# ✅ SECURE (SHA256)
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()

# OR BETTER (bcrypt for passwords)
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# For file checksums use SHA256
file_checksum = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
```

**Estimated Fix Time:** 3-4 hours  
**Priority:** MEDIUM (P2)

---

**Issue 2: ECB Mode Without Authentication (4 findings)**

**Rule:** `crypto-mode-without-authentication`  
**CWE:** CWE-327 - Use of a Broken or Risky Cryptographic Algorithm  
**Status:** ECB mode doesn't provide authentication, use GCM instead

**Affected Files:**
- `src/codex/security/encryption.py` - 2 findings
- `tests/security/test_encryption.py` - 2 findings

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
cipher = Cipher(algorithms.AES(key), modes.ECB())
```

**Recommended Fix:**
```python
# ✅ SECURE (GCM mode with authentication)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

iv = os.urandom(12)  # 96-bit IV for GCM
cipher = Cipher(
    algorithms.AES(key),
    modes.GCM(iv)
)
encryptor = cipher.encryptor()
ciphertext = encryptor.update(plaintext) + encryptor.finalize()
tag = encryptor.tag  # Authentication tag
```

**Estimated Fix Time:** 2-3 hours  
**Priority:** MEDIUM (P2)

---

#### A09:2024 - Logging and Monitoring Failures (19 findings)

**Issue:** Credentials and sensitive information logged without sanitization.

**Primary Rule:** `logger-credential-disclosure`  
**CWE:** CWE-532 - Insertion of Sensitive Information into Log File

**Affected Modules:**
- `auth/` - 8 findings (passwords, tokens)
- `github/` - 5 findings (API tokens, auth headers)
- `services/` - 4 findings (service credentials)
- `utils/` - 2 findings (configuration secrets)

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
logger.info(f"Authenticating user with password: {password}")
logger.debug(f"API token: {api_token}")
logger.warning(f"Connection failed with credentials {username}:{password}")
```

**Recommended Fix:**
```python
# ✅ SECURE (Credential sanitization)
import logging

class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive information from logs"""
    SENSITIVE_PATTERNS = [
        'password', 'token', 'secret', 'api_key', 'apikey',
        'auth', 'credential', 'pwd', 'passwd'
    ]
    
    def filter(self, record):
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.lower() in str(record.msg).lower():
                # Replace sensitive values with asterisks
                record.msg = self._redact(str(record.msg))
        return True
    
    @staticmethod
    def _redact(text, show_chars=2):
        """Replace middle characters with asterisks"""
        if len(text) <= show_chars * 2:
            return '*' * len(text)
        return text[:show_chars] + '*' * (len(text) - show_chars * 2) + text[-show_chars:]

# Usage
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

# Safe logging
logger.info(f"Authenticating user with password: [REDACTED]")
logger.debug(f"API token: {api_token[:4]}****{api_token[-4:]}")  # Show first/last 4 chars
```

**Estimated Fix Time:** 5-8 hours  
**Priority:** MEDIUM (P2)

---

#### A04:2024 - Insecure Design (5 findings)

**Issue:** Incorrect file permissions on sensitive configuration and test files.

**Primary Rule:** `insecure-file-permissions`  
**CWE:** CWE-276 - Incorrect Default Permissions

**Affected Files:**
1. `services/msp_gateway/middleware/tenant_context.py:45` - Config file
2. `src/codex/config/loader.py:120` - Secrets file
3-5. Test fixture files - Various locations

**Example Vulnerable Code:**
```python
# ❌ VULNERABLE
with open('config.json', 'w') as f:
    json.dump(config_data, f)

with open('secrets.yaml', 'w') as f:
    yaml.dump(secrets, f)
```

**Recommended Fix:**
```python
# ✅ SECURE (Restricted permissions)
import os
import tempfile

def write_secure_file(path, content):
    """Write file with restricted permissions"""
    # Use umask to restrict access
    old_umask = os.umask(0o077)  # Owner read/write only
    try:
        with open(path, 'w') as f:
            f.write(content)
    finally:
        os.umask(old_umask)

# OR use tempfile for temporary files
with tempfile.NamedTemporaryFile(mode='w', delete=False, dir='/secure/location') as f:
    f.write(content)
    os.chmod(f.name, 0o600)
    secure_path = f.name
```

**Estimated Fix Time:** 1-2 hours  
**Priority:** MEDIUM (P2)

---

### LOW Severity Findings (1 total)

#### A05:2024 - Security Misconfiguration (1 finding)

**Issue:** EKS cluster endpoint is publicly accessible.

**Rule:** `eks-public-endpoint-enabled`  
**CWE:** CWE-200 - Exposure of Sensitive Information  
**File:** `.github/agents/deploy/terraform/main.tf:85`

**Example Vulnerable Code:**
```hcl
# ❌ VULNERABLE
resource "aws_eks_cluster" "main" {
  name = "production-cluster"
  # ...
  endpoint_private_access = false
  endpoint_public_access  = true  # ❌ VULNERABLE
}
```

**Recommended Fix:**
```hcl
# ✅ SECURE
resource "aws_eks_cluster" "main" {
  name = "production-cluster"
  # ...
  endpoint_private_access = true
  endpoint_public_access  = false  # Or true with CIDR restrictions
  public_access_cidrs     = ["10.0.0.0/8"]  # Restrict to VPN only
}
```

**Estimated Fix Time:** < 1 hour  
**Priority:** LOW (P3)

---

## Summary Statistics

**Total Findings:** 107

**By Severity:**
| Severity | Count | Percentage | Fix Time | Priority |
|----------|-------|-----------|----------|----------|
| CRITICAL | 35 | 32.7% | 10-14h | P0 |
| HIGH | 25 | 23.4% | 16-20h | P1 |
| MEDIUM | 46 | 43.0% | 14-18h | P2 |
| LOW | 1 | 0.9% | <1h | P3 |
| **TOTAL** | **107** | **100%** | **40-56h** | — |

**By OWASP 2024 Category:**
| Category | Count | CWE | Primary Rule |
|----------|-------|-----|--------------|
| A01: Broken Access Control | 39 | CWE-939 | dynamic-urllib-use-detected |
| A02: Cryptographic Failures | 22 | CWE-327 | insecure-hash-algorithms-md5 |
| A03: Injection | 2 | CWE-95 | exec-detected |
| A04: Insecure Design | 2 | CWE-276 | insecure-file-permissions |
| A07: Authentication Failures | 2 | CWE-522 | jwt-hardcode |
| A08: Data Integrity Failures | 23 | CWE-502 | pickle.avoid-pickle |
| A09: Logging & Monitoring | 19 | CWE-532 | logger-credential-disclosure |

**By CWE:**
| CWE | Count | Severity | Title |
|-----|-------|----------|-------|
| CWE-939 | 33 | CRITICAL | Improper Authorization in Handler for Custom URL Scheme |
| CWE-502 | 23 | HIGH | Deserialization of Untrusted Data |
| CWE-327 | 22 | MEDIUM | Use of a Broken or Risky Cryptographic Algorithm |
| CWE-532 | 19 | MEDIUM | Insertion of Sensitive Information into Log File |
| CWE-276 | 5 | MEDIUM | Incorrect Default Permissions |
| CWE-522 | 2 | HIGH | Insufficiently Protected Credentials |
| CWE-95 | 2 | CRITICAL | Improper Neutralization of Directives in Dynamically Evaluated Code |
| CWE-200 | 1 | LOW | Exposure of Sensitive Information to an Unauthorized Actor |

---

## Remediation Timeline

**Phase 1 (Week 1 - P0):** 10-14 hours
- [ ] Fix 35 urllib dynamic URL findings
- [ ] Fix 2 exec() injection findings

**Phase 2 (Week 2 - P1):** 16-20 hours
- [ ] Migrate 23 pickle findings to JSON
- [ ] Fix 2 hardcoded JWT findings

**Phase 3 (Week 2-3 - P2):** 14-18 hours
- [ ] Replace 18 MD5 with SHA256
- [ ] Fix 4 ECB mode findings
- [ ] Sanitize 19 credential logs
- [ ] Fix 5 file permission issues

**Phase 4 (Week 3 - P3):** <1 hour
- [ ] Fix EKS public endpoint

**Total Effort:** 40-56 hours across 3 weeks

---

**Report Generated:** 2026-07-13T13:12:21Z  
**Status:** ✅ Complete  
**Next Step:** Begin Phase 1 remediation (P0 findings)
