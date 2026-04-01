# Pull Request Template

> **Version:** 1.5.0  
> **Generated:** 2026-04-01  
> **Purpose:** Standardized PR workflow with Copilot continuation support, safety checks, and optional capability controls

---

## 🤖 COPILOT CONTINUATION (Auto-Generated)

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
  <!-- ↑ Checking this box enables ALL components below for the full self-healing loop: -->
  - [ ] **Phase 1 — Triage** (`should-escalate` job): detects failure type, determines whether to escalate, resolves PR number and branch
  - [ ] **Phase 2 — RCA Prompt Build** (`post-copilot-prompt` job): runs `scripts/ci/ci_rescue.py`, classifies failure category (test / lint / type / coverage / security / build / ci-pattern / general), builds context-rich `@copilot` prompt
  - [ ] **Phase 3 — Comment Post / Upsert**: posts (or idempotently updates) the `@copilot` rescue prompt as a PR comment; one prompt per commit SHA to avoid duplicate noise
  - [ ] **Phase 4 — Cognitive Brain Update**: records escalation pattern in cognitive brain DB; increments `COGNITIVE_BRAIN_SESSION_NUMBER` repository variable
  - [ ] **Phase 5 — Iterative Loop**: on next push after Copilot addresses the comment, loop restarts from Phase 1 until all concerns resolve or cognitive-brain objectives normalize
  - [ ] **Triggered by**: any of `Pre-Merge Validation`, `Iterative Self-Healing CI`, `mypy Baseline`, `Test — RAG Pipeline`, `Security Scan`, `Nightly CodeQL Alert Triage`, `Deferral Language Gate`, `CI Pattern Pipeline` completing with `failure` or `timed_out` conclusion

### ⚡ Auto-Approve
- [ ] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

> Instructions for Copilot Agent: During wrap-up, check ONLY the workflows needed for
> this session. Unchecked workflows will be SKIPPED by the gate.

**Required if any files are deleted or moved:**

- [ ] **ADR drafted and linked** (`docs/arch/ADR-YYYYMMDD-brief-title.md`) - Architecture Decision Record created
- [ ] **Tombstone stubs added** - Use `docs/arch/tombstone_template.md` for every removed file
- [ ] **Evidence appended** - `.codex/evidence/archive_ops.jsonl` updated via archival API or manual entry
- [ ] **Pointer bundle generated** - For large removal sets (see `scripts/archival/select_and_compress.py`)
- [ ] **CHANGELOG updated** - Deprecations section includes removal details

**If any of the above cannot be satisfied, explain why and propose a remediation plan.**

---

## 🔬 PDA Loop + AfterMath Plan: Reduce mypy Baseline Below 297

> **Scope**: 39 remaining `# type: ignore[assignment]` comments in `src/training/` — all are
> optional-package sentinel guards (`np = None`, `torch = None`, `npt = Any`, etc.).
> These are **intentionally needed** when the packages are installed in full environments,
> but the isolated-venv model treats them as unused-ignore. This plan tracks safe removal.
>
> **Current baseline**: 297 errors · **Target**: ≤ 258 errors (−39)

### 📐 PDA Loop Structure

**Observe** → **Orient** → **Decide** → **Act** cycle, with AfterMath verification after each iteration.

#### Iteration 1 — Sentinel type annotation (estimated −12 errors)
- [ ] **Observe**: Run `python scripts/ci/mypy_baseline.py` in isolated venv; collect the 39 `[assignment]` error locations
- [ ] **Orient**: Classify each sentinel by package — `np`/`npt` (numpy), `torch`/`nn`/`autocast`/`GradScaler` (PyTorch), `fcntl` (stdlib), `Dataset` (datasets), `CheckpointManager`/`_Accelerator` (internal)
- [ ] **Decide**: For each sentinel, determine if the variable can be typed with `Optional[type]` (e.g. `np: Optional[ModuleType] = None`) instead of using `Any` assignment
- [ ] **Act**: Replace `np = None  # type: ignore[assignment]` with `np: Optional[types.ModuleType] = None` where the variable is a module sentinel; import `types` and `Optional` at top of file
- [ ] **AfterMath**: Run baseline; verify error count decreased; confirm ruff still passes

#### Iteration 2 — `TYPE_CHECKING` guard pattern (estimated −15 errors)
- [ ] **Observe**: Identify sentinels where the type is a class from the optional package (e.g. `torch.Tensor`, `torch.nn.Module`, `GradScaler`, `Dataset`)
- [ ] **Orient**: Check if the package ships type stubs that define these types — if yes, use `if TYPE_CHECKING:` guard
- [ ] **Decide**: For numpy (`npt`), torch (`Tensor`, `nn`, `GradScaler`, `autocast`), accelerate (`_Accelerator`), datasets (`Dataset`) — all have stubs; `TYPE_CHECKING` guard is safe
- [ ] **Act**:
  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      import numpy as np
      import numpy.typing as npt
      import torch
      import torch.nn as nn
  ```
  Replace `torch = None  # type: ignore[assignment]` with conditional import; use `"torch"` string annotation where needed at runtime
- [ ] **AfterMath**: Run baseline; verify both isolated-venv AND full-package mypy pass (test in CI with `[assignment]` errors resolved)

#### Iteration 3 — Remaining `[assignment]` cases (estimated −12 errors)
- [ ] **Observe**: After iterations 1 and 2, run baseline to identify any residual `[assignment]` errors
- [ ] **Orient**: For complex cases (`torch = types.SimpleNamespace(...)`, `OmegaConf.to_container(...)` returning `Any`), analyze if the type annotation can be widened
- [ ] **Decide**: Widen return type annotation where the actual type is provably correct (e.g. `to_container` → cast to `dict[str, Any]`); add `cast()` where assignment type truly diverges
- [ ] **Act**: Apply `cast(dict[str, Any], OmegaConf.to_container(...))` and similar targeted fixes
- [ ] **AfterMath**: Confirm baseline ≤ 258; update `.mypy_baseline`; update CHANGELOG

### 📊 Tracking Table

| File | `[assignment]` count | Iteration | Status |
|------|---------------------|-----------|--------|
| `src/training/engine_hf_trainer.py` | ~5 | 1, 2 | ⏳ |
| `src/training/data_utils.py` | ~6 | 1, 2 | ⏳ |
| `src/training/trainer.py` | ~4 | 2 | ⏳ |
| `src/training/checkpoint_manager.py` | ~2 | 1 | ⏳ |
| `src/training/functional_training.py` | ~2 | 3 | ⏳ |
| `src/training/checkpointing.py` | ~1 | 2 | ⏳ |
| `src/training/datasets.py` | ~1 | 2 | ⏳ |
| `src/training/seed_utils.py` | ~1 | 1 | ⏳ |
| `src/training/simple_trainer.py` | ~1 | 2 | ⏳ |
| `src/training/cache.py` | ~2 | 1 | ⏳ |
| `src/training/config.py` | ~1 | 3 | ⏳ |
| `src/training/accelerate_init_guard.py` | ~1 | 2 | ⏳ |

### 🔁 AfterMath Gate (run after every iteration commit)

```bash
# 1. Isolated venv check (must equal new target)
python3 -m venv /tmp/mypy-venv --clear
/tmp/mypy-venv/bin/pip install "mypy>=1.8.0" types-PyYAML types-requests
/tmp/mypy-venv/bin/python scripts/ci/mypy_baseline.py --require-baseline

# 2. Ruff must still pass
python -m ruff check .

# 3. Sync tracked files (baseline hash)
python3 scripts/ci/sync_tracked_files.py --fix
```

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
