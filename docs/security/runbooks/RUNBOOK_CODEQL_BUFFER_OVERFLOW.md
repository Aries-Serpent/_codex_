# Runbook: Buffer Overflow Prevention (CWE-119)

**Severity**: CRITICAL  
**SLA**: <2 hours  
**Category**: CodeQL Alert Remediation  
**CWE**: CWE-119 - Improper Restriction of Operations within the Bounds of a Memory Buffer  
**CVSS Score**: 9.8 (Critical)

---

## Overview

Buffer overflows occur when code writes more data to a buffer than its allocated size, potentially overwriting adjacent memory. This can lead to code execution or denial of service.

---

## Trigger Conditions

CodeQL alerts: `cpp/buffer-overflow`, `c/buffer-overflow`  
Patterns: Fixed-size arrays, unbounded copy operations, pointer arithmetic errors

---

## Remediation Steps

### Step 1: Identify Buffer Operations
```bash
grep -r "strcpy\|memcpy\|sprintf" {file} | grep -v "strncpy\|snprintf"
codeql database analyze --format=json | grep "buffer"
```

### Step 2: Use Safe Functions

```c
// VULNERABLE
char buffer[50];
strcpy(buffer, user_input);  // No bounds checking

// SECURE
char buffer[50];
strncpy(buffer, user_input, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';

// VULNERABLE
sprintf(buffer, "%s", user_input);

// SECURE
snprintf(buffer, sizeof(buffer), "%s", user_input);

// VULNERABLE
memcpy(dest, src, user_length);  // user_length not validated

// SECURE
size_t max_size = sizeof(dest);
size_t copy_size = user_length < max_size ? user_length : max_size;
memcpy(dest, src, copy_size);
```

### Step 3: Use High-Level Languages
- Python, Java, Go: Automatic bounds checking
- Rust: Compile-time memory safety
- Modern C++: Use std::string, std::vector

### Step 4: Input Validation
```c
// Validate input size before operations
if (strlen(user_input) >= sizeof(buffer)) {
    return -1;  // Error: input too large
}
```

---

## Validation

```bash
# Scan for unsafe functions
grep -E "strcpy|sprintf|gets|scanf" {file} && echo "FAILED" || echo "PASSED"

# Run memory safety analysis
clang --analyze {file}
```

---

## References

- [CWE-119](https://cwe.mitre.org/data/definitions/119.html)
- [Buffer Overflow Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Buffer_Overflow_Prevention_Cheat_Sheet.html)
