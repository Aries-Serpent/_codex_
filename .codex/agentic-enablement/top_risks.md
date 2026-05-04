# Top Risks — Agentic Enablement Discovery
> Generated: 2026-05-04T16:44:03Z | Repo: Aries-Serpent/_codex_ | HEAD: d2f849550ea512c30c81de8f68a22e1ea52bbe61
> Phase 6 — Remediation Plan (FIX / MIGRATE / REMOVE)

---

## Risk 1 — `COPILOT_AGENT_AUTH_ENABLED=true` permanently bypasses ALL approval guards
**Severity:** CRITICAL | **Type:** FIX | **File:** `scripts/ci/owner_approval_guard.sh:138–175`

**Evidence:**
```bash
# owner_approval_guard.sh:144
if [ "${COPILOT_AGENT_AUTH_ENABLED:-}" = "true" ]; then
  # bypass ALL tool keys when COPILOT_AGENT_AUTH_BYPASS_TOOLS is unset/empty
```
`agent_context.json` confirms `COPILOT_AGENT_AUTH_ENABLED=true` is the active repo variable.
`COPILOT_AGENT_AUTH_BYPASS_TOOLS` is unset → **every workflow's approval guard is bypassed**.

**Remediation (FIX):**
1. Set `COPILOT_AGENT_AUTH_BYPASS_TOOLS` to an explicit allowlist (e.g., `"labeler,pr-checks"`) — never leave empty.
2. Add a mandatory expiry: bypass token should auto-expire (TTL enforced in guard script, currently honoured via `agent_auth_session.json`).
3. Require re-approval for `autonomous-agent.yml` and `docker-build-push` regardless of `COPILOT_AGENT_AUTH_ENABLED`.

---

## Risk 2 — `agent_auth_session.json` is git-tracked
**Severity:** CRITICAL | **Type:** FIX | **File:** `.codex/agent_auth_session.json`

**Evidence:** `git ls-files .codex/agent_auth_session.json` returns the file — it is committed to the repo.
Contents include `bypass_tools`, `expires_at`, `run_url`, `pr_number` — metadata for the active provenance-chain bypass.

**Remediation (FIX):**
1. Add `.codex/agent_auth_session.json` to `.gitignore` immediately.
2. Remove the file from git history (`git rm --cached .codex/agent_auth_session.json`).
3. Store session state only in ephemeral GitHub Actions artifacts or a repo variable — never in tracked files.

---

## Risk 3 — `autonomous-agent.yml` runs every 6 hours with write permissions, monitor mode requires no approval
**Severity:** CRITICAL | **Type:** FIX | **File:** `.github/workflows/autonomous-agent.yml:1–65`

**Evidence:**
```yaml
on:
  schedule:
    - cron: '0 */6 * * *'
permissions:
  contents: write
  pull-requests: write
  issues: write
jobs.autonomous-agent.if: needs.owner-guard.outputs.approved == 'true' || github.event.inputs.mode == 'monitor'
```
`monitor` mode executes **without** owner-guard approval.

**Remediation (FIX):**
1. Add `if: false` guard (or disable via workflow settings) until Genesis is formally complete.
2. Remove the `|| github.event.inputs.mode == 'monitor'` bypass — monitor mode must also pass the guard.
3. Downgrade permissions to `contents: read` for monitor mode; only escalate to write after explicit human approval per-run.

---

## Risk 4 — `labeler.yml` uses `pull_request_target` with CODEX_MASTER_KEY in rescue job
**Severity:** CRITICAL | **Type:** FIX | **File:** `.github/workflows/labeler.yml:3,41–48`

**Evidence:**
```yaml
on:
  pull_request_target:           # runs with write-token on fork PRs
    branches: ["0D_base_", "main"]
steps:
  - uses: actions/checkout@v5
    with:
      token: ${{ secrets.CODEX_MASTER_KEY || secrets.GITHUB_TOKEN }}
```
The rescue-comment job runs `actions/checkout@v5` with CODEX_MASTER_KEY on the PR head ref — exposing the PAT to checked-out fork code.

**Remediation (FIX):**
1. Change trigger to `pull_request` (drops write-token for forks).
2. If `pull_request_target` is required for labelling, gate the rescue-comment job: `if: github.event.pull_request.head.repo.fork == false`.
3. Add `persist-credentials: false` to all checkout steps (already added for other workflows in Wave 8).

---

## Risk 5 — Self-hosted runners hold CODEX_MASTER_KEY
**Severity:** CRITICAL | **Type:** MIGRATE | **Files:** `docker-build-push.yml:55,66,100,177` · `workflow-expiry-enforcer.yml:20,30`

**Evidence:**
```yaml
runs-on: [self-hosted, linux]
env:
  GITHUB_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}
```
Self-hosted runner has host network access. Any code that runs on it can access the injected token via `$GITHUB_TOKEN`.

**Remediation (MIGRATE):**
1. Move to `ubuntu-latest` (GitHub-hosted) where runners are ephemeral.
2. If self-hosted is required, isolate runners in a network-restricted environment with no external egress.
3. Replace CODEX_MASTER_KEY with a scoped OIDC token for the specific operation (GHCR push uses `id-token: write`).

---

## Risk 6 — `agent-orchestration-unified.yml` auto-triggers from health-check with write permissions
**Severity:** HIGH | **Type:** FIX | **File:** `.github/workflows/agent-orchestration-unified.yml:1–40`

**Evidence:**
```yaml
on:
  workflow_run:
    workflows: ["Workflow Health Check (Quantum-Inspired)", "Workflow Health Check"]
    types: [completed]
permissions:
  contents: write
  issues: write
  pull-requests: write
```
Every health-check completion automatically chains to agent orchestration — no human step in the chain.

**Remediation (FIX):**
1. Add an `environment: agent-operations` protection rule requiring human reviewer approval before jobs run.
2. Change trigger to `workflow_dispatch` only until proper canary/staging is established.
3. Downgrade to `contents: read` until orchestration needs to write.

---

## Risk 7 — ChatOps `/copilot` commands dispatched from issue comments with broad actor allowlist
**Severity:** HIGH | **Type:** FIX | **File:** `.github/workflows/chatops_copilot_trigger.yml:19,64,79`

**Evidence:**
```yaml
ALLOWED_ACTORS: ${{ vars.COGNITIVE_BRAIN_ALLOWED_ACTORS }}
# Value: "mbaetiong,github-actions[bot],copilot-swe-agent[bot],github-copilot[bot]"
```
`github-actions[bot]` is in the allowlist — meaning any workflow that posts a comment starting with `/copilot` can trigger arbitrary agent commands.

**Remediation (FIX):**
1. Remove `github-actions[bot]` from `COGNITIVE_BRAIN_ALLOWED_ACTORS` — only human actors should trigger chat-ops.
2. Add a secondary check: `github.event.comment.author_association` must be `OWNER` or `MEMBER`.
3. Log all dispatched commands to an immutable audit trail.

---

## Risk 8 — `agent_infrastructure_manager.yml` accepts `repository_dispatch` to write variables and configure webhooks
**Severity:** HIGH | **Type:** FIX | **File:** `.github/workflows/agent_infrastructure_manager.yml:37–48`

**Evidence:**
```yaml
repository_dispatch:
  types:
    - agent-infra-apply-vars
    - agent-infra-apply-webhooks
```
Any actor with `repo` scope PAT can send `repository_dispatch` and trigger variable writes or webhook configuration changes.

**Remediation (FIX):**
1. Add an `environment: infra-protected` gate with required reviewers.
2. Require the `client_payload` to include a signed nonce verified against a repo secret.
3. Log every dispatch event to `.codex/evidence/infra_dispatch.jsonl`.

---

## Risk 9 — `autonomous_actions_enabled: true` in `.codex/autonomous_agent.yaml`
**Severity:** HIGH | **Type:** FIX | **File:** `.codex/autonomous_agent.yaml:19`

**Evidence:**
```yaml
# HUMAN: Set to true only AFTER Genesis and secrets are verified
autonomous_actions_enabled: true   # ← already true
```
Comment explicitly says "only AFTER Genesis" — Genesis is not complete (guardrails.md status: "Template - Awaiting Human Review").

**Remediation (FIX):**
1. Set `autonomous_actions_enabled: false` until Genesis Protocol Phase 2 is formally signed off.
2. Add a CI check that fails if `autonomous_actions_enabled: true` and Genesis gate variable is not set.

---

## Risk 10 — Dynamic runner label via repo variable (`vars.RUNS_ON`)
**Severity:** HIGH | **Type:** FIX | **File:** `.github/workflows/runner-diagnostics.yml:15`

**Evidence:**
```yaml
runs-on: ${{ fromJSON(vars.RUNS_ON || '["self-hosted","linux"]') }}
```
An actor who can write repo variables (e.g., via `agent_infrastructure_manager.yml` dispatch) can redirect this job to any runner label — including a compromised one.

**Remediation (FIX):**
1. Hardcode the runner label or validate `vars.RUNS_ON` against an allowlist in a prior step.
2. Remove `fromJSON(vars.RUNS_ON)` pattern; only allow static runner labels in workflow YAML.

---

## Risk 11 — `AGENT_KILL_SWITCH` is only an env var — not durable
**Severity:** HIGH | **Type:** FIX | **File:** `scripts/agent_runner.py:35`

**Evidence:**
```python
_KILL_SWITCH = os.environ.get("AGENT_KILL_SWITCH", "0") == "1"
```
Emergency stop requires setting `AGENT_KILL_SWITCH=1` in the process environment. No GitHub variable, file-based flag, or workflow `if: false` guard serves as a durable kill-switch.

**Remediation (FIX):**
1. Add a check against a GitHub repo variable: `AGENT_EMERGENCY_STOP` — if `true`, all autonomy scripts exit immediately.
2. Create a dedicated `emergency-stop.yml` workflow that sets this variable and cancels in-progress runs.
3. Document the kill-switch procedure in `.codex/guardrails.md`.

---

## Risk 12 — 576 action invocations use mutable version tags (not SHA pins)
**Severity:** MEDIUM | **Type:** FIX | **File:** `.github/workflows/*.yml` (150 files)

**Evidence:**
```
rg 'uses: .+@v[0-9]' .github/workflows/*.yml → 576 matches
rg 'uses: .+@[a-f0-9]{40}' .github/workflows/*.yml → 1 match
```
A supply-chain attack against `actions/checkout`, `actions/cache`, or any other heavily-used action tag would affect all 150 workflows simultaneously.

**Remediation (FIX):**
1. Pin all `uses:` references to full 40-char SHA (e.g., `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683`).
2. Use Dependabot `updates: github-actions` to keep SHA pins current.
3. Prioritise pinning the 5 highest-frequency actions: `checkout`, `cache`, `setup-python`, `upload-artifact`, `download-artifact`.

---

## Risk 13 — 36 workflows have no `permissions:` block
**Severity:** MEDIUM | **Type:** FIX | **File:** `.github/workflows/*.yml` (36 files)

**Remediation (FIX):** Add `permissions: contents: read` as the default to every workflow missing a block. Escalate only where explicitly required.

---

## Risk 14 — `setup-secure-token` action uses base64-encoded token from env vars
**Severity:** MEDIUM | **Type:** MIGRATE | **File:** `.github/actions/setup-secure-token/action.yml:37–39`

**Remediation (MIGRATE):** Replace base64 token storage with GitHub Secrets + OIDC where possible. Remove `CODEX_GHP_TOKEN_BASE64` env var pattern entirely.

---

## Risk 15 — `agent_context.json` is git-tracked and contains `COPILOT_AGENT_AUTH_ENABLED=true`
**Severity:** MEDIUM | **Type:** FIX | **File:** `.codex/agent_context.json`

**Evidence:** `git ls-files .codex/agent_context.json` → tracked. Contains `COPILOT_AGENT_AUTH_ENABLED=true`, `COPILOT_AGENT_MAX_AUTONOMY_LEVEL=D`, `AUTO_PROMOTE_TIER_ENABLED=true`.

**Remediation (FIX):**
1. Add `.codex/agent_context.json` to `.gitignore` — this is a runtime snapshot, not source-of-truth config.
2. Remove from git history (`git rm --cached`).
3. Treat repo variables as the authoritative source; generate `agent_context.json` only at workflow runtime.

---

## Risk 16 — `CODEX_MASTER_KEY` PAT present in 113 of 150 workflow files — blast radius is total
**Severity:** HIGH | **Type:** MIGRATE

**Evidence:** `grep -rl "CODEX_MASTER_KEY" .github/workflows/*.yml | wc -l → 113`

**Remediation (MIGRATE):**
1. Audit each use of `CODEX_MASTER_KEY` — replace with scoped `GITHUB_TOKEN` wherever possible.
2. For operations requiring `contents:write`, use a fine-grained PAT scoped to the exact repository and permission.
3. Adopt OIDC (`id-token: write`) for cloud/registry operations — currently only 6 workflows use OIDC.

---

## Risk 17 — `OWNER_APPROVAL.yml` approval window from 2025-10-20 is expired but `enabled: true`
**Severity:** MEDIUM | **Type:** FIX | **File:** `.github/OWNER_APPROVAL.yml`

**Evidence:**
```yaml
enabled: true
duration: "24h"
created_at: "2025-10-20T19:43:52Z"   # ← 6+ months ago
```
The file-based approval window is stale. The guard script falls through to the `COPILOT_AGENT_AUTH_ENABLED` bypass anyway, but a stale `enabled: true` with expired timestamp is misleading.

**Remediation (FIX):** Set `enabled: false` and add a `last_reviewed:` field. Rely on repo variables for dynamic approval windows, not committed YAML.

---

## Risk 18 — `chatops_copilot_trigger.yml` allows `github-actions[bot]` to dispatch agent commands
**Severity:** HIGH | **Type:** FIX | **File:** `.github/workflows/chatops_copilot_trigger.yml:64`

See Risk 7 above — extracted as a distinct entry because `github-actions[bot]` in the allowlist creates a self-reinforcing loop: a workflow can comment `/copilot continue` → chatops fires → Copilot agent runs → posts comment → chatops fires again.

**Remediation (FIX):** Remove `github-actions[bot]` from `COGNITIVE_BRAIN_ALLOWED_ACTORS` immediately.

---

## Risk 19 — `bootstrap_self_hosted_runner.py` automates runner registration with GitHub App JWT
**Severity:** MEDIUM | **Type:** MIGRATE | **File:** `scripts/ops/bootstrap_self_hosted_runner.py:66–148`

**Remediation (MIGRATE):** Runner registration should require a human-initiated workflow dispatch with environment protection, not an automated script callable from CI.

---

## Risk 20 — `autonomy-phase-ci-matrix.yml` runs and validates all 7 autonomy phases on every PR
**Severity:** REVIEW | **Type:** FIX | **File:** `.github/workflows/autonomy-phase-ci-matrix.yml`

**Remediation (FIX):** Add `permissions: contents: read` (already present ✅). Ensure the autonomy scripts run in `--dry-run` mode during CI. Add an explicit assertion that `AUTONOMY_DRY_RUN=1` is set.

---

## Summary Counts

| Severity | Count | Remediation |
|---|---:|---|
| Critical | 5 | FIX: 4, MIGRATE: 1 |
| High | 7 | FIX: 6, MIGRATE: 1 |
| Medium | 6 | FIX: 4, MIGRATE: 2 |
| Review | 2 | FIX: 2 |
| **Total** | **20** | **FIX: 16, MIGRATE: 4, REMOVE: 0** |
