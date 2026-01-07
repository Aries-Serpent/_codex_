# Guide: Codex ↔ Zendesk Integration Deep Dive
> Generated: Previous Cycle-10-31 16:17:26 | Author: mbaetiong

 Roles: [Primary] Educator, [Secondary] Navigator   Energy: 5/5

Note on scope: Some references below were discovered via code search and Phase 5 be incomplete due to platform limits. For a broader view, browse the code search results: https://github.com/search?q=repo%3AAries-Serpent%2F_codex_+Zendesk&type=code and the repo tree: https://github.com/Aries-Serpent/_codex_/tree/main

---

## 1) What’s the relationship between Codex and Zendesk?

Codex includes an “offline-first” administrative toolkit for Zendesk. It focuses on safe configuration management and documentation curation rather than ticket handling at runtime. The core themes:

- Snapshot → Diff → Plan → Apply: Treat Zendesk configuration (e.g., triggers, fields, forms, views, macros, routing) as versioned infrastructure.
- Evidence and metrics: Every dry-run/apply writes JSONL evidence and emits metrics to support auditability and operations.
- Offline docs capture: Curate Zendesk developer docs snapshots locally to support air‑gapped learning, review, or model fine-tuning.

Key surfaces:
- CLI entrypoints under a “zendesk” subcommand.
- Metrics registration for observability.
- Runbooks and reference docs to guide admins.

---

## 2) Where to look in the codebase

| Area | Path | What it provides |
|---|---|---|
| Zendesk CLI commands | src/codex/cli_zendesk.py | Commands for env checks, docs sync/catalog, exporting snapshots, etc. Uses Typer. |
| Metrics definitions | src/codex/zendesk/monitoring/zendesk_metrics.py | Prometheus-style counters/histograms for API calls, retries, diff/apply outcomes via Codex’s metrics registry. |
| Admin runbook | docs/crm/admin-runbooks/zendesk.md | End-to-end admin workflow with environment setup, dry-run, plan, apply, and metrics. |
| Admin workflow (step-by-step) | docs/runbooks/zendesk_admin_workflow.md | Snapshot/diff/plan/apply/verify flow with example commands and file layout expectations. |
| Offline docs pipeline (guide) | docs/runbooks/zendesk_docs_pipeline.md | How to sync and catalog Zendesk docs snapshots locally. |
| Docs fetch script | scripts/zendesk_docs_fetch.py | Downloads HTML snapshots under `docs/vendors/zendesk/YYYY-MM-DD/...` from a curated manifest. |
| Docs catalog script | scripts/sync_zendesk_docs.py | Builds a markdown catalog `docs/zendesk_api_catalog_generated.md` from `data/zendesk_api_index.json`. |
| API catalog (generated) | docs/zendesk_api_catalog_generated.md | A readable index of key Zendesk API docs captured locally. |
| API references (manual) | docs/zendesk_api_reference.md | Curated links to Zendesk areas: ticketing, views, webhooks, Talk IVR, routing, ZAF apps, etc. |
| API index (JSON) | data/zendesk_api_index.json | Machine-readable mapping of areas to endpoints/docs for cataloging. |

---

## 3) Credential model and environment checks

The CLI expects per-environment credentials expressed as environment variables:

| Env var pattern | Meaning |
|---|---|
| `ZENDESK_{ENV}_SUBDOMAIN` | Zendesk subdomain (e.g., `yourcompany`) |
| `ZENDESK_{ENV}_EMAIL` | Admin/service email |
| `ZENDESK_{ENV}_TOKEN` | API token for that environment |

Quick validation:
```bash
export ZENDESK_DEV_SUBDOMAIN=...
export ZENDESK_DEV_EMAIL=...
export ZENDESK_DEV_TOKEN=...

python -m codex.cli zendesk env-check --env dev      # validates presence + `zenpy` availability
python -m codex.cli zendesk deps-check               # checks optional deps (zenpy, torch)
```text

Notes:
- The CLI requires Zenpy for API access; `env-check` prompts you to install it if missing.
- Credentials are not stored in the repo; set them in your shell or secret manager.

---

## 4) The IaC-style flow: Snapshot → Diff → Plan → Apply

| Step | Command | What it does | Output |
|---|---|---|---|
| Snapshot | `codex zendesk snapshot --env=<env>` | Exports current Zendesk config via APIs | JSON under `snapshot/<env>/<timestamp>/...` |
| Diff | `codex zendesk diff <resource> desired.json current.json > diff.json` | Compares desired vs. current for a resource (e.g., triggers) | A resource-scoped diff |
| Plan | `codex zendesk plan <resource> diff.json > plan.json` | Computes operations from the diff (Phase 5 reuse the diff format) | A plan describing patch operations |
| Dry-run | `codex zendesk apply <resource> plan.json --env <env> --dry-run` | Simulates changes; records evidence | `.codex/evidence/*.jsonl` |
| Apply | `codex zendesk apply <resource> plan.json --env <env>` | Executes mutations against Zendesk API | Mutated state + evidence |
| Verify | `codex zendesk metrics` | Emits/prints metrics; confirm outcomes | Metrics registry/console |

Evidence:
- Dry-run and apply append JSONL entries under `.codex/evidence/` for audit and rollback analysis.

Supported resource examples:
- Triggers, Views, Macros, Ticket Forms, Ticket Fields, Webhooks, Talk IVR entities, Skills-based routing, ZAF Support App contexts.

---

## 5) Observability: Metrics and what they mean

| Metric | Type | Meaning |
|---|---|---|
| `zendesk_api_calls_total` | Counter | Total Zendesk API calls performed |
| `zendesk_rate_limit_retries_total` | Counter | Number of operations retried due to rate limiting |
| `zendesk_diff_operations` | Histogram | Distribution of patch operations per diff run |
| `zendesk_apply_success_total` | Counter | Successful apply operations |
| `zendesk_apply_failure_total` | Counter | Failed apply operations |

How to use:
- If you run Codex within a monitored environment, bind these to your metrics sink (Prometheus, etc.).
- Incorporate them into SLOs: success/failure rates, max diff size, rate-limit behavior.

---

## 6) Offline docs pipeline: building a local catalog

| Step | Command | Input | Output |
|---|---|---|---|
| Plan/source | — | `data/zendesk_docs_manifest.json` | List of curated docs URLs by section/bucket |
| Dry-run | `codex zendesk docs-sync --dry-run` | Manifest | Prints planned URLs (no writes) |
| Fetch | `codex zendesk docs-sync` | Manifest | Writes HTML under `docs/vendors/zendesk/YYYY-MM-DD/<section>/<bucket>/...` |
| Catalog | `codex zendesk docs-catalog` | `data/zendesk_api_index.json` | Regenerates `docs/zendesk_api_catalog_generated.md` |

---

## 7) What Zendesk domains are covered?

| Domain | Example docs |
|---|---|
| Ticketing: Fields, Forms, Triggers, Macros, Views, Groups | Ticket Fields, Ticket Forms, Triggers, Macros, Views |
| Webhooks | Webhooks API |
| Talk (IVR) | IVRs/Menus/Routes |
| Skills-based Routing | Skills + Incremental |
| Apps (ZAF) | Support App: Ticket Sidebar |
| Help Center (Guide) | Themes |

---

## 8) Command cheat sheet (CLI → intent)

| Command | Intent | Notes |
|---|---|---|
| `codex zendesk env-check --env <env>` | Validate env credentials and `zenpy` availability | Fails fast if misconfigured |
| `codex zendesk deps-check` | List optional deps availability | Useful for setup verification |
| `codex zendesk snapshot --env <env>` | Export current Zendesk configuration | Produces JSON snapshots |
| `codex zendesk diff <resource> <desired.json> <current.json> > diff.json` | Compute resource-specific drift | Resource can be `triggers`, `views`, etc. |
| `codex zendesk plan <resource> diff.json > plan.json` | Turn diffs into operations | Phase 5 be identity depending on design |
| `codex zendesk apply <resource> plan.json --env <env> [--dry-run]` | Apply changes (or simulate) | Emits evidence JSONL |
| `codex zendesk metrics` | Emit metrics to console/registry | Connect to your monitoring stack |
| `codex zendesk docs-sync [--dry-run]` | Snapshot Zendesk docs locally | Uses curated manifest |
| `codex zendesk docs-catalog` | Refresh Markdown catalog | Builds a browsable index |

---

## 9) Operational and security considerations

| Topic | Guidance |
|---|---|
| Rate limiting | Implement backoff; watch retries counter |
| Least privilege | Use scoped tokens per env |
| Evidence trail | Append JSONL for audits |
| Rollback | Retain snapshots and inverse diffs |
| CI vs local | Docs pipeline runs local only |

---

## 10) How this benefits Zendesk administrators

| Benefit | Description |
|---|---|
| Repeatable changes | Treat Zendesk as code; reduce drift |
| Safer promotions | Dry-run + evidence supports review |
| Faster onboarding | Local docs cache and guides |
| Observability | Quantify changes and rate-limit behavior |

---

## 11) What to learn next

| Topic | Why | Starting point |
|---|---|---|
| Zendesk Admin APIs | Understand objects and constraints | Official API docs |
| Zenpy | Python client used by the CLI | Zenpy on PyPI/GitHub |
| Codex CLI (Typer) | Wire your own admin flows | `src/codex/cli_zendesk.py` |
| Observability | Dashboards/alerts | `zendesk_metrics.py` |
| Governance | Evidence capture standards | `.codex/evidence/` |
| Offline docs curation | Build internal KB | Docs pipeline runbook |

---

## 12) TL;DR quickstart

```bash
# 1) Setup env (dev example)
export ZENDESK_DEV_SUBDOMAIN=...
export ZENDESK_DEV_EMAIL=...
export ZENDESK_DEV_TOKEN=...

python -m codex.cli zendesk env-check --env dev
python -m codex.cli zendesk deps-check

# 2) Snapshot current config
codex zendesk snapshot --env dev

# 3) Prepare desired/*.json (edit locally)

# 4) Diff, plan, dry-run, apply
codex zendesk diff triggers desired.json current.json > diff.json
codex zendesk plan triggers diff.json > plan.json
codex zendesk apply triggers plan.json --env dev --dry-run
codex zendesk apply triggers plan.json --env dev

# 5) Metrics + evidence
codex zendesk metrics
ls .codex/evidence/
```text
