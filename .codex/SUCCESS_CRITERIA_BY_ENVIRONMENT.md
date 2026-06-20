# Success Criteria by Environment

## Overview

This document defines the success criteria for post-deployment verification in each environment. These criteria determine whether a deployment is ready to proceed.

## Development Environment Criteria

**Target Audience:** Developers and CI/CD systems  
**Time Budget:** ~10 minutes  
**Rigor Level:** Standard

### Functional Criteria

✅ **Service Starts Successfully**
- Service process starts without errors
- No fatal exceptions in startup logs
- Service is listening on configured port
- Startup time < 30 seconds

✅ **Health Endpoints Respond**
- GET /health returns 200 with valid JSON
- GET /mcp/v1/health returns 200 with valid JSON
- Response time < 500ms for both endpoints

✅ **Core Paths Functional**
- Authentication flow completes
- API requests processed without errors
- Data storage operations work
- Error handling returns proper error codes

✅ **Code Quality Checks Pass**
- All unit tests pass (if applicable)
- Linting passes (ruff)
- Type checking passes (mypy)

### Performance Criteria (Relaxed)

- API response time < 3 seconds (typical)
- Health checks < 500ms
- No memory leaks detected in first 5 minutes

### Error Handling

- Service continues operating after non-fatal errors
- Error responses include proper error codes
- Errors are logged appropriately

### Rollback Not Required

- Development can proceed normally
- Rollback only if service cannot start

---

## Staging Environment Criteria

**Target Audience:** QA engineers and integration teams  
**Time Budget:** ~15 minutes  
**Rigor Level:** High

### Functional Criteria (All from Dev +)

✅ **All Development Criteria Met**

✅ **Integration Tests Pass**
- End-to-end workflows complete successfully
- Data flows correctly through system
- All adapters respond correctly

✅ **Data Integrity**
- Written data can be retrieved accurately
- No data corruption detected
- Data consistency checks pass
- Backup/restore procedures work

✅ **Load Testing**
- Service handles 10+ concurrent requests
- No errors under load (error rate 0%)
- Error recovery works correctly

### Performance Criteria

✅ **Response Times Acceptable**
- Mean response time < 1 second
- p95 response time < 3 seconds
- p99 response time < 5 seconds

✅ **Resource Usage Stable**
- Memory usage stable (no leaks)
- CPU usage < 80%
- Disk I/O normal

### Monitoring and Logging

✅ **Observability Working**
- Metrics being collected
- Traces visible in observability system
- Logs include correlation IDs
- No monitoring errors in logs

### Adapter Status

✅ **All Adapters Healthy**
- All configured adapters connected
- Adapter latency < 500ms each
- No adapter errors in last 5 minutes

### Security Checks

✅ **Basic Security Verified**
- TLS certificate valid (if applicable)
- No credentials in logs
- Authentication enforced on protected endpoints

### Rollback Decision

🟢 **GO** if all criteria met  
🟡 **CONDITIONAL** if minor issues with documented workarounds  
🔴 **NO-GO** if any critical criteria fail

---

## Production Environment Criteria

**Target Audience:** Ops teams and deployment engineers  
**Time Budget:** ~30 minutes  
**Rigor Level:** Highest

### Functional Criteria (All from Staging +)

✅ **All Staging Criteria Met**

✅ **High-Load Testing**
- Service handles 100+ concurrent requests
- Error rate remains at 0% (or < 0.1%)
- No timeouts detected
- Recovery after load spike verified

✅ **Disaster Recovery**
- Backup systems operational
- Restore procedure tested (dry-run)
- Rollback procedure ready and tested
- Recovery time objective (RTO) achievable

### Performance Criteria (Strict)

✅ **Response Times Excellent**
- Mean response time < 500ms
- p95 response time < 1.5 seconds
- p99 response time < 3 seconds
- No p100 (max) spikes > 5 seconds

✅ **Resource Utilization Optimal**
- Memory usage stable, peak < 70% of limit
- CPU usage < 60% average
- Disk I/O normal
- Network bandwidth sufficient

✅ **Availability Verified**
- Service uptime > 99.9% in staging over 24 hours
- No crashes or restarts in past hour
- Zero unexpected errors in logs

### Security Criteria (Mandatory)

✅ **Security Controls Active**
- TLS certificate valid and properly installed
- Certificate chain complete
- All APIs require authentication
- Rate limiting active
- CORS policies correct

✅ **Secrets Protection**
- No secrets in logs or error messages
- Credentials properly managed
- API keys rotated if needed
- Security headers present

✅ **Compliance Verification**
- Data privacy policies enforced
- Audit logging operational
- Data retention policies active
- Security scan results reviewed

### Monitoring and Alerting

✅ **Production Monitoring Ready**
- All metrics endpoints operational
- Dashboards showing live data
- Alert rules activated
- On-call team configured and ready
- Alert testing passed

✅ **Logging and Tracing**
- Centralized logging operational
- Traces flowing to collection system
- Log retention configured
- Error tracking active

### Adapter Status (Strict)

✅ **All Adapters Optimal**
- All adapters connected and healthy
- Adapter latency < 250ms each
- No adapter errors in past 30 minutes
- Adapter failover tested

✅ **Adapter Backup**
- Backup adapters ready if applicable
- Automatic failover verified
- Manual switchover procedure ready

### Database and Storage

✅ **Database Health**
- All database servers operational
- Replication lag < 1 second
- Database backups recent and verified
- Connection pool operational

✅ **Data Storage**
- File storage accessible
- Backup storage verified
- Storage performance acceptable
- Disaster recovery storage tested

### Capacity and Scaling

✅ **Capacity Ready**
- Horizontal scaling tested and working
- Load balancing verified
- Auto-scaling policies in place
- Capacity headroom available (< 70% used)

✅ **Scalability Verified**
- Can scale up/down without errors
- Health checks pass during scaling
- No service disruption during scaling

### Deployment Package

✅ **Deployment Package Verified**
- Code changes reviewed and approved
- SBOM (Software Bill of Materials) generated
- Container image scanned for vulnerabilities
- Deployment plan reviewed
- Rollback plan ready

### Communication and Handoff

✅ **Team Readiness**
- Deployment team briefed
- On-call team ready
- Communication channels ready
- Escalation procedures known
- Customer communication prepared (if needed)

### Final Sign-Off

✅ **Executive Approval**
- Technical lead approved deployment
- Operations lead approved deployment
- Release manager approved deployment
- Security review completed (if required)

### Rollback Decision

🟢 **GO** if ALL criteria met (no exceptions)  
🔴 **NO-GO** if any criterion fails

---

## Environment-Specific Thresholds

### Development

| Metric | Threshold | Unit |
|--------|-----------|------|
| Health response time | < 500ms | milliseconds |
| API response time | < 3000ms | milliseconds |
| Error rate | 0% | percent |
| Memory usage | Any | MB |
| CPU usage | Any | percent |

### Staging

| Metric | Threshold | Unit |
|--------|-----------|------|
| Health response time | < 300ms | milliseconds |
| API response p50 | < 1000ms | milliseconds |
| API response p95 | < 3000ms | milliseconds |
| Error rate (load test) | 0% | percent |
| Memory usage | < 2 GB | GB |
| CPU usage | < 80% | percent |
| Concurrent connections | 100+ | connections |

### Production

| Metric | Threshold | Unit |
|--------|-----------|------|
| Health response time | < 200ms | milliseconds |
| API response p50 | < 500ms | milliseconds |
| API response p95 | < 1500ms | milliseconds |
| API response p99 | < 3000ms | milliseconds |
| Error rate | < 0.1% | percent |
| Memory usage | < 70% limit | percent |
| CPU usage | < 60% | percent |
| Concurrent connections | 1000+ | connections |
| Uptime | > 99.9% | percent |

---

## Failure Scenarios and Actions

### Scenario 1: Health Check Endpoint Fails

**Detected by:** Health check runner

**All Environments:**
1. ❌ **Stop** - Do not proceed with deployment
2. 🔍 **Investigate** - Check service logs
3. 🔧 **Fix** - Restart service or fix configuration
4. ✅ **Retry** - Run health checks again
5. ✅ **Proceed** - If checks pass

**Likely Causes:**
- Service crashed
- Adapter not responding
- Network connectivity issue
- Configuration error

### Scenario 2: High Response Latency

**Development:** ⚠️ Warning only - investigate if time permits  
**Staging:** 🟡 Conditional - investigate before proceeding  
**Production:** ❌ NO-GO - must fix before deployment

**Investigation Steps:**
1. Check service CPU/memory usage
2. Check database performance
3. Check network latency to adapters
4. Review recent code changes
5. Check for resource contention

**Remediation:**
- Scale service replicas
- Optimize database queries
- Review code changes
- Clear caches if applicable
- Restart service

### Scenario 3: Errors Under Load

**Development:** ⚠️ Investigate if time permits  
**Staging:** ❌ NO-GO - must fix  
**Production:** ❌ NO-GO - must fix

**Investigation Steps:**
1. Identify which requests are failing
2. Check error logs
3. Check resource usage during load
4. Monitor adapter responses

**Remediation:**
- Add error handling
- Implement circuit breakers
- Scale infrastructure
- Optimize code paths
- Retry logic

### Scenario 4: Incomplete Smoke Tests

**Development:** ⚠️ Warning - may indicate missing tests  
**Staging:** 🟡 Conditional - requires review  
**Production:** ❌ NO-GO - must have complete test coverage

**Action:**
- Review which tests are missing
- Add tests if needed
- Document limitations
- Get approval for waiver (if applicable)

---

## Related Documentation

- [VERIFICATION_CHECKLIST_DEV.md](./verification-checklists/VERIFICATION_CHECKLIST_DEV.md)
- [VERIFICATION_CHECKLIST_STAGING.md](./verification-checklists/VERIFICATION_CHECKLIST_STAGING.md)
- [VERIFICATION_CHECKLIST_PRODUCTION.md](./verification-checklists/VERIFICATION_CHECKLIST_PRODUCTION.md)
- [GO_NO_GO_DECISION_MATRIX.md](./GO_NO_GO_DECISION_MATRIX.md)
- [HEALTH_CHECK_PROCEDURES.md](./HEALTH_CHECK_PROCEDURES.md)

## Contact and Support

For questions about success criteria:
- Development: #dev-deployments on Slack
- Staging: #staging-ops on Slack
- Production: #prod-ops on Slack + on-call engineer
