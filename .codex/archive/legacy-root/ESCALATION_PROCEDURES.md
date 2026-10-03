# Escalation Procedures

**Status:** DRAFT - Review before production use  
**Last Updated:** 2026-06-20T09:00:00Z  

---

## Table of Contents

1. [Escalation Triggers](#escalation-triggers)
2. [Escalation Paths](#escalation-paths)
3. [Approval Authority](#approval-authority)
4. [Emergency Procedures](#emergency-procedures)
5. [Contact Information](#contact-information)

---

## Escalation Triggers

### Severity Classification

Incidents are classified by severity to determine escalation level and urgency:

#### 🔴 CRITICAL (SEV-1)
- **Definition:** Service completely down, all users affected, data loss risk
- **Response Time:** Immediate (< 5 minutes)
- **Escalation Path:** Immediate to L3 (Director of Engineering)
- **Examples:**
  - Service 100% down
  - Data corruption detected
  - Security breach suspected
  - Financial systems offline
  - Customer data at risk

**Escalation Actions:**
1. Page on-call engineer (immediate)
2. Page engineering manager (within 2 min)
3. Notify VP Engineering (within 5 min)
4. Notify CTO (within 10 min)
5. Initiate war room (Zoom + Slack channel)

#### 🟠 HIGH (SEV-2)
- **Definition:** Partial service degradation, some users affected, significant business impact
- **Response Time:** < 15 minutes
- **Escalation Path:** L2 (Engineering Manager) if not resolved in 15 min
- **Examples:**
  - API errors affecting 25%+ of requests
  - Authentication system partially down
  - Data inconsistency detected
  - Performance degradation > 50%
  - Customer complaints increasing

**Escalation Actions:**
1. Page on-call engineer (immediate)
2. Page engineering manager (within 5 min if ongoing)
3. Create Slack incident channel
4. Notify product manager (if customer-facing)
5. Initiate daily standup if ongoing > 1 hour

#### 🟡 MEDIUM (SEV-3)
- **Definition:** Minor degradation, limited user impact, workaround available
- **Response Time:** < 1 hour
- **Escalation Path:** L2 if not resolved in 1 hour
- **Examples:**
  - API errors affecting 5-25% of requests
  - Performance degradation 10-50%
  - Non-critical feature unavailable
  - Sporadic errors on specific endpoints

**Escalation Actions:**
1. Assign to on-call engineer
2. Create ticket in incident tracking system
3. Notify team lead (if ongoing > 30 min)
4. Update status page (if customer-facing)

#### 🟢 LOW (SEV-4)
- **Definition:** Minimal impact, workaround available, scheduled fix acceptable
- **Response Time:** < 4 hours
- **Escalation Path:** Bug queue (no escalation required)
- **Examples:**
  - Non-critical errors in logs
  - Deprecated API warnings
  - Documentation issues
  - Cosmetic UI glitches

**Escalation Actions:**
1. Create bug report
2. Schedule for next sprint
3. No escalation required

---

## Escalation Paths

### Standard Escalation Path (SEV-1 / SEV-2)

```
┌─────────────────────────────────────┐
│ Incident Detection / Alert Triggered│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ L1: On-Call Engineer                │
│ (Initial response, triage)          │
│ Response Time: < 5 min              │
│ Contact: PagerDuty auto-page        │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
   RESOLVED    NOT RESOLVED (> 15 min)
      │             │
      │             ▼
      │  ┌─────────────────────────────┐
      │  │ L2: Engineering Manager     │
      │  │ (Coordinate response)       │
      │  │ Contact: [ops-manager]      │
      │  └────────────┬────────────────┘
      │               │
      │      ┌────────┴────────┐
      │      │                 │
      │   RESOLVED      NOT RESOLVED (> 30 min)
      │      │                 │
      │      │                 ▼
      │      │   ┌──────────────────────┐
      │      │   │ L3: Director/VP Eng  │
      │      │   │ (Strategic decisions)│
      │      │   │ Contact: [vp-eng]    │
      │      │   └────────────┬─────────┘
      │      │                │
      │      │      ┌─────────┴──────────┐
      │      │      │                    │
      │      │   DECISION          NOT RESOLVED (> 1 hour)
      │      │      │                    │
      │      │   [Rollback/Patch]        ▼
      │      │      │          ┌──────────────────┐
      │      │      │          │ CTO/CEO          │
      │      │      │          │ (Executive awareness)
      │      │      │          │ Contact: [cto]   │
      │      │      │          └──────────────────┘
      │      │      │
      └──────┴──────┘
             │
             ▼
        RESOLVED
```

### Approval Authority by Action

| Action | Authority | Escalation Level | Response Time |
|--------|-----------|-----------------|----------------|
| Rollback deployment | L1 oncall + L2 approval | L2 | < 5 min |
| Kill pods manually | L2+ only | L2 | < 10 min |
| Database modification | L3 + DBA | L3 | < 15 min |
| Scale down services | L1 oncall | L1 | Immediate |
| Scale to 0 replicas | L2+ only | L2 | < 10 min |
| Data restoration | L3 + DBA | L3 | < 30 min |
| Customer notification | L2 + Product | L2 | < 30 min |
| Executive notification | L3+ | L3 | < 15 min |

---

## Escalation Contacts

> **Note:** This file references `ESCALATION_CONTACTS.md` for actual contact information (sanitized separately)

### L1: On-Call Engineer

**Primary Method:** PagerDuty automatic page  
**Escalation Time:** 5 minutes  
**Backup Method:** Slack @oncall-eng

**Responsibilities:**
- Initial triage and diagnosis
- Execute runbooks and procedures
- Coordinate with other teams
- Keep stakeholders updated every 15 minutes

### L2: Engineering Manager / Team Lead

**Primary Method:** Manual escalation via Slack / phone  
**Escalation Time:** 15 minutes  
**Contact:** See `ESCALATION_CONTACTS.md`

**Responsibilities:**
- Coordinate broader team response
- Make rollback decisions
- Manage stakeholder communication
- Allocate additional resources

### L3: Director of Engineering / VP

**Primary Method:** Manual escalation via phone / emergency line  
**Escalation Time:** 30 minutes  
**Contact:** See `ESCALATION_CONTACTS.md`

**Responsibilities:**
- Make strategic decisions
- Executive decision authority
- Customer escalation sign-off
- Post-incident leadership

### CTO / CEO (if SEV-1)

**Primary Method:** VP Engineering → automatic escalation  
**Escalation Time:** 15 minutes  
**Contact:** See `ESCALATION_CONTACTS.md`

**Responsibilities:**
- Strategic company decisions
- Customer relationship management
- Media/public relations coordination
- Financial impact assessment

---

## Emergency Procedures

### Immediate Action (First 5 Minutes)

1. **Page on-call engineer immediately**
   ```bash
   # Via PagerDuty
   - Trigger incident in PagerDuty
   - Select service/escalation policy
   - Incident automatically pages on-call
   ```

2. **Create Slack incident channel**
   ```
   #incident-YYYYMMDD-HHMM
   ```

3. **Notify team**
   ```bash
   # Post to #incidents channel
   @on-call-eng @team Incident declared SEV-[1-4]
   Details: [brief description]
   Actions: [what we're doing]
   ```

4. **Start incident timeline**
   - Record start time
   - Begin logging all actions
   - Update every 15 minutes

### Critical Path Decision Tree

```
INCIDENT DETECTED
       │
       ▼
Can it be fixed in < 5 min?
       │
    YES│NO
       │  │
       │  ▼
       │  Is service down?
       │       │
       │    YES│NO
       │       │  │
       │       │  ▼
       │       │  Is data corrupted?
       │       │       │
       │       │    YES│NO
       │       │       │  │
       │       │       │  ▼
       │       │       │  Wait & Monitor (< 1 hour)
       │       │       │       │
       │       │       │   RESOLVED? YES
       │       │       │       │
       │       │       └───┬───┘
       │       │           │
       │       ▼           ▼
       │   ROLLBACK    CLOSE
       │       │
       │       ▼
       │   SUCCESS? YES
       │       │
       └───┬───┘
           │
           ▼
        RESOLVED
```

### Rollback Decision Authority

**Who can authorize rollback:**

| Scenario | Authority | Time Limit |
|----------|-----------|-----------|
| Service completely down | L1 oncall (auto-authorized) | Immediate |
| Data corruption detected | L2+ required | < 10 min |
| Database modifications | L3 + DBA | < 15 min |
| Config issues | L1 oncall | Immediate |
| Memory leaks | L2 | < 5 min |

**Rollback without approval if:**
- Service completely down (100% errors)
- Data corruption confirmed
- Security breach detected
- Customer data at risk

**Must get approval if:**
- Partial degradation (< 100%)
- Uncertain cause
- New deployment with unknown issues
- Any change affecting billing

---

## Communication Escalation

### Initial Communication (0-5 min)

- **Internal Only:** Slack #incidents channel
- **Message:** "Incident SEV-[1-4]: [Service] [Impact]"
- **No external communication yet**

### Escalated Communication (5-15 min)

- **If SEV-1:** Notify VP Engineering immediately
- **If SEV-1:** Notify Product Manager
- **If SEV-1:** Prepare customer notification

### External Communication (15+ min)

- **Decision Authority:** L2 + Product Manager
- **Channels:**
  - Status page update
  - Email to affected customers
  - Social media (if widespread)
  - Customer support scripting

- **Message Template:** See `STAKEHOLDER_NOTIFICATION.txt`

### Post-Incident Communication (After resolution)

- **All-Clear Message:** "Incident resolved at [time]"
- **Post-Mortem Scheduled:** Within 24 hours
- **Timeline:** Share within 48 hours
- **Blameless Culture:** Focus on systems, not people

---

## Escalation Failure Points

### What if Escalation Path Fails?

**If L1 oncall doesn't respond (5 min):**
1. Send emergency Slack message to #incidents
2. Call ops on emergency line
3. Escalate to L2 immediately
4. PagerDuty will escalate automatically (check settings)

**If L2 doesn't respond (15 min):**
1. Call L2 manager backup number
2. Call VP Engineering directly
3. Escalate to CTO if SEV-1
4. Decision authority goes to next available person

**If executives not responding (30 min+):**
1. Call emergency escalation number (see ESCALATION_CONTACTS.md)
2. Invoke emergency decision protocol
3. L1/L2 engineers can make decisions if no authority available
4. Document emergency decision process

---

## Authority & Accountability

### Authority Chain

```
Incident Commander (highest authority on scene)
  ├─ Decision: Technical procedures and tactics
  └─ Approval: Rollback, scaling, data restoration

L2 Engineering Manager
  ├─ Decision: High-level strategy
  ├─ Approval: Major changes, customer communication
  └─ Notify: VP and Product Manager

VP Engineering
  ├─ Decision: Executive-level strategy
  ├─ Approval: CEO notification, media response
  └─ Authority: Final decision if conflict

CTO / CEO (SEV-1 only)
  ├─ Decision: Company-wide impact decisions
  ├─ Approval: Public statements, customer remediation
  └─ Authority: Highest level decision making
```

### Decision Documentation

Every decision during incident must be documented:
- **What:** Decision made
- **When:** Timestamp (ISO 8601)
- **Who:** Decision authority name/role
- **Why:** Rationale for decision
- **Result:** Outcome of decision

Example:
```
2026-06-20 09:45:12Z - Rollback decision
Authority: John Smith (L2 Engineering Manager)
Rationale: Error rate 50%, customer complaints, cause unknown
Decision: Rollback to previous version
Result: Service recovered, error rate < 1%
```

---

## Regular Updates

The escalation procedures will be reviewed:
- **Monthly:** For improvements and feedback
- **After Each SEV-1:** For lessons learned
- **Quarterly:** For process updates
- **Annually:** For complete audit

**Last Review:** 2026-06-20  
**Next Review:** 2026-07-20  
**Review Authority:** VP Engineering

---

## See Also

- `.codex/rollback-procedures.md` - Technical rollback procedures
- `.codex/ESCALATION_CONTACTS.md` - Contact information
- `.codex/incident-templates/` - Communication templates
- `.codex/ROLLBACK_VALIDATION_CHECKLIST.md` - Validation procedures
