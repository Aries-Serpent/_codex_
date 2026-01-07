# Ops: Semgrep SARIF Upload
> Generated: Previous Cycle-11-02 16:00:04 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Security Lead], [Secondary: CI Maintainer] ⚡ Energy: 5

Scope
- Run Semgrep in CI and upload SARIF results to GitHub code scanning.

Workflow
- .github/workflows/semgrep_sarif.yml

Notes
- Requires repository permission security-events: write
- View findings in Security > Code scanning alerts
