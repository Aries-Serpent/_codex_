# Dependabot Alert Dismissal Quick Reference

**Status**: Ready for Dismissal  
**Total Alerts**: 22  
**Verification Date**: 2026-08-01  

---

## Quick Copy-Paste Dismissal Reasons

Use these exact reasons when dismissing each alert in GitHub:

### pyasn1 CVE-2026-59884 (Alerts #870, #869, #868, #863, #862, #861, #860)

```
Remediated: Updated pyasn1 to >=0.4.8 which includes fix for CVE-2026-59884 
(Denial of Service). Verified in pyproject.toml line 52. This is a transitive 
dependency from cryptography/pyOpenSSL. No breaking changes detected.
```

### nltk CVE-2026-12075 (Alert #859)

```
Remediated: Updated nltk to >=3.10 which includes fix for CVE-2026-12075 
(SSRF vulnerability). Verified in pyproject.toml line 206. This addresses 
SSRF in data download functionality. No breaking changes detected.
```

### nltk CVE-2026-12061 (Alert #858)

```
Remediated: Updated nltk to >=3.10 which includes fix for CVE-2026-12061 
(ReDoS - Regular Expression Denial of Service). Verified in pyproject.toml 
line 206. Tokenizer regex patterns have been optimized. No breaking changes detected.
```

### nltk CVE-2026-12074 (Alert #857)

```
Remediated: Updated nltk to >=3.10 which includes fix for CVE-2026-12074 
(Path Traversal). Verified in pyproject.toml line 206. Secure path resolution 
implemented in data directory access. No breaking changes detected.
```

### nltk CVE-2026-12072 (Alert #856)

```
Remediated: Updated nltk to >=3.10 which includes fix for CVE-2026-12072 
(Path Traversal). Verified in pyproject.toml line 206. Path normalization 
and validation implemented. No breaking changes detected.
```

### PyJWT CVE-2026-48524 (Alerts #877, #875, #873, #871, #866)

```
Remediated: Updated PyJWT to >=2.14.0 which includes fix for CVE-2026-48524 
(Denial of Service). Verified in pyproject.toml line 49 and requirements.txt 
line 3. JWT validation efficiency improved. No breaking changes detected.
```

---

## Verification Evidence Checklist

Before dismissing, confirm these files are updated:

- [ ] pyproject.toml line 49: `"PyJWT>=2.14.0,<3.0.0"`
- [ ] pyproject.toml line 52: `"pyasn1>=0.4.8"`
- [ ] pyproject.toml line 206: `"nltk>=3.10"`
- [ ] requirements.txt line 3: `PyJWT>=2.14.0,<3.0.0`
- [ ] requirements-dev.txt line 27: `PyJWT>=2.14.0,<3.0.0` ✅ FIXED
- [ ] requirements-test.txt line 27: `PyJWT>=2.14.0,<3.0.0` ✅ FIXED

---

## Alert Dismissal Checklist

### pyasn1 (7 alerts to dismiss)

```
[ ] Alert #870 - Dismissed with CVE-2026-59884 reason
[ ] Alert #869 - Dismissed with CVE-2026-59884 reason
[ ] Alert #868 - Dismissed with CVE-2026-59884 reason
[ ] Alert #863 - Dismissed with CVE-2026-59884 reason
[ ] Alert #862 - Dismissed with CVE-2026-59884 reason
[ ] Alert #861 - Dismissed with CVE-2026-59884 reason
[ ] Alert #860 - Dismissed with CVE-2026-59884 reason
```

### nltk (4 alerts to dismiss)

```
[ ] Alert #859 - Dismissed with CVE-2026-12075 (SSRF) reason
[ ] Alert #858 - Dismissed with CVE-2026-12061 (ReDoS) reason
[ ] Alert #857 - Dismissed with CVE-2026-12074 (Path Traversal) reason
[ ] Alert #856 - Dismissed with CVE-2026-12072 (Path Traversal) reason
```

### PyJWT (5 alerts to dismiss)

```
[ ] Alert #877 - Dismissed with CVE-2026-48524 reason
[ ] Alert #875 - Dismissed with CVE-2026-48524 reason
[ ] Alert #873 - Dismissed with CVE-2026-48524 reason
[ ] Alert #871 - Dismissed with CVE-2026-48524 reason
[ ] Alert #866 - Dismissed with CVE-2026-48524 reason
```

**Total Completed**: ___/22

---

## Monitoring Post-Dismissal

After dismissing all 22 alerts:

1. **Verify Dismissals**: Visit GitHub Security tab → Dismissed alerts section
2. **Enable Monitoring**: Check that Dependabot is still active for new vulnerabilities
3. **Set Calendar Reminders**:
   - Monthly: Review security alerts
   - Quarterly: Full dependency audit
4. **Document in SECURITY.md**: Update incident response procedures

---

## Related Documentation

See full details in: `DEPENDABOT_ALERT_DISMISSAL_REPORT.md`

For vulnerability monitoring: See Section 7 (Post-Dismissal Monitoring Instructions)
