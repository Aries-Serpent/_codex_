# [PromptBundle]: Dependency Segmentation & Archival Alignment Rollout  
> Generated: 2025-11-12 16:13:40 UTC | Author: mbaetiong  

This bundle provides READY-TO-COPY prompts for GitHub Copilot Agents to implement the archival-aligned, memory-saving dependency segmentation strategy across branches `0C_base_`, `0D_base_`, and `main` in the `Aries-Serpent/_codex_` repository.

---

## 🔧 Implementation Targets

| File | Owner (Maintainer) | Notes |
|------|---------------------|------|
| scripts/setup.sh | Platform | rc5 adds evidence logging; lock prune evidence; minimal augment evidence |
| scripts/maintenance.sh | Platform | rc5 parity + FIRST_SYNC_DONE=1 preflight |
| noxfile.py | Platform/QA | Add session split + markers |
| AGENTS.md | Docs/Platform | Add retention, segmentation, evidence logging guidance |
| requirements-ml-cpu.txt | Platform | Segmented ML install surface |
| requirements-eval.txt | Platform | Segmented evaluation install surface |
| requirements-notebook.txt | Platform | Optional interactive surface |
| docs/analysis/dependency_space_triage.md | Platform | Reference triage (Ref: f40ff2bbcacf567eef3dc6bd8c95733859b927dc) |
| docs/arch/ADR-Previous Cycle-11-XX-dependency-segmentation.md | Architecture | Justifies segmentation & governance hooks |
| .codex/evidence/dependency_ops.jsonl | Platform | New evidence stream (append-only) |

---

## 🚀 Branching & Flow

| Stage | Branch | Purpose | Merge Direction |
|-------|--------|---------|-----------------|
| A | 0C_base_ | Segmentation (requirements), nox CI session changes, evidence stream enablement | 0C_base_ ➜ 0D_base_ |
| B | 0D_base_ | Harden scripts, guardrails, lock/prune logic, ADR/docs | 0D_base_ ➜ main |
| C | main | Consolidation, minimal augmentation defaults, CHANGELOG finalization | — |

---

## 🎯 Objectives & Success Criteria

| Goal | KPI | Target |
|------|-----|--------|
| Reduce CI storage pressure | Peak venv + wheels size | ≥ 2 GB reduction |
| Preserve functionality | Baseline test pass rate | No new failures; ML/eval isolated |
| Governance alignment | Evidence & ADR coverage | 100% logged + ADR for major families |
| Deterministic CPU posture | Vendor residue | 0 nvidia-* or triton (unless allowed) |
| Reversibility | Rollback complexity | Single revert per PR |

---

## 📑 General Usage Instructions

Copy one prompt at a time into a GitHub Copilot Agent or multi-step automation runner.  
Do not batch unrelated prompts. Maintain branch isolation per stage.  
Prompts include “Goal”, “Constraints”, and “Deliverables”.  
Where modifications occur, ask Copilot to generate diffs respecting existing structure, preserving comments, and adding version notes.

---

## 🧩 STAGE A PROMPTS (Branch: 0C_base_)

### PROMPT A1 — Create Segmented Requirements
```text
Goal: Introduce dependency segmentation to reduce baseline install size.
Branch: 0C_base_
Files to add (new):
  - requirements-ml-cpu.txt
  - requirements-eval.txt
  - requirements-notebook.txt
Content specs:
  - requirements-ml-cpu.txt:
      torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
      transformers==4.56.0
      tokenizers==0.22.0
      safetensors==0.6.2
      accelerate==0.29.0
      peft==0.17.1
      sentencepiece==0.2.1
  - requirements-eval.txt:
      scikit-learn==1.7.2
      scipy==1.16.2
      statsmodels==0.14.5
      pandas==2.3.2
      lm-eval==0.4.9.1
      rouge-score==0.1.2
      sacrebleu==2.5.1
      nltk==3.9.2
  - requirements-notebook.txt:
      jupyterlab==4.4.9
      notebook==7.4.7
      nbconvert==7.16.6
      matplotlib==3.10.6
Add trailing newline; no comments except concise header comment.
Deliverable: Commit new files and reference them in plan summary in PR description.
```text

### PROMPT A2 — Update noxfile.py for Session Split
```text
Goal: Add three nox sessions: tests, ml_tests, eval_tests.
Branch: 0C_base_
Modify existing noxfile.py (create if absent).
Rules:
  - tests session installs requirements-dev.txt only and runs pytest -m "not requires_torch" -q
  - ml_tests session installs requirements-dev.txt + requirements-ml-cpu.txt, runs pytest -m "requires_torch or requires_transformers" -q
  - eval_tests session installs requirements-dev.txt + requirements-eval.txt, runs pytest -m "eval or metrics" -q
  - Add helper session 'list_sessions' that prints available session names.
  - Ensure marker usage is documented in a comment block.
Deliverable: Updated noxfile.py with Python 3.11+ interpreter fallback logic if unspecified.
```text

### PROMPT A3 — Introduce Vendor Guard Script
```text
Goal: Add early fail-fast vendor module scan for CI.
Branch: 0C_base_
Add file: scripts/vendor_guard.py
Behavior:
  - Scans pkgutil.iter_modules() for names starting nvidia- or in {triton, torchtriton}.
  - Emits JSON to stdout: { "action": "DEPENDENCY_VENDOR_SCAN", "vendors": [], "ts": UTC }
  - Exit 1 if vendors found AND CODEX_FORCE_CPU=1.
  - Respect env CODEX_ALLOW_TRITON_CPU=1 to filter 'triton'.
Include shebang + executable permission note in script header.
Deliverable: File plus reference in workflow docs (comment at top).
```text

### PROMPT A4 — Enable Evidence Stream (Dependency Ops)
```text
Goal: Create empty evidence file for dependency operations.
Branch: 0C_base_
Path: .codex/evidence/dependency_ops.jsonl
Action:
  - If directory absent, add placeholder .gitkeep where needed.
  - Add initial comment line in PR description (not in file) explaining append-only policy.
Deliverable: Evidence file committed (empty).
```text

### PROMPT A5 — Update AGENTS.md (Retention & Segmentation Section)
```text
Goal: Append new section to AGENTS.md.
Branch: 0C_base_
Content to append (after last existing section):
  ## Dependency Retention & Segmentation
  | Family | Session | Removal Requires ADR | Evidence |
  |--------|---------|----------------------|---------|
  | torch | ml_tests | Yes | dependency_ops.jsonl |
  | jupyterlab | notebook | Yes | dependency_ops.jsonl |
  | mlflow | ml_tests/tracking | Yes (if disabling) | dependency_ops.jsonl |
  | nvidia-* | baseline purge | No (purge logs only) | dependency_ops.jsonl |
  | eval metrics | eval_tests | No (CHANGELOG note if bulk) | dependency_ops.jsonl |
  Evidence log: `.codex/evidence/dependency_ops.jsonl`
Deliverable: Updated file; preserve existing formatting and attribution headers.
```text

### PROMPT A6 — Adjust CI Workflow (If Present)
```text
Goal: Insert vendor guard + session matrix.
Branch: 0C_base_
File: .github/workflows/ci.yml
Changes:
  - Add step before Python install: Run vendor_guard.py (ignore if file missing).
  - Add job matrix: baseline (tests), ml (ml_tests), eval (eval_tests).
  - Export CODEX_FORCE_CPU=1 in all jobs; CODEX_CPU_MINIMAL=1 only in ml job.
  - Cache .venv optionally; avoid caching large ML wheels in baseline.
Deliverable: Workflow diff with comments marking new segmentation logic.
```text

---

## 🔐 STAGE B PROMPTS (Branch: 0D_base_)

### PROMPT B1 — Integrate rc5 Updated scripts/setup.sh
```text
Goal: Replace scripts/setup.sh with rc5 evidence-enabled version.
Branch: 0D_base_
Pull in rc5 modifications:
  - Evidence writer for dependency_ops.jsonl
  - Actions: TORCH_PREINSTALL, DEPENDENCY_VENDOR_SCAN, VENDOR_DETECTED_IN_SYNC_LOG, DEPENDENCY_VENDOR_PURGE, LOCK_PRUNE, MINIMAL_AUGMENT, TORCH_REINSTALL
Add version header line: Version: 5.5.2-rc5 (if not already).
Ensure safe idempotent path creation (.codex/evidence).
Deliverable: Full file replacement; keep executable bit.
```text

### PROMPT B2 — Integrate rc5 Updated scripts/maintenance.sh
```text
Goal: Mirror rc5 parity with setup.sh for maintenance script.
Branch: 0D_base_
Add evidence logging identical schema.
Ensure FIRST_SYNC_DONE=1 logic retained to avoid residue false positives.
Add MINIMAL_AUGMENT evidence when CODEX_CPU_MINIMAL=1 invoked.
Deliverable: scripts/maintenance.sh updated and consistent with setup.sh patterns.
```text

### PROMPT B3 — Add ADR for Dependency Segmentation
```text
Goal: Create architectural decision record.
Branch: 0D_base_
File: docs/arch/ADR-Previous Cycle-11-12-dependency-segmentation.md
Sections:
  - Status: Accepted
  - Context: Disk pressure, optional ML, classification table summary
  - Decision: Segmentation + evidence logging + ADR triggers
  - Consequences: +Space relief / -Need for session awareness
  - Provenance: Link Ref: f40ff2bbcacf567eef3dc6bd8c95733859b927dc
  - Compliance: Evidence JSONL and archive runbook alignment
Deliverable: New ADR in canonical format.
```text

### PROMPT B4 — Update docs/analysis/dependency_space_triage.md (Ref & rc5 note)
```text
Goal: Append implementation status footer.
Branch: 0D_base_
Add section at end:
  ### Implementation Status (rc5)
  - Segmented requirements: added
  - Evidence stream: active
  - setup.sh & maintenance.sh: rc5 instrumentation
  - Nox session matrix: live
  - ADR: included (link)
Deliverable: Minimal, append-only update; preserve original reference.
```text

### PROMPT B5 — CHANGELOG Entry
```text
Goal: Document segmentation rollout.
Branch: 0D_base_
If CHANGELOG.md exists, append:
  ## 2025-11-12
  - Dependency segmentation (requirements-ml-cpu/eval/notebook)
  - Evidence logging introduced (.codex/evidence/dependency_ops.jsonl)
  - rc5 environment scripts (setup.sh, maintenance.sh)
  - Added nox session matrix (tests/ml_tests/eval_tests)
  - ADR: dependency segmentation
Deliverable: Updated CHANGELOG.md; maintain existing formatting style.
```text

### PROMPT B6 — Introduce Optional Lock Prune Enforcement
```text
Goal: Add CODEX_VENDOR_ENFORCE_LOCK_PRUNE=1 path handling explanation.
Branch: 0D_base_
Files:
  - scripts/setup.sh
  - scripts/maintenance.sh
Add inline comment near lock prune function explaining dry-run vs applied behavior and recommended CI usage.
Deliverable: Comment insertion only; no logic changes beyond doc clarity.
```text

### PROMPT B7 — Add Verification Script (Optional)
```text
Goal: Create scripts/verify_dependency_hygiene.py
Branch: 0D_base_
Behavior:
  - Reads dependency_ops.jsonl
  - Summarizes counts per action and unique vendor sets
  - Exits non-zero if DEPENDENCY_VENDOR_PURGE occurred but vendor_set_after not empty
Deliverable: New script with argparse; lightweight (stdlib only).
```text

---

## 🧩 STAGE C PROMPTS (Branch: main)

### PROMPT C1 — Enable CODEX_CPU_MINIMAL=1 Default in CI
```text
Goal: Turn on minimal augmentation by default for baseline & ml jobs.
Branch: main
Modify .github/workflows/ci.yml:
  - Add env: CODEX_CPU_MINIMAL=1 for baseline (tests) only if not breaking torch markers; keep ml job explicit.
  - Confirm tests pass without installing full torch extras unless needed.
Deliverable: Workflow update; include rationale comment.
```text

### PROMPT C2 — Final Consolidation & Cleanup
```text
Goal: Remove any temporary comments or experimental flags no longer needed.
Branch: main
Actions:
  - Confirm any DEBUG-only artifacts not committed.
  - Ensure vendor_audit scripts referenced consistently or disabled if unused.
Deliverable: Diff removing outdated TODO markers.
```text

### PROMPT C3 — Post-Merge Monitoring Guidance (Docs)
```text
Goal: Add monitoring guidance snippet.
Branch: main
Append to docs/analysis/dependency_space_triage.md:
  ### Post-Merge Monitoring
  | Metric | Source | Threshold |
  |--------|--------|-----------|
  | Vendor Recurrence | maintenance_summary.json | Trigger ADR review at 2 consecutive recurrences |
  | Evidence Growth | dependency_ops.jsonl size | Rotate weekly if >1MB |
  | Disk Relief | CI artifact logs | Maintain ≥2GB saved baseline |
Deliverable: Append section; preserve formatting.
```text

### PROMPT C4 — Rollback Readiness Doc
```text
Goal: Create docs/ops/dependency_segmentation_rollback.md
Branch: main
Content:
  - How to revert segmentation (delete requirements-*.txt, restore original noxfile.py)
  - How to disable evidence logging (CODEX_DEPENDENCY_EVIDENCE_ENABLE=0)
  - How to allow GPU (unset CODEX_FORCE_CPU or set vendor policy ignore)
Deliverable: New doc; concise; table of toggle effects.
```text

---

## ✅ VERIFICATION PROMPTS

### PROMPT V1 — Disk Usage Snapshot
```text
Goal: Add script to record disk footprint post-install.
Branch: 0D_base_
File: scripts/disk_snapshot.sh
Content:
  #!/usr/bin/env bash
  set -euo pipefail
  du -sh .venv || true
  du -sh "$(pwd)" | awk '{print "[disk-root] "$0}'
  pip list --format=columns | grep -E 'torch|triton|nvidia' || true
Deliverable: New script; referenced in CI if needed.
```text

### PROMPT V2 — Evidence Consistency Check
```text
Goal: Validate evidence JSON lines schema.
Branch: 0D_base_
File: scripts/check_dependency_evidence.py
Behavior:
  - Load dependency_ops.jsonl
  - Ensure required keys: ts, action, tool
  - Print summary counts per action
  - Exit 2 if any malformed line
Deliverable: New script; stdlib only.
```text

---

## 🔄 ROLLBACK PROMPTS

### PROMPT R1 — Rollback Segmentation
```text
Goal: Provide revert patch (create rollback script).
Branch: main (if needed)
File: scripts/rollback_segmentation.sh
Behavior:
  - Removes requirements-ml-cpu.txt, requirements-eval.txt, requirements-notebook.txt
  - Strips ml_tests/eval_tests sessions from noxfile.py
  - Leaves evidence log intact (append-only)
  - Echo explanation lines
Deliverable: New script; idempotent (checks existence).
```text

### PROMPT R2 — Disable Vendor Purge & Evidence
```text
Goal: Document toggling off governance features.
Branch: main
Update docs/ops/dependency_segmentation_rollback.md:
  - Add table: Toggle | Effect | Risk
    CODEX_VENDOR_PURGE=0 | No uninstall | Residue & disk bloat possible
    CODEX_DEPENDENCY_EVIDENCE_ENABLE=0 | No logging | Loss of audit trail
Deliverable: Append to doc.
```text

---

## 🔧 ENHANCEMENT PROMPTS (Optional Future Iterations)

### PROMPT E1 — Add dependency_plan Generator
```text
Goal: Create script to score dependencies similar to archive plan.
Branch: 0D_base_
File: tools/dependency_plan.py
Inputs: pip freeze, static code import frequency (rudimentary grep).
Output: JSON with entries: name, size_estimate, import_hits, classification (Keep|Optional|Defer|Purge).
Deliverable: New tool; include README snippet at top of file.
```text

### PROMPT E2 — CI Artifact: dependency_summary.json
```text
Goal: Persist summary after setup.sh execution.
Branch: 0D_base_
Modify setup.sh & maintenance.sh:
  - After summary JSON creation, copy to artifacts/dependency_summary.json
Deliverable: Small patch (ensure artifacts/ exists).
```text

---

## 🧪 TEST AUGMENTATION PROMPTS

### PROMPT T1 — Add Marker Definitions
```text
Goal: Ensure markers exist.
Branch: 0C_base_
File: configs/development/pytest.ini (or create)
Add:
  [pytest]
  markers =
    requires_torch: tests needing torch
    requires_transformers: tests needing transformers
    eval: evaluation-only tests
    metrics: metric calculation tests
Deliverable: File updated or created.
```text

### PROMPT T2 — Add Shim Import Tests
```text
Goal: Validate optional dependency shims.
Branch: 0D_base_
Add test file: tests/shims/test_sentencepiece_shim.py
Test:
  - If sentencepiece missing, import path uses adapter fallback without error.
  - Mark with requires_transformers if dependency needed.
Deliverable: New test file.
```text

---

## 📜 PROMPT FOR FINAL CONSOLIDATION SUMMARY (PR to main)

```text
Goal: Create PR description summarizing rollout.
Include:
  - Space saved (report du -sh comparisons)
  - Evidence ops count summary
  - ADR link
  - Residue confirmations (0 vendor)
  - Future enhancements list (dependency_plan, artifact rotation)
Request:
  - Reviewers confirm no baseline regressions
  - Approvers sign off on ADR compliance
```text

---

## 🧠 QUICK COPY MASTER PROMPT (All-in-One Orchestrator)

Use ONLY for automated multi-step agent environment; otherwise apply granular prompts.

```text
You are an orchestration agent. Execute staged rollout for dependency segmentation per plan:
Stage A (branch 0C_base_):
  - Add requirements-ml-cpu.txt, requirements-eval.txt, requirements-notebook.txt with specified contents.
  - Update noxfile.py with tests/ml_tests/eval_tests sessions.
  - Add scripts/vendor_guard.py (scan modules, JSON output, exit on vendor detection).
  - Create .codex/evidence/dependency_ops.jsonl (empty).
  - Append segmentation section to AGENTS.md.
  - Patch .github/workflows/ci.yml with matrix + vendor guard step.

Stage B (branch 0D_base_):
  - Replace scripts/setup.sh and scripts/maintenance.sh with rc5 evidence-enabled versions.
  - Add ADR docs/arch/ADR-Previous Cycle-11-12-dependency-segmentation.md.
  - Append implementation status section to docs/analysis/dependency_space_triage.md.
  - Update CHANGELOG.md with segmentation entry.
  - Add scripts/verify_dependency_hygiene.py and scripts/check_dependency_evidence.py.
  - Optional: tools/dependency_plan.py generator.

Stage C (branch main):
  - Enable CODEX_CPU_MINIMAL=1 default in CI baseline job.
  - Add docs/ops/dependency_segmentation_rollback.md.
  - Append post-merge monitoring section to the triage doc.
Validation:
  - Ensure dependency_ops.jsonl receives all evidence actions.
  - Vendor residue empty post-purge.
  - Disk usage reduced ≥ 2 GB compared to prior baseline.

Output:
  - Provide diffs for every changed file.
  - Summarize actions in final consolidated PR description.
Rollback readiness:
  - Create scripts/rollback_segmentation.sh idempotent revert path.

Execute now, maintaining comments and version headers. Do not remove historical change notes.
```text

---

## 🏁 Closing Note

All prompts intentionally preserve reversibility, auditability, and operational clarity.  
Proceed stage-wise; avoid collapsing stages to maintain governance checkpoints.

*End of Prompt Bundle.*