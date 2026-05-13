# Cherry-Pick Instructions: PR #4431 → PR #4427

**Created:** 2026-05-13T01:00Z  
**Session:** S976  
**Source PR:** #4431 (`dependabot/pip/ujson-5.12.1`)  
**Target PR:** #4427 (`0D_base_`)  
**Status:** ✅ Ready to merge into PR #4427

---

## Summary

This document provides instructions for cherry-picking the ujson dependency bump from PR #4431 into PR #4427 (`0D_base_` branch).

**What's being cherry-picked:**
1. **Dependabot commit** (`701a924`): ujson 5.12.0 → 5.12.1
2. **S976 compliance commit** (`94371d6`): Pattern 25/30 fixes + sync_tracked_files

---

## Cherry-Pick Commands (Already Executed)

The cherry-pick has been completed locally on branch `cherrypick-ujson-to-4427`:

```bash
# 1. Create cherry-pick branch from 0D_base_
git fetch origin 0D_base_
git checkout -b cherrypick-ujson-to-4427 origin/0D_base_

# 2. Cherry-pick Dependabot ujson bump
git cherry-pick 701a9246d5c3da8a1b7f0e1be2b7f4ad8dc19849
# Result: commit 77678ea

# 3. Cherry-pick S976 Pattern 25/30 compliance fix
git cherry-pick 94371d6
# Conflicts resolved in:
#   - CHANGELOG.md (merged S976 entry at top)
#   - .codex/session_context_latest.md (took 0D_base_ version)
# Result: commit 92b6d5f

# 4. Verify sync_tracked_files
python3 scripts/ci/sync_tracked_files.py --check
# ✅ All tracked files are consistent
```

---

## Commits on Cherry-Pick Branch

```
92b6d5f (HEAD -> cherrypick-ujson-to-4427) fix(ci): S976 PR #4431 - Pattern 25/30 compliance + sync_tracked_files
77678ea deps(deps): bump ujson from 5.12.0 to 5.12.1
98f52a2 (origin/0D_base_) fix(ci): S975 — Pattern 25 compliance + CI stabilization confirmation
```

---

## Files Changed

### Commit 77678ea (ujson bump)
- `requirements/lock.txt`: ujson 5.12.0 → 5.12.1

### Commit 92b6d5f (S976 compliance)
- `.codex/aftermath/pda_iterations.jsonl`: Added PDA entry for 2026-05-13
- `CHANGELOG.md`: Added S976 section (cherry-pick from PR #4431)
- `docs/ROADMAP.md`: Updated baseline date to 2026-05-13
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`: Added S976 session summary

---

## Merge Strategy Options

### Option 1: Fast-Forward Merge (Recommended)

Since the cherry-pick branch is based on `0D_base_` HEAD, you can fast-forward merge:

```bash
# On 0D_base_ branch
git checkout 0D_base_
git merge --ff-only cherrypick-ujson-to-4427
git push origin 0D_base_
```

### Option 2: Manual Cherry-Pick

If you prefer to cherry-pick directly onto `0D_base_`:

```bash
git checkout 0D_base_
git cherry-pick 77678ea  # ujson bump
git cherry-pick 92b6d5f  # S976 compliance
git push origin 0D_base_
```

### Option 3: Squash and Rebase

If you want a single commit:

```bash
git checkout 0D_base_
git merge --squash cherrypick-ujson-to-4427
git commit -m "deps(deps): bump ujson 5.12.0→5.12.1 + S976 compliance (cherry-pick from PR #4431)"
git push origin 0D_base_
```

---

## Conflict Resolution Notes

### CHANGELOG.md Conflict

**Resolution:** Merged both versions by adding S976 entry at the top:

```markdown
## [Unreleased]

### Fixed (S976 — cherry-pick from PR #4431)
- Fixed Pattern 25 violation: Added CHANGELOG.md and AGENT_ACCOUNTABILITY_REPORT.md to commit (cherry-picked from PR #4431).
- Fixed Pattern 30 violation: Added PDA entry for 2026-05-13 to `.codex/aftermath/pda_iterations.jsonl`.
- Fixed `sync_tracked_files` stale `.secrets.baseline` CODEX_MANIFEST entry (hash mismatch resolved).
- Updated ROADMAP.md baseline date from 2026-04-28 to 2026-05-13.

### Changed (S976 — cherry-pick from PR #4431)
- Dependency: Bumped ujson from 5.12.0 to 5.12.1 (Dependabot automated update, cherry-picked from PR #4431).

### Fixed (S975 — CI stabilization + all review threads resolved)
[... existing 0D_base_ content ...]
```

### .codex/session_context_latest.md Conflict

**Resolution:** Took `0D_base_` version (--ours) since this file is session-specific and the 0D_base_ context is more relevant for PR #4427.

---

## Validation Results

All checks passing on `cherrypick-ujson-to-4427` branch:

```
✅ sync_tracked_files: All tracked files are consistent
✅ CODEX_MANIFEST integrity: sha256 consistent (f6082099d651…)
✅ .secrets.baseline: CODEX_MANIFEST entry correct
✅ CHANGELOG.md: ## [Unreleased] section present and non-empty
✅ AGENT_ACCOUNTABILITY_REPORT: most-recent session entry dated 2026-05-13
```

---

## Next Steps

1. **Review this document** to understand the cherry-pick changes
2. **Choose merge strategy** (Option 1 recommended)
3. **Merge into 0D_base_** using chosen strategy
4. **Verify CI passes** on PR #4427 after merge
5. **Close PR #4431** (or mark as superseded by PR #4427)

---

## Benefits of This Cherry-Pick

1. **Dependency Security**: ujson 5.12.1 includes bug fixes and performance improvements
2. **Pattern Compliance**: Brings Pattern 25/30 compliance to PR #4427
3. **Tracking Consistency**: Updates all tracking files (PDA, ROADMAP, CHANGELOG, AGENT_ACCOUNTABILITY_REPORT)
4. **Merge Readiness**: Improves PR #4427 merge-readiness score (sync_tracked_files dimension)

---

## Contact

**Session:** S976  
**Agent:** copilot-swe-agent[bot]  
**Date:** 2026-05-13T01:00Z  
**Branch:** `cherrypick-ujson-to-4427`  
**Commits:** `77678ea`, `92b6d5f`
