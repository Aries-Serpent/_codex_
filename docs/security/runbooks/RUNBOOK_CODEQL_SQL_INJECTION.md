# Runbook: SQL Injection Prevention & Remediation (CWE-89)

**Severity**: CRITICAL  
**SLA**: <2 hours for critical findings  
**Category**: CodeQL Alert Remediation  
**CWE**: CWE-89 - Improper Neutralization of Special Elements used in an SQL Command  
**CVSS Score**: 9.8 (Critical)

---

## Overview

SQL Injection vulnerabilities occur when user-controlled input is concatenated directly into SQL queries without proper sanitization or parameterization. This allows attackers to execute arbitrary SQL commands, potentially leading to unauthorized data access, modification, or deletion.

---

## Trigger Conditions

This runbook is activated when:
1. CodeQL detector `py/sql-injection` fires (CWE-89)
2. Log signature: `SQL query|query injection|SQL injection` detected
3. User input flows directly into SQL query without parameterization

---

## Remediation Steps

### Step 1: Identify the Vulnerability
```bash
python -m bandit -r {file} -f csv | grep "SQL"
codeql database analyze /tmp/codeql_db --format=json | grep "SQL injection"
```

### Step 2: Replace with Parameterized Query
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_input}"
cursor.execute(query)

# SECURE
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_input,))
```

### Step 3: Validate the Fix
```bash
ruff check --select E501 {file}
pytest {test_file} -k "sql_injection" -v
```

### Step 4: Code Review Checklist
- [ ] All user inputs are parameterized
- [ ] No f-strings or string formatting for SQL
- [ ] ORM used where possible
- [ ] Input validation in place
- [ ] Tests verify parameterization
- [ ] No dynamic table/column names without validation

---

## Automated Remediation

**Pattern ID**: RP-6001  
**Handler**: `handlers.security_handlers.remediate_sql_injection`  
**Confidence**: HIGH (96%)

---

## Escalation Path

Automatic escalation for:
- Parameterization cannot be applied
- Query spans multiple files
- Legacy code with minimal tests
- Security team review required

---

## Related Patterns

- RP-6002: Hardcoded Secrets Remediation
- RP-6003: Database Connection Security
- RP-6004: Input Validation

---

## References

- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [CWE-89](https://cwe.mitre.org/data/definitions/89.html)
