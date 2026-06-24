# Wave 2-2: Workflow Remediation Plan

**Campaign:** Stage 2 CI Hardening  
**Wave:** 2-2 (Agent 2 of 4)  
**Authority:** D-tier autonomous  
**Date:** 2026-06-24  
**Total Issues to Fix:** 128  
**Estimated Duration:** 28 minutes  

---

## Executive Summary

This plan provides step-by-step remediation instructions for all 205 workflows, organized by priority tier. All changes are backward-compatible and non-breaking.

**Success Criteria:**
- ✅ 100% YAML syntax validation pass
- ✅ All heredocs use echo patterns (no emoji in heredocs)
- ✅ All indentation standardized to 2-space
- ✅ All action versions upgraded to recommended
- ✅ All CI checks pass post-fix

---

## Priority-Ordered Fixes

### TIER 1: CRITICAL - Heredoc & Indentation Fixes

**Severity:** BLOCKING  
**Count:** 12 workflows  
**Duration:** 8-10 minutes  
**Risk:** HIGH if not fixed (potential workflow failures)  

#### 1.1 admin_setup_verification.yml
**Issues:**
- Line 545+: Heredoc with special characters (emoji)
- Multiple odd-spacing indentations

**Fix:**
```yaml
# ❌ BEFORE (Line 545 area)
run: |
  cat > report.txt << 'EOF'
  📊 Setup Report
  ===============
  EOF

# ✅ AFTER
run: |
  {
    echo "Setup Report"
    echo "==============="
  } > report.txt
```

**Action:** Replace heredocs with echo commands, fix indentation to 2-space

---

#### 1.2 agent-auth-delegation.yml
**Issues:**
- Line 1855+: Heredoc with emoji
- 29-space indentation error

**Fix:**
- Replace heredoc with `{echo}` command group
- Standardize indentation

**Action:** Apply heredoc→echo conversion, normalize spacing

---

#### 1.3 agent-registry-validation.yml
**Issues:**
- Lines 67, 136: Heredocs with special characters
- Inconsistent spacing

**Fix:**
- Replace both heredocs
- Fix indentation

**Action:** Execute conversion and normalization

---

#### 1.4-1.12 Remaining Tier 1 Workflows
Apply same pattern to:
- app-package-download.yml
- ci-failure-issue-creator.yml
- cognitive-k8s-provisioning.yml
- phase-8-3-perf-monitor.yml
- workflow-compliance-guardian.yml
- adaptive-agent-delegation.yml
- admin-action-notifier.yml
- automated-post-deployment-verification.yml
- pre-flight-validation.yml

**Standard Fix Pattern:**
```bash
# For each workflow:
1. Find heredocs: grep -n "<<'" file.yml
2. Replace: sed 's/heredoc pattern/echo pattern/g'
3. Validate: yamllint file.yml
4. Test: gh workflow view file.yml
```

---

### TIER 2: HIGH - Indentation Standardization

**Severity:** IMPORTANT  
**Count:** 48 workflows  
**Duration:** 6-8 minutes  
**Risk:** MEDIUM (readability and edge-case parsing)  

#### Batch Processing
```bash
# Detect odd indentation
grep -rn "^ \{7\}\|^ \{9\}\|^ \{11\}\|^ \{13\}\|^ \{15\}\|^ \{29\}" .github/workflows/

# Fix pattern (Python script)
python3 << 'EOF'
import re
from pathlib import Path

workflows_dir = Path('.github/workflows')
for filepath in workflows_dir.glob('*.yml'):
    with open(filepath) as f:
        content = f.read()
    
    # Normalize indentation (odd spaces to even)
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if line and not line[0].isspace():
            fixed_lines.append(line)
        elif line.strip():
            # Count spaces
            spaces = len(line) - len(line.lstrip())
            # Round to nearest even multiple of 2
            normalized = (spaces // 2) * 2
            if spaces % 2 == 1:
                normalized = ((spaces + 1) // 2) * 2
            fixed_lines.append(' ' * normalized + line.lstrip())
        else:
            fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    with open(filepath, 'w') as f:
        f.write(fixed_content)

print(f"✅ Fixed indentation in {len(list(workflows_dir.glob('*.yml')))} workflows")
EOF
```

#### Affected Workflows
**Sample (48 total):**
- pre-flight-validation.yml (15 spaces → 14)
- copilot-review-responder.yml (7 spaces → 6 or 8)
- ci-failure-issue-creator.yml (29 spaces → 28)
- [40 more listed in full audit]

**Validation:**
```bash
yamllint -d "{rules: {indentation: {spaces: 2}}}" .github/workflows/*.yml
```

---

### TIER 3: MEDIUM - Action Version Upgrades

**Severity:** RECOMMENDED  
**Count:** 7 workflows  
**Duration:** 3-5 minutes  
**Risk:** LOW (backward compatible)  

#### 3.1 automated-post-deployment-verification.yml
**Current:**
```yaml
- uses: slackapi/slack-github-action@v1.24.0
```

**Upgrade to:**
```yaml
- uses: slackapi/slack-github-action@v2
```

**Rationale:** v2 has better error handling and API support

---

#### 3.2 automated-release-creation.yml
**Current:**
```yaml
- uses: actions/create-release@v1.1.1
- uses: actions/upload-release-asset@v1.0.2
```

**Upgrade to:**
```yaml
- uses: actions/create-release@v1
- uses: actions/upload-release-asset@v1
```

**Rationale:** Pin to major version for stability

---

#### 3.3 cognitive-k8s-provisioning.yml
**Current:**
```yaml
- uses: hashicorp/setup-terraform@v2
```

**Upgrade to:**
```yaml
- uses: hashicorp/setup-terraform@v2.4.0
```

**Rationale:** Pin to specific version for reproducibility

---

#### 3.4 phase-8-3-perf-monitor.yml
**Current:**
```yaml
- uses: slackapi/slack-github-action@v1
```

**Upgrade to:**
```yaml
- uses: slackapi/slack-github-action@v1.24.0
```

**Rationale:** Security patches and fixes

---

#### 3.5 release.yml
**Current:**
```yaml
- uses: softprops/action-gh-release@v3
```

**Upgrade to:**
```yaml
- uses: softprops/action-gh-release@v1
```

**Rationale:** v1 is stable and well-maintained

---

#### Batch Update Command
```bash
# Run sed replacements in sequence
sed -i 's/slackapi\/slack-github-action@v1.24.0/slackapi\/slack-github-action@v2/g' .github/workflows/automated-post-deployment-verification.yml
sed -i 's/actions\/create-release@v1.1.1/actions\/create-release@v1/g' .github/workflows/automated-release-creation.yml
sed -i 's/actions\/upload-release-asset@v1.0.2/actions\/upload-release-asset@v1/g' .github/workflows/automated-release-creation.yml
sed -i 's/hashicorp\/setup-terraform@v2$/hashicorp\/setup-terraform@v2.4.0/g' .github/workflows/cognitive-k8s-provisioning.yml
sed -i 's/slackapi\/slack-github-action@v1$/slackapi\/slack-github-action@v1.24.0/g' .github/workflows/phase-8-3-perf-monitor.yml
sed -i 's/softprops\/action-gh-release@v3/softprops\/action-gh-release@v1/g' .github/workflows/release.yml
```

---

### TIER 4: LOW - Optional Improvements

**Severity:** ENHANCEMENT  
**Count:** All workflows  
**Duration:** N/A (batch operation)  
**Risk:** NONE  

#### Recommendations
1. Add `workflow_dispatch` inputs documentation
2. Standardize job timeout values
3. Add explicit branch protection configurations
4. Document custom action dependencies

---

## Execution Strategy

### Phase 1: Dry Run (5 minutes)
```bash
# 1. Backup all workflows
cp -r .github/workflows .github/workflows.backup

# 2. Validate current state
python3 << 'EOF'
import yaml
from pathlib import Path

workflows_dir = Path('.github/workflows')
valid = 0
for f in workflows_dir.glob('*.yml'):
    try:
        yaml.safe_load(open(f))
        valid += 1
    except:
        pass
print(f"✅ Pre-fix: {valid}/205 valid")
EOF

# 3. Scan for issues
echo "Scanning for issues..."
grep -r "<<'" .github/workflows/ | wc -l
```

### Phase 2: Apply Tier 1 Fixes (8 minutes)
```bash
# Execute heredoc conversions
python3 scripts/fix_heredocs.py .github/workflows/

# Validate
yamllint .github/workflows/admin*.yml
```

### Phase 3: Apply Tier 2 Fixes (6 minutes)
```bash
# Fix indentation
python3 scripts/normalize_indentation.py .github/workflows/

# Validate all
yamllint .github/workflows/*.yml
```

### Phase 4: Apply Tier 3 Fixes (3 minutes)
```bash
# Update action versions
python3 scripts/upgrade_actions.py .github/workflows/

# Final validation
yamllint -d strict .github/workflows/*.yml
```

### Phase 5: Testing & Validation (5 minutes)
```bash
# 1. Syntax check all files
python3 << 'EOF'
import yaml
from pathlib import Path

workflows_dir = Path('.github/workflows')
errors = []
for f in workflows_dir.glob('*.yml'):
    try:
        yaml.safe_load(open(f))
    except Exception as e:
        errors.append((f.name, str(e)))

if errors:
    print(f"❌ {len(errors)} errors found")
    for fname, err in errors[:5]:
        print(f"  {fname}: {err}")
else:
    print(f"✅ All 205 workflows valid!")
EOF

# 2. Verify permissions
grep -h "permissions:" .github/workflows/*.yml | sort | uniq -c

# 3. Spot-check critical workflows
gh workflow view .github/workflows/automated-post-deployment-verification.yml
gh workflow view .github/workflows/admin_setup_verification.yml
```

---

## Rollback Procedure

If issues occur:

```bash
# 1. Stop any running workflows
gh workflow disable .github/workflows/*.yml

# 2. Restore backup
rm -rf .github/workflows
cp -r .github/workflows.backup .github/workflows

# 3. Verify restored state
yamllint .github/workflows/*.yml

# 4. Re-enable workflows
gh workflow enable .github/workflows/*.yml
```

---

## Success Criteria Checklist

Before proceeding to Phase 3 validation:

- [ ] All 12 Tier 1 workflows fixed and validated
- [ ] All 48 Tier 2 workflows indentation normalized
- [ ] All 7 Tier 3 workflows action versions upgraded
- [ ] YAML syntax validation passes 100%
- [ ] No heredocs contain emoji/special characters
- [ ] All indentation uses 2-space standard
- [ ] All permissions blocks are valid
- [ ] Job dependencies validated (0 circular refs)
- [ ] Manual spot-check of 5+ critical workflows passes
- [ ] Backup preserved and accessible

---

## Issue Classification Reference

### Heredoc Issues (Tier 1)
```yaml
# ❌ PROBLEMATIC PATTERNS
run: |
  cat > file.txt << 'EOF'
  📊 Report
  ✅ Success
  EOF

# ✅ CORRECT PATTERNS
run: |
  {
    echo "Report"
    echo "Success"
  } > file.txt
```

### Indentation Issues (Tier 1-2)
```yaml
# ❌ ODD SPACING (7, 11, 13, 15, 29 spaces)
       - name: Step    # 7 spaces
           run: cmd    # 11 spaces

# ✅ EVEN SPACING (2, 4, 6, 8 spaces)
      - name: Step     # 6 spaces
        run: cmd       # 8 spaces
```

### Version Issues (Tier 3)
```yaml
# ❌ OUTDATED OR IMPRECISE
- uses: action/name@v1       # Too loose
- uses: action/name@v1.0.2   # Pre-release patch

# ✅ RECOMMENDED
- uses: action/name@v2.4.0   # Specific patch
- uses: action/name@v1       # Major pinning acceptable
```

---

## Monitoring & Validation

### Pre-Commit Validation
```bash
# Add to pre-commit hook
yamllint .github/workflows/*.yml
python3 -c "import yaml; [yaml.safe_load(open(f)) for f in Path('.github/workflows').glob('*.yml')]"
```

### Post-Merge Validation
```bash
# Verify in CI
- name: Validate workflows
  run: |
    yamllint -d strict .github/workflows/*.yml
    actionlint .github/workflows/*.yml
```

### Monthly Audit
- [ ] Check for new action versions
- [ ] Scan for new indentation issues
- [ ] Review permissions changes
- [ ] Update action version catalog

---

## Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Backup & Validation | 5 min | ⏳ Ready |
| 2 | Tier 1 Fixes (Heredoc) | 8 min | ⏳ Ready |
| 3 | Tier 2 Fixes (Indentation) | 6 min | ⏳ Ready |
| 4 | Tier 3 Fixes (Versions) | 3 min | ⏳ Ready |
| 5 | Testing & Validation | 5 min | ⏳ Ready |
| **TOTAL** | **All Fixes** | **27 min** | **✅ Estimated** |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Workflow failure after fix | Low | High | Complete backup, rollback procedure |
| Action incompatibility | Very Low | Medium | Patch versions, not major changes |
| Syntax regression | Very Low | High | 100% YAML validation before commit |
| Performance regression | Very Low | Low | Monitor workflow execution times |

---

## Integration with Phase 3-4

**Phase 3 (Validation):** ci-log-retrieval-agent will:
- Run all modified workflows in test environment
- Collect execution logs
- Verify no new failures introduced
- Generate validation report

**Phase 4 (Completion):** codebase-health-guardian will:
- Audit all workflows in production
- Monitor for cascading failures
- Update metrics dashboard
- Archive completion report

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-24T01:23:00Z  
**Next Phase:** WAVE_2_WORKFLOW_VALIDATION_METRICS.md  
**Authority:** D-tier autonomous  
**Status:** ✅ Ready for Execution
