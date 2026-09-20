# Run Full Audit Pipeline

## Purpose
Execute a comprehensive audit of the Codex repository, checking all 39 capabilities against maturity thresholds and generating detailed reports.

## Prerequisites
- Python 3.9+ installed
- Repository cloned locally
- Dependencies installed: `pip install -e .`
- SQLite database initialized (auto-created if missing)

## Commands

### 1. Run Full Audit
```bash
cd /home/runner/work/_codex_/_codex_
python -m scripts.space_traversal.audit_runner run
```

### 2. Store Trend Data
```bash
python -m scripts.space_traversal.audit_runner store-trend
```

### 3. Generate Dashboard
```bash
python -m scripts.space_traversal.audit_runner dashboard --output audit_dashboard.html
```

### 4. Check for Regressions
```bash
python -m scripts.space_traversal.audit_runner check-regressions
```

## Validation

1. **Check Exit Code**: Should be 0 for success
2. **Verify Output Files**:
   - `audit_report.md` - Markdown report
   - `audit_results.json` - JSON results
   - `audit_dashboard.html` - HTML visualization
3. **Check Database**: `sqlite3 audit_trends.db "SELECT COUNT(*) FROM audit_runs;"`
4. **Review Logs**: Check for errors in console output

## Expected Output

### Console Output
```
Running audit pipeline...
✓ Scanned 1,208 test files
✓ Checked 39 capabilities
✓ 18/18 critical capabilities above maturity threshold
✓ Generated dashboard: audit_dashboard.html
✓ Stored trend data
```

### Generated Files
- `audit_report.md` - Capability assessment with pass/fail status
- `audit_results.json` - Machine-readable results
- `audit_dashboard.html` - Interactive dashboard with charts
- `audit_trends.db` - SQLite database with historical data

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Install dependencies
```bash
pip install -e .
pip install -r requirements-dev.txt
```

### Issue: Database locked
**Solution**: Close other connections or delete and recreate
```bash
rm audit_trends.db
python -m scripts.space_traversal.audit_runner run
```

### Issue: Missing capabilities
**Solution**: Check configuration
```bash
cat .copilot-space/workflow.yaml
```

## Integration with CI/CD

This prompt can be used in GitHub Actions:

```yaml
- name: Run Audit Pipeline
  run: |
    python -m scripts.space_traversal.audit_runner run
    python -m scripts.space_traversal.audit_runner store-trend
    python -m scripts.space_traversal.audit_runner check-regressions
```

## Related Prompts
- [check-regressions.md](check-regressions.md) - Detailed regression checking
<!-- TODO: Create generate-dashboard.md for dashboard customization -->
<!-- [generate-dashboard.md](generate-dashboard.md) - Dashboard customization (TODO: Create this file) -->
<!-- TODO: Create show-trend.md for viewing capability trends -->
<!-- [show-trend.md](show-trend.md) - View capability trends (TODO: Create this file) -->
