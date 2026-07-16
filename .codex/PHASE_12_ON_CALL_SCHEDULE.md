# Phase 12 On-Call Schedule
## 24/7 Incident Response Coverage (2026-07-16 → 2026-07-24)

**Monitoring Window**: v0.2.0 Post-Release (8 days)
**Coverage Model**: 3-tier escalation chain
**Contact Protocol**: PagerDuty for Severity 1 | Slack for Severity 2-3

---

## On-Call Roles & Responsibilities

### PRIMARY ON-CALL (@mbaetiong)
**Role**: Incident Commander for all Severity 1-2 incidents
**Responsibilities**:
- ✅ Respond to PagerDuty alerts <2 min
- ✅ Authorize critical remediation decisions
- ✅ Approve rollback to v0.1.0-final
- ✅ Escalate to management if needed
- ✅ Lead war room for Severity 1-2
- ✅ Sign-off on post-mortems

**Availability**: 24/7 (rotation)
**Contact**: PagerDuty (primary) | Phone (backup)
**Response SLA**: <2 min (CRITICAL)

### SECONDARY ON-CALL (ci-emergency-response-agent)
**Role**: Automated diagnostics & initial response
**Responsibilities**:
- ✅ Auto-respond to alerts <30 sec
- ✅ Collect diagnostics automatically
- ✅ Run preliminary RCA
- ✅ Escalate to primary if needed
- ✅ Suggest remediation options
- ✅ Monitor recovery metrics

**Availability**: 24/7 (automated)
**Response SLA**: <30 sec (auto)

### TERTIARY ON-CALL (workflow-health-monitor)
**Role**: Escalation routing & alerting
**Responsibilities**:
- ✅ Monitor alert queue
- ✅ Route alerts based on severity
- ✅ Track escalation timeline
- ✅ Notify secondary/primary
- ✅ Page management if needed
- ✅ Maintain incident chain

**Availability**: 24/7 (automated)
**Response SLA**: <1 min

---

## Active Rotation (Week of 2026-07-16)

### Week 1: 2026-07-16 → 2026-07-22

**Primary On-Call**:
```
Mon 07-16  00:00-23:59 UTC → @mbaetiong (DAY 1 START)
Tue 07-17  00:00-23:59 UTC → @mbaetiong
Wed 07-18  00:00-23:59 UTC → @mbaetiong
Thu 07-19  00:00-23:59 UTC → @mbaetiong
Fri 07-20  00:00-23:59 UTC → @mbaetiong
Sat 07-21  00:00-23:59 UTC → @mbaetiong
Sun 07-22  00:00-23:59 UTC → @mbaetiong
```

**Secondary On-Call**: ci-emergency-response-agent (24/7 automated)
**Tertiary On-Call**: workflow-health-monitor (24/7 automated)

### Week 2: 2026-07-22 → 2026-07-24

**Primary On-Call**:
```
Mon 07-22  00:00-23:59 UTC → @mbaetiong (continued)
Tue 07-23  00:00-23:59 UTC → @mbaetiong (continued)
Wed 07-24  00:00-12:00 UTC → @mbaetiong (WINDOW END)
```

**Note**: Rotation may shift if incidents require extended coverage

---

## Alert Notification Chain

### For Severity 1 (CRITICAL)

**Sequence**:
1. T+0:00 - Alert system fires (automated)
2. T+0:30 - ci-emergency-response-agent responds (diagnostics)
3. T+1:30 - Escalation check (if not resolved)
4. T+2:00 - PagerDuty pages @mbaetiong
5. T+2:01 - Slack notification #incident-critical
6. T+2:15 - War room activation (if needed)

**Notification Channels**:
- PagerDuty (primary to @mbaetiong)
- Slack #incident-critical (all team)
- SMS fallback (if PagerDuty fails)
- Phone call (if needed)

### For Severity 2 (HIGH)

**Sequence**:
1. T+0:00 - Alert fires
2. T+0:30 - ci-emergency-response-agent starts investigation
3. T+1:00 - Slack notification #incident-high
4. T+2:00 - Optional: Page @mbaetiong if not resolved

**Notification Channels**:
- Slack #incident-high (primary)
- Email backup

### For Severity 3 (MEDIUM)

**Sequence**:
1. T+0:00 - Alert logged
2. T+0:30 - Investigation started
3. T+4:00 - Slack notification #incident-medium

**Notification Channels**:
- Slack #incident-medium

### For Severity 4 (LOW)

**Sequence**:
1. T+0:00 - Logged to monitoring
2. No notifications (trend analysis only)

---

## Contact Information

### PRIMARY (@mbaetiong)

| Channel | Value | Availability |
|---------|-------|---------------|
| PagerDuty | @mbaetiong | 24/7 (push alert) |
| Slack | @mbaetiong | 24/7 (monitored) |
| Phone | [REDACTED] | 24/7 (emergency) |
| Email | [REDACTED] | 24/7 (backup) |

**Response Expectations**:
- PagerDuty: <2 min response
- Slack: <5 min response
- Phone: <1 min response

### SECONDARY (ci-emergency-response-agent)

| Channel | Value | Availability |
|---------|-------|---------------|
| Automated Response | ci-emergency-response-agent | 24/7 (<30 sec) |
| API Endpoint | /incident/respond | 24/7 |
| Logs | /var/log/incident_response.log | 24/7 |

### TERTIARY (workflow-health-monitor)

| Channel | Value | Availability |
|---------|-------|---------------|
| Alert Routing | workflow-health-monitor | 24/7 (<1 min) |
| Escalation Log | /var/log/escalation.log | 24/7 |

---

## Escalation Decision Tree

```
Incident Alert Fired
│
├─ Severity 1 (CRITICAL)
│  ├─ Auto-respond (T+0:30)
│  ├─ Check progress (T+1:30)
│  ├─ PAGE @mbaetiong (T+2:00) ✓
│  └─ War room (T+2:30) ✓
│
├─ Severity 2 (HIGH)
│  ├─ Auto-respond (T+0:30)
│  ├─ Slack alert (T+1:00)
│  ├─ Check progress (T+5:00)
│  └─ Escalate if not resolved by T+10:00
│
├─ Severity 3 (MEDIUM)
│  ├─ Log to system
│  ├─ Investigate <30 min
│  └─ No auto-escalation
│
└─ Severity 4 (LOW)
   └─ Trend analysis only
```

---

## Handoff Procedure

### End of On-Call Shift

**Outgoing On-Call**:
- [ ] Review active incidents
- [ ] Prepare handoff notes
- [ ] Brief incoming on-call
- [ ] Ensure monitoring system updated
- [ ] Verify escalation paths working

**Handoff Notes Template**:
```markdown
# Handoff Notes - [Date] [Time UTC]

## Active Incidents
- Incident #[ID]: [Status] [Brief]

## Recent Incidents
- Incident #[ID]: [Resolution] [Brief]

## Known Issues
- [Issue]: [Status] [Action needed]

## Monitoring Notes
- [Observation]: [Implication] [Action]

## Contact with Incoming On-Call
- Called/messaged at: [Time UTC]
- Confirmed receipt: [Time UTC]
```

---

## Schedule Updates & Changes

### Change Notification
- Schedule changes announced 48 hours in advance
- Backup on-call identified
- Handoff meetings scheduled
- All team notified

### Emergency Changes
- If primary unavailable: Secondary takes over automatically
- If secondary unavailable: Manual escalation to management
- All changes logged with timestamp

---

## Backup On-Call Coverage

**If Primary Unavailable**:
- Secondary (ci-emergency-response-agent) escalates to management
- Tertiary (workflow-health-monitor) pages backup on-call
- Backup on-call identified from secondary team

**If Secondary Unavailable**:
- Primary (@mbaetiong) handles all tiers
- Tertiary alerts for escalation
- Manual intervention required

**If Tertiary Unavailable**:
- Primary notified immediately
- All alerts to primary
- Manual follow-up to backup

---

## On-Call Best Practices

### Before Shift
- ✅ Confirm availability
- ✅ Test notification channels
- ✅ Review recent incidents
- ✅ Verify access to systems
- ✅ Update location/phone

### During Shift
- ✅ Monitor alerts closely
- ✅ Respond within SLA
- ✅ Document all actions
- ✅ Escalate when needed
- ✅ Keep team informed

### After Shift
- ✅ Handoff to next on-call
- ✅ Document open incidents
- ✅ Update runbooks if needed
- ✅ Provide feedback
- ✅ Attend post-mortems

---

## SLA Tracking

### Response Time SLAs

| Severity | Target Response | Tracked | Owner |
|----------|------------------|---------|-------|
| 1-CRITICAL | <2 min | YES | ci-emergency-response-agent + @mbaetiong |
| 2-HIGH | <10 min | YES | ci-emergency-response-agent |
| 3-MEDIUM | <30 min | YES | Incident system |
| 4-LOW | None | NO | Monitoring |

### SLA Violations

**Severity 1 missed SLA**:
- Auto-escalate to management
- Post-incident review mandatory
- Pattern analysis required

**Severity 2 missed SLA**:
- Log violation
- Review in weekly meeting
- Escalate if recurring

---

## Post-Mortem Scheduling

### Within 24 Hours (Severity 1)
- [ ] Schedule post-mortem
- [ ] Invite primary on-call + team
- [ ] Reserve war room
- [ ] Prepare incident data

### Within 48 Hours (Severity 2)
- [ ] Schedule post-mortem (if high impact)
- [ ] Invite relevant stakeholders
- [ ] Prepare analysis

### Routine Schedule
- [ ] Weekly incident review (Monday 10:00 UTC)
- [ ] Monthly on-call retrospective (1st Monday)

---

## Off-Hours Support

### Weekend Coverage
- Full primary on-call coverage
- Reduced secondary team on standby
- Critical-only escalation threshold

### Holidays
- Dedicated on-call assigned
- Extended handoff process
- Management backup available

---

## Communication Templates

### Shift Start
```
🔔 @mbaetiong is now PRIMARY ON-CALL for Phase 12 (v0.2.0 monitoring)

Status: ✅ READY
Channels: PagerDuty (critical), Slack (all)
Rollback: Ready (v0.1.0-final verified)

Previous incidents: [count] (details in incident log)
Known issues: [list if any]

Thank you for 24-hour coverage!
```

### Shift End
```
🔄 @mbaetiong off-call, handoff complete

Duration: 24 hours
Incidents handled: [count]
SLA compliance: [%]
Current status: [status]

Incidents logged in `.codex/PHASE_12_INCIDENT_LOG_2026_07_17.md`
```

---

**Last Updated**: 2026-07-16 20:05 UTC
**Schedule Type**: Fixed primary rotation
**Review Frequency**: Daily during monitoring window
**Next Change**: 2026-07-23 (if needed)
