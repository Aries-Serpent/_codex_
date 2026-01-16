# IP-005: Dependency Security Audit Report

**Date**: 2026-01-16
**Audit Tool**: pip-audit v2.10.0
**Status**: COMPLETE

## Executive Summary

pip-audit detected **26 known vulnerabilities** across **11 packages**. Most are medium-severity issues that should be addressed in the next dependency update cycle.

## Vulnerabilities by Package

### 🔴 High Priority (Security-Critical)

| Package | Version | CVE | Severity | Fixed Version | Impact |
|---------|---------|-----|----------|---------------|--------|
| cryptography | 41.0.7 | CVE-2024-26130 | High | 42.0.4 | NULL pointer dereference |
| cryptography | 41.0.7 | CVE-2023-50782 | High | 42.0.0 | TLS RSA key exposure |
| jinja2 | 3.1.2 | CVE-2024-56326 | High | 3.1.5 | RCE via sandbox escape |
| jinja2 | 3.1.2 | CVE-2024-56201 | High | 3.1.5 | Arbitrary code execution |
| setuptools | 68.1.2 | CVE-2025-47273 | High | 78.1.1 | Path traversal RCE |
| setuptools | 68.1.2 | CVE-2024-6345 | High | 70.0.0 | Remote code execution |

### 🟡 Medium Priority

| Package | Version | CVE | Severity | Fixed Version | Impact |
|---------|---------|-----|----------|---------------|--------|
| certifi | 2023.11.17 | CVE-2024-39689 | Medium | 2024.7.4 | Root cert trust issue |
| configobj | 5.0.8 | CVE-2023-26112 | Medium | 5.0.9 | ReDoS |
| filelock | 3.20.0 | CVE-2025-68146 | Medium | 3.20.1 | TOCTOU symlink attack |
| filelock | 3.20.0 | CVE-2026-22701 | Medium | 3.20.3 | SoftFileLock TOCTOU |
| idna | 3.6 | CVE-2024-3651 | Medium | 3.7 | DoS via quadratic complexity |
| pip | 24.0 | CVE-2025-8869 | Medium | 25.3 | Tar symlink vulnerability |
| requests | 2.31.0 | CVE-2024-35195 | Medium | 2.32.0 | TLS verification bypass |
| requests | 2.31.0 | CVE-2024-47081 | Medium | 2.32.4 | .netrc credential leak |
| twisted | 24.3.0 | CVE-2024-41810 | Medium | 24.7.0 | XSS in redirectTo |
| twisted | 24.3.0 | CVE-2024-41671 | Medium | 24.7.0 | HTTP pipelining issue |
| urllib3 | 2.0.7 | CVE-2024-37891 | Medium | 2.2.2 | Proxy-Authorization leak |
| urllib3 | 2.0.7 | CVE-2025-50181 | Medium | 2.5.0 | Redirect handling issue |

### 🟢 Low Priority

| Package | Version | CVE | Severity | Fixed Version | Impact |
|---------|---------|-----|----------|---------------|--------|
| jinja2 | 3.1.2 | CVE-2024-22195 | Low | 3.1.3 | XSS via xmlattr |
| jinja2 | 3.1.2 | CVE-2024-34064 | Low | 3.1.4 | XSS via xmlattr |
| jinja2 | 3.1.2 | CVE-2025-27516 | Low | 3.1.6 | Sandbox escape via |attr |
| cryptography | 41.0.7 | CVE-2024-0727 | Low | 42.0.2 | PKCS12 DoS |

## Recommended Actions

### Immediate (This Week)
1. Upgrade `cryptography` to >=43.0.1
2. Upgrade `jinja2` to >=3.1.6
3. Upgrade `setuptools` to >=78.1.1

### Short Term (This Sprint)
4. Upgrade `certifi` to >=2024.7.4
5. Upgrade `filelock` to >=3.20.3
6. Upgrade `idna` to >=3.7
7. Upgrade `requests` to >=2.32.4
8. Upgrade `urllib3` to >=2.6.3
9. Upgrade `pip` to >=25.3

### Medium Term (Next Release)
10. Upgrade `twisted` to >=24.7.0
11. Upgrade `configobj` to >=5.0.9

## Requirements File Updates

The following changes are recommended for `requirements.txt` or `pyproject.toml`:

```toml
# Updated versions for security fixes
cryptography>=43.0.1
jinja2>=3.1.6
setuptools>=78.1.1
certifi>=2024.7.4
filelock>=3.20.3
idna>=3.7
requests>=2.32.4
urllib3>=2.6.3
```

## Notes

1. Some vulnerabilities (like filelock TOCTOU) require specific attack conditions
2. Most XSS issues in jinja2 require untrusted template content
3. The twisted vulnerabilities require specific server configurations
4. cryptography issues mostly affect PKCS12 handling

## Audit Artifacts

- Full JSON report available at: `.codex/qa_walkthrough/ip005_pip_audit_report.json`
- This summary: `.codex/plans/IP-005_DEPENDENCY_AUDIT.md`

## Status

**IP-005**: ✅ COMPLETE (Audit performed, recommendations documented)
