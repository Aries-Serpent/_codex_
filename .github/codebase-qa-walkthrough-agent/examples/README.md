# QA Walkthrough Agent - Examples

> Generated: 2026-01-26T20:41:00Z | Author: autonomous-codebase-health-agent
> Status: 🟡 Under Development

## 📋 Overview

This directory contains example workflows, configurations, and output samples for the Codebase QA Walkthrough Agent.

## 📁 Directory Structure

```
examples/
├── README.md                       # This file
├── sample_audit_report.json        # Example audit output
├── sample_coverage_analysis.json   # Example coverage report
├── sample_findings.yaml            # Example findings with evidence
├── sample_remediation_plan.yaml    # Example action plan
└── workflows/                      # Example CI integration
    └── qa-audit-scheduled.yml      # Scheduled audit workflow
```

## 🎯 Example Use Cases

### 1. Full Repository Audit

**Scenario**: Comprehensive quality audit before major release

**Command**:
```bash
python -m codex.qa_walkthrough \
  --full-audit \
  --output-dir .codex/qa_walkthrough \
  --format json,yaml
```

**Expected Output**:
- Coverage analysis with module breakdown
- Quality metrics with trend comparison
- Prioritized remediation plan
- Evidence-based findings

### 2. Focused Security Audit

**Scenario**: Security review after dependency updates

**Command**:
```bash
python -m codex.qa_walkthrough \
  --checks security,dependencies \
  --severity critical,high \
  --output-format json
```

**Expected Output**:
- Known vulnerability scan results
- Dependency security analysis
- Secret detection report
- Recommended security patches

### 3. Test Coverage Analysis

**Scenario**: Identify untested code paths

**Command**:
```bash
python -m codex.qa_walkthrough \
  --checks coverage \
  --threshold 70 \
  --show-gaps
```

**Expected Output**:
- Coverage percentage by module
- List of untested files
- Critical paths without tests
- Coverage improvement roadmap

### 4. Documentation Quality Check

**Scenario**: Validate documentation before release

**Command**:
```bash
python -m codex.qa_walkthrough \
  --checks documentation,links \
  --fix-links \
  --output-format yaml
```

**Expected Output**:
- Docstring completeness report
- Broken link detection
- API documentation gaps
- Suggested improvements

## 📊 Sample Output Formats

### JSON Format
```json
{
  "audit_timestamp": "2026-01-26T20:41:00Z",
  "audit_type": "full",
  "quality_score": 75.5,
  "findings": {
    "critical": 0,
    "high": 3,
    "medium": 12,
    "low": 45
  },
  "metrics": {
    "test_coverage": 2.87,
    "documentation_coverage": 78.5,
    "code_quality": 82.3
  }
}
```

### YAML Format
```yaml
audit:
  timestamp: 2026-01-26T20:41:00Z
  type: full
  quality_score: 75.5
findings:
  critical: 0
  high: 3
  medium: 12
  low: 45
metrics:
  test_coverage: 2.87
  documentation_coverage: 78.5
  code_quality: 82.3
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

```yaml
name: QA Audit

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  qa-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run QA Walkthrough
        run: |
          python -m codex.qa_walkthrough \
            --full-audit \
            --output-dir .codex/qa_walkthrough

      - name: Upload Audit Report
        uses: actions/upload-artifact@v4
        with:
          name: qa-audit-report
          path: .codex/qa_walkthrough/
```

## 🎓 Best Practices

### Frequency Recommendations

- **Full Audit**: Weekly or before major releases
- **Security Audit**: After dependency updates
- **Coverage Audit**: After significant code changes
- **Documentation Audit**: Before releases

### Severity Classification

- **P0/Critical**: Security vulnerabilities, data loss risks
- **P1/High**: Test failures, broken functionality
- **P2/Medium**: Code quality issues, missing tests
- **P3/Low**: Documentation gaps, minor improvements

### Remediation Workflow

1. Review findings by severity
2. Assign ownership for fixes
3. Create issues for P0/P1 items
4. Schedule P2/P3 for future sprints
5. Re-run audit after fixes
6. Update quality baselines

## 🔗 Related Documentation

- [QA Walkthrough Agent README](../README.md)
- [Codebase Agency Policy](../../../.codex/CODEBASE_AGENCY_POLICY.md)
- [Quality Metrics](../../../.codex/qa_walkthrough/README.md)

---
*This is a living document maintained by autonomous agents.*
