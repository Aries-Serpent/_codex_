# Runbook: Audit Trail Integrity Verification

**Severity**: HIGH  
**SLA**: <24 hours (upon discovery)  
**Category**: Compliance Violation Remediation  
**Purpose**: Ensure audit logs are complete and tamper-proof

---

## Overview

Audit trails provide evidence of system activity and must be protected against tampering. Integrity verification ensures logs are complete and trustworthy.

---

## Verification Procedure

### Step 1: Verify Log Completeness
```bash
# Check for missing sequences
awk '{print $1}' auth.log | sort -u | tail -20

# Look for gaps in timestamps
grep -E "^\d{4}-\d{2}-\d{2}" /var/log/audit/audit.log | \
  awk -F'T' '{print $1}' | sort -u
```

### Step 2: Verify Log Integrity
```bash
# Check log signatures (if using auditd)
auditctl -l  # List audit rules
ausearch -m INTEGRITY_DATA  # Search integrity checks

# Verify log hashing
sha256sum /var/log/audit/*.log > current_hashes.txt
diff current_hashes.txt last_known_good_hashes.txt
```

### Step 3: Verify Centralized Logging
```bash
# Confirm logs sent to syslog server
tail -f /var/log/syslog | grep "forwarding"

# Verify syslog server received logs
ssh syslog-server 'grep $(hostname) /var/log/remote/*.log'
```

### Step 4: Detect Log Tampering
```bash
# Check for suspicious log deletions
find /var/log -name "*.log-*" -type f

# Verify log rotation is working
ls -la /var/log/*.log* | head -20

# Check file permissions
stat /var/log/auth.log | grep -E "Access:|Modify:"
```

---

## Response to Tampering

- [ ] Isolate affected system
- [ ] Preserve logs as evidence
- [ ] Notify security team
- [ ] Check for unauthorized access
- [ ] Restore from known good backups
- [ ] File incident report

---

## Prevention

- [ ] Send logs to immutable centralized store
- [ ] Implement write-once-read-many (WORM) storage
- [ ] Use cryptographic signatures
- [ ] Restrict log file permissions
- [ ] Monitor for log deletions

---

## References

- [NIST Audit Trail Guidelines](https://nvlpubs.nist.gov/)
- [Syslog Standards](https://tools.ietf.org/html/rfc5424)
