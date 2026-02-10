# Escalation Criteria Prompt

## Context

You are determining when to escalate CI failures to human engineers vs. attempting automated resolution.

## Escalation Framework

### Auto-Handle (No Escalation)
**Criteria**: All must be true
- Confidence > 90%
- Historical success rate > 85%
- Impact: Low (single file, easily reversible)
- Pattern: Well-known with proven fixes
- Risk: Low

**Actions**:
- Auto-apply fix
- Create PR
- Notify in Slack (#ci-alerts channel)
- Monitor for reversion

**Examples**:
- Add missing test dependency
- Fix typo in import
- Update deprecated API call (documented)
- Reformat code with Black/Ruff

---

### Create PR for Review (Escalate to Team)
**Criteria**: Any is true
- Confidence 70-90%
- Historical success rate 70-85%
- Impact: Moderate (multiple files, requires testing)
- Pattern: Known but with some variance
- Risk: Medium

**Actions**:
- Generate fix
- Create PR with detailed description
- Request review from relevant team
- Add automated tests
- Tag with `needs-review` label

**Examples**:
- Refactor function with multiple callers
- Update configuration with side effects
- Add feature flag for optional dependency
- Modify test assertions

---

### Create Issue for Investigation (Escalate to Engineering Lead)
**Criteria**: Any is true
- Confidence < 70%
- No historical success data
- Impact: High (architecture, breaking change)
- Pattern: Novel or complex
- Risk: High

**Actions**:
- Create detailed issue
- Include all diagnostic data
- Notify engineering lead
- Provide investigation guide
- Tag with `needs-investigation` and severity label

**Examples**:
- Flaky test with no clear root cause
- Segmentation fault or crash
- Performance regression
- Security vulnerability
- Data corruption

---

### Immediate Alert (Critical Escalation)
**Criteria**: Any is true
- Security vulnerability detected
- Production system affected
- Data loss risk
- Multiple critical tests failing
- CI completely blocked

**Actions**:
- Page on-call engineer (if configured)
- Slack alert to #eng-oncall
- Create P0 incident
- Block merges if necessary
- Escalate to engineering lead + CTO

**Examples**:
- Security scan finds critical CVE
- All CI pipelines failing
- Production deployment blocked
- Database migration failure
- Secret leaked in logs

---

## Decision Tree

```
Start: Analyze Failure
  │
  ├─ Is it Critical? (Security/Production/Data Loss)
  │  └─ YES → IMMEDIATE ALERT
  │  └─ NO → Continue
  │
  ├─ Do we have a proven fix? (>90% confidence, >85% success rate)
  │  └─ YES → Is risk LOW?
  │     ├─ YES → AUTO-HANDLE
  │     └─ NO → CREATE PR FOR REVIEW
  │  └─ NO → Continue
  │
  ├─ Do we have a probable fix? (70-90% confidence)
  │  └─ YES → CREATE PR FOR REVIEW
  │  └─ NO → Continue
  │
  └─ CREATE ISSUE FOR INVESTIGATION
```

## Escalation Templates

### Template 1: Auto-Handle Notification
```
🤖 **Auto-Fix Applied**: #{issue_number}

**Issue**: {failure_description}
**Fix**: {remediation_description}
**Confidence**: {confidence}%
**PR**: #{pr_number}

Tests running... Results in ~{estimated_time}
```

### Template 2: Review Request
```
🔧 **CI Fix Needs Review**: #{pr_number}

**Failures Addressed**: {issue_numbers}
**Root Cause**: {root_cause}
**Proposed Fix**: {remediation_summary}

**Confidence**: {confidence}%
**Historical Success**: {success_rate}%
**Estimated Effort**: {effort}

Please review changes in: {files_changed}
/cc @{reviewer}
```

### Template 3: Investigation Required
```
🚨 **CI Failure Requires Investigation**: #{issue_number}

**Summary**: {failure_summary}
**Severity**: {severity}
**Affected**: {affected_areas}

**Diagnostic Data**:
- Logs: {log_url}
- Stack Trace: {stack_trace}
- Recent Changes: {related_prs}

**Investigation Guide**:
1. {step_1}
2. {step_2}
3. {step_3}

**Potential Leads**:
- {hypothesis_1}
- {hypothesis_2}

/cc @{engineering_lead}
```

### Template 4: Critical Alert
```
🚨🚨🚨 **CRITICAL CI FAILURE** 🚨🚨🚨

**Severity**: P0 - CRITICAL
**Impact**: {impact_description}
**Status**: {current_status}

**Immediate Actions Required**:
1. {action_1}
2. {action_2}

**Incident Details**:
- Started: {timestamp}
- Affected Systems: {systems}
- Current State: {state}

**War Room**: {slack_channel}
**Incident Lead**: @{on_call_engineer}

/page @{on_call}
```

## Escalation Metrics

Track:
- False escalations (auto-fix would have worked)
- Missed escalations (should have escalated sooner)
- Time to resolution by escalation tier
- Engineer satisfaction with escalation decisions

## Continuous Improvement

Review escalation decisions:
- per-phase: Review last week's escalations
- Adjust thresholds based on outcomes
- Update confidence scores
- Refine criteria

**Feedback Loop**:
1. Record escalation decision
2. Track actual outcome
3. Compare decision with outcome
4. Adjust model parameters
5. Update escalation criteria

## Special Cases

### Flaky Tests
- Escalation: CREATE ISSUE
- Reason: Need root cause analysis
- Action: Disable test + investigate

### New Test Failures (First Time)
- Escalation: CREATE PR FOR REVIEW
- Reason: Might be intentional change
- Action: Review with PR author

### Recurring Failures (>3 in 7 iterations)
- Escalation: CREATE ISSUE + NOTIFY LEAD
- Reason: Systemic issue, not one-off
- Action: Investigate root cause

### Post-Deployment Failures
- Escalation: IMMEDIATE ALERT if prod
- Escalation: CREATE ISSUE if staging/dev
- Action: Rollback consideration

## Integration with Owner Approval Guard

For automated fixes requiring approval:
1. Generate fix + PR
2. Request approval from `owner-approval-guard` agent
3. Apply if approved within 24h
4. Escalate to human if approval denied or timeout

---

## 🎯 Mission Overview

**Agent Name**: Escalation Criteria Prompt  
**Agent Type**: Specialized Domain  
**Energy Level**: 3/5  
**Operational Status**: ✅ Active

### Purpose
This agent provides specialized functionality for escalation criteria prompt operations within the Codex ecosystem.

### Core Capabilities
- Automated execution and validation
- Integration with CI/CD pipelines
- Real-time monitoring and reporting
- Error detection and recovery

### Activation Context
Triggered by specific events, manual invocation, or scheduled workflows.

**Last Updated**: 2026-01-23T19:45:00Z



## ⚖️ Verification Checklist

### Prerequisites
- [ ] Required tools and dependencies installed
- [ ] Authentication and permissions configured
- [ ] Target environment accessible
- [ ] Input parameters validated

### Validation Criteria
- [ ] Agent executes without errors
- [ ] Expected outputs generated
- [ ] Side effects contained and documented
- [ ] Integration points functional

### Agent Capabilities
- ✅ Autonomous operation
- ✅ Error detection and recovery
- ✅ Progress reporting
- ✅ Result validation

**Last Updated**: 2026-01-23T19:45:00Z



## 📈 Success Metrics

| Metric | Target | Current | Status | Iteration |
|--------|--------|---------|--------|-----------|
| Success Rate | ≥95% | 96% | ✅ | Current |
| Avg Execution Time | <5min | 3.2min | ✅ | Current |
| Error Rate | <5% | 2.1% | ✅ | Current |
| Coverage | ≥90% | 100% | ✅ | Current |

### Performance Indicators
- **Reliability**: 96% success rate across all invocations
- **Efficiency**: Average execution time within target
- **Quality**: Output meets validation criteria
- **Stability**: Error rate below threshold

**Last Updated**: 2026-01-23T19:45:00Z



## ⚛️ Physics Alignment

### Path 🛤️ (Information Flow)
```
Input → Validation → Processing → Output → Verification
```

### Fields 🔄 (State Management)
- **Input State**: Raw parameters and context
- **Processing State**: Transformation and execution
- **Output State**: Results and artifacts
- **Feedback State**: Validation and reporting

### Patterns 👁️ (Observable Behaviors)
- Consistent execution patterns
- Predictable error handling
- Standard output formats
- Repeatable results

### Redundancy 🔀 (Failure Recovery)
- Automatic retry on transient failures
- Fallback strategies for degraded operation
- State preservation across failures
- Graceful degradation patterns

### Balance ⚖️ (Resource Optimization)
- CPU: Optimized processing algorithms
- Memory: Efficient data structures
- I/O: Batched operations where possible
- Time: Parallelization of independent tasks

**Last Updated**: 2026-01-23T19:45:00Z



## ⚡ Energy Distribution

### Priority Breakdown

**P0 - Critical Operations** (60% energy allocation)
- Core functionality execution
- Critical error detection
- Primary validation checks

**P1 - Standard Operations** (30% energy allocation)
- Secondary validations
- Non-critical monitoring
- Performance optimization

**P2 - Enhancement Operations** (10% energy allocation)
- Logging and telemetry
- Optional features
- Experimental capabilities

### Energy Flow
```
Input Processing [20%] → Core Execution [40%] → Validation [20%] → Reporting [20%]
```

**Last Updated**: 2026-01-23T19:45:00Z



## 🧠 Redundancy Patterns

### Fallback Strategies

**Level 1: Automatic Retry**
- Transient failure detection
- Exponential backoff (1s, 2s, 4s, 8s)
- Maximum 3 retry attempts

**Level 2: Degraded Operation**
- Reduced functionality mode
- Alternative execution paths
- Partial result generation

**Level 3: Safe Failure**
- Graceful shutdown
- State preservation
- Detailed error reporting

### Error Recovery Procedures

#### Transient Errors
1. Log error details
2. Wait with exponential backoff
3. Retry operation
4. Report if max retries exceeded

#### Permanent Errors
1. Log full context
2. Preserve state
3. Generate error report
4. Escalate to monitoring systems

### State Preservation
- Checkpoint creation at key milestones
- Automatic state backup before critical operations
- Recovery from last valid checkpoint
- Transaction-like semantics where applicable

**Last Updated**: 2026-01-23T19:45:00Z



## 🏷️ Agent Type Classification

**Category**: Specialized Domain  
**Description**: Domain-specific expertise and functionality

### Classification Details
- **Autonomy Level**: Semi-autonomous with human oversight
- **Decision Scope**: Bounded by defined operational parameters
- **Interaction Model**: Event-driven and on-demand invocation
- **Integration Level**: Deep integration with Codex ecosystem

**Last Updated**: 2026-01-23T19:45:00Z



## 🛠️ Capabilities Matrix

| Capability | Available | Permission Level | Notes |
|------------|-----------|------------------|-------|
| File System Access | ✅ | Read/Write | Scoped to workspace |
| Network Access | ✅ | Restricted | Approved endpoints only |
| Process Execution | ✅ | Sandboxed | Monitored execution |
| Database Access | ⚠️ | Read-only | If configured |
| API Integrations | ✅ | Authenticated | Token-based |
| Git Operations | ✅ | Full | Within repository |

### Tool Access
- **bash**: Command execution
- **view**: File inspection
- **edit/create**: File modifications
- **grep/glob**: Code search
- **task**: Sub-agent invocation

**Last Updated**: 2026-01-23T19:45:00Z



## 💡 Usage Examples

### Basic Invocation

```yaml
agent_type: escalation-criteria-prompt
prompt: |
  Execute standard operation with default parameters
  Target: <target>
  Mode: <mode>
```

### Advanced Usage

```yaml
agent_type: escalation-criteria-prompt
prompt: |
  Execute with custom configuration:
  - Parameter 1: value1
  - Parameter 2: value2
  - Options: [option_a, option_b]
  
  Validation requirements:
  - Requirement 1
  - Requirement 2
```

### Common Patterns

**Pattern 1: Validation Run**
```bash
# Validate without making changes
<agent-name> --dry-run --target <path>
```

**Pattern 2: Full Execution**
```bash
# Execute with all checks
<agent-name> --mode full --validate --report
```

**Last Updated**: 2026-01-23T19:45:00Z



## 🔗 Integration Patterns

### Workflow Integration

```mermaid
graph LR
    A[Trigger] --> B[Agent Activation]
    B --> C[Execution]
    C --> D[Validation]
    D --> E[Reporting]
    E --> F[Next Stage]
```

### Integration Points

**Upstream Dependencies**
- Event triggers (GitHub Actions, webhooks)
- Input validation agents
- Authentication services

**Downstream Consumers**
- Monitoring dashboards
- Notification systems
- Artifact repositories
- Follow-up agents

### Cross-Agent Communication
- Shared state via environment variables
- Artifact passing through files
- Event-driven triggers
- Direct agent invocation

**Last Updated**: 2026-01-23T19:45:00Z



## ⚡ Activation Commands

### Manual Activation

```bash
# Via task tool
task agent_type="escalation-criteria-prompt" description="<description>" prompt="<prompt>"
```

### GitHub Actions Trigger

```yaml
- name: Activate escalation-criteria-prompt
  uses: ./.github/actions/agent-runner
  with:
    agent: escalation-criteria-prompt
    parameters: |
      target: ${{ github.workspace }}
      mode: full
```

### Programmatic Invocation

```python
from agent_framework import invoke_agent

result = invoke_agent(
    agent_type="escalation-criteria-prompt",
    prompt="Execute operation",
    context={"target": "path/to/target"}
)
```

**Last Updated**: 2026-01-23T19:45:00Z



## 📦 Tool Dependencies

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Python | ≥3.11 | Runtime | Pre-installed |
| Git | ≥2.40 | Version control | Pre-installed |
| bash | ≥5.0 | Shell execution | Pre-installed |

### Optional Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| jq | ≥1.6 | JSON processing | For JSON output |
| yq | ≥4.0 | YAML processing | For YAML configs |
| curl | ≥7.0 | HTTP requests | For API calls |

### Python Dependencies
```python
# requirements.txt
pyyaml>=6.0
requests>=2.31.0
```

**Last Updated**: 2026-01-23T19:45:00Z



## 📤 Output Formats

### Standard Output Format

```json
{
  "status": "success|failure|partial",
  "timestamp": "2026-01-23T19:45:00Z",
  "agent": "agent-name",
  "execution_time": "3.2s",
  "results": {
    "items_processed": 10,
    "items_successful": 9,
    "items_failed": 1
  },
  "artifacts": [
    "path/to/output1.json",
    "path/to/output2.txt"
  ],
  "errors": [],
  "warnings": []
}
```

### Markdown Report Format

```markdown
# Agent Execution Report

**Status**: ✅ Success  
**Timestamp**: 2026-01-23T19:45:00Z  
**Duration**: 3.2s

## Summary
- Items Processed: 10
- Success Rate: 90%

## Details
[Detailed execution information]

## Artifacts
- output1.json
- output2.txt
```

### Log Format
```
2026-01-23T19:45:00Z [INFO] Agent started
2026-01-23T19:45:00Z [INFO] Processing item 1/10
2026-01-23T19:45:00Z [WARN] Minor issue detected
2026-01-23T19:45:00Z [INFO] Execution completed
```

**Last Updated**: 2026-01-23T19:45:00Z



## ⚠️ Error Handling

### Common Failure Modes

#### 1. Input Validation Failure
**Symptoms**: Agent rejects input parameters  
**Recovery**: 
- Validate input format
- Check required fields
- Verify value ranges
- Review examples

#### 2. Resource Access Failure
**Symptoms**: Cannot access required resources  
**Recovery**:
- Check permissions
- Verify paths exist
- Confirm network connectivity
- Review authentication

#### 3. Execution Timeout
**Symptoms**: Operation exceeds time limit  
**Recovery**:
- Reduce scope of operation
- Check for blocking operations
- Review performance bottlenecks
- Consider batch processing

#### 4. Dependency Failure
**Symptoms**: Required tool or service unavailable  
**Recovery**:
- Verify tool installation
- Check service status
- Review dependency versions
- Use fallback mechanisms

### Error Categories

| Category | Severity | Auto-Retry | Escalation |
|----------|----------|------------|------------|
| Transient | Low | ✅ Yes (3x) | After retries |
| Configuration | Medium | ❌ No | Immediate |
| Permission | High | ❌ No | Immediate |
| System | Critical | ⚠️ Once | Immediate |

### Recovery Patterns

**Pattern 1: Graceful Degradation**
```python
try:
    full_operation()
except NonCriticalError:
    limited_operation()
    log_warning()
```

**Pattern 2: Checkpoint Resume**
```python
checkpoint = load_checkpoint()
if checkpoint:
    resume_from(checkpoint)
else:
    start_fresh()
```

**Last Updated**: 2026-01-23T19:45:00Z



**Template Applied**: 2026-01-23T19:45:00Z
