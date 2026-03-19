# Workflow Cherry-Pick to `main` — Plan

> **Status:** Ready to execute
> **Generated:** 2026-03-19 (S162 — PR #3633)
> **Reason:** `workflow_run` events only fire from the repository default branch (`main`).
>   `copilot-agent-session-done.yml` uses this trigger and will never fire
>   until the file exists in `main`.

---

## Root Cause: Why Some Workflows Require `main`

GitHub Actions workflow triggers have different branch resolution rules:

| Trigger | Workflow resolved from |
|---------|----------------------|
| `push` | The pushed ref |
| `pull_request` | The HEAD branch of the PR |
| `pull_request_review` | The HEAD branch of the PR |
| `issue_comment` | **Default branch (`main`)** |
| `workflow_run` | **Default branch (`main`)** |
| `schedule` | **Default branch (`main`)** |

`copilot-agent-session-done.yml` uses `workflow_run`, so it **must** exist in
`main` to fire.  `copilot-review-responder.yml` was updated to use
`issue_comment` (in addition to `pull_request_review`) — the `issue_comment`
trigger also resolves from `main`, meaning the fix commit must land in `main`
for the autonomous loop to work reliably across ALL PRs (not just PRs whose
head branch contains the workflow file).

---

## Files That Must Be in `main` for the Autonomous Loop to Work

| File | Trigger type | Needs `main`? |
|------|-------------|--------------|
| `.github/workflows/copilot-review-responder.yml` | `issue_comment` + `pull_request_review` | ✅ Yes (for `issue_comment`) |
| `.github/workflows/copilot-agent-session-done.yml` | `workflow_run` | ✅ Yes (always) |

---

## Cherry-Pick Plan

### Option A — Fast path: direct cherry-pick to `main`

This is the quickest way to activate the autonomous loop on all future PRs.

```bash
# 1. Fetch latest
git fetch origin

# 2. Create a hotfix branch from main
git checkout -b hotfix/workflow-cherry-pick-autonomous-loop origin/main

# 3. Cherry-pick the two workflow files from this PR branch
git checkout origin/copilot/cherry-pick-changes-to-branch -- \
  .github/workflows/copilot-review-responder.yml \
  .github/workflows/copilot-agent-session-done.yml

# 4. Commit
git commit -m "feat(workflows): add autonomous copilot review loop (cherry-pick from PR #3633)

- copilot-review-responder.yml: fires on issue_comment (Copilot posts
  overview as issue comment, not as review body) + pull_request_review;
  posts '@copilot apply changes in [this thread](URL#pullrequestreview-ID)'
- copilot-agent-session-done.yml: fires on workflow_run:Copilot Setup Steps;
  posts '@copilot review' after agent session ends (COPILOT_AGENT_AUTH_ENABLED)

Both workflows MUST be in main for workflow_run and issue_comment triggers.
Fixes: copilot-review-responder was always skipped (if condition checked
github.event.review.body which is empty — Copilot posts overview as a
separate issue comment, not as the review body)."

# 5. Open PR targeting main
gh pr create \
  --title "feat(workflows): autonomous copilot review loop (cherry-pick from PR #3633)" \
  --body "Cherry-picks copilot-review-responder.yml and copilot-agent-session-done.yml
from PR #3633 onto main so the workflow_run and issue_comment triggers fire.

These workflow files must be in the default branch (main) to trigger.
See .codex/docs/WORKFLOW_CHERRY_PICK_TO_MAIN_PLAN.md for full explanation.

Closes #3631 (dynaconf SBOM already updated in PR #3633)." \
  --base main \
  --head hotfix/workflow-cherry-pick-autonomous-loop
```

### Option B — Structured path: promote `0D_base_` → `main`

If `0D_base_` → `main` promotion is already planned (as stated in the PR
description), simply ensuring `0D_base_` contains the workflow files and
completing the promotion will activate the loop.

```bash
# Check if 0D_base_ already has the files
git show origin/0D_base_:.github/workflows/copilot-review-responder.yml 2>/dev/null \
  && echo "Present" || echo "Missing"

# If missing, cherry-pick from this branch onto 0D_base_
git checkout -b chore/sync-workflows-to-0D-base origin/0D_base_
git checkout origin/copilot/cherry-pick-changes-to-branch -- \
  .github/workflows/copilot-review-responder.yml \
  .github/workflows/copilot-agent-session-done.yml
git commit -m "feat(workflows): autonomous copilot review loop (from PR #3633)"
gh pr create --base 0D_base_ --head chore/sync-workflows-to-0D-base \
  --title "sync: autonomous review loop workflows to 0D_base_"

# Then follow the normal 0D_base_ → main promotion flow
```

---

## @copilot Prompt for Executing This Plan

Paste the following as a GitHub comment on the target PR (or use `gh workflow run`):

```
@copilot Please execute the workflow cherry-pick plan documented in
.codex/docs/WORKFLOW_CHERRY_PICK_TO_MAIN_PLAN.md (Option A — fast path).

Tasks:
1. Create branch `hotfix/workflow-cherry-pick-autonomous-loop` from `main`
2. Cherry-pick these two files from `copilot/cherry-pick-changes-to-branch`:
   - `.github/workflows/copilot-review-responder.yml`
   - `.github/workflows/copilot-agent-session-done.yml`
3. Commit with the message in the plan
4. Open a PR targeting `main`
5. Verify YAML syntax passes (`python -c "import yaml; yaml.safe_load(...)"`)
6. Document the PR number back in this issue as a follow-up comment

Context: These workflows require main to fire because they use
`issue_comment` and `workflow_run` triggers (GitHub resolves these
from the default branch only). See plan doc for full explanation.
```

---

## Post-Merge Validation

After the workflows land in `main`, validate the loop end-to-end:

1. Create a test PR (can be a trivial change)
2. Trigger `@copilot review` manually
3. Observe `copilot-review-responder.yml` fires on the `issue_comment` event
   (Copilot posts "generated N comments" as an issue comment)
4. Observe the workflow posts `@copilot apply changes based on the comments
   in [this thread](URL#pullrequestreview-ID)`
5. When the Copilot Coding Agent session ends, observe
   `copilot-agent-session-done.yml` fires and posts `@copilot review`
6. Confirm loop terminates when 0 comments are generated or when the agent
   doesn't push changes (loop guard prevents `@copilot review` spam)
