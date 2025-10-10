# Incident Response Plan

## Classification
| Severity | Description | Response Time |
|----------|-------------|---------------|
| Low | Minor bug, no data exposure | 72 hours |
| Medium | Service degradation or suspicious activity | 24 hours |
| High | Confirmed compromise of non-critical data | 4 hours |
| Critical | Active exploitation or sensitive data breach | 1 hour |

## Response Workflow
1. **Detection** – Alerts from monitoring, Semgrep findings, or customer reports.
2. **Triage** – Security engineer assesses severity and assigns incident commander.
3. **Containment** – Disable impacted services, revoke credentials, enable rate limits.
4. **Eradication** – Patch vulnerabilities, rotate secrets, restore from known good artifacts.
5. **Recovery** – Validate service health via `/ready` probe and smoke tests.
6. **Post-Mortem** – Document root cause, remediation tasks, and preventative controls.

## Communication Templates
- **Internal**: `#incident-response` Slack channel updates every 30 minutes for High/Critical incidents.
- **External**: Status page updates and customer email within required disclosure windows.

## Roles & Responsibilities
- **Incident Commander** – Coordinates response, owns timeline.
- **Communications Lead** – Handles stakeholder updates.
- **Scribe** – Maintains incident log and evidence.
- **Subject Matter Experts** – Provide technical remediation support.

## Post-Incident Actions
- File follow-up issues in tracking system.
- Update documentation and runbooks to reflect fixes.
- Schedule tabletop exercises for major incident types.
