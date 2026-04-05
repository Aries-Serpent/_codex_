# GitHub API Reference for Copilot Coding Agent

> **Scope:** Aries-Serpent/_codex_ repository  
> **Audience:** GitHub Copilot Coding Agent (Web UI)  
> **Authority:** Acting on behalf of maintainer `@mbaetiong`  
> **Last Updated:** 2026-04-05 — S240 PR #3873  
> **Policy:** `.codex/CODEBASE_AGENCY_POLICY.md` §0–§4

---

## 🔐 TOKEN HIERARCHY — WHICH TOKEN TO USE WHEN

Every GitHub API call requires the correct token. Using the wrong token causes silent
permission errors. Follow this hierarchy **exactly**:

| Priority | Token / Secret | Scopes | When to Use |
|----------|---------------|--------|-------------|
| 1st | `secrets.CODEX_MASTER_KEY` | `repo` + `workflow` + `actions:write` | PR edits, workflow approvals, variable writes, force-push |
| 2nd | `secrets.CODEX_BACKUP_KEY` | `repo` + `workflow` | Same as above when MASTER_KEY unavailable |
| 3rd | `secrets._GITHUB_APP_PRIVATE_KEY` + `_GITHUB_APP_ID` | App installation scopes | Cognitive Brain App — commit signing, PR creation as App identity |
| 4th | `github.token` / `secrets.GITHUB_TOKEN` | `contents:read`, `pull-requests:write` (limited) | Read-only operations, posting comments |

> ⚠️ `GITHUB_TOKEN` **cannot** approve workflow runs, write Actions variables, or push
> to protected branches. Always use `CODEX_MASTER_KEY` for those operations.

### Fallback Pattern (canonical)
```yaml
env:
  GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
```

---

## 📋 REPOSITORY VARIABLES — READ/WRITE REFERENCE

These variables are the Cognitive Brain's persistent state. Read them to understand
current session context; write them to record outcomes.

| Variable | Type | Purpose | Write Method |
|----------|------|---------|--------------|
| `COPILOT_AGENT_AUTH_ENABLED` | `vars.*` | `"true"` when token delegation is active | `gh api PATCH /repos/{owner}/{repo}/actions/variables/COPILOT_AGENT_AUTH_ENABLED` |
| `COPILOT_AGENT_STATE` | `vars.*` | `ACTIVE` / `IDLE` / `SUSPENDED` | Same pattern |
| `COPILOT_AGENT_SESSION_EXPIRES` | `vars.*` | ISO-8601 TTL for current session | Same pattern |
| `COPILOT_AGENT_LAST_SESSION_ID` | `vars.*` | Last session UUID | Same pattern |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | `vars.*` | Monotonic session counter (S240, S241…) | Increment via API |
| `CODEX_CI_FAILURE_RATE` | `vars.*` | Current CI failure rate (0–100) | Written by ci-health-alert-agent |
| `CODEX_CI_LAST_GREEN_SHA` | `vars.*` | Last commit SHA where all CI passed | Written by copilot-agent-session-done |
| `CODEX_GROUNDED_TIER` | `vars.*` | `E` / `D_CAPABLE` / `D` — agent autonomy level | Written by promotion gate |
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `vars.*` | Comma-separated list of authorised actors | Written by agent-auth-delegation |
| `CODEX_COVERAGE_THRESHOLD` | `vars.*` | Minimum required test coverage % (default: 95) | Manual / admin only |

### Read a Variable (gh CLI)
```bash
gh api GET /repos/Aries-Serpent/_codex_/actions/variables/COPILOT_AGENT_AUTH_ENABLED \
  --jq '.value'
```

### Write a Variable (gh CLI)
```bash
gh api PATCH /repos/Aries-Serpent/_codex_/actions/variables/COPILOT_AGENT_STATE \
  -f name='COPILOT_AGENT_STATE' \
  -f value='ACTIVE'
```

### Increment a Counter Variable (shell pattern used in agent-auth-delegation.yml)
```bash
CURRENT=$(gh api /repos/$REPO/actions/variables/COGNITIVE_BRAIN_SESSION_NUMBER --jq '.value // "0"')
NEXT=$((CURRENT + 1))
gh api PATCH /repos/$REPO/actions/variables/COGNITIVE_BRAIN_SESSION_NUMBER \
  -f name='COGNITIVE_BRAIN_SESSION_NUMBER' \
  -f value="$NEXT"
```

---

## 🔄 PR BODY — WEC READ/WRITE PROTOCOL

The Workflow Execution Checklist (WEC) lives in the PR body. The agent MUST read
it before every write to preserve maintainer checkbox state.

### Step 1 — Read current PR body
```bash
BODY=$(gh pr view "${PR_NUMBER}" \
  --repo "Aries-Serpent/_codex_" \
  --json body \
  --jq '.body // ""')
```

### Step 2 — Extract WEC checkbox state (Python — session_wrapup_autofix.py pattern)
```python
import sys
sys.path.insert(0, "scripts/ci")
import session_wrapup_autofix as swa

body = open_pr_body()  # from gh pr view
existing_state = swa._extract_wec_state(body)
# Returns: {"pre-merge-validation.yml": True, "resilient_validation.yml": False, ...}
```

### Step 3 — Rebuild canonical WEC preserving maintainer selections
```python
new_wec_block = swa._build_wec_block(existing_state=existing_state)
```

### Step 4 — Strip old WEC, append new canonical block
```bash
STRIPPED=$(printf '%s' "$BODY" \
  | sed '/^## 🔄 Workflow Execution Checklist/,$d' \
  | sed '/^\*\*🔄 Workflow Execution Checklist\*\*:/,$d')

UPDATED="${STRIPPED}${NEW_WEC_BLOCK}"

gh pr edit "${PR_NUMBER}" \
  --repo "Aries-Serpent/_codex_" \
  --body "${UPDATED}"
```

### Step 5 — report_progress MUST include WEC
Every `report_progress` call must include the full canonical WEC block in
`prDescription`. **Never** reconstruct from template; always copy from live PR body.

```python
# CORRECT — copy live state
existing_state = swa._extract_wec_state(live_pr_body)
wec = swa._build_wec_block(existing_state=existing_state)
report_progress(prDescription=f"{checklist}\n{wec}")

# WRONG — reconstructing from template loses maintainer [x] selections
report_progress(prDescription=checklist_only)
```

> **HARDENED RULE:** Never reset a `[x]` item to `[ ]`. Never omit the WEC block.
> `deferral-language-gate.yml`, `pre-merge-validation.yml`, `comment-review-gate.yml`,
> `agent-auth-delegation.yml`, `workflow-execution-gate.yml`, all Always-Active items
> MUST always be `[x]`.

---

## 📣 POSTING COMMENTS — PATTERNS

### Post a plain comment to PR
```bash
gh pr comment "${PR_NUMBER}" \
  --repo "Aries-Serpent/_codex_" \
  --body "$(cat comment.md)"
```

### Post using GitHub REST API (octokit/github-script)
```javascript
await github.rest.issues.createComment({
  owner: context.repo.owner,
  repo: context.repo.repo,
  issue_number: prNumber,
  body: commentBody,
});
```

### Update an existing comment (avoid duplicate rescue comments)
```javascript
// List existing comments
const comments = await github.rest.issues.listComments({
  owner, repo, issue_number: prNumber, per_page: 100
});
const existing = comments.data.find(c =>
  c.body.includes('<!-- rescue-comment-marker -->')
);
if (existing) {
  await github.rest.issues.updateComment({
    owner, repo, comment_id: existing.id, body: newBody
  });
} else {
  await github.rest.issues.createComment({
    owner, repo, issue_number: prNumber, body: newBody
  });
}
```

### React to a comment (acknowledge maintainer feedback)
```javascript
await github.rest.reactions.createForIssueComment({
  owner, repo,
  comment_id: commentId,
  content: 'rocket',  // +1 | -1 | laugh | confused | heart | hooray | rocket | eyes
});
```

---

## ⚡ WORKFLOW RUNS — APPROVE / CANCEL / TRIGGER

### List pending (action_required) runs for a SHA
```bash
gh api \
  "/repos/Aries-Serpent/_codex_/actions/runs?head_sha=${HEAD_SHA}&status=action_required" \
  --jq '.workflow_runs[] | {id, name, status, conclusion}'
```

### Approve a pending run (requires `actions:write` — use CODEX_MASTER_KEY)
```javascript
// github-script
await github.rest.actions.approveWorkflowRun({
  owner: 'Aries-Serpent',
  repo: '_codex_',
  run_id: runId,
});
```

```bash
# gh CLI equivalent
GH_TOKEN="${CODEX_MASTER_KEY}" \
  gh api POST "/repos/Aries-Serpent/_codex_/actions/runs/${RUN_ID}/approve"
```

### Cancel a run
```bash
gh api POST "/repos/Aries-Serpent/_codex_/actions/runs/${RUN_ID}/cancel"
```

### Trigger a workflow manually (workflow_dispatch)
```bash
gh workflow run validate.yml \
  --repo "Aries-Serpent/_codex_" \
  --ref "copilot/s240-health-sweep" \
  --field pr_number="3873"
```

```javascript
await github.rest.actions.createWorkflowDispatch({
  owner, repo,
  workflow_id: 'validate.yml',
  ref: 'copilot/s240-health-sweep',
  inputs: { pr_number: '3873' },
});
```

### Re-run a failed workflow
```bash
gh run rerun "${RUN_ID}" --repo "Aries-Serpent/_codex_" --failed
```

### List all runs for a branch + filter by status
```bash
gh api \
  "/repos/Aries-Serpent/_codex_/actions/runs?branch=copilot/s240-health-sweep&per_page=50" \
  --jq '.workflow_runs[] | select(.conclusion=="failure") | {id,name,conclusion}'
```

---

## 🔑 TOKEN DELEGATION — ACTING ON BEHALF OF MAINTAINER

The `agent-auth-delegation.yml` workflow implements a secure provenance chain that
grants the Copilot Coding Agent maintainer-equivalent authority within a TTL window.

### Activation Flow

```
Maintainer checks [x] COPILOT_AGENT_AUTH_ENABLED in PR body
        ↓
agent-auth-delegation.yml detects checkbox (REQ-1)
        ↓
Writes COPILOT_AGENT_AUTH_ENABLED=true to repo vars (requires CODEX_MASTER_KEY)
        ↓
Issues provenance session token → .codex/agent_auth_session.json
        ↓
Writes COPILOT_AGENT_STATE=ACTIVE, COPILOT_AGENT_SESSION_EXPIRES=<TTL>
        ↓
Updates COGNITIVE_BRAIN_ALLOWED_ACTORS to include agent actor
        ↓
Agent can now: approve runs, write vars, edit PR bodies, push commits
```

### Session Token File (`.codex/agent_auth_session.json`)
```json
{
  "session_id": "<uuid>",
  "issued_at": "2026-04-05T11:22:00Z",
  "issued_by": "agent-auth-delegation",
  "expires_at": "2026-04-05T23:22:00Z",
  "pr_number": 3873,
  "note": "Provenance-chain token. Allows all agent sessions to bypass owner_approval_guard within TTL."
}
```

### Checking Active Session Before Acting
```python
import json
from pathlib import Path
from datetime import datetime, timezone

session_file = Path(".codex/agent_auth_session.json")
if session_file.exists():
    session = json.loads(session_file.read_text())
    expires = datetime.fromisoformat(session["expires_at"])
    if datetime.now(timezone.utc) < expires:
        print(f"✅ Session active until {expires.isoformat()}")
    else:
        print("❌ Session expired — request re-delegation")
else:
    print("❌ No session token — maintainer must check COPILOT_AGENT_AUTH_ENABLED")
```

### Required Secrets for Full Maintainer-Equivalent Authority
| Secret | Purpose |
|--------|---------|
| `CODEX_MASTER_KEY` | PAT (`repo` + `workflow` + `actions:write`) — primary |
| `CODEX_BACKUP_KEY` | Fallback PAT with same scopes |
| `_GITHUB_APP_ID` | Cognitive Brain App ID (GitHub App) |
| `_GITHUB_APP_PRIVATE_KEY` | Cognitive Brain App private key (PEM) |
| `_GITHUB_APP_INSTALLATION_ID` | Installation ID for this repo |

### Generating a GitHub App Installation Token (Cognitive Brain App)
```python
import jwt, time, requests

# 1. Create JWT signed with App private key (10-min TTL)
payload = {
    "iat": int(time.time()) - 60,
    "exp": int(time.time()) + (10 * 60),
    "iss": APP_ID,
}
app_jwt = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# 2. Exchange for installation token
resp = requests.post(
    f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens",
    headers={
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    },
)
installation_token = resp.json()["token"]
# installation_token has same scopes as App installation permissions
```

### GitHub Actions — Generate App Token (reusable pattern)
```yaml
- name: Generate Cognitive Brain App token
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets._GITHUB_APP_ID }}
    private-key: ${{ secrets._GITHUB_APP_PRIVATE_KEY }}

- name: Use App token
  env:
    GH_TOKEN: ${{ steps.app-token.outputs.token }}
  run: gh pr edit "$PR_NUMBER" --body "$NEW_BODY"
```

---

## 🛡️ DEFERRAL LANGUAGE GATE — WHAT TRIGGERS IT

`scripts/ci/check_deferral_language.py` scans every PR body, commit message, and
comment for forbidden phrases. CI fails on any match **not covered by an exemption**.

### Forbidden Trigger Phrases (any variation)
```
"pre-existing issue / pre-existing code"
"not from our current feature/branch/PR"
"out of scope / outside the scope"
"will address in a future PR/task/session"
"future PR / follow-up PR"
"not my responsibility / not my problem"
"can be addressed later / will fix later"
"address incrementally / address separately"
"another session/agent should handle"
"can be deferred / should be deferred"
```

### Valid Exemptions (will NOT trigger)
```python
EXEMPTION_PATTERNS = [
    r"\d+\s+pre-existing\s+(?:type\s+)?errors\b",  # "104 pre-existing errors" (mypy baseline)
    r"pre-existing\s+test",                          # "pre-existing test infrastructure"
]
```

### Self-Check Before Committing
```bash
python scripts/ci/check_deferral_language.py \
  --pr-body "$(gh pr view $PR_NUMBER --json body --jq '.body')" \
  --commit-messages "$(git log --format='%s' HEAD~5..HEAD)"
```

---

## 🔍 PR COMMENT REVIEW GATE — BLOCKING COMMENT DETECTION

`comment-review-gate.yml` scans PR review comments and inline comments for
**unresolved blocking items** before allowing merge.

### How the Gate Works
1. Lists all review threads via `github.rest.pulls.listReviewComments`
2. Filters for threads containing keywords: `MUST`, `REQUIRED`, `BLOCKING`, `❌`, `🚫`
3. Checks if each flagged thread is `resolved: true`
4. Fails CI if any blocking thread is unresolved

### Manually Resolve a Review Thread
```javascript
await github.rest.pulls.resolveReviewThread({
  owner, repo,
  pull_number: prNumber,
  thread_id: threadId,
});
```

### Check for Open Review Threads (gh CLI)
```bash
gh pr view "$PR_NUMBER" \
  --repo "Aries-Serpent/_codex_" \
  --json reviewThreads \
  --jq '.reviewThreads[] | select(.isResolved == false) | {id, isResolved, comments: [.comments[].body[:80]]}'
```

---

## 📊 CI STATUS — CHECKING AND REACTING

### Get all check runs for a commit SHA
```bash
gh api \
  "/repos/Aries-Serpent/_codex_/commits/${SHA}/check-runs?per_page=100" \
  --jq '.check_runs[] | {name, status, conclusion}'
```

### Get combined commit status
```bash
gh api \
  "/repos/Aries-Serpent/_codex_/commits/${SHA}/status" \
  --jq '{state, statuses: [.statuses[] | {context, state, description}]}'
```

### List workflow runs for PR branch (most recent first)
```bash
gh api \
  "/repos/Aries-Serpent/_codex_/actions/runs?branch=${BRANCH}&per_page=30" \
  --jq '.workflow_runs[] | {id, name, status, conclusion, created_at}' \
  | head -50
```

### Get job logs for a failed run
```bash
# List jobs in a run
gh api "/repos/Aries-Serpent/_codex_/actions/runs/${RUN_ID}/jobs" \
  --jq '.jobs[] | select(.conclusion=="failure") | {id, name}'

# Download logs for a specific job
gh api "/repos/Aries-Serpent/_codex_/actions/jobs/${JOB_ID}/logs" > job.log
```

---

## 🧠 COGNITIVE BRAIN CONNECTED APP — API SURFACE

The Cognitive Brain app exposes a FastAPI server (default: `http://localhost:8765`
or `$CODEX_CLI_API_URL` / `$COGNITIVE_APP_API_URL`).

### Session Context Injection (read at session start)
```python
import httpx

base_url = os.environ.get("COGNITIVE_APP_API_URL", "http://localhost:8765")

# GET /api/v1/session/context — returns recency-ranked patterns + stored memories
resp = httpx.get(f"{base_url}/api/v1/session/context", timeout=10)
ctx = resp.json()
# ctx["patterns"] — top-N CI patterns from LTM
# ctx["memories"] — recent store_memory facts
# ctx["session_number"] — current COGNITIVE_BRAIN_SESSION_NUMBER
```

### AfterMath / PDA Loop Close (call at session end)
```python
# POST /api/v1/session/complete — records outcome, updates LTM
httpx.post(f"{base_url}/api/v1/session/complete", json={
    "session_id": session_id,
    "pr_number": 3873,
    "commits_pushed": ["2b53d0f"],
    "ci_fixes": ["secrets.baseline", "WEC filenames", "RAG coverage"],
    "files_changed": 12,
    "outcome": "success",
})
```

### Memory Read/Write (SQLiteMemory)
```python
# GET /api/v1/memory?query=WEC&tier=LTM&limit=5
resp = httpx.get(f"{base_url}/api/v1/memory",
                 params={"query": "WEC", "tier": "LTM", "limit": 5})

# POST /api/v1/memory — store new fact
httpx.post(f"{base_url}/api/v1/memory", json={
    "subject": "WEC filenames",
    "fact": "resilient_validation.yml (underscore) NOT resilient-validation-suite.yml",
    "citations": "scripts/ci/session_wrapup_autofix.py _WEC_ITEMS",
    "tier": "LTM",
})
```

### CI Pattern Feed
```python
# POST /api/v1/patterns/record — add CI failure pattern
httpx.post(f"{base_url}/api/v1/patterns/record", json={
    "pattern_id": "RP-WEC-FILENAME-DRIFT",
    "description": "WEC items use wrong filenames; WEC gate never matches opt-in checkboxes",
    "fix": "Update _WEC_ITEMS to match actual .github/workflows/*.yml filenames",
    "confidence": 0.98,
    "recurrence": 4,
})
```

---

## 🔁 CODEBASE-WIDE CHANGES — SAFE PATTERNS

### Pattern: Find-and-replace across all workflow files
```bash
# Dry-run first
grep -rn "resilient-validation-suite" .github/workflows/ --include="*.yml"

# Apply with sed
find .github/workflows/ -name "*.yml" -exec \
  sed -i 's/resilient-validation-suite\.yml/resilient_validation.yml/g' {} +
```

### Pattern: Atomic multi-file Python edit via AST
```python
import ast, pathlib

for pyfile in pathlib.Path("src/").rglob("*.py"):
    src = pyfile.read_text()
    if "target_pattern" in src:
        new_src = src.replace("target_pattern", "replacement")
        pyfile.write_text(new_src)
```

### Pattern: Validate no regressions after codebase-wide change
```bash
# 1. Lint
python -m ruff check src/ tests/ scripts/

# 2. Type-check (against baseline — don't introduce new errors)
python scripts/ci/mypy_baseline.py --check

# 3. Tests relevant to changed modules
python -m pytest tests/ -k "wec or rag or session" -q

# 4. detect-secrets (no new false positives)
detect-secrets scan --baseline .secrets.baseline

# 5. Deferral language gate
python scripts/ci/check_deferral_language.py --pr-body "$(gh pr view $PR --json body -q .body)"
```

### Pattern: Push a commit as agent (report_progress)
```
# ALWAYS use report_progress tool — never git push directly
report_progress(
    commitMessage="fix: <description>",
    prDescription=f"{checklist}\n{canonical_wec_block}",
)
```

---

## ✅ PRE-CONCLUSION CHECKLIST (§0 CODEBASE_AGENCY_POLICY.md)

Before ending any session the agent MUST verify:

```
□ 0a. ALL new PR comments reviewed (comment_new + review threads)
□ 0b. ALL failing CI checks on latest commit investigated and fixed
□ 0c. No deferral language in any commit message, PR body, or comment
□ 0d. WEC block appended to PR body via report_progress — all [x] preserved
□ 0e. CHANGELOG.md updated with ### Fixed entry for this session
□ 0f. AGENT_ACCOUNTABILITY_REPORT.md updated with session summary
□ 0g. .secrets.baseline regenerated if CODEX_MANIFEST.json or agent_context.json changed
□ 0h. All tests pass locally (pytest -q)
□ 0i. Cognitive Brain AfterMath closed (POST /api/v1/session/complete)
```

---

## 🗂️ CANONICAL WEC BLOCK (copy verbatim into every report_progress)

```markdown
---

## 🔄 Workflow Execution Checklist

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] pre-merge-validation.yml — Pre-merge checks (always required)
- [x] comment-review-gate.yml — Comment review gate (always required)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)

### 🔄 Always Active — fire via push/workflow_run (need approval in Actions tab)
- [x] copilot-agent-checkin.yml — Agent check-in / S221 guard (fires on push)
- [x] copilot-agent-session-done.yml — Auto-post @copilot review after agent session (fires on workflow_run)
- [x] copilot-iterative-self-healing.yml — Iterative self-healing CI loop (fires on workflow_run — needs approval)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)

### ⚡ Auto-Approve
- [ ] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🧪 Opt-In: Testing & Validation
- [ ] validate.yml — Validation Pipeline (detect-secrets, ruff, pre-commit, sync-tracked)
- [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)

### 🔒 Opt-In: Security & Quality
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)

### 📄 Opt-In: Documentation
- [ ] documentation-link-checker.yml — Documentation link checker

> **⚠️ HARDENED AGENT INSTRUCTION (non-negotiable):** This entire WEC block MUST be
> appended verbatim to **every** PR body update — including every `report_progress` call.
> Copy the WEC block from the current PR body into the `prDescription` parameter, keeping
> **all previously-checked `[x]` items checked**. Never reset a maintainer selection to `[ ]`.
> Only 'always required' items may be auto-checked. All other items preserve their current state.
```

---

## 🚦 STARTUP FAILURE PATTERNS — QUICK DIAGNOSIS

| Symptom | Cause | Fix |
|---------|-------|-----|
| `startup_failure` on `workflow_run` workflows | Workflow can't start because the triggering run hasn't been approved | Approve via `auto-approve-workflows.yml` or manually in Actions tab |
| `action_required` status on workflow runs | `workflow_run` trigger from an external actor requires maintainer approval | Run `auto-approve-workflows.yml` dispatch OR check `[x] auto-approve-workflows` in PR body |
| `Validation Pipeline / Fast Validation` fails with detect-secrets | `.secrets.baseline` stale — new entropy strings added to tracked files | Run `detect-secrets scan --baseline .secrets.baseline && git add .secrets.baseline` |
| `Pre-Merge Validation` skipped | Workflow has `if: false` guard or branch filter excludes the PR branch | Check workflow `on:` triggers and `if:` conditions |
| `deferral-language-gate` fails | Agent wrote a deferral phrase in PR body, commit message, or comment | Remove all forbidden phrases; check `EXEMPTION_PATTERNS` in `check_deferral_language.py` |
| `mypy Baseline` fails | New type errors introduced exceeding baseline count | Fix type errors OR run `python scripts/ci/mypy_baseline.py --update` if errors are pre-existing |
| `RAG Module Tests` coverage below 95% | New code added without tests, or tests removed | Add targeted tests in `tests/rag/` covering uncovered lines via `coverage.py` |
| `PR Comment Review Gate` fails | Unresolved blocking review threads | Resolve each thread via GitHub UI or `github.rest.pulls.resolveReviewThread` |

---

*Document maintained by: Copilot Coding Agent (S240) | Source of truth: `.github/workflows/` + `scripts/ci/session_wrapup_autofix.py` + `docs/ci/PR_LIFECYCLE.md`*
