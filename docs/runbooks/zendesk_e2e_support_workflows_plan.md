# Plan: End-to-End Zendesk Support Workflows with Codex
> Generated: 2025-10-31 16:17:26 | Author: mbaetiong

This plan explains how to leverage Codex to design, implement, and operate complete Support workflows in Zendesk, building on the first-cycle desired state.

## 1. Workflow building blocks

| Layer | Codex Surface | Zendesk Surface | Purpose |
|---|---|---|---|
| Configuration as Code | `configs/desired/zendesk/*.desired.json` + CLI (snapshot/diff/plan/apply) | Ticket Fields, Forms, Triggers, Views, Macros, Webhooks, Routing, Talk IVR | Versioned, reviewable admin surfaces |
| CLI Orchestration | `codex zendesk *` + `codex-task-sequence` | — | Reproducible promotions with evidence |
| Observability | `codex zendesk metrics` | Admin Center, Webhook deliveries | SLOs: apply success, rate-limit behavior, diff sizes |
| Data Quality | Great Expectations (repo: `great_expectations/`) | Exports (tickets, events) | Validate training/evaluation data if doing ML |
| ML Assist (optional) | `codex-ml` CLI and plugins | Macros suggestions, auto-triage | Train/evaluate models on curated Zendesk data |
| Docs & Ops | Offline docs pipeline, runbooks, checklists | Dev docs, runbooks | Faster onboarding, air-gapped reviews |

## 2. Canonical Support workflows to implement

| Workflow | Zendesk Objects | Codex Role | Notes |
|---|---|---|---|
| Intake triage | Ticket Fields/Forms, Triggers, Views | Desired state + tests | Normalize fields; enforce required on open; queue by priority/product |
| Agent acceleration | Macros | Desired state | Curate top-20 macros; tag and measure utilization |
| Incident escalation | Triggers, Webhooks, Groups | Desired state | Notify incident bridge via webhooks; auto-assign Tier 2 for high priority |
| Skills routing | Routing attributes | Desired state | Define skills; assign agents; validate flow with test tickets |
| Voice front door | Talk IVR | Desired state | Create IVR menus and routes, after-hours rule |
| App surface (ZAF) | Apps (Ticket sidebar) | Plan phase | Identify sidebar data needs; potential custom app for context |

## 3. Implementation path

| Phase | Activities | Outputs |
|---|---|---|
| Design | Author desired JSONs; map names to real entities (groups, schedules) | PR with `configs/desired/zendesk/*.desired.json` |
| Sandbox promote | Run first cycle in `dev` or `sandbox` env | Diffs, plans, evidence JSONL, updated snapshots |
| UAT | Create test tickets; validate views, triggers, macros; IVR test calls | Checklist signed; issues fixed |
| Prod promote | Apply plans to `prod`; snapshot post-state | Evidence archived; metrics reviewed |
| Operate | Monitor metrics; capture docs; iterate desired state | Regular cycles; versioned changes |

## 4. Data and ML augmentation (optional)

| Use Case | Data Source | Codex Capability | Outcome |
|---|---|---|---|
| Macro suggestions | Historical tickets + macro usage | `codex-ml` train/eval; plugins for features | Top-N macro recommendations |
| Auto-priority | Labeled tickets | Classifier; Hydra configs; evaluation via `codex-eval` | Reduced MTTR for critical issues |
| Topic clustering | Ticket subjects/descriptions | Tokenization + embeddings; `codex-perf` | Backlog segmentation driving new macros/views |

Governance: Treat any ML-driven automation as “suggest-first,” then gated triggers once validated.

## 5. Operational guardrails

| Guardrail | Mechanism |
|---|---|
| Rate limits | Exponential backoff; monitor `zendesk_rate_limit_retries_total` |
| Change safety | Dry-run + evidence; PR reviews; staged rollouts |
| Secrets | Use `ENV:` indirection for webhook tokens/headers |
| Rollback | Retain snapshots and last-known-good desired set |
| Docs | Regularly run docs pipeline; keep local catalog updated |

## 6. Next steps checklist

| Item | Owner | Target Date |
|---|---|---|
| Fill in group/schedule/mailbox references in desired JSONs | Support Ops |  |
| Connect metrics to dashboard (Prometheus/Grafana) | Platform Eng |  |
| Stand up webhook target with test harness | SRE |  |
| Draft top-20 macros with agents | Support Ops |  |
| UAT plan with sample tickets and IVR test cases | Support Ops |  |
| Evaluate ML assistance feasibility | Data/ML |  |

Appendix: Run the first-cycle sequence:
- `codex-task-sequence --sequence scripts/task_sequences/zendesk_first_cycle.yaml`
