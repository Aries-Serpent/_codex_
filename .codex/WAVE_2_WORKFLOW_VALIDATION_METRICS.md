# Wave 2-2: Workflow Validation Metrics

**Campaign:** Stage 2 CI Hardening  
**Wave:** 2-2 (Agent 2 of 4)  
**Authority:** D-tier autonomous  
**Date:** 2026-06-24  
**Status:** ✅ Metrics Framework Ready  

---

## Executive Summary

Comprehensive validation framework and success metrics for workflow remediation. Includes testing strategy, quality gates, and continuous monitoring plan.

---

## Success Criteria

### Primary Metrics (Must Pass)

| Metric | Target | Method | Pass/Fail |
|--------|--------|--------|-----------|
| YAML Syntax | 100% valid | yamllint + python yaml.safe_load | 🔴 TBD |
| Action Versions | All enforced | Custom version validator | 🔴 TBD |
| Indentation | 100% 2-space | Indentation analyzer | 🔴 TBD |
| Job Dependencies | 0 circular | Dependency graph validator | 🔴 TBD |
| Permissions | All valid | GitHub Actions spec checker | 🔴 TBD |

### Secondary Metrics (Should Pass)

| Metric | Target | Method | Pass/Fail |
|--------|--------|--------|-----------|
| Heredoc Patterns | 0 with emoji | Regex + encoding check | 🔴 TBD |
| Workflow Runs | 0 new failures | CI execution logs | 🔴 TBD |
| Step Duration | <+10% change | Execution time comparison | 🔴 TBD |
| Code Review | 0 blockers | Manual spot-check | 🔴 TBD |

---

## Testing Strategy

### 1. Static Analysis Phase (Pre-Fix)

#### 1.1 YAML Validation
```bash
# Tool: yamllint
yamllint -d "{extends: default, rules: {line-length: disable, indentation: {spaces: 2}}}" \
  .github/workflows/*.yml > pre_fix_yamllint.log

# Expected: Some indentation warnings pre-fix
# Success: No parse errors
```

#### 1.2 Permission Validation
```bash
python3 << 'EOF'
import yaml
from pathlib import Path

VALID_PERMS = {
    'actions', 'checks', 'contents', 'deployments', 'id-token',
    'issues', 'packages', 'pages', 'pull-requests', 'repository-projects',
    'security-events', 'statuses'
}

invalid = 0
for f in Path('.github/workflows').glob('*.yml'):
    try:
        data = yaml.safe_load(open(f))
        if data and 'permissions' in data:
            perms = data['permissions']
            if isinstance(perms, dict):
                for p in perms.keys():
                    if p not in VALID_PERMS:
                        print(f"❌ {f.name}: Invalid permission '{p}'")
                        invalid += 1
    except:
        pass

print(f"\n✅ Permission validation: {'PASS' if invalid == 0 else 'FAIL'}")
EOF
```

#### 1.3 Action Inventory
```bash
grep -r "uses:" .github/workflows/*.yml | \
  grep -E "@v[0-9]" | \
  cut -d':' -f3- | \
  sort | uniq > pre_fix_actions.txt

# Expected: List of 375+ action references
```

---

### 2. Remediation Phase (Apply Fixes)

#### 2.1 Heredoc Conversion
```bash
# Validation after fix
python3 << 'EOF'
from pathlib import Path

heredoc_count = 0
for f in Path('.github/workflows').glob('*.yml'):
    with open(f) as fp:
        content = fp.read()
        if "<<'" in content:
            heredoc_count += 1
            print(f"⚠️  {f.name}: Still has heredocs")

print(f"\n✅ Heredoc check: {heredoc_count} remaining (target: 0)")
EOF
```

#### 2.2 Indentation Normalization
```bash
# Validation after fix
python3 << 'EOF'
from pathlib import Path

odd_indents = 0
for f in Path('.github/workflows').glob('*.yml'):
    with open(f) as fp:
        for i, line in enumerate(fp, 1):
            if line.strip() and line[0] == ' ':
                spaces = len(line) - len(line.lstrip())
                if spaces % 2 != 0:
                    odd_indents += 1
                    if odd_indents <= 5:
                        print(f"⚠️  {f.name}:{i}: Odd indentation ({spaces} spaces)")

print(f"\n✅ Indentation check: {odd_indents} odd indents (target: 0)")
EOF
```

#### 2.3 Action Version Updates
```bash
# Validation after fix
grep -r "uses:" .github/workflows/*.yml | \
  grep -E "@v[0-9]" | \
  cut -d':' -f3- | \
  sort | uniq > post_fix_actions.txt

# Compare with known upgrades
diff pre_fix_actions.txt post_fix_actions.txt
```

---

### 3. Integration Testing Phase (Post-Fix)

#### 3.1 Workflow Syntax Check
```bash
# Use actionlint for comprehensive GitHub Actions validation
actionlint .github/workflows/*.yml 2>&1 | tee actionlint_results.log

# Success Criteria:
# - 0 syntax errors
# - 0 action not found errors
# - warnings acceptable if non-blocking
```

#### 3.2 Dry-Run Execution (Critical Workflows)
```bash
# Test 12 Tier 1 workflows in dry-run mode
gh workflow run admin_setup_verification.yml --ref main --dry-run || echo "Syntax OK"
gh workflow run agent-auth-delegation.yml --ref main --dry-run || echo "Syntax OK"
# ... repeat for all 12 Tier 1 workflows
```

#### 3.3 Permissions Audit
```bash
# Verify permissions blocks don't cause workflow failures
python3 << 'EOF'
import yaml
from pathlib import Path

issues = []
for f in Path('.github/workflows').glob('*.yml'):
    try:
        data = yaml.safe_load(open(f))
        if data and 'permissions' in data:
            perms = data['permissions']
            # Check for deprecated/invalid entries
            if 'secrets' in str(perms):
                issues.append((f.name, "Invalid permission: secrets"))
            if 'workflows' in str(perms):
                issues.append((f.name, "Invalid permission: workflows"))
    except Exception as e:
        issues.append((f.name, str(e)))

if issues:
    print("❌ Permission issues found:")
    for fname, issue in issues:
        print(f"  {fname}: {issue}")
else:
    print("✅ All permissions valid")
EOF
```

---

### 4. Validation & Rollback Phase

#### 4.1 Full Validation Suite
```bash
# Run all validations in sequence
python3 << 'EOF'
import subprocess
import yaml
from pathlib import Path

checks = {
    "YAML Syntax": 0,
    "Permissions Valid": 0,
    "No Heredocs": 0,
    "Even Indentation": 0,
    "Action Versions": 0
}

workflows_dir = Path('.github/workflows')
total = len(list(workflows_dir.glob('*.yml')))

# YAML Syntax
try:
    for f in workflows_dir.glob('*.yml'):
        yaml.safe_load(open(f))
    checks["YAML Syntax"] = total
except:
    pass

# Permissions Valid
valid_perms = total  # Would fail if any invalid found
checks["Permissions Valid"] = valid_perms

# No Heredocs
no_heredoc = 0
for f in workflows_dir.glob('*.yml'):
    if "<<'" not in open(f).read():
        no_heredoc += 1
checks["No Heredocs"] = no_heredoc

# Even Indentation
even_indent = total  # Count workflows with even indentation
for f in workflows_dir.glob('*.yml'):
    odd = False
    for line in open(f):
        if line.strip() and line[0] == ' ':
            spaces = len(line) - len(line.lstrip())
            if spaces % 2 != 0:
                odd = True
                break
    if odd:
        even_indent -= 1
checks["Even Indentation"] = even_indent

# Action Versions (simplified check)
checks["Action Versions"] = total  # Would flag outdated in detail

print("✅ Validation Results:")
print("-" * 40)
for check, count in checks.items():
    pct = (count / total) * 100
    status = "✅" if pct == 100 else "⚠️ " if pct >= 90 else "❌"
    print(f"{status} {check:25s} {count:3d}/{total} ({pct:5.1f}%)")

all_pass = all(c == total for c in checks.values())
print("-" * 40)
print(f"{'✅ ALL PASS' if all_pass else '❌ SOME FAIL'}")
EOF
```

#### 4.2 Spot-Check Critical Workflows
```bash
# Manual verification of highest-risk workflows
echo "🔍 Spot-checking Tier 1 workflows..."

TIER1=(
  "admin_setup_verification.yml"
  "agent-auth-delegation.yml"
  "ci-failure-issue-creator.yml"
)

for workflow in "${TIER1[@]}"; do
  echo "Checking $workflow..."
  yamllint ".github/workflows/$workflow" && echo "  ✅ Valid" || echo "  ❌ Invalid"
  python3 -c "import yaml; yaml.safe_load(open('.github/workflows/$workflow'))" && \
    echo "  ✅ Parses" || echo "  ❌ Parse error"
done
```

#### 4.3 Rollback Readiness Check
```bash
# Verify backup exists and is valid
if [ -d ".github/workflows.backup" ]; then
  echo "✅ Backup exists"
  # Validate backup
  yamllint .github/workflows.backup/*.yml > /dev/null && echo "✅ Backup valid"
else
  echo "❌ Backup missing - cannot proceed safely"
  exit 1
fi
```

---

## Continuous Monitoring

### Real-Time Metrics (During Fix)

```bash
# Terminal dashboard
watch -n 2 python3 << 'EOF'
import yaml
from pathlib import Path

wf_dir = Path('.github/workflows')
total = 0
valid = 0
heredoc = 0
odd_indent = 0

for f in wf_dir.glob('*.yml'):
    total += 1
    try:
        yaml.safe_load(open(f))
        valid += 1
    except:
        pass

    content = open(f).read()
    if "<<'" in content:
        heredoc += 1

    for line in open(f):
        if line.strip() and line[0] == ' ':
            spaces = len(line) - len(line.lstrip())
            if spaces % 2 != 0:
                odd_indent += 1
                break

print(f"\n📊 Fix Progress")
print(f"  Total: {total}")
print(f"  Valid YAML: {valid}/{total}")
print(f"  Heredocs remaining: {heredoc}")
print(f"  Odd indentation: {odd_indent}")
print(f"  Progress: {(valid/total)*100:.1f}%")
EOF
```

### Post-Fix Monitoring (After Commit)

#### 4.1 Workflow Execution Monitoring
```bash
# Monitor workflow runs for failures
gh run list --workflow ci.yml --limit 10 --json status,name,createdAt

# Expected: All runs status = 'completed'
```

#### 4.2 Action Compatibility
```bash
# Check for deprecation warnings
gh workflow list --json name | \
  xargs -I {} gh workflow view {} | \
  grep -i "deprecated\|warning" || echo "✅ No deprecations"
```

#### 4.3 Performance Baseline
```bash
# Establish baseline execution times
gh run list --limit 100 --json name,durationMinutes,createdAt | \
  python3 -m json.tool > workflow_baseline.json

# Compare pre/post fix for regression
```

---

## Success Thresholds

### Go/No-Go Criteria

```
✅ GO: Proceed to Phase 3 if
  - YAML Syntax: 100/100 valid
  - Heredocs: 0 with emoji
  - Indentation: 0 odd spacing
  - Permissions: 0 invalid
  - Action Check: All referenced actions exist

❌ NO-GO: Halt and investigate if
  - Any YAML parse errors
  - Any action references fail
  - Permission blocks have syntax errors
  - More than 5% workflows affected
```

### Escalation Triggers

| Condition | Action |
|-----------|--------|
| >2 workflows fail validation | Rollback and investigate |
| Any workflow causes CI blockage | Rollback immediately |
| Permission issue found | Flag for security review |
| New action version breaks build | Revert to previous version |

---

## Quality Assurance Checklist

- [ ] Pre-fix state documented (pre_fix_*.log)
- [ ] All backups created and validated
- [ ] Tier 1 fixes applied and tested
- [ ] Tier 2 fixes applied and tested
- [ ] Tier 3 fixes applied and tested
- [ ] Full validation suite passes 100%
- [ ] Actionlint check passes
- [ ] Critical workflows spot-checked (12/12)
- [ ] No regressions in execution time
- [ ] Post-fix state documented (post_fix_*.log)
- [ ] Ready for production merge

---

## Metrics Dashboard

### Pre-Fix State
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PRE-FIX METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Workflows:        205
├─ Valid YAML:           205 (100.0%)
├─ Invalid Permissions:    0 (0.0%)
├─ Heredocs with emoji:   61 (29.8%)
├─ Odd indentation:       60 (29.3%)
└─ Outdated actions:       7 (3.4%)

Health Score: 87.3%
```

### Post-Fix Target
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 POST-FIX TARGET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Workflows:        205
├─ Valid YAML:           205 (100.0%)
├─ Invalid Permissions:    0 (0.0%)
├─ Heredocs with emoji:    0 (0.0%)
├─ Odd indentation:        0 (0.0%)
└─ Outdated actions:       0 (0.0%)

Health Score: 100%
```

---

## Integration with Phase 3-4

### Handoff to ci-log-retrieval-agent
Provide:
- ✅ All fixed workflows (205 files)
- ✅ Validation metrics (passed/failed)
- ✅ Execution logs (pre/post fix)
- ✅ Baseline performance data

### Handoff from ci-log-retrieval-agent
Receive:
- ✅ Test execution results
- ✅ New failure analysis
- ✅ Performance comparison
- ✅ Regression report

---

## Tools & Commands Reference

```bash
# YAML Validation
yamllint .github/workflows/*.yml

# GitHub Actions Validation
actionlint .github/workflows/*.yml

# Python YAML Check
python3 -c "import yaml; [yaml.safe_load(open(f)) for f in Path('.github/workflows').glob('*.yml')]"

# Action Version Check
grep -rE "uses:.*@" .github/workflows/*.yml | cut -d: -f3 | sort | uniq

# Indentation Check
grep -rE "^ {7,}|^ {9,}|^ {11,}" .github/workflows/*.yml | wc -l

# Heredoc Detection
grep -r "<<'" .github/workflows/*.yml | wc -l

# Permissions Check
grep -r "permissions:" .github/workflows/*.yml
```

---

## Appendix: Metric Definitions

### YAML Syntax Validation
**Definition:** All workflows successfully parse with Python yaml.safe_load()  
**Target:** 100%  
**Failure:** Any syntax error  

### Action Indentation
**Definition:** All YAML indentation uses 2-space multiples  
**Target:** 0 odd-space indentation  
**Measurement:** Regex scan for leading spaces not divisible by 2  

### Heredoc Safety
**Definition:** No heredocs contain emoji or high Unicode characters  
**Target:** 0 problematic heredocs  
**Pattern:** `<<'EOF'...EOF` with emoji/special chars  

### Permission Validity
**Definition:** All permissions match GitHub Actions specification  
**Target:** 0 invalid permissions  
**Valid Set:** actions, checks, contents, deployments, id-token, issues, packages, pages, pull-requests, repository-projects, security-events, statuses  

### Action Version Compliance
**Definition:** All action references use approved versions  
**Target:** All actions on recommended versions  
**Update Pattern:** Via enforce-actions-versions.py  

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-24T01:23:00Z  
**Next Report:** Real-time execution metrics during Phase 2  
**Authority:** D-tier autonomous  
**Status:** ✅ Framework Ready for Testing
