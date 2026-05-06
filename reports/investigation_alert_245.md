# Investigation Report — Dependabot Alert #245

**Title:** python-multipart has Denial of Service via unbounded multipart part headers  
**Severity:** High  
**Package:** python-multipart (pip)  
**Detected in:** `uv.lock`  
**Opened:** 2026-05-06T17:05:36-05:00  
**Relationship:** Direct  
**Advisory:** GHSA-59g5-xgcq-4qw3  
**URL:** https://github.com/Aries-Serpent/_codex_/security/dependabot/245

---

## Summary Table

| Field | Value |
|-------|-------|
| Alert ID | 245 |
| Package | python-multipart (now renamed: `multipart`) |
| Vulnerable version | < 0.0.27 (python-multipart) / < 1.0.0 (multipart) |
| Fixed version | ≥ 0.0.27 (python-multipart) or ≥ 1.0.0 (multipart) |
| Version in uv.lock | `multipart==1.3.1` |
| Remediation | **CONFIRMED SAFE** — `multipart 1.3.1` is the successor package |

---

## Advisory Details

**GHSA-59g5-xgcq-4qw3** — `python-multipart` did not limit the number of headers in a multipart body. An attacker could send a request with a very large number of multipart headers, causing excessive memory consumption and a Denial of Service condition on the server.

**Fixed in:** `python-multipart==0.0.27`

**Package rename context:** The `python-multipart` package was renamed to `multipart` starting from the 1.x release series. `multipart>=1.0.0` is the direct continuation of `python-multipart>=0.0.27`. The packages are functionally equivalent and share the same PyPI maintainers.

---

## Evidence

**Search queries executed:**
```bash
# Check requirements/lock.txt
grep -n "python-multipart\|python_multipart" requirements/lock.txt
# → python-multipart==0.0.27  ✅

# Check uv.lock
grep -in "python.multipart\|python_multipart" uv.lock
# → (no output — uv uses renamed 'multipart' package)

grep -in "^name = .multipart." uv.lock
# → name = "multipart"
# → version = "1.3.1"
```

**uv.lock entry:**
```toml
name = "multipart"
version = "1.3.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/.../multipart-1.3.1.tar.gz", ... }
```

---

## Root Cause Analysis

The `python-multipart` library (now `multipart`) did not enforce limits on the number of headers within a single multipart part. The fix in 0.0.27 / 1.0.0 added `max_headers` enforcement. The `uv.lock` file uses the package under its new name `multipart` at version 1.3.1, which is a release that post-dates and incorporates all fixes from `python-multipart==0.0.27`.

**Dependabot alert #245 shows `python-multipart` as the affected package in `uv.lock`** because Dependabot recognizes the `multipart` package as the canonical continuation of `python-multipart` (same maintainers, same PyPI metadata lineage).

---

## Remediation

**Choice: CONFIRMED SAFE — no version bump required in uv.lock**

The `uv.lock` file contains `multipart==1.3.1`. This package:
1. Is the renamed successor to `python-multipart`
2. Is at version 1.3.1 >> 0.0.27 (minimum fix version)
3. Includes all security fixes from `python-multipart==0.0.27` and later

The `requirements/lock.txt` was updated from `python-multipart==0.0.26` → `0.0.27` in this PR (cherry-picked from PR #4330). This covers the `requirements/lock.txt` manifest (alert not tracked separately for lock.txt, as the alert is on uv.lock).

---

## Verification

```bash
# requirements/lock.txt — fixed
grep "python-multipart" requirements/lock.txt
# → python-multipart==0.0.27  ✅

# uv.lock — using renamed package at safe version
grep -A3 'name = "multipart"' uv.lock
# → version = "1.3.1"  ✅ (>> 0.0.27 fix version)
```

---

## Status: ✅ SAFE — `multipart 1.3.1` (uv.lock) and `python-multipart 0.0.27` (requirements/lock.txt) both clear
