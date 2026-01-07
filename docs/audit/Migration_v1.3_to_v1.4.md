# Migration Guide: v1.3.x to v1.4.0

**Target Audience**: Users upgrading from audit pipeline v1.3.x  
**Migration Difficulty**: Easy  
**Estimated Time**: 15-30 minutes

---

## Overview

Upgrade your audit pipeline from v1.3.x to v1.4.0 to gain:
- ✅ **Coverage Augmentation**: Accurate test scoring using actual coverage data
- ✅ **Token-Similarity Detection**: Better duplication detection using content analysis
- ✅ **Enhanced Reporting**: Daily status updates and improved reports
- ✅ **Backward Compatibility**: All v1.3.x configurations work without changes

---

## Breaking Changes

**None** ✅ - v1.4.0 is fully backward compatible with v1.3.x

You can upgrade immediately and your existing configurations will continue to work.

---

## What's New in v1.4.0

### Feature 1: Coverage Augmentation

Enhance test scores with actual code coverage percentages.

**Before v1.4.0**:
- Test scores based on file count heuristics
- No visibility into actual test coverage

**After v1.4.0**:
- Test scores reflect actual coverage percentages
- `coverage_map.json` provides detailed coverage data
- Scores = `max(baseline_heuristic, actual_coverage_percent)`

### Feature 2: Token-Similarity Duplication Detection

Advanced content-based duplication detection.

**Before v1.4.0**:
- Duplication based on filename stems only
- Limited accuracy for actual code duplication

**After v1.4.0**:
- Content-aware duplication using Jaccard similarity
- Configurable sensitivity threshold
- Deterministic and scalable with bounded comparisons

### Feature 3: Enhanced Reporting

Improved audit reports and status tracking.

**Before v1.4.0**:
- Basic capability reports

**After v1.4.0**:
- Daily status issue body generation
- Template-based rendering
- Hash verification for reliability

---

## Migration Steps

### Step 1: Update to v1.4.0

```bash
# Pull latest changes
git checkout main
git pull origin main

# Verify v1.4.0 is available
python scripts/space_traversal/audit_runner.py --version
# Should show v1.4.0 or confirm modules exist
```

### Step 2: Backup Existing Results (Recommended)

```bash
# Backup your current audit artifacts
cp -r audit_artifacts audit_artifacts.v1.3.backup
cp -r reports reports.v1.3.backup

# Backup your configuration
cp workflow.yaml workflow.yaml.v1.3.backup
```

### Step 3: Review Your Current Configuration

```bash
# Check your current workflow.yaml
cat workflow.yaml

# Note your current settings
# You don't need to change anything yet - v1.4.0 is backward compatible
```

### Step 4: Test v1.4.0 (Without New Features)

Run audit with your existing configuration:

```bash
# Run audit (v1.4.0 with backward compatibility)
make space-audit

# Verify it works
ls -lh audit_artifacts/capabilities_scored.json
```

✅ **At this point, you're running v1.4.0 with full backward compatibility**

---

## Optional: Enable New Features

### Option A: Enable Coverage Augmentation

**Step 1**: Edit `workflow.yaml` to add coverage configuration:

```yaml
scoring:
  coverage:
    enabled: true
    xml_patterns:
      - "coverage.xml"
    augment_tests_score: true
```

**Step 2**: Modify your CI/test workflow to generate coverage:

```bash
# In your test script or CI configuration
pytest --cov=src --cov-report=xml
```

**Example for GitHub Actions** (`.github/workflows/ci.yml`):
```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=src --cov-report=xml

- name: Run audit
  run: |
    make space-audit
```

**Step 3**: Run audit and verify:

```bash
# Run audit with coverage
make space-audit

# Check coverage_map.json was created
ls -lh audit_artifacts/coverage_map.json

# Verify test scores improved
cat audit_artifacts/capabilities_scored.json | jq '.capabilities[] | select(.tests.score > 0) | {id, tests: .tests.score}'
```

### Option B: Enable Token-Similarity

**Step 1**: Edit `workflow.yaml` to enable token-similarity:

```yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 1000
    max_tokens_per_file: 1000
```

**Step 2**: Run audit:

```bash
make space-audit
```

**Step 3**: Verify consistency scores changed:

```bash
# Compare with backup
python scripts/space_traversal/audit_runner.py diff \
  audit_artifacts.v1.3.backup/capabilities_scored.json \
  audit_artifacts/capabilities_scored.json
```

### Option C: Enable Both Features

Combine both configurations in `workflow.yaml`:

```yaml
scoring:
  coverage:
    enabled: true
    xml_patterns:
      - "coverage.xml"
    augment_tests_score: true
  
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 1000
    max_tokens_per_file: 1000
```

---

## Comparing Results

### Before vs After

```bash
# Run diff command
python scripts/space_traversal/audit_runner.py diff \
  audit_artifacts.v1.3.backup/capabilities_scored.json \
  audit_artifacts/capabilities_scored.json
```

### Expected Changes

**With Coverage Augmentation**:
- Test scores should be closer to actual coverage percentages
- Capabilities with good coverage will score higher
- Capabilities with poor coverage exposed

**With Token-Similarity**:
- Consistency scores Phase 5 change (usually more accurate)
- Actual code duplication detected
- Phase 5 see score decreases if duplicates were undetected before

---

## Rollback (If Needed)

### If You Need to Revert

**Option 1: Disable New Features**

Edit `workflow.yaml`:
```yaml
scoring:
  coverage:
    enabled: false
  dup:
    heuristic: "simple"  # Back to v1.3.x behavior
```

**Option 2: Restore Backup**

```bash
# Restore v1.3.x results
mv audit_artifacts.v1.3.backup audit_artifacts
mv reports.v1.3.backup reports
mv workflow.yaml.v1.3.backup workflow.yaml
```

**Option 3: Revert Code**

```bash
# Check out previous commit (if you pulled v1.4.0)
git log --oneline | grep "v1.3"
git checkout <v1.3-commit-hash>
```

---

## Troubleshooting Migration Issues

### Issue: Audit fails after upgrade

**Check**:
```bash
# Verify Python dependencies
pip install pyyaml jinja2

# Check for syntax errors in workflow.yaml
python -c "import yaml; yaml.safe_load(open('workflow.yaml'))"

# Run in verbose mode
python scripts/space_traversal/audit_runner.py run --verbose
```

### Issue: Coverage not working

**Solutions**:
- Ensure coverage.xml exists: `ls -lh coverage.xml`
- Check xml_patterns match your file location
- Verify coverage has data: `grep "line-rate" coverage.xml`
- See [Troubleshooting Guide](./Troubleshooting_v1.4.0.md)

### Issue: Scores decreased significantly

**This is expected** if:
- Token-similarity detected actual duplicates that were missed before
- Coverage data revealed lower test coverage than estimated

**Actions**:
1. Review which capabilities decreased
2. Check if duplication or coverage gaps are real
3. Consider this accurate feedback for improvements

**If you disagree with new scores**:
- Lower token-similarity threshold (more lenient)
- Disable coverage augmentation temporarily
- See [Configuration Guide](./Configuration_v1.4.0.md)

---

## Validation Checklist

After migration, verify:

- [ ] Audit runs successfully: `make space-audit`
- [ ] capabilities_scored.json generated
- [ ] Reports generated in reports/ directory
- [ ] (If enabled) coverage_map.json exists
- [ ] (If enabled) Token-similarity is working (check consistency scores)
- [ ] Scores are reasonable and explainable
- [ ] No regression in audit pipeline functionality

---

## Post-Migration Recommendations

1. **Review Score Changes**:
   ```bash
   python scripts/space_traversal/audit_runner.py diff \
     audit_artifacts.v1.3.backup/capabilities_scored.json \
     audit_artifacts/capabilities_scored.json
   ```

2. **Update CI/CD**:
   - Add coverage generation if using coverage augmentation
   - Document new configuration in team wiki

3. **Monitor Performance**:
   - Track audit pipeline runtime
   - Tune token-similarity parameters if needed
   - See [Performance Tuning](./Performance_Tuning.md)

4. **Communicate Changes**:
   - Inform team of v1.4.0 upgrade
   - Explain score changes if significant
   - Share new capability insights

---

## FAQ

### Q: Do I have to enable the new features?

**A**: No. v1.4.0 is fully backward compatible. New features are opt-in.

### Q: Will my scores change?

**A**: Not unless you enable the new features. With default settings, v1.4.0 behaves like v1.3.x.

### Q: Can I enable coverage without token-similarity?

**A**: Yes. Features are independent and can be enabled separately.

### Q: What if I don't have tests with coverage?

**A**: Coverage augmentation will be skipped automatically. No errors will occur.

### Q: Is v1.4.0 slower than v1.3.x?

**A**: With default settings, no. Token-similarity can be slower for large codebases, but it's opt-in. See [Performance Tuning](./Performance_Tuning.md).

### Q: Can I gradually roll out v1.4.0?

**A**: Yes. Recommended approach:
1. Upgrade to v1.4.0 (backward compatible)
2. Test with existing configuration
3. Enable coverage augmentation
4. Enable token-similarity
5. Tune as needed

---

## Getting Help

- **Configuration**: See [Configuration Guide](./Configuration_v1.4.0.md)
- **Issues**: See [Troubleshooting Guide](./Troubleshooting_v1.4.0.md)
- **API**: See [API Reference](./API_Reference_v1.4.0.md)
- **Integrations**: See [Integration Examples](./Integration_Examples.md)
- **Performance**: See [Performance Tuning](./Performance_Tuning.md)

---

## Summary

v1.4.0 migration is **easy and safe**:
- ✅ Fully backward compatible
- ✅ No breaking changes
- ✅ New features are opt-in
- ✅ Can rollback easily if needed
- ✅ Comprehensive documentation available

**Recommendation**: Upgrade now, test, then gradually enable new features.
