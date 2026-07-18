# Runbook: CCPA Consumer Rights Request (45-day SLA)

**Severity**: HIGH  
**SLA**: <45 days for fulfillment  
**Category**: Compliance Violation Remediation  
**Regulation**: California Consumer Privacy Act (CCPA)  
**Affected**: California residents

---

## Overview

CCPA grants consumers rights to know, delete, and opt-out of sale of personal information. Requests must be fulfilled within 45 days.

---

## Request Types

1. **Right to Know**: Disclose data collected
2. **Right to Delete**: Remove consumer data
3. **Right to Opt-Out**: Stop selling/sharing data
4. **Right to Correct**: Update inaccurate data
5. **Right to Limit Use**: Restrict use of sensitive data

---

## Fulfillment Timeline

**T+0 days (Request received)**:
- [ ] Log request in tracking system
- [ ] Verify consumer identity
- [ ] Set 45-day deadline

**T+5 days**:
- [ ] Collect requested data
- [ ] Prepare disclosure document
- [ ] Internal review

**T+15 days**:
- [ ] Prepare deletion plan (if applicable)
- [ ] Send preliminary response
- [ ] Request clarifications if needed

**T+45 days**:
- [ ] Final response due
- [ ] Send to consumer
- [ ] Document fulfillment

---

## Data Inventory

Required to fulfill CCPA requests:

```bash
# Identify all systems storing consumer data
mysql> SELECT * FROM users WHERE email = '{consumer}';

# Check backups
aws s3 ls s3://backups/ | grep -i "consumer"

# Search logs
grep "{consumer_id}" /var/log/*.log

# Collect from third parties (if applicable)
# Email partners: "Please provide all data for ${consumer_id}"
```

---

## Escalation

Deny requests only if:
- Cannot verify identity
- Request is manifestly unfounded
- Excessive burden/cost

Otherwise, must fulfill.

---

## References

- [CCPA Regulations](https://oag.ca.gov/privacy/ccpa)
- [CCPA Rights](https://www.consumer.ftc.gov/articles/0621-california-consumer-privacy-act-ccpa)
