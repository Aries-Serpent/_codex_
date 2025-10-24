---
title: "Migration Template — CLI Hardening"
status: "draft"
template_version: "v1.0.0"
owner: "Docs & Enablement"
last_reviewed: 2025-10-20
tags:
  - migration
  - cli
  - quality-gates
---

# Migration Template — CLI Hardening

> {{cli_change_summary}}

Apply this template when migrating, renaming, or tightening CLI entry points. It emphasizes argument contracts, deterministic behaviour, and rollback safety.

## Snapshot metadata

- **CLI entry point:** `{{cli_entry_point}}`
- **Current package:** `{{current_cli_package}}`
- **Target package:** `{{target_cli_package}}`
- **Primary owners:** `{{cli_owners}}`
- **Affected scripts/jobs:** `{{affected_jobs}}`

Cross-reference the [Migration — Python File Relocation](./Migration_PythonFileRelocation.md) template for module moves that underpin CLI changes, and the [Planning — Intent Validation](./Planning_IntentValidation.md) ritual to ensure stakeholders sign off on tightened contracts.

## Guardrails

- Maintain backwards-compatible aliases for `{{alias_window}}` before enforcing breaking changes.
- Document `--flag` semantics in `docs/CLI.md` and regenerate shell completions.
- Ensure deterministic exit codes and structured JSON logging (see `docs/CLI.md` and `docs/reference/audit_prompt.md`).
- Update automation (nox, Make, CI) to consume the hardened CLI.

## 🔁 Execution phases

### Phase 1 — Discovery & Intent

1. Inventory existing commands with `{{command_inventory_tool}}` and list required/optional arguments.
2. Capture current behaviour using `{{baseline_script}}`, storing outputs in `artifacts/cli/{{timestamp_token}}/baseline.log`.
3. Validate business intent, risk tolerance, and success criteria via the [Planning — Intent Validation](./Planning_IntentValidation.md) template.

### Phase 2 — Design & Spec

1. Define the hardened argument schema, exit codes, and output formats in `{{spec_doc}}`.
2. Map compatibility layers or alias commands needed during the deprecation period.
3. Align with release engineering on deployment windows and broadcast plan (`{{broadcast_channel}}`).

### Phase 3 — Implementation

1. Update CLI parser (Typer, Click, argparse) in `{{cli_module}}` with new validation and defaults.
2. Add regression tests under `tests/{{cli_test_path}}` covering parsing, validation, and telemetry.
3. Update documentation: `docs/CLI.md`, quickstarts, and any runbooks referencing the CLI.
4. Harden telemetry/logging integration to produce structured JSON or NDJSON outputs where applicable.

### Phase 4 — Verification & Rollout

1. Run full CLI smoke tests (`{{smoke_command}}`) and capture transcripts.
2. Validate CI workflows and scheduled jobs consuming the CLI; update pinned commands where necessary.
3. Monitor `{{monitoring_dashboard}}` for error spikes and keep rollback actions ready (see below).

## Rollback playbook

- **Trigger:** {{rollback_trigger}}
- **Action:** Revert to release `{{rollback_release}}` or restore alias command `{{rollback_alias}}`.
- **Communications:** Notify `{{communications_contacts}}` and update `docs/incident_runbook.md`.

## Evidence collection

- Archive before/after `--help` outputs in `artifacts/cli/{{timestamp_token}}/`.
- Store structured logs for phased rollouts in `logs/cli_hardening/{{timestamp_token}}.jsonl`.
- Produce a status update referencing this template and file it under `docs/status_updates/`.
