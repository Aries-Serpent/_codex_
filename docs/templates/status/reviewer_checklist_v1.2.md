# Checklist: Reviewer Guide for Status v1.2
> Generated: 2024-11-02 15:05:03 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Reviewer], [Secondary: QA Buddy] ⚡ Energy: 5

Review Focus
| Area | Questions | Accept Criteria |
|---|---|---|
| Metadata | Is git_context present? Is environment captured? | All fields present; UTC timestamp |
| Snapshot | Are capabilities/findings scored? | Severity/Confidence present (1–5) |
| Schema | Are validation results documented in 2.6? | PASS or actionable remediation |
| Security | Are input validation patterns summarized (2.7)? | Coverage listed; gaps/actions noted |
| Audit | Is the integrity chain table filled (2.8)? | Manifest attached; hashes present |
| Delta | Do deltas quantify change (coverage, perf, issues/PRs)? | Δ computed or N/A justified |
| Patches | Do patches include diff, risk, rollback, tests? | All required fields present |
