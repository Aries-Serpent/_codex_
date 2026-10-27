# Agent Session Diagnostic Guidance

**Version:** 2.0 — 2026-10-22
**Scope:** Relevant diagnostics for the authorized task, not a universal gate.

Use [AI Codebase Agency Policy](../../../.codex/CODEBASE_AGENCY_POLICY.md).
Read-only and local/no-PR preparation do not require repository mutations,
remote calls, a clean repository-wide baseline or exhaustive memory retrieval.

## Orient to the task

- Confirm the objective, permitted writes, existing dirty work and acceptance
  criteria. Preserve user changes; do not reset/stash/rebase them as startup.
- Read applicable current instructions and relevant source before editing.
- Use supplied/relevant memories through actual retrieval capabilities when
  useful. `store_memory` is not a recall/list API. Identify unavailable sources.
- Inspect recent accountability/changelog sections only when relevant.
  Do not require every commit or read-only session to modify shared reports.

## Optional task-specific tools

`scripts/ci/session_bootstrap.py`, `pre_session_context.py`, `monitor_run.py`
and `ci_triage_repro.sh` can assist a relevant authorized CI/PR investigation.
Inspect their actual options, writes and network behavior before invoking them;
do not assume a “check”/“offline” label makes a command read-only.

Choose available tools and session output locations appropriate to the boundary.
Do not automatically write `.codex/session_context_latest.md`, run fix modes,
update baselines or spawn monitors just to satisfy this guide.

For PR investigations, read relevant current feedback and CI with available
authorized tools. Local/no-PR work need not retrieve every PR/base-branch run.
Do not copy hypothetical MCP names/arguments without checking the actual schema.

## Diagnose and resolve

Reproduce the relevant failure, inspect complete available evidence, and make a
bounded source-level repair when authorized. Use focused tests/lint checks;
broader triage is optional when it provides relevant evidence.

Fix issues introduced by the change and related findings in affected areas.
Other findings, access denials, infrastructure failures and exhausted retries
may be documented with exact evidence, impact, mitigation/owner and next steps.
Do not expand a read-only task or erase an accurate scope explanation.

No minimum five attempts/reviews, compulsory delegation or commit count applies.
Stop when evidence is sufficient or the next action needs authorization.
Queued/running/failed/inaccessible CI must not be reported as green; local
tests are not a hosted mergeability or deployment attestation.

## Report or hand off

State actual files, commands/results, delegated agents (or none/direct execution),
unresolved findings and limitations. Handoff may be the response or requested
session artifact; public comments, `@copilot` retriggers, memory writes and
repository status files are conditional on authorization and relevance.

For security findings retain owner/reason evidence and actual execution gates.
Workflow preparation uses applicable YAML/actionlint, secret/permission checks
and review; publishing, activating/dispatching workflows, approvals, settings,
branch writes, merges and deployments require their separate authorization.

Archived diagnostic examples remain historical evidence, not current permission
or capability proof.
