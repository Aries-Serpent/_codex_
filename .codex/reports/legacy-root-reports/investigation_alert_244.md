# Investigation Report — Dependabot Alert #244

**Title:** GitPython: Newline injection in config_writer().set_value() enables RCE via core.hooksPath  
**Severity:** High  
**Package:** GitPython (pip)  
**Detected in:** `requirements/lock.txt`  
**Opened:** 2026-05-06T17:05:36-05:00  
**Relationship:** Direct  
**Advisory:** GHSA-cwvm-v4w8-q58c (Newline injection in `config_writer().set_value()`)  
**URL:** https://github.com/Aries-Serpent/_codex_/security/dependabot/244

---

## Summary Table

| Field | Value |
|-------|-------|
| Alert ID | 244 |
| Package | gitpython |
| Vulnerable version | < 3.1.44 |
| Fixed version | ≥ 3.1.44 |
| Version in lock.txt (before fix) | 3.1.45 |
| Version in lock.txt (after fix) | 3.1.50 |
| Remediation | **FIX** — bumped to 3.1.50 |

---

## Advisory Details

**GHSA-cwvm-v4w8-q58c** — GitPython `config_writer().set_value()` allows a newline character to be injected into a configuration key or value. An attacker who controls the value of a git config key (e.g., via a malicious repository) can set `core.hooksPath` to an attacker-controlled directory, achieving Remote Code Execution (RCE) by placing a hook script there.

**Fixed in:** GitPython 3.1.44 (released 2024-03-25)

---

## Evidence

**Search queries executed:**
```bash
grep -n "gitpython" requirements/lock.txt
# → gitpython==3.1.45  (vulnerable — before fix)
# → gitpython==3.1.50  (after fix applied in this PR)

grep -rn "import git\|from git import" src/ tests/ | head -10
```

**Files referencing GitPython:**
- `requirements/lock.txt` (direct dependency, line 311)
- `uv.lock` (see alert #246 for uv.lock counterpart)

---

## Root Cause Analysis

GitPython's `config_writer` did not sanitize newline characters before writing configuration values. This allowed injection of arbitrary `[section]` blocks into `.git/config`, enabling an attacker to override `core.hooksPath` and trigger hook execution during normal `git` operations.

---

## Remediation

**Choice: FIX (upgrade)**

Alert #244 was associated with PR #4330 (closed without merge). The fix was cherry-picked directly into this PR (PR #4323):

- `requirements/lock.txt`: `gitpython==3.1.45` → `gitpython==3.1.50`

GitPython 3.1.50 > 3.1.44 (fix version) — the newline injection is not present in 3.1.50.

---

## Verification

```bash
grep "gitpython" requirements/lock.txt
# → gitpython==3.1.50  ✅ (fixed)
```

Both path traversal (alerts #239) and newline injection (alert #244) are resolved by the same bump to 3.1.50.

---

## Status: ✅ FIXED (gitpython==3.1.50 in requirements/lock.txt)
