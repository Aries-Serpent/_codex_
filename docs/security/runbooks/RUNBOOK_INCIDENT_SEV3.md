# Runbook: Sev-3 Incident Response (<4 hour SLA)

**Severity**: MEDIUM  
**SLA**: <4 hours for response  
**Category**: Incident Response & Escalation  
**Examples**: Low-impact security issues, configuration problems, policy violations

---

## Response Timeline

**T+0 hours (Same day)**:
- [ ] Log incident
- [ ] Assign to security team member
- [ ] Gather information

**T+2 hours**:
- [ ] Assess impact
- [ ] Develop remediation plan

**T+4 hours**:
- [ ] Implement fix or workaround
- [ ] Verify effectiveness

**T+24 hours**:
- [ ] Complete post-incident documentation
- [ ] Close ticket

---

## Investigation

```bash
# Review relevant logs
grep -r "warning\|anomaly" /var/log/

# Check configurations
grep -r "config" /etc/ | grep -i "security"
```

---

## References

- [NIST Guidelines](https://nvlpubs.nist.gov/)
