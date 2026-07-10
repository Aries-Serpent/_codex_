# GitHub Actions Workflow Best Practices
# Codex Repository — Authoritative Reference

> **Generated:** 2026-03-01 | Deep research synthesis (3 search passes)
> **Scope:** Concurrency, timeouts, GitHub Copilot Coding Agent workflow abilities,
>            repo variables, advanced patterns, agent empowerment
> **Status:** ✅ All 89 workflows in this repo now comply with every rule below.

---

## Table of Contents

1. [Concurrency — The Non-Negotiable Rule](#1-concurrency--the-non-negotiable-rule)
2. [Timeouts — Never Let a Job Hang](#2-timeouts--never-let-a-job-hang)
3. [Deployment Workflows — Special Case](#3-deployment-workflows--special-case)
4. [Advanced Variable Techniques](#4-advanced-variable-techniques)
5. [GitHub Copilot Coding Agent — What It Can and Cannot Do](#5-github-copilot-coding-agent--what-it-can-and-cannot-do)
6. [Empowering the Copilot Agent via Workflows](#6-empowering-the-copilot-agent-via-workflows)
7. [Advanced Workflow Patterns](#7-advanced-workflow-patterns)
8. [This Repo's Enforcement Inventory](#8-this-repos-enforcement-inventory)

---

## 1. Concurrency — The Non-Negotiable Rule

### The Rule
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```

### Why `head_ref || ref`?
| Context | `github.head_ref` | `github.ref` | Effective group |
|---------|-------------------|--------------|-----------------|
| Open PR | `feature/my-branch` | `refs/pull/N/merge` | `workflow-feature/my-branch` |
| Push to main after merge | _(empty)_ | `refs/heads/main` | `workflow-refs/heads/main` |
| Scheduled cron | _(empty)_ | `refs/heads/main` | `workflow-refs/heads/main` |
| Different PR branch | `feature/other` | `refs/pull/M/merge` | `workflow-feature/other` |

**Result:**
- ✅ Same workflow + same branch → cancel older run, keep newest
- ✅ Same workflow + different branches → separate groups, run in parallel
- ✅ Branch merged → workflow restarts on main → deduplicated among post-merge runs
- ✅ Scheduled/cron → single global instance on main

### Special Trigger Overrides

| Trigger | Recommended group |
|---------|-------------------|
| `issue_comment` | `${{ github.workflow }}-${{ github.event.issue.number }}` |
| `workflow_run` | `${{ github.workflow }}-${{ github.event.workflow_run.head_branch }}` |
| `pull_request_target` | `${{ github.workflow }}-${{ github.base_ref }}-${{ github.event.pull_request.head.ref }}` |

### Pitfalls
- **Reusable workflow callee:** Set concurrency at the **caller** side, not inside the callee — the callee inherits the caller's concurrency context.
- **Wildcard `workflow_run: ["*"]`:** Creates exponential cascade — two such workflows trigger each other → thousands of queued runs. This repo fixed this (commit `86e1fb3`). Always add a self-exclusion `if:` filter.
- **Typos in group names:** Break deduplication silently. Use `${{ github.workflow }}` (auto-derives from the `name:` field) rather than hard-coding the name string.

---

## 2. Timeouts — Never Let a Job Hang

GitHub's default job timeout is **360 minutes (6 hours)**. This is almost always wrong — it wastes runner minutes and hides hung processes.

### Recommended Defaults by Category

| Category | `timeout-minutes` | Examples |
|----------|-------------------|---------|
| Quick / utility | **10** | labeler, watchdog, link-check, flush, cleanup |
| Standard CI | **30** | tests, analysis, preflight, auth checks |
| Coverage / quality | **45** | coverage collection, code quality suites |
| Heavy build / ML | **60** | Rust, Docker builds, OpenVINO, PyTorch |

### Step-level Timeouts for Network Steps
```yaml
- name: Call external API
  timeout-minutes: 2
  run: curl --max-time 90 https://api.example.com/data
```

### Tooling
- [`ghalint`](https://github.com/suzuki-shunsuke/ghalint) — linter that enforces `timeout-minutes` presence
- [`ghatm`](https://github.com/suzuki-shunsuke/ghatm) — CLI to bulk-add `timeout-minutes` to all jobs

---

## 3. Deployment Workflows — Special Case

For workflows that deploy to production (PyPI, Docker, release publishing):

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: false  # deployment: never cancel in-progress — leaves prod in unknown state
```

**Why `false`:** Cancelling a mid-flight deployment can leave production in a partially-updated,
unknown state. Queue deployments — don't cancel them.

**Workflows in this repo using `cancel-in-progress: false`:**
- `pypi-publish.yml`
- `docker-build-push.yml`
- `publish_dashboard_release.yml`
- `unified-deployment.yml`

---

## 4. Advanced Variable Techniques

### 4a. `vars` Context — Repository Configuration Variables
Non-sensitive configuration (flags, URLs, env names) should live as **repo variables**, not secrets:

```yaml
steps:
  - name: Use repo variable
    run: echo "Environment: ${{ vars.DEPLOY_ENV }}"
```

Set via: **Settings → Secrets and variables → Actions → Variables tab**

Scopes: `repository`, `environment`, `organization` (narrowest scope wins).

### 4b. Dynamic `GITHUB_ENV` — Cross-Step Variables
```yaml
- name: Compute version
  run: echo "VERSION=$(git describe --tags)" >> "$GITHUB_ENV"

- name: Use it in next step
  run: echo "Building version $VERSION"
```

### 4c. Cross-Job Outputs
```yaml
jobs:
  compute:
    outputs:
      sha: ${{ steps.get_sha.outputs.sha }}
    steps:
      - id: get_sha
        run: echo "sha=$(git rev-parse --short HEAD)" >> "$GITHUB_OUTPUT"

  deploy:
    needs: compute
    steps:
      - run: echo "Deploying ${{ needs.compute.outputs.sha }}"
```

### 4d. Dynamic `workflow_dispatch` Choices (Self-Updating)
Static `type: choice` options go stale. Pattern to auto-update them:
```yaml
# A scheduled workflow fetches current tags and patches the YAML file,
# committing updated choices — so manual dispatch always shows latest options.
```

### 4e. JSON Blob for Dynamic Parameter Count (Reusable Workflows)
When the number of parameters is unknown at authoring time:
```yaml
# Caller
with:
  config: '{"APP_ENV": "prod", "LOG_LEVEL": "warn", "REPLICA_COUNT": "3"}'

# Callee
- run: |
    echo '${{ inputs.config }}' | jq -r 'to_entries[] | "\(.key)=\(.value)"' >> "$GITHUB_ENV"
```

### 4f. Writing Repo Variables from a Workflow (Agent Token Delegation Pattern)
```yaml
- uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.CODEX_MASTER_KEY }}
    script: |
      // Upsert a repo variable (PATCH if exists, POST if 404)
      async function upsertVar(name, value) {
        try {
          await github.request('PATCH /repos/{owner}/{repo}/actions/variables/{name}',
            { owner: context.repo.owner, repo: context.repo.repo, name, value });
        } catch (e) {
          if (e.status === 404)
            await github.request('POST /repos/{owner}/{repo}/actions/variables',
              { owner: context.repo.owner, repo: context.repo.repo, name, value });
          else throw e;
        }
      }
      await upsertVar('COPILOT_AGENT_AUTH_ENABLED', 'true');
```
> **Note:** `GITHUB_TOKEN` cannot write variables — requires a PAT with `repo` scope
> (`CODEX_MASTER_KEY` in this repo).

---

## 5. GitHub Copilot Coding Agent — What It Can and Cannot Do

### Workflow Abilities (2025)

| Capability | ✅ Can | ❌ Cannot |
|------------|--------|----------|
| **Environment** | Runs in ephemeral Actions VM (destroyed post-session) | Persist state across sessions without committing |
| **Code** | Read entire codebase; write to `copilot/` branches | Push directly to protected branches (`main`) |
| **PRs** | Open draft PRs; iterate on feedback | Merge its own PRs (human review required) |
| **Secrets** | Use secrets exposed in `copilot-setup-steps.yml` | Access `GITHUB_TOKEN` or secrets in its own runtime |
| **Repo vars** | Read `${{ vars.* }}` in setup steps | Write repo variables directly (needs PAT via wrapper workflow) |
| **Network** | Pre-allow-listed endpoints | Arbitrary internet egress (firewall blocks by default) |
| **Triggers** | Triggered by issue assignment, chat, CLI, scheduled workflow | Self-trigger or re-dispatch autonomously without a human |
| **MCP** | Use configured MCP servers for extended tool access | Use unconfigured external APIs |
| **Audit** | All actions logged in session logs and PR history | Hide actions from audit trail |

### Security Boundaries (By Design)
- **Sandbox isolation:** Each session runs in a fresh container, destroyed after the task.
- **No self-merge:** Branch protections and required reviews are always enforced.
- **Firewall:** Outbound network requests are restricted to an allow-list defined in `copilot-setup-steps.yml`. Unauthorized external calls are blocked.
- **Token scope:** The agent uses a scoped session token — not the owner's PAT. It cannot escalate its own permissions.
- **CodeQL + secret scan:** Every agent PR is automatically scanned before any CI runs.

### Copilot Token Precedence
```
COPILOT_GITHUB_TOKEN  →  GH_TOKEN  →  GITHUB_TOKEN (read-only in agent context)
```

---

## 6. Empowering the Copilot Agent via Workflows

### Pattern A — `copilot-setup-steps.yml` (Environment Customization)
The **only** officially supported way to customize the agent's execution environment:
```yaml
# .github/workflows/copilot-setup-steps.yml
name: "Copilot Setup Steps"
on:
  workflow_dispatch:
  push:
    paths: [.github/workflows/copilot-setup-steps.yml]
  pull_request:
    paths: [.github/workflows/copilot-setup-steps.yml]

jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip
      - run: pip install -e ".[dev]"
      # Install tools the agent needs (git, gh CLI, safe_git_show, etc.)
      - run: install -m 0755 scripts/ci/safe_git_show.sh /usr/local/bin/safe_git_show
```

### Pattern B — `agent-auth-delegation.yml` (Grounded Token Delegation)
Elevate agent permissions via owner-approved environment gate:
1. PR body checkbox → `cognitive-preflight` gates pass → owner approves in GH UI
2. Workflow writes `COPILOT_AGENT_AUTH_ENABLED=true` and session token `.codex/agent_auth_session.json` (4h TTL)
3. Posts `@copilot continue` to resume the agent session with elevated context

### Pattern C — `session-watchdog.yml` (Behavioral Enforcement via Workflow)
Detects timebox and exploration directives from PR comments, posts structured markers:
- `SESSION_TIMEBOX_START` + `EXPIRES_AT` timestamp
- `SESSION_TYPE_EXPLORATION` (triggers Session Continuity Policy enforcement)
- `SESSION_TIMEBOX_EXPIRED` → blocks `/copilot continue` until Session Summary posted

### Pattern D — `session-incremental-summary-reminder.yml` (Cron-Based Agent Prompting)
```yaml
on:
  schedule:
    - cron: '*/5 * * * *'   # Every 5 minutes
```
Scans open PRs for active exploration sessions. If last agent comment was >10 min ago,
posts `INCREMENTAL_SUMMARY_REMINDER` directly into the PR conversation — visible as
present-tense instruction, not background memory.

### Pattern E — `cognitive_brain_ci_feedback.yml` (CI Outcome → Agent Learning)
Triggered on `workflow_run: completed`. Maps workflow names to pattern IDs via keyword
map, calls `brain.report_completion()` for each match — closes the PDA feedback loop.

### Pattern F — Scheduled Agent Dispatch via Copilot CLI
```yaml
# Trigger the Copilot coding agent on a schedule via CLI
on:
  schedule:
    - cron: '0 2 * * 1'   # Weekly Monday 2am
jobs:
  dispatch-agent:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: |
          gh copilot suggest --issue <issue_number> --repo $GITHUB_REPOSITORY
        env:
          GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY }}
```

---

## 7. Advanced Workflow Patterns

### Pattern: Path Filters (Run Only When Relevant)
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'
    paths-ignore:
      - 'docs/**'
      - '**.md'
```

### Pattern: `[skip ci]` Commit Message Support
```yaml
jobs:
  build:
    if: "!contains(github.event.head_commit.message, '[skip ci]')"
```

### Pattern: Matrix with `fail-fast: false`
```yaml
strategy:
  fail-fast: false    # All matrix combinations run even if one fails
  max-parallel: 4
  matrix:
    python: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest]
```

### Pattern: Reusable Workflow (`workflow_call`)
```yaml
# Callee: .github/workflows/run-tests.yml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        required: true
    secrets:
      CODECOV_TOKEN:
        required: false

# Caller
jobs:
  tests:
    uses: ./.github/workflows/run-tests.yml
    with:
      python-version: '3.12'
    secrets: inherit
```

### Pattern: Composite Action (Step-Level Reuse)
```yaml
# .github/actions/setup-python-cached/action.yml
name: Setup Python (cached)
inputs:
  python-version:
    required: true
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
    - run: pip install -e ".[dev]"
      shell: bash
```

### Pattern: Merge Queue Integration
```yaml
on:
  merge_group:      # Fires when PR enters the merge queue
    types: [checks_requested]
```

### Pattern: OIDC Token for Cloud Auth (No Long-Lived Secrets)
```yaml
permissions:
  id-token: write   # Required for OIDC
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/GitHubActions
      aws-region: us-east-1
```

### Pattern: Self-Exclusion Filter (Cascade Prevention)
```yaml
# workflow_run workflows MUST exclude themselves to prevent infinite cascades
jobs:
  my-job:
    if: |
      github.event.workflow_run.name != 'My Workflow Name' &&
      github.event.workflow_run.name != 'Other Cascade Trigger'
```

### Pattern: Grounded Base-Ref Fetch (Cross-Branch Diff)
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0

- name: Fetch base branch for diff
  run: git fetch origin "${{ github.base_ref }}" --depth=1

- name: Diff against base
  run: git diff "origin/${{ github.base_ref }}...HEAD" -- src/
```

---

## 8. This Repo's Enforcement Inventory

| Rule | Mechanism | Coverage |
|------|-----------|----------|
| Branch-scoped concurrency | `${{ github.workflow }}-${{ github.head_ref \|\| github.ref }}` | 89/89 workflows |
| `cancel-in-progress: true` (CI) | All non-deployment workflows | 85/89 workflows |
| `cancel-in-progress: false` (Deploy) | `pypi-publish`, `docker-build-push`, `publish_dashboard_release`, `unified-deployment` | 4/4 deployment workflows |
| `timeout-minutes` on all jobs | Defaults: 10/30/45/60 by category | 89/89 workflows |
| Cascade prevention (workflow_run) | Self-exclusion `if:` + concurrency | `cognitive_brain_ci_feedback.yml`, `workflow-analytics-unified.yml` |
| Agent behavioral enforcement | GROUNDED Tier-1/2 gates | `agent-auth-delegation.yml` REQ-1 through REQ-7 |
| Session reminders | Cron-based cue injection | `session-incremental-summary-reminder.yml` |
| CI health monitoring | 16-pattern telemetry + issue alert | `ci-health-monitor.yml` |

---

## Sources

- [GitHub Docs — Control workflow concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- [GitHub Docs — Store information in variables](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables)
- [GitHub Docs — Customize Copilot agent environment](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)
- [GitHub Docs — Extend coding agent with MCP](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/extend-coding-agent-with-mcp)
- [Blacksmith — Protect prod, cut costs: concurrency in GitHub Actions](https://www.blacksmith.sh/blog/protect-prod-cut-costs-concurrency-in-github-actions)
- [Agentic DevOps — Getting the most out of GitHub Copilot's Coding Agent](https://azurewithaj.com/agentic-devops-github-copilot-coding-agent/)
- [Agentic DevOps Safe Mode — Arinco](https://arinco.com.au/blog/agentic-devops-safe-mode-a-practical-framework-for-secure-github-copilot-agents/)
- [Schedule GitHub Coding Agents — luke.geek.nz](https://luke.geek.nz/azure/schedule-github-coding-agents/)
- [Securing GitHub Copilot in Actions with Harden-Runner](https://www.stepsecurity.io/blog/securing-github-copilot-in-github-actions-with-harden-runner)
- [Dev.to — Set GitHub Actions timeout-minutes](https://dev.to/suzukishunsuke/set-github-actions-timeout-minutes-1jkk)
- [Exercism — GitHub Actions Best Practices](https://exercism.org/docs/building/github/gha-best-practices)

*Updated: 2026-03-01 | Applies to all 89 workflows in `.github/workflows/`*

---

## 9. CODEX_BACKUP_KEY Rotation Procedure (Sprint 5)

> **Status:** ✅ COMPLETE — token-probe S117 confirms 100%/100% (2026-03-01)

### When to Rotate

Rotate `CODEX_BACKUP_KEY` when:
- `ci-health-monitor.yml` backup key health check returns non-200
- `token-probe.yml` shows backup key at < 100% coverage
- A Personal Access Token (PAT) expiry warning appears in GitHub settings

### Rotation Steps

1. **Generate new PAT** (repo owner: @mbaetiong):
   ```
   GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
   Permissions: Actions (read/write), Contents (write), Issues (write), Pull requests (write)
   Expiry: 90 days (recommended)
   ```

2. **Update repository secret**:
   ```
   Repository → Settings → Secrets and variables → Actions → Secrets
   Update CODEX_BACKUP_KEY with new token value
   ```

3. **Verify with token-probe**:
   ```
   Actions → Token Probe → Run workflow → enter PR number
   Expected: CODEX_BACKUP_KEY Read: HTTP 200, Write: HTTP 201
   ```

4. **Confirm in ci-health-monitor**:
   The `🔑 Sprint 5: Backup key health check` step will show:
   ```
   ✅ CODEX_BACKUP_KEY healthy (HTTP 200)
   ```

5. **Update .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md** with rotation date and W-number.

### Enforcement
- `ci-health-monitor.yml` checks backup key health on every run (every 6 hours)
- `token-probe.yml` provides on-demand detailed coverage report
- `agent-auth-delegation.yml` REQ-7 gates require both keys active

*Updated: 2026-03-01 | Applies to: `.github/workflows/ci-health-monitor.yml`, `token-probe.yml`*
