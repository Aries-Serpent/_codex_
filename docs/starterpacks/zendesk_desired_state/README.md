# Starter Pack: Zendesk Desired State (First Cycle)
> Generated: Previous Cycle-10-31 16:17:26 | Author: mbaetiong

This starter pack bootstraps a Zendesk admin “first cycle” using Codex:
- Define “desired state” JSONs per resource (triggers, ticket fields/forms, views, macros, webhooks, routing, Talk IVR).
- Run Snapshot → Diff → Plan → Dry-run → Apply with audit evidence and metrics.
- Prepare for end-to-end Support workflows development (macros, automation, routing, app surfaces).

Use with Codex CLI:
- Validate env: `python -m codex.cli zendesk env-check --env dev`
- Docs pipeline: `codex zendesk docs-sync --dry-run` then `codex zendesk docs-sync`
- Admin runbooks: see repo docs for Zendesk Admin Runbook and Admin Workflow.

## Folder layout

| Path | Purpose |
|---|---|
| configs/desired/zendesk/*.desired.json | Authoritative desired-state per Zendesk resource |
| scripts/task_sequences/zendesk_first_cycle.yaml | Declarative task sequence for first cycle |
| docs/checklists/zendesk_first_cycle_verification.md | Verification checklist for changes |
| docs/runbooks/zendesk_e2e_support_workflows_plan.md | Plan to build end-to-end Support workflows |

## Prerequisites

| Item | Details |
|---|---|
| Credentials | `ZENDESK_{ENV}_SUBDOMAIN`, `ZENDESK_{ENV}_EMAIL`, `ZENDESK_{ENV}_TOKEN` exported in shell |
| Python deps | `zenpy` required for live API operations. Optional: `torch` (if using ML aides) |
| CLI | Codex installed in editable mode. Run `codex zendesk deps-check` |

## Resource coverage (first cycle)

| Domain | Resource | Desired file | Notes |
|---|---|---|---|
| Ticketing | Triggers | triggers.desired.json | Automation for ticket updates |
| Ticketing | Ticket Fields | ticket_fields.desired.json | Custom fields, dropdowns, etc. |
| Ticketing | Ticket Forms | ticket_forms.desired.json | Per-form composition of fields |
| Ticketing | Views | views.desired.json | Agent inbox segmentations |
| Ticketing | Macros | macros.desired.json | Agent quick actions |
| Platform | Webhooks | webhooks.desired.json | Outbound callbacks |
| Routing | Attributes/Skills | routing.desired.json | Skills-based routing attributes |
| Talk | IVR | talk_ivr.desired.json | IVR trees, menus, routes |

Notes:
- Desired files prefer stable keys (e.g., titles/names) over numeric IDs. Codex resolvers can map by name then hydrate IDs at apply-time.
- Keep human-readable comments in separate README; JSON payloads themselves are comment-free.

## First cycle commands (happy path)

| Step | Command | Output |
|---|---|---|
| 0. Validate env | `python -m codex.cli zendesk env-check --env dev` | ok |
| 1. Snapshot | `codex zendesk snapshot --env dev` | snapshot/dev/<timestamp>/*.json |
| 2. Diff | `codex zendesk diff <resource> desired.json current.json > diffs/<resource>.json` | diffs/*.json |
| 3. Plan | `codex zendesk plan <resource> diffs/<resource>.json > plans/<resource>.json` | plans/*.json |
| 4. Dry-run | `codex zendesk apply <resource> plans/<resource>.json --env dev --dry-run` | .codex/evidence/*.jsonl |
| 5. Apply | `codex zendesk apply <resource> plans/<resource>.json --env dev` | Changes + evidence |
| 6. Metrics | `codex zendesk metrics` | Counters/histograms |

Optional: run the bundled sequence
- `codex-task-sequence --sequence scripts/task_sequences/zendesk_first_cycle.yaml`

## Evidence and metrics

| Channel | Path/Name | Description |
|---|---|---|
| Evidence | `.codex/evidence/*.jsonl` | Append-only logs of dry-run/apply operations |
| Metrics | `zendesk_api_calls_total`, `zendesk_rate_limit_retries_total`, `zendesk_diff_operations`, `zendesk_apply_success_total`, `zendesk_apply_failure_total` | Instrumentation registered via Codex metrics registry |

## Change governance tips

- Require PR review for any `configs/desired/zendesk/*.desired.json` edits.
- Store “after” snapshots under versioned artifacts and link to evidence JSONL in PR descriptions.
- Establish a rollback playbook: re-apply last-known-good desired set; maintain dated snapshots.
