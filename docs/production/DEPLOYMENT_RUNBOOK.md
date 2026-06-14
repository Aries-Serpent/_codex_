# Production Deployment Runbook

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**Maintainer**: DevOps Lead  
**Approver**: Production Engineering Manager  

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | DevOps Lead | Initial creation for Phase 6 production readiness |

---

## Executive Summary

This runbook provides comprehensive step-by-step procedures for deploying Aries-Serpent/_codex_ to production. It covers all deployment phases from pre-deployment validation through post-deployment verification, with explicit rollback procedures and approval gates.

**Deployment Target**: Production environment (us-east-1, Kubernetes cluster, managed PostgreSQL)  
**Estimated Duration**: 2-3 hours (normal flow), 30-45 minutes (expedited with pre-validated components)  
**Recovery Target Objective (RTO)**: < 5 minutes via automated rollback  
**Recovery Point Objective (RPO)**: < 1 minute (continuous backup)  

---

## Pre-Deployment Phase

### 1.1 Prerequisites Verification

**Objective**: Confirm all pre-requisites are met before initiating deployment.

**Checklist**:
- [ ] Production deployment approval obtained from Production Engineering Manager
- [ ] All required credentials (AWS API keys, DB passwords, SSL certificates) stored in AWS Secrets Manager
- [ ] VPN access verified to production cluster
- [ ] SSH key for bastion host accessible and functional
- [ ] Kubernetes cluster is responsive: `kubectl cluster-info`
- [ ] Database backup completed and verified: `pg_dump --version && pg_dumpall --file=/backup/prod-$(date +%s).sql`
- [ ] All microservices have been tested in staging environment
- [ ] Load balancer health checks configured and responding
- [ ] Monitoring dashboards prepared in Grafana
- [ ] Incident response team on standby
- [ ] Communication channels established (Slack #prod-deploy, PagerDuty bridge)

**Pre-Deployment Approval Signature**:

```
Approved by: _________________________ Date: _________
Name: _________________________ Title: _________
Contact: _________________________ Phone: _________
```

### 1.2 Backup and Rollback Preparation

**Procedure**:

1. Execute full database backup:
   ```bash
   BACKUP_ID=$(date +%Y%m%d_%H%M%S)
   AWS_PROFILE=production aws s3 cp /backup/prod-full-${BACKUP_ID}.sql \
     s3://prod-backups/database/prod-full-${BACKUP_ID}.sql
   aws s3api head-object --bucket prod-backups --key database/prod-full-${BACKUP_ID}.sql
   echo "Backup ID for rollback: $BACKUP_ID"
   ```

2. Verify backup integrity:
   ```bash
   pg_restore --list /backup/prod-full-${BACKUP_ID}.sql | head -20
   ```

3. Create Docker image snapshot for rollback:
   ```bash
   CURRENT_VERSION=$(kubectl get deployment codex-api -n production -o jsonpath='{.spec.template.spec.containers[0].image}')
   echo "Current production version: $CURRENT_VERSION" > /tmp/rollback-version.txt
   ```

4. Document current state in deployment log:
   ```bash
   echo "Pre-deployment snapshot at $(date): Version=$CURRENT_VERSION, Backup=$BACKUP_ID" >> /var/log/deployment.log
   ```

**Sign-off**:
- [ ] Backup verified and accessible
- [ ] Rollback version documented
- [ ] Previous state snapshot created

---

## Phase 1: Pre-Deployment Validation (15 minutes)

### 2.1 Configuration Validation

**Objective**: Verify all configurations are correct before deployment.

**Procedure**:

1. **Validate deployment manifest**:
   ```bash
   kubectl apply -f k8s/production/deployment.yaml --dry-run=client -o yaml > /tmp/deployment-dry-run.yaml
   echo "Deployment manifest validation passed"
   ```

2. **Check resource limits**:
   ```bash
   kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, cpu: .status.allocatable.cpu, memory: .status.allocatable.memory}'
   ```

3. **Verify secrets exist**:
   ```bash
   kubectl get secrets -n production | grep -E "db-credentials|api-keys|ssl-cert"
   ```

4. **Test database connection string**:
   ```bash
   psql -h $DB_HOST -U $DB_USER -d codex_prod -c "SELECT version();"
   ```

### 2.2 Service Health Check

**Objective**: Ensure all dependent services are operational.

**Checklist**:
- [ ] PostgreSQL database responsive and reachable
- [ ] Redis cache cluster online: `redis-cli --cluster info $REDIS_ENDPOINT`
- [ ] S3 storage accessible: `aws s3 ls s3://prod-app-storage/ --profile production`
- [ ] External API endpoints (if applicable) responding within SLA
- [ ] SSL/TLS certificates valid: `openssl x509 -in /etc/ssl/certs/prod.crt -noout -dates`
- [ ] DNS records resolving correctly: `nslookup api.codex.prod`

**Health Check Verification**:
```bash
# Run comprehensive health check script
./scripts/prod-health-check.sh 2>&1 | tee /tmp/health-check-$(date +%Y%m%d_%H%M%S).log
```

---

## Phase 2: Core Infrastructure Deployment (30 minutes)

### 3.1 Docker Image Build and Registry Push

**Objective**: Build production-ready Docker image and verify in registry.

**Procedure**:

1. **Build Docker image**:
   ```bash
   VERSION=$(cat VERSION)
   docker build -t codex-api:${VERSION} -f Dockerfile.prod .
   docker tag codex-api:${VERSION} $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/codex-api:${VERSION}
   ```

2. **Scan image for vulnerabilities**:
   ```bash
   trivy image --severity HIGH,CRITICAL codex-api:${VERSION}
   ```

3. **Push to ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/codex-api:${VERSION}
   ```

4. **Verify image availability**:
   ```bash
   aws ecr describe-images --repository-name codex-api --region us-east-1
   ```

### 3.2 Kubernetes Deployment Configuration

**Objective**: Update Kubernetes manifests with new image version.

**Procedure**:

1. **Update deployment manifest**:
   ```bash
   kubectl set image deployment/codex-api codex-api=$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/codex-api:${VERSION} \
     -n production --record
   ```

2. **Wait for rollout to complete**:
   ```bash
   kubectl rollout status deployment/codex-api -n production --timeout=10m
   ```

3. **Verify pod readiness**:
   ```bash
   kubectl get pods -n production -l app=codex-api -o wide
   kubectl describe pods -n production -l app=codex-api | grep -A 5 "Readiness"
   ```

4. **Check endpoint status**:
   ```bash
   kubectl get endpoints codex-api -n production
   ```

### 3.3 Database Migration

**Objective**: Apply all pending database migrations safely.

**Procedure**:

1. **Pre-migration database backup**:
   ```bash
   MIGRATION_BACKUP_ID=$(date +%Y%m%d_%H%M%S)
   pg_dumpall -h $DB_HOST -U $DB_USER > /backup/pre-migration-${MIGRATION_BACKUP_ID}.sql
   ```

2. **Run migration scripts**:
   ```bash
   cd /app && python -m alembic upgrade head
   ```

3. **Verify migration success**:
   ```bash
   psql -h $DB_HOST -U $DB_USER -d codex_prod -c "\dt" | head -20
   psql -h $DB_HOST -U $DB_USER -d codex_prod -c "SELECT version FROM alembic_version;"
   ```

4. **Rollback contingency documentation**:
   ```bash
   echo "Pre-migration backup: /backup/pre-migration-${MIGRATION_BACKUP_ID}.sql" > /tmp/migration-rollback.log
   echo "Database name: codex_prod" >> /tmp/migration-rollback.log
   ```

---

## Phase 3: Monitoring and Observability Deployment (15 minutes)

### 4.1 Prometheus Configuration

**Objective**: Deploy Prometheus scrape configurations for production monitoring.

**Procedure**:

1. **Update Prometheus scrape config**:
   ```bash
   kubectl apply -f k8s/prometheus/scrape-config-prod.yaml -n monitoring
   ```

2. **Verify target discovery**:
   ```bash
   kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
   curl http://localhost:9090/api/v1/targets
   ```

3. **Test metric collection**:
   ```bash
   curl 'http://localhost:9090/api/v1/query?query=up{job="codex-api"}'
   ```

### 4.2 Grafana Dashboard Deployment

**Objective**: Deploy production dashboards for visualization and alerting.

**Procedure**:

1. **Apply dashboard ConfigMaps**:
   ```bash
   kubectl apply -f k8s/grafana/dashboards-prod/ -n monitoring
   ```

2. **Verify dashboard availability**:
   ```bash
   kubectl exec -n monitoring grafana-pod -- grafana-cli admin list-dashboards
   ```

3. **Test alerting rules**:
   ```bash
   kubectl apply -f k8s/alertmanager/rules-prod.yaml -n monitoring
   amtool alert
   ```

### 4.3 Logging Pipeline Validation

**Objective**: Ensure log aggregation is working for production.

**Procedure**:

1. **Deploy Fluent Bit DaemonSet**:
   ```bash
   kubectl apply -f k8s/logging/fluent-bit-prod.yaml -n logging
   kubectl get daemonset -n logging
   ```

2. **Verify log ingestion**:
   ```bash
   kubectl logs -n logging -l app=fluent-bit --tail=50
   ```

3. **Test log queries in Elasticsearch**:
   ```bash
   curl -X GET "localhost:9200/_cat/indices?v"
   curl -X GET "localhost:9200/logs-prod*/_search?size=1"
   ```

---

## Phase 4: Security Hardening and Compliance (20 minutes)

### 5.1 Network Security

**Objective**: Verify network policies and firewall rules are enforced.

**Procedure**:

1. **Apply network policies**:
   ```bash
   kubectl apply -f k8s/network-policies/prod-policies.yaml -n production
   ```

2. **Verify network policy enforcement**:
   ```bash
   kubectl get networkpolicies -n production
   ```

3. **Test connectivity (allowed paths)**:
   ```bash
   # Test: App → DB (should succeed)
   kubectl run debug-pod --image=busybox --rm -it -- nc -zv $DB_HOST 5432
   ```

4. **Test isolation (denied paths)**:
   ```bash
   # Test: Pod → external network (should fail per policy)
   kubectl run debug-pod --image=busybox --rm -it -- curl http://external.com --connect-timeout 5
   ```

### 5.2 Secret Management

**Objective**: Verify all secrets are properly injected and accessible.

**Procedure**:

1. **Verify secret injection**:
   ```bash
   kubectl get secret -n production
   kubectl describe secret db-credentials -n production
   ```

2. **Test secret access in pod**:
   ```bash
   kubectl run secret-test --image=$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/codex-api:${VERSION} \
     --env="TEST_SECRET=$(kubectl get secret db-credentials -n production -o jsonpath='{.data.password}' | base64 -d)" \
     --rm -it -- env | grep TEST_SECRET
   ```

3. **Rotate secrets if needed**:
   ```bash
   # Document secret rotation procedure
   echo "Secrets rotated at $(date)" >> /tmp/security-log.txt
   ```

### 5.3 RBAC and Access Control

**Objective**: Verify role-based access controls are in place.

**Procedure**:

1. **Apply RBAC manifests**:
   ```bash
   kubectl apply -f k8s/rbac/prod-roles.yaml -n production
   kubectl apply -f k8s/rbac/prod-rolebindings.yaml -n production
   ```

2. **Verify service accounts**:
   ```bash
   kubectl get serviceaccounts -n production
   kubectl get rolebindings -n production
   ```

3. **Test permission enforcement**:
   ```bash
   # Test: Verify restricted access denied
   kubectl auth can-i get pods --as=system:serviceaccount:production:app-user -n production
   ```

---

## Phase 5: Integration Testing (25 minutes)

### 6.1 API Endpoint Validation

**Objective**: Verify all API endpoints are responsive and functioning.

**Procedure**:

1. **Get service endpoint**:
   ```bash
   API_ENDPOINT=$(kubectl get svc codex-api -n production -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
   echo "API Endpoint: $API_ENDPOINT"
   ```

2. **Test health endpoint**:
   ```bash
   curl -v http://${API_ENDPOINT}/health
   ```

3. **Test critical business endpoints**:
   ```bash
   # Test endpoint 1: Authentication
   curl -X POST http://${API_ENDPOINT}/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test"}' <!-- pragma: allowlist secret -->

   # Test endpoint 2: Core functionality
   curl http://${API_ENDPOINT}/api/v1/resources

   # Test endpoint 3: Data retrieval
   curl http://${API_ENDPOINT}/api/v1/status
   ```

4. **Run smoke test suite**:
   ```bash
   ./tests/smoke-tests/prod-smoke-test.sh
   ```

### 6.2 Database Integration Testing

**Objective**: Verify database connections and queries work correctly.

**Procedure**:

1. **Test database query performance**:
   ```bash
   PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
     -c "EXPLAIN ANALYZE SELECT * FROM users LIMIT 1000;" | head -30
   ```

2. **Verify critical tables exist**:
   ```bash
   PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod -c "\dt"
   ```

3. **Test transaction support**:
   ```bash
   PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod << EOF
   BEGIN;
   SELECT COUNT(*) FROM users;
   ROLLBACK;
   EOF
   ```

### 6.3 Cache Layer Validation

**Objective**: Verify Redis cache is functioning correctly.

**Procedure**:

1. **Test cache connectivity**:
   ```bash
   redis-cli -h $REDIS_ENDPOINT PING
   ```

2. **Test cache operations**:
   ```bash
   redis-cli -h $REDIS_ENDPOINT SET test-key "test-value"
   redis-cli -h $REDIS_ENDPOINT GET test-key
   redis-cli -h $REDIS_ENDPOINT DEL test-key
   ```

3. **Monitor cache metrics**:
   ```bash
   redis-cli -h $REDIS_ENDPOINT INFO stats | grep -E "total_commands_processed|used_memory"
   ```

---

## Phase 6: Load and Performance Testing (20 minutes)

### 7.1 Baseline Performance Testing

**Objective**: Establish performance baseline under production load.

**Procedure**:

1. **Run load test with production-like traffic**:
   ```bash
   ./tests/load-tests/artillery.yml --target http://${API_ENDPOINT}
   ```

2. **Monitor system metrics during load test**:
   ```bash
   # Monitor in separate terminal
   kubectl top nodes
   kubectl top pods -n production --containers
   ```

3. **Analyze performance results**:
   - Response time: < 200ms (p95)
   - Error rate: < 0.1%
   - Throughput: > 100 req/sec

4. **Document baseline metrics**:
   ```bash
   echo "Performance baseline recorded at $(date)" >> /tmp/baseline-metrics.log
   ```

### 7.2 Stress Testing

**Objective**: Verify system behavior under stress conditions.

**Procedure**:

1. **Run stress test**:
   ```bash
   ./tests/stress-tests/run-stress-test.sh --duration=5m --concurrent=500
   ```

2. **Verify graceful degradation**:
   - System remains responsive
   - Error rates controlled
   - No cascading failures

3. **Verify recovery**:
   ```bash
   # After stress test, verify system returns to normal
   curl http://${API_ENDPOINT}/health
   kubectl get pods -n production
   ```

---

## Phase 7: Go-Live and Production Cutover (30 minutes)

### 8.1 Traffic Cutover Strategy

**Objective**: Safely switch production traffic to new deployment.

**Decision Tree**:

```
START: Execute Traffic Cutover
  │
  ├─ Are all tests passing? 
  │   ├─ NO → ABORT, perform rollback
  │   └─ YES → Continue
  │
  ├─ Is load balancer health green?
  │   ├─ NO → ABORT, investigate infrastructure
  │   └─ YES → Continue
  │
  ├─ Execute canary deployment (10% traffic)
  │   ├─ Monitor for 5 minutes
  │   ├─ Error rate < 0.5%?
  │   │   ├─ NO → ABORT, perform rollback
  │   │   └─ YES → Continue
  │   │
  │   ├─ Response time p95 < 250ms?
  │   │   ├─ NO → ABORT, perform rollback
  │   │   └─ YES → Continue
  │
  ├─ Increase to 50% traffic
  │   ├─ Monitor for 5 minutes
  │   ├─ All metrics healthy?
  │   │   ├─ NO → ABORT, perform rollback
  │   │   └─ YES → Continue
  │
  ├─ Full 100% traffic cutover
  │   ├─ Monitor continuously
  │   ├─ All metrics healthy?
  │   │   ├─ NO → ABORT, perform rollback
  │   │   └─ YES → CUTOVER COMPLETE
  │
  └─ END: Production cutover successful
```

### 8.2 Canary Deployment

**Procedure**:

1. **Deploy canary replicas (10% traffic)**:
   ```bash
   kubectl patch deployment codex-api -n production -p '{"spec":{"replicas":10}}'
   kubectl set image deployment/codex-api codex-api=$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/codex-api:${VERSION} \
     -n production --selector=version=canary
   ```

2. **Configure traffic split (10% to canary)**:
   ```bash
   kubectl apply -f k8s/traffic-management/canary-10pct.yaml -n production
   ```

3. **Monitor canary metrics for 5 minutes**:
   ```bash
   # Run continuous monitoring
   watch -n 5 'curl -s http://${API_ENDPOINT}/health | jq .'
   ```

4. **Validate canary metrics**:
   ```bash
   # Check in Prometheus
   curl 'http://localhost:9090/api/v1/query?query=rate(http_requests_total{version="canary"}[5m])'
   ```

### 8.3 Progressive Traffic Rollout

**Procedure**:

1. **Increase to 50% traffic**:
   ```bash
   kubectl apply -f k8s/traffic-management/canary-50pct.yaml -n production
   kubectl patch deployment codex-api -n production -p '{"spec":{"replicas":20}}'
   ```

2. **Monitor for 5 minutes**:
   ```bash
   kubectl logs -n production -l app=codex-api --tail=100 -f
   ```

3. **Increase to 100% traffic**:
   ```bash
   kubectl apply -f k8s/traffic-management/stable-100pct.yaml -n production
   kubectl patch deployment codex-api -n production -p '{"spec":{"replicas":30}}'
   ```

4. **Monitor post-cutover (10 minutes)**:
   ```bash
   # Continuous health monitoring
   for i in {1..10}; do
     echo "=== Health check $i ==="
     curl -s http://${API_ENDPOINT}/health
     sleep 60
   done
   ```

### 8.4 Cutover Sign-Off

**Sign-off Checklist**:
- [ ] All integration tests passing
- [ ] Performance metrics within acceptable range
- [ ] No critical errors in application logs
- [ ] Database replication lag < 100ms
- [ ] Cache hit ratio > 80%
- [ ] All alerts configured and functional
- [ ] Incident response team monitoring active
- [ ] Rollback procedure documented and verified

**Cutover Approval**:

```
Production Cutover Approved By: _________________________ Date: _________
Name: _________________________ Title: _________
Witness: _________________________ Title: _________
```

---

## Phase 8: Post-Deployment Validation (15 minutes)

### 9.1 System Stability Verification

**Objective**: Confirm production system is stable after cutover.

**Procedure**:

1. **Verify all pods are healthy**:
   ```bash
   kubectl get pods -n production
   kubectl get pods -n production --field-selector=status.phase!=Running
   ```

2. **Check for pod restart cycles**:
   ```bash
   kubectl get pods -n production -o json | jq '.items[] | select(.status.containerStatuses[].restartCount > 3)'
   ```

3. **Verify resource utilization**:
   ```bash
   kubectl top pods -n production --containers
   ```

4. **Check database replication lag**:
   ```bash
   PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod \
     -c "SELECT now() - pg_last_wal_receive_lsn() AS replication_lag;"
   ```

### 9.2 Application Monitoring

**Objective**: Verify application is functioning correctly.

**Procedure**:

1. **Monitor error rates**:
   ```bash
   curl 'http://localhost:9090/api/v1/query?query=rate(http_errors_total[5m])'
   ```

2. **Monitor response times**:
   ```bash
   curl 'http://localhost:9090/api/v1/query?query=http_request_duration_seconds{quantile="0.95"}'
   ```

3. **Check business logic correctness**:
   ```bash
   # Run business-critical endpoint test
   curl -X GET http://${API_ENDPOINT}/api/v1/validation/production-health
   ```

4. **Monitor external dependencies**:
   ```bash
   curl 'http://localhost:9090/api/v1/query?query=up{job="external-service"}'
   ```

### 9.3 Security Validation

**Objective**: Verify security controls are active in production.

**Procedure**:

1. **Verify SSL/TLS enforcement**:
   ```bash
   curl -I https://${API_ENDPOINT}
   openssl s_client -connect ${API_ENDPOINT}:443 -showcerts < /dev/null
   ```

2. **Check security headers**:
   ```bash
   curl -I https://${API_ENDPOINT} | grep -E "X-Content-Type-Options|X-Frame-Options|Strict-Transport-Security"
   ```

3. **Verify WAF rules active**:
   ```bash
   aws wafv2 get-web-acl-for-resource --resource-arn $(kubectl get svc codex-api -n production -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
   ```

4. **Test rate limiting**:
   ```bash
   for i in {1..100}; do
     curl -s http://${API_ENDPOINT}/api/v1/test > /dev/null &
   done
   wait
   ```

---

## Rollback Procedure

### 10.1 Immediate Rollback (< 5 minutes)

**Trigger Criteria**:
- Error rate > 5% for > 2 minutes
- Response time p95 > 1 second
- Database replication lag > 5 seconds
- Critical service down

**Rollback Procedure**:

```bash
# Step 1: Identify current and previous versions
CURRENT_VERSION=$(kubectl get deployment codex-api -n production -o jsonpath='{.spec.template.spec.containers[0].image}')
PREVIOUS_VERSION=$(cat /tmp/rollback-version.txt)

echo "Current version: $CURRENT_VERSION"
echo "Rolling back to: $PREVIOUS_VERSION"

# Step 2: Immediate rollback to previous version
kubectl set image deployment/codex-api codex-api=${PREVIOUS_VERSION} \
  -n production --record

# Step 3: Wait for rollout completion
kubectl rollout status deployment/codex-api -n production --timeout=5m

# Step 4: Verify rollback success
kubectl get pods -n production -l app=codex-api
curl -v http://${API_ENDPOINT}/health

# Step 5: Monitor post-rollback metrics
watch -n 5 'kubectl top pods -n production'

# Step 6: Rollback sign-off
echo "Rollback completed at $(date)" >> /var/log/rollback.log
```

### 10.2 Database Rollback

**Procedure** (only if database migrations caused issues):

```bash
# Step 1: Restore from pre-migration backup
BACKUP_ID=$(cat /tmp/migration-rollback.log | grep "Backup ID" | awk '{print $NF}')

# Step 2: Restore database
PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -U $DB_USER -d codex_prod \
  /backup/pre-migration-${BACKUP_ID}.sql

# Step 3: Verify restoration
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d codex_prod -c "SELECT version FROM alembic_version;"

# Step 4: Verify application connectivity
curl http://${API_ENDPOINT}/health
```

### 10.3 Rollback Sign-Off

**Rollback Approved By**: _________________________ Date: _________  
**Reason for Rollback**: _______________________________________________  
**Witness**: _________________________ Title: _________

---

## Deployment Completion Checklist

**Final Verification**:
- [ ] All pods running and healthy
- [ ] Load balancer health checks passing
- [ ] API endpoints responding normally
- [ ] Database replication synced
- [ ] All alerts green (no false positives)
- [ ] Error logs reviewed (no critical errors)
- [ ] Performance metrics within SLA
- [ ] Security compliance verified
- [ ] Incident response team briefed on changes
- [ ] Deployment communication sent to stakeholders
- [ ] Post-deployment documentation updated

**Deployment Completion Sign-Off**:

```
Deployment completed and verified by: _________________________ Date: _________
Name: _________________________ Title: _________
Witness: _________________________ Title: _________
Time of Completion: _________________________
Total Duration: _________________________
Incidents During Deployment: [ ] None  [ ] Minor  [ ] Major
```

---

## Contact Information and Escalation

**On-Call DevOps Engineer**: [Phone: ________________, Slack: @devops]  
**Production Engineering Manager**: [Phone: ________________, Slack: @prod-manager]  
**CTO/Technical Lead**: [Phone: ________________, Slack: @cto]  

**Emergency Escalation Path**:
1. Page on-call engineer via PagerDuty
2. Alert #prod-deploy channel in Slack
3. Create SEV1 incident if RTO exceeded
4. Notify CTO if > 5 minute outage

---

## Appendix A: Environment Variables Reference

```bash
# Required environment variables
DB_HOST="prod-rds.us-east-1.amazonaws.com"
DB_USER="codex_admin"
DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id prod/db/password --query SecretString --output text)
REDIS_ENDPOINT="prod-redis.us-east-1.cache.amazonaws.com:6379"
AWS_ACCOUNT_ID="123456789012"
AWS_PROFILE="production"
API_ENDPOINT="api.codex.prod"
VERSION=$(cat VERSION)
```

---

## Appendix B: Troubleshooting Quick Reference

| Issue | Symptom | Solution |
|-------|---------|----------|
| Pod pending | `kubectl get pods` shows Pending | Check resource availability: `kubectl top nodes` |
| DB connection error | "psql: could not connect to server" | Verify DB host/port: `nslookup $DB_HOST` |
| Image pull failed | ImagePullBackOff | Check ECR credentials: `aws ecr get-login-password` |
| Network policy blocking | Connection timeout | Review policies: `kubectl get networkpolicies` |
| Secret not found | Key error in logs | Verify secrets: `kubectl get secrets -n production` | <!-- pragma: allowlist secret -->

---

**Document Version**: 1.0  
**Last Reviewed**: 2024-01-15  
**Next Review Date**: 2024-02-15
