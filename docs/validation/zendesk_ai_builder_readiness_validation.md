# Validation: Zendesk AI App Builder Readiness
> Generated: Previous Cycle-10-31 16:17:26 | Author: mbaetiong

 Roles: [Primary] Educator, [Secondary] Navigator  Energy: 5/5  

Use this checklist to validate an AI agent built with Zendesk App Builder before pilot.

## A) Functional readiness

| Check | Status | Notes |
|---|---|---|
| Tools list defined and reviewed (least privilege) |  |  |
| JSON schemas implemented server-side (strict) |  |  |
| Happy-path flow: snapshot → diff → plan → dry-run → apply |  |  |
| Dry-run requires human confirmation for destructive ops |  |  |
| Evidence JSONL written for both dry-run and apply |  |  |
| Error taxonomy mapped to UX (retryable vs terminal) |  |  |

## B) Performance and rate limits

| Check | Status | Notes |
|---|---|---|
| Read/write budgets per run enforced |  |  |
| Backoff + jitter on 429/5xx verified |  |  |
| Caching of common reads (e.g., forms/fields) |  |  |
| Async apply available for >N operations |  |  |

## C) Security and compliance

| Check | Status | Notes |
|---|---|---|
| Secrets only in ITA; never in client |  |  |
| Redaction layer for logs/evidence |  |  |
| PII handling reviewed with Compliance |  |  |
| Tool inputs validated; allowlists applied |  |  |

## D) UX and accessibility

| Check | Status | Notes |
|---|---|---|
| Sidebar flows fit within width and scroll |  |  |
| Long outputs returned as links (not inlined) |  |  |
| Confirmation modals for risky changes |  |  |
| Keyboard navigation and ARIA roles validated |  |  |

## E) Observability

| Check | Status | Notes |
|---|---|---|
| `zendesk_*` metrics live in dashboard |  |  |
| Alerting thresholds set for failures/429s |  |  |
| Evidence retention policy documented |  |  |

## F) Change management

| Check | Status | Notes |
|---|---|---|
| PR process for desired-state JSONs |  |  |
| Rollback plan tested using snapshots |  |  |
| Canary environment promotion path |  |  |
| Docs cache updated and linked in app |  |  |
