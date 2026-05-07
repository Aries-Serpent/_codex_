# Investigation Report — Alert #241 (Mako, requirements/lock.txt)

**Alert ID:** 241  
**Title:** Mako vulnerable to path traversal via backslash URI on Windows in TemplateLookup  
**Severity:** High  
**Package:** Mako  
**File:** requirements/lock.txt  
**Opened:** 2026-05-06T21:53:59Z  
**Relationship:** Direct  
**Alert URL:** https://github.com/Aries-Serpent/_codex_/security/dependabot/241

---

## Advisory

| Field | Value |
|-------|-------|
| GHSA | [GHSA-v92g-xgxw-vvmm](https://github.com/sqlalchemy/mako/security/advisories/GHSA-v92g-xgxw-vvmm) |
| CVE | CVE-2026-41205 |
| Fixed Version | ≥ 1.3.11 |
| Severity | High |

**Root Cause:** `TemplateLookup.get_template()` did not properly normalize Windows backslash (`\`) in URI paths, allowing path traversal to retrieve arbitrary files if untrusted user input was passed as a template name.

---

## Evidence Gathering

### Search Queries Executed

```bash
# Lexical — direct Mako usage
grep -rn "import mako\|from mako\|TemplateLookup" src/ scripts/ tools/
# Result: 0 direct Mako imports found

# Lock file presence
grep -n "^mako==" requirements/lock.txt
# Result: mako==1.3.10 at line 504

# Dependency chain
grep -A3 "^mako==" requirements/lock.txt
# via: alembic (transitive)
```

### Codebase Scan Results

| Query | Matches | Notes |
|-------|---------|-------|
| `import mako` in src/ | 0 | Not directly imported |
| `TemplateLookup` usage | 0 | Vulnerable class not used directly |
| `mako` in requirements/lock.txt | 1 | Line 504: `mako==1.3.10` |
| Consumer | 1 | `alembic` (transitive) |

### Exploitation Risk Assessment

- **Direct usage**: None. `TemplateLookup` is not instantiated anywhere in this codebase.
- **Transitive risk**: Minimal. Alembic uses Mako internally for migration templates; it does not expose user-controlled template lookup paths.
- **Windows-specific**: The backslash traversal is most severe on Windows; the CI runs on Linux. The path normalization fix in 1.3.11 is still beneficial for correctness.

---

## Root Cause Analysis

1. `requirements/lock.txt` pinned `mako==1.3.10`
2. `GHSA-v92g-xgxw-vvmm` affects all versions < 1.3.11
3. Fix was released in `1.3.11`; latest available is `1.3.12`
4. The lock file was not updated after the advisory

---

## Impact Assessment

- **Exploitability**: Low (no direct `TemplateLookup` usage)
- **Impact if exploited**: High (arbitrary file disclosure)
- **Attack surface**: Requires passing user-controlled template names to `TemplateLookup.get_template()`
- **Data at risk**: Arbitrary file read on the server

---

## Remediation: FIX

**Action taken:** Bumped `mako==1.3.10` → `mako==1.3.12` in `requirements/lock.txt`

```diff
- mako==1.3.10
+ mako==1.3.12
```

**Commit:** Applied in PR #4323 (`copilot/fix-timeline-structure`)

---

## Verification Steps

1. Confirm `requirements/lock.txt` shows `mako==1.3.12`
2. Dependabot alert #241 should auto-close on next Dependabot rescan
3. Run: `pip install mako==1.3.12 --dry-run` — no dependency conflicts

---

## Acceptance Criteria

- [x] `requirements/lock.txt` updated to `mako==1.3.12`
- [x] Version ≥ 1.3.11 (patched)
- [x] PR references advisory GHSA-v92g-xgxw-vvmm and CVE-2026-41205
- [ ] Dependabot alert #241 auto-closes on rescan
