# DependaBot Sheriff - User Guide

## Overview

**DependaBot Sheriff** is a bash script that consolidates multiple Dependabot PRs into a single, manageable pull request. This tool is adapted from [kiba-d/dependabot-sheriff](https://github.com/kiba-d/dependabot-sheriff) for the Aries-Serpent/_codex_ repository.

## 🤔 When to Use This Tool

### ✅ Use DependaBot Sheriff When:

1. **Multiple low-risk patches** - You have 5+ Dependabot PRs with minor version bumps
2. **Time-constrained reviews** - You need to process many dependency updates quickly
3. **Well-tested dependencies** - All dependencies have comprehensive test coverage
4. **Non-breaking updates** - Mostly patch and minor version updates
5. **Batch testing desired** - You want to test all updates together before merging

### ❌ Do NOT Use When:

1. **Major version bumps** - Dependencies with breaking changes (e.g., v4 → v6)
2. **Critical dependencies** - Core dependencies like transformers, torch, or pytest
3. **Different dependency types** - Mixing GitHub Actions and Python packages
4. **Failed CI checks** - Some PRs have failing tests
5. **Known conflicts** - Dependencies that might conflict with each other

## ⚠️ Important Considerations

### Trade-offs

**Pros:**
- ✅ Faster review process for bulk updates
- ✅ Single CI run for all changes
- ✅ Reduces PR clutter in repository
- ✅ One-click revert if issues arise

**Cons:**
- ❌ Harder to identify which dependency caused issues
- ❌ Less granular git history
- ❌ Cannot selectively merge updates
- ❌ Increased blast radius if something breaks

### Risk Assessment

Based on the analysis in `.codex/CONSOLIDATED_DEPENDENCY_UPDATES_PR3198_3212.md`:

**Current Dependabot PRs (#3198-#3212):**
- **HIGH RISK:** 5 PRs (transformers, lm-eval, altair, GitHub Actions)
- **MEDIUM RISK:** 4 PRs (huggingface-hub, msgspec, pytest-rerunfailures)
- **LOW RISK:** 6 PRs (patches and minor updates)

**Recommendation:** Only consolidate the **6 LOW RISK** PRs. Handle high-risk updates individually.

## 📋 Prerequisites

### Required Tools

1. **Git** (version 2.20+)
   ```bash
   git --version
   ```

2. **GitHub CLI** (gh)
   ```bash
   gh --version
   ```

3. **Bash** (4.0+)
   ```bash
   bash --version
   ```

### Installation

#### macOS
```bash
brew install git gh
```

#### Ubuntu/Debian
```bash
sudo apt install git gh
```

#### GitHub CLI Authentication
```bash
gh auth login
```

## 🚀 Usage

### Basic Usage

```bash
# From the repository root
./scripts/dependabot_sheriff.sh
```

### Advanced Usage

#### Custom Base Branch
```bash
BASE_BRANCH=develop ./scripts/dependabot_sheriff.sh
```

#### Custom Assignee
```bash
DEPENDABOT_ASSIGNEE=your-username ./scripts/dependabot_sheriff.sh
```

#### Combined Options
```bash
BASE_BRANCH=develop DEPENDABOT_ASSIGNEE=your-username ./scripts/dependabot_sheriff.sh
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_BRANCH` | `main` | Base branch to merge into |
| `DEPENDABOT_ASSIGNEE` | `mbaetiong` | GitHub username for PR assignment |

### Customization

Edit `scripts/dependabot_sheriff.sh` to modify:
- Log file location (line 13-14)
- Branch naming convention (line 21)
- PR body template (line 184-224)
- Check status filtering (line 158-168)

## 📊 What the Script Does

### Workflow

1. **Prerequisites Check**
   - Verifies Git, GitHub CLI, and authentication
   - Ensures no uncommitted changes

2. **Branch Management**
   - Switches to base branch (`main`)
   - Pulls latest changes
   - Creates dated branch (e.g., `dependabot-consolidated-20260209`)

3. **PR Discovery**
   - Finds all open Dependabot PRs
   - Filters by author (`dependabot[bot]`)

4. **Status Validation**
   - Checks CI status for each PR
   - Skips PRs with failed checks
   - Skips PRs with no checks

5. **Consolidation**
   - Fetches each passing PR branch
   - Merges into consolidated branch
   - Handles merge conflicts gracefully

6. **PR Creation**
   - Pushes consolidated branch
   - Creates new PR with detailed summary
   - Assigns to designated reviewer
   - Adds `dependencies` and `dependabot` labels

### Output Files

#### Log File
Location: `.codex/logs/dependabot_sheriff_YYYYMMDD_HHMMSS.log`

Contains:
- Timestamped execution log
- PR processing details
- Merge status for each PR
- Error messages and warnings

#### Summary Document
Location: `.codex/logs/dependabot_sheriff_summary_YYYYMMDD.md`

Contains:
- Statistics (merged/skipped/failed counts)
- List of processed PRs
- Link to full log file

## 🔍 Example Scenarios

### Scenario 1: All PRs Pass (Ideal Case)

```
Input: 15 Dependabot PRs, all with passing checks

Output:
✅ Merged: 15 PRs
⚠️  Skipped: 0 PRs
❌ Failed: 0 PRs
📝 Created: 1 consolidated PR
```

### Scenario 2: Mixed Status

```
Input: 15 Dependabot PRs with mixed status

Output:
✅ Merged: 10 PRs (passing checks)
⚠️  Skipped: 3 PRs (failed checks)
❌ Failed: 2 PRs (merge conflicts)
📝 Created: 1 consolidated PR with 10 updates
```

### Scenario 3: No Passing PRs

```
Input: 5 Dependabot PRs, all failing checks

Output:
✅ Merged: 0 PRs
⚠️  Skipped: 5 PRs (failed checks)
❌ Failed: 0 PRs
📝 No PR created, branch deleted
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Uncommitted Changes Error

**Error:**
```
❌ ERROR: Uncommitted tracked changes detected!
```

**Solution:**
```bash
git status
git add .
git commit -m "Save work"
# OR
git stash
```

#### 2. GitHub CLI Not Authenticated

**Error:**
```
❌ ERROR: GitHub CLI is not authenticated
```

**Solution:**
```bash
gh auth login
```

#### 3. Merge Conflicts

**Error:**
```
❌ ERROR: Merge conflict in PR #1234
```

**Solution:**
- Script automatically aborts the merge and continues
- Review the consolidated PR for missing updates
- Handle conflicting PR manually

#### 4. No Dependabot PRs Found

**Warning:**
```
⚠️  WARNING: No Dependabot PRs found.
```

**Reason:**
- No open Dependabot PRs
- All Dependabot PRs have failing checks
- All Dependabot PRs are already merged

## 📈 Best Practices

### 1. Risk-Based Consolidation

**Strategy:**
```bash
# Option A: Consolidate only LOW RISK patches
# Close high-risk PRs temporarily, run script, then reopen them

# Option B: Use labels to filter
# Add "consolidate" label to safe PRs
# Modify script to filter by label
```

### 2. Pre-Consolidation Review

**Checklist:**
- [ ] Review each PR's CI status
- [ ] Check for breaking changes in changelogs
- [ ] Identify dependencies that might conflict
- [ ] Verify test coverage for affected code

### 3. Post-Consolidation Validation

**After running the script:**
1. Review the consolidated PR diff carefully
2. Run full test suite locally
3. Check for unexpected interactions
4. Monitor CI for flaky tests
5. Review dependency compatibility

### 4. Incremental Consolidation

**Recommended approach:**
```bash
# Week 1: Consolidate 3-5 lowest-risk PRs
./scripts/dependabot_sheriff.sh

# Week 2: If successful, consolidate next batch
./scripts/dependabot_sheriff.sh

# Gradually increase batch size
```

## 🔄 Comparison with Manual Approach

### Manual Individual Merging

**Time:** 5-10 min per PR × 15 PRs = 75-150 min
**Risk:** LOW (isolated failures)
**History:** CLEAR (one commit per dependency)
**Rollback:** EASY (revert specific commit)

### DependaBot Sheriff Consolidation

**Time:** 5 min script + 20 min review = 25 min
**Risk:** MEDIUM (combined failures)
**History:** GROUPED (one commit for all)
**Rollback:** MEDIUM (revert entire batch)

## 📝 Script Modifications

### Filtering by Risk Level

To only consolidate low-risk updates, add this function:

```bash
is_low_risk_pr() {
    local PR=$1
    local TITLE=$(gh pr view "$PR" --json title --jq '.title')
    
    # Define low-risk patterns
    if echo "$TITLE" | grep -qE "patch|importlib-metadata|nvidia-nccl|regex|pytest-timeout"; then
        return 0  # Low risk
    fi
    
    return 1  # Not low risk
}
```

Then modify the loop:

```bash
for PR in $PR_NUMBERS; do
    if ! is_low_risk_pr "$PR"; then
        log_warning "PR #$PR is not low-risk. Skipping."
        continue
    fi
    # ... rest of processing
done
```

### Custom PR Body Template

Edit lines 184-224 in `scripts/dependabot_sheriff.sh` to customize the PR description.

### Notification Integration

Add Slack/Discord notifications:

```bash
# At the end of main() function
if [ -n "$SLACK_WEBHOOK" ]; then
    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"DependaBot Sheriff: Consolidated $merged_count PRs into $PR_URL\"}"
fi
```

## 🔗 Related Documentation

- **Analysis Document:** `.codex/CONSOLIDATED_DEPENDENCY_UPDATES_PR3198_3212.md`
- **Original Tool:** https://github.com/kiba-d/dependabot-sheriff
- **GitHub CLI Docs:** https://cli.github.com/manual/
- **Dependabot Docs:** https://docs.github.com/en/code-security/dependabot

## ⚖️ License

Adapted from [kiba-d/dependabot-sheriff](https://github.com/kiba-d/dependabot-sheriff) (MIT License)

## 🤝 Contributing

To improve the script:
1. Fork the repository
2. Make changes to `scripts/dependabot_sheriff.sh`
3. Test thoroughly
4. Submit PR with detailed description

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Review the troubleshooting section
- Check GitHub Actions logs
- Consult with @mbaetiong

---

**Last Updated:** 2026-02-09
**Version:** 1.0.0
**Maintainer:** @mbaetiong
