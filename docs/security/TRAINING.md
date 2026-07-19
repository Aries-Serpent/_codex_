# Security Training Resources

**For**: All Developers & Engineers  
**Duration**: 4-6 hours self-paced  
**Purpose**: Build secure coding skills and vulnerability awareness

---

## Quick Start

1. **New to security?** Start with [Fundamentals](#security-fundamentals)
2. **Fixing a vulnerability?** Check [Vulnerability Remediation](#vulnerability-remediation)
3. **Responding to incident?** See [Incident Response](#incident-response)
4. **Compliance question?** Review [Compliance Guide](#compliance--regulations)

---

## Security Fundamentals

### The Three Pillars of Security

**Confidentiality**: Keep sensitive information private
- Passwords should not be readable by unauthorized users
- API keys should not be in source code
- PII should be encrypted at rest

**Integrity**: Ensure data is not tampered with
- Database transactions should be atomic
- Files should not be modifiable by attackers
- Code should only be changed by authorized developers

**Availability**: Systems should be accessible when needed
- Websites should not go down
- APIs should respond quickly
- Data should not be lost

### OWASP Top 10 Vulnerabilities

**1. Broken Access Control** - Users access resources they shouldn't  
**2. Cryptographic Failures** - Sensitive data not properly encrypted  
**3. Injection** - SQL injection, command injection, etc.  
**4. Insecure Design** - Security not built into design phase  
**5. Security Misconfiguration** - Default credentials, open ports  
**6. Vulnerable & Outdated Components** - Old libraries with known CVEs  
**7. Authentication Failures** - Weak passwords, no MFA  
**8. Software & Data Integrity Failures** - Malicious code in dependencies  
**9. Logging & Monitoring Failures** - Attacks not detected  
**10. SSRF** - Server-Side Request Forgery attacks  

---

## Secure Coding Practices

### Rule #1: Validate Input

Always check that user input is what you expect:

```python
# Good: Validate email format
import re
email = request.get('email')
if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
    raise ValueError("Invalid email")

# Bad: No validation
name = request.get('name')
greeting = f"Hello {name}!"  # What if name = "<script>alert('xss')</script>"?
```

### Rule #2: Use Parameterized Queries

Never build SQL queries by concatenating strings:

```python
# Good: Use ? placeholders
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (email,))

# Good: Use ORM
user = User.objects.get(email=email)

# Bad: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL injection!
cursor.execute(query)
```

### Rule #3: Encode Output

Encode data based on context:

```python
# Good: HTML escaping for HTML context
from html import escape
html = f"<p>{escape(user_input)}</p>"

# Good: JSON encoding for JavaScript context
import json
js = f"<script>var data = {json.dumps(user_input)};</script>"

# Good: URL encoding for URL context
from urllib.parse import quote
url = f"?search={quote(user_input)}"

# Bad: No encoding
html = f"<p>{user_input}</p>"  # XSS vulnerability!
```

### Rule #4: Use HTTPS

Always encrypt data in transit:

```python
# Good: HTTPS
response = requests.get('https://api.example.com/users')

# Bad: HTTP
response = requests.get('http://api.example.com/users')  # Data in plain text!
```

### Rule #5: Never Hardcode Secrets

Never commit API keys, passwords, or tokens to git:

```python
# Good: Load from environment
import os
API_KEY = os.getenv('API_KEY')  # Load from environment variable
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Bad: Hardcoded secret
API_KEY = "sk_live_abc123xyz"  # This will be compromised!
DB_PASSWORD = "admin123"
```

### Rule #6: Implement Authentication

Protect endpoints that handle sensitive data:

```python
# Good: Require authentication
from flask_login import login_required

@app.route('/profile')
@login_required
def profile():
    return f"Welcome {current_user.email}"

# Bad: No authentication
@app.route('/admin')
def admin():
    return render('admin_panel.html')  # Anyone can access!
```

### Rule #7: Use Password Hashing

Never store plain-text passwords:

```python
# Good: Use bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
hashed = generate_password_hash('password123', method='pbkdf2:sha256')
if check_password_hash(hashed, 'password123'):
    print("Password matches!")

# Bad: Plain text
users[email] = password  # DON'T DO THIS!

# Bad: Weak hashing
import hashlib
hashed = hashlib.md5(password).hexdigest()  # MD5 is broken!
```

---

## Vulnerability Remediation

### When CodeQL Alerts Fire

CodeQL runs automatically on every PR and alerts you to security issues. **Do not ignore these alerts!**

**High-severity alerts must be fixed before merging.**

### Common CodeQL Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| SQL Injection | User input in SQL query | Use parameterized queries with ? |
| Hardcoded Secret | Secret in source code | Load from environment variables |
| XSS | Unescaped user input in HTML | Escape HTML entities |
| Path Traversal | User input in file path | Validate path is within allowed directory |
| Hardcoded Password | Password in source code | Use environment variable or secret manager |
| Weak Cryptography | Using MD5/SHA1 | Use SHA-256 or bcrypt |

See: [Security Runbook Index](../runbooks/SECURITY_RUNBOOK_INDEX.md)

### CVE (Vulnerability) Response

When a CVE is announced in one of your dependencies:

1. **Assess Severity**: Check CVSS score
2. **Check Affected**: Does your project use that package/version?
3. **Update**: Run `pip install --upgrade vulnerable_package`
4. **Test**: Run full test suite
5. **Deploy**: Follow the update to production

**SLAs**:
- Critical (CVSS 9-10): Fix within 4 hours
- High (CVSS 7-8): Fix within 24 hours
- Medium (CVSS 4-6): Fix within 48 hours

See: [CVE Response Runbooks](../runbooks/SECURITY_RUNBOOK_INDEX.md#cve-response-procedures)

---

## Incident Response

### If You Suspect a Security Breach

**DO**:
1. ✅ Preserve evidence (don't delete logs)
2. ✅ Notify the security team immediately
3. ✅ Follow the incident runbook
4. ✅ Document what you did

**DON'T**:
1. ❌ Delete logs or make changes to cover it up
2. ❌ Post about it on social media
3. ❌ Negotiate with attackers
4. ❌ Ignore alerts

### Incident Severity Levels

| Level | Example | Response Time |
|-------|---------|-----------------|
| **Sev-1** (Critical) | Active attack, data breach | <2 minutes |
| **Sev-2** (High) | Unpatched vulnerability | <30 minutes |
| **Sev-3** (Medium) | Configuration issue | <4 hours |

See: [Incident Response Runbooks](../runbooks/SECURITY_RUNBOOK_INDEX.md#incident-response--escalation)

---

## Compliance & Regulations

### GDPR (EU Data Protection)

**Applies if**: You collect data from people in the EU

**Key Rules**:
- Get explicit consent before collecting data
- Protect personal data from unauthorized access
- Notify people within 24 hours if their data is breached
- Notify authorities within 72 hours of discovering a breach

**What is Personal Data?** Names, emails, phone numbers, addresses, IP addresses, cookies, etc.

See: [GDPR Runbook](../runbooks/SECURITY_RUNBOOK_INDEX.md#compliance-violation-remediation)

### CCPA (California Consumer Privacy)

**Applies if**: You collect data from California residents

**Key Rules**:
- Consumers can request to see their data
- Consumers can request deletion of their data
- Consumers can opt out of data sales
- You have 45 days to fulfill requests

See: [CCPA Runbook](../runbooks/SECURITY_RUNBOOK_INDEX.md#compliance-violation-remediation)

### SOC2 (Security Audit Standard)

**Applies if**: Your company is SOC2 certified or audited

**Key Controls**:
- Access control: Only authorized people can access systems
- Monitoring: Security events are logged and monitored
- Backups: Data is backed up and can be restored
- Incident response: Security incidents are handled properly

---

## Security Tools & Commands

### Check for Vulnerabilities

```bash
# Check Python dependencies for known CVEs
pip install safety
safety check

# Scan code for security issues
python -m bandit -r .

# Find hardcoded secrets
truffleHog filesystem .

# Scan dependencies for CVEs
pip install trivy
trivy fs .

# Check for common security issues
semgrep --config=p/security-audit
```

### Keep Dependencies Updated

```bash
# List packages with known vulnerabilities
pip install pip-audit
pip-audit

# Update all packages
pip install -U -r requirements.txt

# Check what will break
pip install --dry-run -U -r requirements.txt
```

### Generate Secure Passwords

```bash
# Generate random password
openssl rand -base64 32

# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/id_rsa
```

---

## Glossary

**API Key**: Secret token for authenticating with a service  
**CVSS**: Common Vulnerability Scoring System (0-10 scale)  
**CVE**: Common Vulnerabilities and Exposures identifier  
**Encryption**: Converting data to unreadable form to protect it  
**Hash**: One-way function to verify data integrity  
**MFA**: Multi-Factor Authentication (password + additional verification)  
**OAuth**: Secure way to grant access without sharing passwords  
**PII**: Personally Identifiable Information (names, emails, SSNs, etc.)  
**SQL Injection**: Inserting malicious SQL into queries  
**XSS**: Cross-Site Scripting (injecting JavaScript into web pages)  

---

## Getting Help

- **Security Questions**: Post in #security Slack channel
- **Incident Report**: Email security@company.com
- **Training Support**: security-training@company.com
- **CodeQL Help**: See GitHub CodeQL documentation

---

## Additional Resources

### Internal
- [Security Guidelines](SECURITY_GUIDELINES.md)
- [Threat Model](THREAT_MODEL.md)
- [Incident Response Plan](incident_response.md)
- [Security Runbooks](runbooks/SECURITY_RUNBOOK_INDEX.md)

### External
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices/)
- [CWE (Common Weakness Enumeration)](https://cwe.mitre.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [PortSwigger Web Security](https://portswigger.net/web-security)

---

**Last Updated**: 2026-07-18  
**Version**: 1.0.0  
**Questions?** security@company.com
