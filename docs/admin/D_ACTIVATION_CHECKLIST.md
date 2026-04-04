# D Model Activation Checklist

> **Purpose:** Step-by-step checklist for activating the D model (full autonomous operations)
> after successful Genesis Phase 1 and Phase 2 completion.
>
> **When to use:** After the human admin has completed all §1–§7 items in
> `ADMIN_MANUAL_SETUP_GUIDE.md` and the Admin Setup Verification workflow passes.
>
> **Rollback instructions:** See [§5 Rollback](#5-rollback) below.

---

## Prerequisites

Before starting, confirm all of the following:

- [ ] Genesis Phase 1 complete (template files committed, safety guards active)
- [ ] Genesis Phase 2 complete (human admin injected secrets, enabled workflows)
- [ ] `admin_setup_verification.yml` passes with ✅ for all §2–§7 checks
- [ ] `CODEX_MASTER_KEY` and `CODEX_BACKUP_KEY` are functional (§3a/§3b green)
- [ ] GitHub Discussions enabled and accessible (§4 green)
- [ ] At least one Copilot agent session has completed successfully on PR #3854

---

## §1 Pre-Activation Checklist

### 1.1 Repository Variables

Verify these repository variables are set (Settings → Secrets and variables → Actions → Variables):

| Variable | Required value | Purpose |
|----------|---------------|---------|
| `COPILOT_AGENT_AUTH_ENABLED` | `true` | Enables bot-posted @copilot triggers |
| `AUTONOMOUS_ACTIONS_ENABLED` | `true` | Allows autonomous code changes |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `true` | Enables session context injection |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | Current session (e.g. `296`) | Tracks active session |
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | Includes all three agent identities | Restricts CB access |

Expected `COGNITIVE_BRAIN_ALLOWED_ACTORS` value:
```
mbaetiong,github-actions[bot],copilot-swe-agent[bot],github-copilot[bot]
```

### 1.2 Secrets

| Secret | Purpose | Verify |
|--------|---------|--------|
| `CODEX_MASTER_KEY` | PAT for posting @copilot triggers as @mbaetiong | Run Admin Setup Verification |
| `CODEX_BACKUP_KEY` | Fallback PAT | Run Admin Setup Verification |

### 1.3 Workflow Concurrency Gate

Verify the session concurrency TTL is set to 1 hour:

```bash
grep -n "TTL_SECONDS" .github/workflows/agent-auth-delegation.yml
# Expected: const TTL_SECONDS = 3600; // 1 hour
```

### 1.4 Safety Guard Status

Verify safety guards are correctly configured:

```bash
# Script guard
grep -n "SAFE_MODE\|autonomous_actions_enabled" scripts/autonomous_agent.py | head -5

# Workflow guard (genesis-bootstrap.yml should have if: false in pre-activation)
grep -n "^    if:" .github/workflows/genesis-bootstrap.yml | head -3
```

---

## §2 Activation Steps (GitHub Actions)

### Step 1: Enable Agent Token Delegation

1. Navigate to PR #3854 on GitHub
2. Check the box **"🔐 Agent Token Delegation"** in the PR description
3. Confirm `COPILOT_AGENT_AUTH_ENABLED=true` is set as a repository variable
4. The `agent-auth-delegation.yml` workflow will fire on the next push

### Step 2: Approve Cost Governance

1. In the PR description, check **"💰 Cost Proposal Approved"**
2. This serves as standing approval for all sessions on this PR
3. Copilot sessions will now start without requiring additional approval gates

### Step 3: Trigger the First Autonomous Session

Post a comment on PR #3854:

```
@copilot+claude-sonnet-4.6 Please start the first autonomous session.
Load `.codex/CODEBASE_AGENCY_POLICY.md` and run the §ARLOOP PR Completion Sweep.
```

### Step 4: Verify Session Starts

Monitor the GitHub Actions tab for:
- `agent-auth-delegation.yml` — should acquire `COPILOT_ACTIVE_SESSION` lock
- `Copilot coding agent` workflow — should appear within 2–5 minutes of the comment

If no session starts within 10 minutes, see [§4 Troubleshooting](#4-troubleshooting).

---

## §3 Post-Activation Verification

After the first autonomous session completes:

### 3.1 Automated Checks

Run the Admin Setup Verification workflow:

```bash
# Replace 0D_base_ with the active PR branch name if different
gh workflow run "Admin Setup Verification" \
  --ref 0D_base_ \
  -f pr_number=3854
```

Verify all checks pass:
- [ ] `CODEX_MASTER_KEY` read + write: ✅
- [ ] `CODEX_BACKUP_KEY` read + write: ✅ (or ⚠️ if optional)
- [ ] GitHub Discussions: ✅
- [ ] Repository variables: ✅
- [ ] Follow-up prompt file: ✅

### 3.2 Session Health Checks

```bash
# Verify COPILOT_ACTIVE_SESSION was acquired and released correctly
gh api repos/Aries-Serpent/_codex_/actions/variables/COPILOT_ACTIVE_SESSION 2>/dev/null \
  || echo "No active session lock (expected after session completes)"

# Verify PDA loop is recording sessions
python3 scripts/ci/pda_failure_logger.py summarize

# Check agent_context.json was updated
python3 -c "
import json
with open('.codex/agent_context.json') as f:
    d = json.load(f)
print('Last session:', d.get('COGNITIVE_BRAIN_SESSION_NUMBER'))
print('Last SHA:', d.get('CODEX_CI_LAST_GREEN_SHA', '')[:12])
"
```

### 3.3 CI Health Check

```bash
# Check for any failing workflows on HEAD
python3 scripts/ci/scan_failing_workflows.py --sha "$(git rev-parse HEAD)"

# Verify ruff is clean
python3 -m ruff check . --quiet && echo "Ruff: ✅ clean" || echo "Ruff: ❌ errors"
```

### 3.4 Session Completion Attestation

Verify the completed session posted `<!-- session-completion-attestation -->` in a PR comment.
If missing, the `copilot-agent-checkin.yml` incomplete-session guard will auto-retrigger.

---

## §4 Troubleshooting

### Session Not Starting

**Symptom:** `@copilot` comment posted but no session started within 10 minutes.

**Diagnosis:**
```bash
# Check if agent-auth-delegation fired
gh run list --workflow=agent-auth-delegation.yml --limit=5

# Check COPILOT_ACTIVE_SESSION lock
gh api repos/Aries-Serpent/_codex_/actions/variables/COPILOT_ACTIVE_SESSION 2>/dev/null

# Check if another session has the lock
gh api repos/Aries-Serpent/_codex_/actions/variables/COPILOT_SESSION_QUEUE 2>/dev/null
```

**Fixes:**
1. If lock is stale (age > 1h): the TTL guard will auto-clear it on the next push
2. If queue is stuck: manually clear `COPILOT_SESSION_QUEUE` variable in repo settings
3. If `agent-auth-delegation.yml` failed: check the run logs for token issues

### Rescue Comment Not Triggering Session

**Symptom:** CI failure posted rescue comment but Copilot never started.

**Diagnosis:** The rescue comment must be posted as `@mbaetiong` (via `CODEX_MASTER_KEY`).
If posted as `github-actions[bot]`, Copilot will not respond to the @mention.

```bash
# Verify last rescue comment author
gh api repos/Aries-Serpent/_codex_/issues/3854/comments \
  --jq '[.[] | select(.body | test("ci-rescue-sha"))] | last | {author: .user.login, url: .html_url}'
```

**Fix:** Ensure `CODEX_MASTER_KEY` is functional and has `issues:write` scope.
Run Admin Setup Verification to confirm.

### COPILOT_ACTIVE_SESSION Lock Stuck

**Symptom:** New sessions can't start because TTL hasn't expired yet.

**Manual clear** (admin only):
```bash
gh api -X DELETE repos/Aries-Serpent/_codex_/actions/variables/COPILOT_ACTIVE_SESSION
```

---

## §5 Rollback

If autonomous operations need to be paused:

### Immediate Pause (soft stop)

1. Set `COPILOT_AGENT_AUTH_ENABLED` to `false` in repository variables
2. The `agent-auth-delegation.yml` and `copilot-agent-checkin.yml` missed-trigger guards
   will immediately stop posting new `@copilot` triggers
3. Any in-progress session will complete normally

### Full Rollback (hard stop)

1. Set `AUTONOMOUS_ACTIONS_ENABLED` to `false`
2. Set `COPILOT_AGENT_AUTH_ENABLED` to `false`
3. Clear `COPILOT_ACTIVE_SESSION` variable if set
4. Clear `COPILOT_SESSION_QUEUE` variable if set

To verify rollback is effective:
```bash
gh api repos/Aries-Serpent/_codex_/actions/variables \
  --jq '.variables[] | select(.name | startswith("COPILOT")) | {name, value}'
```

---

## §6 Reference

| Document | Purpose |
|----------|---------|
| `ADMIN_MANUAL_SETUP_GUIDE.md` | Click-by-click setup instructions |
| `GENESIS_SETUP_GUIDE.md` | Full Genesis Protocol documentation |
| `docs/ci/PR_LIFECYCLE.md` | PR lifecycle and session management |
| `.codex/CODEBASE_AGENCY_POLICY.md` | Agent accountability policy |
| `.codex/guardrails.md` | Operational constraints |
| `scripts/ci/scan_failing_workflows.py` | Grounded workflow health scanner |

---

*Document version: 1.0.0 — S296 (2026-04-03)*
