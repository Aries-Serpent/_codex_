# Rubric: Status Report Quality (v1.2)
> Generated: 2024-11-02 15:38:25 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Quality Steward], [Secondary: Reviewer] ⚡ Energy: 5

Overview
- Use this rubric during review to grade completeness, correctness, and actionability of daily reports.

Rubric
| Dimension | 1 (Needs Work) | 3 (Good) | 5 (Excellent) |
|---|---|---|---|
| Metadata | Missing title/UTC, env, or git_context | Title/UTC correct; partial env/git_context | All fields complete and accurate |
| Snapshot | Sparse; missing key sections | Most sections present with basic data | Complete snapshot; evidence links provided |
| Findings | No scores or evidence | Scores present; limited evidence | Clear evidence, impact, remediation, cross-links |
| Tests & Gates | No coverage or gates reported | Overall coverage and pass/fail noted | Per-module coverage; gate statuses with thresholds |
| Reproducibility | Not addressed | Core controls listed | Core + registry with owners and next audits |
| Schema Validation | Not addressed | PASS/FAIL stated | Detailed table + remediation actions |
| Security | Not addressed | Patterns listed | Coverage, gaps, actions, and tests linked |
| Delta | Not addressed | High-level notes | Quantified changes with trends |
| Patches | Not addressed | Titles and rationale | Full diff blocks, risk, rollback, tests, checklists |
| Automation | Not addressed | Coverage % or issues/PRs imported | Multiple automation sections merged and referenced |
| Integrity | Not addressed | Manifest created | Hash table referenced; verification steps outlined |

Acceptance Thresholds
- Minimum: All mandatory sections populated (Metadata, Snapshot, Findings, Tests & Gates, Schema Validation, Security)
- Target: Average score ≥ 3
- Stretch: Average score ≥ 4 with no dimension < 3
