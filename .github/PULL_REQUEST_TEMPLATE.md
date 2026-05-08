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
| **Token Chain** | `CODEX_MASTER_KEY ‖ CODEX_BACKUP_KEY ‖ github.token` |

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
| 3 | `validate` / `pre-merge-validation` | pre-commit / detect-secrets / ruff failures | `@copilot Fix validation: run pre-commit run --files <changed> and python -m ruff check src/ tests/ --fix` |
| 4 | `agent-auth-delegation` | AGENT_ACCOUNTABILITY_REPORT or CHANGELOG not touched in last commit | `@copilot Fix REQ-4/REQ-5: touch docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md and CHANGELOG.md in the last commit` |
| 5 | `comment-review-gate` | Unanswered `<comment_new>` PR comments | `@copilot reply_to_comment for all open <comment_new> items using the reply_to_comment tool` |
| 6 | `deferral-language-gate` | Prohibited deferral phrase in PR body or commit | `@copilot Fix deferral-language: scan PR body and last 3 commits for prohibited phrases; remove or rephrase` |
| 7 | `codeql` | New CWE alert in changed Python | `@copilot Fix CodeQL alert: check security/code-scanning tab; fix the finding or request dismissal with rationale` |
| 8 | `resilient_validation` | pytest failures or import errors | `@copilot Fix Resilient Validation: run pytest tests/ -x --tb=short and fix any broken imports or assertions` |
| 9 | `auto-fix-pr-check` | ruff F401 unused imports or Pattern 20 YAML multiline | `@copilot Fix auto-fix: run python scripts/ci/auto_fix_common_issues.py and commit fixes` |
| 10 | `copilot-swe-agent` | Agent context overflow or API timeout | Re-trigger with smaller scope, or run `python scripts/ci/generate_manifest.py` to refresh context |
| 11 | `token-expiry-monitor` | PAT near expiry | Follow 7-step playbook in `docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md §9` |

- [ ] **Failure(s) detected** — @copilot please investigate and fix the checked items above.

</details>

---

## 🔄 Workflow Execution Checklist

> **For Copilot Cloud Agent:** Check ONLY the workflows needed this session. Unchecked
> workflows are SKIPPED by the gate. `always required` items are pre-checked and
> **must never be unchecked**. Preserve all previously-checked `[x]` maintainer
> selections across every `report_progress` call.
>
> **Rate-limit note:** Opt-in workflows consume REST quota. Avoid checking more than
> 10 opt-in workflows per session when `GH_TRICKLE_MIN_REMAINING` is below 100.
>
> **HARDENED INSTRUCTION (non-negotiable):** This entire WEC block MUST be appended
> verbatim to **every** PR body update — including every `report_progress` call.
> Generate it via: `python scripts/ci/session_wrapup_autofix.py --print-wec-block --pr-number <N>`

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] pre-merge-validation.yml — Pre-merge checks (always required)
- [x] comment-review-gate.yml — Comment review gate (always required)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)

### 🔄 Always Active — fire via push/workflow_run (need approval in Actions tab)
- [x] copilot-agent-checkin.yml — Agent check-in / S221 guard (fires on push)
- [ ] copilot-agent-session-done.yml — Auto-post @copilot review after agent session (fires on workflow_run)
- [ ] copilot-iterative-self-healing.yml — Iterative self-healing CI loop (fires on workflow_run — needs approval)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)

### ⚡ Auto-Approve
- [x] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🧪 Opt-In: Testing & Validation
- [ ] validate.yml — Validation Pipeline (detect-secrets, ruff, pre-commit, sync-tracked)
- [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
- [ ] mypy-baseline.yml — mypy type-check anti-regression gate
- [ ] coverage-with-timeout.yml — Coverage with timeout guards
- [ ] progressive-validation.yml — Progressive Validation Suite
- [ ] pre-flight-validation.yml — Pre-flight CI validation
- [ ] ci-checkpoint-validation.yml — CI Checkpoint Validation
- [ ] data-quality-suite.yml — Data Quality & Determinism Suite
- [ ] auth-tests.yml — Authentication Tests
- [ ] pr-checks.yml — PR Checks (isolated cache, src/ scope)
- [ ] html_visual_regression.yml — HTML Visual Regression Screenshots

### 🔒 Opt-In: Security & Quality
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)
- [ ] codeql-analysis.yml — CodeQL SAST analysis
- [ ] actionlint-audit.yml — Workflow compliance audit (actionlint)
- [ ] semgrep_sarif.yml — Semgrep SAST (SARIF upload)
- [ ] auto-fix-common-issues.yml — Auto-Fix Common CI Issues
- [ ] auto-fix-pr-check.yml — PR Auto-Fix Check
- [ ] code-quality-coverage-suite.yml — Code Quality & Coverage Suite
- [ ] audit-qa-suite.yml — Audit & QA Suite (Unified)
- [x] codeql-alert-fetcher.yml — CodeQL Alert Fetcher (artifact for in-session review)

### 📄 Opt-In: Documentation
- [ ] documentation-link-checker.yml — Documentation link checker
- [ ] pages-pre-merge-validation.yml — Pages pre-merge validation

### ⚙️ Opt-In: Infrastructure & Deployment
- [ ] reference-integrity.yml — Reference integrity + agent size gate
- [ ] dependency-submission.yml — Resilient dependency submission
- [ ] docker-build-push.yml — Build & push Docker image (GHCR)
- [ ] rust_swarm_ci.yml — Rust-Python hybrid swarm CI/CD
- [ ] root-org-validation.yml — Root organization validation
- [ ] agent-registry-validation.yml — Agent registry validation
- [ ] qa-walkthrough.yml — QA walkthrough agent
- [ ] token-expiry-monitor.yml — Daily PAT expiry monitor (T-02)

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


---

## 🤖 COPILOT CONTINUATION (Auto-Generated)

@copilot continue with remaining tasks for this PR

**📋 Follow-Up Prompt**: See `COGNITIVE_BRAIN_CONTINUATION_PROMPT_PHASE_*.md` for active prompts

### Quick Reference
- **Test Count:** 1225+ (Phase 14-17 complete)
- **Coverage Threshold:** 90% (pyproject.toml)
- **Python Versions:** 3.11, 3.12

---

## ⚠️ REQUIRED Safety Confirmations

**These checkboxes MUST be confirmed before merge:**

- [ ] **Network Safety Acknowledgment** (`NETWORK_SAFETY_ACK`) - I confirm NO unauthorized network operations are performed by this PR
- [ ] **Offline Mode Confirmation** (`OFFLINE_MODE_CONFIRM`) - I confirm all audit and test operations run in strict offline mode
- [ ] **Security Review** - I confirm no secrets, API keys, or sensitive data are committed
- [ ] **Test Validation** - I confirm tests pass locally (`pytest`)

---

## 💰 Cost Governance — Stakeholder Approval

> **Subscription:** GitHub Team (3,000 Actions min/mo · 2 GB artifacts) + Copilot Pro Plus (1,500 premium requests/mo)
>
> The **Cost Gate** CI job classifies each workflow run into a tier and blocks `RED`-tier jobs
> until a stakeholder ticks the checkbox below.
>
> | Tier | Threshold | Behaviour |
> |------|-----------|-----------|
> | ✅ GREEN | < 30 effective min, no GHCR push | Auto-approved — no action needed |
> | ⚠️ YELLOW | 30–90 effective min | Warning posted — proceeds after 60 s |
> | 🔴 RED | > 90 effective min **or** GHCR push | **Blocked** — requires checkbox below |
>
> **Effective minutes** = `timeout × runner-multiplier × matrix-jobs`
> (ubuntu-latest-m = 2×, macos = 10×, windows = 2×)

### 💰 Stakeholder Sign-off

_Tick this box to unblock a RED-tier cost gate. Leave unticked for GREEN/YELLOW workflows._

- [ ] 💰 **Cost Proposal Approved** — I (@mbaetiong) have reviewed the cost estimate posted by the Cost Gate CI job and approve the Actions-minutes spend for this PR.

> ℹ️ If no Cost Gate comment has been posted yet (GREEN/YELLOW tier), leave this unchecked.
> The CI gate polls this checkbox every 60 s for up to 10 minutes after posting its estimate.

---

## 📝 Commit Message Checklist

**Each commit message MUST include:**

- [ ] **What Was Done** - Clear description of completed work in this commit
- [ ] **What's Next** - Brief note on remaining work or next steps
- [ ] **Phase/Task Reference** - Reference to the phase or task being worked on

### Commit Message Format

```
<type>: <short description>

**Done:**
- [x] Completed item 1
- [x] Completed item 2

**Next:**
- [ ] Pending item 1
- [ ] Pending item 2

Phase: <phase number> | Status: <percentage>%
```

### Example Commit Message

```
feat: Add Phase 16.0 documentation tests

**Done:**
- [x] Created tests/docs/test_doc_validation.py (20+ tests)
- [x] Created tests/docs/test_api_docs.py (15+ tests)
- [x] Updated PR template to v2.0

**Next:**
- [ ] Create API contract tests (Phase 16.1)
- [ ] Create E2E workflow tests (Phase 16.2)

Phase: 16.0 | Status: 100%
```

---

## Scope

| Field | Value |
|-------|-------|
| **Type** | Feature / Bug Fix / Docs / CI / Refactor |
| **Areas** | _e.g., tests, CI, docs, workflows, security_ |

### Description

_Provide a clear and concise description of the changes._

### Changes Made

_List the key changes:_
- Change 1
- Change 2
- Change 3

---

## 📋 Configuration (Opt-In)

### Testing Options
- [ ] **Run Full Test Suite** - Execute all 960+ tests
- [ ] **Coverage Report** - Generate coverage report with `--cov`
- [ ] **Performance Benchmarks** - Run benchmark tests in `tests/perf/`

### Documentation
- [ ] **Build Docs** - Build MkDocs documentation
- [ ] **Update CHANGELOG** - Add entry to CHANGELOG.md

### Security
- [ ] **Security Scan** - Run CodeQL/Semgrep analysis
- [ ] **Dependency Audit** - Run `pip-audit` for vulnerabilities

---

## Verification Commands

```bash
# Quick validation
pytest tests/ -x --tb=short

# Full test suite with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=85

# Linting
ruff check src/ tests/
black --check src/ tests/

# YAML validation
yamllint -c .yamllint.yml .github/workflows/
```

---

## Testing Checklist

- [ ] Tests pass locally (`pytest`)
- [ ] Linting passes (`ruff check`, `black --check`)
- [ ] Type checking passes (`mypy` if applicable)
- [ ] New tests added for new functionality
- [ ] Existing tests updated for changed functionality

---

## Documentation Checklist

- [ ] README.md updated (if applicable)
- [ ] Docstrings added/updated for new functions
- [ ] CHANGELOG.md updated (if applicable)
- [ ] API documentation updated (if applicable)

---

## Code Quality Checklist

- [ ] Code follows repository style guidelines
- [ ] Self-review completed
- [ ] No hardcoded secrets or sensitive data
- [ ] No new warnings introduced
- [ ] Error handling is appropriate

---

## 🚨 CI Failure Triage (Frequently Failing Jobs)

> **Instructions for @mbaetiong:** Check any boxes below for jobs that are currently failing on this PR. Copy the fix prompt and post it as a PR comment to queue Copilot for automated resolution. Leave all boxes unchecked if CI is green.

- [ ] **`cost-gate`** — 💰 Cost Gate  
  *Failure:* RED-tier job timed out waiting for stakeholder checkbox  
  *Fix:* `Tick the checkbox: - [x] 💰 Cost Proposal Approved in the PR description, or trigger the workflow via workflow_dispatch to bypass.`

- [ ] **`actionlint-gate`** — Workflow Compliance Audit (actionlint)  
  *Failure:* SC2086/SC1073 shellcheck errors or duplicate step IDs  
  *Fix:* `@copilot Fix actionlint-audit failure: check .github/workflows/ for SC2086 unquoted vars, SC1073 parse errors, or duplicate step IDs. Run: actionlint .github/workflows/*.yml`

- [ ] **`art-validation-fast`** — Art_Validation Pipeline / Fast Validation  
  *Failure:* pre-commit trailing whitespace / EOF / detect-secrets  
  *Fix:* `@copilot Fix Art_Validation fast failure: run pre-commit hooks on changed files. Check trailing whitespace, end-of-file newlines, detect-secrets baseline, and check-yaml on .github/workflows/. Run: pre-commit run --files <changed_files>`

- [ ] **`agent-token-delegation`** — Agent Token Delegation (REQ-4/REQ-5)  
  *Failure:* Missing `AGENT_ACCOUNTABILITY_REPORT.md` or `CHANGELOG.md` touch in last commit  
  *Fix:* `@copilot Fix Agent Token Delegation failure (REQ-4/REQ-5): touch docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md and CHANGELOG.md with appropriate W-NNN entries in the last commit. Both files must appear in git diff HEAD~1 HEAD.`

- [ ] **`resilient-validation`** — Resilient Validation Suite  
  *Failure:* pytest failures or import errors in src/codex  
  *Fix:* `@copilot Fix Resilient Validation Suite failure: check the failing job log for import errors or test failures. Run: pytest tests/ -x --tb=short and fix any broken imports or assertions.`

- [ ] **`progressive-validation`** — Progressive Validation Suite  
  *Failure:* Coverage threshold or test regressions  
  *Fix:* `@copilot Fix Progressive Validation Suite failure: check coverage thresholds in pyproject.toml (currently 90%). Run: pytest --cov=src --cov-report=term-missing --cov-fail-under=90 and add tests for uncovered lines.`

- [ ] **`e-to-d-gate`** — E→D Transition Readiness Gate  
  *Failure:* One of 5 transition conditions not met (GROUNDED count, CI rate, manifests)  
  *Fix:* `@copilot Fix E→D Transition Gate failure: run scripts/ci/enforcement_kpi_dashboard.py to see which of the 5 conditions is failing. Typically: GROUNDED agent count < threshold, CODEX_CI_FAILURE_RATE too high, or CODEX_MANIFEST.json stale. Regenerate: python scripts/ci/generate_manifest.py`

- [ ] **`rust-swarm-ci`** — Art_Rust-Python Hybrid Swarm CI/CD  
  *Failure:* Rust compilation errors or cargo test failures  
  *Fix:* `@copilot Fix Rust Swarm CI failure: check the failing job log for cargo errors. Run: cargo test --workspace in the repo root and fix any compilation or test failures. Note: matrix is restricted to ubuntu-latest only.`

- [ ] **`security-scanning`** — Art_Security Scanning Suite  
  *Failure:* Bandit B310/B601 or CodeQL alert  
  *Fix:* `@copilot Fix Security Scanning failure: run bandit -r src/ and check CodeQL alerts. For B310 add HTTPS-only URL validation + nosec annotation. See .bandit for existing skip list.`

- [ ] **`codeql`** — Art_"CodeQL"  
  *Failure:* New CWE finding in changed Python files  
  *Fix:* `@copilot Fix CodeQL failure: check the code scanning alerts tab for the new finding. Common fixes: parameterize SQL queries, validate URL schemes before urlopen, avoid shell=True in subprocess calls.`

- [ ] **`auto-fix-check`** — PR Auto-Fix Check  
  *Failure:* ruff F401 unused imports or SC2086 in workflows  
  *Fix:* `@copilot Fix PR Auto-Fix Check: run python scripts/ci/auto_fix_common_issues.py --check-only --json-output /tmp/diag.json and then python scripts/ci/copilot_agent_auto_fix.py to apply all auto-fixable patterns.`

- [ ] **`pre-merge-validation`** — Pre-Merge Validation  
  *Failure:* Same as auto-fix-check or test failure  
  *Fix:* `@copilot Fix Pre-Merge Validation failure: run python scripts/ci/auto_fix_common_issues.py and then pytest tests/ -x --tb=short to ensure all checks pass before merge.`

- [ ] **`workflow-link-validation`** — Art_Workflow Documentation Link Validation  
  *Failure:* Dead link in .github/workflows/*.yml or docs/  
  *Fix:* `@copilot Fix Workflow Link Validation failure: run the link-validator-agent to find and fix broken Markdown/YAML links. Check .github/workflows/*.yml for references to deleted files or renamed steps.`

- [ ] **`dependency-submission`** — Automatic Dependency Submission  
  *Failure:* pip dependency graph submission failed  
  *Fix:* `@copilot Fix Dependency Submission failure: this is usually a transient GitHub API issue. Re-run the workflow. If persistent, check that the GITHUB_TOKEN has dependency-graph write permissions.`

- [ ] **`semgrep-sast`** — Art_Semgrep SAST (SARIF Upload)  
  *Failure:* New semgrep policy violation in changed Python  
  *Fix:* `@copilot Fix Semgrep SAST failure: run semgrep --config .codex/policies/semgrep/ src/ and fix any new findings. Check .codex/policies/semgrep/soft_enforcement.yaml for the active rule set.`

- [ ] **`generate-followup`** — Generate PR Follow-Up Prompt  
  *Failure:* Missing required context file or CODEX_MANIFEST.json stale  
  *Fix:* `@copilot Fix Generate PR Follow-Up Prompt failure: regenerate CODEX_MANIFEST.json with python scripts/ci/generate_manifest.py and ensure .codex/docs/FOLLOWUP_PROMPT_PR3483.md exists and is valid Markdown.`

- [ ] **`admin-setup-verify`** — Admin Setup Verification  
  *Failure:* CODEX_MASTER_KEY or CODEX_BACKUP_KEY not functional  
  *Fix:* `@copilot Fix Admin Setup Verification failure: check that secrets CODEX_MASTER_KEY and CODEX_BACKUP_KEY are set and have issues:write scope. Re-run the workflow manually with the PR number to test probes.`

- [ ] **`embedding-rebuild`** — Embedding Index Rebuild  
  *Failure:* FAISS index build failure or missing corpus files  
  *Fix:* `@copilot Fix Embedding Index Rebuild failure: run python scripts/ci/build_embeddings.py --verify to check corpus integrity. If the corpus is empty, run python scripts/ci/prune_corpus.py --stats first to confirm DB state.`

- [ ] **`copilot-swe-agent`** — Copilot coding agent  
  *Failure:* Agent failed to process the request  
  *Fix:* `@copilot Fix the Copilot SWE agent failure: check the failing run log for the specific error (API timeout, context overflow, or tool execution failure). If context overflow: regenerate CODEX_MANIFEST.json with a lower budget: COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS=16000 python scripts/ci/generate_manifest.py`

---

> **Auto-fill comment:** Copy the fix prompt(s) from the checked item(s) above and paste them as a PR comment to queue Copilot for automated resolution.

---

## AI Agency Policy Compliance

For Copilot/AI-assisted PRs:
- [ ] Plan documented before execution
- [ ] Pre-commit/commit terminology used correctly
- [ ] Codebase left better than found
- [ ] 5-pass self-review completed (if applicable)
- [ ] PDA loop (Plan→Do→Assess) documented

---

---

- [ ] **Multiple Copilot Coding Agent Sessions** (`COPILOT_MULTI_SESSION`)
  - ⚠️ **Default: disabled** — Only ONE Copilot session active at a time
  - When enabled: allows parallel Copilot sessions on different PRs
  - When disabled: sessions are queued and executed sequentially
  - **Caution:** Multiple sessions may cause merge conflicts on shared files
  - See: [`docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md`](docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md)

---

## 🔄 Workflow Execution Checklist

> **Instructions for Copilot Agent:** During wrap-up, check ONLY the workflows needed for
> this session. Unchecked workflows will be SKIPPED by the gate. **Use EXACT filenames**
> (see `docs/ci/PR_LIFECYCLE.md §7` for the Tier 1/Tier 2 rescue model).
> `always required` items are pre-checked and must never be unchecked.
> `always active` items fire via push/workflow_run — Tier 2 needs manual approval in Actions tab.

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] pre-merge-validation.yml — Pre-merge checks (always required)
- [x] comment-review-gate.yml — Comment review gate (always required)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)

### 🔄 Always Active — fire via push/workflow_run (Tier 2: need manual approval in Actions tab)
- [x] copilot-agent-checkin.yml — Agent check-in / S221 guard (fires on push)
- [ ] copilot-agent-session-done.yml — Auto-post @copilot review after agent session (fires on workflow_run)
- [ ] copilot-iterative-self-healing.yml — Iterative self-healing CI loop (fires on workflow_run — needs approval)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)

### ⚡ Auto-Approve
- [ ] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🧪 Opt-In: Testing & Validation
- [ ] validate.yml — Validation pipeline (detect-secrets, ruff, pre-commit, sync-tracked)
- [ ] resilient_validation.yml — Resilient validation (full pytest suite, 4 shards)
- [x] mypy-baseline.yml — Type-check anti-regression gate
- [ ] test-rag.yml — RAG module tests (coverage ≥95%)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
- [x] coverage-with-timeout.yml — Coverage with timeout guards
- [ ] progressive-validation.yml — Progressive validation suite
- [x] pre-flight-validation.yml — Pre-flight CI validation
- [x] ci-checkpoint-validation.yml — CI checkpoint validation
- [ ] data-quality-suite.yml — Data quality & determinism suite
- [x] auth-tests.yml — Authentication tests
- [x] pr-checks.yml — PR Checks (isolated cache, src/ scope)
- [ ] html_visual_regression.yml — HTML Visual Regression Screenshots

### 🔒 Opt-In: Security & Quality
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)
- [x] codeql-analysis.yml — CodeQL SAST analysis
- [x] actionlint-audit.yml — Workflow compliance audit (actionlint)
- [x] semgrep_sarif.yml — Semgrep SAST (SARIF upload)
- [x] auto-fix-common-issues.yml — Auto-fix common CI issues
- [x] auto-fix-pr-check.yml — PR auto-fix check
- [x] code-quality-coverage-suite.yml — Code quality & coverage suite
- [x] audit-qa-suite.yml — Audit & QA Suite (Unified)

### 📄 Opt-In: Documentation
- [ ] documentation-link-checker.yml — Documentation link checker
- [x] pages-pre-merge-validation.yml — Pages pre-merge validation

### ⚙️ Opt-In: Infrastructure & Deployment
- [x] reference-integrity.yml — Reference integrity + agent size gate
- [x] dependency-submission.yml — Resilient dependency submission
- [ ] docker-build-push.yml — Build & push Docker image (GHCR)
- [ ] rust_swarm_ci.yml — Rust-Python hybrid swarm CI/CD
- [x] root-org-validation.yml — Root organization validation
- [x] agent-registry-validation.yml — Agent registry validation
- [x] qa-walkthrough.yml — QA walkthrough agent

### ⚡ Fast-Forward Safe Files to `main`

> Promote pre-approved files from this PR directly to `main` without waiting for
> the full merge cycle. Critical for workflow files that only take effect from the
> default branch (`schedule`, `workflow_run`, `workflow_dispatch` triggers).
> See [`docs/ci/PR_LIFECYCLE.md §19`](docs/ci/PR_LIFECYCLE.md) for full specification.

**Step 1 — Set parameters** *(edit the `<!-- FF_... -->` comment lines in the raw PR body — they are invisible when rendered but are read directly by the WEC gate parser)*

```
FF_MERGE_MODE  create-pr      # create-pr = opens reviewable PR to main
                               # direct-push = commits directly (admin only)
FF_FILES       (blank)         # blank = use full .codex/fast_forward_allowlist.yaml
                               # or comma-separated: .github/workflows/foo.yml, scripts/ci/bar.py
FF_DRY_RUN     false           # true = simulate only, no files are pushed
```

<!-- ═══════════════════════════════════════════════════════════════════════════
     WEC GATE PARAMETERS — edit the values below (one per line, must stay as
     separate HTML comment lines so the grep parser in workflow-execution-gate.yml
     can extract them with:
       grep -oP '(?<=<!-- FF_MERGE_MODE: )\S+(?= -->)'
       grep -oP '(?<=<!-- FF_FILES: ).*(?= -->)'
       grep -oP '(?<=<!-- FF_DRY_RUN: )\S+(?= -->)'
     ═══════════════════════════════════════════════════════════════════════════ -->

<!-- FF_MERGE_MODE: create-pr -->

<!-- FF_FILES:  -->

<!-- FF_DRY_RUN: false -->

**Step 2 — List files** *(optional — leave blank to use the full allowlist)*

<!-- FF_BLOCK_START
Files to fast-forward (one per line, leave blank to use full allowlist):

FF_BLOCK_END -->

**Step 3 — Approve**

- [ ] ⚡ **Fast-Forward Approved** — I (@mbaetiong) approve promoting the files above to `main` immediately

> **⚠️ HARDENED AGENT INSTRUCTION (non-negotiable):** This entire WEC block MUST be
> appended verbatim to **every** PR body update — including every `report_progress` call.
> Copy the WEC block from the current PR body into the `prDescription` parameter, keeping
> **all previously-checked `[x]` items checked**. Never reset a maintainer selection to `[ ]`.
> Only `always required` and `always active` items may be auto-checked. All other items
> preserve their current maintainer-selected state.
> **Use EXACT filenames** — do NOT substitute hyphens for underscores or vice versa.

_Add screenshots for UI changes_

---

## Related Issues

_Link related issues: Fixes #123, Relates to #456_

---

## Reviewer Notes

_Any specific areas that need careful review?_

---

## Reviewer(s)

- @mbaetiong
