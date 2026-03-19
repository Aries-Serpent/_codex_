# Workflow Approval Guide — Reducing the Auto-Commit Cascade

**Status:** ✅ Implemented (S155 — 2026-03-18)  
**Problem:** Clicking "Approve and run" in GitHub Actions triggers ALL pending workflows
simultaneously, including auto-commit ones. Multiple concurrent commits → rebase conflicts
on the next `report_progress` push.

---

## Root Cause: The Approval Cascade

When the `agent-auth-delegation` environment gate fires (PR opened → checkbox detected →
"Awaiting owner approval"), GitHub queues ALL other `pull_request`-triggered workflows at
the same time. When the owner clicks "Approve" in the GitHub Actions UI:

```
Owner clicks Approve
  ↓
agent-auth-delegation activates
  ├── commits: accountability report + CHANGELOG auto-update
  ├── commits: provenance session token [skip ci]
  └── commits: session context digest [skip ci]

simultaneously:
codex-manifest-refresh fires (was triggered by PR push)
  └── commits: CODEX_MANIFEST.json [skip ci]

Result: 3-4 concurrent commits on the branch
Next report_progress rebase: CONFLICT ← the sync+new-work anti-pattern
```

**S155 fix:** Removed `synchronize` from `codex-manifest-refresh.yml`,
`agent-auth-delegation.yml`, and `copilot-evolution-suite.yml`.

---

## Essential vs. Non-Essential Workflows

### ✅ Essential (must run, run automatically)

These are **checks only** — they never commit to the branch:

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| PR Checks (Isolated Cache) | `pr-checks.yml` | synchronize | Tests, lint, ruff |
| Pre-Merge Validation | `pre-merge-validation.yml` | synchronize | Auto-fix check, quick tests |
| 🚨 Deferral Language Gate | `deferral-language-gate.yml` | synchronize | Block deferral language |
| 🔀 Branch Rebase Gate | `branch-rebase-gate.yml` | synchronize | Rebase freshness check |
| mypy Baseline | `mypy-baseline.yml` | synchronize | Type regression guard |
| Agent Registry Validation | `agent-registry-validation.yml` | synchronize | Agent schema validation |

### ⚠️ Commit-on-open (fire once on PR creation — safe)

These workflows **commit to the branch** but only on `opened`/`reopened` (not every push):

| Workflow | File | Trigger | Commits | Note |
|----------|------|---------|---------|------|
| CODEX Manifest Auto-Refresh | `codex-manifest-refresh.yml` | opened, 6h schedule | CODEX_MANIFEST.json | S155: removed `synchronize` |
| Generate PR Follow-Up Prompt | `pr-followup-generator.yml` | opened | PR follow-up .md | Safe — one-time |
| Agent Token Delegation | `agent-auth-delegation.yml` | opened, edited, ready_for_review | accountability + auth | S155: removed `synchronize` |
| Art_Copilot Evolution & Review | `copilot-evolution-suite.yml` | opened, 4h schedule | evolution patches | S155: removed `synchronize` |

### 🔴 Approval-gated (require human approval before running)

These workflows pause at an **environment protection gate** and only proceed after
`@mbaetiong` clicks "Approve and run" in the Actions UI:

| Workflow | File | Environment | What it does |
|----------|------|-------------|-------------|
| Agent Token Delegation | `agent-auth-delegation.yml` | `agent-auth-delegation` | Sets COPILOT_AGENT_AUTH_ENABLED=true, posts @copilot continue |
| PyPI Publish | `pypi-publish.yml` | `pypi` | Publishes package to PyPI |
| GitHub Pages (MkDocs) | `pages-mkdocs.yml` | `github-pages` | Deploys site to GitHub Pages |

---

## What Happens When You Click "Approve and Run"

**Before S155 (old behaviour):**
```
Click Approve
→ agent-auth-delegation environment unblocks
→ ALSO triggers manifest-refresh + evolution-suite (were pending from same push)
→ 3-4 concurrent commits on branch
→ Next push: rebase conflict
```

**After S155 (new behaviour):**
```
Click Approve
→ agent-auth-delegation environment unblocks
→ Only agent-auth-delegation runs (manifest-refresh no longer queued for this push)
→ 2 commits max (auth token + session context)
→ Next push: clean rebase
```

---

## Recommended Approval Workflow

### When you see "Waiting for approval" in GitHub Actions UI:

1. **Check which workflow needs approval:**
   - If it's `Agent Token Delegation` → only approve if you intend to activate
     `COPILOT_AGENT_AUTH_ENABLED=true` for the current Copilot session
   - If it's `PyPI Publish` → verify the release is intended
   - If it's `GitHub Pages` → verify the docs are ready

2. **Before approving, check for pending commit workflows:**
   ```bash
   gh run list --repo Aries-Serpent/_codex_ --status queued --limit 10
   ```
   If `codex-manifest-refresh` or `copilot-evolution-suite` are queued, wait for them
   to complete before approving (prevents concurrent commits).

3. **After approving:**
   - Wait ~60 seconds for the post-approval commits to land
   - Run `git fetch origin` in your local clone (or Codespace) before the next push
   - The `prevent_sync_commit_conflict.py` pre-push hook will warn if staged files
     overlap with any remote auto-commits

---

## Auto-Commit Inventory (full list)

These workflows **write commits** to the repository branch:

| Workflow | When it commits | Skip pattern |
|----------|----------------|--------------|
| `agent-auth-delegation.yml` | On approval: auth token + session context | `[skip ci]` |
| `codex-manifest-refresh.yml` | PR opened + every 6h | `[skip ci]` |
| `pr-followup-generator.yml` | PR opened | `[skip ci]` |
| `iterative-self-healing-ci.yml` | After detecting fixable CI failure | `[skip ci-if-no-change]` |
| `auto-fix-common-issues.yml` | Manual trigger | none |
| `copilot-evolution-suite.yml` | PR opened + every 4h | `[automated]` |
| `audit-qa-suite.yml` | Schedule | various |
| `cognitive-action-decision.yml` | Schedule + workflow_run | various |

### How to prevent concurrent commit conflicts

```bash
# Before any report_progress push, check for recent auto-commits:
git fetch origin
git log --oneline origin/copilot/update-ci-failure-triage-report -5

# The prevent_sync_commit_conflict.py hook (added S155) also catches this at pre-push time
```

---

## Reducing Pending Workflows on a PR

If the "Approve" button shows many workflows, use these skip-ci techniques:

1. **Push with `[skip ci]`** in the commit message — skips ALL CI:
   ```bash
   git commit -m "chore: minor fix [skip ci]"
   ```

2. **Push with `[skip-non-essential]`** — future enhancement (tracked in cognitive brain)

3. **Use `paths` filters** — already implemented in `auto-fix-pr-check.yml`:
   ```yaml
   paths:
     - 'src/**/*.py'
     - 'tests/**/*.py'
   ```
   Only fires when Python or workflow files change.

4. **Draft PR** — some workflows skip `draft: true` PRs:
   ```bash
   gh pr ready --undo   # convert back to draft
   ```

---

## Future Enhancement: Explicit Workflow Approval List

**Tracked as:** Cognitive Brain Phase 6 objective  
**Goal:** Replace the "approve all pending" button with a selective approval mechanism
where only the specific workflow needing approval is run, not all queued ones.

**Implementation approach:**
- Use `pull_request_target` with explicit branch allowlist to isolate approval scope
- Add `if: github.event.action == 'ready_for_review'` guard to all commit-generating PR workflows
  so they only fire when the PR is explicitly marked ready (not on every push)
- Consider `workflow_dispatch` with explicit PR number for all agent-auth related workflows

---

*Created: S155 — 2026-03-18 | PR #3628*  
*See also: `.codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md`*
