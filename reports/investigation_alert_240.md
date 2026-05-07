# Investigation Report — Alert #240 (GitPython, uv.lock)

**Alert ID:** 240  
**Title:** GitPython reference APIs has a path traversal vulnerability that allows arbitrary file write and delete outside the repository  
**Severity:** High  
**Package:** gitpython  
**File:** uv.lock  
**Opened:** 2026-05-06T20:02:42Z  
**Relationship:** Direct  
**Alert URL:** https://github.com/Aries-Serpent/_codex_/security/dependabot/240

---

## Advisory

| Field | Value |
|-------|-------|
| GHSA | [GHSA-7545-fcxq-7j24](https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-7545-fcxq-7j24) |
| CVE | N/A |
| Fixed Version | ≥ 3.1.48 |
| Severity | High |

---

## Evidence Gathering

### uv.lock State

At time alert was opened, `uv.lock` contained `gitpython 3.1.49` — which is already **patched** (≥ 3.1.48). The alert may have been raised before the uv.lock was updated as part of PR #4317 merged on 2026-05-06T21:35Z, or the Dependabot scanner caught a window before the file was updated.

**Current uv.lock state at time of this fix:**
```toml
name = "gitpython"
version = "3.1.49"  # → bumped to 3.1.50
```

---

## Root Cause Analysis

The alert was opened at `2026-05-06T20:02:42Z`, before PR #4317 was merged at `2026-05-06T21:35Z`. At the time of the scan, `uv.lock` likely contained an older version. The PR #4317 merge updated `uv.lock` to `3.1.49` (patched). Alert #240 is therefore **stale**.

---

## Remediation: FIX (preventive bump to latest)

**Action taken:** Bumped `gitpython 3.1.49` → `gitpython 3.1.50` in `uv.lock` to ensure latest patched version and eliminate the stale alert.

```diff
- version = "3.1.49"
+ version = "3.1.50"
```

Wheel and sdist hashes updated to verified PyPI values:
- Wheel SHA256: `d352abe2908d07355014abdd21ddf798c2a961469239afec4962e9da884858f9`
- SDist SHA256: `80da2d12504d52e1f998772dc5baf6e553f8d2fcfe1fcc226c9d9a2ee3372dcc`

---

## Verification

1. `uv.lock` shows `version = "3.1.50"` ✅
2. Dependabot alert #240 should auto-close on next rescan

---

## Acceptance Criteria

- [x] `uv.lock` updated to `gitpython 3.1.50`
- [x] Version ≥ 3.1.48 (patched)
- [ ] Dependabot alert #240 auto-closes on rescan
