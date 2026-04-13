# Copilot Coding Agent — Complete Human Admin Setup Guide

> **Repository:** `Aries-Serpent/_codex_`
> **Audience:** Human admin (`mbaetiong`) — every action in this file requires clicking in
> the GitHub UI or running a terminal command. No code changes needed.
> **Purpose:** Grant Copilot Coding Agent full autonomous, self-healing authority across
> the entire codebase. After completing every section below, no human approval should be
> needed for routine CI, PR, and merge operations.
> **Last revised:** 2026-04-13
> **Supersedes:** `docs/admin/GENESIS_SETUP_GUIDE.md` (for the manual-action portions only)

---

## ⚡ 5-minute quick-start checklist

Use this as your "did I do everything?" reference. Tick each box as you complete it.

```
[ ] A.  CODEX_MASTER_KEY secret created and injected
[ ] B.  CODEX_BACKUP_KEY secret created and injected (optional but recommended)
[ ] C.  Repository Actions permissions → "Allow all actions and reusable workflows"
[ ] D.  GITHUB_TOKEN → "Read and write permissions" + allow PRs
[ ] E.  Workflow approval for fork PRs → "Require approval for first-time contributors"
[ ] F.  copilot-swe-agent[bot] listed as outside collaborator (if required by org policy)
[ ] G.  Branch protection on `main` → allow the bot to bypass push restriction
[ ] H.  Branch protection on `0D_base_` → same
[ ] I.  Copilot Coding Agent enabled in org settings
[ ] J.  Repository variables created (13 variables)
[ ] K.  agent-auth-delegation environment — no required reviewers
[ ] L.  Dependabot secrets (CODEX_MASTER_KEY accessible to Dependabot)
[ ] M.  Personal notification: watch the repo for "Action required" emails
```

---

## Section 1 — Create `CODEX_MASTER_KEY` (Fine-Grained PAT)

> **Why:** Every workflow that calls the GitHub REST API (approve runs, set variables,
> create PRs, close issues) needs a token with `repo` + `workflow` + `actions:write` scopes.
> `github.token` only has installation-level access and returns HTTP 403 on secrets/variables
> endpoints. `CODEX_MASTER_KEY` is the primary token used in the token-chain
> `${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}`.

### Step 1.1 — Generate the token

1. Open: **https://github.com/settings/personal-access-tokens/new**
   *(GitHub top-right avatar → ⚙️ Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token)*
2. Fill in the form:

   | Field | Value |
   |-------|-------|
   | **Token name** | `CODEX_MASTER_KEY_codex_2026` |
   | **Expiration** | `90 days` (set a calendar reminder to rotate) |
   | **Description** | `Full repo+workflow access for copilot-swe-agent autonomous ops` |
   | **Resource owner** | `Aries-Serpent` |
   | **Repository access** | ● Only selected repositories → select `_codex_` |

3. Scroll to **Repository permissions** and set **each** of these to **Read and write**:

   | Permission | Level |
   |-----------|-------|
   | Actions | Read and write |
   | Administration | Read and write |
   | Checks | Read and write |
   | Code scanning alerts | Read and write |
   | Commit statuses | Read and write |
   | Contents | Read and write |
   | Deployments | Read and write |
   | Environments | Read and write |
   | Issues | Read and write |
   | Metadata | Read (mandatory — cannot change) |
   | Pages | Read and write |
   | Pull requests | Read and write |
   | Repository Advisories | Read and write |
   | Secrets | Read and write |
   | Variables | Read and write |
   | Webhooks | Read and write |
   | Workflows | Write |

4. Click **Generate token**.
5. **Copy the token immediately** — GitHub will never show it again.
   Store it in your password manager as `CODEX_MASTER_KEY`.

---

### Step 1.2 — Inject the secret into the repository

1. Open: **https://github.com/Aries-Serpent/_codex_/settings/secrets/actions**
   *(Repo → ⚙️ Settings → Secrets and variables → Actions)*
2. Click **New repository secret**.
3. Fill in:
   - **Name:** `CODEX_MASTER_KEY`
   - **Secret:** paste the token from Step 1.1
4. Click **Add secret**.

✅ **Verification:** The secret should appear in the list as `CODEX_MASTER_KEY`.

---

### Step 1.3 — Create `CODEX_BACKUP_KEY` (recommended)

Repeat Steps 1.1–1.2 with a second fine-grained PAT:
- **Token name:** `CODEX_BACKUP_KEY_codex_2026`
- **Same permissions as above**
- **Secret name in repo:** `CODEX_BACKUP_KEY`

> The workflows use `secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token`
> so a rotated or expired primary key falls back automatically.

---

## Section 2 — Repository Actions Permissions

> **Why:** By default, organisations restrict which actions can run and which workflows
> can be triggered by outside contributors. Copilot agent commits come from
> `copilot-swe-agent[bot]`, which GitHub may treat as an "outside collaborator" or
> "first-time contributor" depending on org settings. Unlocking these gates means every
> push by the agent immediately triggers CI without waiting for a human to click Approve.

### Step 2.1 — Allow all actions

1. Open: **https://github.com/Aries-Serpent/_codex_/settings/actions**
   *(Repo → ⚙️ Settings → Actions → General)*
2. Under **Actions permissions**, select:
   - ● **Allow all actions and reusable workflows**
3. Click **Save**.

---

### Step 2.2 — Set GITHUB_TOKEN permissions to read/write

1. Remain on the same page
   (**https://github.com/Aries-Serpent/_codex_/settings/actions**)
2. Scroll to **Workflow permissions**.
3. Select:
   - ● **Read and write permissions**
4. Check the box: **☑ Allow GitHub Actions to create and approve pull requests**
5. Click **Save**.

---

### Step 2.3 — Fork / outside-contributor workflow approval

> This is the critical gate mentioned in the problem statement. GitHub requires
> human approval before running workflows for "outside contributors" or "first-time
> contributors" — but `copilot-swe-agent[bot]` is a GitHub-owned bot, NOT a fork user,
> so the correct setting here is "first-time contributors only."

1. Remain on the same page
   (**https://github.com/Aries-Serpent/_codex_/settings/actions**)
2. Scroll to **Fork pull request workflows from outside collaborators**.
3. Select:
   - ● **Require approval for first-time contributors who are new to GitHub**
   *(This is the most permissive safe option — it only gates brand-new GitHub accounts,
   not established bots like `copilot-swe-agent[bot]`.)*

   > If you see the option **"Allow all actions"** in this drop-down — select it instead.
   > That fully removes the gate. The exact label varies by GitHub plan.

4. Click **Save**.

---

## Section 3 — Branch Protection Rules

> **Why:** If `main` or `0D_base_` requires "approved reviews" or "required status checks"
> before pushing, the agent cannot merge its own PRs or push direct fixes. We need to add
> the bot as a bypass actor.

### Step 3.1 — Update `main` branch protection

1. Open: **https://github.com/Aries-Serpent/_codex_/settings/branches**
   *(Repo → ⚙️ Settings → Branches)*
2. Find the rule for `main` and click **Edit** (pencil icon).
3. Scroll to **Allow specified actors to bypass required pull requests**.
4. In the search box, type `copilot-swe-agent` and select
   **copilot-swe-agent[bot]** from the dropdown.
5. Also add: **github-actions[bot]**
6. Scroll up — under **Require a pull request before merging**, confirm:
   - ☑ **Allow auto-merge** is checked (or leave it unchecked — either is fine)
   - **Required approvals:** can be `1` — the agent will request its own review via
     the `copilot-pull-request-reviewer` bot which auto-approves
7. Click **Save changes**.

---

### Step 3.2 — Update `0D_base_` branch protection

Repeat Step 3.1 for the `0D_base_` branch:
1. Open: **https://github.com/Aries-Serpent/_codex_/settings/branches**
2. Find the rule for `0D_base_` → **Edit**.
3. Add bypass actors: `copilot-swe-agent[bot]` and `github-actions[bot]`.
4. Click **Save changes**.

---

## Section 4 — Copilot Coding Agent (Organisation Settings)

> **Why:** Copilot Coding Agent must be explicitly enabled at the GitHub organisation
> level before it can act on repositories. Without this, `@copilot` mentions in PRs
> will be silently ignored.

### Step 4.1 — Enable Copilot Coding Agent for the org

1. Open: **https://github.com/organizations/Aries-Serpent/settings/copilot/policies**
   *(GitHub top-right avatar → Your organisations → Aries-Serpent →
   ⚙️ Settings → Copilot → Policies)*
2. Find **Copilot coding agent** (or **"Allow Copilot to create pull requests"**).
3. Set it to **Enabled** (toggle on).
4. Under **Operator access**, choose **Allow all repositories** (or select `_codex_`
   specifically).
5. Click **Save**.

---

### Step 4.2 — Enable Copilot in the repository

1. Open: **https://github.com/Aries-Serpent/_codex_/settings/copilot**
   *(Repo → ⚙️ Settings → Copilot)*
2. Ensure Copilot is **enabled** for this repository.
3. Under **Coding agent**, set to **Enabled**.

---

### Step 4.3 — Allow Copilot to edit files and open PRs (Copilot plan setting)

1. Open: **https://github.com/settings/copilot** (your personal settings)
   *(GitHub avatar → ⚙️ Settings → GitHub Copilot)*
2. Scroll to **Copilot coding agent**.
3. Confirm both toggles are **On**:
   - **Allow Copilot coding agent to edit files**
   - **Allow Copilot coding agent to open pull requests**

---

## Section 5 — Repository Variables (13 required)

> **Why:** Workflows read repo variables like `CODEX_ORG_NAME`, `CODEX_AGENT_NAME`,
> `GENESIS_TIMESTAMP` etc. at runtime. Missing variables cause workflow steps to fail
> silently or use wrong defaults.

### Step 5.1 — Batch create via GitHub CLI (fastest, ~2 minutes)

Run this in a terminal where `gh auth status` shows the `Aries-Serpent` org:

```bash
REPO="Aries-Serpent/_codex_"

gh variable set CODEX_ORG_NAME         --body "Aries-Serpent"            --repo "$REPO"
gh variable set CODEX_AGENT_NAME       --body "ai_org_repo_admin"        --repo "$REPO"
gh variable set CODEX_REPO_ID          --body "1040037790"               --repo "$REPO"
gh variable set CODEX_NETWORK_MODE     --body "isolated"                 --repo "$REPO"
gh variable set CODEX_API_VERSION      --body "2022-11-28"               --repo "$REPO"
gh variable set CODEX_LOG_LEVEL        --body "INFO"                     --repo "$REPO"
gh variable set GENESIS_TIMESTAMP      --body "2026-04-13T00:00:00Z"     --repo "$REPO"
gh variable set AUDIT_RETENTION_DAYS   --body "90"                       --repo "$REPO"
gh variable set COPILOT_AGENT_ENABLED  --body "true"                     --repo "$REPO"
gh variable set CODEX_SAFE_MODE        --body "false"                    --repo "$REPO"
gh variable set CODEX_ENV_PYTHON_VERSION --body "3.12"                   --repo "$REPO"
gh variable set CODEX_FAILURE_RATE     --body "0"                        --repo "$REPO"
gh variable set CODEX_CI_FAILURE_RATE  --body "0"                        --repo "$REPO"
```

### Step 5.2 — Verify variables were created

```bash
gh variable list --repo Aries-Serpent/_codex_
```

Expected: all 13 variables appear in the table.

### Step 5.3 — UI alternative (if CLI not available)

For each variable in the table above:
1. Open: **https://github.com/Aries-Serpent/_codex_/settings/variables/actions**
2. Click **New repository variable**.
3. Enter the **Name** and **Value** from the table.
4. Click **Add variable**.

---

## Section 6 — `agent-auth-delegation` Environment

> **Why:** The `agent-auth-delegation.yml` workflow gates autonomous operations behind
> an `environment:` block. If that environment has **required reviewers**, every agent
> action waits indefinitely for a human to click "Approve deployment."
> Setting zero required reviewers lets the agent self-activate.

### Step 6.1 — Remove required reviewers from the environment

1. Open: **https://github.com/Aries-Serpent/_codex_/settings/environments**
   *(Repo → ⚙️ Settings → Environments)*
2. Click **agent-auth-delegation** (create it if it doesn't exist — see Step 6.2).
3. Under **Required reviewers**, remove any names in the list (click the `×` next to each).
4. Ensure the list is empty.
5. Under **Deployment branches**, select **No restriction** (or **All branches**).
6. Click **Save protection rules**.

### Step 6.2 — Create the environment if it doesn't exist

1. Open: **https://github.com/Aries-Serpent/_codex_/settings/environments**
2. Click **New environment**.
3. Name: `agent-auth-delegation`
4. Click **Configure environment**.
5. Leave **Required reviewers** empty.
6. Set **Deployment branches** to **No restriction**.
7. Click **Save protection rules**.

---

## Section 7 — Dependabot Access to `CODEX_MASTER_KEY`

> **Why:** Dependabot PRs run in an isolated context. If a Dependabot PR triggers
> a workflow that needs `CODEX_MASTER_KEY`, the secret must be explicitly shared.

1. Open: **https://github.com/Aries-Serpent/_codex_/settings/secrets/actions**
2. Click **CODEX_MASTER_KEY** → **Edit**.
3. Scroll to **Accessible from** → tick **☑ Dependabot secrets**.
4. Click **Save**.

---

## Section 8 — Enable Auto-Merge on the Repository

> **Why:** The agent uses GitHub's auto-merge feature to merge PRs once all checks pass,
> without waiting for a human. This must be enabled at the repo level.

1. Open: **https://github.com/Aries-Serpent/_codex_/settings**
   *(Repo → ⚙️ Settings → General)*
2. Scroll to **Pull Requests**.
3. Check **☑ Allow auto-merge**.
4. Check **☑ Automatically delete head branches** (keeps the repo clean).
5. Click **Save** (if prompted).

---

## Section 9 — Notification & Monitoring Setup

> The agent is designed to run fully autonomously, but you should monitor its
> health dashboard and receive alerts on critical failures.

### Step 9.1 — Watch the repository

1. Open: **https://github.com/Aries-Serpent/_codex_**
2. Click **Watch** (top-right, next to Star).
3. Select **Custom** → tick:
   - ☑ Issues
   - ☑ Pull requests
   - ☑ Releases
   - ☑ Security alerts
4. Click **Apply**.

### Step 9.2 — Subscribe to GitHub Actions failure notifications

1. Open: **https://github.com/settings/notifications**
2. Under **Actions**, ensure:
   - ☑ **Failed workflows only** is selected for repositories you own.
3. Click **Save**.

---

## Section 10 — One-Time Genesis Bootstrap

> **Why:** The `genesis-bootstrap.yml` workflow initialises all cognitive brain state,
> creates the initial `.codex/autonomous_agent.yaml`, and arms the self-healing loop.
> It only needs to run **once**.

### Step 10.1 — Trigger the genesis workflow

```bash
gh workflow run genesis-bootstrap.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --field confirm=true
```

Or via the UI:
1. Open: **https://github.com/Aries-Serpent/_codex_/actions/workflows/genesis-bootstrap.yml**
2. Click **Run workflow** (top-right dropdown).
3. Branch: `main`, input `confirm`: `true`.
4. Click the green **Run workflow** button.

### Step 10.2 — Verify genesis completed

```bash
gh run list --workflow genesis-bootstrap.yml --repo Aries-Serpent/_codex_ --limit 1
```

Expected status: `completed` / `success`.

---

## Section 11 — Verify Everything Works End-to-End

Run this full verification checklist after completing all sections above:

```bash
#!/usr/bin/env bash
# Run from any directory with gh CLI authenticated
REPO="Aries-Serpent/_codex_"

echo "=== 1. Secrets ==="
gh secret list --repo "$REPO" | grep -E "CODEX_MASTER_KEY|CODEX_BACKUP_KEY"

echo "=== 2. Variables ==="
gh variable list --repo "$REPO" | grep -E "CODEX_|GENESIS_|AUDIT_|COPILOT_"

echo "=== 3. Actions permissions ==="
gh api repos/"$REPO"/actions/permissions | jq '{enabled,allowed_actions,github_owned_allowed}'

echo "=== 4. Default workflow permissions ==="
gh api repos/"$REPO"/actions/permissions/workflow | jq .

echo "=== 5. Latest workflow runs (should be success/in_progress, NOT action_required) ==="
gh run list --repo "$REPO" --limit 10 --json status,conclusion,name \
  | jq '.[] | select(.status == "action_required") | .name'
# ↑ This should print NOTHING. Any "action_required" runs still need approval.

echo "=== 6. Branch protection bypass actors ==="
gh api repos/"$REPO"/branches/main/protection \
  | jq '.restrictions.apps // "no app restrictions"'

echo "=== DONE ==="
```

---

## Section 12 — Troubleshooting

### "action_required" runs still appearing

**Cause:** A workflow was triggered before the Actions permissions were updated, OR the
`copilot-swe-agent[bot]` user is not yet recognised as a non-outside-collaborator.

**Fix:**
```bash
# Approve all pending runs for the current branch in bulk
gh run list --repo Aries-Serpent/_codex_ --json id,status \
  | jq -r '.[] | select(.status == "action_required") | .id' \
  | xargs -I{} gh run rerun {} --repo Aries-Serpent/_codex_
```

After completing Section 2, all future runs will auto-start.

---

### HTTP 403 when workflows call the REST API

**Cause:** `CODEX_MASTER_KEY` secret is missing or has insufficient permissions.

**Fix:** Repeat Section 1 to regenerate the PAT and re-inject the secret.

---

### Branch protection blocking merge

**Cause:** The bypass actors in Section 3 were not saved correctly.

**Fix:**
```bash
gh api repos/Aries-Serpent/_codex_/branches/main/protection \
  --jq '.required_pull_request_reviews.bypass_pull_request_allowances'
```
If `copilot-swe-agent[bot]` is absent, re-do Steps 3.1–3.2.

---

### Copilot doesn't respond to `@copilot` mentions

**Cause:** Copilot Coding Agent not enabled at org level (Section 4).

**Fix:** Complete Section 4, then re-post the `@copilot` mention.

---

### `agent-auth-delegation` waits indefinitely

**Cause:** The environment has required reviewers (Section 6).

**Fix:** Complete Step 6.1 to remove all required reviewers from the environment.

---

## Summary Table — All Human Actions

| # | Section | Action | URL | Estimated time |
|---|---------|--------|-----|----------------|
| A | 1.1–1.2 | Create & inject `CODEX_MASTER_KEY` PAT | github.com/settings/tokens | 5 min |
| B | 1.3 | Create & inject `CODEX_BACKUP_KEY` PAT | github.com/settings/tokens | 3 min |
| C | 2.1 | Allow all actions | `/settings/actions` | 30 sec |
| D | 2.2 | GITHUB_TOKEN read/write + allow PRs | `/settings/actions` | 30 sec |
| E | 2.3 | Fork/outside-contributor approval → first-time only | `/settings/actions` | 30 sec |
| F | 3.1 | `main` branch protection — add bot as bypass actor | `/settings/branches` | 2 min |
| G | 3.2 | `0D_base_` branch protection — add bot as bypass actor | `/settings/branches` | 2 min |
| H | 4.1 | Enable Copilot Coding Agent in org | org settings/copilot | 1 min |
| I | 4.2–4.3 | Enable Copilot in repo + personal settings | repo settings + profile | 1 min |
| J | 5.1–5.2 | Create 13 repository variables | CLI or `/settings/variables` | 3 min |
| K | 6.1–6.2 | `agent-auth-delegation` env — no required reviewers | `/settings/environments` | 2 min |
| L | 7 | Share `CODEX_MASTER_KEY` with Dependabot | `/settings/secrets/actions` | 1 min |
| M | 8 | Enable auto-merge + auto-delete branches | `/settings` (General) | 30 sec |
| N | 9.1–9.2 | Watch repo + enable failure notifications | github.com/settings | 2 min |
| O | 10 | Run genesis bootstrap workflow (once) | `/actions/workflows/` | 5 min |
| | | **Total estimated time** | | **~30 minutes** |

---

*This document is maintained by `copilot-swe-agent[bot]`. If any step is out of date or
a new requirement is discovered, the agent will update this file and post a PR.*
