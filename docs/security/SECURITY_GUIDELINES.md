# Security Best Practices Guide

## Table of Contents
1. [Sensitive Data Handling](#sensitive-data-handling)
2. [Log Injection Prevention](#log-injection-prevention)
3. [Secure Storage](#secure-storage)
4. [Dependency Management](#dependency-management)
5. [Code Review Checklist](#code-review-checklist)
6. [Common Pitfalls](#common-pitfalls)

---

## Sensitive Data Handling

### ✅ DO: Mask Sensitive Data in Logs

```python
from codex.security import mask_token, mask_email, mask_password

# API Keys and Tokens
logger.info(f"Processing request with token: {mask_token(api_key)}")
# Output: "Processing request with token: ************xyz789"

# Email Addresses
logger.info(f"User email: {mask_email('user@example.com')}")
# Output: "User email: u***@example.com"

# Passwords (always fully masked)
logger.info(f"Password validation: {mask_password(password)}")
# Output: "Password validation: ***"
```

### ❌ DON'T: Log Sensitive Data in Plain Text

```python
# NEVER DO THIS
logger.info(f"API Key: {api_key}")  # ❌ Exposes full key in logs
logger.info(f"User password: {password}")  # ❌ Security violation
print(f"Secret: {secret_token}")  # ❌ may appear in console logs
```

---

## Log Injection Prevention

### ✅ DO: Sanitize User-Controlled Input

```python
from codex.security import sanitize_log

# User input that may contain control characters
user_input = request.form.get('username')
logger.info(f"Login attempt: {sanitize_log(user_input)}")

# File paths from user
filepath = user_provided_path
logger.info(f"Processing file: {sanitize_log(filepath)}")
```

### ❌ DON'T: Use Unsanitized User Input in Logs

```python
# NEVER DO THIS
user_input = request.form.get('data')
logger.info(f"User provided: {user_input}")  # ❌ Log injection vulnerability

# Attacker input: "normal\nFAKE LOG ENTRY: Admin password reset"
# Result in logs:
#   User provided: normal
#   FAKE LOG ENTRY: Admin password reset  # ← Injected by attacker
```

---

## Secure Storage

### ✅ DO: Use Encrypted Storage for Secrets

```python
from codex.security.storage import SecureStorage
import os

# Set encryption key (do this once, store securely)
os.environ['ENCRYPTION_KEY'] = "your-base64-key-here"

# Initialize storage
storage = SecureStorage()

# Store secrets encrypted
storage.store_secret("secrets/api_key.enc", api_key)
storage.store_secret("secrets/db_password.enc", db_password)

# Load secrets when needed
api_key = storage.load_secret("secrets/api_key.enc")
```

### 🔐 Key Management Best Practices

```bash
# Generate encryption key
python3 -c "from codex.security.storage import generate_key; print(generate_key())"

# Store in environment (DO NOT COMMIT TO GIT)
export ENCRYPTION_KEY="generated_key_here"

# Or use password-based key derivation
from codex.security.storage import derive_key_from_password
key, salt = derive_key_from_password("my_secure_password")
# Store salt securely, regenerate key when needed
```

### ❌ DON'T: Store Secrets in Plain Text

```python
# NEVER DO THIS
with open("api_key.txt", "w") as f:
    f.write(api_key)  # ❌ Plain text file

config = {
    "api_key": "sk_live_abc123",  # ❌ Hard-coded secret
    "password": "admin123"  # ❌ Plain text in config
}

# In .env file:
API_KEY=sk_live_abc123  # ❌ Plain text (add .env to .gitignore!)
```

---

## Dependency Management

### ✅ DO: Keep Dependencies Updated

```bash
# Check for vulnerabilities
pip-audit

# Update to secure versions
pip install --upgrade torch>=2.5.1
pip install --upgrade starlette>=0.45.1
pip install --upgrade nbconvert>=7.16.6

# Lock dependencies
pip freeze > requirements/lock.txt
```

### 📋 Security Requirements

- **Critical/High CVEs**: Must be fixed within 7 days
- **Moderate CVEs**: Should be fixed within 30 days
- **Low CVEs**: Review and fix within 90 days

### ❌ DON'T: Ignore Dependabot Alerts

```yaml
# In dependabot.yml - Keep this enabled
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Code Review Checklist

### Security Items to Check

- [ ] No hard-coded secrets (API keys, passwords, tokens)
- [ ] Sensitive data is masked in logs
- [ ] User input is sanitized before logging
- [ ] Dependencies have no known vulnerabilities
- [ ] File permissions are secure (0o600 for sensitive files)
- [ ] No use of weak cryptography (MD5, SHA-1 for security)
- [ ] Error messages don't leak sensitive information
- [ ] SQL queries use parameterized statements
- [ ] File uploads are validated and sanitized

### Quick Scan Commands

```bash
# Search for potential secrets
git secrets --scan

# Check for common security issues
bandit -r src/ -ll

# Find TODO security items
grep -r "TODO.*secur" src/

# Check for weak crypto
grep -r "hashlib.md5\|hashlib.sha1" src/
```

---

## Common Pitfalls

### 1. Using MD5 for Security

```python
# ❌ WRONG
import hashlib
token_hash = hashlib.md5(token.encode()).hexdigest()

# ✅ CORRECT
from codex.security import hash_secure
token_hash = hash_secure(token, algorithm='sha256')
```

### 2. Logging Exception Details

```python
# ❌ WRONG (Phase 5 expose sensitive data in traceback)
try:
    api_call(api_key=secret_key)
except Exception as e:
    logger.error(f"API call failed: {e}")  # may contain secret_key

# ✅ CORRECT
try:
    api_call(api_key=secret_key)
except Exception as e:
    logger.error("API call failed", exc_info=False)  # No sensitive data
    logger.debug(f"Error details: {type(e).__name__}")
```

### 3. String Formatting in SQL

```python
# ❌ WRONG (SQL injection vulnerability)
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# ✅ CORRECT (parameterized query)
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

### 4. Insecure File Permissions

```python
# ❌ WRONG (world-readable)
with open("secret.txt", "w") as f:
    f.write(secret)

# ✅ CORRECT (owner-only permissions)
import os, stat
with open("secret.txt", "w") as f:
    f.write(secret)
os.chmod("secret.txt", stat.S_IRUSR | stat.S_IWUSR)  # 0o600
```

---

## Quick Reference

### Import Statement

```python
# All security utilities in one place
from codex.security import (
    # Masking
    mask_token,
    mask_email,
    mask_password,
    mask_sensitive,
    # Sanitization
    sanitize_log,
    sanitize_dict_for_log,
    # Hashing
    hash_secure,
)

# Encrypted storage
from codex.security.storage import SecureStorage, generate_key
```

### Environment Variables

```bash
# Required for encrypted storage
export ENCRYPTION_KEY="base64-encoded-key"

# Optional: Custom security settings
export LOG_SANITIZE_MAX_LENGTH=1000
export MASK_TOKEN_SHOW_CHARS=6
```

---

## Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

Contact: security@localhost (replace with actual contact)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://docs.python.org/3/library/security_warnings.html)
- [Bandit Security Linter](https://bandit.readthedocs.io/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)

---

**Last Updated**: 2025-12-23  
**Maintained By**: Security Team
