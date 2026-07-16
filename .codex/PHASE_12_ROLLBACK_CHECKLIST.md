# Phase 12 Rollback Checklist
## Emergency Rollback to v0.1.0-final (5-20 min)

**Status**: ✅ READY FOR EXECUTION
**Target Version**: v0.1.0-final (verified stable)
**Trigger**: SEVERITY 1 incident with critical data impact

---

## Pre-Rollback Verification (Before Activation)

- [ ] v0.1.0-final binary verified and tested
- [ ] Database migration rollback script prepared
- [ ] v0.2.0 data backup taken
- [ ] Service dependencies documented
- [ ] Rollback communication template ready
- [ ] @mbaetiong approval obtained (for Severity 1)
- [ ] War room participants identified
- [ ] Monitoring dashboard prepared
- [ ] Post-incident review scheduled

---

## Phase 1: Preparation (T+0:00 → T+2:00)

### 1.1 Access & Permissions
- [ ] Verify production access
- [ ] Confirm elevated privileges available
- [ ] Authenticate to deployment system
- [ ] Verify SSH keys working

### 1.2 Data Backup
```bash
# Create v0.2.0 database backup
mysqldump --all-databases > /backups/v0.2.0_$(date +%s).sql

# Backup v0.2.0 configuration
tar -czf /backups/v0.2.0_config_$(date +%s).tar.gz /etc/app/

# Backup v0.2.0 application state
tar -czf /backups/v0.2.0_data_$(date +%s).tar.gz /var/app/data/
```
- [ ] Backup completed successfully
- [ ] Backup verified and transferred to safe location

### 1.3 Service Dependency Check
```bash
# Verify all services are running
systemctl status service_a service_b service_c

# Verify no ongoing deployments
ps aux | grep -E 'docker|deploy|kubectl'

# Check database connectivity
mysql -e "SELECT 1"

# Check external API connectivity
curl https://api.external.service/health
```
- [ ] All services healthy
- [ ] No conflicting deployments
- [ ] Database accessible
- [ ] External APIs responding

---

## Phase 2: Execution (T+2:00 → T+8:00)

### 2.1 Stop v0.2.0 Services
```bash
# Signal graceful shutdown (allow 30 sec for in-flight requests)
systemctl stop application_service

# Stop dependent services (if applicable)
systemctl stop service_x service_y

# Verify shutdown
systemctl status application_service
ps aux | grep -E 'python|node|java'
```
- [ ] Application service stopped
- [ ] Dependent services stopped
- [ ] Verify no lingering processes

### 2.2 Deploy v0.1.0-final
```bash
# Pull v0.1.0-final from artifact storage
aws s3 cp s3://codex-releases/v0.1.0-final.tar.gz /tmp/
tar -xzf /tmp/v0.1.0-final.tar.gz -C /opt/app/

# Verify deployment
ls -la /opt/app/
/opt/app/bin/version

# Expected output: v0.1.0-final
```
- [ ] v0.1.0-final deployed
- [ ] Version verified

### 2.3 Database Rollback (if needed)
```bash
# Create savepoint before rollback
mysql < /scripts/create_savepoint.sql

# Run rollback migration
mysql < /scripts/v0.2.0_to_v0.1.0_rollback.sql

# Verify rollback completed
mysql -e "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1"
# Expected: v0.1.0-final
```
- [ ] Rollback migration executed
- [ ] Schema version confirmed
- [ ] Savepoint created (for emergency redo)

### 2.4 Configuration Restore
```bash
# Restore v0.1.0-final configuration
cp /backups/v0.1.0_config/app.conf /etc/app/
systemctl reload application_service

# Verify configuration
/opt/app/bin/validate-config
```
- [ ] Configuration restored
- [ ] Configuration validated

### 2.5 Service Startup
```bash
# Start application service
systemctl start application_service

# Wait for startup (30 sec)
sleep 30

# Verify service is running
systemctl status application_service

# Check service logs for errors
journalctl -u application_service -n 50 --no-pager
```
- [ ] Service started successfully
- [ ] No error messages in logs
- [ ] Service responding to requests

### 2.6 Health Check
```bash
# Application health check
curl -s http://localhost:8080/health | jq '.status'
# Expected: "healthy"

# Service readiness check
curl -s http://localhost:8080/ready | jq '.ready'
# Expected: true

# Database connectivity test
curl -s http://localhost:8080/api/v1/db-check | jq '.connected'
# Expected: true
```
- [ ] Application healthy
- [ ] Service ready
- [ ] Database connected

---

## Phase 3: Verification (T+8:00 → T+18:00)

### 3.1 Metrics Verification
```bash
# Check uptime trending
curl https://metrics.internal/api/uptime?service=app | jq '.uptime_percent'
# Expected: >99%

# Check error rate
curl https://metrics.internal/api/errors?service=app | jq '.error_rate_percent'
# Expected: <0.05%

# Check latency p99
curl https://metrics.internal/api/latency?service=app | jq '.p99_ms'
# Expected: <300ms
```
- [ ] Uptime >99%
- [ ] Error rate <0.05%
- [ ] Latency p99 <300ms

### 3.2 Transaction Verification
```bash
# Verify sample transactions working
curl -X POST http://localhost:8080/api/v1/transaction \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "amount": 10}' | jq '.status'
# Expected: "success"

# Check for data integrity
mysql -e "SELECT COUNT(*) FROM transactions WHERE status='failed'" 
# Expected: Low number (no mass failures)
```
- [ ] Transactions processing
- [ ] Data integrity confirmed

### 3.3 User Report Verification
- [ ] Check support ticket volume (should decrease)
- [ ] Monitor social media / customer feedback
- [ ] Verify user login success rate
- [ ] Check API usage patterns (returning to baseline)

### 3.4 Log Analysis
```bash
# Check for error spikes
tail -n 10000 /var/log/application.log | grep -c ERROR
# Expected: <50 errors in last 10k lines

# Check for warnings
tail -n 10000 /var/log/application.log | grep WARN | head -20

# No critical errors from application
tail -n 10000 /var/log/application.log | grep -i "critical\|fatal"
# Expected: Empty or only expected messages
```
- [ ] Error rate low
- [ ] No critical messages
- [ ] Application running normally

---

## Phase 4: Monitoring (T+18:00 → T+38:00)

### 4.1 Close Monitoring (First 20 min)
- [ ] Monitor error rate continuously
- [ ] Watch latency distribution
- [ ] Check resource utilization
- [ ] Verify no new issues emerging
- [ ] Watch for error spike recurrence

### 4.2 Extended Monitoring (Next 10 min)
- [ ] Verify stability maintained
- [ ] Check for memory leaks
- [ ] Monitor database connection pool
- [ ] Watch cache hit rate

### 4.3 Success Criteria
- ✅ Uptime sustained >99% for 20 minutes
- ✅ Error rate consistently <0.05%
- ✅ No new errors or warnings
- ✅ User reports dropped to zero
- ✅ Performance baseline restored

---

## Phase 5: Post-Rollback (T+38:00+)

### 5.1 Communication
- [ ] Notify @mbaetiong: "Rollback successful, monitoring continues"
- [ ] Update incident log with completion time
- [ ] Notify affected users via status page
- [ ] Send all-clear notification

### 5.2 Evidence Collection
- [ ] Archive v0.2.0 logs (for RCA)
- [ ] Export metrics snapshot
- [ ] Capture database state
- [ ] Document exact rollback timeline

### 5.3 Documentation
- [ ] Update incident log
- [ ] Record rollback decision and rationale
- [ ] Document any data loss or inconsistencies
- [ ] Document any manual interventions

### 5.4 Schedule Follow-Up
- [ ] Schedule post-mortem within 24 hours
- [ ] Identify v0.2.0 issue for hotfix
- [ ] Plan v0.2.1 hotfix release
- [ ] Document lessons learned

---

## Emergency Redo Procedure (if rollback fails)

**If v0.1.0-final deployment fails:**

```bash
# Stop v0.1.0-final attempt
systemctl stop application_service

# Restore database from savepoint
mysql < /scripts/restore_savepoint.sql

# Restore v0.2.0 deployment
tar -xzf /backups/v0.2.0_deployment_$(date +%s).tar.gz -C /opt/app/

# Restart with v0.2.0
systemctl start application_service

# Notify @mbaetiong: "Rollback failed, reverting to v0.2.0"
# Escalate to emergency response team
```

- [ ] If needed, execute redo procedure
- [ ] Notify incident commander
- [ ] Transition to hotfix strategy

---

## Rollback Decision Matrix

| Scenario | Decision | Time |
|----------|----------|------|
| Error rate >2% | ROLLBACK | Immediate |
| Data loss detected | ROLLBACK | Immediate |
| Service unavailable >5 min | ROLLBACK | Immediate |
| Latency p99 >1s | TBD by lead | 5 min |
| Error rate 0.5-1% | MONITOR | 10 min |
| Database issues | ROLLBACK | Immediate |
| Security vulnerability | ROLLBACK | Immediate |

---

## Communication Templates

### Rollback Initiated
```
🚨 INCIDENT RESPONSE: Initiating rollback to v0.1.0-final

Incident #: [ID]
Severity: CRITICAL
Reason: [Root cause]
ETA to completion: ~10 min
Status page: [URL]

Actions taken:
- v0.2.0 services stopped (T+2:00)
- v0.1.0-final deploying (T+3:00)
- Database rollback in progress (T+5:00)

We appreciate your patience.
```

### Rollback Successful
```
✅ SERVICE RECOVERY COMPLETE

Incident #: [ID]
Issue: [Brief description]
Duration: [X minutes]
Resolution: Rolled back to v0.1.0-final
Status: ✅ NORMAL

All services are operating normally. No further action required.
Post-incident analysis: [link to post-mortem]
```

---

## Abort Rollback Decision

**Only abort if:**
- Rollback cannot complete in <20 min
- Rollback causes more severe issues
- @mbaetiong explicitly authorizes

**Action if aborting:**
```
- Halt rollback attempt
- Restore v0.2.0 deployment
- Notify incident team immediately
- Escalate to emergency response
```

---

## Checklist Completion Sign-Off

**Rollback Executed By**: _________________ (Name)
**Date/Time**: _________________________ (UTC)
**Completion Status**: ☐ SUCCESSFUL ☐ PARTIAL ☐ FAILED
**Issues Encountered**: _________________________________
**Data Loss/Impact**: ___________________________________
**Follow-Up Actions**: __________________________________

**Verified By**: _________________ (Supervisor)
**Date/Time**: _________________________ (UTC)

---

**Last Updated**: 2026-07-16 20:05 UTC
**Next Verification**: Before each monitoring window
**Owner**: @mbaetiong
