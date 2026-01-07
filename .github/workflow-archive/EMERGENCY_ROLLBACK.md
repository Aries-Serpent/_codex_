# Emergency Rollback Playbook

**Generated**: 2025-12-28  
**Purpose**: Quick reference for restoring workflows if issues arise post-consolidation

---

## 🚨 When to Use This Playbook

Use this playbook if:
- Critical CI workflows fail after consolidation
- Functionality is broken and cannot be quickly fixed
- Immediate restoration is required to unblock development

---

## ⚡ Quick Rollback (Option 1: Full Restoration)

**Time**: ~2 minutes  
**Impact**: Restores all 67 original workflows

```bash
# Navigate to repository root
cd /path/to/_codex_

# Copy all workflows from backup
cp .github/workflow-archive/backups/2025-12-28/*.yml .github/workflows/

# Verify count
ls -1 .github/workflows/*.yml | wc -l  # Should show 67

# Commit and push
git add .github/workflows/
git commit -m "rollback: restore all 67 workflows from 2025-12-28 backup"
git push origin main

# Verify workflows are enabled
gh run list --limit 5
```

**Verification**: Check that all expected workflows appear in GitHub Actions UI

---

## 🎯 Selective Rollback (Option 2: Restore Single Workflow)

**Time**: ~1 minute per workflow  
**Impact**: Restores specific workflow(s)

### Example: Restore test-suite.yml

```bash
# Copy workflow from disabled archive
cp .github/workflow-archive/disabled/test-suite.yml .github/workflows/

# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/test-suite.yml'))"

# Commit and push
git add .github/workflows/test-suite.yml
git commit -m "restore: test-suite.yml"
git push origin main
```

### Available Workflows for Restoration

List all disabled workflows:
```bash
ls -1 .github/workflow-archive/disabled/*.yml
```

Current disabled workflows (19 total):
1. test-suite.yml
2. mcp-ci.yml
3. docs.yml
4. validate-docs.yml
5. validate-docs-enhanced.yml
6. container-build.yml
7. build-container-cache.yml
8. workflow-lint.yml
9. workflow-validator.yml
10. template-validation.yml
11. daily_status_cron.yml
12. daily_status_enrich.yml
13. automation_ingest.yml
14. produce-trend.yml
15. report_publish.yml
16. cache-cleanup.yml
17. cache-warmer.yml
18. duplicate-detection-weekly.yml
19. post-merge-validation.yml

---

## 🖥️ UI-Driven Rollback (Option 3: Workflow Restore Tool)

**Time**: ~2 minutes  
**Impact**: Restores single workflow via GitHub Actions UI

### Steps

1. Navigate to your repository on GitHub
2. Click **Actions** tab
3. Find **Workflow Restore Tool** in left sidebar
4. Click **Run workflow** button
5. Fill in parameters:
   - **workflow_file**: Select workflow to restore (dropdown)
   - **restore_source**: Choose `archive-disabled`
   - **enable_immediately**: Select `true`
6. Click **Run workflow** button
7. Wait for completion (~30 seconds)
8. Verify workflow appears in Actions list

---

## 🔍 Backup Integrity Verification

Before any rollback, verify backup integrity:

```bash
# Navigate to backup directory
cd .github/workflow-archive/backups/2025-12-28/

# Verify SHA256 checksums
sha256sum -c MANIFEST.txt

# Expected output: All files should show "OK"
# Example:
# agent-runtime.yml: OK
# api-documentation.yml: OK
# ...
```

If checksum verification fails:
```bash
# Re-run backup script to create fresh backup
bash scripts/backup_workflows.sh

# Use new backup location
cp .github/workflow-archive/backups/$(date +%Y-%m-%d)/*.yml .github/workflows/
```

---

## 📋 Post-Rollback Checklist

After performing any rollback:

- [ ] Verify workflow count: `find .github/workflows -name "*.yml" | wc -l` (should be 67 for full rollback)
- [ ] Check YAML syntax: Run `bash scripts/validate_ci_health.sh`
- [ ] Monitor GitHub Actions: Watch for workflow execution in Actions tab
- [ ] Update team: Notify stakeholders of rollback
- [ ] Document issue: Create GitHub issue with rollback reason and details
- [ ] Plan fix: Determine root cause and fix strategy before re-attempting consolidation

---

## 🛠️ Troubleshooting

### Issue: Workflows not appearing in GitHub Actions UI

**Solution**:
```bash
# Check if files were committed
git log --oneline -1

# Check if files are present
ls -la .github/workflows/

# Force push if needed (use with caution)
git push --force origin main
```

### Issue: YAML syntax errors after restoration

**Solution**:
```bash
# Validate each workflow
for file in .github/workflows/*.yml; do
    python -c "import yaml; yaml.safe_load(open('$file'))" || echo "❌ $file has syntax error"
done

# Fix syntax errors or restore from backup again
cp .github/workflow-archive/backups/2025-12-28/BROKEN_FILE.yml .github/workflows/
```

### Issue: Workflows restored but not running

**Solution**:
1. Check workflow triggers in YAML (on: push, on: pull_request, etc.)
2. Verify branch protections haven't changed
3. Check workflow permissions in repository settings
4. Manually trigger workflow: Actions → Select workflow → Run workflow

---

## 📞 Escalation

If rollback fails or issues persist:

1. **Check CI Health Script**:
   ```bash
   bash scripts/validate_ci_health.sh
   ```

2. **Review Consolidation Report**:
   ```bash
   cat .github/workflow-archive/FINAL_CONSOLIDATION_REPORT.md
   ```

3. **Contact Repository Maintainers**:
   - Open GitHub issue with:
     - Rollback steps attempted
     - Error messages
     - CI health report output
     - Specific workflows affected

4. **Emergency Contact**: @mbaetiong (repository owner)

---

## 🔐 Backup Locations

### Primary Backup
- **Location**: `.github/workflow-archive/backups/2025-12-28/`
- **Files**: 67 workflows
- **Checksum**: MANIFEST.txt with SHA256 hashes
- **Retention**: Indefinite (never delete)

### Disabled Archive
- **Location**: `.github/workflow-archive/disabled/`
- **Files**: 19 disabled workflows + metadata (.meta files)
- **Purpose**: Consolidation archive with restoration metadata
- **Retention**: Indefinite (never delete)

### Backup Manifest Structure
```
.github/workflow-archive/backups/2025-12-28/
├── MANIFEST.txt (SHA256 checksums)
├── agent-runtime.yml
├── api-documentation.yml
├── ... (65 more workflows)
```

---

## 📊 Rollback Success Metrics

After rollback, verify these metrics:

| Metric | Expected | Command |
|--------|----------|---------|
| Workflow count | 67 | `find .github/workflows -name "*.yml" \| wc -l` |
| YAML validity | 100% pass | `bash scripts/validate_ci_health.sh` |
| Active workflows | All enabled | Check GitHub Actions UI |
| Recent CI runs | Passing | `gh run list --limit 10` |
| No missing files | 0 | Compare backup vs workflows dir |

---

## 🔄 Re-Consolidation Planning

If rollback is successful and you want to re-attempt consolidation:

1. **Root Cause Analysis**: Document why original consolidation failed
2. **Test Plan**: Create testing strategy for re-consolidation
3. **Phased Approach**: Consolidate 1-2 workflows at a time
4. **Monitoring**: Watch CI for 24 hours after each phase
5. **Rollback Ready**: Keep this playbook handy for quick reversion

---

**Last Updated**: 2025-12-28  
**Status**: ✅ Ready for Use  
**Maintenance**: Update after each successful consolidation change
