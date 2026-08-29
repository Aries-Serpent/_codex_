# Historical Runtime Artifacts

**Purpose**: Archived CI/CD artifacts and validation reports  
**Retention**: Permanent (for audit compliance)  
**Active Files**: See `artifacts/` in main repository

## Contents

This directory contains historical runtime artifacts from CI/CD pipelines, including gate logs, validation reports, and coverage outputs that are no longer actively referenced but preserved for audit purposes.

### Structure

```
historical-artifacts/
├── validate_report_20251119.json.gz.b64  # Historical validation report
└── gates/                                 # CI/CD gate logs
    ├── nox-typecheck.log
    ├── nox-lint.log
    ├── pytest-analysis-cov.log
    ├── pytest-analysis.log
    ├── nox-tests_min-rerun.log
    └── nox-tests_min-rerun2.log
```

## Usage

### For Audit Trail
Access gate logs to verify historical CI/CD execution:
```bash
# View specific gate log
cat gates/nox-typecheck.log

# Check validation report
base64 -d validate_report_20251119.json.gz.b64 | gunzip | jq .
```

### For Compliance
These files support audit requirements for tracking testing and validation history.

## Current Artifacts

For current/active artifacts, see:
- `artifacts/metrics/` (main repo - active metrics)
- `artifacts/models/` (main repo - ML models)
- `artifacts/coverage/` (main repo - recent coverage)
- `artifacts/model_regression_log.ndjson` (main repo - active tracking)

---
**Offloaded**: 2026-01-26  
**Maintained by**: QA Walkthrough Agent
