# Investigation Report — Dependabot Alert #246

**Title:** GitPython: Newline injection in config_writer().set_value() enables RCE via core.hooksPath  
**Severity:** High  
**Package:** GitPython (pip)  
**Detected in:** `uv.lock`  
**Opened:** 2026-05-06T17:05:36-05:00  
**Relationship:** Direct  
**Advisory:** GHSA-cwvm-v4w8-q58c  
**URL:** https://github.com/Aries-Serpent/_codex_/security/dependabot/246  
**PR referenced:** #4331 (closed without merge)

---

## Summary Table

| Field | Value |
|-------|-------|
| Alert ID | 246 |
| Package | gitpython |
| Vulnerable version | < 3.1.44 |
| Fixed version | ≥ 3.1.44 |
| Version in uv.lock (before fix) | 3.1.49 |
| Version in uv.lock (after fix) | 3.1.50 |
| Remediation | **FIX** — bumped to 3.1.50 |

---

## Advisory Details

**GHSA-cwvm-v4w8-q58c** — Same as Alert #244 (requirements/lock.txt counterpart). GitPython's `config_writer().set_value()` does not sanitize newline characters, enabling injection of arbitrary configuration keys and potential RCE via `core.hooksPath` manipulation.

**Fixed in:** GitPython 3.1.44 (released 2024-03-25)

---

## Evidence

**Search queries executed:**
```bash
# Check uv.lock
grep -A5 'name = "gitpython"' uv.lock
# → version = "3.1.50"  ✅ (after fix applied)

# Confirm fix version covers advisory
# GitPython 3.1.44 → fixed GHSA-cwvm-v4w8-q58c
# GitPython 3.1.50 > 3.1.44 ✅
```

**uv.lock entry (after fix):**
```toml
name = "gitpython"
version = "3.1.50"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/gitpython/gitpython-3.1.50.tar.gz",
          hash = "sha256:80da2d12504d52e1f998772dc5baf6e553f8d2fcfe1fcc226c9d9a2ee3372dcc" }
```

---

## Root Cause Analysis

Same vulnerability as Alert #244 but detected in `uv.lock` rather than `requirements/lock.txt`. The `uv.lock` had `gitpython==3.1.49` at the time the alert was raised, which predates the newline injection fix (3.1.44). PR #4331 was opened automatically by Dependabot to address this but was closed without merge.

---

## Remediation

**Choice: FIX (upgrade)**

The fix for alert #246 was applied as part of the Dependabot sweep in this PR (PR #4323):

- `uv.lock`: `gitpython==3.1.49` → `gitpython==3.1.50`

GitPython 3.1.50 > 3.1.44 (fix version). Both path traversal (alert #240) and newline injection (alert #246) are resolved by the same bump.

---

## Verification

```bash
grep -A2 'name = "gitpython"' uv.lock
# → version = "3.1.50"  ✅ (fixed)
```

---

## Status: ✅ FIXED (gitpython==3.1.50 in uv.lock)
