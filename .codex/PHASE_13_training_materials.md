# PHASE 13 TRAINING MATERIALS & GUIDES
# Team Onboarding & Knowledge Base
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z

---

## 1. GRAFANA DASHBOARD NAVIGATION GUIDE

### Getting Started

1. **Access:** https://grafana.example.com (OAuth2 login)
2. **First Time Setup:** 
   - Click "Home" → "Browse"
   - Pin your favorite dashboards
   - Set theme (Settings → Profile → Dark Mode)

### Dashboard: "SLA Status" (Most Important)

**What It Shows:**
- Green gauge: Uptime % (target: >99.9%)
- Red line graph: Error rate % (target: <0.05%)
- Yellow line: Latency p95 (target: <350ms)
- Heatmap: Resource utilization (CPU/mem/disk/net)

**How to Read It:**
- Green = All good, no action needed
- Yellow = Warning level, monitor closely
- Red = Alert threshold crossed, escalate

**What To Do If Something's Red:**

1. Click on the red metric (opens detailed view)
2. Look at the time range (when did it spike?)
3. Check the related metrics (cause detection)
4. Decide:
   - Can wait 15 min? → #operations channel
   - Urgent? → @oncall in Slack
   - Crisis? → Escalate to Tier 3

### Dashboard: "Application Performance"

**Metrics:**
- Requests/second (throughput)
- Latency breakdown (by endpoint)
- Error rate (by status code)
- Top slow endpoints

**How to Use:**
- Spot trends: Is throughput increasing/decreasing?
- Find bottlenecks: Which endpoint is slowest?
- Debug errors: Are 5xx errors increasing?

### Dashboard: "Database Health"

**Metrics:**
- Query latency p95, p99, p99.9
- Replication lag (should be <1 sec)
- Connection count (warning: >300)
- Active queries (identify long-runners)

**Action Thresholds:**
- Latency p95 >300ms: Run slow query analysis
- Replication lag >30 sec: Alert, possible failover
- Connections >300: May need pool tuning

### Dashboard: "Kubernetes Cluster"

**Metrics:**
- Pod restart count (should be <1 per day/pod)
- Node CPU/Memory (warning: >85%)
- Failed pods (should be 0)
- Persistent volume usage

**Common Issues:**
- Pod CrashLoopBackOff: Check recent logs
- Node at 95% CPU: May need scaling
- PVC almost full: Clean up or expand

---

## 2. INCIDENT RESPONSE PLAYBOOK

### When You Get Paged

**Immediate (0-1 min):**
```
1. Wake up! ☎️
2. Open Slack
3. Go to #oncall-alerts
4. Look for your page alert
5. Read the alert text carefully
```

**Acknowledgment (1-2 min):**
```
1. React ✅ to the alert message
2. Say: "Acknowledged, investigating..."
3. Take a screenshot (for documentation)
4. Grab your runbook (see Step 4)
```

**Diagnosis (2-5 min):**
```
1. Ask: Is this real or a false alarm?
   - Check Grafana dashboard
   - Query recent logs
   - Test connectivity manually
   
2. If false alarm:
   - Post: "False positive - [reason]"
   - Disable alert (if recurring)
   - Mark resolved in PagerDuty
   
3. If real issue:
   - Proceed to Step 4
```

**Response (5-30 min):**
```
1. Find the correct runbook
   Location: .codex/PHASE_13_RB_[type].md
   
2. Follow the runbook step-by-step
   - Don't skip steps!
   - Take notes on what you do
   
3. Document actions:
   - Screenshot before/after
   - Note any unexpected behavior
   
4. Verify fix:
   - Metrics return to green
   - Services respond normally
   - No side effects
```

**Communication (Ongoing):**
```
1. Every 15 minutes:
   - Post status update in #incidents thread
   - Example: "Still investigating DB latency. Checking query logs now."
   
2. When resolved:
   - Post: "RESOLVED: [issue] - [brief fix description]"
   - Set PagerDuty incident to "Resolved"
```

**Post-Incident (Next day):**
```
1. Write post-mortem (use template in runbook)
2. Identify root cause
3. Add action items (prevent recurrence)
4. Share summary in #incidents
```

---

## 3. ESCALATION DECISION TREE

**Decision 1: Tier 2 Auto-Response?**

```
Is it a pod crash?
  → YES: Wait 1 min (auto-restart)
  → NO: Continue

Is it a cache failover?
  → YES: Wait 30 sec (auto-failover)
  → NO: Continue

Is it a cleanup task (disk full)?
  → YES: Auto-script will handle
  → NO: Continue

→ RESULT: Needs manual response (go to Decision 2)
```

**Decision 2: Can I Fix It?**

```
Do I know which runbook to use?
  → YES: Follow the runbook
  → NO: Ask in #infrastructure or escalate

Am I making progress?
  → YES: Continue (up to 30 min)
  → NO: Escalate now (don't waste time)

Have I tried the runbook steps 1-3?
  → YES: Continue
  → NO: Do not skip steps!

Is it taking >30 min?
  → YES: Escalate to Tier 3
  → NO: Keep going
```

**Decision 3: Escalate to Tier 3?**

```
Is it a P1 incident?
  → YES: Escalate after 5 min if not making progress
  → NO: May not need escalation

Is it taking >30 min?
  → YES: Escalate now
  → NO: Keep trying

Is customer impact?
  → YES: Escalate
  → NO: Can wait

→ RESULT: Page Tier 3 lead via PagerDuty
   Or: Direct Slack to @[tier3-lead] if urgent
```

---

## 4. ON-CALL ROTATION & EXPECTATIONS

### Your On-Call Week

**Monday 00:00 - Sunday 23:59 (UTC)**

**Daily Routine:**
- Morning: Check dashboard for any overnight issues
- Throughout day: Monitor #oncall-alerts
- Evening: Review SLA metrics
- Before bed: Ensure phone is charged & notifications on

**Friday Handoff (16:00 UTC):**
- Call with outgoing engineer (30 min)
- Ask about recent issues & unstable systems
- Get their contact info for emergencies
- Review Grafana dashboards together

**Response Times (SLA):**
- P1 alerts: Acknowledge within 2 min, respond <5 min
- P2 alerts: Acknowledge within 5 min, respond <15 min
- P3 alerts: Acknowledge within 15 min, respond <1 hour

**What You Have:**
- All 12 runbooks (`.codex/PHASE_13_RB_*.md`)
- Dashboard access (24/7)
- Slack access & on-call channels
- PagerDuty access
- SSH to production (with proper auth)

**What You Don't Need to Know:**
- Every internal detail (runbooks guide you)
- How to code-fix production bugs (that's engineers)
- Every possible edge case (escalate if unsure)

### Coverage Gaps (Prevention)

- Sick? Notify on-call team ASAP → activate backup
- Vacation? Ensure coverage beforehand (rotate)
- Emergency? Use PagerDuty to transfer pages

---

## 5. COMMON SCENARIOS & RESPONSES

### Scenario 1: Database Latency Alert

```
Alert: "database_query_latency_p95 > 350ms"

What to do:
1. Check Grafana: Is p95 really high?
2. Query slow logs:
   psql -d codex_prod -c "SELECT query, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 5;"
3. Look for:
   - New query (recent deploy?)
   - Missing index?
   - Table bloat (VACUUM)?
4. If identified:
   - Execute fix (add index, vacuum, etc.)
   - Monitor latency return to green
5. If not identified:
   - Escalate to database team
   - Run runbook: PHASE_13_RB_query_performance.md
```

### Scenario 2: Pod Crashing

```
Alert: "kubernetes_pod_crash_loop"

What to do:
1. Check pod status:
   kubectl get pods -n production | grep crash
2. Get pod logs:
   kubectl logs [pod-name] -n production --previous
3. Identify reason:
   - OutOfMemory? → Increase limits
   - Segfault? → Report bug to dev team
   - Connection refused? → Check DB/cache
4. Kubernetes will auto-restart
5. Monitor for recurring crashes
6. If crashes continue → escalate

Note: Runbook handles this (PHASE_13_RB_pod_crash_recovery.md)
```

### Scenario 3: High Error Rate

```
Alert: "error_rate_high (>0.05%)"

What to do:
1. Check which errors:
   curl -s https://prometheus:9090/api/v1/query?query=http_requests_total | jq '.data.result[] | select(.value[1] | tonumber > 0)'
2. Group by status code:
   - 500s: Application bug (check recent deploy)
   - 503s: Service down (check dependencies)
   - 504s: Timeout (check latency)
3. Determine scope:
   - Single endpoint? → Fix that endpoint
   - All endpoints? → Infrastructure issue
4. Escalate if needed

Note: Runbook available (but usually straightforward)
```

---

## 6. RUNBOOK QUICK REFERENCE

**When to Use Each Runbook:**

| Alert | Runbook | RTO |
|-------|---------|-----|
| Database down | PHASE_13_RB_database_failover.md | 5 min |
| Cache unresponsive | PHASE_13_RB_cache_failover.md | 2 min |
| Pod CrashLoopBackOff | PHASE_13_RB_pod_crash_recovery.md | 1 min |
| Memory climbing | PHASE_13_RB_memory_leak_detection.md | 10 min |
| Latency spike | PHASE_13_RB_network_latency.md | 5 min |
| Query slow | PHASE_13_RB_query_performance.md | 15 min |
| External API down | PHASE_13_RB_dependency_outage.md | 15 min |
| Disk almost full | PHASE_13_RB_storage_capacity.md | 2 min |
| LB not healthy | PHASE_13_RB_lb_health_check.md | 5 min |
| Security detected | PHASE_13_RB_security_incident.md | 5 min |
| Cert expiring | PHASE_13_RB_ssl_renewal.md | N/A |
| Audit coming | PHASE_13_RB_compliance_audit.md | 1 hour |

**Location:** All in `.codex/PHASE_13_RB_*.md`

---

## 7. FAQ (FREQUENTLY ASKED QUESTIONS)

**Q: What if I don't know what to do?**
A: Don't guess. Escalate immediately. Better safe than sorry.

**Q: Can I make changes to production?**
A: Only if the runbook explicitly says so. Otherwise escalate.

**Q: How do I know if I fixed it?**
A: Grafana metrics should return to green within 5 min of fix.

**Q: What if the runbook doesn't match my situation?**
A: Document what's different and escalate to specialist team.

**Q: Can I delegate the work?**
A: Only if they're an on-call backup (pre-arranged). Otherwise you own it.

**Q: How long should I wait before escalating?**
A: P1: 5 min. P2: 15 min. P3: 1 hour. If no progress by then, escalate.

**Q: What if I'm on call but can't respond?**
A: Transfer pages to backup ASAP in PagerDuty. Don't leave a gap.

**Q: Can I take on-call time off?**
A: Yes, arrange swap with another engineer beforehand.

---

## 8. METRICS TO KNOW

**You Don't Need to Memorize These, But Know Where to Find Them:**

**SLA Dashboard:**
- Uptime: 99.9% target (red if <99%)
- Error rate: 0.05% target (red if >0.1%)
- Latency p95: 350ms target (red if >500ms)

**Database:**
- Query latency p95: 150ms target
- Replication lag: <1 sec (alert: >30 sec)
- Connections: <300 (alert: >350)

**Infrastructure:**
- CPU: <70% (alert: >85%)
- Memory: <75% (alert: >90%)
- Disk: <80% (alert: >90%)
- Network: <70% link (alert: >80%)

**All Metrics:** Grafana "SLA Status" dashboard (real-time)

---

## 9. TEAM CONTACTS

| Role | Name | Slack | Phone |
|------|------|-------|-------|
| VP Engineering | @mbaetiong | Direct | [emergency] |
| DB Lead | [name] | @db-lead | [phone] |
| Infra Lead | [name] | @infra-lead | [phone] |
| Current On-Call | [rotation] | @oncall | [phone] |

---

## 10. TRAINING CHECKLIST

**Before Your First On-Call:**

- [ ] Read "Operations Model" (PHASE_13_operations_model.md)
- [ ] Review 5 key runbooks
- [ ] Know how to access Grafana dashboard
- [ ] Know how to escalate (PagerDuty + Slack)
- [ ] Have backup contact info
- [ ] Shadow on-call engineer (at least 1 shift)
- [ ] Participate in dry-run incident
- [ ] Pass knowledge assessment

**Ongoing:**

- [ ] Monthly runbook review
- [ ] Quarterly disaster recovery drill
- [ ] Review recent incidents
- [ ] Update personal contact info annually

---

**Status:** ✅ TRAINING COMPLETE  
**Last Updated:** 2026-07-16T20:51Z  
**Next Training Session:** [TBD]
