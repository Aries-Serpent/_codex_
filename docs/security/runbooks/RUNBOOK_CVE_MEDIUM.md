# Runbook: Medium-Severity CVE Response (<48-hour SLA)

**Severity**: MEDIUM  
**SLA**: <48 hours for patch deployment  
**Category**: CVE Response Procedures  
**CVSS Threshold**: 4.0-6.9 (Medium)

---

## Overview

Medium-severity CVEs should be patched within 48 hours as part of regular maintenance. These have moderate potential impact and can usually be batched with other updates.

---

## Response Timeline

**T+0 hours (Day 1)**:
- [ ] Log in security tracking system
- [ ] Check patch availability
- [ ] Assess impact on our systems

**T+12 hours**:
- [ ] Create patch PR
- [ ] Run standard test suite
- [ ] Schedule review

**T+24 hours**:
- [ ] Deploy to staging environment
- [ ] Verify no regressions

**T+36 hours**:
- [ ] Deploy to production
- [ ] Monitor for issues

**T+48 hours**:
- [ ] Confirm deployment complete
- [ ] Close tracking ticket

---

## Remediation Steps

1. **Update dependency**
   ```bash
   pip install --upgrade "package_name"
   ```

2. **Test**
   ```bash
   pytest tests/ -v
   ```

3. **Deploy normally**
   ```bash
   gh pr create --title "CVE-XXXX: Medium-severity patch"
   ```

---

## References

- [NVD](https://nvd.nist.gov/)
