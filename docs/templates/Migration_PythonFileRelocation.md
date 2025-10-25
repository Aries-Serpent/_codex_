---
title: "Migration Template — Python File Relocation"
status: "draft"
template_version: "v1.0.0"
owner: "Docs & Enablement"
last_reviewed: 2025-10-20
tags:
  - migration
  - python
  - release-management
---

# Migration Template — Python File Relocation

> {{summary_of_change}}

Use this template when moving Python modules or packages to a new location while preserving import stability, release automation, and observability hooks.

## Snapshot metadata

- **Current module path:** `{{current_package_path}}`
- **Target module path:** `{{target_package_path}}`
- **Owning squad:** `{{owning_team}}`
- **Release window:** `{{release_window}}`
- **Dependencies touched:** `{{dependencies_list}}`

## Related templates

- [Planning — Intent Validation](./Planning_IntentValidation.md)
- [Migration — CLI Hardening](./Migration_CLIHardening.md)
- [Manual Verification Checklist](./verification.md)

## Guardrails

- Maintain compatibility shims (re-export modules or add import fallbacks) for at least `{{deprecation_window}}`.
- Capture deterministic before/after import graphs using `python -m codex_ml.cli.module_map` or equivalent tooling.
- Update release notes and docs in `docs/` plus automation manifests such as `codex_task_sequence.py`.
- Verify reproducibility via the [Manual Verification Checklist](./verification.md) when data artifacts relocate alongside code.

## 🔁 Execution phases

### Phase 1 — Discovery & Intent

1. Audit the existing module tree under `{{discovery_root}}`, documenting imports that will break without shims.
2. Confirm business intent and rollback thresholds using the [Planning — Intent Validation](./Planning_IntentValidation.md) template.
3. Log baseline tests (`pytest`, `ruff`, `mypy`) and record their outputs in `reports/{{report_stub}}`.

### Phase 2 — Design & Alignment

1. Draft the new package layout and update `pyproject.toml`/`setup.cfg` entry points.
2. Plan compatibility layers (namespace packages, import forwarding) and document them in `{{design_doc_path}}`.
3. Circulate proposed changes for sign-off, noting owners in `{{signoff_tracker}}`.

### Phase 3 — Implementation

1. Move files using `git mv` to preserve history and implement shims in `{{shim_module}}`.
2. Update imports, type checkers, and tooling configuration (e.g., `noxfile.py`, `ruff.toml`).
3. Refresh documentation: update `docs/`, READMEs, and any CLI help text referencing the old paths.
4. Run the full validation suite (tests, lint, type checks) and attach logs to `{{artifact_bucket}}`.

### Phase 4 — Verification & Rollout

1. Execute smoke tests in staging or CI mirrors and capture import graphs for regression comparison.
2. Monitor telemetry dashboards and error capture logs for `{{monitoring_window}}` after deployment.
3. Remove or schedule removal of compatibility shims after the agreed deprecation period.

## Rollback playbook

- **Trigger:** {{rollback_trigger}}
- **Action:** Revert to tag `{{rollback_tag}}` or cherry-pick `{{rollback_commits}}`.
- **Communications:** Notify `{{communication_channels}}` and document in `docs/incident_runbook.md`.

## Evidence collection

- Store before/after module maps in `artifacts/module_maps/{{timestamp_token}}`.
- Attach test and lint transcripts to `logs/migration/{{timestamp_token}}.md`.
- Capture a short status update in `docs/status_updates/` referencing this template.
