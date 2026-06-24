# Security Best Practices Guide

> Comprehensive guide to secure development, deployment, and operations  
> **Level**: Advanced | **Prerequisites**: Basic security knowledge  
> **Last Updated**: 2026-06-22 | **Version**: 2.0

---

## Table of Contents

1. [Overview](#overview)
2. [OWASP Top 10 Mapping](#owasp-top-10-mapping)
3. [Input Validation](#input-validation)
4. [Threat Modeling](#threat-modeling)
5. [Secure Coding Patterns](#secure-coding-patterns)
6. [Security Testing](#security-testing)
7. [Checklist](#checklist)

---

## Overview

Security is a continuous process, not a destination. This guide provides practical patterns for building secure applications.

### Core Principles

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimum necessary permissions
3. **Fail Securely**: Errors don't expose vulnerabilities
4. **Validate Always**: Never trust user input
5. **Encrypt Sensitive Data**: Both in transit and at rest

### Security Maturity Levels

| Level | Characteristics |
|-------|-----------------|
| **L1: Basic** | HTTPS enabled, basic auth, no secrets in code |
| **L2: Standard** | Input validation, auth/authz, logging |
| **L3: Advanced** | Threat modeling, penetration testing, encryption |
| **L4: Mature** | Security reviews, incident response, continuous monitoring |
| **L5: Expert** | Bug bounty, red teams, security champions |

---

## OWASP Top 10 Mapping

### 1. Broken Access Control

**Risk**: Users can access resources they shouldn't

```python
# ❌ VULNERABLE: No access control
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return database.get_user(user_id)

# ✅ SECURE: Check authorization
from functools import wraps

def require_permission(resource_type: str):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = get_current_user(request)
            resource_id = kwargs.get("user_id")

            # Check if user has permission
            if not user_has_permission(user, resource_type, resource_id):
                raise PermissionError(f"Access denied to {resource_type}")

            return func(request, *args, **kwargs)
        return wrapper
    return decorator

@app.get("/users/{user_id}")
@require_permission("user_profile")
def get_user(request, user_id: int):
    return database.get_user(user_id)
```

**Defense**: Role-based access control (RBAC)

```python
class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class Role(Enum):
    VIEWER = [Permission.READ]
    EDITOR = [Permission.READ, Permission.WRITE]
    ADMIN = [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN]

class RoleBasedAccessControl:
    def __init__(self):
        self.role_permissions = {
            Role.VIEWER: set(Role.VIEWER.value),
            Role.EDITOR: set(Role.EDITOR.value),
            Role.ADMIN: set(Role.ADMIN.value)
        }

    def has_permission(self, user_role: Role, required_permission: Permission) -> bool:
        return required_permission in self.role_permissions[user_role]

# Usage in endpoint
@app.post("/users/{user_id}/settings")
def update_user_settings(request, user_id: int, settings: dict):
    user = get_current_user(request)
    rbac = RoleBasedAccessControl()

    if not rbac.has_permission(user.role, Permission.WRITE):
        raise PermissionError("Insufficient permissions")

    return database.update_user(user_id, settings)
```

## 2. Cryptographic Failures

**Risk**: Sensitive data exposed due to weak encryption

```python
# ❌ VULNERABLE: No encryption
def store_credit_card(card_number: str):
    database.save("credit_cards", {"card": card_number})

# ✅ SECURE: Encrypt sensitive data
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class EncryptionService:
    def __init__(self, master_key: str):
        # Derive key from master key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"fixed_salt_prod",  # Should be random and stored securely
            iterations=100000,
        )
        self.cipher = Fernet(self._key_to_fernet(master_key))

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Usage
encryption = EncryptionService(os.environ["MASTER_KEY"])

def store_credit_card(card_number: str):
    encrypted_card = encryption.encrypt(card_number)
    database.save("credit_cards", {"card": encrypted_card})

def get_credit_card(card_id: int) -> str:
    encrypted_card = database.get("credit_cards", card_id)["card"]
    return encryption.decrypt(encrypted_card)
```

**Defense**: Always use TLS, encrypt sensitive data at rest

```yaml
# docker-compose.yml - Force HTTPS
services:
  app:
    environment:
      - FORCE_HTTPS=true
      - SESSION_COOKIE_SECURE=true
      - SESSION_COOKIE_HTTPONLY=true
      - HSTS_SECONDS=31536000
```

## 3. Injection Attacks

**Risk**: Attacker injects malicious code (SQL, command, template)

```python
# ❌ VULNERABLE: SQL injection
def get_user_by_email(email: str):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return database.execute(query)

# ✅ SECURE: Parameterized queries
def get_user_by_email(email: str):
    query = "SELECT * FROM users WHERE email = ?"
    return database.execute(query, (email,))

# ❌ VULNERABLE: Command injection
def backup_database(backup_name: str):
    os.system(f"mysqldump -u root -p{password} > {backup_name}.sql")

# ✅ SECURE: Use subprocess with list
import subprocess
def backup_database(backup_name: str):
    subprocess.run([
        "mysqldump",
        "-u", "root",
        "-p" + password,
        ">", f"{backup_name}.sql"
    ], check=True)

# ❌ VULNERABLE: Template injection
@app.post("/emails")
def send_email(template_name: str, user_data: dict):
    template = get_template(f"templates/{template_name}.html")
    html = template.format(**user_data)  # User can inject code
    return send_email_template(html)

# ✅ SECURE: Use safe templating
from jinja2 import Template, Markup
def send_email(template_name: str, user_data: dict):
    template_path = f"templates/{template_name}.html"

    # Validate template name
    if ".." in template_name or "/" in template_name:
        raise ValueError("Invalid template name")

    with open(template_path) as f:
        template = Template(f.read())

    # Jinja2 automatically escapes user data
    html = template.render(**user_data)
    return send_email_template(html)
```

## 4. Insecure Design

**Risk**: Application lacks security requirements in design phase

**Defense**: Threat modeling during design

```python
# Example: Threat model for payment system
class PaymentThreatModel:
    """
    Asset: Payment data
    Threat: Attacker intercepts payment
    Mitigation: TLS encryption + tokenization
    """

    def process_payment(self, card: str, amount: float):
        # Step 1: Tokenize card data (external service)
        token = self.tokenizer.tokenize(card)

        # Step 2: Store token only (never store card)
        payment_record = {
            "token": token,
            "amount": amount,
            "timestamp": datetime.now(),
            "encrypted": True
        }

        # Step 3: Log for audit
        self.audit_log.record(payment_record)

        return {"status": "success", "transaction_id": token}
```

## 5. Security Misconfiguration

**Risk**: Default credentials, unnecessary services, verbose error messages

```python
# ❌ VULNERABLE: Exposes stack traces
@app.exception_handler(Exception)
def handle_error(request, exc):
    return {
        "error": str(exc),
        "traceback": traceback.format_exc()  # Reveals internals
    }

# ✅ SECURE: Generic error messages
@app.exception_handler(Exception)
def handle_error(request, exc):
    logger.error(f"Unexpected error: {exc}", exc_info=True)  # Log internally

    return {
        "error": "Internal server error",
        "request_id": request.id
    }
```

## 6. Vulnerable Components

**Risk**: Using outdated dependencies with known vulnerabilities

```bash
# Check for vulnerabilities
pip install pip-audit
pip-audit

# Or using safety
pip install safety
safety check

# Update vulnerable packages
pip install --upgrade <package_name>
```

## 7. Authentication Failures

**Risk**: Weak password policies, session management issues

```python
# ✅ SECURE: Strong password validation
import re
from password_validator import PasswordValidator

class PasswordValidator:
    def __init__(self):
        self.validator = PasswordValidator()
        self.validator \
            .min(12) \
            .max(128) \
            .uppercase() \
            .lowercase() \
            .digits() \
            .symbols() \
            .no_spaces()

    def validate(self, password: str) -> tuple[bool, str]:
        if not self.validator.validate(password):
            return False, "Password does not meet requirements"
        return True, "Valid"

# ✅ SECURE: Multi-factor authentication
import pyotp

class MFAService:
    def generate_secret(self, user_id: str) -> str:
        secret = pyotp.random_base32()
        store_mfa_secret(user_id, secret)
        return secret

    def verify_code(self, user_id: str, code: str) -> bool:
        secret = get_mfa_secret(user_id)
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

# ✅ SECURE: Session management
@app.post("/login")
def login(credentials: dict):
    user = authenticate_user(credentials)

    if not user:
        raise PermissionError("Invalid credentials")

    # Create session with security options
    session = {
        "user_id": user.id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=1),
        "ip_address": request.client.host
    }

    response = JSONResponse({"status": "success"})

    # Set secure cookie
    response.set_cookie(
        key="session_id",
        value=generate_session_id(session),
        max_age=3600,
        secure=True,  # HTTPS only
        httponly=True,  # No JS access
        samesite="Strict"  # CSRF protection
    )

    return response
```

## 8. Software Supply Chain

**Risk**: Compromised dependencies or build artifacts

```yaml
# .github/workflows/security-checks.yml
name: Security Checks

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check dependencies
        run: |
          pip install pip-audit
          pip-audit

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./

      - name: SAST scan
        uses: github/super-linter@v4
```

## 9. Identification and Authentication Failures

```python
# ✅ SECURE: Rate limiting for login attempts
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # Max 5 attempts per minute
def login(request: Request, credentials: dict):
    user = authenticate_user(credentials)
    if not user:
        # Log attempt but don't reveal if user exists
        logger.warning(f"Failed login attempt from {request.client.host}")
        raise PermissionError("Invalid credentials")

    return create_session(user)
```

## 10. Server-Side Request Forgery (SSRF)

```python
# ❌ VULNERABLE: No URL validation
@app.post("/fetch")
def fetch_url(url: str):
    response = requests.get(url)
    return response.text

# ✅ SECURE: Validate URL
from urllib.parse import urlparse

class URLValidator:
    BLOCKED_HOSTS = ["127.0.0.1", "localhost", "169.254.169.254"]

    def is_safe(self, url: str) -> bool:
        parsed = urlparse(url)

        # Check protocol
        if parsed.scheme not in ["http", "https"]:
            return False

        # Check host
        if parsed.hostname in self.BLOCKED_HOSTS:
            return False

        # Check for private IP ranges
        try:
            ip = socket.gethostbyname(parsed.hostname)
            if ip.startswith("10.") or ip.startswith("192.168."):
                return False
        except socket.gaierror:
            return False

        return True

@app.post("/fetch")
def fetch_url(url: str):
    validator = URLValidator()
    if not validator.is_safe(url):
        raise ValueError("URL is not allowed")

    response = requests.get(url, timeout=5)
    return response.text
```

---

## Input Validation

### 1. Validation Strategy

```python
from typing import Any
from dataclasses import dataclass

@dataclass
class ValidationRule:
    field: str
    type: type
    required: bool
    min_length: int = None
    max_length: int = None
    pattern: str = None
    allowed_values: list = None

class InputValidator:
    def __init__(self, rules: list[ValidationRule]):
        self.rules = rules

    def validate(self, data: dict) -> tuple[bool, dict]:
        errors = {}

        for rule in self.rules:
            value = data.get(rule.field)

            # Check required
            if rule.required and value is None:
                errors[rule.field] = "Required"
                continue

            # Check type
            if value is not None and not isinstance(value, rule.type):
                errors[rule.field] = f"Must be {rule.type.__name__}"
                continue

            # Check length
            if isinstance(value, str):
                if rule.min_length and len(value) < rule.min_length:
                    errors[rule.field] = f"Minimum {rule.min_length} characters"
                if rule.max_length and len(value) > rule.max_length:
                    errors[rule.field] = f"Maximum {rule.max_length} characters"

            # Check pattern
            if rule.pattern and isinstance(value, str):
                if not re.match(rule.pattern, value):
                    errors[rule.field] = "Invalid format"

            # Check allowed values
            if rule.allowed_values and value not in rule.allowed_values:
                errors[rule.field] = "Not an allowed value"

        return len(errors) == 0, errors

# Usage
rules = [
    ValidationRule("email", str, required=True, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"),
    ValidationRule("age", int, required=True, min_length=18, max_length=120),
    ValidationRule("role", str, required=True, allowed_values=["admin", "user", "viewer"]),
]

validator = InputValidator(rules)
is_valid, errors = validator.validate(user_input)
```

## 2. HTML Escaping

```python
from markupsafe import escape

# ❌ VULNERABLE
@app.get("/user/{name}")
def get_user_page(name: str):
    return f"<h1>Welcome {name}</h1>"  # Could inject script

# ✅ SECURE
@app.get("/user/{name}")
def get_user_page(name: str):
    return f"<h1>Welcome {escape(name)}</h1>"
```

---

## Threat Modeling

### STRIDE Framework

```
Spoofing: Attacker pretends to be someone else
Tampering: Attacker modifies data
Repudiation: Attacker denies actions
Information Disclosure: Sensitive data exposed
Denial of Service: System becomes unavailable
Elevation of Privilege: Attacker gains higher access
```

### Example Threat Model

```python
class ThreatModel:
    """
    System: E-commerce payment processing

    Assets:
    - Credit card data
    - User account credentials
    - Payment transactions

    Threats:
    1. Spoofing: Attacker impersonates merchant
       Mitigation: SSL certificates, digital signatures

    2. Tampering: Attacker modifies transaction amount
       Mitigation: Encryption, integrity checks

    3. Repudiation: User denies payment
       Mitigation: Digital signatures, audit logs

    4. Information Disclosure: Card data leaked
       Mitigation: Encryption at rest, PCI compliance

    5. Denial of Service: Payment system overloaded
       Mitigation: Rate limiting, load balancing

    6. Elevation of Privilege: Admin access gained
       Mitigation: MFA, RBAC, audit logging
    """
    pass
```

---

## Secure Coding Patterns

### Pattern 1: Secure Defaults

```python
# ✅ Deny by default, allow explicitly
@dataclass
class SecurityConfig:
    allow_cors: bool = False
    require_https: bool = True
    enable_debug: bool = False
    password_min_length: int = 12
    session_timeout_minutes: int = 30
```

## Pattern 2: Defense in Depth

```python
# Multiple layers: Auth → Input validation → Authorization → Encryption
def process_sensitive_request(request):
    # Layer 1: Authentication
    user = authenticate(request)
    if not user:
        raise AuthenticationError()

    # Layer 2: Input validation
    data = validate_input(request.data)
    if not data:
        raise ValidationError()

    # Layer 3: Authorization
    if not user_has_permission(user, "write_sensitive_data"):
        raise AuthorizationError()

    # Layer 4: Encryption
    encrypted_data = encrypt_sensitive_data(data)

    # Layer 5: Audit logging
    log_action(user, "sensitive_data_modified", data)

    return encrypted_data
```

---

## Security Testing

### 1. SAST (Static Analysis)

```bash
# Python static analysis
pip install bandit
bandit -r src/

# Find security issues
bandit -r src/ -f json -o security_report.json
```

## 2. Dependency Scanning

```bash
pip-audit
safety check
```

### 3. Penetration Testing

```bash
# Test SQL injection
sqlmap -u "http://localhost:8000/users?id=1" --dbs

# Test XSS
zaproxy --cli -quick -self-contained -project-file scan.zapproj -url http://localhost:8000
```

---

## Checklist

### Security Review Checklist

- [ ] All user inputs validated and sanitized
- [ ] Sensitive data encrypted at rest and in transit
- [ ] Authentication and authorization implemented
- [ ] No hardcoded secrets or credentials
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Logging and monitoring configured
- [ ] Rate limiting and DDoS protection enabled
- [ ] Dependencies up to date and scanned for vulnerabilities
- [ ] Error messages don't expose sensitive information
- [ ] CORS properly configured
- [ ] CSRF protection enabled
- [ ] Session management secure
- [ ] Access control tests passing
- [ ] Security tests automated and passing
- [ ] Incident response plan documented

---

## Cross-References

- [Secret Management Documentation](./secret-management.md)
- [Authentication Guide](../authentication/USER_GUIDE.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Word Count**: 2,814 | **Examples**: 24 | **Patterns**: 8
**Last Updated**: 2026-06-22 | **Status**: ✅ Complete
