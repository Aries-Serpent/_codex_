# Runbook: XSS Prevention & Remediation (CWE-79)

**Severity**: HIGH  
**SLA**: <4 hours  
**Category**: CodeQL Alert Remediation  
**CWE**: CWE-79 - Improper Neutralization of Input During Web Page Generation  
**CVSS Score**: 7.1 (High)

---

## Overview

Cross-Site Scripting (XSS) vulnerabilities allow attackers to inject malicious JavaScript code into web pages viewed by other users. XSS can be used to steal cookies, hijack sessions, or perform actions on behalf of users.

---

## Trigger Conditions

CodeQL alert: `js/xss` or `py/xss` fired  
Pattern: User input displayed in HTML without escaping  
Affected: Web templates, API responses, DOM updates

---

## Remediation Steps

### Step 1: Identify XSS Source
```bash
grep -r "innerHTML\|innerText" {file} | grep -v "textContent"
grep -r "eval\|Function\|setTimeout.*code" {file}
python -m bandit -r {file} -f csv | grep "xss\|injection"
```

### Step 2: Apply Context-Appropriate Escaping

**HTML Context**:
```python
# VULNERABLE
return f"<div>{user_input}</div>"

# SECURE: HTML escape
from html import escape
return f"<div>{escape(user_input)}</div>"
```

**JavaScript Context**:
```python
# VULNERABLE
return f"<script>var user = '{user_input}';</script>"

# SECURE: JSON encode
import json
return f"<script>var user = {json.dumps(user_input)};</script>"
```

**URL Context**:
```python
# VULNERABLE
return f"<a href='/search?q={user_input}'>Link</a>"

# SECURE: URL encode
from urllib.parse import quote
return f"<a href='/search?q={quote(user_input)}'>Link</a>"
```

### Step 3: Use Template Auto-Escaping
```python
# Jinja2 (auto-escaping enabled)
env = Environment(autoescape=True)

# Django templates (auto-escape by default)
{{ user_input }}  # Safe: auto-escaped

# FastAPI templates
return templates.TemplateResponse("template.html", {"user": user_input})
```

### Step 4: Content Security Policy
```html
<!-- In HTTP header or meta tag -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'">
```

---

## Validation

```bash
# Verify escaping is applied
grep -E "escape\(|quote\(|json.dumps\(" {file}

# Test XSS payloads don't execute
pytest {test_file} -k "xss" -v
```

---

## Escalation Path

Escalate for:
- DOM-based XSS in JavaScript
- Complex template escaping requirements
- Custom escaping functions

---

## Related Patterns

- RP-6003: XSS Prevention
- RP-6004: Input Validation

---

## References

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [CWE-79](https://cwe.mitre.org/data/definitions/79.html)
