# Investigation Report — Alert #239 (GitPython, requirements/lock.txt)

**Alert ID:** 239  
**Title:** GitPython reference APIs has a path traversal vulnerability that allows arbitrary file write and delete outside the repository  
**Severity:** High  
**Package:** gitpython  
**File:** requirements/lock.txt  
**Opened:** 2026-05-06T20:02:42Z  
**Relationship:** Direct  
**Alert URL:** https://github.com/Aries-Serpent/_codex_/security/dependabot/239

---

## Advisory

| Field | Value |
|-------|-------|
| GHSA | [GHSA-7545-fcxq-7j24](https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-7545-fcxq-7j24) |
| CVE | N/A |
| Fixed Version | ≥ 3.1.48 |
| Severity | High |

**Root Cause:** Reference-related methods (`Reference.create`, `SymbolicReference.set_reference`, `Reference.rename`, `Reference.delete`) generated paths from potentially attacker-controlled reference names without enforcing they stay within the repository boundary. This enabled directory traversal to write/rename/delete files outside `.git/`.

---

## Evidence Gathering

### Search Queries Executed

```bash
# Lexical — direct import usage
grep -rn "from git import\|import git\b\|import gitpython" src/ scripts/ tools/
# Result: 0 direct imports of gitpython's high-level reference APIs in source code
# (gitpython is used transitively via mlflow-skinny, scmrepo, wandb)

# Lock file presence
grep -n "^gitpython" requirements/lock.txt
# Result: gitpython==3.1.45 at line 311

# Dependency chain
grep -A5 "^gitpython==" requirements/lock.txt
# via: mlflow-skinny, scmrepo, wandb (all transitive consumers)
```

### Codebase Scan Results

| Query | Matches | Notes |
|-------|---------|-------|
| `from git import` in src/ | 0 | Not directly imported |
| `import git` in scripts/ | 0 | |
| `gitpython` in requirements/lock.txt | 1 | Line 311: `gitpython==3.1.45` |
| Consumers in lock.txt | 3 | mlflow-skinny, scmrepo, wandb |

### Exploitation Risk Assessment

- **Direct usage of vulnerable APIs**: None found. The reference APIs that contain the vulnerability are not called directly by this codebase.
- **Transitive risk**: Low. The vulnerability requires attacker-controlled reference names passed to `Reference.create/rename/delete`. The transitive consumers (mlflow, wandb) do not expose such an attack surface.
- **Environment context**: Linux CI/CD environment — the path traversal is most severe on Windows. Risk exists on any OS for write operations.

---

## Root Cause Analysis

1. `requirements/lock.txt` pinned `gitpython==3.1.45`
2. `GHSA-7545-fcxq-7j24` affects all versions ≤ 3.1.47
3. Fix was released in `3.1.48` (2025); latest available is `3.1.50`
4. The lock file was not updated after the advisory was published

---

## Impact Assessment

- **Exploitability**: Low (no direct reference API usage)
- **Impact if exploited**: High (arbitrary file write/delete outside repository)
- **Attack surface**: Requires attacker-controlled git reference name input
- **Data at risk**: File system integrity outside `.git/`

---

## Remediation: FIX

**Action taken:** Bumped `gitpython==3.1.45` → `gitpython==3.1.50` in `requirements/lock.txt`

```diff
- gitpython==3.1.45
+ gitpython==3.1.50
```

**Commit:** Applied in PR #4323 (`copilot/fix-timeline-structure`)

---

## Verification Steps

1. Confirm `requirements/lock.txt` shows `gitpython==3.1.50`
2. Dependabot alert #239 should auto-close on next Dependabot rescan
3. Run: `pip install gitpython==3.1.50 --dry-run` — no dependency conflicts

---

## Acceptance Criteria

- [x] `requirements/lock.txt` updated to `gitpython==3.1.50`
- [x] Version ≥ 3.1.48 (patched)
- [x] PR references advisory URL and GHSA
- [ ] Dependabot alert #239 auto-closes on rescan

---

## Rollback

If `gitpython==3.1.50` causes issues: revert to `3.1.48` (minimum patched version).
