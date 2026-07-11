# Production Checklist
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 0.1.0  
**Last Updated: 2026-07-09
**Audience:** SRE, DevOps, Platform Engineers

---

## Pre-Launch Verification

### Security

```markdown
## Security (Required)

- [x] Secrets not hardcoded (verified via gitleaks scan)
- [x] RBAC configured (K8s ServiceAccount + ClusterRole with least privilege)
- [x] Network policies set (egress/ingress rules defined)
- [x] TLS enabled for API (certificate management in place)
- [x] Regular security scans scheduled (weekly via CI/CD)
- [x] Dependency vulnerabilities resolved (0 CRITICAL, 0 HIGH)
- [x] Container images scanned (trivy, 0 CRITICAL findings)
- [x] No secrets in Docker images (verified)
- [x] Access logs enabled (for audit trail)
- [x] Rate limiting configured (DDoS protection)
```

### Monitoring

```markdown
## Monitoring (Required)

- [x] Prometheus metrics exported (:9090/metrics)
- [x] Alerting configured (PagerDuty, Slack, email)
- [x] Centralized logging (ELK Stack, DataDog, or equivalent)
- [x] Health checks passing (HTTP 200 on /health)
- [x] SLA targets defined (p95 latency <100ms, 99.9% uptime)
- [x] Error rate alerts set (threshold >1%)
- [x] Performance baselines recorded (latency, throughput, memory)
- [x] Dashboard created (key metrics visible at a glance)
- [x] Log retention configured (minimum 30 days)
- [x] Tracing enabled (distributed tracing for debugging)
```

### Scaling

```markdown
## Scaling (Required)

- [x] HPA configured (min=2, max=10 replicas, CPU 70% target)
- [x] Load balancing tested (round-robin verified, health checks OK)
- [x] Database replication set up (master-slave or multi-node)
- [x] Cache warmup strategy documented (pre-load embeddings on startup)
- [x] Graceful shutdown implemented (SIGTERM handling with timeout)
- [x] Connection pooling configured (DB, Redis, etc)
- [x] Concurrent request limits set (prevent resource exhaustion)
- [x] Chaos testing completed (fault tolerance verified)
- [x] Load testing results documented (max throughput known)
- [x] Scaling policies tested under realistic load
```

### Disaster Recovery

```markdown
## Disaster Recovery (Required)

- [x] Backup procedure documented (frequency, retention)
- [x] RTO < 1 hour (tested and verified)
- [x] RPO < 5 minutes (checkpoints/snapshots enabled)
- [x] Recovery procedure tested and validated (dry run completed)
- [x] Runbooks in place for incident response (10+ scenarios)
- [x] Database failover tested (automatic or manual)
- [x] Data consistency verified after recovery
- [x] Point-in-time recovery capability confirmed
- [x] Backup encryption enabled
- [x] Off-site backup copies maintained
```

### Operations

```markdown
## Operations (Required)

- [x] Runbooks documented (startup, shutdown, incident response)
- [x] On-call escalation path defined and tested
- [x] Team training complete (3+ sessions, certification required)
- [x] Communication plan for outages (Slack, email, status page)
- [x] Change management process in place (staging, canary, rollback)
- [x] Deployment process automated (CI/CD pipeline)
- [x] Rollback procedure documented and tested
- [x] Maintenance windows scheduled and communicated
- [x] Capacity planning completed (growth forecast 6-12 months)
- [x] Regular post-mortems scheduled for incidents
```

---

## Pre-Deployment Checklist

### Code Quality

- [ ] All tests passing (unit, integration, e2e)
- [ ] Code coverage ≥85%
- [ ] Linting clean (black, ruff, mypy)
- [ ] No deprecated APIs used
- [ ] Documentation updated
- [ ] CHANGELOG updated

### Dependencies

- [ ] All dependencies pinned to specific versions
- [ ] Vulnerability scan passing (0 CRITICAL, 0 HIGH)
- [ ] License compatibility verified
- [ ] Security patches applied

### Infrastructure

- [ ] Kubernetes manifests validated (kubeval)
- [ ] Resource limits set (memory, CPU)
- [ ] Health checks configured
- [ ] Network policies in place
- [ ] Storage provisioned and tested

### Release

- [ ] Version bumped (semantic versioning)
- [ ] Git tag created and signed
- [ ] Docker images built and pushed
- [ ] PyPI package built and validated
- [ ] Release notes prepared
- [ ] Announcement prepared

---

## Launch Day Checklist

### 30 Minutes Before

- [ ] All alerts configured and tested
- [ ] On-call engineer assigned and briefed
- [ ] Status page updated
- [ ] Communication channels ready

### Launch

- [ ] Deployment started (canary or staged rollout)
- [ ] Health checks monitored
- [ ] Error rates tracked
- [ ] Performance baselines verified
- [ ] Key metrics within SLA

### 1 Hour After

- [ ] All systems stable
- [ ] No spike in error rates
- [ ] Performance meeting targets
- [ ] Customer feedback positive
- [ ] Team standing by for issues

### Post-Launch (Day 1)

- [ ] Monitor for issues
- [ ] Collect metrics baseline
- [ ] Team debriefs
- [ ] Document any issues
- [ ] Plan follow-up improvements

---

## Post-Launch Monitoring

### Daily

- [ ] Check uptime (should be >99.5%)
- [ ] Review error logs
- [ ] Monitor performance trends
- [ ] Check security alerts

### Weekly

- [ ] Review performance metrics
- [ ] Run backup/restore test
- [ ] Security scan execution
- [ ] Dependency updates check
- [ ] Capacity utilization review

### Monthly

- [ ] Full system health review
- [ ] Security audit
- [ ] Disaster recovery drill
- [ ] Capacity planning update
- [ ] Team training session

---

## Rollback Procedure

If issues occur:

1. **Assess**: Determine severity and impact
2. **Notify**: Alert on-call team and stakeholders
3. **Rollback**: Previous stable version (automated or manual)
4. **Verify**: Confirm rollback successful
5. **Investigate**: Root cause analysis
6. **Communicate**: Status updates to stakeholders

**Rollback Time Target:** <5 minutes

---

## Success Criteria

Production deployment is successful when:

-  99.9% uptime maintained
-  p95 latency <100ms
-  Error rate <0.1%
-  No critical security issues
-  Team confident in operations
-  Customers reporting positive experience

---

**Last Updated: 2026-07-09
**Review Frequency:** Monthly  
**Owner:** @sre-team
