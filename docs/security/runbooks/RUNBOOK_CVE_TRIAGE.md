# Runbook: CVE Triage & Prioritization

**Category**: CVE Response Procedures  
**Purpose**: Rapid assessment and prioritization of reported CVEs

---

## Triage Criteria

### Step 1: Gather Information
- [ ] CVE ID and NVD link
- [ ] CVSS score and vector
- [ ] Affected software/versions
- [ ] Exploit availability
- [ ] Vendor advisory link

### Step 2: Assess Applicability
```bash
# Check if we use affected package
grep -r "package_name" requirements.txt setup.py package.json

# Check version
pip show package_name | grep Version
npm list package_name
```

### Step 3: Score Severity in Our Context

| Factor | Impact | Scoring |
|--------|--------|---------|
| CVSS Score | 9.0-10.0 → Critical | Adjust by 0-1 point |
| | 7.0-8.9 → High | based on |
| | 4.0-6.9 → Medium | applicability |
| | <4.0 → Low | |
| Production Impact | Yes → +1 | |
| Exploit Available | Yes → +1 | |
| Affected Component | Public API → +2 | |
| | Internal only → -1 | |

### Step 4: Determine Response SLA

| Score | SLA | Priority |
|-------|-----|----------|
| 10+ | <4 hours | P0 Emergency |
| 8-9 | <24 hours | P1 Urgent |
| 6-7 | <48 hours | P2 High |
| 4-5 | <1 week | P3 Medium |
| <4 | <2 weeks | P4 Low |

### Step 5: Create Tracking Issue
```bash
gh issue create --title "CVE-XXXX: [Priority] Patch Required" \
                --label "security,cve" \
                --body "CVSS: X.X
Severity: ${PRIORITY}
SLA: ${SLA}
Patch Status: Available/Pending
Assigned: ${SECURITY_TEAM}"
```

---

## Escalation

- **No patch available**: Contact vendor, implement WAF rules
- **Widespread impact**: Executive notification required
- **Exploit confirmation**: Activate Sev-1 incident response

---

## References

- [NVD](https://nvd.nist.gov/)
- [CVSS v3.1](https://www.first.org/cvss/v3.1/specification-document)
