# Operations Alert Runbooks
**Version**: 1.0.0
**Status**: Production Ready
**Date**: 2026-06-14

---

## 📞 Critical Alert Runbooks

All CRITICAL alerts require immediate action. These runbooks are designed to restore service within 15 minutes.

---

## 🔴 CRITICAL: High Error Rate (>5% for 5 min)

**Alert Trigger**:
- Error rate exceeds 5% for 5 consecutive minutes
- Affects user experience immediately

**Immediate Actions** (First 2 minutes):
1. **Verify the alert** is real (not a dashboarding glitch)
   ```bash
   curl -s http://metrics:9090/api/v1/query?query='rate(http_requests_errors_total[5m])' | jq
   ```

2. **Check which service is failing**
   ```bash
   # Check error distribution by service
   kubectl logs -n production -l app=user-service --tail=50 | grep ERROR
   kubectl logs -n production -l app=order-service --tail=50 | grep ERROR
   ```

3. **Identify error type** from logs
   - Database errors?
   - Timeout errors?
   - Validation errors?
   - Authentication errors?

**Triage** (Next 3 minutes):

| Error Type | Investigation | Action |
|-----------|---|---------|
| **Database Errors** | Check DB connectivity, check slow queries | [See DB Runbook](#critical-database-connection-failed) |
| **Timeout Errors** | Check upstream service latency, check resources | Scale pods or increase timeout |
| **Validation Errors** | Check recent deployments, check data | Rollback recent deployment |
| **Auth Errors** | Check auth service, check tokens | Restart auth-service, check token storage | <!-- pragma: allowlist secret -->

**Escalation** (After 5 minutes):
```
1. Notify product team (Slack: #incidents)
2. If no resolution in 5 min → Page on-call manager
3. If no resolution in 10 min → Page engineering lead
```

**Resolution Examples**:

**Scenario A: Database Connection Pool Exhausted**
```bash
# 1. Check pool status
kubectl exec -it deployment/user-service -- python -c "import db; print(db.pool.qsize())"

# 2. Check for connection leaks
kubectl logs -n production -l app=user-service | grep "connection leak"

# 3. Restart pod to clear connections
kubectl rollout restart deployment/user-service -n production

# 4. Monitor error rate
watch "kubectl logs -n production -l app=user-service --tail=20 | grep -c ERROR"
```

**Scenario B: Recent Bad Deployment**
```bash
# 1. Check recent deployments
kubectl rollout history deployment/user-service -n production

# 2. Rollback to previous version
kubectl rollout undo deployment/user-service -n production

# 3. Monitor error rate drops
watch "curl -s http://metrics:9090/api/v1/query?query='rate(http_requests_errors_total[5m])'"

# 4. After verification, investigate root cause
git log --oneline -5
```

**Scenario C: Downstream Service Degradation**
```bash
# 1. Check which requests are failing
kubectl logs -n production -l app=order-service --tail=100 | grep -A2 "timeout"

# 2. Check downstream service (payment-service)
kubectl describe pod -n production -l app=payment-service
kubectl get events -n production --sort-by='.lastTimestamp' | tail -10

# 3. If downstream is slow, scale it
kubectl scale deployment payment-service -n production --replicas=5

# 4. Monitor latency recovery
```

**Recovery Validation**:
```
- Error rate < 0.5% for 5 consecutive minutes ✓
- p99 latency < 2 seconds ✓
- No new alerts triggering ✓
- User impact: RESTORED ✓
```

**Post-Incident**:
1. Document root cause (Slack thread in #incidents)
2. Create post-mortem issue
3. Schedule blameless review

---

## 🔴 CRITICAL: Response Latency p99 > 2 seconds

**Alert Trigger**:
- p99 latency exceeds 2 seconds for 5 consecutive minutes

**Immediate Actions** (First 2 minutes):

1. **Confirm latency spike**
   ```bash
   kubectl logs -n production -l app=api-gateway | tail -20 | grep "latency"
   ```

2. **Identify affected endpoints**
   ```promql
   # In Prometheus
   topk(5, rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]))
   ```

3. **Check resource availability**
   ```bash
   kubectl top nodes
   kubectl top pods -n production
   ```

**Investigation** (Next 5 minutes):

| Check | Command | Action if Bad |
|-------|---------|---------------|
| **Database Latency** | `kubectl logs db-pod \| grep duration` | See DB runbook |
| **Cache Performance** | `redis-cli INFO stats` | See Cache runbook |
| **Pod CPU/Memory** | `kubectl top pod` | Scale deployment |
| **Network Issues** | `kubectl exec -it pod -- ping upstream` | Check network policies |

**Common Causes & Fixes**:

**Cause 1: Database Query Slow**
```bash
# 1. Check slow query log
kubectl exec -it postgres-pod -- psql -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"

# 2. Add index if missing
kubectl exec -it postgres-pod -- psql -c "CREATE INDEX idx_users_email ON users(email);"

# 3. Restart query cache
kubectl exec -it postgres-pod -- pg_ctl restart
```

**Cause 2: Cache Misses**
```bash
# 1. Check hit ratio
redis-cli INFO stats | grep hit

# 2. If hit ratio < 80%, warm cache
python -c "
import redis
r = redis.Redis(host='localhost')
for key in get_critical_keys():
    value = fetch_from_db(key)
    r.set(key, value, ex=3600)
"

# 3. Monitor hit ratio recovery
watch "redis-cli INFO stats | grep hit"
```

**Cause 3: Pod Resource Exhaustion**
```bash
# 1. Check CPU/memory
kubectl describe node <node-name>

# 2. Scale horizontally
kubectl scale deployment user-service -n production --replicas=10

# 3. Monitor latency improvement
watch "kubectl logs metrics | grep p99"
```

**Escalation**:
- If latency still >1.5s after 10 min → Page on-call
- If latency still >2.5s after 5 min → Page engineering lead

**Recovery Validation**:
```
- p99 latency < 1 second ✓
- p95 latency < 500ms ✓
- No timeout errors ✓
- Cache hit ratio > 85% ✓
```

---

## 🔴 CRITICAL: Health Check Failed (>3 consecutive failures)

**Alert Trigger**:
- Service health check fails 3+ consecutive times (>30 seconds)
- Service is likely already removed from load balancer

**Immediate Actions** (URGENT - under 30 seconds):

1. **Check service status**
   ```bash
   kubectl describe pod -n production -l app=user-service | tail -20
   ```

2. **Check pod logs for startup errors**
   ```bash
   kubectl logs -n production -l app=user-service --tail=50
   ```

3. **Check resource availability**
   ```bash
   kubectl top nodes
   kubectl describe events -n production
   ```

**Diagnosis** (Next 1-2 minutes):

```bash
# 1. Manually test health endpoint
curl -v http://pod-ip:8080/health/ready

# 2. Check which dependency is failing
curl http://pod-ip:8080/health/detailed | jq '.dependencies'

# 3. Check pod events
kubectl describe pod <pod-name> -n production
```

**Common Causes**:

| Dependency | Check Command | Fix |
|------------|--------|-----|
| **Database** | `curl pod:8080/health/detailed \| jq '.dependencies.database'` | Restart pod or scale DB |
| **Cache** | `redis-cli ping` | Restart Redis or failover |
| **Message Queue** | `kafka-console-consumer.sh --bootstrap-servers localhost:9092` | Check Kafka cluster |

**Recovery Steps**:

**Scenario 1: Pod Crashed**
```bash
# 1. Check crash logs
kubectl logs -n production -l app=user-service --previous

# 2. Restart pod
kubectl delete pod -n production -l app=user-service

# 3. Monitor new pod comes up
kubectl get pods -n production -w -l app=user-service
```

**Scenario 2: Database Connection Failed**
```bash
# 1. Check database
kubectl get pods -n production -l app=postgres
kubectl describe pod postgres-pod -n production

# 2. Restart service pod
kubectl rollout restart deployment/user-service -n production

# 3. Verify health check passes
kubectl exec pod -- curl -s localhost:8080/health/ready
```

**Scenario 3: Out of Disk**
```bash
# 1. Check disk
kubectl exec pod -- df -h /

# 2. Clean up (logs, temp files)
kubectl exec pod -- rm -rf /tmp/*

# 3. Restart pod
kubectl delete pod pod-name -n production
```

**Escalation**:
- First failure: Monitor closely
- 3rd failure: Send warning alert
- 5th consecutive: Page on-call
- 10+ consecutive: Page manager + engineering lead

**Recovery Validation**:
```
- Health check returns 200 OK ✓
- Service receiving traffic ✓
- No dependency errors ✓
- All downstream calls working ✓
```

---

## 🟡 WARNING: Resource Utilization High (CPU/Memory >80%)

**Alert Trigger**:
- CPU > 80% for 5 minutes
- Memory > 85% for 5 minutes
- Disk > 85% for 30 minutes

**Investigation** (First 3 minutes):

```bash
# 1. Check which pods using resources
kubectl top pods -n production --sort-by=cpu
kubectl top pods -n production --sort-by=memory

# 2. Check resource requests/limits
kubectl describe pod <pod-name> -n production | grep -A5 "Limits\|Requests"

# 3. Check if pod is memory-leaking
kubectl exec pod -- ps aux | head -20
```

**Common Causes & Fixes**:

**Cause 1: Memory Leak**
```bash
# 1. Check memory trend
kubectl top pod --containers=true pod-name -n production

# 2. Capture heap dump (Java)
kubectl exec pod -- jcmd <pid> GC.heap_dump /tmp/heap.bin

# 3. Restart pod
kubectl delete pod pod-name -n production

# 4. Monitor memory after restart
watch "kubectl top pod pod-name -n production"
```

**Cause 2: Insufficient Resources**
```bash
# 1. Increase resource requests/limits
kubectl patch deployment user-service -n production -p '{"spec":{"template":{"spec":{"containers":[{"name":"user-service","resources":{"requests":{"memory":"2Gi"}}}]}}}}'

# 2. Scale horizontally
kubectl scale deployment user-service -n production --replicas=5

# 3. Monitor new resource levels
watch "kubectl top pods -n production -l app=user-service"
```

**Cause 3: Disk Cleanup Needed**
```bash
# 1. Check disk usage
kubectl exec pod -- du -sh /var/log/*

# 2. Archive and delete old logs
kubectl exec pod -- gzip /var/log/app.log.* && rm /var/log/app.log.*.gz

# 3. Restart pod to clear temp files
kubectl delete pod pod-name -n production
```

**Escalation**:
- If spike recovers naturally: No escalation needed
- If sustained >2 hours: Create capacity planning ticket
- If exceeding 95%: Page on-call

---

## 🟡 WARNING: Error Rate Elevated (>1% for 10 min)

**Alert Trigger**:
- Error rate 1-5% for 10+ minutes
- Not as critical as >5% but indicates degradation

**Quick Check**:
```bash
# 1. Get current error rate
curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_requests_errors_total[5m])'

# 2. Check error types
kubectl logs -n production -l app=user-service | grep ERROR | head -20

# 3. Identify pattern
# - Same endpoint failing?
# - Same error type (timeout, validation)?
# - Same service failing?
```

**Investigation**:
- See "CRITICAL: High Error Rate" runbook for detailed investigation
- This is a warning, so likely self-recoverable
- Monitor for 10 minutes to confirm improvement

---

## 🔍 Runbook Index

| Alert | Severity | Response Time | Escalation |
|-------|----------|--------------|------------|
| Error Rate >5% | CRITICAL | <2 min | Page on-call |
| Latency p99 >2s | CRITICAL | <2 min | Page on-call |
| Health Check Failed | CRITICAL | <1 min | Page on-call |
| Resource Exhaustion | CRITICAL | <5 min | Page on-call |
| Error Rate >1% | WARNING | <10 min | Slack notify |
| Latency p95 >500ms | WARNING | <10 min | Slack notify |
| Resource Warn | WARNING | <30 min | Log + monitor |

---

## 🧪 Drill Procedures

**Weekly Drill: Test Alert Notification**
```bash
# Trigger test alert
curl -X POST http://prometheus:9090/api/v1/alerts/fire \
  -H "Content-Type: application/json" \
  -d '{"alert": "TestAlert", "severity": "critical"}'

# Verify notification reaches on-call
# Expected: Slack message in #alerts within 1 minute
```

**Monthly Drill: End-to-End Alert Response**
```bash
# 1. Simulate service failure
kubectl scale deployment user-service -n production --replicas=0

# 2. Verify alert triggers within 2 minutes
# 3. Practice triage steps
# 4. Restore service
kubectl scale deployment user-service -n production --replicas=3

# 5. Verify service recovery
# Expected: Service returns to 100% health within 5 minutes
```

---

## 📞 Escalation Contacts

```yaml
escalation_path:
  - primary_oncall: "@on-call-engineer"
  - backup_oncall: "@on-call-backup"
  - engineering_manager: "engineering-manager@company.com"
  - director: "engineering-director@company.com"
  - cto: "cto@company.com"

escalation_timing:
  tier1_timeout: 5min  # If primary doesn't ack in 5 min, page backup
  tier2_timeout: 15min # If backup doesn't ack, page manager
  tier3_timeout: 15min # If manager doesn't ack, page director
```

---

## 📊 Incident Tracking Template

```markdown
## Incident: [Alert Name]

**Start Time**: 2026-06-14T15:30:00Z
**End Time**: 2026-06-14T15:45:00Z
**Duration**: 15 minutes

**Severity**: CRITICAL / WARNING / INFO

**Impact**:
- Users affected: X
- Services degraded: X
- Data loss: None / Minor / Major

**Root Cause**:
[Describe root cause]

**Resolution**:
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Follow-Up**:
- [ ] Create JIRA ticket for root cause fix
- [ ] Schedule post-mortem
- [ ] Update runbooks if needed
```

---

**Last Updated**: 2026-06-14 | **Next Review**: 2026-07-14 | **Owned by**: Operations Team

**Emergency Contact**: Slack @on-call or +1-555-ONCALL
