# Validation: Dependency Segmentation Readiness
> Generated: 2025-11-12 16:58:19 UTC | Author: mbaetiong

## Summary
This validation confirms that the opened workbench files and new support utilities enable GitHub Copilot Agents to orchestrate segmented CI (`.github/workflows/ci.yml`) with auditable, reversible dependency hygiene.

## Readiness Matrix

| File | Status | Purpose | Notes |
|------|--------|---------|-------|
| docs/analysis/implementation_plan_archival_memory_saving.md | Present | End-to-end plan | Links stages/branches and KPI targets |
| .github/copilot-prompts/dependency_segmentation_prompt_bundle.md | Present | Agent prompts bundle | Ready-to-copy prompts per stage |
| requirements-ml-cpu.txt | Present | ML surface | CPU-only torch, minimal stack |
| requirements-eval.txt | Present | Eval surface | Sci/metrics stack isolated |
| requirements-notebook.txt | Present | Notebook surface | Optional; not in baseline CI |
| docs/analysis/dependency_space_triage.md | Present | Rationale & triage | Space savings table and governance |
| noxfile.py | Present | Session orchestration | tests/ml_tests/eval_tests + helpers |
| AGENTS.md | Present | Maintainer/agent guide | Evidence schema, toggles, sessions |
| docs/arch/ADR-2025-11-12-dependency-segmentation.md | Present | Decision record | Accepted; compliance-aligned |
| .codex/evidence/dependency_ops.jsonl | Present | Evidence stream | Append-only; sample lines provided |
| .github/workflows/ci.yml | Added | CI matrix and env posture | Matrix: baseline/ml/eval/hygiene |
| scripts/vendor_guard.py | Added | Vendor guard | Fail-fast CPU posture check |
| configs/development/pytest.ini | Added | Markers | Aligns with nox sessions |
| scripts/check_dependency_evidence.py | Added | Evidence schema check | Used in CI step |
| scripts/verify_dependency_hygiene.py | Added | Evidence summarizer | Optional gate |
| scripts/disk_snapshot.sh | Added | Disk footprint | Diagnostics for CI artifacts |
| docs/ops/dependency_segmentation_rollback.md | Added | Rollback guide | Clear, reversible steps |

## Gaps Addressed
- CI workflow: Provided segmented matrix with environment toggles and evidence checks.
- Guardrails: Added vendor guard, schema validation, hygiene verification, and disk snapshot.
- Marker alignment: Ensured pytest markers defined to match nox sessions.

## Validation Checklist

| Check | Result | Evidence |
|-------|--------|----------|
| CPU posture enforced | ✅ | env CODEX_FORCE_CPU=1 in CI |
| Vendor guard invoked pre/post | ✅ | scripts/vendor_guard.py steps |
| Evidence logging enabled | ✅ | CODEX_DEPENDENCY_EVIDENCE_ENABLE=1 |
| Evidence schema validated | ✅ | scripts/check_dependency_evidence.py |
| Session split operative | ✅ | noxfile.py tests/ml_tests/eval_tests |
| Requirements segmented | ✅ | three requirements-*.txt files |
| Rollback documented | ✅ | docs/ops/dependency_segmentation_rollback.md |
| Disk savings verifiable | ✅ | scripts/disk_snapshot.sh artifact |

## Enhancement Notes
- Consider enabling `CODEX_VENDOR_ENFORCE_LOCK_PRUNE=1` for CI once dry-run diffs stabilize.
- Optionally add artifact publishing of `artifacts/dependency_plan.json` from `nox -s dependency_plan` for observability.
- For stricter compliance, set `CODEX_ABORT_ON_GPU_PULL=1` after observing several clean runs.

## Next Steps
- Merge Stage A to 0D_base_ after green runs.
- Promote rc5 scripts parity across environments.
- Monitor `.codex/cache/*summary.json` and vendor recurrence metrics for two cycles.