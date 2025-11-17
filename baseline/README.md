# Baseline Scores - Post Gap Remediation

> Created: 2025-11-17 06:30 UTC  
> Purpose: Establish baseline for regression tracking

## Files

- `capabilities_scored_post_remediation.json` - Capability scores after implementing gap remediation
- Use with: `audit_runner.py diff --old baseline/capabilities_scored_post_remediation.json --new audit_artifacts/capabilities_scored.json`

## Context

This baseline was created after:
1. Implementing 103 new tests across 8 capabilities
2. Creating 8 comprehensive documentation guides
3. Re-running full S1-S7 audit workflow

## Score Summary

- Total capabilities: 25
- Above threshold (≥0.70): 17
- Below threshold (<0.70): 8
- Average improvement from initial: +0.0134

## Usage

Compare against this baseline in CI/CD:
```bash
python scripts/space_traversal/audit_runner.py diff \
  --old baseline/capabilities_scored_post_remediation.json \
  --new audit_artifacts/capabilities_scored.json
```text

Fail build if any score drops >0.02 from baseline.
