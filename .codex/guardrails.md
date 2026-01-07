# Guardrails - Genesis (template)

Generated: 2024-12-26T07:54:45Z | Author: mbaetiong

## Overview

These are policy placeholders for the Genesis Protocol. Human admin (mbaetiong) must review and finalize before enabling autonomous operations.

## Authorization Levels

| Operation Type | Authorization Level | Human Approval Required |
|----------------|---------------------|-------------------------|
| Maintenance | Autonomous | No |
| Testing | Autonomous | No |
| Documentation | Autonomous | No |
| Optimization | Approval Required | Yes |
| Refactoring | Approval Required | Yes |
| Security Changes | Escalate | Yes (immediate) |
| Config Changes | Escalate | Yes (immediate) |
| Dependency Updates | Approval Required | Yes |

## Must Do

- Human admin (mbaetiong) **must** create CODEX_MASTER_KEY secret in repository settings before enabling workflows
- All PRs from agent **must** list the decision rationale and test results
- Agent **must** escalate security-related changes to human admin immediately
- Agent **must** respect rate limits and daily PR caps (max 5 PRs/day)
- Agent **must** maintain audit trail in `.codex/change_log.md`
- Agent **must** generate validation artifacts for all operations

## Must Not

- Agent **must not** rotate or expose secrets
- Agent **must not** perform security-sensitive changes without explicit human approval
- Agent **must not** delete protected branches or perform force pushes
- Agent **must not** modify workflow files without human review
- Agent **must not** exceed resource quotas or API rate limits
- Agent **must not** bypass established escalation policies

## Secret Management

- **CODEX_MASTER_KEY**: Primary authentication token (Fine-grained PAT)
  - Required permissions: Actions, Administration, Contents, Pull Requests, Workflows
  - Rotation schedule: Every 90 days
  - Storage: GitHub repository secrets only
  
- **CODEX_WEBHOOK_SECRET**: Webhook signature verification
  - Generation: `openssl rand -hex 32`
  - Storage: GitHub repository secrets only
  
- **CODEX_BACKUP_KEY**: Fallback authentication (optional)
  - Same permissions as CODEX_MASTER_KEY
  - Storage: GitHub repository secrets only

## Network Isolation

- Agent operations run in `isolated` network mode
- Network path: `/codex/network/isolated`
- External integrations require explicit approval
- API endpoints limited to GitHub API only (during Genesis)

## Audit and Monitoring

- All operations logged to `.codex/action_log.ndjson`
- Validation reports stored for 90 days
- Change log maintained permanently in `.codex/change_log.md`
- Results tracked in `.codex/results.md`

## TODO (Human Admin Actions Required)

- [ ] Define required reviewers for codex-production environment
- [ ] Define acceptable risk thresholds for automatic execution
- [ ] Configure notification channels for escalation alerts
- [ ] Set up token rotation reminders (14 days before expiry)
- [ ] Review and customize allowed_operations in autonomous_agent.yaml
- [ ] Test escalation workflow with sample security issue
- [ ] Document organization-specific compliance requirements
- [ ] Establish backup and recovery procedures

## Risk Thresholds

| Risk Level | Description | Agent Action |
|------------|-------------|--------------|
| **Low** | Maintenance, tests, docs | Execute autonomously |
| **Medium** | Optimizations, refactoring | Create PR, await approval |
| **High** | Security, config, secrets | Escalate immediately |

## Escalation Contacts

| Issue Type | Primary Contact | Response SLA |
|------------|-----------------|--------------|
| Critical Security | @mbaetiong | Immediate |
| Configuration | @mbaetiong | 4 hours |
| General | Repository Issues | 24 hours |

## Review Schedule

- **Daily**: Review agent activity in action_log.ndjson
- **Weekly**: Review PRs and merge activity
- **Monthly**: Review and update guardrails as needed
- **Quarterly**: Full security audit and token rotation

---

**Last Updated**: 2024-12-26T07:54:45Z  
**Status**: Template - Awaiting Human Review  
**Next Action**: Human admin must complete TODO checklist before enabling autonomous operations
