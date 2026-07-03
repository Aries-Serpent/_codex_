# PHASE 9.2: Self-Healing Cascade Implementation Guide

**Version**: 1.0.0  
**Date**: 2026-07-05  
**Authority**: @mbaetiong (D-tier autonomous)  
**Status**: Production Ready

---

## Quick Start

### 1. Verify Installation

```bash
# Check that all Phase 9.2 components are in place
python scripts/ci/phase_9_2_cascade_orchestrator.py --version
python scripts/ci/phase_9_2_pattern_router.py --help

# Verify workflow file
ls -la .github/workflows/phase-9-2-cascade.yml

# Verify configuration
ls -la .codex/phase_9_2_config.yaml
```

### 2. Test Basic Functionality

```bash
# Test pattern routing with sample log
cat > /tmp/test_failure.log << 'EOF'
error: F401 - unused import 'subprocess'
src/module.py:5:1: F401 Unused import
EOF

python scripts/ci/phase_9_2_pattern_router.py \
  --log-file /tmp/test_failure.log \
  --json
```

Expected output:
```json
{
  "status": "route",
  "pattern_id": "RP-001",
  "confidence": 0.85,
  "agent": "ci-auto-healer-agent"
}
```

### 3. Activate Workflow

```bash
# Enable the cascade workflow
gh workflow enable phase-9-2-cascade -R owner/repo

# Or verify it's already enabled
gh workflow list | grep phase-9-2
```

---

## Architecture Overview

```
Phase 8.2 (Triage)
  ↓ Issue classified
Phase 9.2.1 (Detect & Classify)
  ↓ Pattern matched
Phase 9.2.2 (Route & Apply)
  ├─ Pattern 1: Unused Imports → ci-auto-healer-agent
  ├─ Pattern 2: YAML Indentation → workflow-ci-fixer
  ├─ Pattern 3: Coverage → unified-coverage-agent
  ├─ Pattern 4: CodeQL → code-scanning-remediation-agent
  ├─ Pattern 5: Workflow Triggers → workflow-ci-fixer
  ├─ Pattern 6: Test Assertions → autonomous-test-healer-agent
  ├─ Pattern 7: Import Consolidation → ci-auto-healer-agent
  └─ Pattern 8: Links → link-validator-agent
  ↓ Fix applied
Phase 9.2.3 (Verify)
  ├─ Run tests → pytest
  ├─ Lint → ruff
  └─ Verify fix → git diff check
  ↓ Decision made
Phase 9.1 (Decision Log)
  ↓ Logged immutably
Phase 12.3 (Observability)
  ↓ Metrics aggregated
Dashboard
```

---

## The 8 Auto-Fix Patterns

### Pattern 1: Unused Imports (RP-001)

**Detects**: Unused imports flagged by ruff F401

**Example**:
```python
# Before
import unused_module
import sys

print("Hello")

# After
import sys

print("Hello")
```

**Risk**: SAFE (auto-fixes, no review needed)  
**Confidence Threshold**: 65%  
**Success Rate Target**: >95%

---

### Pattern 2: YAML Indentation (RP-002)

**Detects**: YAML syntax errors due to incorrect indentation

**Example**:
```yaml
# Before (error)
jobs:
  build:
  runs-on: ubuntu-latest

# After (fixed)
jobs:
  build:
    runs-on: ubuntu-latest
```

**Risk**: SAFE (structure preserved)  
**Confidence Threshold**: 75%  
**Success Rate Target**: >99%

---

### Pattern 3: Coverage Thresholds (RP-003)

**Detects**: Inconsistent coverage thresholds across config files

**Example**:
```toml
# Before
[tool.coverage.report]
fail_under = 65

# After
[tool.coverage.report]
fail_under = 70
```

**Risk**: REQUIRES_REVIEW (changes policy)  
**Confidence Threshold**: 80%  
**Success Rate Target**: >100% (human approval required)

---

### Pattern 4: CodeQL Remediation (RP-004)

**Detects**: CodeQL findings (F401, F841) reported by GitHub Advanced Security

**Example**:
```python
# Before
unused_var = 42  # F841 warning
import unused_module  # F401 warning

# After
# (unused_var removed, unused_module removed)
```

**Risk**: SAFE (removes identified unused code)  
**Confidence Threshold**: 70%  
**Success Rate Target**: >90%

---

### Pattern 5: Workflow Trigger Migration (RP-005)

**Detects**: Deprecated `true:` syntax for workflow triggers

**Example**:
```yaml
# Before
true:
  push:
    branches: [main]

# After
on:
  push:
    branches: [main]
```

**Risk**: SAFE (syntax modernization only)  
**Confidence Threshold**: 85%  
**Success Rate Target**: >99%

---

### Pattern 6: Test Assertion Fixes (RP-006)

**Detects**: Malformed or vague test assertions

**Example**:
```python
# Before
assert x == y  # No message

# After
assert x == y, f"Expected {x} == {y}"
```

**Risk**: REQUIRES_REVIEW (logic implications)  
**Confidence Threshold**: 75%  
**Success Rate Target**: >80%

---

### Pattern 7: Import Consolidation (RP-007)

**Detects**: Duplicate imports or redundant import statements

**Example**:
```python
# Before
from module import func_a
from module import func_b
from module import func_c

# After
from module import func_a, func_b, func_c
```

**Risk**: SAFE (style improvement only)  
**Confidence Threshold**: 80%  
**Success Rate Target**: >95%

---

### Pattern 8: Documentation Links (RP-008)

**Detects**: Broken links (404 errors) in documentation

**Example**:
```markdown
# Before
[Old Link](https://old-domain.com/docs)

# After
[Old Link](https://new-domain.com/docs)
```

**Risk**: REQUIRES_REVIEW (link correctness critical)  
**Confidence Threshold**: 70%  
**Success Rate Target**: >90%

---

## Configuration

### Enable/Disable Patterns

Edit `.codex/phase_9_2_config.yaml`:

```yaml
cascade:
  autofix:
    patterns:
      RP-001:
        enabled: true
        confidence_threshold: 0.65
      RP-002:
        enabled: true
        confidence_threshold: 0.75
      # ... etc
```

### Adjust Confidence Thresholds

If you see too many false positives for a pattern:

```yaml
# Increase threshold to require higher confidence
confidence_threshold: 0.85  # from 0.70
```

If pattern is not matching real issues:

```yaml
# Decrease threshold to auto-fix more cases
confidence_threshold: 0.50  # from 0.70
```

---

## Usage

### Automatic Activation

Phase 9.2 activates automatically when:

1. **Workflow failure** detected by Phase 8.2 triage
2. **PR comment** with `@copilot heal` or `@copilot fix ci`
3. **Scheduled validation** at 2 AM UTC daily

### Manual Trigger

```bash
# Trigger cascade on specific PR
gh pr comment 123 --body "@copilot heal"

# Or via API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/owner/repo/issues/123/comments \
  -d '{"body":"@copilot heal"}'
```

### Monitor Progress

```bash
# Check workflow status
gh workflow run phase-9-2-cascade.yml --watch

# View recent cascade results
tail -f .codex/phase_9_2_operations.log

# Query Phase 9.1 decision log
python scripts/ci/phase_9_1_decision_logger.py query \
  --since 2026-07-05 \
  --limit 20
```

---

## Troubleshooting

### Issue: High False Positive Rate (>2%)

**Symptoms**: Pattern fixes are making things worse

**Solution**:
```bash
# 1. Review recent failures
grep "false_positive\|FAILED" .codex/phase_9_2_operations.log | tail -20

# 2. Identify problematic pattern
# Example: Too many RP-003 (coverage) escalations

# 3. Increase confidence threshold
# Edit .codex/phase_9_2_config.yaml
# RP-003: confidence_threshold: 0.90  # was 0.80

# 4. Test with dry-run
python scripts/ci/phase_9_2_cascade_orchestrator.py \
  --dry-run \
  --failure-log logs/test_failure.txt

# 5. Monitor improvement
```

### Issue: Cascade Loops (Same Issue Fixed Repeatedly)

**Symptoms**: Same PR keeps triggering cascade, same fix applied over and over

**Solution**:
```bash
# 1. Identify the loop
grep "pr:123.*attempt:[5]" .codex/phase_9_2_operations.log

# 2. Check iteration count
# Phase 9.2 stops after 5 attempts → escalates

# 3. If still looping, disable problematic pattern
sed -i 's/enabled: true  # RP-XXX/enabled: false  # RP-XXX/' \
  .codex/phase_9_2_config.yaml

# 4. Escalate to human review
# Issue will be escalated on next cascade run
```

### Issue: Workflow Fails After Auto-Fix

**Symptoms**: Cascade applies fix, but CI still fails

**Solution**:
```bash
# 1. Check what was changed
git log --oneline -1 | grep "Phase 9.2"
git show --stat

# 2. Review fix in detail
git diff HEAD~1 HEAD

# 3. Check verification output
grep "verification.*failed" .codex/phase_9_2_operations.log

# 4. Rollback fix (if committed)
git revert <commit-sha> -m "Rollback failed Phase 9.2 auto-fix"

# 5. Re-run tests to confirm rollback worked
pytest tests/ -v
```

---

## Metrics & Monitoring

### View Real-Time Metrics

```bash
# Dashboard endpoint
cat .codex/phase_9_2_metrics.json | jq .

# Expected output
{
  "period": "2026-07-05",
  "total_cascades": 42,
  "successful_auto_fixes": 24,
  "auto_fix_rate": 0.571,
  "by_pattern": {
    "RP-001": {"count": 12, "success": 12, "rate": 1.0},
    "RP-002": {"count": 5, "success": 5, "rate": 1.0},
    ...
  }
}
```

### Key Metrics to Track

1. **Auto-Fix Rate**: % of issues auto-fixed (Target: >50%)
2. **False Positive Rate**: % of fixes that broke things (Target: <2%)
3. **Average Latency**: Time from detection to fix (Target: <5 min)
4. **Pattern Coverage**: Which patterns are being matched
5. **Escalation Rate**: % of issues escalated (Target: <20%)

---

## Best Practices

### ✅ Do's

- ✅ Review escalation issues promptly (human review required for high-risk patterns)
- ✅ Monitor metrics daily (first week)
- ✅ Adjust confidence thresholds based on data
- ✅ Document new patterns as they emerge
- ✅ Integrate with Phase 9.3 for complex failures

### ❌ Don'ts

- ❌ Disable all patterns (defeats purpose)
- ❌ Set confidence thresholds to 0 (will cause false positives)
- ❌ Force fixes on requires_review patterns
- ❌ Ignore cascade loops (address root cause)
- ❌ Manually override fixes without testing

---

## Integration Examples

### Integrate with Phase 8.2 Triage

```python
# In Phase 8.2 triage classification
def route_to_cascade(issue: ClassifiedIssue):
    """Send classified issue to Phase 9.2 cascade"""
    
    # Get cascade routing decision
    from phase_9_2_pattern_router import PatternRouter
    
    router = PatternRouter()
    decision = router.route(issue.failure_log)
    
    if decision["status"] == "route":
        # Auto-fix this issue
        dispatch_to_cascade(issue, decision)
    else:
        # Escalate
        escalate_to_human(issue)
```

### Integrate with Phase 9.3 Router

```python
# If Phase 9.2 can't fix, escalate to Phase 9.3
def cascade_to_semantic_router(issue: ClassifiedIssue):
    """Escalate unresolved issue to Phase 9.3"""
    
    from phase_9_3_semantic_router import SemanticRouter
    
    router = SemanticRouter()
    routing = router.route(issue.failure_log)
    
    # Route to appropriate specialist agent
    dispatch_agent_task(routing["agent"], issue)
```

---

## FAQ

### Q: How does Phase 9.2 decide whether to auto-fix?

**A**: Pattern matching + confidence scoring
1. Analyze failure log using regex + ML scoring
2. Calculate confidence (0-100%) for each pattern
3. If confidence ≥ threshold → auto-fix
4. If confidence < threshold → escalate to human

### Q: Can I disable Phase 9.2?

**A**: Yes, temporarily
```bash
gh workflow disable phase-9-2-cascade
```

Permanently: Set `cascade.enabled: false` in config

### Q: What if Phase 9.2 breaks something?

**A**: Automatic rollback on verification failure
- Fix is applied
- Tests run
- If tests fail → revert commit
- Escalate to human review

### Q: How long does a cascade take?

**A**: Typical: 3-5 minutes
- Detection: 10 sec
- Classification: 20 sec
- Fix application: 2-3 min
- Verification: 1-2 min
- Reporting: 10 sec

### Q: Can I customize patterns?

**A**: Yes, patterns are configurable
- Adjust confidence thresholds
- Enable/disable specific patterns
- Add pattern-specific rules (in code)

### Q: What happens if multiple patterns match?

**A**: Highest confidence pattern wins
- Top-5 alternatives returned
- Can override if needed
- Conflict detection prevents overlaps

---

## Support & Questions

For issues or questions about Phase 9.2:

1. Check `.codex/phase_9_2_operations.log` for details
2. Review `.codex/PHASE_9_2_AUTOFIX_PATTERNS.md` for pattern specs
3. Check `.codex/PHASE_9_2_CASCADE_DEPLOYMENT_PLAN.md` for troubleshooting
4. Query Phase 9.1 decision log for historical context
5. Contact @mbaetiong (authority) for approval/escalation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-05 | Initial release: 8 patterns, workflow, monitoring |

