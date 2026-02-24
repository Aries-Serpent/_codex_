# [Policy]: Non-Deferral Mandate for GitHub Copilot Agent — CI Data Handling
> Generated: 2026-02-15T10:55:00Z | Author: mbaetiong

🧠 Roles: [Primary], [Secondary]
⚡ Energy: [5]
⚛️ Physics:
- Path🛤️: MCP-first exhaustive collection → evidence logging → deterministic population → commit/PR
- Fields🔄: PRs, commits, check-runs, workflow runs, jobs, artifacts, UI-backed automation
- Patterns👁️: Per-commit queries, pagination/backoff, resume-on-interrupt, batch commits
- Redundancy🔀: API + UI automation fallbacks; cached indices; retry with SSO refresh
- Balance⚖️: Safety/compliance respected; zero human data entry; agent-only escalation with evidence

Executive Summary
- Mandate: GitHub Copilot Agent MUST NEVER defer CI/data-handling requests (e.g., populating failing checks tables) to a human. The agent must exhaust all MCP capabilities and complete the task autonomously, escalating only when access is explicitly and demonstrably blocked and documented with evidence.
- Rationale: CI metadata (runs, jobs, artifacts) is non-PII, bounded, machine-retrievable, and within the agent's MCP access domain. Deferral undermines reliability, auditability, and the purpose of agent automation.

Scope
- In scope: Retrieving and populating CI-related data for PRs/commits (run_id, run_html_url, run_name, run_conclusion, job_id, job_name, job_html_url, job_status, artifact_archive_download_url), PR and commit listings, branch refs, check-runs, and Actions jobs/artifacts.
- Out of scope: Actions that require privileged write access beyond branch-level commits/PRs, or operations expressly prohibited by org policy (still requires agent-only escalation, not human data collection).

Authority & References
- Codebase Agency Policy: [CODEBASE_AGENCY_POLICY.md](https://github.com/Aries-Serpent/_codex_/raw/refs/heads/main/.codex/CODEBASE_AGENCY_POLICY.md)
- Sprint Execution Template (for plansets): [Sprint Plan TEMPLATE](https://github.com/Aries-Serpent/_codex_/raw/refs/heads/main/.github/prompts/sprint_execution_plan/TEMPLATE.md)

Operational Guarantees (MCP capability mapping)

| Required Column | MCP Capability | Primary Endpoint | Fallback Endpoint | Notes |
|---|---|---|---|---|
| run_id | Actions runs by head_sha | GET /repos/{owner}/{repo}/actions/runs?head_sha={sha} | UI automation (/pull/{n}/checks) | Deterministic; preserved in URLs |
| run_html_url | Actions run page | From run object | UI automation | Direct link for triage |
| run_name | Actions run name | From run object | Check-run name | Prefer workflow run name |
| run_conclusion | Actions run conclusion | From run object | Check-run conclusion | Completed/failed/action_required |
| job_id | Jobs in run | GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs | UI automation (job URL) | Extracted from job detail |
| job_name | Jobs in run | From job object | UI automation | Stable, human-readable |
| job_html_url | Job page | From job object | UI automation | Direct navigation |
| job_status | Job status | From job object | UI automation | queued/in_progress/completed |
| artifact_archive_download_url | Artifacts | GET /repos/{owner}/{repo}/actions/artifacts/{id}/zip | List artifacts + match by run_id/name | Requires auth; record id+URL |

Non-Deferral Justification (context vs. typical industry reasons)

| Industry Reason for Deferral | Why it does not apply to our CI data tasks | Enforced Agent Behavior |
|---|---|---|
| Human-in-the-loop for ambiguity | CI metadata is objective, structured, and machine-retrievable | Agent exhausts endpoints; no human data entry |
| Safety/compliance (PII risk) | CI metadata contains no PII; access is read-only | Agent logs and stores evidence; complies with repo policy |
| Access controls/SSO | MCP runner has org-approved access; agent can auto-refresh SSO | Agent retries/refreshes; escalates with evidence if truly blocked |
| Reliability/validation | Deterministic API + UI-backed automation; outputs validated via evidence | Agent attaches raw JSON/HTML snapshots; reproducible |
| Rate limits/cost | Pagination/backoff and resume-on-reset make collection tractable | Agent manages limits; continues until completion |

Exception & Escalation Procedure (Agent-only; never human collection)
- Exception criteria (ALL must be true to escalate):
  - Explicit 403/401/404/410 on required endpoints after retries, backoff, and SSO refresh attempts.
  - UI automation unable to retrieve required elements due to auth gating or hard removal (archival).
  - Evidence captured: raw responses, headers, DOM snapshots, timestamps.
- Escalation actions:
  - Open a minimal PR comment or issue (agent-auth) tagging repo admins with evidence bundle and the exact access scope required (read-only Actions/check-runs).
  - Continue automated collection for remaining accessible commits; annotate unavailable entries as ARCHIVED/UNAVAILABLE with evidence.
- Prohibited:
  - Requesting the user to perform manual UI collection or supply data.
  - Deferring completion when automation is viable.

SLOs & Verification
- SLO: First row population within 10–30 minutes under normal rate limits; full PR coverage within session limits (respects rate-limit reset).
- Verification:
  - Evidence files per commit: check-runs JSON, runs JSON, jobs JSON, artifacts JSON, optional UI HTML snapshot.
  - Deterministic table rows populated; counts match commit list.
  - Pre-commit hooks/tests pass; branch commit + PR opened.

Failure Modes & Mitigations

| Failure Mode | Mitigation | Status Output |
|---|---|---|
| API 403/SSO prompt | Automated SSO refresh + retry/backoff | If unresolved, agent-only escalation with evidence |
| Pagination depth | Resume tokens, batch processing, cache progress | Continue until completion |
| Artifact pruned | Mark ARCHIVED/UNAVAILABLE with evidence | Document timestamp and response |
| UI structure changes | Robust selectors, DOM snapshot validation | Fallback to API-only paths if UI changes |
| Rate limit hit | Backoff to reset window, reduce concurrency | Progress logged, resume after reset |

Communication Guidelines
- Always communicate progress via commits/PR comments—include evidence and counts.
- Never request human data entry; never propose manual collection.
- Use concise summaries plus links to evidence artifacts.

Implementation Note (First-row priority)
- The agent MUST begin with the first row and exhaust all MCP routes before proceeding (commits → check-runs → actions runs/jobs → artifacts → UI-backed automation). Populate immediately once any path yields required fields; attach evidence.

Conclusion
- This policy codifies the non-defer mandate: Copilot Agent must complete CI data-handling requests autonomously using MCP, capturing full evidence and only escalating for documented, non-resolvable access constraints—never to request human data collection.
