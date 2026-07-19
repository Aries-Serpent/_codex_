# Runbook: Path Traversal Prevention & Remediation (CWE-22)

**Severity**: HIGH  
**SLA**: <4 hours  
**Category**: CodeQL Alert Remediation  
**CWE**: CWE-22 - Improper Limitation of a Pathname to a Restricted Directory  
**CVSS Score**: 7.5 (High)

---

## Overview

Path Traversal vulnerabilities allow attackers to access files outside the intended directory by using path traversal sequences like `../` or absolute paths. This can lead to unauthorized file access or overwrite.

---

## Remediation Steps

### Step 1: Identify Vulnerability
```bash
grep -r "open\|read\|write" {file} | grep -E "\+|\.format|f\""
python -m bandit -r {file} -f csv | grep "path"
```

### Step 2: Sanitize Path Input

```python
# VULNERABLE
user_file = request.args.get('file')
with open(f'/uploads/{user_file}') as f:
    return f.read()

# SECURE: Validate path is within allowed directory
import os
from pathlib import Path

ALLOWED_DIR = Path('/uploads')
user_file = request.args.get('file')

# Remove any path traversal attempts
safe_path = Path(ALLOWED_DIR) / user_file
safe_path = safe_path.resolve()  # Resolve symlinks

# Verify path is within allowed directory
if not str(safe_path).startswith(str(ALLOWED_DIR.resolve())):
    abort(403)  # Forbidden

with open(safe_path) as f:
    return f.read()
```

### Step 3: Use Path Validation Libraries
```python
from pathvalidate import ValidationError, validate_filepath

try:
    validate_filepath(user_file, platform='auto')
    safe_path = Path(ALLOWED_DIR) / user_file
except ValidationError:
    abort(400)  # Bad request
```

---

## Validation

```bash
# Test path traversal doesn't work
pytest {test_file} -k "path_traversal" -v

# Verify no ../ in file paths
grep -r "\\.\\." {file} | grep -v "range\|test"
```

---

## References

- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [CWE-22](https://cwe.mitre.org/data/definitions/22.html)
