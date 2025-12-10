# Check for Regressions

## Purpose
Detect regressions in capability scores by comparing current audit results against historical trends and configured thresholds.

## Prerequisites
- Full audit completed at least once
- Trend data stored in database
- Regression detection enabled in workflow.yaml

## Commands

### 1. Basic Regression Check
```bash
cd /home/runner/work/_codex_/_codex_
python -m scripts.space_traversal.audit_runner check-regressions
```

### 2. With Custom Threshold
```bash
python -m scripts.space_traversal.audit_runner check-regressions --threshold 5.0
```

### 3. Check Specific Capability
```bash
python -m scripts.space_traversal.audit_runner show-trend "Automated Testing" --check-regression
```

## Validation

1. **Exit Code**: 0 = no regressions, 1 = regressions detected
2. **Console Output**: Lists any capabilities that regressed
3. **Regression Report**: Generated if regressions found

## Expected Output

### No Regressions Detected
```
Checking for regressions...
✓ Analyzing 39 capabilities
✓ Comparing against 5 historical runs
✓ No regressions detected
```

### Regressions Detected
```
Checking for regressions...
✓ Analyzing 39 capabilities
✓ Comparing against 5 historical runs
⚠ 2 regressions detected:

Capability: Automated Testing
  Previous: 95.0 → Current: 88.0 (↓7.0)
  Threshold: 5.0
  
Capability: Model Monitoring
  Previous: 92.0 → Current: 85.0 (↓7.0)
  Threshold: 5.0

Generated regression report: regression_report.md
```

## Regression Criteria

A regression is detected when:
1. **Capability score decreased** from previous run
2. **Decrease exceeds threshold** (default: 5.0 points)
3. **Capability is marked as critical** in workflow.yaml

## Configuration

Edit `.copilot-space/workflow.yaml`:

```yaml
regression_detection:
  enabled: true
  threshold: 5.0  # Point decrease to trigger alert
  lookback_runs: 5  # Compare against last N runs
  critical_only: false  # Only check critical capabilities
```

## Troubleshooting

### Issue: No historical data
**Solution**: Run audit and store trend first
```bash
python -m scripts.space_traversal.audit_runner run
python -m scripts.space_traversal.audit_runner store-trend
```

### Issue: False positives
**Solution**: Adjust threshold or lookback period
```bash
# Increase threshold to reduce sensitivity
python -m scripts.space_traversal.audit_runner check-regressions --threshold 10.0
```

### Issue: Missing capabilities
**Solution**: Ensure all capabilities have historical data
```bash
# List stored trends
sqlite3 audit_trends.db "SELECT DISTINCT capability_name FROM capability_trends;"
```

## Integration with CI/CD

Use in GitHub Actions to fail builds on regressions:

```yaml
- name: Check Regressions
  run: |
    python -m scripts.space_traversal.audit_runner check-regressions
  continue-on-error: false  # Fail build if regressions found

- name: Upload Regression Report
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: regression-report
    path: regression_report.md
```

## Webhook Notifications

Configure webhooks to alert on regressions:

```yaml
webhooks:
  - url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
    events: [regression_detected]
    format: slack
```

## Related Prompts
- [run-full-audit.md](run-full-audit.md) - Full audit execution
- [show-trend.md](show-trend.md) - View capability trends
- [store-trend.md](store-trend.md) - Store trend data
