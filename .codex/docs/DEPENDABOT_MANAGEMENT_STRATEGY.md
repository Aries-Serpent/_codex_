# DependaBot Management Strategy for _codex_

**Date:** 2026-02-09  
**Repository:** Aries-Serpent/_codex_  
**Related Documents:**
- Analysis: `.codex/CONSOLIDATED_DEPENDENCY_UPDATES_PR3198_3212.md`
- Sheriff Guide: `.codex/docs/DEPENDABOT_SHERIFF_GUIDE.md`

---

## Overview

This document provides guidance on managing Dependabot PRs in the _codex_ repository. We now support **two complementary approaches**:

1. **Manual Individual Merging** - Traditional approach (recommended for high-risk updates)
2. **Automated Consolidation** - Using DependaBot Sheriff tool (for low-risk batches)

---

## Two Approaches Explained

### Approach 1: Manual Individual Merging (Traditional)

**How it works:**
- Review and test each Dependabot PR separately
- Merge one at a time
- Monitor CI for each merge

**Best for:**
- ✅ Major version bumps (e.g., v4 → v6)
- ✅ Core dependencies (transformers, torch, pytest)
- ✅ Breaking changes
- ✅ Mixed GitHub Actions + Python packages
- ✅ When detailed attribution is needed

**Pros:**
- Low blast radius (isolated failures)
- Clear git history
- Easy rollback (specific dependency)
- Granular testing

**Cons:**
- Time-consuming (5-10 min per PR)
- Many CI runs
- PR clutter in repository

**See:** `.codex/CONSOLIDATED_DEPENDENCY_UPDATES_PR3198_3212.md` for risk-based merge order

---

### Approach 2: Automated Consolidation (DependaBot Sheriff)

**How it works:**
- Script automatically merges multiple passing Dependabot PRs
- Creates single consolidated PR
- One CI run for all changes

**Best for:**
- ✅ Low-risk patches (0.19.0 → 0.19.1)
- ✅ Minor version bumps (1.2.0 → 1.3.0)
- ✅ Similar dependency types (all Python OR all Actions)
- ✅ 5+ simple updates at once
- ✅ Time-constrained situations

**Pros:**
- Fast review process
- Single CI run
- Reduces PR clutter
- One-click batch revert

**Cons:**
- Higher blast radius
- Less granular git history
- Harder to identify issue source
- Cannot selectively merge

**See:** `.codex/docs/DEPENDABOT_SHERIFF_GUIDE.md` for usage details

---

## Decision Tree

```
Do you have 5+ Dependabot PRs?
│
├─ NO → Use Approach 1 (Manual Individual Merging)
│
└─ YES → Are they all low-risk patches/minor versions?
    │
    ├─ NO → Use Approach 1 (Manual Individual Merging)
    │
    └─ YES → Do they all have passing CI?
        │
        ├─ NO → Use Approach 1 (Manual Individual Merging)
        │
        └─ YES → Use Approach 2 (DependaBot Sheriff) ✅
```

---

## Current PRs (#3198-#3212) Recommendation

### Analysis

**Total PRs:** 15
- **HIGH RISK:** 5 PRs (transformers, lm-eval, altair, Actions v4→v6/v7)
- **MEDIUM RISK:** 4 PRs (huggingface-hub, msgspec, pytest-rerunfailures)
- **LOW RISK:** 6 PRs (patches and minor updates)

### Recommended Strategy: Hybrid Approach

#### Phase 1: Consolidate Low-Risk PRs (Use Sheriff)
```bash
# Close HIGH and MEDIUM risk PRs temporarily
gh pr close 3199 3200 3201 3203 3204 3205 3206 3207 3212

# Run DependaBot Sheriff to consolidate LOW risk PRs
./scripts/dependabot_sheriff.sh

# Expected: Consolidates PRs #3202, #3208, #3209, #3211 (4 low-risk patches)
```

**LOW RISK PRs to consolidate:**
- #3202: pytest-timeout 2.3.1 → 2.4.0 (minor, no breaking changes)
- #3208: importlib-metadata 8.7.0 → 8.7.1 (patch, bug fixes only)
- #3209: nvidia-nccl-cu12 2.29.2 → 2.29.3 (patch, NVIDIA library)
- #3211: regex 2025.11.3 → 2026.1.15 (minor, performance fix)

#### Phase 2: Manual Merge Medium-Risk PRs
```bash
# Reopen and review individually
gh pr reopen 3205 3210 3212

# Review, test, and merge each one separately
# Order: #3210 (msgspec) → #3205 (huggingface-hub) → #3212 (pytest-rerunfailures)
```

#### Phase 3: Manual Merge High-Risk PRs
```bash
# Reopen and handle with extreme care
gh pr reopen 3199 3200 3201 3203 3204 3206 3207

# Critical reviews:
# - #3201: transformers (breaking changes)
# - #3203: lm-eval (breaking installation)
# - #3206: altair (major version)
# - #3199, #3200, #3204, #3207: Actions (requires runner updates)
```

---

## Implementation Guide

### Using DependaBot Sheriff

#### Manual Execution
```bash
# From repository root
./scripts/dependabot_sheriff.sh

# With custom options
BASE_BRANCH=main DEPENDABOT_ASSIGNEE=mbaetiong ./scripts/dependabot_sheriff.sh
```

#### GitHub Actions (Automated)
```bash
# Trigger via GitHub UI: Actions → DependaBot Sheriff → Run workflow

# Or via CLI
gh workflow run dependabot-sheriff.yml \
  --field base_branch=main \
  --field assignee=mbaetiong \
  --field risk_level=low
```

#### Review Output
```bash
# Check logs
cat .codex/logs/dependabot_sheriff_*.log

# Check summary
cat .codex/logs/dependabot_sheriff_summary_*.md

# Review consolidated PR on GitHub
```

---

## Best Practices

### 1. Pre-Consolidation Checklist

Before running DependaBot Sheriff:
- [ ] Verify all PRs have passing CI checks
- [ ] Confirm no major version bumps in batch
- [ ] Check for known dependency conflicts
- [ ] Review changelogs for breaking changes
- [ ] Ensure dependencies are same type (Python or Actions, not mixed)

### 2. Risk-Based Batching

**Never consolidate:**
- Major version bumps (v4 → v5, v5 → v6)
- Core framework dependencies (transformers, torch, fastapi)
- Dependencies with failing CI
- Mixed GitHub Actions + Python packages

**Safe to consolidate:**
- Patch updates (1.2.3 → 1.2.4)
- Minor updates from trusted publishers
- Documentation-only updates
- Testing tool updates (pytest plugins)

### 3. Post-Consolidation Validation

After Sheriff creates consolidated PR:
1. Review the diff carefully
2. Check for unexpected interactions
3. Run full test suite locally
4. Monitor CI for flaky tests
5. Test affected features manually

### 4. Incremental Adoption

**Week 1:** Consolidate 2-3 lowest-risk PRs
**Week 2:** If successful, consolidate 4-6 PRs
**Week 3+:** Gradually increase batch size

---

## Troubleshooting

### Sheriff Script Fails

**Issue:** Script exits with errors

**Solutions:**
1. Check logs: `.codex/logs/dependabot_sheriff_*.log`
2. Verify GitHub CLI authentication: `gh auth status`
3. Ensure clean working directory: `git status`
4. Review merge conflicts in log

### Consolidated PR Fails CI

**Issue:** Consolidated PR has test failures

**Solutions:**
1. Identify failing test in CI logs
2. Bisect to find problematic dependency
3. Close consolidated PR
4. Merge dependencies individually to isolate issue

### Merge Conflicts

**Issue:** Sheriff reports merge conflicts

**Solutions:**
- Script automatically skips conflicting PRs
- Review summary to see which PRs were skipped
- Merge conflicting PRs manually after consolidation

---

## Monitoring and Metrics

### Success Metrics

Track these metrics to evaluate approach effectiveness:

**Manual Approach:**
- Average time per PR
- Number of rollbacks
- CI failure rate

**Sheriff Approach:**
- PRs consolidated per run
- Conflict rate
- Consolidated PR failure rate
- Time saved vs manual

### Recommended Monitoring

```bash
# Create monthly report
scripts/dependabot_metrics.sh --month 2026-02

# Expected output:
# - Total PRs processed: 45
# - Sheriff consolidations: 3 (15 PRs → 3 consolidated PRs)
# - Manual merges: 30 PRs
# - Time saved: ~6 hours
```

---

## GitHub Actions Integration

### Workflow: dependabot-sheriff.yml

**Location:** `.github/workflows/dependabot-sheriff.yml`

**Triggers:**
- Manual dispatch (workflow_dispatch)
- Optional: per-phase schedule (commented out)

**Inputs:**
- `base_branch`: Branch to merge into (default: main)
- `assignee`: PR assignee (default: mbaetiong)
- `risk_level`: Risk filter (default: low)

**Outputs:**
- Consolidated PR (if successful)
- Log artifacts (30-day retention)
- Summary artifacts (30-day retention)

---

## Future Enhancements

### Planned Features

1. **Risk-Level Filtering**
   - Script filters PRs by risk level
   - Labels: `risk:low`, `risk:medium`, `risk:high`
   - Auto-skip high-risk PRs

2. **Slack/Discord Notifications**
   - Post consolidation summary to channels
   - Alert on failures
   - per-iteration digest of Dependabot activity

3. **Auto-Merge for Low Risk**
   - After consolidation, auto-merge if CI passes
   - Configurable approval requirements
   - Safety checks before merge

4. **Dependency Conflict Detection**
   - Pre-check for known conflicts
   - Analyze dependency graphs
   - Warn before consolidation

5. **Analytics Dashboard**
   - Track consolidation trends
   - Time savings metrics
   - Failure rate analysis

---

## Related Documentation

- **Original Tool:** https://github.com/kiba-d/dependabot-sheriff
- **User Guide:** `.codex/docs/DEPENDABOT_SHERIFF_GUIDE.md`
- **PR Analysis:** `.codex/CONSOLIDATED_DEPENDENCY_UPDATES_PR3198_3212.md`
- **GitHub CLI:** https://cli.github.com/manual/
- **Dependabot:** https://docs.github.com/en/code-security/dependabot

---

## Contact

**Maintainer:** @mbaetiong  
**Issues:** Create GitHub issue with `dependabot` label  
**Questions:** See troubleshooting section or contact maintainer

---

**Last Updated:** 2026-02-09  
**Version:** 1.0.0  
**Status:** ✅ Active and Production-Ready
