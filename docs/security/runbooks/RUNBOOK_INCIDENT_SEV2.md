# Runbook: Sev-2 Incident Response (<30 minute SLA)

**Severity**: HIGH  
**SLA**: <30 minutes for initial response  
**Category**: Incident Response & Escalation  
**Examples**: Unpatched vulnerabilities, unauthorized access to non-critical systems

---

## Response Timeline

**T+0 minutes**:
- [ ] Acknowledge incident
- [ ] Alert security team lead
- [ ] Begin initial assessment

**T+15 minutes**:
- [ ] Confirm scope and impact
- [ ] Start incident log
- [ ] Implement temporary mitigations

**T+30 minutes**:
- [ ] Establish root cause hypothesis
- [ ] Deploy fixes or workarounds
- [ ] Enable enhanced monitoring

**T+4 hours**:
- [ ] Confirm fix effectiveness
- [ ] Document incident
- [ ] Plan post-incident review

---

## Investigation Steps

```bash
# Check for unauthorized access
grep "FAILED\|ERROR" /var/log/auth.log | tail -50

# Review recent changes
git log --oneline | head -20

# Check running processes
ps aux | grep -i "suspicious"

# Network connections
netstat -tulpn | grep -i "LISTEN"
```

---

## Escalation

Escalate to Sev-1 if:
- Scope widens beyond initial assessment
- Data breach confirmed
- Attacker still active

---

## References

- [NIST Incident Response](https://nvlpubs.nist.gov/nistpubs/)
