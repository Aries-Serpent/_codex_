# [Validation]: Workflow Expiry Enforcer — auto-disable on next commit
> Generated: 2025-10-20 23:58:36 UTC | Author: mbaetiong

Goal
- Verify that CI workflows are automatically disabled (moved out of .github/workflows/) once the OWNER approval window expires, specifically on the next user commit.

Pre-checks
- .github/OWNER_APPROVAL.yml configured with:
  - enabled: true
  - mode: "duration" + duration: "24h" and a recent created_at
  - or mode: "until" + until: "YYYY-MM-DDTHH:MM:SSZ"
- Repo grants contents: write to GITHUB_TOKEN for the enforcer workflow to commit.

Scenarios
1. During approval window
   - Push a commit to any branch.
   - Expect: enforcer logs “Approval window active; no workflows moved.”
2. After expiry
   - Push a commit (any file change).
   - Expect: enforcer moves all workflow YAMLs except itself to .github/_workflows_disabled/, commits, and pushes to the branch.
3. Idempotency
   - Push again after workflows moved.
   - Expect: enforcer reports “No workflows to move” and exits 0.

Notes
- If branch protections block direct push by GITHUB_TOKEN, the enforcer prints a warning to open a PR; files are staged and committed locally in the run log for manual promotion.
- The enforcer leaves itself in .github/workflows/ so it can continue to observe future windows.
- Policy-proof Docker workflow ensures CI build/push completes during the window under restrictive Actions policies.

Troubleshooting
- “could not compute expiry”: check created_at and duration formatting.
- Push failure: allow Actions to push to the branch or promote via PR.
- No workflows moved: they may already be in .github/_workflows_disabled/ or only enforcer exists.
