# Escalation Matrix

## Severity Definitions

| Level | Definition | Response Time | Examples |
|-------|------------|---------------|----------|
| P0 | Critical - Service down | Immediate | Model serving offline, data breach |
| P1 | High - Degraded service | 30 minutes | Accuracy drop >10%, pipeline failures |
| P2 | Medium - Partial impact | 1 hour | Drift detected, slow performance |
| P3 | Low - Minor issues | 4 hours | Documentation bugs, minor errors |

## Escalation Paths

### P0 - Critical
1. Page on-call engineer immediately
2. If no response in 5 min → Page team lead
3. If no response in 10 min → Page engineering manager
4. After 15 min → Notify VP Engineering + executives

### P1 - High
1. Contact on-call engineer (Slack + email)
2. If no response in 15 min → Contact team lead
3. If no response in 30 min → Contact engineering manager

### P2 - Medium
1. Create ticket and assign to on-call
2. If no action in 2 hours → Notify team lead

### P3 - Low
1. Create ticket for next business day
2. Assign to appropriate team

## Contact Templates

```
On-call ML Engineer: [Name] <email> | [Phone]
Team Lead: [Name] <email> | [Phone]  
Engineering Manager: [Name] <email> | [Phone]
VP Engineering: [Name] <email> | [Phone]
Security Team: security@example.com | [Phone]
```

## On-Call Rotation

Update weekly schedule in PagerDuty and Slack channel #ml-ops-oncall.
