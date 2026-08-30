# Root hygiene archive map

**Audit date:** 2026-08-29
**Status:** current root is already aligned with the active metadata-only policy; this folder records the archival destinations for any stale root duplicates or historical scratch artifacts that reappear.

## Canonical top-level metadata to keep

The repository root should remain limited to active project metadata and current operational inputs. Examples of files that belong at the top level include:

- `README.md`, `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `CITATION.cff`, `CODEX_MANIFEST.json`
- build and environment metadata: `pyproject.toml`, `pyproject_core.toml`, `pyproject_cognitive.toml`, `package.json`, `requirements*.txt`, `runtime.txt`, `Cargo.toml`, `Cargo.lock`
- operational configuration: `.codex/`, `.github/`, `.gitignore`, `.gitattributes`, `.bandit*`, `.secrets.baseline`, `.statusrc.json`, `.semgrepignore`
- canonical project trees: `docs/`, `src/`, `tests/`, `scripts/`, `configs/`, `site/`, `apps/`, `ops/`, and active release tooling

## Historical material that must move out of the root

Archive any files that are historical, superseded, generated, or scratch instead of live metadata. This covers the file families explicitly named in `docs/archive/README.md` and the usual root-noise patterns seen in earlier session dumps:

- phase and completion reports: `PHASE_*`, `*_SUMMARY.md`, `*_REPORT.md`, `*_FINAL_*`, `*_COMPLETE_*`
- governance / PR artifacts: `WEC_*`, `TIMEOUT_*`, `WORKFLOW_*`, `AAIS_*`, `SECURITY_REMEDIATION_*`, `SESSION_COMPLETION_*`, `MONITORING_*`
- validation dumps and generated evidence: `VALIDATION_SUMMARY*`, `validation_summary.json`, `workflow-*report*.json`, `telemetry_report.json`, `semgrep-*.json`, `checksums-*`, `*.sarif`
- one-off scratch artifacts: `*_draft.md`, `*.backup`, `a.py`, `b.py`, `test_a.py`, `test_b.py`, `*fix_all*.py`, `*repair*.py`, `*validation*runner*.py`, `secrets.txt`
- historical root-side helpers and duplicates: `failover_scenarios.py`, `metrics_collection.py`, `profiling_baseline.py`, `repair_yamls.py`, `stress_test_suite.py`, `test_optimizations.py`, `test_policy.py`, `test_yaml.py`, `patch_approval_service.py`, `patch_rbac_engine*.py`, `session_checkpoint_manager.py`, `session_resume_engine.py`, `load_test_scripts.py`

## Archive destinations

Use the following directories when a stale file is removed from the root:

- `docs/archive/phases/` — phase plans, completion reports, project milestones, handoff notes
- `docs/archive/session_reports/` — sessions, completion summaries, execution notes, final follow-up summaries
- `docs/archive/pr_reports/` — PR analysis, governance reports, security/compliance review outputs
- `docs/archive/validation/` — CI, quality, audit, and generated validation dumps
- `docs/archive/misc/` — scratch scripts, one-off helper files, duplicate runtime probes, temporary secrets/artifact dumps

## Current status

This checkout already keeps the root slim and aligned with the policy in `docs/archive/README.md`. No live stale duplicates were left at the top level during this audit, so the archive map above acts as the definitive destination list for any future cleanup.
