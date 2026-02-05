# Agent Chaining Guide

**Version:** 1.0.0  
**Last Updated:** 2026-02-05T08:40:00Z  
**Purpose:** Enable effective agent-to-agent orchestration and delegation

---

## Overview

Agent chaining allows specialized agents to collaborate by delegating tasks to other agents, creating powerful workflows that leverage each agent's specific expertise.

---

## Chaining Patterns

### 1. Sequential Chain
Execute agents in order, passing results forward.

```yaml
primary_agent: ci-diagnostic-orchestrator
sequence:
  - agent: ci-log-retrieval-agent
    action: fetch_logs
    output: logs
  
  - agent: dependency-conflict-agent
    action: analyze_dependencies
    input: logs
    output: dependency_analysis
  
  - agent: workflow-ci-fixer
    action: apply_fixes
    input: dependency_analysis
    output: fixes_applied
```

**Use When:**
- Each step depends on previous results
- Linear problem-solving flow
- Need to maintain state between steps

**Examples:**
- CI debugging: logs → analysis → fix → verify
- Test development: coverage → gaps → tests → validation

---

### 2. Parallel Fan-Out
Execute multiple agents simultaneously, aggregate results.

```yaml
primary_agent: qa-walkthrough-agent
parallel:
  - agent: test-coverage-monitor
    action: check_coverage
  
  - agent: test-alignment-fixer
    action: verify_alignment
  
  - agent: integration-test-runner
    action: run_tests

aggregate:
  strategy: combine
  on_failure: continue
```

**Use When:**
- Independent validation steps
- Performance optimization needed
- Multiple perspectives required

**Examples:**
- QA validation: coverage + alignment + integration (parallel)
- Security audit: vulnerabilities + code quality + compliance (parallel)

---

### 3. Conditional Routing
Route to different agents based on conditions.

```yaml
primary_agent: artifact-monitor-agent
decision_tree:
  - condition: failure_type == 'test_failure'
    agent: ci-testing-agent
  
  - condition: failure_type == 'dependency_conflict'
    agent: dependency-conflict-agent
  
  - condition: failure_type == 'coverage_drop'
    agent: coverage-roadmap-agent
  
  - default:
    agent: ci-emergency-response-agent
```

**Use When:**
- Multiple failure modes
- Expertise varies by condition
- Need intelligent routing

**Examples:**
- CI monitoring: route by failure type
- Security: route by alert severity
- Performance: route by metric threshold

---

### 4. Hierarchical Delegation
Parent delegates to children, children may delegate further.

```yaml
primary_agent: repository-hygiene-agent
delegates:
  - agent: root-organizer-agent
    delegates:
      - agent: reference-updater-agent
        action: update_references
      - agent: link-validator-agent
        action: validate_links
  
  - agent: documentation-consolidator
    delegates:
      - agent: documentation-quality-agent
        action: assess_quality
      - agent: doc-freshness-checker
        action: check_freshness
```

**Use When:**
- Complex multi-level tasks
- Need organization hierarchy
- Subtasks have subtasks

**Examples:**
- Repository cleanup: hygiene → organize → validate → update
- Documentation: consolidate → quality → freshness → links

---

## Agent Compatibility Matrix

### High Compatibility Pairs

| Primary Agent | Chain To | Reason |
|---------------|----------|--------|
| ci-testing-agent | ci-log-retrieval-agent | Logs needed for diagnosis |
| ci-testing-agent | dependency-conflict-agent | Dependency issues common |
| dependency-conflict-agent | dependency-vulnerability-scanner | Security check after resolution |
| documentation-quality-agent | link-validator-agent | Links are part of quality |
| documentation-quality-agent | doc-freshness-checker | Freshness is quality metric |
| qa-walkthrough-agent | test-coverage-monitor | Coverage is QA metric |
| qa-walkthrough-agent | test-alignment-fixer | Alignment is QA requirement |
| security-alert-verification-agent | code-scanning-remediation-agent | Fix after verification |
| coverage-roadmap-agent | test-coverage-monitor | Monitor progress |
| root-organizer-agent | reference-updater-agent | Updates needed after moves |
| repository-hygiene-agent | documentation-consolidator | Docs are part of hygiene |

---

## Chaining Implementation

### Method 1: Markdown Comments (Simple)

Add to agent markdown file:

```markdown
## Agent Chaining

### Recommended Chains
- **Next Agent:** ci-log-retrieval-agent (for log analysis)
- **Parallel With:** dependency-conflict-agent (simultaneous diagnosis)
- **Delegates To:** workflow-ci-fixer (for applying fixes)

### Activation Example
```
@copilot Use CI Testing Agent to diagnose the failure, 
then chain to CI Log Retrieval Agent for detailed logs,
then apply fixes using Workflow CI Fixer
```
```

### Method 2: YAML Configuration (Advanced)

Add to `agent.yml`:

```yaml
agent:
  name: ci-testing-agent
  version: 1.0.0
  
  chains:
    sequential:
      - agent: ci-log-retrieval-agent
        trigger: on_diagnosis_complete
        pass_data: [failure_type, commit_sha]
      
      - agent: dependency-conflict-agent
        trigger: if_dependency_issue
        pass_data: [requirements_files]
    
    parallel:
      - agent: test-coverage-monitor
      - agent: test-failure-analyzer-agent
    
    delegates:
      - agent: workflow-ci-fixer
        trigger: on_fix_needed
        approval_required: true
```

### Method 3: Programmatic (Framework)

```python
from agent_framework import Agent, Chain

class CITestingAgent(Agent):
    def execute(self, context):
        # Main logic
        result = self.diagnose(context)
        
        # Chain to next agent
        if result.needs_logs:
            logs = self.chain_to('ci-log-retrieval-agent', {
                'run_id': result.run_id
            })
        
        # Parallel execution
        analyses = self.parallel_chain([
            ('dependency-conflict-agent', context),
            ('test-coverage-monitor', context)
        ])
        
        # Conditional delegation
        if result.needs_fix:
            self.delegate_to('workflow-ci-fixer', {
                'fix_type': result.fix_type,
                'approval': True
            })
        
        return result
```

---

## Chaining Best Practices

### 1. Minimize Data Passing
✅ **Good:** Pass only necessary IDs, paths, or references
```yaml
pass_data:
  - run_id: 12345
  - file_path: "tests/test_foo.py"
```

❌ **Bad:** Pass large data structures
```yaml
pass_data:
  - full_logs: [100MB of text]
  - all_files: [entire codebase]
```

### 2. Handle Failures Gracefully
```yaml
chain:
  - agent: dependency-conflict-agent
    on_failure: continue  # Don't block workflow
    fallback: manual_review  # Escalate if needed
```

### 3. Document Chain Intentions
```markdown
## Why This Chain?
This agent chains to `ci-log-retrieval-agent` because:
1. Logs provide diagnostic context
2. Prevents re-running expensive CI jobs
3. Enables deeper failure analysis
```

### 4. Avoid Circular Chains
❌ **Bad:**
```
A → B → C → A  (infinite loop)
```

✅ **Good:**
```
A → B → C → End
```

### 5. Set Timeouts
```yaml
chain:
  - agent: ci-log-retrieval-agent
    timeout: 60s
    on_timeout: fail
```

---

## Common Chain Workflows

### CI Failure Investigation
```
artifact-monitor-agent
  ↓ (detects failure)
ci-testing-agent
  ↓ (diagnoses)
ci-log-retrieval-agent
  ↓ (fetches logs)
dependency-conflict-agent OR test-failure-analyzer-agent
  ↓ (analyzes)
workflow-ci-fixer OR test-alignment-fixer
  ↓ (fixes)
test-coverage-monitor
  ✓ (validates)
```

### Documentation Quality Pipeline
```
documentation-quality-agent
  ├─ doc-freshness-checker (parallel)
  ├─ link-validator-agent (parallel)
  └─ claim-verification-agent (parallel)
  ↓ (aggregate results)
documentation-consolidator
  ↓ (if consolidation needed)
reference-updater-agent
  ✓ (updates references)
```

### Security Alert Response
```
security-alert-verification-agent
  ↓ (verifies alert)
dependency-vulnerability-scanner OR code-scanning-remediation-agent
  ↓ (scans for issues)
security-audit-agent
  ↓ (comprehensive audit)
codeql-alert-resolution-agent
  ↓ (fixes issues)
owner-approval-guard
  ✓ (approval checkpoint)
```

### Test Coverage Improvement
```
test-coverage-monitor
  ↓ (identifies gaps)
coverage-roadmap-agent
  ↓ (plans strategy)
  ├─ coverage-gapfill-agent (fills gaps)
  ├─ test-enhancement-agent (improves existing)
  └─ tokenization-coverage-agent (specialized)
  ↓ (implementation)
test-coverage-monitor
  ✓ (validates improvement)
```

### Repository Cleanup
```
repository-hygiene-agent
  ├─ root-organizer-agent
  │   ├─ reference-updater-agent
  │   └─ link-validator-agent
  ├─ documentation-consolidator
  │   ├─ documentation-quality-agent
  │   └─ doc-freshness-checker
  └─ code-analysis-agent
  ✓ (validation)
```

---

## Agent Orchestration Metadata

Each agent should declare its orchestration capabilities:

```yaml
# In agent.yml
orchestration:
  can_chain: true
  can_be_chained: true
  can_delegate: true
  can_accept_delegation: true
  
  recommended_chains:
    - agent: ci-log-retrieval-agent
      when: needs_logs
      priority: high
    
    - agent: dependency-conflict-agent
      when: dependency_failure
      priority: high
  
  chain_protocols:
    - sequential
    - parallel
    - conditional
  
  data_requirements:
    input: [run_id, failure_type]
    output: [diagnosis, recommendations, fixes]
```

---

## Testing Chain Workflows

### 1. Unit Test Individual Agents
```python
def test_agent_standalone():
    agent = CITestingAgent()
    result = agent.execute(mock_context)
    assert result.success
```

### 2. Integration Test Chains
```python
def test_ci_diagnostic_chain():
    chain = Chain([
        CITestingAgent(),
        CILogRetrievalAgent(),
        WorkflowCIFixerAgent()
    ])
    result = chain.execute(test_context)
    assert result.all_agents_succeeded
```

### 3. Validate Chain Contracts
```python
def test_data_passing():
    # Ensure agent A output matches agent B input
    agent_a_output = ci_testing_agent.output_schema
    agent_b_input = ci_log_retrieval_agent.input_schema
    assert agent_a_output.compatible_with(agent_b_input)
```

---

## Migration Guide

### Adding Chaining to Existing Agents

1. **Identify Natural Chains**
   - What agents work well together?
   - What tasks naturally follow this one?

2. **Document in Markdown**
   ```markdown
   ## Agent Chaining
   This agent chains to:
   - `next-agent`: description
   ```

3. **Add YAML Config (Optional)**
   ```yaml
   chains:
     - agent: next-agent
       trigger: on_complete
   ```

4. **Update Agent Registry**
   ```yaml
   agents:
     - id: my-agent
       has_chaining: true
       chains_to: [agent1, agent2]
   ```

5. **Test End-to-End**
   - Verify chain works
   - Check data passing
   - Validate error handling

---

## Future Enhancements

### Planned Features
1. **Auto-discovery:** Agents auto-discover compatible chains
2. **Learning:** System learns optimal chains from usage
3. **Metrics:** Track chain success rates
4. **Visualization:** Graph of agent relationships
5. **Versioning:** Chain compatibility across versions

---

## Support

**Questions about chaining?**
- See: `.codex/CUSTOM_AGENT_CONSOLIDATION_REPORT.md`
- Contact: @mbaetiong
- Docs: `/home/runner/work/_codex_/_codex_/.github/agents/README.md`

---

**Document Status:** ✅ COMPLETE  
**Version:** 1.0.0  
**Next Review:** After implementing orchestration framework
