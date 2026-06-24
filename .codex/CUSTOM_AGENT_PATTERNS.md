# 🔄 CUSTOM AGENT PATTERNS & INTEGRATION GUIDE

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:51:23.982199  
**Purpose:** Document 15+ integration patterns for agent execution

---

## Overview

This guide documents common patterns for integrating and orchestrating agents within the _codex_ ecosystem.

---

## PATTERN 1: Sequential Execution

### Description
Agent 1 completes → Agent 2 starts (wait for completion).

### Use Cases
- Multi-step workflows with dependencies
- Coordinated diagnostics and remediation
- Build verification (build → test → deploy)

### Implementation
```yaml
workflow:
  steps:
    - agent: autonomous-test-healer-agent
      wait_for: completion
    - agent: test-coverage-monitor
      depends_on: autonomous-test-healer-agent
      wait_for: completion
    - agent: code-scanning-remediation-agent
      depends_on: test-coverage-monitor
```

### Common Agents
- ci-auto-healer-agent → ci-testing-agent → code-scanning-remediation-agent
- autonomous-test-healer-agent → test-coverage-monitor → codeql-alert-resolution-agent

### Performance Impact
- **Runtime:** Sum of all agent runtimes
- **Tokens:** Additive (each agent independent)
- **Best for:** Tight dependencies, sequential reasoning

---

## PATTERN 2: Parallel Execution

### Description
Agents 1-N run simultaneously (limited to 4-lane capacity).

### Use Cases
- Independent analysis tasks
- Multiple security scans (SAST + dependency + secrets)
- Parallel coverage gap-filling

### Implementation
```yaml
workflow:
  parallel_lanes: 4
  tasks:
    - agent: unified-security-scanner
      mode: sast
    - agent: unified-security-scanner
      mode: dependency
    - agent: unified-security-scanner
      mode: secrets
    - agent: codeql-alert-resolution-agent
```

### Common Agents
- Security scanning (4 parallel scans)
- Coverage gap-filling (multiple modules in parallel)
- Documentation validation (multiple paths in parallel)

### Performance Impact
- **Runtime:** Max(individual runtimes) + coordination overhead
- **Tokens:** Additive (all agents run independently)
- **Best for:** Independent tasks, cost optimization

---

## PATTERN 3: Conditional Branching

### Description
IF condition THEN run Agent A ELSE Agent B.

### Use Cases
- Failure detection and routing
- Smart agent selection based on complexity
- Context-aware agent delegation

### Implementation
```yaml
workflow:
  steps:
    - agent: ci-triage-pipeline-agent
    - conditional:
        if: failure_severity == "critical"
        then:
          agent: ci-emergency-response-agent
          timeout: 30m
        else:
          agent: ci-failure-resolution-agent
          timeout: 60m
```

### Common Agents
- ci-triage-pipeline-agent → (critical: ci-emergency-response-agent | normal: ci-failure-resolution-agent)
- test-failure-analyzer-agent → (flaky: fragile-test-guardian | real: autonomous-test-healer-agent)

### Performance Impact
- **Runtime:** Depends on branch taken
- **Tokens:** Only branch taken incurs costs
- **Best for:** Smart routing, cost optimization

---

## PATTERN 4: Error Handling & Fallback

### Description
If primary agent fails, run fallback agent.

### Use Cases
- Graceful degradation
- Alternative approaches when primary fails
- Escalation chain

### Implementation
```yaml
workflow:
  steps:
    - agent: ci-failure-resolution-agent
      on_failure:
        retry: 2
        then: ci-emergency-response-agent
        then: human_review (escalate)
```

### Common Agents
- ci-failure-resolution-agent → (fail) → ci-emergency-response-agent → (fail) → human
- codeql-alert-resolution-agent → (fail) → code-scanning-remediation-agent

### Performance Impact
- **Runtime:** Primary + fallback (if needed)
- **Tokens:** Primary + fallback(s)
- **Best for:** High-confidence workflows, safety nets

---

## PATTERN 5: Result Aggregation

### Description
Collect outputs from multiple agents and synthesize results.

### Use Cases
- Comprehensive reporting (security, coverage, quality)
- Multi-perspective analysis
- Dashboard aggregation

### Implementation
```yaml
workflow:
  parallel_tasks:
    - id: security
      agent: unified-security-scanner
    - id: coverage
      agent: unified-coverage-agent
    - id: quality
      agent: code-analysis-agent
  aggregate:
    template: comprehensive_report
    inputs: [security.output, coverage.output, quality.output]
```

### Common Agents
- Security aggregation (SAST + dependency + secrets)
- Quality aggregation (tests + coverage + mutations)
- Health dashboard (all agents → summary)

### Performance Impact
- **Runtime:** Max(parallel) + aggregation time
- **Tokens:** Sum of all agents
- **Best for:** Comprehensive analysis, reporting

---

## PATTERN 6: State Persistence (PDA Loop)

### Description
Pass data between agents via persistent data store.

### Use Cases
- Cross-session context preservation
- Long-running workflows
- Learning from previous executions

### Implementation
```yaml
workflow:
  steps:
    - agent: ci-pattern-guardian
      store_key: ci_failure_patterns
    - agent: autonomous-test-healer-agent
      retrieve_key: ci_failure_patterns
      use_for: pattern_matching
    - agent: memory-sync-agent
      consolidate: ci_failure_patterns
```

### Common Agents
- ci-pattern-guardian ↔ autonomous-test-healer-agent
- mypy-manager-agent ↔ python-312-type-fixer
- PDA loop: all agents ↔ memory-sync-agent

### Performance Impact
- **Runtime:** +5-10% for state I/O
- **Tokens:** Minimal (state retrieval)
- **Best for:** Long-running workflows, learning systems

---

## PATTERN 7: Rate Limiting

### Description
Throttle concurrent agents to avoid resource exhaustion.

### Use Cases
- API rate limiting prevention
- Resource-constrained environments
- Gradual scaling

### Implementation
```yaml
workflow:
  rate_limit:
    max_concurrent: 4
    backoff_strategy: exponential
  tasks:
    - agent: ci-auto-healer-agent (slot 1)
    - agent: autonomous-test-healer-agent (slot 2)
    - agent: code-scanning-remediation-agent (slot 3)
    - agent: unified-doc-agent (slot 4)
    - agent: workflow-ci-fixer (queued, waits for slot)
```

### Common Agents
- Large parallel operations (>4 agents)
- External API calls
- Resource-intensive tasks

### Performance Impact
- **Runtime:** +queue_wait_time
- **Tokens:** Unchanged
- **Best for:** High concurrency, resource protection

---

## PATTERN 8: Orchestration with Gating

### Description
Multi-agent workflows with gating conditions and checkpoints.

### Use Cases
- Release pipelines
- Deployment verification
- Quality gates

### Implementation
```yaml
workflow:
  checkpoints:
    - name: security_gate
      required: true
      agents: [unified-security-scanner]
      approval: manual
    - name: coverage_gate
      required: true
      agents: [unified-coverage-agent]
      threshold: 80%
    - name: docs_gate
      required: true
      agents: [unified-doc-agent]
  on_all_pass: deploy
```

### Common Agents
- Release pipeline: security → coverage → docs → deploy
- PR gate: analysis → testing → approval
- Deployment: health check → smoke test → canary

### Performance Impact
- **Runtime:** Sequential with gates
- **Tokens:** Only passing gates incur costs
- **Best for:** Critical workflows, compliance

---

## PATTERN 9: Model Selection Based on Complexity

### Description
Route to Haiku (simple) vs Sonnet (complex) based on task complexity.

### Use Cases
- Cost optimization
- Performance optimization
- Dynamic resource allocation

### Implementation
```python
if len(code_changes) < 1000:
    model = "haiku-4.5"  # Simple changes
elif complexity_score < 5:
    model = "haiku-4.5"
else:
    model = "sonnet-4.6"  # Complex analysis

workflow.use_agent(agent_id, model=model)
```

### Common Agents
- Simple checks: policy-coach-agent (Haiku)
- Complex analysis: unified-security-scanner (Sonnet)
- Gap detection: unified-coverage-agent (Haiku) or (Sonnet)

### Performance Impact
- **Runtime:** ~30% faster with Haiku (when appropriate)
- **Tokens:** ~50% cheaper with Haiku
- **Best for:** Cost-conscious operations

---

## PATTERN 10: Cache Reuse

### Description
Share outputs between agent runs to avoid redundant work.

### Use Cases
- Same analysis multiple times
- Intermediate result reuse
- Cost optimization

### Implementation
```yaml
workflow:
  cache:
    key: "security_baseline_{commit_sha}"
    ttl: 24h
  steps:
    - agent: unified-security-scanner
      use_cache: true
    - agent: code-scanning-remediation-agent
      depends_on_cache: security_baseline
```

### Common Agents
- Security baseline caching
- Coverage baseline caching
- Documentation structure caching

### Performance Impact
- **Runtime:** -50-80% on cache hits
- **Tokens:** -90% on cache hits
- **Best for:** Repeated operations, cost optimization

---

## PATTERN 11: Dependency Chaining

### Description
Execute agents in dependency order (topological sort).

### Use Cases
- Complex workflows with multiple dependencies
- Automated task scheduling
- Dependency-aware execution

### Implementation
```yaml
dependencies:
  autonomous-test-healer-agent: []
  test-coverage-monitor: [autonomous-test-healer-agent]
  codeql-alert-resolution-agent: [test-coverage-monitor]
  workflow-ci-fixer: [autonomous-test-healer-agent]

execute:
  - parallel: [autonomous-test-healer-agent, workflow-ci-fixer]
  - then: test-coverage-monitor
  - then: codeql-alert-resolution-agent
```

### Common Agents
- CI/CD healing workflows
- Multi-phase coverage improvement
- Security remediation chains

### Performance Impact
- **Runtime:** Optimal (minimum time while respecting deps)
- **Tokens:** Additive
- **Best for:** Complex DAGs, automatic scheduling

---

## PATTERN 12: Timeout Handling

### Description
Graceful degradation if agent exceeds timeout.

### Use Cases
- Long-running operations
- Resource-constrained environments
- Fast-fail scenarios

### Implementation
```yaml
workflow:
  steps:
    - agent: unified-security-scanner
      timeout: 45m
      on_timeout:
        action: graceful_degradation
        partial_results: true
        fallback: basic_security_check
```

### Common Agents
- Long scans: unified-security-scanner, unified-doc-agent
- Fast-fail: policy validation, basic checks

### Performance Impact
- **Runtime:** Capped by timeout
- **Tokens:** Partial consumption on timeout
- **Best for:** Uncertain durations, safety limits

---

## PATTERN 13: Cost Optimization

### Description
Minimize token usage through smart batching and sequencing.

### Use Cases
- Budget constraints
- Cost-sensitive operations
- Token efficiency

### Implementation
```yaml
optimization:
  strategy: cost_aware
  batch_size: 5
  model_selection: dynamic
  cache_reuse: enabled
  steps:
    - batch: 5 modules
    - agent: unified-coverage-agent
    - model: haiku  # cheaper
    - reuse_cache: yes
```

### Common Agents
- Haiku models: haiku-4.5 for simple tasks
- Batching: multiple modules/files at once
- Caching: reuse previous results

### Performance Impact
- **Runtime:** +5-10% for optimization overhead
- **Tokens:** -30-60% through optimization
- **Best for:** Cost-sensitive environments

---

## PATTERN 14: Monitoring & Observability

### Description
Real-time monitoring of agent execution with metrics.

### Use Cases
- Performance tracking
- SLA compliance
- Debugging

### Implementation
```yaml
monitoring:
  enabled: true
  metrics:
    - agent_runtime
    - tokens_consumed
    - success_rate
    - error_rate
  dashboard: real_time
  alerts:
    - if: runtime > 60m then alert
    - if: error_rate > 10% then alert
```

### Common Agents
- All agents report metrics
- Dashboards: workflow-health-monitor, artifact-monitor-agent
- Alerts: ci-health-alert-agent

### Performance Impact
- **Runtime:** <1% overhead
- **Tokens:** Minimal
- **Best for:** Production workflows, troubleshooting

---

## PATTERN 15: Escalation Chains

### Description
Escalate from automation to human review on failure.

### Use Cases
- Critical decisions
- Manual approval needed
- Audit trails

### Implementation
```yaml
workflow:
  escalation_chain:
    - level_1: autonomous-test-healer-agent (auto-fix)
    - level_2: human_review_queue (if level_1 fails)
    - level_3: team_discussion (if level_2 blocks)
    - level_4: manager_approval (high-risk changes)
```

### Common Agents
- CI fixing: ci-auto-healer-agent → ci-emergency-response-agent → human
- Security: code-scanning-remediation-agent → unified-security-scanner → human
- Deployment: workflow orchestrator → owner-approval-guard → manual

### Performance Impact
- **Runtime:** Depends on escalation level
- **Tokens:** Only executed levels
- **Best for:** Critical workflows, compliance

---

## Integration Pattern Performance Matrix

| Pattern | Runtime | Tokens | Parallel | Best For | <!-- pragma: allowlist secret -->
|---------|---------|--------|----------|----------|
| Sequential | Additive | Additive | No | Dependencies |
| Parallel | Max | Additive | Yes | Independent tasks |
| Conditional | Branch | Branch | No | Smart routing |
| Error Handling | +Fallback | +Fallback | No | Safety nets |
| Aggregation | Max+Agg | Additive | Yes | Reporting |
| State Persist | +5-10% | Minimal | Yes | Long workflows |
| Rate Limiting | +Queue | Unchanged | No | Resource protection |
| Gating | Sequential | Gates | No | Quality gates |
| Model Select | -30% | -50% | N/A | Cost optimization |
| Cache Reuse | -50-80% | -90% | N/A | Repeated ops |
| Dependency Chain | Optimal | Additive | Mixed | Complex DAGs |
| Timeout | Capped | Partial | N/A | Safety limits |
| Cost Opt | +5-10% | -30-60% | N/A | Budget constraints |
| Monitoring | <1% | Minimal | N/A | Production |
| Escalation | Variable | Variable | No | Critical decisions |

---

## Metadata

- **Generated:** 2026-06-20T06:51:23.982208
- **Patterns:** 15+
- **Authority:** @mbaetiong
- **Next Update:** 2026-06-22T12:00Z
