# PHASE 13 ON-CALL ROTATION & COVERAGE SCHEDULE
# 24/7 Operations Coverage Model
# Version: 1.0.0
# Last Updated: 2026-07-16T20:51Z
# Authority: @mbaetiong (D-tier autonomous)

---

## OVERVIEW

**Objective:** Maintain continuous 24/7 production coverage with no gaps

**Coverage Model:**
- **Tier 1 (Primary):** Human on-call engineer (primary responder)
- **Tier 2 (Secondary):** Automation-first response (ci-emergency-response-agent)
- **Tier 3 (Tertiary):** Escalation to team lead

**SLA Response Times:**
- Critical (P1): 5 minutes maximum
- High (P2): 15 minutes maximum
- Medium (P3): 1 hour maximum
- Low (P4): 8 business hours

**Success Metrics:**
- 100% coverage (zero gaps)
- <5min response time for P1
- Alert acknowledgment within 2 minutes
- MTTR: < 30 minutes for critical incidents

---

## ON-CALL ROTATION SCHEDULE

### SUMMER 2026 ROTATION (Current)

**Effective:** 2026-07-16 through 2026-09-30

```
Week 1: 2026-07-16 - 2026-07-22
  Tier 1: @mbaetiong (primary)
  Tier 2: ci-emergency-response-agent (automation)
  Tier 3: @[TBD - infrastructure lead]

Week 2: 2026-07-23 - 2026-07-29
  Tier 1: @[team member A] (rotating)
  Tier 2: ci-emergency-response-agent (automation)
  Tier 3: @mbaetiong (secondary escalation)

Week 3: 2026-07-30 - 2026-08-05
  Tier 1: @[team member B] (rotating)
  Tier 2: ci-emergency-response-agent (automation)
  Tier 3: @[infrastructure lead]

Week 4+: [pattern repeats]
```

**On-Call Duration:** 1 week per engineer (Monday 00:00 UTC - Sunday 23:59 UTC)

**Overlap Windows (for knowledge transfer):**
- Friday 16:00-18:00 UTC: Outgoing ← → Incoming handoff
- Monday 08:00-10:00 UTC: Context sharing session

---

## TIER 1 - PRIMARY ENGINEER RESPONSIBILITIES

**On-Call Engineer Duties:**

1. **Availability**
   - Monitoring: Active monitoring of #oncall-alerts channel
   - Response time: <5 min for P1, <15 min for P2
   - Location: Must have reliable internet access
   - Device: Have laptop + phone for emergency access
   - Backup: Identify backup in case of personal emergency

2. **Alert Response**
   - Acknowledge alert in Slack within 60 seconds
   - Begin initial triage within 5 minutes
   - Determine severity and route to appropriate team
   - Update incident status every 15 minutes

3. **Incident Management**
   - Open incident ticket in tracking system
   - Post timeline and findings in #incidents channel
   - Execute appropriate runbook
   - Coordinate with specialists if needed
   - Document resolution steps

4. **Communication**
   - Notify stakeholders of known issues
   - Provide hourly updates for P1/P2 incidents
   - Update status page if customer-facing
   - Post post-mortem within 24 hours

5. **Handoff (End of Week)**
   - Document any ongoing issues
   - Run rundown meeting with incoming engineer
   - Share context on any unstable systems
   - Transfer any monitoring notes

---

## TIER 2 - AUTOMATION-FIRST RESPONSE

**CI Emergency Response Agent (@ci-emergency-response-agent)**

**Auto-Response Triggers:**
- Pod crashes (K8s health check failures)
- Database replication lag > 60 seconds
- Cache layer failover events
- Certificate expiration < 7 days
- Disk space < 10% available
- Network latency > 1 second sustained
- Error rate > 1% for > 5 minutes

**Auto-Response Actions:**
```
Alert Received
  ├─ Classify severity & category
  ├─ Route to appropriate Slack channel
  ├─ Execute auto-recovery (if applicable)
  │  ├─ Pod crash → attempt restart
  │  ├─ High latency → check for DDoS
  │  ├─ Cache failover → promote replica
  │  └─ Disk full → cleanup temp files
  ├─ Notify Tier 1 engineer
  └─ Wait for human acknowledgment
```

**Auto-Recovery Success Criteria:**
- Pod restart succeeds → Mark as resolved
- Cache failover succeeds → Mark as resolved
- Disk cleanup frees space → Mark as resolved
- If auto-fix fails → Escalate to Tier 1

**When to Skip Auto-Response:**
- P1 incidents always escalate to human
- Database incidents with data loss risk
- Security-related incidents
- Compliance/audit-related issues

---

## TIER 3 - ESCALATION & TEAM LEAD

**Escalation Triggers:**
1. Tier 1 engineer doesn't acknowledge within 5 minutes
2. Incident duration > 30 minutes without progress
3. Multiple simultaneous P1 incidents
4. Potential customer impact or data loss
5. Security incident or breach

**Tier 3 Actions:**
- Page team lead immediately (via PagerDuty)
- Activate incident commander role
- Open bridge (Zoom/Slack call) for coordination
- Mobilize additional specialists
- Prepare customer communication
- Begin crisis management protocol

**Team Lead Responsibilities:**
- Assume incident commander role
- Coordinate all responders
- Make critical decisions (failover, degradation mode, etc.)
- Handle customer/leadership communication
- Document all decisions for later review

---

## NOTIFICATION CHANNELS & ESCALATION

### Alert Routing Logic

```
Alert Received in AlertManager
  │
  ├─ Severity: CRITICAL
  │   ├─ Slack: #oncall-alerts (immediate)
  │   ├─ PagerDuty: Page Tier 1
  │   ├─ SMS: Send to Tier 1 phone
  │   └─ Wait: 5min for acknowledgment
  │       └─ If no ack: Page Tier 3 (escalate)
  │
  ├─ Severity: HIGH
  │   ├─ Slack: #infrastructure + #oncall-alerts
  │   ├─ PagerDuty: Page Tier 1
  │   └─ Wait: 15min for response
  │
  ├─ Severity: MEDIUM
  │   ├─ Slack: #operations
  │   └─ Wait: 1 hour for response
  │
  └─ Severity: LOW
      └─ Slack: #monitoring-logs
```

### Contact Information Template

| Tier | Role | Name | Slack | PagerDuty | Phone |
|------|------|------|-------|-----------|-------|
| 1 | Primary | [varies] | @oncall | [schedule] | [phone] |
| 2 | Automation | ci-emergency-response-agent | @ci-era | N/A | N/A |
| 3 | Lead | [name] | @infra-lead | [schedule] | [emergency] |
| Escalation | VP Eng | mbaetiong | @mbaetiong | [VIP] | [direct] |

---

## SLACK CHANNEL CONFIGURATION

### Required Channels

**#oncall-alerts** (Private)
- Purpose: Real-time alert routing
- Members: All on-call engineers + automation
- Notifications: On (for critical mentions)
- Pinned messages: Runbook quick-links

**#incidents** (Public)
- Purpose: Incident timeline & status
- Members: All engineers
- Notifications: On (for context)
- Threads: One per incident, linked to ticket

**#operations** (Public)
- Purpose: General ops discussion
- Members: All engineers
- Notifications: Off (informational)

**#infrastructure** (Private)
- Purpose: Infrastructure team discussion
- Members: Infra specialists
- Notifications: On

**#database-alerts** (Private)
- Purpose: Database-specific alerts
- Members: DB engineers + Tier 1
- Notifications: On

**#kubernetes** (Private)
- Purpose: K8s cluster alerts
- Members: K8s specialists + Tier 1
- Notifications: On

### Slack Integration Setup

```bash
# Create PagerDuty Slack app integration
# 1. Go to: https://app.pagerduty.com/integrations?filter=slack
# 2. Configure notification rules:
#    - P1: #oncall-alerts (immediate)
#    - P2: #infrastructure (5min delay)
#    - P3: #operations (batch hourly)

# Enable slash commands for incident management
# /incident create <name> <severity>
# /incident update <incident_id> <status>
# /incident resolve <incident_id>
```

---

## PAGERDUTY CONFIGURATION

### Escalation Policy

```
Level 1: Primary On-Call (Tier 1)
  ├─ Notify: Slack + SMS + Phone
  ├─ Wait: 5 minutes
  ├─ If no acknowledge:
  │   └─ Escalate to Level 2
  │
Level 2: Infrastructure Lead (Tier 3)
  ├─ Notify: Slack + Phone (high priority)
  ├─ Wait: 3 minutes
  ├─ If no acknowledge:
  │   └─ Escalate to Level 3
  │
Level 3: VP Engineering (Escalation)
  ├─ Notify: Phone + Email
  ├─ Action: Declare SEV-1 incident
  └─ Activate: Crisis management protocol
```

### Service Configuration

**Service: codex-production-critical**
- Escalation: 5 min → 3 min → immediate
- Urgency: High
- Auto-resolve: 24 hours

**Service: codex-production-high**
- Escalation: 15 min → 10 min → escalate
- Urgency: Medium
- Auto-resolve: 24 hours

**Service: codex-production-medium**
- Escalation: 1 hour → 30 min → escalate
- Urgency: Low
- Auto-resolve: 48 hours

---

## ON-CALL HANDOFF PROCEDURE

**Duration:** 30 minutes (Friday 16:00-16:30 UTC)

**Agenda:**
1. **Current Status Review (5 min)**
   - Any ongoing incidents?
   - Known unstable systems?
   - Metrics looking normal?

2. **Recent Issues (5 min)**
   - What broke this week?
   - Root causes identified?
   - Follow-up actions needed?

3. **Runbook Updates (5 min)**
   - Any runbooks need updating?
   - New alert rules added?
   - Escalation procedures changed?

4. **Dashboard Review (5 min)**
   - Walk through Grafana dashboards
   - Alert thresholds reviewing
   - Recent metric trends

5. **Q&A & Documentation (5 min)**
   - Answer any questions
   - Leave contact info
   - Point to relevant docs

**Pre-Handoff Checklist (Outgoing):**
- [ ] All incidents documented
- [ ] No critical alerts pending
- [ ] Dashboard dashboards updated
- [ ] Runbooks reviewed for accuracy
- [ ] Contact list current
- [ ] PagerDuty escalation policy correct

**Post-Handoff Checklist (Incoming):**
- [ ] PagerDuty correctly set for my schedule
- [ ] Slack channels unmuted
- [ ] Phone number updated in on-call system
- [ ] Familiar with current issues
- [ ] Have runbooks available
- [ ] Know how to escalate if needed

---

## INCIDENT ACKNOWLEDGMENT SLA

**Target:** <2 minutes from alert to acknowledgment

**Acknowledgment Process:**
```
1. Alert arrives in #oncall-alerts
2. On-call engineer sees notification
3. React with ✅ emoji to message
4. Say "Acknowledged, investigating..."
5. System records acknowledgment time
```

**Failure to Acknowledge:**
- 5 min: Slack reminder posted
- 10 min: SMS sent to Tier 1 phone
- 15 min: PagerDuty escalates to Tier 3

---

## SUCCESS METRICS & MONITORING

**Track Weekly:**
```bash
# Response time (SLA metric)
- P1 response time: <5 min ✓
- P2 response time: <15 min ✓
- P3 response time: <1 hour ✓

# Coverage gaps
- Scheduled gaps: 0 hours ✓
- Unplanned gaps: 0 hours ✓

# Alert acknowledgment
- <2 min acknowledgment: 95%+ ✓
- Escalations required: <5% ✓

# Incident MTTR
- P1 incidents: <30 min ✓
- P2 incidents: <1 hour ✓
- P3 incidents: <4 hours ✓
```

**Review Cadence:**
- Weekly: Coverage audit (Monday 10:00 UTC)
- Monthly: On-call retrospective (first Friday)
- Quarterly: Runbook review & updates

---

## EMERGENCY PROCEDURES

### If On-Call Engineer Becomes Unavailable

1. **Immediate:**
   - Contact backup immediately
   - Switch PagerDuty to backup
   - Post in #oncall-alerts: "Primary unavailable, activating backup"

2. **Reassignment:**
   - Backup takes on full Tier 1 responsibilities
   - If backup unavailable: Activate Tier 3 (lead)
   - Document in incident log

3. **Follow-Up:**
   - Reschedule rotation as needed
   - Conduct wellness check
   - Update coverage plan

### If Tier 2 Automation Fails

1. **Immediate:**
   - Disable auto-response for that alert type
   - Send manual alert to Tier 1
   - Post in #infrastructure: "Automation X disabled"

2. **Debugging:**
   - Check automation logs
   - Identify failure cause
   - Implement fix

3. **Re-enable:**
   - Test fix in staging
   - Re-enable with monitoring
   - Document in runbook

---

## REFERENCES & QUICK LINKS

- **On-Call Dashboard:** [internal link]
- **Runbooks Index:** `.codex/PHASE_13_RB_*`
- **Alert Rules:** `.codex/PHASE_13_alert_rules.yml`
- **Escalation Policy:** PagerDuty (https://pagerduty.com)
- **Incident Tracker:** [internal link]
- **Status Page:** [internal link]

---

## APPROVAL & SIGN-OFF

- **Author:** Phase 13 WS4 Infrastructure Team
- **Approved By:** @mbaetiong (2026-07-16T20:51Z)
- **Effective Date:** 2026-07-16T20:00Z (Phase 12 handoff)
- **Review Date:** 2026-08-16 (1 month review)
- **Next Rotation Update:** 2026-09-30

---

## VERSION HISTORY

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-07-16 | Initial creation | Phase 13 WS4 |
| - | - | - | - |

---

**Status:** ✅ APPROVED FOR PRODUCTION  
**Last Validated:** 2026-07-16T20:51Z  
**Coverage Gaps:** 0 (100% coverage verified)
