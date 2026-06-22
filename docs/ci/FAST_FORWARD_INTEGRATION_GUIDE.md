# Fast-Forward Safe Files + Auto-Approve Workflows Integration Guide

**Last Updated:** 2026-06-22

## Overview

This document explains how to use **fast-forward-safe-files.yml** and **auto-approve-workflows.yml** together to enable **immediate deployment of discussion-posting workflows** from PR → main, without waiting for full PR merge.

## The Problem It Solves

GitHub Actions workflows only take effect **from the default branch (main)**. When you define a new workflow (like `post-phase-4-5-to-discussion.yml`) in a PR:

- ❌ The `workflow_dispatch` button is **inactive** on the PR branch
- ❌ Schedule triggers are **inert** until the file lands on main
- ❌ The workflow can only run **after the PR is fully merged**

**Result**: Discussion posts are delayed until PR merge, slowing down communication.

## The Solution

**Combine two workflows:**

1. **fast-forward-safe-files.yml** — Promotes the workflow file to main immediately
2. **auto-approve-workflows.yml** — Auto-approves the fast-forward PR, completing the loop

### Architecture

```
┌─────────────────────────────────────────────────┐
│ Edit .github/workflows/post-*.yml in PR          │
│ (e.g., post-phase-4-5-to-discussion.yml)        │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│ Run: fast-forward-safe-files.yml                 │
│ Input: PR number, dry_run=false                 │
│ → Creates "fast-forward/pr-XXXX-{sha}" branch   │
│ → Opens Fast-Forward PR for review             │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│ auto-approve-workflows.yml fires (workflow_run) │
│ → Detects "wec:auto-approve" or "once" label   │
│ → Approves pending workflow runs                │
│ → Merges the Fast-Forward PR                    │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│ Workflow file now ACTIVE on main                │
│ → workflow_dispatch button works immediately    │
│ → Schedule triggers become active               │
└─────────────────────────────────────────────────┘
```

## Usage Workflow

### Step 1: Edit the Workflow in a PR

Create or modify a discussion-posting workflow in a new PR:

```bash
git checkout -b fix/add-discussion-posting
# Edit .github/workflows/post-phase-4-5-to-discussion.yml
git push origin fix/add-discussion-posting
# Open PR
```

## Step 2: Run Fast-Forward Manually

Once the PR is ready, manually trigger the fast-forward:

**Via GitHub Actions UI:**
1. Go to: https://github.com/Aries-Serpent/_codex_/actions/workflows/fast-forward-safe-files.yml
2. Click **"Run workflow"** button
3. Fill in:
   - **PR number**: `3856` (or your PR number)
   - **dry_run**: `false` (to apply for real)
   - **merge_mode**: `create-pr` (default — safe)
4. Click the green **"Run workflow"** button

**Via GitHub CLI:**

```bash
gh workflow run fast-forward-safe-files.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  -f pr_number=3856 \
  -f dry_run=false \
  -f merge_mode=create-pr
```

### Step 3: Monitor the Fast-Forward

1. A new PR will be created: `[FF] Promote safe files from PR #3856`
2. The PR branch is: `fast-forward/pr-3856-{sha8}`
3. Files promoted will be listed in the PR body

### Step 4: Auto-Approve (Optional but Recommended)

To auto-approve the fast-forward PR:

**One-time approval:**
```bash
gh workflow run auto-approve-workflows.yml \
  --repo Aries-Serpent/_codex_ \
  -f pr_number=<FF_PR_NUMBER> \
  -f enable_one_session=true
```

**Persistent approval** (auto-approve future sessions too):
```bash
gh workflow run auto-approve-workflows.yml \
  --repo Aries-Serpent/_codex_ \
  -f pr_number=<FF_PR_NUMBER> \
  -f enable_persistent=true
```

### Step 5: Verify Workflow is Active

Once merged to main:

1. Go to: https://github.com/Aries-Serpent/_codex_/actions/workflows/post-phase-4-5-to-discussion.yml
2. Verify the **"Run workflow"** button is now **active** (not grayed out)
3. You can now trigger it manually or let schedules run automatically

## Allowlist Configuration

The fast-forward allowlist is defined in: `.codex/fast_forward_allowlist.yaml`

**Currently allowed files:**
- `.github/workflows/*.yml` — All workflows (safe files only)
- `.github/workflows/*.yaml` — YAML workflows
- `.github/agents/*.md` — Agent prompt files
- `scripts/ci/*.py` — CI scripts
- `docs/ci/*.md` — CI documentation
- `CHANGELOG.md` — Changelog

**Explicitly denied** (never promoted):
- `*deploy*.yml` — Deployment workflows
- `*release*.yml` — Release workflows
- `*publish*.yml` — Publishing workflows
- `*prod*.yml` — Production workflows
- `.github/settings.yml` — Repository settings
- `secrets.env` / `.env` — Secret files

To add more patterns, edit `.codex/fast_forward_allowlist.yaml` and commit it to main.

## Safety Guarantees

✅ **Denied files are NEVER promoted** — Deployment/release/publish workflows are blocked

✅ **Default mode is safe** — Creates a PR (never pushes directly to main)

✅ **All operations are logged** — Every fast-forward is recorded in `.codex/fast_forward_log.ndjson`

✅ **Dry-run available** — Preview changes before applying: `--dry_run=true`

✅ **Manual review** — Maintainers review the Fast-Forward PR before merge (unless auto-approve is configured)

## Example: Real-World Scenario

### Scenario: Post Phase 4-5 Summary to Discussion

**Goal**: Make `post-phase-4-5-to-discussion.yml` active on main so the `workflow_dispatch` button works.

**Steps**:

```bash
# 1. Create feature branch
git checkout -b feature/phase-4-5-discussion-post

# 2. Edit the workflow
nano .github/workflows/post-phase-4-5-to-discussion.yml
# ... make changes ...

# 3. Commit and push
git add .github/workflows/post-phase-4-5-to-discussion.yml
git commit -m "Add Phase 4-5 discussion posting workflow"
git push origin feature/phase-4-5-discussion-post

# 4. Create PR (via GitHub)
# PR #3856 created

# 5. Run fast-forward (via Actions UI)
# PR #3856 is now being promoted...
# Fast-Forward PR #3860 is created: "fast-forward/pr-3856-a1b2c3d4"

# 6. (Optional) Set auto-approve label on PR #3860
gh pr edit 3860 --add-label "wec:auto-approve-once"

# 7. Monitor merges
# Within 5 minutes, PR #3860 is merged to main

# 8. Verify
# Go to Actions → post-phase-4-5-to-discussion.yml
# "Run workflow" button is now ACTIVE ✅
```

## Troubleshooting

### Fast-Forward PR won't merge

**Check:**
1. Does the workflow file match the allowlist? Run: `python scripts/ci/fast_forward_safe_files.py --repo Aries-Serpent/_codex_ --dry-run --pr 3856`
2. Is it on the denylist? Files with `deploy`, `release`, `publish`, `prod` in the name are denied.
3. Are there other changes? The fast-forward only promotes files in the allowlist. Non-safe files stay in the original PR.

### Workflow still inactive on main

**Check:**
1. Did the Fast-Forward PR merge? Verify the file is on main: `git log --oneline -S ".github/workflows/post-phase-4-5-to-discussion.yml" main | head -1`
2. Reload the Actions page (browser cache may be showing old state)
3. If it's a new workflow file (no prior version), GitHub may cache the workflow list for a few minutes

### auto-approve-workflows.yml didn't auto-approve

**Check:**
1. Is the label present? Run: `gh pr view 3860 --json labels -q '.labels[].name'`
2. If using `wec:auto-approve-once`, did you add it? Run: `gh pr edit 3860 --add-label "wec:auto-approve-once"`
3. Check the workflow run logs: https://github.com/Aries-Serpent/_codex_/actions/workflows/auto-approve-workflows.yml

## Advanced: Direct-Push Mode

By default, fast-forward creates a PR (safe). For immediate main push:

```bash
gh workflow run fast-forward-safe-files.yml \
  --repo Aries-Serpent/_codex_ \
  -f pr_number=3856 \
  -f merge_mode=direct-push \
  -f dry_run=false
```

⚠️ **Use with caution** — Commits directly to main, bypassing PR review.

## References

- **Fast-Forward Workflow**: `.github/workflows/fast-forward-safe-files.yml`
- **Auto-Approve Workflow**: `.github/workflows/auto-approve-workflows.yml`
- **Allowlist Config**: `.codex/fast_forward_allowlist.yaml`
- **Fast-Forward Script**: `scripts/ci/fast_forward_safe_files.py`
- **Example Discussion Post**: `.github/workflows/post-phase-4-5-to-discussion.yml`

## Questions?

See `.github/workflows/fast-forward-safe-files.yml` for comprehensive comments and examples.
