# Production Checklist - Aries-Serpent v0.2.0
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Document Type:** Operations & Deployment Verification
**Audience:** DevOps Engineers, Release Managers, Operations Teams
**Last Updated: 2026-07-16

## Pre-Deployment Checklist

### 1. Code Quality & Testing

**Testing:**
- [ ] All unit tests pass: `pytest tests/ -v`
- [ ] Integration tests pass: `pytest tests/integration/`
- [ ] Coverage meets threshold (>85%): `pytest --cov=src tests/`
- [ ] No linting errors: `ruff check src/`
- [ ] Type checks pass: `mypy src/`
- [ ] Security scan clean: `bandit -r src/`

**Code Review:**
- [ ] PR reviewed and approved
- [ ] Code follows project standards
- [ ] Documentation updated
- [ ] Changelog updated

### 2. Security Verification

**Dependency Security:**
- [ ] No critical vulnerabilities: `pip-audit --desc`
- [ ] Safety check passes: `safety check`
- [ ] SBOM generated and reviewed
- [ ] Dependencies pinned to specific versions

**Code Security:**
- [ ] No hardcoded secrets or credentials
- [ ] No sensitive data in logs
- [ ] SQL injection protections in place
- [ ] Input validation implemented
- [ ] Authentication/authorization tested

**Container Security:**
- [ ] Images scanned for vulnerabilities
- [ ] Non-root user in Dockerfile
- [ ] No secrets in environment variables
- [ ] Resource limits defined

**Kubernetes Security:**
- [ ] SecurityContexts configured
- [ ] RBAC policies defined
- [ ] Network policies applied
- [ ] Secrets management configured
- [ ] Pod security standards enforced

### 3. Performance & Load Testing

**Performance Testing:**
- [ ] API response times acceptable (<500ms baseline)
- [ ] Database queries optimized (see query plans)
- [ ] Memory usage stable (no leaks detected)
- [ ] CPU usage at expected levels

**Load Testing:**
- [ ] Tested at 100% expected load
- [ ] Tested at 150% expected load
- [ ] Tested at 200% expected load
- [ ] Auto-scaling triggers properly
- [ ] Graceful degradation under load

**Benchmarks:**
- [ ] Record baseline metrics
- [ ] Compare against previous release
- [ ] Document any regressions
- [ ] Plan optimizations if needed

### 4. Infrastructure Readiness

**Database:**
- [ ] PostgreSQL production version (15+)
- [ ] Backups configured and tested
- [ ] Replication setup (if multi-region)
- [ ] Indexes created and optimized
- [ ] Maintenance windows scheduled
- [ ] Monitoring alerts configured

**Cache:**
- [ ] Redis production version (7+)
- [ ] Persistence configured
- [ ] Replication setup
- [ ] Memory limits set
- [ ] Eviction policy defined

**Storage:**
- [ ] Persistent volumes provisioned
- [ ] Storage class configured
- [ ] Snapshots configured
- [ ] Retention policy defined

**Networking:**
- [ ] Ingress configured with TLS
- [ ] Service mesh operational (if used)
- [ ] Network policies enforced
- [ ] DNS resolution working
- [ ] Load balancer health checks passing

### 5. Monitoring & Observability

**Metrics:**
- [ ] Prometheus scrape targets configured
- [ ] Key metrics defined and dashboards created
- [ ] Alert rules configured
- [ ] Alert routing tested

**Logging:**
- [ ] Log aggregation configured (ELK/Loki)
- [ ] Log retention policy set
- [ ] Sensitive data filtering in place
- [ ] Log search tested

**Tracing:**
- [ ] Distributed tracing configured
- [ ] Jaeger backend operational
- [ ] Sampling configured
- [ ] Trace visualization tested

**Alerting:**
- [ ] Alerts configured for:
 - [ ] High CPU/memory
 - [ ] Database connection errors
 - [ ] API error rate >1%
 - [ ] Response time >1s
 - [ ] Disk space <20%
- [ ] On-call notification tested
- [ ] Alert escalation paths defined

### 6. Configuration Management

**Environment Variables:**
- [ ] Production env vars defined
- [ ] Secrets stored securely
- [ ] Configuration verified
- [ ] No hardcoded values

**ConfigMaps & Secrets:**
- [ ] Kubernetes ConfigMaps deployed
- [ ] Kubernetes Secrets created
- [ ] Secret encryption enabled
- [ ] Access controls verified

**Feature Flags:**
- [ ] Feature flags configured
- [ ] Default flags safe
- [ ] Rollback plan documented

### 7. Backup & Disaster Recovery

**Backup Plan:**
- [ ] Daily backups configured
- [ ] Backups tested and verified
- [ ] Restore procedure documented
- [ ] RTO/RPO defined and met

**Disaster Recovery:**
- [ ] Failover procedures documented
- [ ] Failover tested
- [ ] Data consistency procedures
- [ ] Communication plan ready

**Documentation:**
- [ ] Runbooks created
- [ ] Incident response plan
- [ ] Escalation procedures
- [ ] Contact list updated

### 8. API & Interface Testing

**API Endpoints:**
- [ ] All endpoints tested
- [ ] Response formats validated
- [ ] Error handling tested
- [ ] Rate limiting working
- [ ] CORS configured correctly

**API Documentation:**
- [ ] OpenAPI spec generated
- [ ] API docs deployed
- [ ] Example requests provided
- [ ] Deprecation warnings in place

**Client Compatibility:**
- [ ] Tested with production clients
- [ ] Backward compatibility verified
- [ ] Version negotiation working

### 9. Compliance & Legal

**Compliance:**
- [ ] GDPR requirements met
- [ ] Data residency requirements met
- [ ] Encryption requirements met
- [ ] Audit logging in place

**Documentation:**
- [ ] License file present
- [ ] Terms of service updated
- [ ] Privacy policy updated
- [ ] Data handling procedures documented

### 10. Team Readiness

**Runbooks:**
- [ ] Deployment runbook
- [ ] Incident response runbook
- [ ] Rollback runbook
- [ ] Scaling runbook
- [ ] All runbooks reviewed and tested

**Training:**
- [ ] Team trained on new features
- [ ] Operational procedures reviewed
- [ ] On-call rotation ready
- [ ] Escalation procedures understood

**Communication:**
- [ ] Deployment announcement prepared
- [ ] Stakeholders notified
- [ ] Communication channels open
- [ ] Status page updated

## Deployment Day Checklist

### Before Deployment

- [ ] **T-30min:** Pre-flight checks
 - [ ] All systems green
 - [ ] Backups current
 - [ ] Team assembled

- [ ] **T-15min:** Notifications
 - [ ] Team notification sent
 - [ ] Stakeholders notified
 - [ ] Status page updated

- [ ] **T-5min:** Final checks
 - [ ] Database backup verified
 - [ ] Rollback plan confirmed
 - [ ] Monitoring systems live

### During Deployment

- [ ] **Phase 1:** Blue-Green Deployment
 - [ ] Green environment healthy
 - [ ] Health checks passing
 - [ ] Smoke tests passing
 - [ ] Sample traffic routing

- [ ] **Phase 2:** Gradual Rollout
 - [ ] 10% traffic monitor for 5 min
 - [ ] 25% traffic monitor for 5 min
 - [ ] 50% traffic monitor for 10 min
 - [ ] 100% traffic continue monitoring

- [ ] **Phase 3:** Validation
 - [ ] Error rates normal
 - [ ] Response times acceptable
 - [ ] Database replication healthy
 - [ ] Cache hit rates normal

### Post-Deployment

- [ ] **T+30min:** Post-deploy checks
 - [ ] All metrics green
 - [ ] No error spikes
 - [ ] User reports normal
 - [ ] Database healthy

- [ ] **T+4 hours:** Extended monitoring
 - [ ] Continued stability
 - [ ] No performance regressions
 - [ ] Backup completed

- [ ] **T+24 hours:** Final verification
 - [ ] All systems stable
 - [ ] All metrics within SLA
 - [ ] No pending issues
 - [ ] Post-deployment review

## Rollback Procedure

If issues detected, trigger rollback:

```bash
# Phase 1: Stop new traffic
kubectl patch svc api -p '{"spec":{"selector":{"version":"blue"}}}'

# Phase 2: Scale down green deployment
kubectl scale deployment api-green --replicas=0

# Phase 3: Verify health
kubectl get pods -l version=blue
curl http://service/health

# Phase 4: Notify stakeholders
# Issue: <issue description>
# Rollback triggered at: <timestamp>
# Status: INVESTIGATING
```

## Success Criteria

Deployment is successful when:

 All health checks pass for 30 minutes
 Error rate < 0.1%
 Response times < baseline + 10%
 No customer-facing issues
 All monitoring alerts normal
 Database replication healthy
 No security issues detected

## Post-Deployment Review

Schedule review meeting within 24 hours:

- What went well?
- What could be improved?
- Action items for next release
- Update documentation based on learnings

---

## Useful Commands

```bash
# Deployment status
kubectl get deployment,pod,svc

# Check rollout status
kubectl rollout status deployment/api

# View logs
kubectl logs -l app=api -f

# Monitor metrics
kubectl top pods

# Port forward for testing
kubectl port-forward svc/api 8000:8000

# Rollback to previous
kubectl rollout undo deployment/api
```

---

**Status:** COMPLETE
**Last Updated: 2026-07-16
