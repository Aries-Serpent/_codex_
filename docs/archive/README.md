# Archived Documentation
**Last Updated:** 2026-08-29
**Version:** v0.3.0

This directory contains archived documentation, historical reports, and superseded validation artifacts. It exists to keep the repository root focused on active project metadata instead of stale execution dumps.

## Root-level archival policy

The repository root is reserved for active metadata and the files that directly support the current release, governance, and automation surfaces. Historical reports, phase summaries, validation dumps, and one-off transient artifacts should live under `docs/archive/` or be removed.

### Active repo metadata that stays at the root

- Project identity and release data: `README.md`, `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `CITATION.cff`, `CODEX_MANIFEST.json`, `pyproject.toml`, `package.json`, `requirements*.txt`, `runtime.txt`
- Operational state: `.codex/`, `.github/`, `.gitignore`, `.gitattributes`, `.coverage_baseline.json`, `.mypy_baseline`, `.statusrc.json`, `.secrets.baseline`, `.bandit*`, `.semgrepignore`
- Canonical docs and source trees: `docs/`, `site/`, `src/`, `tests/`, `scripts/`, `configs/`

### Historical material that should be archived

Archive root-level material when it is historical, superseded, or generated during investigation rather than part of the live toolchain.

- Phase summaries and completion reports: `PHASE_*`, `*_SUMMARY.md`, `*_REPORT.md`, `*_FINAL_*`, `*_COMPLETE_*`
- PR and governance reports: `WEC_*`, `TIMEOUT_*`, `WORKFLOW_*`, `SESSION_COMPLETION_*`, `MONITORING_*`, `AAIS_*`, `SECURITY_REMEDIATION_*`
- Validation dumps and compliance artifacts: `VALIDATION_SUMMARY*`, `validation_summary.json`, `workflow-*report*.json`, `telemetry_report.json`, `semgrep-*.json`, `checksums-*`, `*.sarif`
- Temporary or ad hoc production artifacts: `*_draft.md`, `*.backup`, `*.tmp`, `*fix_all*.py`, `*repair*.py`, `*validation*runner*.py`, `secrets.txt`, `a.py`, `b.py`, `test_a.py`, `test_b.py`

### 2026-08-29 root hygiene archive map

The current checkout already keeps the repository root limited to active metadata. When a stale duplicate or scratch artifact reappears at the root, it should be classified using the destinations in [`root_hygiene_2026_08_29/README.md`](./root_hygiene_2026_08_29/README.md):

- `docs/archive/phases/` for phase summaries and completion reports
- `docs/archive/session_reports/` for session/completion summaries
- `docs/archive/pr_reports/` for PR, governance, and remediation reports
- `docs/archive/validation/` for validation, CI, and generated artifact dumps
- `docs/archive/misc/` for scratch scripts, one-off helper files, and temporary data dumps

## Archive layout

### pr_reports/
Contains PR-specific analysis, completion summaries, and error logs from past PRs.

### session_reports/
Contains session completion summaries and status reports from development sessions.

### phases/
Contains historical phase plans, completion reports, and handoff notes.

### validation/
Contains CI, audit, and validation dumps that should not remain at the repository root.

### misc/
Contains one-off notes, drafts, and temporary investigation artifacts that are preserved only for historical reference.

## Deletion policy for obsolete files

1. Remove temporary and duplicate artifacts immediately once they have been superseded and are no longer referenced by the active repo state.
2. Delete old root-level drafts, one-off scripts, and generated dumps after they have been archived or confirmed redundant.
3. Keep release-critical, legal, or compliance evidence in `docs/archive/` instead of the root; do not delete historical security, SBOM, or incident artifacts without a retention decision.
4. Never delete active project metadata, build manifests, security baselines, workflow definitions, or governance files under `.codex/` or `.github/`.
5. When a file is retained for historical reference, preserve it in `docs/archive/` with a descriptive path and name rather than leaving a stale copy at the root.

## Safe retention rules

- Root-level files should only be kept when they are live project metadata or are required by an active workflow.
- Prefer `docs/archive/` over the root for superseded reports and evidence.
- Keep only the newest version of a report in active use; archive or delete older duplicates.
- Maintain a clear distinction between active repo metadata and historical investigation artifacts so the root remains legible and maintainable.

## Note

These files are kept for historical reference but are no longer actively maintained. For current documentation, refer to the main `docs/` directory and the active metadata files at the repository root.
