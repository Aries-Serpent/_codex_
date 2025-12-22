# Security Best Practices Guide

## Overview

This guide provides security best practices for developers working on the _codex_ codebase. Following these practices helps maintain a secure, production-ready system.

---

## 🔐 Core Principles

### 1. Defense in Depth
Apply multiple layers of security controls:
- Input validation at boundaries
- Proper authentication and authorization
- Secure defaults for all configurations
- Logging for security events

### 2. Principle of Least Privilege
- Run processes with minimum required permissions
- Limit API access to necessary operations only
- Use read-only access where possible

### 3. Fail Securely
- Handle errors gracefully without exposing internals
- Log failures for investigation
- Provide generic error messages to users
- Include detailed context in logs

---

## 🛡️ Security Patterns by Category

### Model Loading (PyTorch)

#### ✅ SAFE Pattern
```python
from utils.safe_torch_loader import safe_load

# Always use weights_only=True for untrusted models
model_state = safe_load('model.pth', weights_only=True)
model.load_state_dict(model_state)
```

#### ❌ UNSAFE Pattern
```python
# NEVER do this with untrusted models
model = torch.load('untrusted.pth')  # RCE vulnerability!
```

**Why**: `torch.load()` without `weights_only=True` can execute arbitrary code during deserialization.

---

### Pickle Deserialization

#### ✅ SAFE Pattern
```python
from utils.safe_pickle import safe_pickle_load

# Use RestrictedUnpickler for untrusted data
data = safe_pickle_load('data.pkl', use_restricted_unpickler=True)
```

#### ❌ UNSAFE Pattern
```python
# NEVER deserialize untrusted pickle data directly
with open('untrusted.pkl', 'rb') as f:
    data = pickle.load(f)  # RCE vulnerability!
```

**Why**: Pickle can execute arbitrary code during deserialization. Only use RestrictedUnpickler for untrusted sources.

**Alternative**: Use safer formats for data exchange:
```python
import json

# For simple data structures
data = json.loads(json_string)

# For ML models, use safetensors
from safetensors.torch import save_file, load_file
save_file(model.state_dict(), 'model.safetensors')
state_dict = load_file('model.safetensors')
```

---

### Subprocess Execution

#### ✅ SAFE Pattern
```python
import subprocess
import shlex

# Use list form - safe from command injection
result = subprocess.run(['git', 'status', '--short'], 
                       capture_output=True, 
                       text=True,
                       check=True)

# If you must parse a string command
command = "git status --short"
args = shlex.split(command)
result = subprocess.run(args, capture_output=True, text=True)
```

#### ❌ UNSAFE Pattern
```python
# NEVER use shell=True with user input
user_input = request.args.get('file')
subprocess.run(f'cat {user_input}', shell=True)  # Command injection!
```

**Why**: `shell=True` interprets shell metacharacters, allowing command injection.

---

### Cryptographic Hashing

#### ✅ SAFE Pattern
```python
import hashlib

# For security purposes: use SHA256
secure_hash = hashlib.sha256(data).hexdigest()

# For non-security purposes (caching, checksums): mark explicitly
cache_key = hashlib.md5(data, usedforsecurity=False).hexdigest()
```

#### ❌ UNSAFE Pattern
```python
# Don't use MD5 for security without marking it
hash_value = hashlib.md5(password)  # Security warning!
```

**Why**: MD5 is cryptographically broken. Use SHA256+ for security, or explicitly mark MD5 as non-security use.

---

### Error Handling

#### ✅ SAFE Pattern
```python
import logging
logger = logging.getLogger(__name__)

try:
    risky_operation()
except FileNotFoundError as e:
    # Specific exception, with logging
    logger.warning(f"File not found: {e}", exc_info=True)
    return default_value
except PermissionError as e:
    # Critical error - log and re-raise
    logger.error(f"Permission denied: {e}", exc_info=True)
    raise
```

#### ❌ UNSAFE Pattern
```python
# Silent failure - hides bugs
try:
    risky_operation()
except:
    pass  # No logging, no visibility!

# Overly broad exception catching
try:
    operation()
except Exception:  # Too broad
    pass
```

**Why**: Silent failures make debugging impossible. Always log exceptions with context.

---

### API Security

#### ✅ SAFE Pattern
```python
from fastapi import FastAPI, HTTPException
from services.api.middleware.form_validator import SecureMultipartMiddleware
from services.api.config import APIConfig

app = FastAPI()
app.add_middleware(SecureMultipartMiddleware)

@app.post("/upload")
async def upload_file(file: UploadFile):
    # Validate file size
    if file.size > APIConfig.MAX_UPLOAD_SIZE:
        raise HTTPException(413, "File too large")
    
    # Validate file type
    allowed_types = {'text/plain', 'application/json'}
    if file.content_type not in allowed_types:
        raise HTTPException(415, "Unsupported media type")
    
    # Process file safely
    content = await file.read()
    return {"status": "success"}
```

#### ❌ UNSAFE Pattern
```python
# No validation, no size limits
@app.post("/upload")
async def upload_file(file: UploadFile):
    content = await file.read()  # No size limit! DoS risk
    eval(content)  # Never eval user input! RCE risk
```

**Why**: Always validate and limit user input. Never execute user-provided code.

---

### XML Parsing

#### ✅ SAFE Pattern
```python
from defusedxml.ElementTree import parse

# Safe from XXE attacks
tree = parse('data.xml')
```

#### ❌ UNSAFE Pattern
```python
from xml.etree.ElementTree import parse

# Vulnerable to XXE attacks
tree = parse('untrusted.xml')
```

**Why**: Standard XML parsers are vulnerable to XXE (XML External Entity) attacks.

---

## 🔒 Security Checklist for Code Reviews

### Before Committing
- [ ] No `eval()` or `exec()` with user input
- [ ] All `torch.load()` uses `weights_only=True`
- [ ] All `pickle.load()` uses `RestrictedUnpickler` for untrusted data
- [ ] No `shell=True` in subprocess calls
- [ ] MD5 usage marked with `usedforsecurity=False`
- [ ] All exceptions are logged (no bare `except: pass`)
- [ ] Input validation on all API endpoints
- [ ] File uploads have size and type restrictions
- [ ] XML parsing uses `defusedxml`
- [ ] Secrets not hardcoded in source

### Security Utilities to Use
- `utils.safe_torch_loader.safe_load()` - PyTorch models
- `utils.safe_pickle.safe_pickle_load()` - Pickle data
- `utils.torch_resource_manager.torch_resource_guard()` - GPU cleanup
- `services.api.middleware.form_validator.SecureMultipartMiddleware` - Form validation
- `services.api.config.APIConfig` - Security limits

---

## 📚 Additional Resources

### Internal Documentation
- [SECURITY.md](./SECURITY.md) - Security policy and patched vulnerabilities
- [PYTORCH_MIGRATION_GUIDE.md](./PYTORCH_MIGRATION_GUIDE.md) - PyTorch security migration
- [ERROR_HANDLING_IMPROVEMENT_GUIDE.md](./ERROR_HANDLING_IMPROVEMENT_GUIDE.md) - Error handling patterns

### External References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [PyTorch Security](https://pytorch.org/docs/stable/notes/serialization.html#security)

---

## 🚨 Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email: security@codex.dev
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

---

## 🔄 Security Review Process

### For All Pull Requests
1. Run security validation: `python scripts/security/validate_security.py`
2. Check for new security alerts: Review GitHub Security tab
3. Verify no secrets committed: `git secrets --scan`
4. Review dependencies: `pip-audit`

### For Security-Sensitive Changes
1. Request security review from team lead
2. Run comprehensive test suite including security tests
3. Update security documentation as needed
4. Add entry to SECURITY.md if applicable

---

## 📊 Security Metrics

Track these metrics for ongoing security health:

- Security alerts (target: 0 critical/high)
- Test coverage for security utilities (target: >80%)
- Time to patch vulnerabilities (target: <7 days for critical)
- Security training completion (target: 100% of team)

---

## ✅ Quick Reference Card

### Most Common Security Mistakes

| Mistake | Fix |
|---------|-----|
| `torch.load(path)` | `safe_load(path, weights_only=True)` |
| `pickle.load(f)` | `safe_pickle_load(path, use_restricted_unpickler=True)` |
| `subprocess.run(cmd, shell=True)` | `subprocess.run(shlex.split(cmd))` |
| `hashlib.md5(data)` | `hashlib.md5(data, usedforsecurity=False)` |
| `except: pass` | `except Exception as e: logger.warning(f"{e}", exc_info=True)` |
| `eval(user_input)` | Use `ast.literal_eval()` or `json.loads()` |

### Remember
- **Default to secure**: Use secure patterns by default
- **Validate inputs**: Trust no input without validation
- **Log everything**: Especially security-relevant events
- **Test security**: Include security tests in test suite
- **Stay updated**: Follow security advisories for dependencies

---

**Last Updated**: 2024-12-22  
**Version**: 1.0  
**Owner**: Security Team
