# Pull Request Template

> **Version:** 2.1.0
> **Updated:** 2026-01-18
> **Repository:** Aries-Serpent/_codex_
> **Status:** 🏆 Level 4 MLOps Certified | 1225+ Tests | 90% Coverage Threshold

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

### ✅ Validation & Testing
- [x] pre-merge-validation.yml — Pre-merge checks (always required)
- [ ] resilient-validation-suite.yml — Resilient validation
- [ ] nox-gates.yml — Nox test gates

### ✅ Security & Quality
- [x] comment-review-gate.yml — Comment review gate (always required)
- [ ] security-scanning-suite.yml — Full security audit
- [ ] deferral-language-gate.yml — Deferral language guard

### 📄 Documentation
- [ ] docs-build.yml — Documentation build

### 🤖 Automation
- [x] agent-auth-delegation.yml — Agent auth delegation (always required)
- [ ] copilot-agent-checkin.yml — Agent check-in (always required)
- [ ] cost-gate.yml — Cost governance gate
- [ ] copilot-agent-session-done.yml — Auto-Post @copilot review After Agent Session
- [ ] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows
- [ ] copilot-iterative-self-healing.yml — Iterative self-healing CI loop

### ⚡ Auto-Approve
- [ ] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

> Instructions for Copilot Agent: During wrap-up, check ONLY the workflows needed for
> this session. Unchecked workflows will be SKIPPED by the gate.

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
