# Escalation Contacts

**Status:** DRAFT - Fill in with actual contact information  
**Last Updated:** 2026-06-20T09:00:00Z  
**Sensitive:** YES - Do not commit to public repository

---

## Contact Information

### Important Security Note

This file contains contact information for critical personnel. It should be:
- ✅ Stored in a secure location (not committed to Git)
- ✅ Protected by RBAC
- ✅ Accessible to on-call staff 24/7
- ✅ Updated whenever contact information changes
- ✅ Reviewed quarterly for accuracy

### L1: On-Call Engineer

**Primary Contact Method:** PagerDuty (automatic page)  

| Name | Role | Phone | Email | Slack | Available |
|------|------|-------|-------|-------|-----------|
| [Team rotation] | On-Call Eng | [XXX-XXX-XXXX] | [email] | @oncall-eng | 24/7 |

**Backup Contacts:**
- Slack channel: `#incident-response-sme`
- Email list: `oncall-engineers@company.com`

**How to reach:**
1. Trigger PagerDuty incident
2. If not responding (5 min): Call backup number
3. If still no response: Escalate to L2

---

### L2: Engineering Manager

**Primary Contact Method:** Manual page or Slack  
**Escalation Time:** 15 minutes for SEV-1

| Name | Title | Phone | Email | Slack | Timezone |
|------|-------|-------|-------|-------|----------|
| [Manager Name] | Eng Manager | [XXX-XXX-XXXX] | [email] | @[slack] | [TZ] |
| [Manager Name] | Eng Manager | [XXX-XXX-XXXX] | [email] | @[slack] | [TZ] |

**How to reach (in order):**
1. Slack direct message `@manager-name`
2. Phone call to listed number
3. Email with "URGENT: SEV-1 Incident" in subject
4. SMS to backup number (if critical)

---

### L3: Director of Engineering

**Primary Contact Method:** Phone (emergency escalation)  
**Escalation Time:** 30 minutes for SEV-1

| Name | Title | Phone | Email | Slack | Backup Phone |
|------|-------|-------|-------|-------|--------------|
| [Director Name] | Dir Engineering | [XXX-XXX-XXXX] | [email] | @[slack] | [Backup] |

**Emergency Line (24/7):**
```
[Emergency number] - Press option [X] for incidents
```

**How to reach:**
1. Call listed phone number
2. If busy, try backup phone
3. If no answer, call emergency line
4. All L2 managers to escalate immediately

---

### VP Engineering

**Primary Contact Method:** Phone (emergency escalation only)  
**Escalation Time:** < 15 minutes for SEV-1

| Name | Title | Phone | Email | Slack | Backup Phone |
|------|-------|-------|-------|-------|--------------|
| [VP Name] | VP Engineering | [XXX-XXX-XXXX] | [email] | @[slack] | [Backup] |

**Emergency Procedures:**
- Only escalate for SEV-1 incidents
- L3 makes initial contact
- Emergency protocols activate

---

### CTO / CEO (SEV-1 Critical Only)

| Name | Title | Phone | Email | Notes |
|------|-------|-------|-------|-------|
| [CTO Name] | CTO | [XXX-XXX-XXXX] | [email] | Via VP only |
| [CEO Name] | CEO | [XXX-XXX-XXXX] | [email] | Via CTO/VP only |

**Protocol:**
- VP Engineering escalates
- VP provides executive summary
- CTO/CEO notified, not directly contacted

---

## External Escalation Contacts

### Customer Success Lead

**Contact:** [Name]  
**Phone:** [XXX-XXX-XXXX]  
**Email:** [email]  
**Role:** Customer communication for SEV-1/SEV-2

**Responsibilities:**
- Draft customer communication
- Coordinate with affected customers
- Track customer impact
- Plan remediation communication

---

### Database Administrator (DBA)

**Contact:** [Name]  
**Phone:** [XXX-XXX-XXXX]  
**Email:** [email]  
**Slack:** @dba-oncall  

**Escalation Triggers:**
- Data corruption detected
- Database unavailable
- Data recovery needed
- Backup restoration required

---

### Security Team

**Contact:** [Name / Security Lead]  
**Email:** `security-incidents@company.com`  
**Phone:** [XXX-XXX-XXXX]  
**Slack:** @security-team  

**Escalation Triggers:**
- Security breach suspected
- Unauthorized access detected
- Credentials compromised
- Data exposure risk

---

### Infrastructure / Operations

**Contact:** [Name / Ops Lead]  
**Phone:** [XXX-XXX-XXXX]  
**Email:** `ops-team@company.com`  
**Slack:** @ops-team  

**Escalation Triggers:**
- Infrastructure failure
- Cloud provider issues
- Network problems
- Datacenter issues

---

## Communication Preferences

### Preferred Contact Methods (in order)

**For L1/L2 (Routine):**
1. Slack direct message
2. Phone call
3. Email

**For L3/VP (Urgent):**
1. Phone call
2. SMS to backup
3. Emergency number

**For Incidents (Any level):**
1. PagerDuty (automatic)
2. Slack #incidents
3. Direct phone call

### Timezone Considerations

| Person | Primary TZ | Secondary | Overlap Hours |
|--------|-----------|-----------|----------------|
| [Name] | [TZ] | [TZ] | [Hours UTC] |
| [Name] | [TZ] | [TZ] | [Hours UTC] |

**Coverage Goal:** 24/7 with <15 min response time  
**Current Coverage:** [X hours / 24 hours]

---

## Outage Notification List

### Immediate Notification (< 5 min)

- [X] L1 Oncall (automatic via PagerDuty)
- [X] L2 Manager (manual escalation)
- [X] #incidents Slack channel

### Secondary Notification (5-15 min)

- [ ] Product Manager
- [ ] Customer Success Lead
- [ ] Marketing (if public impact)

### Tertiary Notification (15-30 min)

- [ ] VP Engineering
- [ ] CTO (if SEV-1)
- [ ] Finance (if revenue impact)

### Executive Notification (> 30 min)

- [ ] CEO (if public incident or major business impact)
- [ ] Board (if required by governance)

---

## Testing & Validation

### Quarterly Contact Verification

- **Schedule:** First Monday of each quarter
- **Method:** Call each contact to verify current information
- **Owner:** HR / Ops Manager
- **Frequency:** Q1, Q2, Q3, Q4

### Change Protocol

When contact information changes:
1. Notify the primary escalation team
2. Update this file
3. Verify changes with test call
4. Email stakeholders of update
5. Wait 24 hours before using in production

**Notification Template:**
```
Subject: Update - Escalation Contact Information Changed

The following contact has changed:
- [Previous name] → [New name]
- [Previous phone] → [New phone]

Please update your emergency contacts.
New file: [location]
Effective: [date]
```

---

## Emergency Response Checklist

When an incident occurs, use this checklist:

- [ ] Trigger PagerDuty incident
- [ ] Create Slack channel `#incident-YYYYMMDD-HHMM`
- [ ] Notify L1 (automatic via PagerDuty)
- [ ] Post to `#incidents` channel with summary
- [ ] If no response (5 min) → escalate to L2
- [ ] If SEV-1 → escalate to VP immediately
- [ ] Update status every 15 minutes
- [ ] Post all-clear when resolved
- [ ] Schedule post-mortem within 24 hours

---

## Related Documents

- `ESCALATION_PROCEDURES.md` - Escalation protocols and triggers
- `ROLLBACK_PROCEDURES.md` - Technical rollback procedures
- `incident-templates/` - Communication templates
- `ROLLBACK_VALIDATION_CHECKLIST.md` - Validation procedures

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-06-20 | Initial draft | [Name] |
| | | |

---

## Notes

- This file contains sensitive information
- Update contact information whenever changes occur
- Test quarterly with verification calls
- Keep printed copy in war room
- Share only with authorized personnel
