# Investigation Report — Alert #242 (Mako, uv.lock)

**Alert ID:** 242  
**Title:** Mako vulnerable to path traversal via backslash URI on Windows in TemplateLookup  
**Severity:** High  
**Package:** Mako  
**File:** uv.lock  
**Opened:** 2026-05-06T21:54:00Z  
**Relationship:** Direct  
**Alert URL:** https://github.com/Aries-Serpent/_codex_/security/dependabot/242

---

## Advisory

| Field | Value |
|-------|-------|
| GHSA | [GHSA-v92g-xgxw-vvmm](https://github.com/sqlalchemy/mako/security/advisories/GHSA-v92g-xgxw-vvmm) |
| CVE | CVE-2026-41205 |
| Fixed Version | ≥ 1.3.11 |
| Severity | High |

---

## Evidence Gathering

`uv.lock` at the time of this session already contains `mako 1.3.12` (patched). The alert was opened at `2026-05-06T21:54:00Z` — likely based on a stale Dependabot scan of a pre-merge version of the file.

**Current uv.lock state:**
```toml
name = "mako"
version = "1.3.12"  # already patched ≥1.3.11
```

---

## Root Cause Analysis

Alert #242 is **stale**. `uv.lock` already contains `mako 1.3.12` which satisfies the ≥1.3.11 fix requirement. No changes needed in `uv.lock` for Mako.

---

## Remediation: NONE REQUIRED (already patched)

`uv.lock` mako is already at `1.3.12` — no action taken. Dependabot should auto-close this alert on its next rescan.

---

## Acceptance Criteria

- [x] `uv.lock` shows `mako 1.3.12` (already present)
- [ ] Dependabot alert #242 auto-closes on rescan
