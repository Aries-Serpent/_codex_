# Pull Request Template

> **Version:** 1.5.0
> **Generated:** 2026-04-01
> **Purpose:** Standardized PR workflow with Copilot continuation support, safety checks, and optional capability controls

---

## 🤖 COPILOT CONTINUATION (Auto-Generated)

> ✅ **Pre-authorized.** `COPILOT_AGENT_AUTH_ENABLED=true` · `💰 Cost Proposal Approved` — start immediately.
> ✅ Confirm no blocking comments are present on this PR before proceeding.

@copilot continue with next phase tasks for this PR

**📋 Follow-Up Prompt**: View Active Prompt

<!-- Note: The {pr_number} placeholder is NOT automatically replaced in this template.
     After PR creation, the workflow will post a comment with the correct link.
     Alternatively, manually replace {pr_number} with your actual PR number. -->

### Quick Phase Summary

**🔴 Priority 1 - Immediate** (must complete in next session):
- Tasks will be auto-populated when PR is opened

**🟡 Priority 2 - Validation** (complete after P1):
- Validation tasks will be auto-populated

**🟢 Priority 3 - Enhancement** (future scope):
- Future enhancements will be listed here

### Execution Instructions

**To Continue This Work**:
1. Comment `@copilot continue` on this PR
2. Copilot will load the full follow-up prompt with detailed steps
3. Execute tasks in priority order with mandatory self-review
4. Update continuation prompt with progress
5. Repeat until all phases complete

**For Manual Execution**:
- Review the complete follow-up prompt (link will be provided in workflow comment)
- Follow step-by-step implementation guide
- Run all validation commands
- Complete 5-pass self-review before concluding

### Session Metrics

**Progress**: Auto-tracked across sessions
**Latest Session**: Will be updated automatically

---

## ⚠️ REQUIRED Safety Confirmations

**These checkboxes MUST be confirmed before merge:**

- [ ] **Network Safety Acknowledgment** (`NETWORK_SAFETY_ACK`) - I confirm NO network operations (web scraping, API calls, external fetches) are performed by this PR
- [ ] **Offline Mode Confirmation** (`OFFLINE_MODE_CONFIRM`) - I confirm all audit and test operations run in strict offline mode

---

## 📋 RECOMMENDED Configuration (Opt-In)

### Audit Depth & Evidence Control

- [ ] **Full Depth Audit** (`AUDIT_DEPTH=4`) - Use recommended depth for complete evidence capture (default: 3)
- [ ] **Depth Restriction Acknowledged** - I acknowledge that `AUDIT_DEPTH < 4` may truncate evidence

### PII & Content Filtering

- [ ] **PII Filtering Enabled** (`CONTENT_FILTER_MODE=pii` or `combined`) - Apply PII redaction to artifacts
- [ ] **Extended PII Patterns** (`PII_PATTERN_SET=extended`) - Use extended pattern set (emails, phones, IPs, postal codes)
- [ ] **Custom PII Patterns** (`PII_CUSTOM_LIST=<patterns>`) - Additional custom regex patterns specified
- [ ] **Allowlist Profile Selected** (`ALLOWLIST_PROFILE=A|B|C`) - File type filtering applied (Profile: _____)

### Archival & Compression

- [ ] **Auto-Archive Large Bundles** (`MAX_BUNDLE_MB` threshold configured) - Compress artifacts > _____ MB
- [ ] **Archive Format** (`ARCHIVE_FORMAT=tar.gz|zip`) - Format: _____
- [ ] **Dual Pointer Style** (`ARCHIVE_POINTER_STYLE=both`) - Generate both JSON pointer + SHA256 sidecar

### Agent-Run Heavy Jobs (Optional)

- [ ] **Agent-Run: Distributed** (`ACCELERATE_TEST=1`) - Triggers agent harness; collects `agent_env.json`
- [ ] **Agent-Run: LoRA** (`RUN_LORA_TESTS=1`) - Agent harness executes LoRA minimal tests
- [ ] **Agent-Run: Perf Smoke** (`RUN_PERF_SMOKE=1`) - Optional performance gate

### Documentation Build

- [ ] **Build Docs** (`SKIP_OPTIONAL=1`) - Produces `artifacts/docs` + `docs_manifest.sha`
- [ ] **Strict Docs** (`FAIL_ON_MISSING=1`) - Strict import gate (merge-to-main only)

### Baseline & Reporting

- [ ] **Capture Baseline** - Commits to `audit_artifacts/baselines/` (with rotation/archival)
- [ ] **Create Draft PR with Artifacts + Diffs** - Opens draft PR with matrix and manifest diffs

- [ ] **Multiple Copilot Coding Agent Sessions** (`COPILOT_MULTI_SESSION`)
  - ⚠️ **Default: disabled** — Only ONE Copilot session active at a time
  - When enabled: allows parallel Copilot sessions on different PRs
  - When disabled: sessions are queued and executed sequentially
  - **Caution:** Multiple sessions may cause merge conflicts on shared files

---

## 🔄 Workflow Execution Checklist

> **How the WEC gate works:** `workflow-execution-gate.yml` parses this section on every
> `pull_request_review` event. Filenames must match exactly (including underscores vs hyphens).
> **Always required** items fire automatically and cannot be skipped. **Opt-in** items are
> enabled by ticking `[x]`; unchecked items are reported as SKIPPED in the gate summary.

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] pre-merge-validation.yml — Pre-merge checks (always required)
- [x] comment-review-gate.yml — Comment review gate (always required)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)

### 🔄 Always Active — fire via push/workflow_run (Tier 2: need manual approval in Actions tab)
- [x] copilot-agent-checkin.yml — Agent check-in / S221 guard (fires on push)
- [x] copilot-agent-session-done.yml — Auto-post @copilot review after agent session (fires on workflow_run)
- [x] copilot-iterative-self-healing.yml — Iterative self-healing CI loop (fires on workflow_run — needs approval)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)

### ⚡ Auto-Approve
- [ ] auto-approve-workflows.yml — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🧪 Opt-In: Testing & Validation
- [ ] validate.yml — Validation Pipeline (detect-secrets, ruff, pre-commit, sync-tracked)
- [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
- [ ] mypy-baseline.yml — mypy type-check anti-regression gate
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
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
- [ ] auto-fix-common-issues.yml — Auto-fix common CI issues
- [ ] auto-fix-pr-check.yml — PR auto-fix check
- [ ] code-quality-coverage-suite.yml — Code quality & coverage suite
- [ ] audit-qa-suite.yml — Audit & QA Suite (Unified)
- [ ] template_lint.yml — Template / HTML Include Lint

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
- [ ] e-to-d-transition-gate.yml — E→D Transition Readiness Gate
- [ ] d-capable-promotion-gate.yml — D_CAPABLE Agent Promotion Gate
- [ ] qa-walkthrough.yml — QA Walkthrough Agent
- [ ] mcp-health.yml — MCP Health & Metrics Gate (src/mcp/ scope)

> **⚠️ HARDENED AGENT INSTRUCTION (non-negotiable):** This entire WEC block MUST be
> appended verbatim to **every** PR body update — including every `report_progress` call.
> **BEFORE writing any `prDescription`:** fetch the live PR body via the GitHub API and
> copy the WEC block exactly as it appears there — do NOT reconstruct it from this template.
> Preserve the **exact `[x]`/`[ ]` state** of every item as found in the live PR body.
> `auto-approve-workflows.yml` is **sticky**: if the maintainer checked `[x]` it stays `[x]`
> for the entire session; if the maintainer unchecks it `[ ]` that `[ ]` is preserved.
> Never flip any checkbox in either direction — only the maintainer may change checkbox state.

**Required if any files are deleted or moved:**

- [ ] **ADR drafted and linked** (`docs/arch/ADR-YYYYMMDD-brief-title.md`) - Architecture Decision Record created
- [ ] **Tombstone stubs added** - Use `docs/arch/tombstone_template.md` for every removed file
- [ ] **Evidence appended** - `.codex/evidence/archive_ops.jsonl` updated via archival API or manual entry
- [ ] **Pointer bundle generated** - For large removal sets (see `scripts/archival/select_and_compress.py`)
- [ ] **CHANGELOG updated** - Deprecations section includes removal details

**If any of the above cannot be satisfied, explain why and propose a remediation plan.**

---

## Scope

| Field | Value |
|-------|-------|
| **S‑IDs** | <!-- e.g., S‑17, S‑14, S‑15 --> |
| **Areas** | <!-- e.g., docs, tests, CI, detectors --> |

### Description
<!-- Provide a clear and concise description of the changes -->



---

## Verification Commands
<!-- Paste the commands you ran locally to validate changes -->

```bash
# Example verification commands:
# SKIP_OPTIONAL=1 bash scripts/docs_build.sh
# python scripts/space_traversal/audit_runner.py run
# python scripts/canonicalize_artifacts.py --out audit_artifacts/canonical_manifest.json
```text

---

## Artifacts (attach or paste SHAs)

```text
# Example:
# artifacts/docs_manifest.sha: <sha256>
# audit_run_manifest.json: <sha256>
# audit_artifacts/canonical_manifest.json: <sha256>
```text

---

## Determinism Proof

```text
# Paste canonical SHA equality proof from two runs:
# canonical[runA].sha == canonical[runB].sha ✅
```text

---

## Agent Environment (if Agent‑run)

```text
# If Agent-run jobs selected, attach: audit_artifacts/agent_env.json
# Or paste content here
```text

---

## Notes

<!-- Additional context, rotation notes, or baseline archival info -->

**Baseline Storage:** Baselines are stored under `audit_artifacts/baselines/` and will be rotated/archived if repository size grows.

---

### Related Issues
<!-- Link related issues using keywords: Fixes #123, Closes #456, Relates to #789 -->



### Testing
<!-- Describe the tests you ran and how to reproduce them -->
- [ ] Tests pass locally (`pytest`)
- [ ] Linting passes (`ruff check`, `black --check`)
- [ ] Type checking passes (`mypy`)
- [ ] Pre-commit hooks pass

### 🚨 Pre-Merge CI Verification (CRITICAL)
**DO NOT MERGE until ALL items are verified:**

- [ ] **All CI checks are GREEN** - No yellow/red status on required checks
- [ ] **Test Summary sentinel passed** - Final test status shows 0 failures
- [ ] **No flaky test failures** - If tests failed, verified they are not flaky
- [ ] **CodeQL passed** - Security scan completed without new alerts
- [ ] **Local verification done** - Ran `pytest tests/ -v` locally before merge

> ⚠️ **WARNING**: Merging with failing CI pollutes main branch and hides future regressions.
> If CI is failing, fix the issues or create a follow-up hotfix PR immediately after merge.

### Documentation
- [ ] Documentation has been updated (if needed)
- [ ] CHANGELOG.md has been updated (if applicable)
- [ ] Architecture docs updated (if applicable)

### Checklist
- [ ] My code follows the repository's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

### Screenshots (if applicable)
<!-- Add screenshots to help explain your changes -->



---

## Promotion / Readiness Checklist

**Note:** Fill this section out only for PRs that:
- Promote work from a rollout ring (for example `0D_base_`) toward `main`, OR
- Introduce / update reasoning-serving infra (deployment presets, pod YAMLs, etc.).

If this PR is only docs, bug fixes, or features, the section below does not apply.

---

### 1. Rollout ring and branch context
- Target rollout_ring from training artifacts (run_metadata.json):
  `rollout_ring = ____________________`

- Source branch / ring being promoted (e.g. `0D_base_`):
  `branch = ____________________`

- Target branch (e.g. `main`):
  `target = ____________________`

### 2. Survey snapshot
- Path to the committed survey snapshot under docs/status_updates/:
  `docs/status_updates/____________________.md`

Confirm this file:
- Describes orchestrators (TrainLoop / UnifiedTraining), reasoning harness trace capture, curricula config, evaluation preset, deployment preset.
- Captures any known code/docs mismatches.

### 3. Status report
Attach the output of:

```bash
python -m codex_ml.cli.codex_cli status-report \
  --run-metadata-dir runs/train_loop
```text

Paste JSON here (trim secrets if any):

```text
<status-report JSON here>
```text

This MUST include:
- `rollout_ring`
- `knobs.trace_mode`
- `knobs.curriculum_preset`
- `knobs.evaluation_preset`
- `knobs.deployment_preset`

### 4. Dry-run deploy proof
Provide the output (or summary) of:

```bash
python -m codex_ml.cli.codex_cli deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --dry-run \
  --run-metadata-dir runs/train_loop
```text

`codex_ml.cli.codex_cli deploy` MUST report success with `--dry-run`. If it printed `DEPLOYMENT BLOCKED`, stop and explain why.

Paste result / summary here:

```text
<deploy dry-run result>
```text

### 5. Evaluation preset sign-off
Check ONE:

- [ ] Offline evaluation preset passed and is reflected in `evaluation.json`.
- [ ] This PR does not modify model behavior; safe to merge without new evaluation.
      Rationale:
      ____________________________________________

### 6. Ack: This PR follows docs/ops/promotion_checklist.md
- [ ] I confirm I walked through `docs/ops/promotion_checklist.md` and this PR satisfies the required gates.

---

Reviewer notes / escalation contact:
- Owner / escalation contact from run_metadata.json: ____________________
- Additional context:
  ______________________________________________________

---

## Status v1.2 Compliance (if applicable)

**Note:** Fill this section if your PR includes status reports, schemas, or validation tooling changes.

### Validation Checklist
- [ ] Status example JSON validates against v1.2 schema (run `pytest -q tests/status/test_example_report_schema.py`)
- [ ] Hydra configs validated or explicitly N/A (run `python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml`)
- [ ] Security gates executed; artifacts uploaded
- [ ] CAP-/FIND-/PATCH-/REPRO- IDs consistent and cross-linked
- [ ] No secrets or sensitive data in diffs/logs

### Validation Commands Run
```bash
# Schema validation
pytest -q tests/status/test_example_report_schema.py

# Config validation
python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml

# Audit chain
python scripts/audit/build_integrity_chain.py
```text
