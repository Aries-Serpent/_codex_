# Pull Request Template

> **Version:** 1.2.0  
> **Generated:** 2025-11-06  
> **Purpose:** Standardized PR workflow with required safety checks and optional capability controls

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

---

## ARCHIVAL OPERATIONS (if this PR removes or renames files)

**Required if any files are deleted or moved:**

- [ ] **ADR drafted and linked** (`docs/arch/ADR-YYYYMMDD-brief-title.md`) - Architecture Decision Record created
- [ ] **Tombstone stubs added** - Use `docs/arch/tombstone_template.md` for every removed file
- [ ] **Evidence appended** - `.codex/evidence/archive_ops.jsonl` updated via archival API or manual entry
- [ ] **Pointer bundle generated** - For large removal sets (see `scripts/archive/select_and_compress.py`)
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
```

---

## Artifacts (attach or paste SHAs)

```text
# Example:
# artifacts/docs_manifest.sha: <sha256>
# audit_run_manifest.json: <sha256>
# audit_artifacts/canonical_manifest.json: <sha256>
```

---

## Determinism Proof

```text
# Paste canonical SHA equality proof from two runs:
# canonical[runA].sha == canonical[runB].sha ✅
```

---

## Agent Environment (if Agent‑run)

```text
# If Agent-run jobs selected, attach: audit_artifacts/agent_env.json
# Or paste content here
```

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
```

Paste JSON here (trim secrets if any):

```text
<status-report JSON here>
```

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
```

`codex_ml.cli.codex_cli deploy` MUST report success with `--dry-run`. If it printed `DEPLOYMENT BLOCKED`, stop and explain why.

Paste result / summary here:

```text
<deploy dry-run result>
```

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
```
