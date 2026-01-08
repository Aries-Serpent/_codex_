# Ops: Dependency Segmentation Rollback
> Generated: 2025-11-12 16:58:19 UTC | Author: mbaetiong

## Overview
This guide describes how to revert the dependency segmentation rollout quickly and safely, while preserving audit evidence.

## Rollback Steps

| Step | Command | Effect | Notes |
|------|---------|--------|-------|
| 1 | git rm requirements-ml-cpu.txt requirements-eval.txt requirements-notebook.txt | Remove segmented install surfaces | Reversible via git revert |
| 2 | Edit noxfile.py | Remove sessions: ml_tests, eval_tests, notebook_env | Keep helper sessions if desired |
| 3 | CI workflow | Switch matrix back to single baseline job | Ensure markers don’t exclude tests |
| 4 | Evidence logging | export CODEX_DEPENDENCY_EVIDENCE_ENABLE=0 | Not recommended; you lose audit trail |
| 5 | CPU posture | export CODEX_FORCE_CPU=0 | Allows CUDA wheels (document rationale) |

## Toggle Reference

| Toggle | Default | Effect | Risk |
|--------|---------|--------|------|
| CODEX_VENDOR_PURGE | 1 | Uninstalls vendor wheels | Turning off Phase 5 reintroduce bloat |
| CODEX_DEPENDENCY_EVIDENCE_ENABLE | 1 | Appends evidence JSONL lines | Disabling removes auditability |
| CODEX_FORCE_CPU | 1 | CPU-only torch posture | Setting 0 allows CUDA pulls |
| CODEX_ABORT_ON_GPU_PULL | 0 | Fail on vendor detection | Enable for strict pipelines |
| CODEX_VENDOR_ENFORCE_LOCK_PRUNE | 0 | Removes GPU specs from lock | Prefer dry-run first |
| CODEX_VENDOR_ENFORCE_LOCK_PRUNE_DRYRUN | 1 | Diff-only lock prune | Safe observation mode |

## Evidence Retention
- Never delete `.codex/evidence/dependency_ops.jsonl`.
- Rotate by copying and compressing older snapshots:
  - cp .codex/evidence/dependency_ops.jsonl ".codex/evidence/dependency_ops_$(date +%F).jsonl"
  - gzip -9 .codex/evidence/dependency_ops_$(date +%F).jsonl

## Validation After Rollback

| Check | Command | Expectation |
|-------|---------|-------------|
| Test run | pytest -q | Baseline green |
| Vendor guard | python scripts/vendor_guard.py | vendors=[] |
| Disk usage | ./scripts/disk_snapshot.sh | Reasonable footprint |
| Evidence presence | ls .codex/evidence | Historical logs preserved |

## Notes
- Keep ADRs and CHANGELOG entries intact; add a short note explaining rollback scope and reason.
- Consider a follow-up ADR if rollback is long-lived.