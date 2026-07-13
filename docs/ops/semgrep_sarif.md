# Ops: Semgrep SARIF Upload
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> Generated: 2026-06-22 (audited) | Author: mbaetiong  
 Roles: [Primary: Security Lead], [Secondary: CI Maintainer]  Energy: 5

Scope
- Run Semgrep in CI and upload SARIF results to GitHub code scanning.

Workflow
- .github/workflows/semgrep_sarif.yml

Notes
- Requires repository permission security-events: write
- View findings in Security > Code scanning alerts
