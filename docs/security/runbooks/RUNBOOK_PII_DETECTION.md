# Runbook: PII Detection & Remediation

**Severity**: CRITICAL  
**SLA**: <1 hour (immediate action)  
**Category**: PII/Secret Detection & Remediation  
**Regulations**: GDPR, CCPA, HIPAA  

---

## Overview

Personally Identifiable Information (PII) exposed in code, logs, or backups violates data protection regulations and exposes individuals to identity theft.

---

## PII Categories

- **Tier 1 (Most Critical)**: SSN, credit card numbers, financial account numbers
- **Tier 2**: Full names with email/phone, date of birth, passport numbers
- **Tier 3**: Usernames, email addresses (without other identifiers), IP addresses

---

## Trigger Conditions

- Regex matches common patterns (SSN: XXX-XX-XXXX, CC: XXXX-XXXX-XXXX-XXXX)
- Data loss prevention (DLP) system alerts
- Developer reports suspected PII exposure
- Scheduled PII scan finds data

---

## Immediate Response (<15 minutes)

### Step 1: Confirm PII Exposure
```bash
# Scan repository
truffleHog filesystem {repo} --only-verified --json > pii_findings.json

# Scan logs
grep -rE "(\d{3}-\d{2}-\d{4}|4[0-9]{12})" /var/log/ > suspicious_logs.txt

# Check backups
# Query backup metadata for exposed files
```

### Step 2: Notify Affected Individuals (within 24 hours for GDPR)
```bash
# Prepare notification
# Include:
# - What PII was exposed
# - How it was exposed
# - Steps taken to remediate
# - What individuals should do
# - Contact information

# Send via secure channel (encrypted email, phone)
```

### Step 3: Incident Response
- [ ] Create incident ticket
- [ ] Notify privacy officer
- [ ] Begin formal investigation
- [ ] Preserve evidence (logs, backups)

---

## Remediation Steps

### Step 1: Identify All Instances
```bash
# Find PII patterns
grep -rE "(\d{3}-\d{2}-\d{4}|4[0-9]{12}|(?:SSN|ssn))" {repo}

# Check git history
git log -S "SSN" --oneline | head -20

# Scan database backups
```

### Step 2: Remove from Codebase
```bash
# Redact in code
# Replace with placeholder or variable reference
OLD_PII = "123-45-6789"
REDACTED_PII = "XXX-XX-6789"

# OR use environment variables
PII_DATA = os.getenv('PII_DATA')  # Loaded from secure vault
```

### Step 3: Purge from Git History
```bash
# Use git filter-branch or BFG
bfg --delete-files-with-regex "SSN|ssn" --no-blob-protection {repo}
git reflog expire --expire=now --all
git gc --prune=now

# Force push with team coordination
git push --force --all
```

### Step 4: Notify Users (GDPR/CCPA Requirement)
```
Subject: Important Security Notice - PII Exposure

Dear User,

We discovered that your [specific PII] may have been exposed due to [incident summary].

Affected: [date range or specific incident]
Details: [description]
Your ID: [anonymized reference]

Steps we took:
- Removed PII from all systems
- Rotated affected credentials
- Enhanced security controls

Steps you should take:
- Monitor financial accounts
- Enable fraud alerts
- Consider credit freezes

Contact: privacy@company.com
```

---

## Validation

```bash
# Verify PII is removed
truffleHog filesystem {repo} --only-verified --json | wc -l  # Should be 0

# Confirm git history is clean
git log -S "sensitive_data" --all | wc -l  # Should be 0
```

---

## Escalation Path

**Automatic escalation for**:
- Large-scale exposure (>1000 records)
- Sensitive categories (SSN, credit cards)
- Public exposure (GitHub, internet)
- Regulatory violations

---

## References

- [GDPR Article 33](https://gdpr-info.eu/articles/notification-personal-data-breach/) (Breach Notification)
- [CCPA Breach Notification](https://oag.ca.gov/privacy/databreach/notification)
- [PII Categories](https://www.nist.gov/publications/guide-protecting-confidentiality-personally-identifiable-information-pii)
