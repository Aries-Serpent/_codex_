# Phase 6 Lane 4: Security Training Guide

**For**: Software Engineers & Developers  
**Duration**: Self-paced (4-6 hours)  
**Certification**: Completion tracking via training dashboard  
**Updated**: 2026-07-18

---

## Module 1: Security Fundamentals

### 1.1: The CIA Triad

**Confidentiality**: Only authorized users can access data
- Example: Database passwords should not be readable by unauthorized users
- Threat: Data breach, social engineering

**Integrity**: Data cannot be tampered with or altered
- Example: Transaction amounts should not be modifiable
- Threat: Data corruption, financial fraud

**Availability**: Systems must be accessible when needed
- Example: APIs should not be taken offline
- Threat: Denial of service (DoS), ransomware

### 1.2: OWASP Top 10 (2021)

| # | Vulnerability | Description | Prevention |
|---|---|---|---|
| 1 | Broken Access Control | Users access data they shouldn't | Implement RBAC, least privilege |
| 2 | Cryptographic Failures | Sensitive data not encrypted | Use HTTPS, encrypt at rest |
| 3 | Injection | SQL injection, command injection | Use parameterized queries |
| 4 | Insecure Design | Security not built into design | Threat modeling, secure coding |
| 5 | Security Misconfiguration | Default credentials, open ports | Configuration hardening |
| 6 | Vulnerable & Outdated Components | Old dependencies with CVEs | Dependency scanning, updates |
| 7 | Authentication Failures | Weak password policies | MFA, password managers |
| 8 | Software & Data Integrity Failures | Malicious code/data | Code signing, package verification |
| 9 | Logging & Monitoring Failures | Attacks not detected | Comprehensive logging, SIEM |
| 10 | Server-Side Request Forgery (SSRF) | Requests to unintended servers | Input validation, URL whitelisting |

---

## Module 2: Secure Coding Practices

### 2.1: Input Validation

**DO**: Always validate user input
```python
# Validate email format
import re
email = request.get('email')
if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
    raise ValueError("Invalid email format")
```

**DON'T**: Trust user input
```python
# VULNERABLE
name = request.get('name')
greeting = f"Hello {name}!"  # What if name contains <script>?
```

### 2.2: Output Encoding

**DO**: Encode output for the context
```python
# HTML context: Escape HTML entities
from html import escape
return f"<p>{escape(user_input)}</p>"

# JavaScript context: JSON encode
import json
return f"<script>var data = {json.dumps(user_input)};</script>"

# URL context: URL encode
from urllib.parse import quote
return f"<a href='?q={quote(user_input)}'>Search</a>"
```

### 2.3: Parameterized Queries

**DO**: Use parameterized queries to prevent SQL injection
```python
# SECURE
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (user_email,))

# SECURE (Django ORM)
user = User.objects.get(email=user_email)
```

**DON'T**: Concatenate SQL strings
```python
# VULNERABLE - DO NOT USE
query = f"SELECT * FROM users WHERE email = '{user_email}'"
cursor.execute(query)
```

### 2.4: Authentication & Authorization

**DO**: Use framework-provided authentication
```python
# Flask example
from flask_login import login_required, current_user

@app.route('/profile')
@login_required
def profile():
    return f"Welcome {current_user.email}"

# Django example
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
```

**DON'T**: Implement your own auth
```python
# VULNERABLE - DO NOT IMPLEMENT YOUR OWN
def login(username, password):
    if username == "admin" and password == "password123":
        return True
```

### 2.5: Cryptography

**DO**: Use established cryptographic libraries
```python
# Password hashing
from werkzeug.security import generate_password_hash, check_password_hash
hashed = generate_password_hash('password123', method='pbkdf2:sha256')

# Data encryption
from cryptography.fernet import Fernet
cipher = Fernet(key)
encrypted = cipher.encrypt(b"secret data")
```

**DON'T**: Implement crypto yourself
```python
# VULNERABLE - DO NOT DO THIS
import hashlib
hashed = hashlib.md5(password).hexdigest()  # MD5 is broken

# VULNERABLE
from base64 import b64encode
"encrypted" = b64encode(data)  # Base64 is not encryption!
```

---

## Module 3: Threat Modeling

### 3.1: STRIDE Methodology

**S**poofing: Can an attacker pretend to be someone else?  
**T**ampering: Can an attacker modify data or code?  
**R**epudiation: Can an attacker deny they performed an action?  
**I**nformation Disclosure: Can an attacker access sensitive data?  
**D**enial of Service: Can an attacker take the system down?  
**E**levation of Privilege: Can an attacker gain higher permissions?

### 3.2: Threat Modeling Process

1. **Define scope**: What systems/data are in scope?
2. **Identify assets**: What needs protecting? (data, code, credentials)
3. **Identify threats**: Use STRIDE to brainstorm threats
4. **Identify mitigations**: How will you prevent/detect each threat?
5. **Document results**: Create threat model document

### 3.3: Example: User Registration

**Scope**: Web form that collects email and password

**Assets**:
- User email (PII)
- User password (authentication)

**Threats**:
- Attacker submits malicious input (SQL injection) → TAMPERING
- Attacker intercepts password over HTTP → INFORMATION DISCLOSURE
- Attacker brute-forces weak passwords → AUTHENTICATION FAILURE
- Attacker scrapes email addresses → INFORMATION DISCLOSURE

**Mitigations**:
- Use parameterized queries
- Enforce HTTPS
- Implement rate limiting
- Require strong passwords
- Encrypt password in database (bcrypt)

---

## Module 4: Vulnerability Remediation

### 4.1: CodeQL Vulnerabilities

When CodeQL alerts fire, follow the corresponding runbook:

| Alert | Runbook | SLA |
|-------|---------|-----|
| `py/sql-injection` | SQL Injection Prevention | <2h |
| `py/hardcoded-secret` | Hardcoded Secrets Remediation | <1h |
| `py/xss` | XSS Prevention | <4h |
| `py/path-injection` | Path Traversal Prevention | <4h |

See: `docs/security/runbooks/SECURITY_RUNBOOK_INDEX.md`

### 4.2: CVE Response

When a CVE is announced:

1. Check if you use affected package
2. Assess CVSS score (9.0+ = Critical)
3. Follow corresponding runbook (Critical/High/Medium)
4. Update dependencies and test

### 4.3: Secret Compromise

If a secret (API key, password) is exposed:

1. **IMMEDIATELY** rotate in provider (AWS/GitHub/etc.)
2. Follow `RUNBOOK_CODEQL_HARDCODED_SECRETS.md`
3. Remove from git history
4. Notify affected teams

---

## Module 5: Incident Response

### 5.1: Incident Severity Levels

| Severity | Example | SLA | Response |
|----------|---------|-----|----------|
| Sev-1 | Active exploitation | <2 min | Page on-call, war room |
| Sev-2 | Unpatched vulnerability | <30 min | Alert security team |
| Sev-3 | Config problem | <4h | Log and schedule fix |

See: `RUNBOOK_INCIDENT_SEV*.md`

### 5.2: What to Do During an Incident

1. **Preserve Evidence**: Don't delete logs or make changes
2. **Follow the Runbook**: Execute steps in order
3. **Communicate**: Keep team informed
4. **Escalate**: Follow escalation paths
5. **Document**: Record timeline and actions

### 5.3: What NOT to Do During an Incident

❌ Don't panic  
❌ Don't make unauthorized system changes  
❌ Don't discuss on public channels  
❌ Don't delete evidence  
❌ Don't negotiate with attackers

---

## Module 6: Compliance & Regulations

### 6.1: GDPR (EU Data Protection)

- If you collect data from EU residents, you must comply
- Personal data must be protected from unauthorized access
- Data breach notification: <72 hours to authorities, <24 hours to individuals
- Runbook: `RUNBOOK_COMPLIANCE_GDPR.md`

### 6.2: CCPA (California Consumer Privacy)

- Covers California residents' personal information
- Consumers have rights: know, delete, opt-out, correct
- Requests must be fulfilled within 45 days
- Runbook: `RUNBOOK_COMPLIANCE_CCPA.md`

### 6.3: SOC2 (Service Organization Control)

- Auditor verifies your security controls
- CC6.1: Logical access controls
- CC7.2: System monitoring & logging
- A1.1: Backup & disaster recovery
- Runbook: `RUNBOOK_COMPLIANCE_SOC2.md`

---

## Module 7: Security Tools & Practices

### 7.1: Code Scanning Tools

| Tool | Purpose | Command |
|------|---------|---------|
| Bandit | Find Python security issues | `python -m bandit -r .` |
| Semgrep | Find pattern-based vulnerabilities | `semgrep --config=p/security-audit` |
| CodeQL | GitHub's static analysis | Runs automatically on every PR |
| Trivy | Scan dependencies for CVEs | `trivy fs .` |
| truffleHog | Find secrets in git history | `truffleHog filesystem .` |

### 7.2: Dependency Management

- Keep dependencies up to date
- Use Dependabot or Renovate for auto-updates
- Review CVEs before updating
- Run tests after updates

```bash
# Check for known vulnerabilities
pip install safety
safety check

# Update all packages
pip install -U -r requirements.txt
```

### 7.3: Secure Development Lifecycle

1. **Design**: Threat modeling
2. **Code**: Secure coding practices
3. **Test**: Security testing
4. **Deploy**: Secure deployment
5. **Monitor**: Continuous monitoring
6. **Respond**: Incident response

---

## Module 8: Self-Assessment

### Quiz Questions

1. **What is the difference between confidentiality and integrity?**
   - A) Same thing
   - B) Confidentiality = only authorized users see data; Integrity = data can't be tampered with
   - C) Confidentiality = fast; Integrity = slow
   
   **Answer**: B

2. **You find a hardcoded API key in production code. What do you do?**
   - A) Ignore it (probably not a real key)
   - B) Delete the file and commit
   - C) Immediately rotate the key in the provider, remove from code, purge from git history
   
   **Answer**: C

3. **Which is most secure?**
   - A) `query = f"SELECT * FROM users WHERE id = {user_id}"`
   - B) `query = "SELECT * FROM users WHERE id = " + str(user_id)`
   - C) `query = "SELECT * FROM users WHERE id = ?"; cursor.execute(query, (user_id,))`
   
   **Answer**: C

4. **GDPR breach notification deadline?**
   - A) 24 hours
   - B) 72 hours
   - C) 1 week
   
   **Answer**: B (72 hours to authorities)

5. **What should you do if you suspect an active attack?**
   - A) Wait and see if it continues
   - B) Post about it on social media
   - C) Immediately follow Sev-1 incident response runbook
   
   **Answer**: C

---

## Module 9: Resources & References

### Internal Resources
- Security Guidelines: `docs/security/SECURITY_GUIDELINES.md`
- Runbooks Index: `docs/security/runbooks/SECURITY_RUNBOOK_INDEX.md`
- Threat Model: `docs/security/THREAT_MODEL.md`

### External Resources
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE/CVSS: https://cwe.mitre.org/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- Security Cheat Sheets: https://cheatsheetseries.owasp.org/

### Tools
- Bandit (Python): https://bandit.readthedocs.io/
- Semgrep: https://semgrep.dev/
- CodeQL: https://codeql.github.com/
- Trivy: https://github.com/aquasecurity/trivy

---

## Certification & Completion

**To complete this training**:

1. ✅ Review all 9 modules
2. ✅ Complete Module 8 quiz (80%+ required to pass)
3. ✅ Review one runbook relevant to your role
4. ✅ Ask questions in #security channel

**Completion Time**: Expected 4-6 hours  
**Certificate Valid For**: 1 year  
**Renewal**: Required annually or after major security updates

**Submit completion**: [Training Dashboard Link]

---

## Appendix A: Common Security Mistakes

### Mistake #1: SQL Injection
```python
# WRONG
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# RIGHT
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (email,))
```

### Mistake #2: Storing Passwords
```python
# WRONG
users[email] = password  # Plain text!

# RIGHT
from werkzeug.security import generate_password_hash
users[email] = generate_password_hash(password, method='pbkdf2:sha256')
```

### Mistake #3: Hardcoded Secrets
```python
# WRONG
API_KEY = "sk_live_abc123xyz"

# RIGHT
import os
API_KEY = os.getenv('API_KEY')  # Load from environment
```

---

**Training Created**: 2026-07-18  
**Version**: 1.0.0  
**Maintained By**: Security Team
