# Security Runbook Index

**Last Updated**: 2026-07-18  
**Total Runbooks**: 20+  
**Status**: Production Ready

---

## Quick Search

### By Severity
- [CRITICAL (Immediate Action)](#critical-runbooks)
- [HIGH (Within 24 hours)](#high-runbooks)
- [MEDIUM (Within 48 hours)](#medium-runbooks)

### By Category
- [CodeQL Alert Remediation (6 runbooks)](#codeql-alert-remediation)
- [CVE Response Procedures (4 runbooks)](#cve-response-procedures)
- [PII/Secret Detection & Remediation (3 runbooks)](#piisecret-detection--remediation)
- [Incident Response & Escalation (3 runbooks)](#incident-response--escalation)
- [Compliance Violation Remediation (4 runbooks)](#compliance-violation-remediation)

### By Trigger
- [CodeQL Alert](#codeql-alerts)
- [CVE Announcement](#cve-announcement)
- [Secret Detection](#secret-detection)
- [Security Incident](#security-incident)
- [Compliance Violation](#compliance-violation)
- [Data Breach](#data-breach)

---

## Critical Runbooks

### CodeQL Alert Remediation

| Runbook | CWE | Trigger | SLA | Pattern |
|---------|-----|---------|-----|---------|
| [SQL Injection Prevention](RUNBOOK_CODEQL_SQL_INJECTION.md) | CWE-89 | `py/sql-injection` CodeQL alert | <2h | RP-6001 |
| [Hardcoded Secrets Remediation](RUNBOOK_CODEQL_HARDCODED_SECRETS.md) | CWE-798 | `py/hardcoded-secret` detected | <1h | RP-6002 |
| [XSS Prevention](RUNBOOK_CODEQL_XSS.md) | CWE-79 | `js/xss` or `py/xss` alert | <4h | RP-6003 |
| [Path Traversal Prevention](RUNBOOK_CODEQL_PATH_TRAVERSAL.md) | CWE-22 | Path traversal pattern detected | <4h | RP-6004 |
| [Insecure Deserialization](RUNBOOK_CODEQL_DESERIALIZATION.md) | CWE-502 | Unsafe pickle/yaml usage | <2h | RP-6005 |
| [Buffer Overflow Prevention](RUNBOOK_CODEQL_BUFFER_OVERFLOW.md) | CWE-119 | Unsafe memory operations | <2h | RP-6006 |

---

## CVE Response Procedures

| Runbook | CVSS | Response Time | SLA | Pattern |
|---------|------|----------------|-----|---------|
| [Critical CVE Response](RUNBOOK_CVE_CRITICAL.md) | 9.0-10.0 | Immediate | <4h | RP-6010 |
| [High CVE Response](RUNBOOK_CVE_HIGH.md) | 7.0-8.9 | Urgent | <24h | RP-6011 |
| [Medium CVE Response](RUNBOOK_CVE_MEDIUM.md) | 4.0-6.9 | Prompt | <48h | RP-6012 |
| [CVE Triage & Prioritization](RUNBOOK_CVE_TRIAGE.md) | All | Assessment | Varies | RP-6013 |

---

## PII/Secret Detection & Remediation

| Runbook | Regulation | Trigger | SLA | Pattern |
|---------|-----------|---------|-----|---------|
| [PII Detection & Remediation](RUNBOOK_PII_DETECTION.md) | GDPR/CCPA | PII found in code/logs | <1h | RP-6020 |
| [Hardcoded Secret Remediation](RUNBOOK_CODEQL_HARDCODED_SECRETS.md) | General | Secret detected | <1h | RP-6002 |
| [Secret Rotation Procedures](RUNBOOK_SECRET_ROTATION.md) | General | Routine rotation or compromise | <24h | RP-6021 |

---

## Incident Response & Escalation

| Runbook | Severity | Response Time | SLA | Pattern |
|---------|----------|-----------------|-----|---------|
| [Sev-1 Incident Response](RUNBOOK_INCIDENT_SEV1.md) | CRITICAL | Immediate | <2m | RP-6030 |
| [Sev-2 Incident Response](RUNBOOK_INCIDENT_SEV2.md) | HIGH | Urgent | <30m | RP-6031 |
| [Sev-3 Incident Response](RUNBOOK_INCIDENT_SEV3.md) | MEDIUM | Prompt | <4h | RP-6032 |

---

## Compliance Violation Remediation

| Runbook | Regulation | Response Time | SLA | Pattern |
|---------|-----------|-----------------|-----|---------|
| [GDPR Data Breach Notification](RUNBOOK_COMPLIANCE_GDPR.md) | GDPR | Immediate | <72h | RP-6040 |
| [CCPA Consumer Rights Request](RUNBOOK_COMPLIANCE_CCPA.md) | CCPA | Upon receipt | <45d | RP-6041 |
| [SOC2 Control Remediation](RUNBOOK_COMPLIANCE_SOC2.md) | SOC2 | Before audit | <30d | RP-6042 |
| [Audit Trail Integrity Verification](RUNBOOK_COMPLIANCE_AUDIT_TRAIL.md) | General | Upon discovery | <24h | RP-6043 |

---

## Search by Keyword

### SQL & Database Security
- [SQL Injection Prevention](RUNBOOK_CODEQL_SQL_INJECTION.md) - CWE-89
- [Database Connection Security](runbooks/RUNBOOK_CODEQL_SQL_INJECTION.md#database-connection-security)

### Authentication & Authorization
- [Hardcoded Secrets Remediation](RUNBOOK_CODEQL_HARDCODED_SECRETS.md) - CWE-798
- [Secret Rotation Procedures](RUNBOOK_SECRET_ROTATION.md)

### Web Security
- [XSS Prevention](RUNBOOK_CODEQL_XSS.md) - CWE-79
- [Path Traversal Prevention](RUNBOOK_CODEQL_PATH_TRAVERSAL.md) - CWE-22

### Data Protection
- [PII Detection & Remediation](RUNBOOK_PII_DETECTION.md)
- [GDPR Data Breach Notification](RUNBOOK_COMPLIANCE_GDPR.md)
- [CCPA Consumer Rights Request](RUNBOOK_COMPLIANCE_CCPA.md)

### Incident Management
- [Sev-1 Incident Response](RUNBOOK_INCIDENT_SEV1.md)
- [Sev-2 Incident Response](RUNBOOK_INCIDENT_SEV2.md)
- [Sev-3 Incident Response](RUNBOOK_INCIDENT_SEV3.md)

### Vulnerability Management
- [Critical CVE Response](RUNBOOK_CVE_CRITICAL.md)
- [High CVE Response](RUNBOOK_CVE_HIGH.md)
- [Medium CVE Response](RUNBOOK_CVE_MEDIUM.md)
- [CVE Triage & Prioritization](RUNBOOK_CVE_TRIAGE.md)

### Compliance & Auditing
- [SOC2 Control Remediation](RUNBOOK_COMPLIANCE_SOC2.md)
- [Audit Trail Integrity Verification](RUNBOOK_COMPLIANCE_AUDIT_TRAIL.md)

---

## How to Use This Index

1. **Identify the trigger**: What event activated this runbook?
2. **Find the category**: Use the category tables above
3. **Open the runbook**: Click the link to the specific runbook
4. **Follow the steps**: Execute the remediation steps in order
5. **Validate the fix**: Run validation commands to confirm
6. **Escalate if needed**: Follow escalation paths if manual intervention required

---

## Related Documentation

- [Security Guidelines](../SECURITY_GUIDELINES.md)
- [Security Architecture](../SECURITY_ARCHITECTURE.md)
- [Threat Model](../THREAT_MODEL.md)
- [Incident Response Plan](../incident_response.md)

---

## Maintenance

- **Review Frequency**: Quarterly
- **Update Triggers**: When new vulnerabilities discovered or regulations change
- **Approval**: Security team lead
- **Last Review**: 2026-07-18
- **Next Review**: 2026-10-18

---

**Generated for Phase 6 Lane 4: Security Runbook Library & Pattern Integration**  
**Authority**: Security & Compliance Team  
**Version**: 1.0.0
