# Runbook: GDPR Data Breach Notification (72-hour SLA)

**Severity**: CRITICAL  
**SLA**: <72 hours for notifying authorities  
**Category**: Compliance Violation Remediation  
**Regulation**: GDPR Article 33 & 34  
**Affected**: EU residents' personal data

---

## Overview

GDPR requires notification of data protection authorities within 72 hours of discovering a breach affecting EU residents' personal data.

---

## Trigger Conditions

- Personal data breach confirmed
- Affects EU residents
- Involves special categories (medical, biometric, financial)
- Loss of confidentiality or integrity

---

## Notification Timeline

**T+0 hours (Upon discovery)**:
- [ ] Confirm breach details
- [ ] Determine affected individuals
- [ ] Assess risk to individuals

**T+4 hours**:
- [ ] Notify supervisory authority (DPA)
- [ ] Prepare notification template
- [ ] Prepare evidence/documentation

**T+24 hours**:
- [ ] Send authority notification
- [ ] Begin individual notifications
- [ ] Activate incident response

**T+72 hours**:
- [ ] Complete authority notification
- [ ] Confirm receipt
- [ ] Log response

---

## Authority Notification

**Required Elements**:
- Name of organisation
- Breach description
- Categories and approximate number of individuals
- Data categories affected
- Name/contact of DPA
- Likely consequences
- Measures taken or proposed

**Submit to**:
```
[Country] Data Protection Authority (DPA)
Example: CNIL (France), ICO (UK), BfDI (Germany)
Portal: [DPA website]
```

---

## Individual Notification

**Required Elements**:
- What personal data was breached
- Likely consequences
- Measures taken or proposed
- Your DPA contact
- How to contact you

**Timing**: Without undue delay, within 72 hours max

---

## Documentation

- [ ] Breach incident report
- [ ] Timeline of discovery
- [ ] List of affected individuals
- [ ] Authority notification letter
- [ ] Individual notification letter
- [ ] Evidence of data destruction/recovery

---

## References

- [GDPR Article 33](https://gdpr-info.eu/articles/notification-personal-data-breach/)
- [GDPR Article 34](https://gdpr-info.eu/articles/notification-data-subjects-concerning-personal-data-breach-risk/)
- [EDPB Guidelines](https://edpb.ec.europa.eu/)
