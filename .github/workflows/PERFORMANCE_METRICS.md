# Workflow Performance Metrics & Monitoring

This document tracks performance metrics for consolidated GitHub Actions workflows and provides guidelines for monitoring and optimization.

## 📊 Performance Targets

Based on Phase 29 consolidation, these are our target metrics for the 2 phase validation period:

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Success Rate | ≥95% | Workflow conclusion status |
| Performance Improvement | 30-50% | Execution time vs baseline |
| Cache Hit Rate | 70-80% | Cache action reports |
| Cost Reduction | 20-30% | GitHub Actions usage API |

## 🎯 Success Criteria

### Must Have (Week 1-2)
- ✅ All consolidated workflows run successfully
- ✅ Zero critical failures
- ✅ No regression in test coverage
- ✅ Documentation updated and accurate

### Should Have (Week 2-4)
- ✅ Performance improvements validated
- ✅ Cache efficiency meets targets
- ✅ Cost reduction confirmed
- ✅ Original workflows deprecated

## 📈 Monitoring Dashboard

### per-iteration Metrics

Track these metrics per-iteration during the validation period:

1. **Workflow Execution Count**
   - Total runs per workflow
   - Success vs failure ratio
   - Average execution time

2. **Cache Performance**
   - Cache hit rate by tier (Live, Common, Ephemeral)
   - Cache size and storage usage
   - Cache restoration times

3. **Cost Tracking**
   - Compute minutes consumed
   - Cost per workflow run
   - Comparison to baseline

### per-phase Analysis

Perform per-phase analysis to identify trends:

1. **Performance Trends**
   - Execution time trends (improving/degrading)
   - Success rate trends
   - Failure pattern analysis

2. **Cache Optimization**
   - Identify workflows with poor cache performance
   - Recommend tier adjustments
   - Optimize cache keys

3. **Cost Optimization**
   - Identify expensive workflows
   - Recommend optimization opportunities
   - Calculate ROI of consolidation

## 🔧 Monitoring Tools

### 1. Performance Monitoring Script

Located at: `scripts/monitor_workflow_performance.py`

```bash
# Run basic monitoring
python scripts/monitor_workflow_performance.py --days 14 --format markdown

# Compare consolidated vs original
python scripts/monitor_workflow_performance.py --days 14 --compare --format markdown

# Generate JSON report for automation
python scripts/monitor_workflow_performance.py --days 7 --format json --output .codex/reports/performance.json
```

### 2. GitHub Actions API

Query workflow runs directly:

```bash
# Get recent workflow runs
gh api repos/Aries-Serpent/_codex_/actions/runs \
  --jq '.workflow_runs[] | {name: .name, status: .status, conclusion: .conclusion, created_at: .created_at}'

# Get workflow timing
gh api repos/Aries-Serpent/_codex_/actions/runs \
  --jq '.workflow_runs[] | {name: .name, duration: (.updated_at | fromdateiso8601) - (.created_at | fromdateiso8601)}'
```

### 3. CI Health Suite

Use the consolidated CI Health Suite for automated monitoring:

```bash
# Run full health check
gh workflow run ci-health-suite.yml -f operation=all

# Monitor specific aspect
gh workflow run ci-health-suite.yml -f operation=health-monitor
```

## 📊 Baseline Metrics (Pre-Consolidation)

### Original Workflows Performance

| Workflow Category | Avg Time | Success Rate | Runs/Day |
|-------------------|----------|--------------|----------|
| Testing (6 workflows) | 8-12 min | 92% | 40 |
| Cache (3 workflows) | 3-5 min | 95% | 24 |
| CI Health (5 workflows) | 5-8 min | 94% | 16 |
| Security (4+ workflows) | 10-15 min | 90% | 20 |
| Documentation (4 workflows) | 4-6 min | 96% | 12 |

### Cache Performance (Pre-Consolidation)

| Tier | Hit Rate | Workflows |
|------|----------|-----------|
| Live | 60-70% | 10 |
| Common | 50-65% | 50 |
| Ephemeral | 30-40% | 11 |
| **No Cache** | N/A | 23 |

## 🎯 Expected Improvements

### Consolidated Workflows Performance

| Suite | Expected Time | Expected Success | Expected Runs/Day |
|-------|--------------|------------------|-------------------|
| test-suite.yml | 5-8 min | ≥95% | 40 |
| cache-suite.yml | 2-3 min | ≥97% | 8 |
| ci-health-suite.yml | 3-5 min | ≥96% | 8 |
| security-scanning-suite.yml | 7-10 min | ≥93% | 20 |
| documentation-suite.yml | 3-4 min | ≥97% | 12 |

### Expected Cache Improvements

| Tier | Target Hit Rate | Improvement |
|------|----------------|-------------|
| Live | 85-95% | +20-25% |
| Common | 70-85% | +15-20% |
| Ephemeral | 40-60% | +10-20% |

## 📉 Known Issues & Mitigation

### Common Performance Issues

1. **Cache Misses**
   - **Symptom:** Lower than expected hit rates
   - **Cause:** Unstable cache keys, dependency updates
   - **Mitigation:** Review cache key generation, use lock files

2. **Slow Job Startup**
   - **Symptom:** Long time before first step
   - **Cause:** Runner queue delays
   - **Mitigation:** Use workflow concurrency, optimize trigger conditions

3. **Test Timeouts**
   - **Symptom:** Workflows timing out during tests
   - **Cause:** Resource constraints, flaky tests
   - **Mitigation:** Increase timeouts, fix flaky tests, use parallelization

### Failure Patterns

Track these common failure patterns:

1. **Transient Infrastructure Failures**
   - Network issues
   - Runner availability
   - GitHub API rate limits
   - **Action:** Implement automatic retry

2. **Test Failures**
   - Flaky tests
   - Environment-specific issues
   - Race conditions
   - **Action:** Fix root cause, improve test isolation

3. **Configuration Errors**
   - Invalid YAML syntax
   - Missing secrets
   - Permission issues
   - **Action:** Validate before merge, use linters

## 🔔 Alert Thresholds

Configure alerts for these conditions:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Success Rate Drop | <90% for 24h | Investigate immediately |
| Execution Time Spike | >2x baseline | Check for regressions |
| Cache Hit Rate Drop | <50% for live tier | Review cache configuration |
| Cost Spike | >150% of baseline | Analyze expensive workflows |
| Critical Workflow Failure | Any failure | Immediate notification |

## 📝 per-phase Report Template

Use this template for per-phase performance reports:

```markdown
# Workflow Performance Report - Week [N]

**Date Range:** [Start] to [End]  
**Report Generated:** [Date]

## Summary

- Total Workflow Runs: [N]
- Average Success Rate: [N]%
- Average Execution Time: [N] min
- Cache Hit Rate: [N]%
- Estimated Cost: $[N]

## Consolidated Workflow Performance

| Suite | Runs | Success | Avg Time | vs Baseline |
|-------|------|---------|----------|-------------|
| test-suite.yml | [N] | [N]% | [N]m | [+/-N]% |
| cache-suite.yml | [N] | [N]% | [N]m | [+/-N]% |
| ci-health-suite.yml | [N] | [N]% | [N]m | [+/-N]% |
| security-scanning-suite.yml | [N] | [N]% | [N]m | [+/-N]% |
| documentation-suite.yml | [N] | [N]% | [N]m | [+/-N]% |

## Key Observations

### Successes
- [List successful improvements]

### Issues
- [List any issues encountered]

### Recommendations
- [List recommended actions]

## Next Week Actions

1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
```

## 🔍 Investigation Procedures

### When Success Rate Drops

1. Check workflow run logs for error patterns
2. Identify common failure causes
3. Check if failures are transient or permanent
4. Review recent changes that may have caused issues
5. Implement fixes and monitor improvement

### When Performance Degrades

1. Compare execution times to baseline
2. Identify slow jobs/steps
3. Check cache hit rates
4. Review resource utilization
5. Optimize slow steps or add parallelization

### When Cache Efficiency Drops

1. Check cache key stability
2. Review dependency changes
3. Verify cache tier assignments
4. Check cache size and eviction
5. Optimize cache keys if needed

## 📊 Data Collection

### Automated Collection

Set up these automated data collection mechanisms:

1. **per-iteration Performance Snapshot**
   ```bash
   # Cron: Daily at 2 AM UTC
   python scripts/monitor_workflow_performance.py --days 1 --format json
   ```

2. **per-phase Comparison Report**
   ```bash
   # Cron: Sunday at 3 AM UTC
   python scripts/monitor_workflow_performance.py --days 7 --compare --format markdown
   ```

3. **Monthly Cost Analysis**
   ```bash
   # Cron: 1st of month at 4 AM UTC
   python scripts/analyze_workflow_costs.py --days 30 --format html
   ```

### Manual Collection

For ad-hoc analysis:

1. **Performance Deep Dive**
   ```bash
   gh run list --workflow=[workflow-name] --limit 100 --json status,conclusion,createdAt,updatedAt
   ```

2. **Cache Analysis**
   ```bash
   gh api repos/Aries-Serpent/_codex_/actions/caches
   ```

3. **Cost Breakdown**
   ```bash
   gh api repos/Aries-Serpent/_codex_/actions/workflows/[workflow-id]/timing
   ```

## 🎓 Best Practices

### For Optimal Performance

1. **Cache Effectively**
   - Use appropriate cache tiers
   - Stable cache keys
   - Reasonable cache sizes

2. **Parallelize Wisely**
   - Independent jobs in parallel
   - Use matrix strategies
   - Avoid over-parallelization

3. **Optimize Conditions**
   - Skip unnecessary jobs
   - Use path filters
   - Implement smart triggers

4. **Monitor Continuously**
   - Track key metrics per-iteration
   - Set up alerts
   - Regular reviews

### For Reliable Workflows

1. **Handle Failures Gracefully**
   - Use `continue-on-error` appropriately
   - Implement retry logic
   - Clear error messages

2. **Maintain Stability**
   - Pin action versions
   - Lock dependencies
   - Test changes thoroughly

3. **Document Changes**
   - Update documentation
   - Communicate changes
   - Track deprecations

## 📞 Support & Escalation

### Normal Issues
- Create issue with `workflow-performance` label
- Include performance report and logs
- Tag @mbaetiong for review

### Critical Issues
- Contact @mbaetiong directly
- Include immediate impact assessment
- Provide recent performance data

### Performance Reviews
- per-phase review meetings
- Monthly optimization sessions
- Quarterly strategy planning

---

**Last Updated:** 2026-01-26  
**Phase:** 30 - Production Deployment & Monitoring  
**Status:** Active Monitoring  
**Next Review:** 2026-02-09
