# Runbook: High-Severity CVE Response (<24-hour SLA)

**Severity**: HIGH  
**SLA**: <24 hours for patch deployment  
**Category**: CVE Response Procedures  
**CVSS Threshold**: 7.0-8.9 (High)

---

## Overview

High-severity CVEs require prompt patching within 24 hours. These vulnerabilities have significant potential impact but may have mitigations or require specific configurations to exploit.

---

## Response Timeline

**T+0 hours (Day 1 morning)**:
- [ ] Alert security team
- [ ] Assess applicability to our systems
- [ ] Check vendor for patch availability

**T+4 hours**:
- [ ] Create patch PR
- [ ] Run comprehensive test suite
- [ ] Schedule code review with security team

**T+8 hours**:
- [ ] Deploy to staging
- [ ] Execute integration tests
- [ ] Approve and merge PR

**T+16 hours**:
- [ ] Deploy to production
- [ ] Monitor logs for anomalies
- [ ] Verify patch effectiveness

**T+24 hours**:
- [ ] Confirm full deployment
- [ ] Document incident

---

## Remediation Steps

1. **Identify affected versions**
   ```bash
   grep -r "package_name" requirements.txt
   pip show package_name
   ```

2. **Update to patched version**
   ```bash
   pip install --upgrade "package_name>=X.Y.Z"
   ```

3. **Test thoroughly**
   ```bash
   pytest tests/ -v
   python -m pytest tests/integration/ -v
   ```

4. **Deploy with standard review**
   ```bash
   gh pr create --title "CVE-XXXX: High-severity patch"
   ```

---

## References

- [NVD](https://nvd.nist.gov/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1)
