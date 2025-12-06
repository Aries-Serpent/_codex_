# Compliance Guide

## Supported Policies

- GDPR (General Data Protection Regulation)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOC2 (Service Organization Control 2)

## Usage

```python
from codex_ml.governance.compliance_gates import ComplianceGate

# GDPR compliance check
gdpr = ComplianceGate("GDPR")
report = gdpr.validate(model, data, deployment)

if not report.is_compliant:
    print("Violations:", report.violations)
```

## Policy Checklists

### GDPR
- [ ] Data minimization
- [ ] Right to explanation  
- [ ] Purpose limitation
- [ ] Data retention policies

### HIPAA
- [ ] PHI protection
- [ ] Encryption (at rest + transit)
- [ ] Audit logs
- [ ] Access controls

### SOC2
- [ ] Security controls
- [ ] Availability monitoring
- [ ] Processing integrity
- [ ] Confidentiality
- [ ] Privacy protections

See `src/codex_ml/governance/compliance_gates.py` for implementation details.
