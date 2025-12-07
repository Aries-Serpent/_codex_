# Operational Runbooks

Comprehensive incident response procedures for production ML operations.

## Available Runbooks

1. **model_performance_degradation.md** - Response procedures for model accuracy drops
2. **data_pipeline_failures.md** - Data pipeline recovery procedures  
3. **deployment_rollback.md** - Automated rollback procedures
4. **security_incidents.md** - Security incident response

## Quick Reference

| Incident Type | Severity | Response Time | Runbook |
|---------------|----------|---------------|---------|
| Model accuracy drop >20% | P0 | Immediate | model_performance_degradation.md |
| Data pipeline down | P1 | 15 min | data_pipeline_failures.md |
| Deployment issues | P1 | 30 min | deployment_rollback.md |
| Security breach | P0 | Immediate | security_incidents.md |

## Escalation

See `escalation_matrix.md` for contact information and escalation paths.
