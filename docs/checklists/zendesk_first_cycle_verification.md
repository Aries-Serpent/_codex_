# Checklist: Zendesk First Cycle Verification
> Generated: 2025-10-31 16:17:26 | Author: mbaetiong

Use this checklist after dry-run and after apply.

## Pre-apply (dry-run)

| Check | Status | Notes |
|---|---|---|
| Env validated (`env-check`) |  |  |
| Dependencies ok (`deps-check`) |  |  |
| Snapshot present (`snapshot/dev/<ts>`) |  |  |
| Diffs generated (no unexpected deletes) |  |  |
| Plans normalized and review-approved |  |  |
| Evidence JSONL appended for dry-run |  |  |

## Post-apply

| Check | Status | Notes |
|---|---|---|
| No `zendesk_apply_failure_total` increments |  |  |
| Views reflect expected tickets |  |  |
| Triggers fire correctly (test tickets) |  |  |
| Macros visible to agents with correct actions |  |  |
| Ticket fields/forms render and store values |  |  |
| Webhook deliveries succeed (monitor target) |  |  |
| Routing attributes assign to correct agents |  |  |
| Talk IVR routes as designed (test calls) |  |  |
| Evidence JSONL captured and archived |  |  |
| Snapshot after apply stored and tagged |  |  |

## Governance

| Check | Status | Notes |
|---|---|---|
| PR links to diffs, plans, evidence |  |  |
| Rollback plan documented |  |  |
| Metrics dashboard updated |  |  |
| Stakeholder sign-off captured |  |  |
