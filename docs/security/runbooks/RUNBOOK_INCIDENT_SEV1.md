# Runbook: Sev-1 Incident Response (<2 minute SLA)

**Severity**: CRITICAL  
**SLA**: <2 minutes for initial acknowledgment  
**Category**: Incident Response & Escalation  
**Examples**: Active exploitation, data breach, system compromise

---

## Immediate Actions (0-2 minutes)

### Step 1: Page On-Call Team
```bash
# Trigger PagerDuty alert
# Escalate to VP/Director
# Notify Security Officer

# All-hands alert
echo "SECURITY INCIDENT - SEV-1" | mail -s "URGENT" team@company.com
```

### Step 2: Establish War Room
```bash
# Open incident bridge
# Zoom/Google Meet incident channel
# Share incident link in Slack #security-incidents

# Start incident recording (for post-mortem)
```

### Step 3: Initial Assessment
- [ ] What system is affected?
- [ ] Is it currently under attack?
- [ ] What data is at risk?
- [ ] What is the scope?

---

## 0-15 Minute Actions

### Step 1: Contain the Threat
```bash
# Isolate affected systems (if possible without service loss)
# - Disable compromised service
# - Block attacker IP addresses
# - Revoke compromised credentials

# Preserve evidence
# - Copy logs to secure location
# - Screenshot error states
# - Capture memory dumps
```

### Step 2: Activate Incident Response Team
- [ ] Security Lead
- [ ] Engineering Lead
- [ ] Database Admin
- [ ] DevOps Lead
- [ ] Legal/Compliance (for data breach)

### Step 3: Begin Root Cause Analysis
```bash
# Gather evidence
grep -r "attack_pattern" /var/log/
tail -f /var/log/auth.log | grep -i "unauthorized"

# Timeline reconstruction
```

---

## 15-60 Minute Actions

- [ ] Confirm extent of compromise
- [ ] Implement emergency fixes
- [ ] Prepare customer communication (if needed)
- [ ] Enable enhanced monitoring

---

## Post-Incident (24 hours)

- [ ] Schedule full post-mortem
- [ ] Document timeline
- [ ] Implement preventive measures
- [ ] Notify affected users

---

## Escalation Path

**Automatic escalation if**:
- Multiple systems compromised
- Customer data confirmed exposed
- Ransomware attack
- Attacker still active

**Actions**:
- Contact incident response firm
- Notify law enforcement (if applicable)
- Prepare press statement
- Engage cyber insurance

---

## References

- [NIST Incident Response Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf)
- [SANS Incident Response](https://www.sans.org/white-papers/)
