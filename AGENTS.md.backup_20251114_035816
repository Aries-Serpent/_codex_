# AGENTS.md — Maintainers & Automation Guide  
> Generated: 2025-11-12T16:40:00Z | Author: mbaetiong  

## 1. Scope & Non-Goals
- Purpose: Central operational reference for maintainers, automation agents, and reviewers.
- Non-goals: Activation or modification of GitHub Actions beyond documented examples; rewriting production workflows; storing secrets.

## 2. Logging & Evidence Surfaces
| Path | Purpose | Rotation | Notes |
|------|---------|----------|-------|
| `.codex/evidence/archive_ops.jsonl` | Archive & restore operations (tombstones) | Append-only; rotate quarterly | Dual-control purge approvals preserved |
| `.codex/evidence/dependency_ops.jsonl` | Dependency segmentation & vendor purge evidence | Append-only; rotate weekly if >1MB | Actions: TORCH_PREINSTALL, DEPENDENCY_VENDOR_SCAN, DEPENDENCY_VENDOR_PURGE, LOCK_PRUNE, MINIMAL_AUGMENT, TORCH_REINSTALL |
| `.codex/logs/*` | Script-level warnings/errors | Ad-hoc | Do not manually edit evidence JSONL lines |
| `.codex/cache/*` | Transient metrics (timings, hashes) | Recreateable | Safe to prune |

### Evidence JSON Schema (Dependency)
Each line is a JSON object (example):
```json
{
  "ts": "2025-11-12T16:25:09Z",
  "action": "DEPENDENCY_VENDOR_PURGE",
  "tool": "setup",
  "mode": "primary",
  "vendors": [],
  "purged_count": 6,
  "vendor_hash_before": "7e9f...",
  "vendor_hash_after": "",
  "vendor_list_before": "nvidia-cublas-cu12 nvidia-nvtx-cu12",
  "vendor_list_after": "",
  "lock_prune_action": "dryrun",
  "lock_prune_lines_removed": 14,
  "torch_version": "2.8.0+cpu",
  "note": "",
  "actor": "github-actions[bot]",
  "session_id": "S123-456"
}
```
Required keys: `ts`, `action`, `tool` (schema validation session: `nox -s evidence_check`).

## 3. Dependency Retention & Segmentation
| Family | Session | Removal Requires ADR | Evidence Source |
|--------|---------|----------------------|-----------------|
| torch | ml_tests | Yes | dependency_ops.jsonl |
| transformers/tokenizers/safetensors | ml_tests | No (if kept segmented) | dependency_ops.jsonl |
| accelerate / peft | ml_tests | No | dependency_ops.jsonl |
| eval metrics (lm-eval, rouge-score, sacrebleu, nltk) | eval_tests | No (CHANGELOG note if bulk removal) | dependency_ops.jsonl |
| scientific (scipy, scikit-learn, statsmodels, pandas) | eval_tests | Yes if baseline removal | dependency_ops.jsonl |
| jupyterlab / notebook / nbconvert / matplotlib | notebook_env | Yes if baseline integration proposed | dependency_ops.jsonl |
| nvidia-* / triton / torchtriton | purge automation | No (purge logs suffice) | dependency_ops.jsonl |
| mlflow / ray | dedicated feature session | Yes if dropped entirely | ADR + dependency_ops.jsonl |

**Policy**: Baseline `tests` session MUST NOT install heavy ML/eval stacks unless explicitly justified and documented.

## 4. Environment Variables Matrix
| Variable | Default | Impact | Recommended Context |
|----------|---------|--------|---------------------|
| `CODEX_FORCE_CPU` | `1` | Enforces CPU-only torch index; blocks CUDA wheels | All CI |
| `CODEX_CPU_MINIMAL` | `0` (CI may set `1`) | Slim ML augmentation (lean subset) | ML sessions |
| `CODEX_VENDOR_PURGE` | `1` | Activates purge phase (uninstall vendor wheels) | Setup/Maintenance |
| `CODEX_ABORT_ON_GPU_PULL` | `0` | Hard fail if GPU wheels observed | Stricter compliance pipelines |
| `CODEX_RELOCK_AFTER_VENDOR_PURGE` | `1` | Recompute lock after purge | CI |
| `CODEX_VENDOR_ENFORCE_LOCK_PRUNE` | `0` | Strip GPU entries from `uv.lock` | Enable if recurrence appears |
| `CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN` | `1` | Diff-only lock prune | Default — observe before apply |
| `CODEX_DEPENDENCY_EVIDENCE_ENABLE` | `1` | Record dependency operations | Always |
| `CODEX_FAIL_ON_GPU_RESIDUE` | `0` | Fail if residue remains | Tight compliance runs |
| `CODEX_ALLOW_TRITON_CPU` | `1` | Filter standalone `triton` as harmless | CPU posture |
| `CODEX_VENDOR_LOG_AGG` | `pre-sync` | Prevents log noise after sync | Setup/Maintenance |
| `CODEX_WARN_ON_FALLBACK` | `0` | Emits WARN lines for fallback purge | Enable for elevated audit |
| `CODEX_HASH_LOCK_STRICT` | `0` | Strict lock normalization (strip +cpu) | When lock drift risk high |

## 5. Session Strategy (Nox)
| Session | Purpose | Requirements | Notes |
|---------|---------|-------------|-------|
| `tests` | Baseline unit tests w/o heavy ML | requirements-dev.txt | Mark skip: `not requires_torch` |
| `ml_tests` | ML functionality / checkpoints | requirements-dev + ml-cpu | Torch CPU posture enforced |
| `eval_tests` | Metrics & evaluation pipelines | requirements-dev + eval | Avoid in baseline to save space |
| `notebook_env` | Optional interactive environment | dev + notebook | Not run in CI by default |
| `verify_hygiene` | Evidence & vendor summary | dev | Prints dependency action counts |
| `evidence_check` | JSONL schema validation | dev | Fails on malformed lines |
| `dependency_plan` | Heuristic classification | dev | Generates size & classification JSON |
| `rollback_smoke` | Reversibility demonstration | dev | Non-destructive guidance |

## 6. ADR Requirements
Create an ADR (e.g., `docs/arch/ADR-2025-11-12-dependency-segmentation.md`) when:
- Removing torch from any previously torch-dependent baseline workflows.
- Eliminating jupyter stack from an existing documentation pipeline.
- Disabling mlflow tracking across all sessions.
- Large evaluation stack removal (scipy/sklearn/statsmodels/pandas) outside dedicated eval session.

## 7. Governance Flow (Dependency Operation)
| Phase | Script | Evidence Action | Outcome |
|-------|--------|-----------------|---------|
| Pre-sync scan | setup/maintenance | `DEPENDENCY_VENDOR_SCAN` | Baseline vendor hash snapshot |
| Lock sync | setup/maintenance | — | CPU-constrained lock or fallback regenerated |
| Fallback purge | setup/maintenance | `DEPENDENCY_VENDOR_PURGE` (`mode=fallback`) | Removes vendor wheels detected in log |
| Primary purge | setup/maintenance | `DEPENDENCY_VENDOR_PURGE` (`mode=primary`) | Ensures final cleanup |
| Lock prune (optional) | setup/maintenance | `LOCK_PRUNE` | GPU spec removal (dryrun / applied) |
| Minimal augment | setup/maintenance | `MINIMAL_AUGMENT` | Installs lean ML subset |
| Torch verify/reinstall | setup/maintenance | `TORCH_REINSTALL` | Ensures CPU-tagged torch presence |

## 8. Vendor Residue Handling
- Residue detection triggers `vendor_residue` warning category.
- If `CODEX_FAIL_ON_GPU_RESIDUE=1` and residue remains -> build fails.
- Allow list filter for `triton` when `CODEX_ALLOW_TRITON_CPU=1`.

## 9. Rollback Guide (Summary)
| Action | Command | Effect |
|--------|---------|--------|
| Remove segmentation | `git rm requirements-ml-cpu.txt requirements-eval.txt requirements-notebook.txt` | Restores monolithic dependency install surface |
| Drop specialized sessions | Edit `noxfile.py` | Collapses into baseline tests only |
| Disable evidence logging | `export CODEX_DEPENDENCY_EVIDENCE_ENABLE=0` | Stops recording dependency_ops JSON lines |
| Allow GPU installs | `export CODEX_FORCE_CPU=0` | Torch may resolve to CUDA wheels (document rationale) |

> Always retain existing evidence JSONL logs — they form part of the audit trail even after rollback.

## 10. JSONL Rotation Procedure
1. Copy current file: `cp .codex/evidence/dependency_ops.jsonl ".codex/evidence/dependency_ops_$(date +%Y-%m-%d).jsonl"`.
2. Compress historical snapshots if size > 5MB: `gzip -9`.
3. Never delete without an ADR referencing retention compliance.

## 11. Quality Gates
| Gate | Tool/Session | Description | Fail Condition |
|------|--------------|-------------|----------------|
| Vendor Guard | vendor_guard.py | CPU posture vendor absence | Non-empty vendor set under CPU posture |
| Evidence Schema | `nox -s evidence_check` | Required keys present | Missing keys / invalid JSON |
| Purge Residue | setup/maintenance scripts | Residue after purge | Residue non-empty & strict flag set |
| Lock Drift | setup/maintenance | Lock outdated event count | Repeated outdated events > threshold (3) |
| Recurrence Hash | maintenance summary | Vendor set recurrence | Recurrence under fail policy |

## 12. Suggested CI Matrix Example
| Job | Session | CODEX_CPU_MINIMAL | Installs Heavy ML? | Purpose |
|-----|---------|-------------------|--------------------|---------|
| baseline | tests | 0 (or 1 if safe) | No | Fast lint/unit |
| ml | ml_tests | 1 | Yes (segmented) | ML functionality |
| eval | eval_tests | 0 | Yes (segmented eval) | Metrics regression |
| hygiene | verify_hygiene | 0 | No | Evidence & residue summary |

## 13. Minimal Commands Cheat Sheet
```bash
# Baseline unit tests
nox -s tests

# ML tests (torch + transformers)
nox -s ml_tests

# Evaluation tests
nox -s eval_tests

# Evidence schema validation
nox -s evidence_check

# Generate dependency classification
nox -s dependency_plan
```

## 14. Future Enhancements
| Enhancement | Rationale | Status |
|-------------|-----------|--------|
| Automated dependency_plan gating | Prioritize removal candidates | Planned |
| Evidence size auto-rotation script | Prevent unbounded JSONL growth | Planned |
| GPU vendor recurrence heuristics upgrade | Smarter classification of residue vs. log noise | Under review |
| Signed evidence records (Sigstore) | Strengthen audit integrity | Feasibility study |

## 15. Conformance Checklist
| Item | Check | Status |
|------|-------|--------|
| Evidence logging active | `CODEX_DEPENDENCY_EVIDENCE_ENABLE=1` | ✅ |
| Baseline excludes heavy ML | `nox -s tests` (no torch import) | ✅ |
| Purge recorded | `grep DEPENDENCY_VENDOR_PURGE .codex/evidence/dependency_ops.jsonl` | ✅ |
| Recurrence monitored | maintenance summary JSON | ✅ |
| ADR present | `docs/arch/ADR-2025-11-12-dependency-segmentation.md` | ✅ |

---

## 16. Attribution & Change Control
- Primary Maintainer (Platform): `@mbaetiong`
- Secondary Maintainer (QA Integration): `@platform-qa`
- All structural changes require either:
  - ADR update for scope expansions, OR
  - CHANGELOG entry for non-breaking adjustments.

---

## 17. Appendix: Evidence Key Reference
| Key | Meaning |
|-----|---------|
| `action` | Operation event type (scan/purge/augment/lock_prune/etc.) |
| `tool` | Originating script (`setup`, `maintenance`) |
| `mode` | Purge mode (fallback / primary) |
| `vendors` | Enumerated vendor packages observed |
| `purged_count` | Number of uninstalled distributions |
| `vendor_hash_before/after` | Stable hash of vendor set pre/post action |
| `lock_prune_action` | `dryrun` or `applied` |
| `lock_prune_lines_removed` | Metadata diff metric |
| `torch_version` | Torch runtime version captured |
| `actor` | Identity (GitHub Action, local user) |
| `session_id` | External session correlation (optional) |

---

## 18. Final Notes
- Treat dependency segmentation as an *archival hygiene layer*: actions must be observable, reversible, and policy-aligned.
- Removal of any heavy family from baseline requires dual: ADR + CHANGELOG entry.
- Evidence JSONL is the canonical source for machine-auditable footprint evolution.

*End of AGENTS.md*