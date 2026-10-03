# WORKFLOW ACTION VERSION FIX CHECKLIST

**Phase**: 3.2 Audit & Remediation
**Target**: 422 action version violations across 212 workflows
**Automation**: Ready for batch processing
**Estimated Duration**: 20 minutes total

---

## HIGH PRIORITY - actions/checkout@v7 → v5

### Statistics
- **Total Violations**: 306
- **Affected Workflows**: 160
- **Complexity**: LOW (simple sed replacement)
- **Risk**: VERY LOW

### Violation List (Top 20)

| # | Workflow | Violations | Status |
|----|----------|-----------|--------|
| 1 | rust_swarm_ci.yml | 10 | ⏳ PENDING |
| 2 | progressive-validation.yml | 7 | ⏳ PENDING |
| 3 | agent-auth-delegation.yml | 6 | ⏳ PENDING |
| 4 | iterative-self-healing-ci.yml | 5 | ⏳ PENDING |
| 5 | agent_infrastructure_manager.yml | 5 | ⏳ PENDING |
| 6 | cognitive-brain-session-injector.yml | 4 | ⏳ PENDING |
| 7 | post-merge-doc-alignment-agent.yml | 4 | ⏳ PENDING |
| 8 | adaptive-agent-delegation.yml | 4 | ⏳ PENDING |
| 9 | workflow-ci-audit-strict.yml | 4 | ⏳ PENDING |
| 10 | workflow-compliance-guardian.yml | 4 | ⏳ PENDING |
| 11 | ci-health-alert-agent.yml | 4 | ⏳ PENDING |
| 12 | semantic-search-indexing.yml | 4 | ⏳ PENDING |
| 13 | codeql-analysis.yml | 3 | ⏳ PENDING |
| 14 | archive-old-branches.yml | 3 | ⏳ PENDING |
| 15 | auth-tests.yml | 3 | ⏳ PENDING |
| 16 | dependency-scan.yml | 3 | ⏳ PENDING |
| 17 | issue-event-workflow.yml | 3 | ⏳ PENDING |
| 18 | security-alert-notification.yml | 3 | ⏳ PENDING |
| 19 | automated-monitoring-setup.yml | 2 | ⏳ PENDING |
| 20 | category-router.yml | 2 | ⏳ PENDING |

### Fix Command
```bash
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/checkout@v7/actions\/checkout@v5/g'
```

### Validation
```bash
# Count fixes applied
grep -r "actions/checkout@v5" .github/workflows/ | wc -l
# Should be >= 383 (300 fixed + 83 already correct)
```

---

## HIGH PRIORITY - actions/setup-python → v6

### Statistics
- **Total Violations**: 97 (2 direct + 95 custom)
- **Affected Workflows**: 66
- **Complexity**: MEDIUM (custom action requires review)
- **Risk**: LOW

### Direct Violations (2)

| # | Workflow | Current | Required | Status |
|----|----------|---------|----------|--------|
| 1 | agent-handoff-gate.yml | ./.github/actions/setup-python-cached | actions/setup-python@v6 | ⏳ PENDING |
| 2 | agent-orchestration-unified.yml | ./.github/actions/setup-python-cached | actions/setup-python@v6 | ⏳ PENDING |

### Custom Action: setup-python-cached (95 instances)
The custom action `./.github/actions/setup-python-cached` is used 95 times.

**Action**: Review compatibility with v6 standards
```bash
cat .github/actions/setup-python-cached/action.yml
```

**Assessment**: Custom action appears to be wrapper/caching mechanism
- Not a direct version violation
- May inherit from actions/setup-python
- Requires manual compatibility review

### Fix Strategy
```bash
# Fix only direct violations (if any exist beyond custom action)
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/setup-python@v[0-5]/actions\/setup-python@v6/g'

# Review custom action separately
ls -la .github/actions/setup-python-cached/
cat .github/actions/setup-python-cached/action.yml
```

---

## MEDIUM PRIORITY - actions/upload-artifact@v7 → v5

### Statistics
- **Total Violations**: 15
- **Affected Workflows**: 13
- **Complexity**: LOW (simple version bump)
- **Risk**: VERY LOW

### Violation List

| # | Workflow | Current | Required | Status |
|----|----------|---------|----------|--------|
| 1 | agent-health-check.yml | v7.0.1 | v5 | ⏳ PENDING |
| 2 | ci-pass-rate-gate.yml | v7.0.1 | v5 | ⏳ PENDING |
| 3 | container-scan.yml | v7.0.1 | v5 | ⏳ PENDING |
| 4 | codeql-analysis.yml | v7.0.1 | v5 | ⏳ PENDING |
| 5 | dependency-scan.yml | v7.0.1 | v5 | ⏳ PENDING |
| 6 | docs-health.yml | v7.0.1 | v5 | ⏳ PENDING |
| 7 | documentation-quality-check.yml | v7.0.1 | v5 | ⏳ PENDING |
| 8 | github-guru.yml | v7.0.1 | v5 | ⏳ PENDING |
| 9 | mcp-health.yml | v7.0.1 | v5 | ⏳ PENDING |
| 10 | nightly-codeql-alert-triage.yml | v7.0.1 | v5 | ⏳ PENDING |
| 11 | post-merge-validation-optimized.yml | v7.0.1 | v5 | ⏳ PENDING |
| 12 | security-scanning-suite.yml | v7.0.1 | v5 | ⏳ PENDING |
| 13 | test-pyramid-report.yml | v7.0.1 | v5 | ⏳ PENDING |

### Fix Command
```bash
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/upload-artifact@v7\.[0-9]\+/actions\/upload-artifact@v5/g'
```

### Validation
```bash
# Verify no v7.x remains
grep -r "upload-artifact@v7" .github/workflows/
# Should return nothing if successful
```

---

## LOW PRIORITY - actions/setup-node → v5

### Statistics
- **Total Violations**: 4
- **Affected Workflows**: 4
- **Complexity**: LOW (simple version bump)
- **Risk**: VERY LOW

### Violation List

| # | Workflow | Current | Required | Status |
|----|----------|---------|----------|--------|
| 1 | copilot-evolution-suite.yml | v4 | v5 | ⏳ PENDING |
| 2 | documentation-link-checker.yml | v4 | v5 | ⏳ PENDING |
| 3 | har-capture.yml | v4 | v5 | ⏳ PENDING |
| 4 | test-pyramid-report.yml | v4 | v5 | ⏳ PENDING |

### Fix Command
```bash
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/setup-node@v[0-4]/actions\/setup-node@v5/g'
```

### Validation
```bash
# Verify all are v5
grep -r "actions/setup-node" .github/workflows/
# All results should show @v5
```

---

## COMPLIANT - actions/github-script@v8

### Status: ✅ PASS - 0 Violations

All workflows using `actions/github-script` are correctly at version v8.

**Count**: 123 instances of actions/github-script@v8
**Action Required**: NONE

---

## EXECUTION PLAN

### Phase 1: Preparation (< 1 minute)

```bash
# Create feature branch
git checkout -b fix/phase-3-2-workflow-actions

# Create backup
find .github/workflows -type f \( -name "*.yml" -o -name "*.yaml" \) \
  -exec cp {} {}.backup \;
```

### Phase 2: Apply Fixes (< 5 minutes)

```bash
# Fix 1: actions/checkout
echo "Fixing actions/checkout..."
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/checkout@v7/actions\/checkout@v5/g'

# Fix 2: actions/upload-artifact
echo "Fixing actions/upload-artifact..."
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/upload-artifact@v7\.[0-9]\+/actions\/upload-artifact@v5/g'

# Fix 3: actions/setup-node
echo "Fixing actions/setup-node..."
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/setup-node@v[0-4]/actions\/setup-node@v5/g'

# Fix 4: actions/setup-python (direct only)
echo "Fixing actions/setup-python..."
find .github/workflows -name "*.yml" -o -name "*.yaml" | \
  xargs sed -i 's/actions\/setup-python@v[0-5]/actions\/setup-python@v6/g'

echo "✅ All fixes applied"
```

### Phase 3: Validation (< 10 minutes)

```bash
# Validate YAML syntax
echo "Validating YAML syntax..."
python3 << 'EOF'
import yaml
from pathlib import Path
errors = 0
for f in sorted(Path('.github/workflows').glob('*.yml')):
    try:
        yaml.safe_load(open(f))
    except Exception as e:
        print(f"❌ {f.name}: {e}")
        errors += 1
if errors == 0:
    print("✅ All workflows valid!")
else:
    print(f"❌ {errors} workflows have errors")
EOF

# Verify versions
echo ""
echo "=== VERSION SUMMARY ==="
echo "actions/checkout:"
grep -c "actions/checkout@v5" .github/workflows/*.yml 2>/dev/null || echo "0"

echo "actions/setup-python:"
grep -c "actions/setup-python@v6" .github/workflows/*.yml 2>/dev/null || echo "0"

echo "actions/upload-artifact:"
grep -c "actions/upload-artifact@v5" .github/workflows/*.yml 2>/dev/null || echo "0"

echo "actions/setup-node:"
grep -c "actions/setup-node@v5" .github/workflows/*.yml 2>/dev/null || echo "0"
```

### Phase 4: Commit & Deploy (< 5 minutes)

```bash
# Stage changes
git add .github/workflows/
git add .codex/

# Commit
git commit -m "Phase 3.2: Fix action version violations

- Fixed actions/checkout@v7 → v5 (306 violations)
- Fixed actions/setup-python → v6 (2 direct violations)
- Fixed actions/upload-artifact@v7 → v5 (15 violations)
- Fixed actions/setup-node → v5 (4 violations)
- Total: 327 violations remediated
- All workflows validated and passing
"

# Push for review
git push origin fix/phase-3-2-workflow-actions
```

---

## QUALITY ASSURANCE

### Pre-Merge Checklist

- [ ] All YAML files parse correctly
- [ ] No new syntax errors introduced
- [ ] All 4 action versions are fixed
- [ ] 327+ violations remediated
- [ ] 212/212 workflows validated
- [ ] Job dependencies unchanged
- [ ] Condition logic unchanged

### Post-Merge Verification

- [ ] PR merged to main
- [ ] CI/CD pipeline passes
- [ ] No workflow execution failures
- [ ] Monitor for 24 hours post-deployment

---

## ROLLBACK PLAN

If issues arise:

```bash
# Restore backups
find .github/workflows -name "*.backup" | while read f; do
  mv "$f" "${f%.backup}"
done

# Verify restore
python3 -c "import yaml; [yaml.safe_load(open(f)) for f in ...]"
```

---

**Last Updated**: 2026-07-02
**Status**: ✅ READY FOR EXECUTION
**Estimated Total Time**: 20 minutes
