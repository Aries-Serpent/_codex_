# Workflow Consolidation Recommendations

## Current State

The repository contains **60+ GitHub Actions workflows**, creating complexity and maintenance burden.

**Key Metrics**:
- Total workflows: 60+
- Average workflow length: ~150 lines
- Estimated monthly CI minutes: High
- Complexity score: High

## Issues with Current State

1. **Maintenance Burden**: Each workflow requires individual updates for dependency changes, action version updates, etc.

2. **Duplication**: Similar patterns repeated across workflows (checkout, setup Python, install deps, etc.)

3. **Discovery Difficulty**: New contributors struggle to understand which workflow does what

4. **Execution Costs**: Multiple workflows running similar tasks waste CI resources

5. **Interdependency Complexity**: Workflows triggering other workflows create hard-to-debug chains

## Consolidation Strategy

### Phase 1: Quick Wins (Immediate)

Merge workflows with significant overlap:

#### 1.1 Test Workflows → Unified Test Suite

**Current**:
- `ci.yml`
- `ci-pytest.yml`
- `tests.yml`
- `ml-tests.yml`
- `comprehensive_tests.yml`
- `multi-python-ci.yml`

**Proposed**: Single `test-suite.yml` with matrix strategy

```yaml
name: Test Suite

on:
  pull_request:
  push:
    branches: [main, 0D_base_]

jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        test-type: [unit, smoke, ml, comprehensive]
        exclude:
          - python-version: '3.10'
            test-type: comprehensive
    runs-on: ubuntu-latest
    steps:
      # ... consolidated steps
```

**Benefits**: 
- Reduce from 6 workflows to 1
- Clearer test organization
- Easier to add new Python versions

#### 1.2 Security Workflows → Unified Security Suite

**Current**:
- `security.yml`
- `security-scanning.yml`
- `security_gates.yml`
- `security_policy_gate.yml`
- `secrets_baseline_check.yml`
- `semgrep_sarif.yml`

**Proposed**: Single `security-suite.yml` with parallel jobs

```yaml
name: Security Suite

jobs:
  dependency-scan:
    # ...
  secret-scan:
    # ...
  code-scan:
    # ...
  policy-check:
    # ...
  summary:
    needs: [dependency-scan, secret-scan, code-scan, policy-check]
    # ...
```

**Benefits**:
- Reduce from 6 workflows to 1
- Single security status check
- Easier to add new security tools

#### 1.3 Audit Workflows → Unified Audit Pipeline

**Current**:
- `audit_chain.yml`
- `capability-audit.yml`
- `nightly-audit.yml`
- `space-audit.yml`
- `audit-improvement-pipeline.yml`

**Proposed**: Keep `audit-improvement-pipeline.yml`, remove others

**Benefits**:
- Reduce from 5 workflows to 1
- Single source of truth for audits
- Scheduled and manual triggers in one place

### Recommended Consolidations

### Priority 1 (Do First)

| Current Workflows | New Workflow | Reduction |
|------------------|--------------|-----------|
| 6 test workflows | `test-suite.yml` | 6→1 |
| 6 security workflows | `security-suite.yml` | 6→1 |
| 5 audit workflows | `audit-pipeline.yml` | 5→1 |

**Total**: 17 → 3 workflows (-14 workflows, 82% reduction)

### Priority 2 (Do Next)

| Current Workflows | New Workflow | Reduction |
|------------------|--------------|-----------|
| 5 doc workflows | `doc-pipeline.yml` | 5→1 |
| 4 validation workflows | `validation-suite.yml` | 4→1 |
| Various status/check workflows | `status-checks.yml` | ~5→1 |

**Total**: 14 → 3 workflows (-11 workflows)

## Success Metrics

**Target Reductions**:
- Workflows: 60 → ~25 (58% reduction)
- Lines of YAML: ~9,000 → ~3,500 (61% reduction)
- Duplicate code: 70% → 20%

**Improved Metrics**:
- CI minutes/month: -40% expected
- Workflow update time: -60% expected
- Onboarding time: -50% expected

## Implementation Plan

### Week 1: Test Suite Consolidation

1. Create new `test-suite.yml`
2. Test on feature branch
3. Disable old workflows (rename .yml → .yml.disabled)
4. Monitor for 1 week
5. Delete old workflows

### Week 2: Security Suite Consolidation

1. Create new `security-suite.yml`
2. Test on feature branch
3. Disable old workflows
4. Monitor for 1 week
5. Delete old workflows

## Next Steps

1. **Review this proposal** with team
2. **Get approval** for consolidation approach
3. **Create tracking issue** with checklist
4. **Implement Phase 1** (Priority 1 consolidations)
5. **Monitor and adjust** based on feedback

## Related Documents

- GAP_ANALYSIS.md - Overall gap analysis
- .github/workflows/ - Current workflows
