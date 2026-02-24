# Workflow Consolidation Guide

## Overview

This repository has undergone a major workflow consolidation to improve efficiency, reduce duplication, and optimize cache usage. The number of active workflows has been reduced while maintaining all functionality through intelligent job-level conditions and workflow_call integration for AI agents.

## Python 3.12 Migration

**All workflows now use Python 3.12** as the default version. This ensures:
- Consistent behavior across all CI/CD operations
- Access to latest Python features and performance improvements
- Better type checking and error messages
- Improved compatibility with modern dependencies

### Custom Actions Updated
- `.github/actions/setup-python-cached` - Default: 3.12
- `.github/actions/setup-python-uv` - Default: 3.12

## Cache Optimization

All workflows now use the **tiered cache system** for optimal performance:

### Cache Tiers

| Tier | Retention | Use Case | Examples |
|------|-----------|----------|----------|
| **live** | Permanent | Critical workflows run frequently | test-suite, autonomous-agent |
| **common** | 7 iterations | Standard workflows | Most PR checks, security scans |
| **ephemeral** | 1 iteration | Infrequent workflows | Sync jobs, experimental features |

### Benefits
- ✅ **Faster builds**: Cache hits on subsequent runs
- ✅ **Reduced network**: Fewer package downloads
- ✅ **Cost optimization**: Shared cache across workflows
- ✅ **Better organization**: Clear tier strategy

## Consolidated Workflows

### 1. Cache Management Suite (`cache-suite.yml`)

**Replaces:**
- cache-warmup.yml
- cache-management.yml
- cache-cleanup.yml

**Features:**
- Scheduled warmup every 6 hours
- per-iteration cleanup of old ephemeral caches
- per-phase cache analysis and optimization
- Manual trigger with operation selection

**Usage:**
```bash
# Manual trigger
gh workflow run cache-suite.yml -f operation=warmup

# Via AI agent
gh workflow run cache-suite.yml --ref main
```

### 2. Testing Suite (`test-suite.yml`)

**Replaces:**
- test-comprehensive.yml
- test-rag.yml
- auth-tests.yml
- coverage_report.yml (integrated)
- determinism.yml
- integration-gated.yml

**Features:**
- Unified test execution with intelligent job gating
- Selective test scopes (core, rag, auth, integration, determinism)
- Parallel execution with shared cache
- Comprehensive coverage reporting

**Usage:**
```bash
# Run all tests
gh workflow run test-suite.yml -f test-scope=all

# Run specific scope
gh workflow run test-suite.yml -f test-scope=rag

# Via PR (automatic)
# Tests run automatically on all PRs
```

### 3. CI/CD Health Monitoring (Distributed)

**Note:** CI/CD health monitoring uses a distributed pattern rather than a consolidated suite.

**Active Workflows:**
- ci-health-monitor.yml - Core health monitoring
- artifact-monitoring.yml - Artifact tracking
- repository-health-monitoring.yml - Repository health checks
- batch-ci-triage.yml - Batch CI issue triage

**Features:**
- Automated health monitoring every 3 hours
- Artifact expiration tracking
- Runner health diagnostics
- Automated issue creation for failures
- Comprehensive CI/CD metrics

**Usage:**
```bash
# Run CI health monitor
gh workflow run ci-health-monitor.yml

# Check artifact status
gh workflow run artifact-monitoring.yml

# Monitor repository health
gh workflow run repository-health-monitoring.yml
```

## AI Agent Integration

All consolidated workflows support `workflow_call` for seamless AI agent integration:

### Example: Invoking from an AI Agent

```yaml
# In your agent workflow
jobs:
  run-tests:
    uses: ./.github/workflows/test-suite.yml
    with:
      test-scope: core
      python-version: '3.12'
```

### Agent Patterns

1. **Task Delegation**: Agents can invoke specific test scopes
2. **Health Monitoring**: Agents can trigger health checks on-demand
3. **Cache Management**: Agents can request cache operations
4. **Selective Execution**: Fine-grained control via inputs

## Migration Status

### Phase 1: Python 3.12 Migration ✅ COMPLETE
- [x] Updated all custom actions to Python 3.12
- [x] Migrated 20+ workflows to cached actions
- [x] Updated environment variables
- [x] Validated compatibility

### Phase 2: Cache Optimization ✅ COMPLETE
- [x] Implemented tiered cache system
- [x] Assigned appropriate cache tiers
- [x] Created cache management suite
- [x] Documented tier selection guidelines

### Phase 3: Workflow Consolidation ✅ IN PROGRESS
- [x] Cache Management (3 → 1 workflow)
- [x] Testing (7 → 1 workflow)
- [x] CI/CD Health (6 → 1 workflow)
- [ ] Security (17 → 3 workflows) - NEXT
- [ ] Documentation (5 → 2 workflows) - NEXT

### Phase 4: Validation 🔄 ONGOING
- [ ] Test all consolidated workflows
- [ ] Verify cache efficiency metrics
- [ ] Validate AI agent integration
- [ ] Update documentation

## Cache Tier Selection Guidelines

### Use LIVE tier for:
- Critical test suites (test-comprehensive)
- Autonomous agents
- Frequently-run PR checks
- Production deployments

### Use COMMON tier for:
- Standard PR workflows
- Security scans
- Documentation builds
- Most scheduled jobs

### Use EPHEMERAL tier for:
- Sync operations
- Experimental features
- One-off diagnostics
- Temporary workflows

## Performance Metrics

**Before Consolidation:**
- 94 active workflows
- 26 workflows without cache optimization
- Inconsistent Python versions (3.11, 3.12)
- Redundant setup steps

**After Consolidation:**
- 91 active workflows (3 consolidated into suites)
- 71 workflows with optimized caching (up from 51)
- 100% Python 3.12 compliance
- Shared cache infrastructure

**Expected Improvements:**
- 🚀 **30-50% faster** workflow execution (cache hits)
- 💰 **20-30% cost reduction** (fewer compute minutes)
- 🎯 **Better organization** (logical grouping)
- 🤖 **AI agent ready** (workflow_call support)

## Troubleshooting

### Cache Miss Issues
```bash
# Each workflow manages its own cache - no centralized cache suite
# Check specific workflow cache usage in GitHub Actions cache tab
# Caches auto-expire after 7-30 days based on workflow configuration
```

### Workflow Syntax Errors
```bash
# Run CI health monitor
gh workflow run ci-health-monitor.yml

# Run batch CI triage
gh workflow run batch-ci-triage.yml
```

### Test Failures
```bash
# Run specific test scope
gh workflow run test-suite.yml -f test-scope=core -f fail-fast=true
```

## Best Practices

1. **Always use cached actions**: Use `.github/actions/setup-python-cached` instead of direct `actions/setup-python`
2. **Select appropriate cache tier**: Consider workflow frequency and criticality
3. **Use workflow_call**: Enable AI agent integration from the start
4. **Monitor health**: Use ci-health-monitor.yml to track workflow performance
5. **Keep distributed caching**: Each workflow manages its own cache

## Future Enhancements

- [x] Security suite consolidation (security-scanning-suite.yml)
- [x] Cognitive workflow consolidation (Phase 2 phase 1)
- [x] Agent workflow consolidation (Phase 2 phase 1)
- [x] Deployment consolidation (Phase 2 phase 2)
- [ ] Advanced cache analytics
- [ ] Predictive failure detection

## Documentation

- [Custom Actions README](../actions/)
- [Cache Architecture](CACHE_ARCHITECTURE_DIAGRAMS.md)
- [Workflow Analytics](WORKFLOW_ANALYTICS_USAGE.md)
- [Agent Integration Guide](../../docs/agent/OPERATIONAL_GUIDELINES.md)

## Support

For issues or questions:
1. Check [CI Health Monitor](ci-health-monitor.yml) for automated diagnostics
2. Review workflow run logs
3. Create an issue with `ci-health` label
4. Contact @mbaetiong for critical issues

---

**Last Updated**: 2026-01-26
**Version**: 1.0.0
**Status**: ✅ Phase 2 Complete, Phase 3 In Progress
