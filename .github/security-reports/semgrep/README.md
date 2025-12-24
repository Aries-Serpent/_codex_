# Semgrep Security Reports

This directory contains Semgrep security scanning outputs and remediation tracking.

## Directory Structure

```
semgrep/
├── alerts-raw.json       # Raw Semgrep CI output (generated)
├── alerts.csv            # Parsed alerts for analysis (generated)
├── remediation-plan.md   # Prioritized fix plan (generated)
└── README.md             # This file
```

## Generating Reports

### Export Alerts
```bash
python scripts/security/export_semgrep_alerts.py
```

### Score and Prioritize
```bash
python scripts/security/score_alerts.py
```

### Generate Remediation Plan
```bash
python scripts/security/generate_remediation_plan.py
```

## Baseline Mode

After remediation is complete, enable baseline mode in `.semgrep/semgrep.yml`:
- Only new alerts will block CI
- Existing alerts are tracked but don't fail builds

## Alert Priority Tiers

| Tier | Score Range | Action |
|------|-------------|--------|
| P0 | ≥9.0 | Fix immediately |
| P1 | 6.0-8.9 | Fix this sprint |
| P2 | 3.0-5.9 | Backlog |
| P3 | <3.0 | Defer/Suppress |
