# Workflow Portfolio Analysis (7-Day Window)

Generated at: 2026-05-16T04:13:40.786806+00:00  
Repository: `Aries-Serpent/_codex_`

## Dataset Artifacts

- `docs/reporting/workflow_portfolio_7d_table.csv`
- `docs/reporting/workflow_portfolio_7d_table.md`
- `docs/reporting/copilot_agent_session_standard_operation.md` (standard Copilot session lifecycle, required living docs, and streamlining planset)

## Executive Snapshot

- Total workflows discovered: **180**
- Workflows active in last 7 days: **82**
- Workflows not utilized in 7 days (including disabled): **100**
- Workflows with rate-limit controls/signals: **155**
- Workflows with variable mappings detected: **144**
- Branch-update conflict risk counts: **high=10**, **medium=38**
- Aggregate run conclusions (7 days): success=361, failure=50, action_required=78

## Mermaid Mapping — Workflow + Variable + Conflict Logic

```mermaid
flowchart TD
  A[Trigger Event] --> B[Workflow Entry]
  B --> C{Guardrails}
  C --> C1[permissions]
  C --> C2[concurrency/rate-limit]
  C --> C3[timeout-minutes]
  C --> D[Execution + Artifacts]
  D --> E{Dependency Paths}
  E --> E1[workflow_call]
  E --> E2[workflow_run]
  E --> E3[direct jobs]
  E1 --> F[Session Context Outputs]
  E2 --> F
  E3 --> F
```

```mermaid
flowchart LR
  M[main branch update] --> G[PR branch behind]
  G --> H{Write-capable workflows?}
  H -->|yes| I[Conflict risk rises
merge/rebase/write races]
  H -->|no| J[Low conflict risk]
  I --> K[Mitigation vars
CODEX_SWEEP_SKIP_MAIN
CODEX_MAX_HEALER_RUNS_PER_HOUR
CODEX_HEALER_SKIP_SKIPCI]
```

## Tokenized Variable Mapping (Top Frequency)

| Token | Referencing workflows |
|---|---:|
| `TSEC_CODEX_MASTER_KEY` | 119 |
| `TSEC_CODEX_BACKUP_KEY` | 114 |
| `TSEC_GITHUB_TOKEN` | 93 |
| `TVAR_CODEX_CACHE_VERSION` | 29 |
| `TENV_PYTHON_VERSION` | 8 |
| `TVAR_COPILOT_AGENT_AUTH_ENABLED` | 7 |
| `TVAR_COGNITIVE_BRAIN_SESSION_NUMBER` | 6 |
| `TENV_PR_NUMBER` | 5 |
| `TVAR_COGNITIVE_BRAIN_ALLOWED_ACTORS` | 4 |
| `TENV_DRY_RUN` | 4 |
| `TSEC_CODECOV_TOKEN` | 3 |
| `TVAR_CODEX_CI_LAST_GREEN_SHA` | 3 |
| `TVAR_CODEX_HEALER_SKIP_SKIPCI` | 3 |
| `TVAR_CODEX_MAX_HEALER_RUNS_PER_HOUR` | 3 |
| `TVAR_CODEX_SWEEP_SKIP_MAIN` | 3 |
| `TVAR_AUTONOMOUS_ACTIONS_ENABLED` | 2 |
| `TVAR_COGNITIVE_BRAIN_INJECTION_ENABLED` | 2 |
| `TVAR_AGENT_HANDOFF_TIMEOUT_SECONDS` | 2 |
| `TVAR_EMBEDDING_INDEX_AUTO_REBUILD` | 2 |
| `TVAR_CODEX_CI_FAILURE_THRESHOLD` | 2 |
| `TENV_REF` | 2 |
| `TENV_SHA` | 2 |
| `TVAR_CODEX_CI_FAILURE_RATE` | 2 |
| `TVAR_CODEX_COVERAGE_THRESHOLD` | 2 |
| `TVAR_COPILOT_AGENT_STATE` | 2 |

## Quantum-Inspired Equations Depicting Workflow Logic (Tokenized)

\[
\left|\Psi_{workflow}\right\rangle =
\sum_{i=1}^{N} \alpha_i \left|w_i\right\rangle
+ \beta_1 \cdot TVAR\_COPILOT\_AGENT\_AUTH\_ENABLED
+ \beta_2 \cdot TVAR\_COGNITIVE\_BRAIN\_SESSION\_NUMBER
\]

\[
U_i = \lambda_1 A_i + \lambda_2 D_i + \lambda_3 V_i - \lambda_4 R_i
+ \lambda_5 \cdot \mathbb{I}(TVAR\_CODEX\_SWEEP\_SKIP\_MAIN=1)
\]

\[
Q_i = \mu_1(1-A_i) + \mu_2R_i + \mu_3C_i + \mu_4B_i
+ \mu_5 \cdot TVAR\_CODEX\_CI\_FAILURE\_RATE
+ \mu_6 \cdot \mathbb{I}(TVAR\_CODEX\_HEALER\_SKIP\_SKIPCI=0)
\]

Where:
- \(A_i\): 7-day activity utility
- \(D_i\): dependency centrality
- \(V_i\): variable observability/tokenization quality
- \(R_i\): missing guardrail risk
- \(C_i\): Copilot cloud/coding-session relevance
- \(B_i\): branch-update conflict exposure
- `TVAR_CODEX_SWEEP_SKIP_MAIN`: branch-drift safety gate
- `TVAR_CODEX_CI_FAILURE_RATE`: live instability pressure signal
- `TVAR_CODEX_HEALER_SKIP_SKIPCI`: skip-ci bypass risk control

## Copilot Session Intended Process (Codeless, Workflow-Centric)

```mermaid
flowchart LR
  S0[Copilot session starts] --> S1[Read startup packet + conflict dashboard]
  S1 --> S2{drift severity}
  S2 -->|LOW| S3[Run planned workflow path]
  S2 -->|MED/HIGH| S4[Set TVAR_CODEX_SWEEP_SKIP_MAIN + healer bounds]
  S4 --> S5[Rebase gate]
  S5 --> S3
  S3 --> S6[Validation + checks]
  S6 --> S7[Living-doc updates]
  S7 --> S8[Session handoff]
```

## Requested Findings Summary

### What works

- Strong automation breadth and policy controls across core workflows.
- High adoption of guardrails (permissions/concurrency/timeout) in many active paths.
- Variable ecosystem (`CODEX_*`, `COPILOT_*`, `COGNITIVE_BRAIN_*`) is present and exploitable for session optimization.

### What does not work

- Workflow sprawl and mixed orchestration modes increase debugging overhead.
- Some high-value active workflows are under-utilized in the recent 7-day window.
- Branch-update conflict exposure remains in write-capable, event-driven workflows.

### What is missing

- Canonical owner/criticality metadata contract per workflow.
- Unified variable token registry and enforcement policy.
- Automated conflict-risk scoring artifact in CI outputs.

### What needs to be improved

1. Standardize tokenized variable contracts in all Copilot/agent workflows.
2. Apply branch-scoped concurrency + timeout parity to lagging workflows.
3. Harden write-capable automation against main-branch drift.
4. Consolidate overlapping pipelines to reduce fanout complexity.
5. Publish conflict-risk and quick-win rankings as default Copilot session context.

## 🚨 Branch-Update Conflict Dashboard

> **Priority section — read before editing any file during an active session.**
> When `main` receives commits while your branch session is active, the workflows below
> can race, produce stale-head writes, or cascade into each other via `workflow_run`.
> **Total conflict-risk workflows: HIGH=10, MEDIUM=38.**
>
> Cross-reference: [.codex/plans/LEAN_WORKFLOW_OS_PLANSET.md → Plan C](../../.codex/plans/LEAN_WORKFLOW_OS_PLANSET.md)

### Active Session Conflict Protocol

```
Detect drift (git log main..HEAD --oneline | wc -l):
  0 commits → LOW   → proceed normally
  1–3       → MEDIUM → add drift note to handoff; set CODEX_SWEEP_SKIP_MAIN=true if writing
  4+        → HIGH   → rebase first; run steps below before ANY write operation
  force-push→ CRITICAL → abort session; fetch main; restart from baseline
```

```mermaid
flowchart TD
  START([Active Copilot Session]) --> DETECT{Detect branch drift\ngit log main..HEAD}
  DETECT -->|0 commits| LOW[LOW: Proceed normally]
  DETECT -->|1-3 commits| MEDIUM[MEDIUM: Note drift in handoff]
  DETECT -->|4+ commits| HIGH[HIGH: Rebase before any write]
  DETECT -->|force-push detected| CRIT[CRITICAL: Abort + Restart]

  MEDIUM --> MITM[Set CODEX_SWEEP_SKIP_MAIN=true\nfor all write-capable workflows]
  HIGH --> MITH[1 Rebase branch on main\n2 Re-run setup probe\n3 Set all three mitigation vars]
  CRIT --> MITC[Fetch latest main\nRe-run session bootstrap\nRe-validate required checks]

  MITM --> WRITE[Safe to edit files]
  MITH --> WRITE
  LOW --> WRITE
  WRITE --> DONE([Continue session])
```

### Mitigation Variables — Quick Reference

| Variable | Purpose | Set when |
|---|---|---|
| `CODEX_SWEEP_SKIP_MAIN` | Stops write-capable sweeps from touching main during drift | Drift ≥ MEDIUM |
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | Caps self-healer firing rate to prevent cascades | Any active session with high run volume |
| `CODEX_HEALER_SKIP_SKIPCI` | Prevents healer from ignoring `[skip ci]` tags | Drift ≥ MEDIUM to avoid feedback loops |

### HIGH-Risk Workflows — Mandatory Mitigation

> These workflows **write to the repo or dispatch other workflows** and will race with branch
> drift if not guarded. Apply all three mitigation variables before running these during an
> active session.

---

#### 🔴 `iterative-self-healing-ci.yml` — Iterative Self-Healing CI
- **Runs (7d):** 413 &nbsp;|&nbsp; **Risk:** HIGH
- **Why it conflicts:** Write-capable + event-driven; fires on every push and can race with
  main-branch updates during active sessions, producing concurrent writes to the same files.
- **Mitigation steps:**
  1. Set repo variable `CODEX_SWEEP_SKIP_MAIN=true` before running or triggering this workflow.
  2. Set `CODEX_MAX_HEALER_RUNS_PER_HOUR` to `3` or lower to cap cascade rate.
  3. Set `CODEX_HEALER_SKIP_SKIPCI=true` to prevent skip-ci bypass during drift.
  4. Rebase your branch on latest `main` before committing any healer-initiated changes.
  5. After rebase, re-run the session access probe to confirm drift is cleared.
- **Required workflow controls:**
  ```yaml
  concurrency:
    group: "${{ github.workflow }}-${{ github.head_ref }}"
    cancel-in-progress: true
  timeout-minutes: 30
  ```

---

#### 🔴 `copilot-evolution-suite.yml` — Copilot Evolution & Review (Unified)
- **Runs (7d):** 10 &nbsp;|&nbsp; **Risk:** HIGH
- **Why it conflicts:** Dispatches review + write operations; if `main` moved since checkout,
  the "evolution" diff will target a stale base and can produce incorrect PR edits.
- **Mitigation steps:**
  1. Confirm `main` HEAD SHA matches your branch's merge-base before triggering.
  2. Set `CODEX_SWEEP_SKIP_MAIN=true`.
  3. Do not trigger manually during HIGH drift; wait for rebase to complete.
  4. After rebase, confirm no open review comments from a prior run target stale lines.
- **Required workflow controls:**
  ```yaml
  concurrency:
    group: "${{ github.workflow }}-${{ github.head_ref }}"
    cancel-in-progress: true
  timeout-minutes: 45
  ```

---

#### 🔴 `copilot-agent-session-done.yml` — Auto-Post @copilot Review After Agent Session
- **Runs (7d):** 10 &nbsp;|&nbsp; **Risk:** HIGH
- **Why it conflicts:** Fires on `workflow_run` completion; if the triggering run targeted a
  stale SHA, the auto-post will reference an outdated diff and can confuse subsequent sessions.
- **Mitigation steps:**
  1. Verify the triggering workflow ran against your current branch HEAD (not a prior SHA).
  2. Set `CODEX_SWEEP_SKIP_MAIN=true` when drift is detected.
  3. If auto-post fires against a stale SHA, manually close the generated comment and re-trigger
     after rebase.
- **Required workflow controls:**
  ```yaml
  concurrency:
    group: "${{ github.workflow }}-${{ github.head_ref }}"
    cancel-in-progress: false  # allow completion but gate new runs
  timeout-minutes: 15
  ```

---

#### 🔴 `agent-var-writer.yml` — Agent Variable Writer (Provenance-Chain)
- **Runs (7d):** 5 &nbsp;|&nbsp; **Risk:** HIGH
- **Why it conflicts:** Writes directly to GitHub Repo Variables using `CODEX_MASTER_KEY`;
  concurrent writes during drift can overwrite a value set by a prior healer run.
- **Mitigation steps:**
  1. Never trigger in parallel with `iterative-self-healing-ci.yml` on the same branch.
  2. Confirm `CODEX_CI_LAST_GREEN_SHA` matches the last known-good commit before writing.
  3. Set `CODEX_SWEEP_SKIP_MAIN=true` to prevent the variable writer from broadcasting to `main`.
  4. After any variable write, re-read the value via the GitHub API to confirm it was not
     overwritten by a concurrent run.
- **Required workflow controls:**
  ```yaml
  concurrency:
    group: "var-writer-${{ github.repository }}"
    cancel-in-progress: false  # variable writes must not be interrupted mid-write
  timeout-minutes: 10
  ```

---

#### 🔴 `copilot-session-chain.yml` — Copilot Session Chain
- **Runs (7d):** 0 (active, not triggered recently) &nbsp;|&nbsp; **Risk:** HIGH
- **Why it conflicts:** Chains multiple session workflows in sequence; if `main` moves between
  chain steps, later steps will operate on a branch that is already behind, producing
  incorrect artifacts or triggering redundant self-healing cycles.
- **Mitigation steps:**
  1. Only trigger when branch drift is LOW (0 commits behind `main`).
  2. Add a `git fetch origin main && git merge-base --is-ancestor main HEAD` pre-check to the
     first job; fail fast if the check fails.
  3. Set all three mitigation variables before any chain run when drift is MEDIUM or higher.
- **Required workflow controls:**
  ```yaml
  concurrency:
    group: "${{ github.workflow }}-${{ github.head_ref }}"
    cancel-in-progress: true
  timeout-minutes: 60
  ```

---

#### 🔴 `agent-orchestration-unified.yml` — Agent Orchestration (Unified)
- **Runs (7d):** 0 (active) &nbsp;|&nbsp; **Risk:** HIGH (elevated from medium by write scope)
- **Why it conflicts:** Orchestrates multiple write-capable sub-agents; stale-branch execution
  will propagate stale context to all sub-agents simultaneously.
- **Mitigation steps:**
  1. Inject `branch_drift_severity` from startup probe into the orchestration context before
     dispatching sub-agents.
  2. Add a drift gate: if `drift_severity != LOW`, sub-agents that write should be skipped.
  3. Set `CODEX_SWEEP_SKIP_MAIN=true` and `CODEX_MAX_HEALER_RUNS_PER_HOUR=2`.
- **Required workflow controls:**
  ```yaml
  concurrency:
    group: "${{ github.workflow }}-${{ github.head_ref }}"
    cancel-in-progress: true
  timeout-minutes: 60
  ```

---

### MEDIUM-Risk Workflows — Standard Mitigation

Apply `CODEX_SWEEP_SKIP_MAIN=true` and branch-scoped concurrency when drift is MEDIUM or higher.
No immediate abort required, but monitor for `workflow_run` ordering anomalies.

| Workflow file | Workflow name | Runs 7d | Conflict reason | Action |
|---|---|---:|---|---|
| `ci-rescue.yml` | CI Rescue — Auto-Fix & @copilot RCA | 55 | `workflow_run` chain ordering; stale-head auto-fix applies to wrong base | Set `CODEX_SWEEP_SKIP_MAIN=true`; verify triggering run SHA matches branch HEAD |
| `copilot-iterative-self-healing.yml` | Copilot Iterative Self-Healing Auto-Poster | 55 | Fires on `workflow_run`; stale-head post targets wrong diff | Confirm triggering run HEAD before allowing auto-post |
| `cleanup-stale-pr-comments.yml` | Cleanup Stale PR Comments | 12 | Writes PR comment deletions; can conflict if PR metadata changed mid-drift | Run only after rebase when drift ≥ MEDIUM |
| `codebase-health-sweep.yml` | Codebase Health Sweep | 7 | Write-capable sweep; stale-head run touches wrong file versions | Set `CODEX_SWEEP_SKIP_MAIN=true`; re-run post-rebase |
| `audit-qa-suite.yml` | Audit & QA Suite (Unified) | 6 | Writes audit artifacts; stale base produces mismatched diff | Confirm base SHA before triggering |
| `pr-followup-generator.yml` | Generate PR Follow-Up Prompt | 6 | Writes follow-up prompt file; stale PR state produces wrong next-action list | Rebase + re-trigger |
| `agent_infrastructure_manager.yml` | Agent Infrastructure Manager | 5 | Infrastructure writes conflict with concurrent healer changes | Serialize with `iterative-self-healing-ci.yml` via concurrency group |
| `agent-auth-delegation.yml` | Agent Token Delegation | 5 | Token delegation writes can race with healer variable writes | Set concurrency group shared with `agent-var-writer.yml` |
| `copilot-agent-vars-bootstrap.yml` | Agent Vars Bootstrap | 5 | Variable bootstrap conflicts with mid-session variable mutations | Only run at session start before any writes |
| `chatops_copilot_trigger.yml` | Chat-Ops @copilot Webhook Trigger | 5 | Dispatches other workflows; stale trigger context propagates | Validate branch HEAD SHA in webhook payload |
| `session-watchdog.yml` | Session Watchdog | 5 | Timebox enforcement may cancel work mid-rebase | Set generous timeout when rebase is in progress |
| `workflow-execution-gate.yml` | Workflow Execution Gate | 5 | Gate parses PR body; stale PR body from drift produces wrong gate state | Re-push after rebase to refresh PR body parse |
| `secrets-baseline-enforcer.yml` | Secrets Baseline Enforcer | 5 | Writes baseline file; concurrent writes corrupt the baseline | Serialize via `secrets-baseline-enforcer` concurrency group |
| `copilot-agent-checkin.yml` | Agent Check-In | 5 | Check-in fires on push; stale-head check-in logs wrong context | Acceptable; log only — no write action needed |
| `copilot-review-responder.yml` | Copilot Review Responder | 5 | Responds to review events; stale PR state produces mismatched response | Re-trigger after rebase if response targets stale diff |
| `codex-manifest-refresh.yml` | CODEX Manifest Auto-Refresh | 4 | Writes manifest; stale-head manifest references removed files | Run post-rebase; add `main` merge-base check |

---

### Workflows That Conflict (or Could Conflict) When Main Updates During Active Branch Sessions

> Legacy flat table retained for grep/tooling compatibility. The expanded cards above
> are the authoritative reference for step-by-step mitigation.

| Workflow file | Workflow name | Risk | Runs 7d | Conflict reason | Suggested mitigation variables |
|---|---|---|---:|---|---|
| `.github/workflows/iterative-self-healing-ci.yml` | Iterative Self-Healing CI | **HIGH** | 413 | write-capable + event-driven; races with branch/main drift | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/copilot-evolution-suite.yml` | Copilot Evolution & Review (Unified) | **HIGH** | 10 | write-capable + event-driven; stale base diff | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/copilot-agent-session-done.yml` | Auto-Post @copilot review After Agent Session | **HIGH** | 10 | workflow_run stale-SHA auto-post | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/agent-var-writer.yml` | Agent Variable Writer (Provenance-Chain) | **HIGH** | 5 | concurrent variable writes with healer | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/copilot-session-chain.yml` | Copilot Session Chain | **HIGH** | 0 | chained workflows amplify stale-head errors | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/agent-orchestration-unified.yml` | Agent Orchestration (Unified) | **HIGH** | 0 | stale context propagated to all sub-agents | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/ci-rescue.yml` | CI Rescue — Auto-Fix & @copilot RCA | medium | 55 | workflow_run ordering; stale-head auto-fix | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/copilot-iterative-self-healing.yml` | Copilot Iterative Self-Healing Auto-Poster | medium | 55 | workflow_run stale-head post | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/cleanup-stale-pr-comments.yml` | Cleanup Stale PR Comments | medium | 12 | comment writes on stale PR state | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/codebase-health-sweep.yml` | Codebase Health Sweep | medium | 7 | write-capable; stale-head sweep | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/audit-qa-suite.yml` | Audit & QA Suite (Unified) | medium | 6 | stale base audit artifacts | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/pr-followup-generator.yml` | Generate PR Follow-Up Prompt | medium | 6 | stale PR next-action file | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/agent_infrastructure_manager.yml` | Agent Infrastructure Manager | medium | 5 | concurrent infrastructure writes | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/agent-auth-delegation.yml` | Agent Token Delegation | medium | 5 | token delegation races with variable writes | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/copilot-agent-vars-bootstrap.yml` | Agent Vars Bootstrap | medium | 5 | mid-session variable mutation conflicts | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/chatops_copilot_trigger.yml` | Chat-Ops @copilot Webhook Trigger | medium | 5 | stale trigger context propagated | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/session-watchdog.yml` | Session Watchdog | medium | 5 | cancels work mid-rebase | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/workflow-execution-gate.yml` | Workflow Execution Gate | medium | 5 | stale PR body parse | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/secrets-baseline-enforcer.yml` | Secrets Baseline Enforcer | medium | 5 | concurrent baseline file writes | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/copilot-agent-checkin.yml` | Agent Check-In | medium | 5 | stale-head check-in log | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/copilot-review-responder.yml` | Copilot Review Responder | medium | 5 | stale diff review response | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |
| `.github/workflows/codex-manifest-refresh.yml` | CODEX Manifest Auto-Refresh | medium | 4 | stale-head manifest | `CODEX_SWEEP_SKIP_MAIN`, `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_HEALER_SKIP_SKIPCI` |

## Top 20 Quick-Win Workflows to Update (Copilot Session First)

| Rank | Workflow file | Workflow name | State | Runs 7d | Conflict risk | Quick-win updates | Copilot variable refs |
|---:|---|---|---|---:|---|---|---|
| 1 | `dynamic/agents/anthropic-code-agent` | Claude | active | 0 | unknown | Review trigger scope and remove stale fanout; Add timeout-minutes to jobs; Add branch-scoped concurrency group | n/a |
| 2 | `dynamic/anthropic-code-agent/claude` | Claude | active | 0 | unknown | Review trigger scope and remove stale fanout; Add timeout-minutes to jobs; Add branch-scoped concurrency group | n/a |
| 3 | `.github/workflows/copilot-automation.yml` | Copilot Automation Suite | active | 0 | unknown | Review trigger scope and remove stale fanout; Add timeout-minutes to jobs; Add branch-scoped concurrency group | n/a |
| 4 | `dynamic/copilot-pull-request-reviewer/copilot-pull-request-reviewer` | Copilot code review | active | 0 | unknown | Review trigger scope and remove stale fanout; Add timeout-minutes to jobs; Add branch-scoped concurrency group | n/a |
| 5 | `dynamic/agents/openai-code-agent` | OpenAI Codex | active | 0 | unknown | Review trigger scope and remove stale fanout; Add timeout-minutes to jobs; Add branch-scoped concurrency group | n/a |
| 6 | `.github/workflows/copilot-session-chain.yml` | 🔗 Copilot Session Chain | active | 0 | high | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | n/a |
| 7 | `dynamic/copilot-swe-agent/copilot` | Copilot cloud agent | active | 6 | unknown | Add timeout-minutes to jobs; Add branch-scoped concurrency group; Add explicit rate-limit/throughput guard | n/a |
| 8 | `.github/workflows/agent-orchestration-unified.yml` | Agent Orchestration (Unified) | active | 0 | medium | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | CODEX_CACHE_VERSION |
| 9 | `.github/workflows/ci-rescue.yml` | CI Rescue — Auto-Fix & @copilot RCA | disabled_manually | 55 | medium | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | COPILOT_AGENT_AUTH_ENABLED |
| 10 | `.github/workflows/cognitive_brain_ci_feedback.yml` | Cognitive Brain CI Feedback | disabled_manually | 0 | medium | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | CODEX_CACHE_VERSION |
| 11 | `.github/workflows/copilot-setup-steps.yml` | Copilot Agent Environment Setup | active | 0 | medium | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | CODEX_CACHE_VERSION,CODEX_CI_LAST_GREEN_SHA,CODEX_HEALER_SKIP_SKIPCI,CODEX_MAX_HEALER_RUNS_PER_HOUR,CODEX_SWEEP_SKIP_MAIN,COPILOT_AGENT_STATE,COPILOT_RUNNER_PROFILE |
| 12 | `.github/workflows/copilot-iterative-self-healing.yml` | Copilot Iterative Self-Healing Auto-Poster | disabled_manually | 55 | medium | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | COGNITIVE_BRAIN_SESSION_NUMBER |
| 13 | `.github/workflows/copilot-pr-session-injector.yml` | Copilot PR Session Injector | active | 0 | medium | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | n/a |
| 14 | `.github/workflows/d-capable-promotion-gate.yml` | D_CAPABLE Agent Promotion Gate | active | 0 | medium | Review trigger scope and remove stale fanout; Harden against main-update drift (rebase gate + write isolation) | n/a |
| 15 | `.github/workflows/agent-registry-validation.yml` | Agent Registry Validation | active | 0 | low | Review trigger scope and remove stale fanout | CODEX_CACHE_VERSION |
| 16 | `.github/workflows/build-agent-env-cache.yml` | Build Agent Environment Cache | active | 0 | low | Review trigger scope and remove stale fanout | CODEX_CACHE_VERSION |
| 17 | `.github/workflows/create-sub-pr-to-0D_base_.yml` | 🔀 Create Sub-PR: Session Branch → 0D_base_ | active | 0 | low | Review trigger scope and remove stale fanout | n/a |
| 18 | `.github/workflows/agent-var-writer.yml` | Agent Variable Writer (Provenance-Chain) | active | 5 | high | Harden against main-update drift (rebase gate + write isolation) | n/a |
| 19 | `.github/workflows/copilot-evolution-suite.yml` | Copilot Evolution & Review (Unified) | active | 10 | high | Harden against main-update drift (rebase gate + write isolation) | n/a |
| 20 | `.github/workflows/copilot-agent-session-done.yml` | 🔄 Auto-Post @copilot review After Agent Session | active | 10 | high | Harden against main-update drift (rebase gate + write isolation) | COPILOT_AGENT_AUTH_ENABLED |

## Perspective: Capability + Future Vision

### What this codebase is capable of doing well

The repository can already function as a policy-aware CI/CD and agent-orchestration platform with strong guardrail patterns and reusable workflow composition.

### Future vision and path improvement

Move toward a lean, high-signal workflow operating system for Copilot sessions: standardized tokenized variable contracts, explicit conflict-risk controls for branch drift, and continuous pruning/consolidation of stale or overlapping automation paths.
