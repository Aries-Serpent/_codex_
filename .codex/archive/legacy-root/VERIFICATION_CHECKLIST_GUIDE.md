# Verification Checklist Usage Guide

## Overview

These checklists provide systematic verification procedures for post-deployment validation.

## Checklist Types

### Development Checklist
**Target Environment:** Local development or CI/CD pipeline  
**Target Audience:** Developers and CI systems  
**Time Budget:** ~10 minutes  
**Rigor Level:** Standard (code quality + basic functionality)

Use this checklist for:
- Local testing before pushing
- CI/CD validation on every commit
- Development deployment validation

### Staging Checklist
**Target Environment:** Staging/QA environment  
**Target Audience:** QA engineers and integration teams  
**Time Budget:** ~15 minutes  
**Rigor Level:** High (performance + integration + data integrity)

Use this checklist for:
- Pre-release validation
- Performance regression testing
- Integration testing in production-like environment

### Production Checklist
**Target Environment:** Production environment  
**Target Audience:** Ops teams and deployment engineers  
**Time Budget:** ~30 minutes  
**Rigor Level:** Highest (load testing + security + disaster recovery)

Use this checklist for:
- Final pre-deployment validation
- Post-deployment verification
- Disaster recovery testing

## How to Use a Checklist

### 1. Preparation
- Read through the entire checklist before starting
- Gather required credentials and access tokens
- Notify relevant teams (ops, on-call, etc.)
- Start a timer to track total verification time

### 2. Execution
- Work through items in order (don't skip)
- Follow verification steps exactly as written
- Mark checkbox when item is complete
- Note any unusual observations

### 3. Failure Handling
If any verification fails:
- **STOP** - Don't continue to next items
- **Note** - Record which item failed and why
- **Follow** - Execute the "Action on Failure" guidance
- **Investigate** - Understand root cause before retrying
- **Retry** - Once fix is applied, re-run failed item

### 4. Completion
- Verify all items are checked
- Calculate total time taken
- Confirm go/no-go decision (see below)
- Archive checklist results

## Go/No-Go Decision Guide

### GO (Approve for Production)
✅ **Conditions:**
- [ ] All checklist items pass
- [ ] No critical failures encountered
- [ ] Response times within acceptable range
- [ ] Error rates at 0% (or < 1% for staging)
- [ ] All security controls verified
- [ ] Backup/rollback procedures confirmed

### CONDITIONAL (Investigate Before GO)
⚠️ **Conditions:**
- [ ] One or more warnings recorded
- [ ] Performance slightly degraded but acceptable
- [ ] Minor security considerations
- [ ] Non-critical errors that recovered

**Action:** Investigate and document before proceeding

### NO-GO (Do Not Deploy)
❌ **Conditions:**
- [ ] Critical verification failed
- [ ] Error rates > acceptable threshold
- [ ] Security controls not verified
- [ ] Performance unacceptable
- [ ] Data integrity issues detected
- [ ] Rollback procedures not ready

**Action:** Halt deployment, investigate root cause, fix, restart verification

## Integration with Automation

These checklists are integrated into:
- `scripts/deployment/generate_verify_checklist.py` - Generate dynamic checklists
- `.github/workflows/automated-post-deployment-verification.yml` - Automated workflow
- `.codex/GO_NO_GO_DECISION_MATRIX.md` - Automated decision logic

## Examples

### Example: Successful Development Verification

```
1. Service Startup ✓ (15s)
2. Health Endpoint ✓ (5s)
3. Authentication Flow ✓ (45s)
4. API Request Processing ✓ (30s)
5. Error Handling ✓ (20s)
6. Metrics Collection ✓ (10s)
7. Unit Tests ✓ (120s)
8. Linting ✓ (45s)

Total: 290s (~5 min)
Result: ✅ GO
```

### Example: Staging Verification with Issue

```
1. Service Startup ✓ (30s)
2. Health Endpoint ✓ (15s)
3. Authentication ✓ (60s)
4. API Requests ✓ (45s)
5. Error Handling ✓ (30s)
6. Metrics ✓ (30s)
7. Load Testing ⚠️ (p99=4.5s, threshold=3s) - INVESTIGATE
   - Action: Scaling investigation → Found insufficient replicas
   - Fix: Increased replicas to 5
   - Retry: p99=1.2s ✓
8. Data Integrity ✓ (120s)
9. Integration Tests ✓ (180s)

Total: 510s (~8.5 min)
Result: ✅ GO (after investigation & fix)
```

## Troubleshooting

### "Health endpoint returning degraded status"
- Check adapter connectivity
- Verify adapter credentials
- Check network connectivity to adapter services
- Restart adapter processes

### "API requests timing out"
- Check request latency metrics
- Verify adapter is not overloaded
- Check network connectivity
- Review database performance

### "Error handling verification failing"
- Verify error handlers are active
- Check error logging is functional
- Ensure circuit breakers are configured
- Review recent error patterns

## Related Documents

- `.codex/CRITICAL_PATHS_FOR_VERIFICATION.md` - Critical business paths
- `.codex/GO_NO_GO_DECISION_MATRIX.md` - Automated decision logic
- `.codex/SUCCESS_CRITERIA_BY_ENVIRONMENT.md` - Success criteria
- `.codex/SMOKE_TEST_GUIDE.md` - Automated smoke tests

## Contact

For checklist issues or updates:
- Deployment Team: #deployments on Slack
- On-Call Engineer: Check pagerduty
- Documentation: Create issue in repository
