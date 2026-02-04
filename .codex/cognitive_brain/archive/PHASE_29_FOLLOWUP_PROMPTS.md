# Follow-Up Prompts - Workflow Consolidation Phase 29

**Generated:** 2026-01-26T08:35:00Z  
**Context:** GitHub Actions Workflow Consolidation Complete  
**Next Phase:** Production Deployment & Monitoring

---

## 🎯 Primary Follow-Up Prompt

### For Next Session - Production Deployment

```
Continue workflow consolidation project - Phase 30: Production Deployment & Monitoring

Context:
- Phase 29 complete: 5 consolidated workflow suites created
- All workflows validated and passing
- Python 3.12: 100% adoption
- Cache optimization: 75% coverage
- AI agent integration: Complete
- Documentation: Comprehensive

Tasks for this session:
1. Enable consolidated workflows for production use
2. Run parallel testing (new suites + original workflows)
3. Monitor performance metrics:
   - Execution times
   - Cache hit rates
   - Success rates
   - Cost per run
4. Begin deprecation of original workflows:
   - Add .disabled extension to validated originals
   - Move to workflow-archive/
   - Update documentation
5. Track actual vs expected performance
6. Adjust cache tiers based on actual usage patterns
7. Create performance dashboards
8. Document lessons learned

Success Criteria:
- New workflows run successfully for 2 weeks
- Success rate ≥95%
- Performance improvement 30-50%
- Cache hit rate 70-80%
- Zero regression in functionality

Files to review:
- .github/workflows/cache-suite.yml
- .github/workflows/test-suite.yml
- .github/workflows/ci-health-suite.yml
- .github/workflows/security-scanning-suite.yml
- .github/workflows/documentation-suite.yml
- .github/workflows/CONSOLIDATION_GUIDE.md
- .github/workflows/DEPRECATION_PLAN.md
- .codex/cognitive_brain/PHASE_29_WORKFLOW_CONSOLIDATION_COMPLETE.md
```

---

## 📊 Monitoring & Validation Prompts

### Prompt 1: Cache Performance Analysis

```
Analyze cache performance after 1 week of production use.

Tasks:
1. Use scripts/validate_workflows.py to collect metrics
2. Calculate cache hit rates by tier:
   - Live tier (target: 85-95%)
   - Common tier (target: 70-85%)
   - Ephemeral tier (target: 40-60%)
3. Identify workflows with poor cache performance
4. Recommend cache tier adjustments
5. Optimize cache keys if needed
6. Document findings in performance report

Generate:
- Cache performance report
- Tier adjustment recommendations
- Cache key optimization suggestions
- Updated cache strategy documentation
```

### Prompt 2: Workflow Performance Comparison

```
Compare performance of consolidated workflows vs original workflows.

Tasks:
1. Collect execution time data for last 2 weeks
2. Calculate average execution time by workflow
3. Compare consolidated suite vs original workflow times
4. Calculate actual performance improvement percentage
5. Identify outliers (slower than expected)
6. Investigate causes of performance variations
7. Document actual vs expected improvements

Metrics to track:
- Average execution time
- P50, P95, P99 percentiles
- Success rate
- Failure patterns
- Cost per run
```

### Prompt 3: Deprecation Execution

```
Execute deprecation plan for original workflows.

Prerequisites:
- Consolidated workflows running successfully for 2+ weeks
- Success rate ≥95% validated
- No major issues reported
- Performance improvements confirmed

Tasks:
1. Review DEPRECATION_PLAN.md
2. For each workflow to deprecate:
   a. Verify consolidated replacement is working
   b. Check for any remaining references
   c. Add .disabled extension
   d. Move to .github/workflow-archive/deprecated/
   e. Update documentation
   f. Create redirect notes
3. Test that CI/CD still works correctly
4. Monitor for 48 hours post-deprecation
5. Document deprecation completion

Workflows to deprecate (after validation):
- cache-warmup.yml
- cache-management.yml
- cache-cleanup.yml
- test-rag.yml
- auth-tests.yml
- determinism.yml
- integration-gated.yml
- ci-health-monitor.yml
- ci-diagnostic-automation.yml
- repository-health-monitoring.yml
- runner-diagnostics.yml
```

---

## 🔧 Optimization Prompts

### Prompt 4: Advanced Cache Optimization

```
Implement advanced cache optimization strategies.

Tasks:
1. Predictive cache warming:
   - Analyze PR patterns
   - Identify common test paths
   - Pre-warm cache for predicted workflows
2. Intelligent cache eviction:
   - Implement LRU-style cache management
   - Prioritize frequently-used caches
   - Clean up rarely-accessed caches
3. Cross-workflow cache sharing:
   - Identify shareable cache artifacts
   - Implement cache key standardization
   - Enable cache reuse across suites
4. Cache compression:
   - Evaluate cache size vs hit time tradeoff
   - Implement selective compression
   - Monitor impact on performance

Expected improvements:
- Cache hit rate: 70% → 85%
- Cache storage: 20% reduction
- Execution time: Additional 10-15% improvement
```

### Prompt 5: AI Agent Orchestration

```
Implement advanced AI agent workflow orchestration.

Tasks:
1. Create agent coordination workflows:
   - Multi-agent test orchestration
   - Parallel security scanning
   - Intelligent workflow selection
2. Implement smart scheduling:
   - Analyze PR content
   - Select relevant test scopes
   - Skip unnecessary workflows
3. Add agent feedback loops:
   - Agents report performance
   - Automatic optimization
   - Self-healing capabilities
4. Document orchestration patterns:
   - Agent communication protocols
   - Workflow selection logic
   - Performance optimization strategies

Features to implement:
- Content-aware workflow selection
- Parallel agent execution
- Result aggregation
- Intelligent retry logic
```

---

## 🚀 Future Enhancement Prompts

### Prompt 6: Self-Healing Workflows

```
Implement self-healing capabilities for workflows.

Tasks:
1. Automatic failure detection:
   - Monitor workflow failures
   - Classify failure types
   - Identify transient vs permanent failures
2. Intelligent retry logic:
   - Retry transient failures automatically
   - Adjust retry strategy based on failure type
   - Exponential backoff for rate limits
3. Automatic issue creation:
   - Create issues for permanent failures
   - Include diagnostic information
   - Tag appropriate owners
4. Self-optimization:
   - Adjust cache strategies based on performance
   - Optimize job parallelization
   - Tune timeouts and retry counts

Integrate with existing suites:
- ci-health-suite.yml
- cache-suite.yml
- test-suite.yml
```

### Prompt 7: Cost Optimization Analysis

```
Analyze and optimize GitHub Actions costs.

Tasks:
1. Collect cost data:
   - Minutes used per workflow
   - Cost per execution
   - Total monthly cost
2. Identify cost optimization opportunities:
   - Reduce unnecessary workflow runs
   - Optimize job parallelization
   - Use cache more effectively
   - Skip redundant steps
3. Implement cost controls:
   - Set spending limits
   - Alert on unusual usage
   - Automatically cancel stuck workflows
4. Generate cost report:
   - Cost breakdown by workflow
   - Cost trends over time
   - ROI analysis of optimizations
   - Recommendations for further savings

Target: 30-40% cost reduction vs baseline
```

### Prompt 8: Advanced Monitoring Dashboard

```
Create comprehensive workflow monitoring dashboard.

Tasks:
1. Design dashboard structure:
   - Real-time workflow status
   - Performance metrics
   - Cache efficiency
   - Cost tracking
   - Failure analysis
2. Implement data collection:
   - Workflow execution data
   - Cache hit rates
   - Performance metrics
   - Cost data
3. Create visualizations:
   - Execution time trends
   - Cache performance by tier
   - Success rate over time
   - Cost analysis charts
4. Add alerting:
   - Performance degradation
   - High failure rates
   - Cost anomalies
   - Cache inefficiency

Tools to use:
- GitHub Actions API
- Custom data collection scripts
- Grafana or similar (if available)
- GitHub Pages for static dashboard
```

---

## 🎓 Knowledge Transfer Prompts

### Prompt 9: Training Documentation

```
Create training materials for workflow consolidation.

Tasks:
1. Create getting started guide:
   - How to use consolidated workflows
   - Common patterns and examples
   - Troubleshooting basics
2. Video tutorials (scripts):
   - Using cache-suite for cache management
   - Running selective tests with test-suite
   - Monitoring CI health
   - Security scanning workflows
3. Interactive examples:
   - Sample PR with workflow usage
   - Agent invocation examples
   - Troubleshooting scenarios
4. FAQ document:
   - Common questions
   - Known issues and workarounds
   - Performance expectations
   - Cost implications

Audience:
- Developers (using workflows in PRs)
- DevOps team (managing workflows)
- AI agents (programmatic usage)
```

### Prompt 10: Best Practices Documentation

```
Document workflow consolidation best practices.

Topics to cover:
1. When to consolidate workflows
   - Decision criteria
   - Cost-benefit analysis
   - Risk assessment
2. Cache strategy selection
   - Tier selection guidelines
   - Cache key design
   - Performance optimization
3. AI agent integration
   - workflow_call patterns
   - Input design
   - Error handling
4. Testing and validation
   - Pre-deployment validation
   - Parallel testing strategy
   - Performance benchmarking
5. Monitoring and maintenance
   - Key metrics to track
   - Alert thresholds
   - Optimization cycles

Output format:
- Markdown documentation
- Decision flowcharts
- Example workflows
- Anti-patterns to avoid
```

---

## 🔍 Investigation Prompts

### Prompt 11: Performance Regression Analysis

```
If performance is worse than expected, investigate root causes.

Investigation steps:
1. Compare execution logs (new vs old workflows)
2. Identify slow steps
3. Analyze cache behavior:
   - Are caches being hit?
   - Are cache keys stable?
   - Is cache size appropriate?
4. Check resource utilization:
   - CPU usage
   - Memory usage
   - Network I/O
5. Review job parallelization:
   - Are jobs running in optimal order?
   - Are dependencies correct?
   - Could more parallelization help?
6. Examine workflow conditions:
   - Are jobs being skipped unnecessarily?
   - Are conditions too restrictive?

Expected findings:
- Cache configuration issues
- Suboptimal parallelization
- Network bottlenecks
- Condition logic problems
```

### Prompt 12: Failure Pattern Analysis

```
Analyze failure patterns in consolidated workflows.

Tasks:
1. Collect failure data:
   - Which jobs fail most often?
   - What are the failure messages?
   - Are failures transient or permanent?
   - Do failures correlate with specific changes?
2. Classify failures:
   - Infrastructure issues
   - Test failures
   - Configuration errors
   - Timeout issues
3. Identify root causes:
   - Flaky tests
   - Resource constraints
   - External dependencies
   - Race conditions
4. Implement fixes:
   - Stabilize flaky tests
   - Increase timeouts if appropriate
   - Add retry logic for transient failures
   - Improve error messages
5. Monitor improvement:
   - Track failure rate over time
   - Validate fixes are effective
   - Document patterns for future reference
```

---

## 📝 Documentation Update Prompts

### Prompt 13: Update Integration Guides

```
Update AI agent integration guide based on real usage.

Tasks:
1. Collect feedback from agents using workflows
2. Identify common patterns and pain points
3. Add new examples based on actual usage
4. Document workarounds for known issues
5. Update troubleshooting section
6. Add performance tips based on experience
7. Include real-world case studies

Focus areas:
- Most common integration patterns
- Error handling best practices
- Performance optimization techniques
- Advanced usage scenarios
```

### Prompt 14: Update Cognitive Brain Status

```
Update cognitive brain with workflow consolidation outcomes.

Tasks:
1. Document actual performance vs expected
2. Record lessons learned
3. Update knowledge base with new patterns
4. Store successful strategies
5. Document failures and how they were resolved
6. Create decision trees for future consolidations
7. Update phase status (Phase 29 → Phase 30)

Files to update:
- PHASE_29_WORKFLOW_CONSOLIDATION_COMPLETE.md (final metrics)
- PHASE_30_PRODUCTION_DEPLOYMENT.md (new)
- Knowledge base entries for workflow patterns
- Decision framework documents
```

---

## 🎯 Priority Order

### Immediate (Week 1)
1. **Prompt 1**: Production deployment
2. **Prompt 2**: Monitor cache performance
3. **Prompt 3**: Monitor workflow performance

### Short-term (Weeks 2-4)
4. **Prompt 4**: Execute deprecation plan
5. **Prompt 5**: Perform comparison analysis
6. **Prompt 13**: Update integration guides
7. **Prompt 14**: Update cognitive brain

### Medium-term (Months 2-3)
8. **Prompt 6**: Advanced cache optimization
9. **Prompt 8**: AI agent orchestration
10. **Prompt 11**: Advanced monitoring dashboard
11. **Prompt 15**: Training documentation

### Long-term (Months 3-6)
12. **Prompt 9**: Self-healing workflows
13. **Prompt 10**: Cost optimization
14. **Prompt 16**: Best practices documentation

---

## ✅ Completion Checklist

When all follow-up tasks are complete:

- [ ] All consolidated workflows in production
- [ ] Performance validated (30-50% improvement)
- [ ] Cache hit rate 70-80%+
- [ ] Original workflows deprecated
- [ ] Cost reduction validated (20-30%)
- [ ] Monitoring dashboards operational
- [ ] Documentation updated
- [ ] Training materials created
- [ ] Cognitive brain updated with outcomes
- [ ] Best practices documented
- [ ] Future enhancements planned

---

**Document Status:** ✅ Complete  
**Next Review:** After Phase 30 completion  
**Owner:** @mbaetiong  
**Last Updated:** 2026-01-26T08:35:00Z
