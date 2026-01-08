# [Plan]: Archival‑Aligned, Memory‑Saving Implementation (CI/Dev)  
> Generated: 2025-11-12 15:58:21 UTC | Author: mbaetiong

Ref Inputs:
- Dependency triage: docs/analysis/dependency_space_triage.md (Ref: f40ff2bbcacf567eef3dc6bd8c95733859b927dc)
- Environment scripts: scripts/setup.sh and scripts/maintenance.sh (rc5 evidence-enabled revisions)
- Archive policy and runbooks: docs/guides/codex_archive_runbook.md, docs/policies/archive-policy.md (redirect), docs/arch/_archive-policy/*
- Retention utilities: tools/purge_session_logs.py; src/codex_ml/utils/retention.py; docs/logging/log_rotation.md

---

## 1) Objectives & Success Criteria

| Goal | KPI | Target |
|------|-----|--------|
| Reduce CI storage pressure | Peak venv + wheels size | ≥ 2 GB reduction (baseline job) |
| Preserve functionality | Test pass rate | No net new failures in baseline unit suite; ML/eval suites pass/skip as designed |
| Governance alignment | Evidence & ADR | 100% of purge/segmentation steps logged to .codex/evidence/dependency_ops.jsonl; ADR required for major family removals |
| Deterministic CPU posture | Vendor residue | 0 residual nvidia-* or triton (allow-triton override supported) |
| Reversibility | Rollback | Single-commit revert per PR restores prior behavior |

---

## 2) Branching & PR Flow Strategy

| Stage | Branch | Purpose | Merge Direction |
|-------|--------|---------|-----------------|
| A | 0C_base_ | Introduce segmentation (requirements), CI session changes, evidence logging enablers | 0C_base_ ➜ 0D_base_ |
| B | 0D_base_ | Harden scripts (rc5), guardrails, env toggles, lock/prune logic, docs updates | 0D_base_ ➜ main |
| C | main | Consolidate, finalize ADRs/CHANGELOG, enable selective minimal augmentation | — |

Notes:
- Feature work lands in 0C_base_. Integrations and guardrails stabilize in 0D_base_. Fast-forward or merge commits to main once green and signed off.
- If a direct 0D_base_ ➜ main window is preferred, sequence A and B inside 0D_base_ before promoting.

---

## 3) Deliverables (By PR)

| PR | Branch | Deliverable | Files/Areas |
|----|--------|-------------|-------------|
| PR-A1 | 0C_base_ | Segmented requirement files | requirements-ml-cpu.txt; requirements-eval.txt; requirements-notebook.txt |
| PR-A2 | 0C_base_ | CI session split + markers | noxfile.py (tests/ml_tests/eval_tests); pytest markers in configs |
| PR-A3 | 0C_base_ | Vendor guard step | CI job pre-test step invoking vendor scan (fail-fast) |
| PR-B1 | 0D_base_ | Evidence-enabled scripts | scripts/setup.sh, scripts/maintenance.sh (rc5) with dependency_ops.jsonl logging |
| PR-B2 | 0D_base_ | Agents & docs updates | AGENTS.md, docs/analysis/dependency_space_triage.md, CHANGELOG.md |
| PR-B3 | 0D_base_ | ADRs for large families | docs/arch/ADR-2025-11-XX-dependency-segmentation.md |
| PR-C1 | main | Enable minimal augmentation by default in CPU posture | Default CODEX_CPU_MINIMAL=1 for CI; keep developer opt-in documented |

---

## 4) Technical Changes (Implementation Detail)

### 4.1 Segmented Installs (no baseline bloat)
- requirements-ml-cpu.txt: torch (CPU index), transformers, tokenizers, safetensors, accelerate, peft, sentencepiece.
- requirements-eval.txt: scipy, scikit-learn, statsmodels, pandas, eval metrics (lm-eval, rouge-score, sacrebleu, nltk).
- requirements-notebook.txt: jupyterlab, notebook, nbconvert, matplotlib.

Impact:
- Baseline dev spec stays lean; heavy families only installed in targeted nox sessions.

### 4.2 CI Session Matrix
- tests: unit without ML markers.
- ml_tests: installs requirements-ml-cpu.txt; run markers: requires_torch|requires_transformers.
- eval_tests: installs requirements-eval.txt; run markers: eval|metrics.
- Optional notebook docs build gated by SKIP_OPTIONAL=1 default.

### 4.3 Vendor Governance & Guard
- Early guard script: scans installed modules for nvidia-*, triton, torchtriton; fail-fast if CPU-only posture.
- Lock prune (optional, dry-run by default) removes GPU vendor specs from uv.lock; evidence recorded.

### 4.4 Evidence-First Deps Hygiene (rc5)
- setup.sh / maintenance.sh append JSONL records to .codex/evidence/dependency_ops.jsonl:
  - DEPENDENCY_VENDOR_SCAN (pre/post)
  - VENDOR_DETECTED_IN_SYNC_LOG
  - DEPENDENCY_VENDOR_PURGE (fallback/primary)
  - LOCK_PRUNE (dryrun/applied)
  - TORCH_PREINSTALL / TORCH_REINSTALL
  - MINIMAL_AUGMENT
- Actor: CODEX_EVIDENCE_ACTOR (defaults to $GITHUB_ACTOR, else “local”).

### 4.5 CPU Index & Minimal ML Mode
- PIP_INDEX_URL pinned to CPU wheels for torch.
- CODEX_CPU_MINIMAL=1 installs a constrained ML subset (no-deps transformers/tokenizers/safetensors/accelerate).

---

## 5) Governance: ADR, Archival, and Retention

| Action | Trigger | Required Artefact |
|--------|--------|-------------------|
| Remove from baseline dev spec (e.g., torch, jupyter, mlflow) | High-impact family | ADR referencing triage table & expected savings |
| Purge GPU vendor wheels | CPU-only CI | Evidence JSON lines (scan+purge), optional prune-request if code stubs touched |
| Documentation relocations | Paths or module imports change | Markdown pointer shim + Python shim (DeprecationWarning) |
| Session/Log retention | 30-day policy | Use tools/purge_session_logs.py; back up SQLite before purge (docs/logging/log_rotation.md) |

---

## 6) Environment Toggles Matrix

| Toggle | Default | Purpose |
|--------|---------|---------|
| CODEX_FORCE_CPU | 1 | Enforce CPU-only behavior |
| CODEX_VENDOR_PURGE | 1 | Enable vendor uninstall flow |
| CODEX_ABORT_ON_GPU_PULL | 0 | Hard-fail if GPU wheel detected |
| CODEX_CPU_MINIMAL | 0 (dev), 1 (CI recommended) | Constrained ML augmentation |
| CODEX_VENDOR_LOG_AGG | pre-sync | Prevent false-positive residue post-purge |
| CODEX_VENDOR_ENFORCE_LOCK_PRUNE | 0 | Strip GPU entries from lock (CI can enable) |
| CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN | 1 | Dry-run diff capture by default |
| CODEX_FAIL_ON_GPU_RESIDUE | 0 | Gate failure if residue remains |
| CODEX_DEPENDENCY_EVIDENCE_ENABLE | 1 | Append dependency_ops.jsonl records |

---

## 7) Memory & Storage Savings Budget

| Item | Disk Saved (est.) |
|------|-------------------|
| nvidia-* + triton removal | 1.0–1.2 GB+ |
| Jupyter stack defer | 180–250 MB |
| Torch absent in baseline | 180–220 MB |
| Scientific stack defer | 150–200 MB |
| Eval metrics defer | 30–45 MB |
| pandas/matplotlib defer | 65–95 MB |
| TOTAL (baseline gain) | ~2.2–2.5 GB |

---

## 8) Verification & Gates

| Check | Where | Pass Criteria |
|-------|-------|---------------|
| Vendor guard | Pre-test step | vendors=[] in CPU posture |
| Baseline tests | tests | Green; coverage retained or documented |
| ML tests | ml_tests | Pass or skip by markers |
| Eval tests | eval_tests | Pass or skip by markers |
| Evidence | scripts | dependency_ops.jsonl lines appended each event |
| Lock scan | scripts | GPU name count 0 after prune (or dry-run diff captured) |
| Residue strict | scripts | Optional gate: fail if any residue remains |
| Disk usage delta | CI | ≥ 2 GB reduction vs. prior |

---

## 9) Rollback Strategy

| Level | Action |
|-------|--------|
| PR-Level | Revert PR; restore prior requirements and CI sessions |
| Toggle-Level | Disable CODEX_CPU_MINIMAL / enforcement flags |
| Guard-Level | Set CODEX_VENDOR_LOG_ONLY_POLICY=ignore to suppress fallback |
| Evidence | Keep JSONL records; they are append-only and harmless on rollback |

---

## 10) Risk Assessment & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hidden transitive pulls | Disk bloat returns | Lock scan + vendor audit; set ABORT_ON_GPU_PULL=1 in CI |
| Test drift due to missing ML deps | False failures | Use markers/importorskip; install segmented sets in target sessions |
| Lock prune aggression | Build inconsistency | Default to dry-run; capture diff; apply only when validated |
| Developer friction | Onboarding overhead | Update AGENTS.md with clear session usage & toggles |

---

## 11) Documentation & Agents Update

- Update AGENTS.md with:
  - Dependency Retention & Segmentation table
  - Evidence stream: .codex/evidence/dependency_ops.jsonl
  - Session usage examples (nox -s ...)
  - Toggle matrix and purpose
  - Reference canonical archive policy location
- CHANGELOG.md entry summarizing segmentation and storage impact.
- Link docs/analysis/dependency_space_triage.md inside PR descriptions (Ref: f40ff2…).

---

## 12) Execution Timeline (Indicative)

| Week | Actions |
|------|---------|
| W1 | Land PR-A1/A2/A3 into 0C_base_; validate CI disk deltas; confirm tests & evidence logs |
| W2 | Promote to 0D_base_; land PR-B1/B2/B3; enable optional lock prune dry-run in CI; finalize ADR |
| W3 | Merge 0D_base_ ➜ main; set CODEX_CPU_MINIMAL=1 in CI; monitor recurrence and adjust toggles |

---

## 13) Acceptance Criteria (Go/No-Go)

- All baseline CI jobs pass; ML/eval isolated and green or skipped.
- Vendor residue absent; no unintended GPU wheels present.
- Evidence log populated for scan/purge/lock prune/torch steps.
- Disk usage improvement ≥ 2 GB at peak install.
- ADR for any family removed from baseline, linked in PR.

---

## 14) Post‑Merge Monitoring

| Signal | Source | Action Threshold |
|--------|--------|------------------|
| Vendor recurrence | maintenance summary JSON | 2+ consecutive occurrences ➜ investigate lock/index |
| Evidence growth | dependency_ops.jsonl size | Rotate weekly; archive per policy |
| CI time regression | job duration | +10% sustained ➜ review session composition |
| Developer pain | feedback/issues | Add helper scripts; revisit defaults |

---

## 15) Appendix: Files & Ownership

| File | Owner (Maintainer) | Notes |
|------|---------------------|------|
| scripts/setup.sh | Platform | rc5 adds evidence logging; lock prune evidence; minimal augment evidence |
| scripts/maintenance.sh | Platform | rc5 maintenance parity; preflight FIRST_SYNC_DONE=1 |
| noxfile.py | Platform/QA | Session split + markers |
| AGENTS.md | Docs/Platform | New sections per plan |
| requirements-*.txt | Platform | Segmented install surfaces |
| docs/analysis/dependency_space_triage.md | Platform | Triaged tables (Ref: f40ff2…) |
| docs/arch/ADR-2025-11-XX-*.md | Architecture | Dependency segmentation ADR |

---