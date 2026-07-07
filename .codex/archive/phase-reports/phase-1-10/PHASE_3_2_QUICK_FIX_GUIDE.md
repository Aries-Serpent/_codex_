# PHASE 3.2 QUICK FIX GUIDE
## Workflow YAML Audit - Remediation Instructions

**Last Updated**: 2026-01-23  
**Status**: Ready for Implementation  
**Estimated Time**: 40 minutes (Tier 1 Critical Fixes)

---

## 🚨 CRITICAL FIXES (8 files - 40 minutes)

### Issue: Invalid GitHub Actions Permission `discussions`

**Files Affected** (8 total):
1. `.github/workflows/automated-release-creation.yml`
2. `.github/workflows/copilot-agent-checkin.yml`
3. `.github/workflows/discussion-cleanup.yml`
4. `.github/workflows/discussion-response-bridge.yml`
5. `.github/workflows/post-accountability-to-discussion.yml`
6. `.github/workflows/post-ci-status-to-discussion.yml`
7. `.github/workflows/post-phase-4-5-to-discussion.yml`
8. `.github/workflows/post-phase-update-to-discussion.yml`

### Quick Fix (Copy-Paste Script)

```bash
#!/bin/bash
# Remove invalid 'discussions' permission from all affected files

cd /home/runner/work/_codex_/_codex_

# List of files to fix
FILES=(
  ".github/workflows/automated-release-creation.yml"
  ".github/workflows/copilot-agent-checkin.yml"
  ".github/workflows/discussion-cleanup.yml"
  ".github/workflows/discussion-response-bridge.yml"
  ".github/workflows/post-accountability-to-discussion.yml"
  ".github/workflows/post-ci-status-to-discussion.yml"
  ".github/workflows/post-phase-4-5-to-discussion.yml"
  ".github/workflows/post-phase-update-to-discussion.yml"
)

echo "Fixing invalid 'discussions' permission..."
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    # Remove the discussions: write line
    sed -i '/^[[:space:]]*discussions:[[:space:]]*write$/d' "$file"
    echo "✓ Fixed: $file"
  else
    echo "⚠ File not found: $file"
  fi
done

echo ""
echo "Validating YAML syntax..."
python3 << 'PYEOF'
import yaml
from pathlib import Path

files = [
    ".github/workflows/automated-release-creation.yml",
    ".github/workflows/copilot-agent-checkin.yml",
    ".github/workflows/discussion-cleanup.yml",
    ".github/workflows/discussion-response-bridge.yml",
    ".github/workflows/post-accountability-to-discussion.yml",
    ".github/workflows/post-ci-status-to-discussion.yml",
    ".github/workflows/post-phase-4-5-to-discussion.yml",
    ".github/workflows/post-phase-update-to-discussion.yml",
]

errors = 0
for f in files:
    try:
        yaml.safe_load(Path(f).read_text())
        print(f"✅ {f}")
    except Exception as e:
        print(f"❌ {f}: {e}")
        errors += 1

if errors == 0:
    print("\n✅ All files validate successfully!")
else:
    print(f"\n❌ {errors} file(s) failed validation")
    exit(1)
PYEOF
```

### Manual Fix (Step-by-Step)

For each file:

1. **Open the file** in your editor
2. **Find the line** with `discussions: write`
3. **Delete that line**
4. **Save the file**

Example (automated-release-creation.yml):
```yaml
# BEFORE (Line 14-17):
permissions:
  contents: write
  discussions: write  # ← DELETE THIS LINE
  packages: write

# AFTER (Line 14-16):
permissions:
  contents: write
  packages: write
```

### Validation

After applying the fix:

```bash
# Quick syntax check
python3 -c "
import yaml
from pathlib import Path
for f in ['.github/workflows/automated-release-creation.yml', 
          '.github/workflows/copilot-agent-checkin.yml',
          '.github/workflows/discussion-cleanup.yml',
          '.github/workflows/discussion-response-bridge.yml',
          '.github/workflows/post-accountability-to-discussion.yml',
          '.github/workflows/post-ci-status-to-discussion.yml',
          '.github/workflows/post-phase-4-5-to-discussion.yml',
          '.github/workflows/post-phase-update-to-discussion.yml']:
    try:
        yaml.safe_load(Path(f).read_text())
        print(f'✅ {f}')
    except Exception as e:
        print(f'❌ {f}: {e}')
"
```

---

## 📊 TIER 2 FIXES (207 heredocs - 1-2 weeks)

### Pattern: Heredoc Usage in Workflows

**Issue**: Heredocs can cause YAML parsing errors with special characters  
**Count**: 207+ occurrences across 120+ workflows  
**Risk**: Medium (may cause runtime failures)  
**Timeline**: 1-2 weeks (progressive remediation)

### Top 20 High-Priority Files

```
1.  adaptive-agent-delegation.yml
2.  admin_setup_verification.yml
3.  agent-auth-delegation.yml
4.  agent-health-check.yml
5.  agent-registry-validation.yml
6.  agent_infrastructure_manager.yml
7.  app-package-download.yml
8.  auto-approve-workflows.yml
9.  automated-monitoring-setup.yml
10. automated-post-deployment-verification.yml
... (see full list in PHASE_3_2_WORKFLOW_AUDIT_REPORT.md)
```

### Fix Pattern 1: Replace with Echo Groups

**Before** (❌ RISKY):
```yaml
run: |
  cat > report.txt << 'EOF'
  📊 Benchmark Report
  ===================
  EOF
```

**After** (✅ SAFE):
```yaml
run: |
  {
    echo "📊 Benchmark Report"
    echo "==================="
  } > report.txt
```

### Fix Pattern 2: Use Printf

**Before** (❌ RISKY):
```yaml
run: |
  python3 << 'PYEOF'
  # Code here
  PYEOF
```

**After** (✅ SAFE):
```yaml
- name: Run Python
  run: python3 << 'PYEOF'
import json
# Code here
PYEOF
```

---

## ✅ VALIDATION CHECKLIST

Before committing changes:

- [ ] All 8 critical files fixed
- [ ] YAML syntax validates: `python3 -m yaml [file]`
- [ ] No invalid permissions found: `grep -r "discussions:" .github/workflows/`
- [ ] Workflows parse correctly
- [ ] Test workflows pass
- [ ] No new errors introduced

---

## 📋 COMMIT TEMPLATE

```
fix: Remove invalid 'discussions' permission from 8 workflows

SUMMARY:
- Removed unsupported 'discussions: write' permission from:
  * automated-release-creation.yml
  * copilot-agent-checkin.yml
  * discussion-cleanup.yml
  * discussion-response-bridge.yml
  * post-accountability-to-discussion.yml
  * post-ci-status-to-discussion.yml
  * post-phase-4-5-to-discussion.yml
  * post-phase-update-to-discussion.yml

DETAILS:
- GitHub Actions does not support 'discussions' as a permission
- Workflows must use GitHub API calls instead
- All affected workflows now use valid permissions only
- No functional changes, permission cleanup only

VALIDATION:
- ✅ All YAML files validate
- ✅ No workflow logic affected
- ✅ Ready for immediate deployment

Fixes: Phase 3.2 Workflow Audit (PHASE_3_2_WORKFLOW_AUDIT_REPORT.md)
```

---

## 🚀 IMPLEMENTATION TIMELINE

### Day 1 (Today) - 40 minutes
- [ ] Run critical fixes script
- [ ] Validate all 8 files
- [ ] Create and merge PR
- [ ] Verify workflows still trigger

### Week 1 (Next 5 days) - 200 minutes
- [ ] Identify top 20 heredoc issues
- [ ] Refactor high-priority workflows
- [ ] Test each change
- [ ] Progressive merge

### Week 2-3 (Following weeks) - 750+ minutes
- [ ] Continue medium-priority fixes
- [ ] Batch similar patterns
- [ ] Team review + testing
- [ ] Monitor for regressions

### Week 4+ - Ongoing
- [ ] Add linting to CI (actionlint)
- [ ] Document best practices
- [ ] Team training
- [ ] Monthly audits

---

## 🔗 REFERENCES

- **Audit Report**: `.codex/PHASE_3_2_WORKFLOW_AUDIT_REPORT.md`
- **Priority Matrix**: `.codex/PHASE_3_2_REMEDIATION_PRIORITY_MATRIX.json`
- **Official Docs**: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Permissions Docs**: https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token

---

**Status**: ✅ Ready for Implementation  
**Next Step**: Execute critical fixes script
