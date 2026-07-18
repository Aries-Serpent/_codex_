# Runbook: Critical CVE Response (<4-hour SLA)

**Severity**: CRITICAL  
**SLA**: <4 hours for patch deployment  
**Category**: CVE Response Procedures  
**CVSS Threshold**: 9.0-10.0 (Critical)  
**Escalation**: Immediate VP/Director notification

---

## Overview

Critical CVE (Common Vulnerabilities and Exposures) response requires rapid assessment and patching. Critical-severity vulnerabilities (CVSS 9.0+) in production dependencies can lead to immediate system compromise.

---

## Trigger Conditions

- CVSS Score ≥ 9.0 (Critical)
- Vulnerability affects production dependencies
- Exploit code publicly available or actively exploited
- Significant downstream impact

---

## Emergency Response Timeline

**T+0 minutes (Immediate)**:
- [ ] Declare security incident
- [ ] Notify VP/Director of Engineering
- [ ] Page on-call security engineer
- [ ] Initiate incident response protocol

**T+15 minutes**:
- [ ] Identify all affected services/projects
- [ ] Determine patch availability from vendor
- [ ] Assess if immediate mitigation exists (WAF rules, network segmentation)
- [ ] Assess severity in your specific context

**T+30 minutes**:
- [ ] Create emergency patch PR
- [ ] Skip code review if necessary (with documentation)
- [ ] Deploy to staging environment
- [ ] Execute rapid security validation tests

**T+60 minutes**:
- [ ] Deploy to production
- [ ] Verify fix in production logs
- [ ] Monitor for any regression

**T+120 minutes**:
- [ ] Confirm no unauthorized access occurred
- [ ] Post-incident review (within 24 hours)
- [ ] Document remediation steps

---

## Step-by-Step Remediation

### Step 1: Identify Affected Components
```bash
# Search for vulnerable package
grep -r "vulnerable_package" requirements*.txt pyproject.toml setup.py package.json

# Get current version
pip show vulnerable_package | grep Version
npm list vulnerable_package

# List all dependencies that might transitively use it
pip freeze | grep vulnerable_package
npm ls vulnerable_package
```

### Step 2: Patch or Upgrade
```bash
# Update to patched version
pip install --upgrade "vulnerable_package>=X.X.X"
npm install "vulnerable_package@^X.X.X"

# Update lock files
pip freeze > requirements-updated.txt
npm ci  # To update package-lock.json

# Create emergency patch branch
git checkout -b emergency/cve-XXXX-patch
```

### Step 3: Emergency Testing
```bash
# Fast-track testing (skip non-critical tests if necessary)
pytest tests/ -k "critical or security" -v --tb=short

# Run production smoke tests
python -m pytest tests/smoke/ -v

# Validate no dependency conflicts
python -c "import vulnerable_package; print(vulnerable_package.__version__)"

# Performance baseline check
python -m pytest tests/performance/ --baseline
```

### Step 4: Deploy with Caution
```bash
# Create PR with emergency label
gh pr create --title "[EMERGENCY] CVE-XXXX Patch" \
             --body "Critical CVE affects ${package}. Patched in v${version}." \
             --label "security,emergency,cve-XXXX"

# For truly critical: Deploy with limited review
# Document override reason clearly in PR

# Deploy to production
git push origin emergency/cve-XXXX-patch
# Manual merge or deploy via CD pipeline with emergency approval
```

### Step 5: Post-Deployment Verification
```bash
# Verify in production
curl -v https://prod.example.com/health

# Check for errors in logs
grep -i "error\|exception" /var/log/app.log | tail -20

# Monitor metrics
# - Application error rate
# - Response time
# - Security-related errors
```

---

## Escalation Path

**Automatic Escalation**:
- Patch not available from vendor (use workaround/WAF rules)
- Regression detected in production
- Unauthorized access confirmed

**Actions**:
1. Engage vendor for emergency patch
2. Deploy network-level mitigations
3. Prepare for rollback
4. Notify affected users

---

## Post-Incident Checklist

- [ ] Confirm no unauthorized access in logs
- [ ] Document timeline and actions taken
- [ ] Review why vulnerability wasn't caught earlier
- [ ] Update dependency scanning tools
- [ ] Schedule comprehensive security review

---

## Related Patterns

- RP-6010: CVE Triage & Prioritization
- RP-6011: Dependency Update Automation
- RP-6012: Incident Response (Sev-1)

---

## References

- [NVD CVE Database](https://nvd.nist.gov/)
- [CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)
- [OWASP Vulnerability Management](https://owasp.org/www-community/controls/Vulnerability_Management)
