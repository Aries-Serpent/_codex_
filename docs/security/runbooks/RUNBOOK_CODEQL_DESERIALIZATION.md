# Runbook: Insecure Deserialization Prevention (CWE-502)

**Severity**: CRITICAL  
**SLA**: <2 hours  
**Category**: CodeQL Alert Remediation  
**CWE**: CWE-502 - Deserialization of Untrusted Data  
**CVSS Score**: 9.8 (Critical)

---

## Overview

Insecure deserialization occurs when untrusted data is deserialized using unsafe methods. Attackers can inject malicious serialized objects to execute arbitrary code.

---

## Remediation Steps

### Step 1: Identify Deserialization
```bash
grep -r "pickle\|yaml.load\|json.loads" {file}
python -m bandit -r {file} -f csv | grep "deserial"
```

### Step 2: Use Safe Deserialization Methods

```python
# VULNERABLE: pickle with untrusted data
import pickle
data = pickle.loads(user_input)  # DANGEROUS

# VULNERABLE: unsafe yaml
import yaml
data = yaml.load(user_input)  # DANGEROUS

# SECURE: Use json (safe by default)
import json
data = json.loads(user_input)  # Safe

# SECURE: Use pickle with restricted classes
import pickle
import io

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == '__main__':
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Untrusted module: {module}")

data = RestrictedUnpickler(io.BytesIO(user_input)).load()
```

### Step 3: Validate Deserialized Data
```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    email: str

# SECURE: Validate after deserialization
data = json.loads(user_input)
try:
    user = User(**data)
except ValidationError as e:
    abort(400, f"Invalid data: {e}")
```

---

## Validation

```bash
# Ensure json used instead of pickle/yaml
grep -r "pickle.loads\|yaml.load" {file} && echo "FAILED" || echo "PASSED"

# Run security tests
pytest {test_file} -k "deserialization" -v
```

---

## References

- [OWASP Deserialization](https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data)
- [CWE-502](https://cwe.mitre.org/data/definitions/502.html)
