# Pull Request

> **Template:** v3.0.0 — S860 Copilot Cloud Agent Edition
> **Updated:** 2026-05-08
> **Repository:** Aries-Serpent/_codex_ (ID: 1040037790)
> **Copilot Agent Model Target:** claude-sonnet-4.x / gpt-4.1 (set in copilot-setup-steps.yml)

---

## 🤖 Copilot Cloud Agent — Session Context

> **⚡ MANDATORY FOR EVERY AGENT SESSION:** This block gives the cloud agent its
> environment fingerprint. Fill in or auto-generate before the first `report_progress` call.
> Leave `<!-- AUTO -->` comments in place — `session_wrapup_autofix.py` populates them.

| Key | Value |
|-----|-------|
| **PR Number** | <!-- AUTO: pr_number --> |
| **Branch** | <!-- AUTO: branch_name --> |
| **Base Branch** | `main` |
| **Head SHA (short)** | <!-- AUTO: head_sha_short --> |
| **Agent Session ID** | <!-- AUTO: session_id --> |
| **Session Label** | <!-- AUTO: session_label --> (e.g. S860) |
| **AAIS Score** | <!-- AUTO: aais_score --> / 100 |
| **Merge Readiness** | <!-- AUTO: merge_score --> % |
| **Rate-Limit Status** | <!-- AUTO: rate_limit_status --> |
| **Copilot Auth** | `COPILOT_AGENT_AUTH_ENABLED=true` (permanent — no checkbox needed) |
| **Token Chain** | `CODEX_MASTER_KEY ‖ CODEX_BACKUP_KEY ‖ github.token` <!-- pragma: allowlist secret --> |

### 🧠 Agent Pre-Load Checklist (run in order at session start)
1. `READ .codex/AGENTIC_REPO_STATE.md` — confirms auth state
2. `READ .codex/CODEBASE_AGENCY_POLICY.md` — fix ALL issues, never defer
3. `READ docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` — last session state
4. Read the last 5 lines of `.codex/aftermath/pda_iterations.jsonl` — PDA loop state
5. `READ .codex/agent_context.json` — live repo variable snapshot
6. `LOAD` all stored session memories (store_memory tool)

### ⚡ P-045 Wrap-Up Gate (run before EVERY `report_progress`)
```bash
python -m ruff check src/ tests/ --fix
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/sync_tracked_files.py --fix
python scripts/ci/auto_fix_common_issues.py --check-only
actionlint .github/workflows/*.yml 2>&1 | grep -c error  # must be 0
git diff --name-only --diff-filter=U                      # must be EMPTY
```

---

## 🔄 Workflow Execution Checklist

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)
- [x] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🔄 Active Workflows — currently enabled in the live repo baseline
- [ ] auth-tests.yml — Authentication Tests
- [ ] audit-qa-suite.yml — Audit & QA Suite (Unified)
- [ ] data-quality-suite.yml — Data Quality & Determinism Suite
- [ ] docker-build-push.yml — Build & push Docker image (GHCR)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] scheduled-archival.yml — Scheduled archival
- [ ] scheduled-dependency-audit.yml — Dependency audit

## 📋 Change Summary

| Field | Value |
|-------|-------|
| **Type** | `feat` / `fix` / `ci` / `docs` / `refactor` / `chore` |
| **Scope** | _e.g. workflows, src/codex, scripts/ci, docs_ |
| **Linked Issue** | Fixes # / Relates to # |
| **Breaking Change** | Yes / No |

### What Changed
_Concise description of the change and why._

### Key Files Modified
- `path/to/file.py` — _reason_
- `.github/workflows/foo.yml` — _reason_

---

## ⚠️ Required Safety Confirmations

- [ ] **Security Review** — No secrets, API keys, or sensitive data committed
- [ ] **Network Safety** (`NETWORK_SAFETY_ACK`) — No unauthorized network operations
- [ ] **Offline Mode** (`OFFLINE_MODE_CONFIRM`) — Audit/test operations run in strict offline mode
- [ ] **Test Validation** — Tests pass locally (`nox -s tests` or `pytest`)
- [ ] **Deferral-Language Gate** — No prohibited deferral phrases in commit messages or PR body

---

## 💰 Cost Governance — Stakeholder Approval

> | Tier | Threshold | Behaviour |
> |------|-----------|-----------|
> | ✅ GREEN | < 30 effective min, no GHCR push | Auto-approved |
> | ⚠️ YELLOW | 30–90 effective min | Warning — proceeds after 60 s |
> | 🔴 RED | > 90 effective min **or** GHCR push | **Blocked** — requires sign-off below |
>
> **Effective minutes** = `timeout × runner-multiplier × matrix-jobs`
> (`ubuntu-latest-m` = 2×, `macos` = 10×, `windows` = 2×)

- [ ] 💰 **Cost Proposal Approved** — I (@mbaetiong) have reviewed the cost estimate and approve the Actions-minutes spend for this PR.

> Leave unchecked for GREEN/YELLOW-tier workflows. The CI gate polls this every 60 s for up to 10 min.

---

## 🚦 Rate-Limit Awareness

> The sandbox token (`github.token` / `GITHUB_TOKEN`) has a **separate, smaller quota** from
> `CODEX_MASTER_KEY`. Both pools can be exhausted independently.
>
> **Before any bulk API call:** `python scripts/ci/github_api_trickle.py --status --write-env`
>
> **Polite-sleep defaults** (set as job-level `env:` in workflows):
> | Variable | Default | When to raise |
> |----------|---------|---------------|
> | `GH_TRICKLE_POLITE_SLEEP` | `0.5` s | Scheduled / bulk workflows → `1.0` |
> | `GH_TRICKLE_MIN_REMAINING` | `50` | Lower-risk read-only calls → `20` |
> | `GH_TRICKLE_MAX_WAIT` | `120` s | Never raise above `300` |
>
> **Circuit-breaker pattern** — add before every paginate loop:
> ```javascript
> const rl = await github.rest.rateLimit.get();
> if ((rl.data?.resources?.core?.remaining ?? 999) < 20) {
>   core.warning('Rate limit low — stopping pagination');
>   break;
> }
> ```

---

## 🧪 Testing Checklist

- [ ] Unit / integration tests pass (`pytest` or `nox -s tests`)
- [ ] Linting passes (`ruff check src/ tests/`)
- [ ] Type checking passes (`python scripts/ci/mypy_baseline.py --require-baseline`)
- [ ] New tests added for new functionality
- [ ] No coverage regression (`--cov-fail-under` threshold respected)
- [ ] `actionlint .github/workflows/*.yml` — **0 errors** (if workflows changed)

---

## 📖 Documentation Checklist

- [ ] `CHANGELOG.md` updated under `## [Unreleased]` with `### Added/Fixed (SN)` entry
- [ ] `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` updated with today's session entry
- [ ] Docstrings added/updated for new public functions
- [ ] Living docs updated (`docs/roadmap/`, `docs/sessions/`) if architecture changed
- [ ] README.md updated (if user-facing behaviour changed)

---

## 🤖 AI Agency Policy Compliance

_For Copilot / AI-assisted PRs:_

- [ ] Plan documented before execution (via `report_progress` checklist)
- [ ] `CODEBASE_AGENCY_POLICY.md` followed — ALL issues fixed, none deferred
- [ ] PDA loop (Plan → Do → Assess) documented in session diagram
- [ ] Codebase left better than found

---

## 🚨 CI Failure Triage

> **Instructions:** Check the box next to any failing job, then post the fix prompt as a PR comment.
> Leave all boxes unchecked if CI is green.

<details>
<summary>🔴 Common Failure Patterns (click to expand)</summary>

| # | Job | Common Cause | Fix Prompt |
|---|-----|-------------|------------|
| 1 | `cost-gate` | RED-tier timeout waiting for stakeholder checkbox | Tick `💰 Cost Proposal Approved` above or re-run with `workflow_dispatch` |
| 2 | `actionlint-gate` | SC2086 unquoted vars / duplicate step IDs | `@copilot Fix actionlint-audit: run actionlint .github/workflows/*.yml and fix all errors` |
| 3 | `nox_gates.yml` | pre-commit / detect-secrets / ruff failures | `@copilot Fix validation: run pre-commit run --files <changed> and python -m ruff check src/ tests/ --fix` <!-- pragma: allowlist secret --> |
| 4 | `agent-auth-delegation.yml` | AGENT_ACCOUNTABILITY_REPORT or CHANGELOG not touched in last commit | `@copilot Fix REQ-4/REQ-5: touch docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md and CHANGELOG.md in the last commit` |
| 5 | `workflow-execution-gate.yml` | WEC checklist drift or stale workflow-name mismatch | `@copilot Fix WEC contract: align the PR checklist with the active workflow baseline and preserve the current maintainer selections` |
| 6 | `deferral-language-gate.yml` | Prohibited deferral phrase in PR body or commit | `@copilot Fix deferral-language: scan PR body and last 3 commits for prohibited phrases; remove or rephrase` |
| 7 | `codeql` | New CWE alert in changed Python | `@copilot Fix CodeQL alert: check security/code-scanning tab; fix the finding or request dismissal with rationale` |
| 8 | `resilient_validation` | pytest failures or import errors | `@copilot Fix Resilient Validation: run pytest tests/ -x --tb=short and fix any broken imports or assertions` |
| 9 | `auto-fix-pr-check` | ruff F401 unused imports or Pattern 20 YAML multiline | `@copilot Fix auto-fix: run python scripts/ci/auto_fix_common_issues.py and commit fixes` |
| 10 | `copilot-swe-agent` | Agent context overflow or API timeout | Re-trigger with smaller scope, or run `python scripts/ci/generate_manifest.py` to refresh context |
| 11 | `token-expiry-monitor` | PAT near expiry | Follow 7-step playbook in `docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md §9` <!-- pragma: allowlist secret --> |

- [ ] **Failure(s) detected** — @copilot please investigate and fix the checked items above.

</details>

---

## 🤖 Agents Used

> **For Copilot Cloud Agent:** List every Custom Agent (from `AGENT_REGISTRY.yaml`) invoked during this session.
> Check the box using `- [x] \`agent_type\`` format to indicate usage.
> Required by CAD-Mandate (Rule 3).

- [ ] `agent-type-here`
- [ ] `another-agent-here`

---

## 🔄 Workflow Execution Checklist

> **For Copilot Cloud Agent:** Check ONLY the workflows needed this session. Unchecked
> workflows are SKIPPED by the gate. `always required` items are pre-checked and
> **must never be unchecked**. Preserve all previously-checked `[x]` maintainer
> selections across every `report_progress` call.
>
> **E→D maintainer rule:** Copilot agent operates as codebase maintainer in active E→D logic.
> Deployment-orchestration actions (including privileged queued operations for repo/org
> secrets, variables, webhooks, and Copilot queued-session reaction cleanup) must be
> executed through approval-gated workflows using elevated token chain only.
>
> **Rate-limit note:** Opt-in workflows consume REST quota. Avoid checking more than
> 10 opt-in workflows per session when `GH_TRICKLE_MIN_REMAINING` is below 100.
>
> **HARDENED INSTRUCTION (non-negotiable):** This entire WEC block MUST be appended
> verbatim to **every** PR body update — including every `report_progress` call.
> Generate it via: `python scripts/ci/session_wrapup_autofix.py --print-wec-block --pr-number <N>`

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)
- [x] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🔄 Active Workflows — currently enabled in the live repo baseline
- [ ] auth-tests.yml — Authentication Tests
- [ ] audit-qa-suite.yml — Audit & QA Suite (Unified)
- [ ] data-quality-suite.yml — Data Quality & Determinism Suite
- [ ] docker-build-push.yml — Build & push Docker image (GHCR)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] scheduled-archival.yml — Scheduled archival
- [ ] scheduled-dependency-audit.yml — Dependency audit

### ⚡ Fast-Forward Safe Files to `main`

> Promote pre-approved files from this PR directly to `main` without waiting for
> the full merge cycle. Critical for workflow files that only take effect from the
> default branch.

<!-- FF_MERGE_MODE: create-pr -->
<!-- FF_FILES:  -->
<!-- FF_DRY_RUN: false -->

- [ ] ⚡ **Fast-Forward Approved** — I (@mbaetiong) approve promoting the files above to `main` immediately

> **⚠️ HARDENED AGENT INSTRUCTION (non-negotiable):** This entire WEC block MUST be
> appended verbatim to **every** PR body update — including every `report_progress` call.
> **ALWAYS generate the WEC block via the CLI** before calling `report_progress`:
>
>     python scripts/ci/session_wrapup_autofix.py --print-wec-block --pr-number <N>
>
> The script reads `.codex/wec_state.json` (human-grant history) and returns the correct
> WEC block with ALL human grants preserved as sticky `[x]`.

---

## 🔗 Related Issues / PRs

_Fixes # · Relates to # · Blocked by #_

---

## 👀 Reviewer Notes

_Areas needing careful review, trade-offs made, or known limitations._

---

_Add screenshots for UI/visual changes._

- [ ] **Multiple Copilot Sessions** (`COPILOT_MULTI_SESSION`) — ⚠️ Default: disabled (one session at a time). Enable only to allow parallel sessions on different PRs.

---

## 👤 Reviewer(s)

- @mbaetiong
