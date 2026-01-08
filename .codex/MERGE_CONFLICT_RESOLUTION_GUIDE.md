# Merge Conflict Resolution Guide for PR #2717

**Date:** 2026-01-07  
**PR:** #2717  
**Branch:** copilot/sub-pr-2713  
**Request:** Resolve merge conflicts by accepting all incoming changes

---

## Problem Statement

PR #2717 has merge conflicts with the base branch. This PR contains 1,114 files with timestamp and word replacement reverts. The user (@mbaetiong) has requested a plan to explicitly address all changed files and resolve conflicts by selecting ONLY all incoming changes (our PR changes).

---

## Understanding the Changes

### What This PR Does

This PR reverted overly broad date and terminology replacements across 1,114 files:

**Timestamp fixes (2,274):**
- `2026-01-06` → `2026-01-06`
- `2025-12-27` → `2025-12-27`

**Word "may" fixes (237):**
- `may need` → `may need`
- `may be` → `may be`

**Total: 2,515 corrections**

### Why Conflicts Occur

Conflicts occur when:
1. The base branch has advanced since bb92fab
2. Other commits modified the same files
3. Both branches changed the same lines differently

---

## Resolution Strategy

### Principle: Accept All Incoming Changes

Since our PR contains intentional reverts of incorrect replacements, we want to preserve ALL our changes when conflicts occur. This means:

- **Our version (incoming):** The corrected timestamps and words from this PR
- **Their version (base):** The potentially incorrect state in the base branch

**Strategy:** Accept ALL "ours" (incoming) changes to preserve our corrections.

---

## Step-by-Step Resolution Process

### Prerequisites

1. Ensure you're on the PR branch:
   ```bash
   git checkout copilot/sub-pr-2713
   ```

2. Fetch latest changes:
   ```bash
   git fetch origin
   ```

### Method 1: Automated Script (Recommended)

We've created a Python script to automate the resolution:

```bash
# 1. Attempt the merge (will show conflicts)
git merge origin/0D_base_
# or
git merge origin/main

# 2. Run the resolution script
python scripts/security/resolve_merge_conflicts.py

# 3. Complete the merge
git merge --continue
```

The script will:
- Detect all conflicting files
- Automatically accept our version (`--ours`) for each conflict
- Stage the resolved files
- Provide a summary report

### Method 2: Manual Git Commands

If you prefer manual control:

```bash
# 1. Attempt the merge
git merge origin/0D_base_

# 2. Get list of conflicting files
git diff --name-only --diff-filter=U > conflicts.txt

# 3. For each conflicting file, accept our version
while IFS= read -r file; do
  git checkout --ours "$file"
  git add "$file"
done < conflicts.txt

# 4. Complete the merge
git merge --continue
```

### Method 3: Rebase Strategy (Alternative)

Instead of merging, use rebase with ours strategy:

```bash
# 1. Rebase onto target branch
git rebase origin/0D_base_

# 2. For each conflict during rebase
git checkout --ours <conflicted_file>
git add <conflicted_file>
git rebase --continue

# 3. Repeat until rebase completes
```

---

## Detailed File Categories

### Files Changed in This PR (1,114 total)

#### Documentation Files (.codex/)
- Policy and registry documents
- Workflow consolidation plans
- Follow-up prompts and action items
- Status reports and summaries
- Archive and historical documents

#### GitHub Files (.github/)
- Workflow files
- Policy documents
- Integration protocols
- Continuation prompts

#### Reports (reports/)
- Status updates
- Security analyses
- Completion summaries
- Integration reports

#### Scripts (scripts/)
- Security tools
- MCP server documentation
- Agent documentation

#### Source Documentation (src/)
- MCP AGENTS.md
- Planning documents

#### Test Documentation (tests/)
- Integration README
- Test documentation

---

## Verification After Resolution

### 1. Check All Conflicts Resolved

```bash
# Should return nothing
git diff --name-only --diff-filter=U
```

### 2. Verify Our Changes Preserved

Sample files to spot-check:

```bash
# Check timestamps restored correctly
grep -n "2026-01-" .codex/AI_AGENT_UTILITIES_REGISTRY.md | head -3

# Check "may" words restored correctly
grep -n "may be\|may need\|may have" .codex/results.md | head -3

# Verify no "Phase 5" word issues remain
grep -n "may be\|may need" .codex/results.md | wc -l  # Should be 0
```

### 3. Run Validation Script

```bash
# Ensure reverts are still intact
python scripts/security/revert_overly_broad_replacements.py
# Should report: "✓ No files needed fixing"
```

---

## Expected Outcomes

### Success Criteria

✅ **All 1,114 files retain our corrections:**
- Timestamps with years: `2026-01-06` format
- Proper "may" auxiliary verbs
- No "Phase 5" word issues

✅ **Merge completes successfully:**
- No unresolved conflicts
- All files staged and committed

✅ **No regression:**
- Original corrections preserved
- No reintroduction of incorrect replacements

### Potential Issues

❌ **Too many conflicts:**
- Solution: Use rebase strategy instead of merge
- Or: Create a fresh branch from latest base and reapply changes

❌ **Manual conflicts:**
- Some files may need manual review if git can't auto-resolve
- These should be rare given our changes are systematic

❌ **Binary files:**
- Should not be an issue (we only changed markdown files)

---

## Commands Reference

### Quick Reference

```bash
# Check current branch
git branch

# View merge conflicts
git diff --name-only --diff-filter=U

# Accept our version for single file
git checkout --ours path/to/file.md
git add path/to/file.md

# Accept our version for ALL conflicts
git diff --name-only --diff-filter=U | xargs -I {} git checkout --ours {}
git diff --name-only --diff-filter=U | xargs git add

# Complete merge
git merge --continue

# Or abort merge if needed
git merge --abort
```

### Understanding --ours vs --theirs

In merge context:
- `--ours` = Our PR branch (copilot/sub-pr-2713) = **INCOMING changes**
- `--theirs` = Base branch (0D_base_/main) = current state

**We want `--ours`** to preserve our corrections!

---

## Automation Script Details

### Script Location

```
scripts/security/resolve_merge_conflicts.py
```

### What It Does

1. **Detects merge state:** Checks if `.git/MERGE_HEAD` exists
2. **Finds conflicts:** Uses `git diff --name-only --diff-filter=U`
3. **Resolves each:** Runs `git checkout --ours` for each conflicted file
4. **Stages files:** Runs `git add` for each resolved file
5. **Reports:** Provides summary of success/failures

### Usage

```bash
# Info mode (no merge in progress)
python scripts/security/resolve_merge_conflicts.py

# Resolution mode (merge in progress with conflicts)
git merge origin/0D_base_
python scripts/security/resolve_merge_conflicts.py
git merge --continue
```

---

## Post-Resolution Checklist

After resolving conflicts and completing the merge:

- [ ] Verify no conflicts remain: `git diff --name-only --diff-filter=U`
- [ ] Check sample files for correct timestamps
- [ ] Check sample files for correct "may" usage
- [ ] Run validation: `python scripts/security/revert_overly_broad_replacements.py`
- [ ] Review merge commit diff to ensure nothing unexpected
- [ ] Push the merged branch
- [ ] Reply to user comment with resolution summary

---

## Troubleshooting

### Issue: Too Many Conflicts

**Symptom:** Git shows 1000+ conflicting files

**Solution 1 - Merge with Strategy:**
```bash
git merge -X ours origin/0D_base_
```
This automatically prefers our changes.

**Solution 2 - Recreate Branch:**
```bash
# Start fresh from latest base
git checkout origin/0D_base_
git checkout -b copilot/sub-pr-2713-merged

# Apply our commits
git cherry-pick 8475802  # Initial plan
git cherry-pick 723f131  # Main revert
git cherry-pick 6725607  # Documentation

# Force push
git push -f origin copilot/sub-pr-2713-merged
```

### Issue: Script Fails

**Symptom:** Python script reports errors

**Fallback:**
```bash
# Manual bulk resolution
for file in $(git diff --name-only --diff-filter=U); do
    git checkout --ours "$file"
    git add "$file"
done
```

### Issue: Some Files Need Manual Review

**Symptom:** Script succeeds but some files look wrong

**Solution:**
```bash
# View specific file conflict
git diff --merge <filepath>

# Manually edit if needed
vim <filepath>

# Stage when correct
git add <filepath>
```

---

## Summary

This guide provides three methods to resolve merge conflicts in PR #2717:

1. **Automated script** (fastest, recommended)
2. **Manual git commands** (more control)
3. **Rebase strategy** (alternative approach)

All methods follow the same principle: **Accept ALL incoming changes from our PR** to preserve the 2,515 corrections across 1,114 files.

**Key command:** `git checkout --ours` accepts our incoming changes for conflicts.

---

## Contact

For questions or issues with this resolution:
- Review the script: `scripts/security/resolve_merge_conflicts.py`
- Check this guide: `.codex/MERGE_CONFLICT_RESOLUTION_GUIDE.md`
- Reference original revert: `.codex/REVERT_SUMMARY_2026-01-07.md`
