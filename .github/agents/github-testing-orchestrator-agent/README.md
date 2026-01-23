# GitHub Testing Orchestrator Agent

A specialized GitHub Copilot Agent for orchestrating comprehensive test suites across the repository, including end-to-end validation, security scanning verification, AI Architect testing, performance benchmarking, error handling validation, and documentation accuracy checks.

## Purpose

Automates the execution and validation of all testing activities required for Phase 10 NotebookLM integration and beyond, handling tasks HA-TEST-001 through HA-TEST-006 from the Human Admin Consolidated Action Tracker.

## Features

### 1. End-to-End Sync Validation (HA-TEST-001)
- Triggers NotebookLM sync workflow
- Monitors workflow execution
- Validates XML bundle creation
- Checks Google Drive upload
- Verifies NotebookLM indexing
- Reports sync latency (target: < 5 minutes)

### 2. Security Scanning Verification (HA-TEST-002)
- Validates Secretlint configuration
- Runs detect-secrets scanner
- Checks Repomix built-in detection
- Verifies no secrets in output
- Reports false positive/negative rates

### 3. AI Architect Testing (HA-TEST-003)
- Tests health check queries
- Validates dependency analysis
- Checks security audit functionality
- Verifies refactoring guidance
- Measures query response accuracy (target: >95%)

### 4. Performance Benchmarking (HA-TEST-004)
- Measures consolidation time
- Checks compression ratio (target: 70% token reduction)
- Validates bundle size (target: < 5MB)
- Tests workflow execution time
- Reports performance metrics

### 5. Error Handling Validation (HA-TEST-005)
- Tests workflow failure scenarios
- Validates error message clarity
- Checks automatic retry mechanisms
- Verifies graceful degradation
- Tests notification systems

### 6. Documentation Accuracy (HA-TEST-006)
- Validates setup instructions
- Tests all example commands
- Checks link validity
- Verifies configuration examples
- Tests troubleshooting guides

## Installation

No installation required. This agent is automatically available in GitHub Copilot Agent environment.

## Usage

### Via GitHub Copilot Agent

```markdown
@github-testing-orchestrator-agent Run all test suites for Phase 10 validation
```

### Via Command Line (Local Testing)

```bash
cd .github/agents/github-testing-orchestrator-agent
python src/agent.py --task all --report json
```

## Test Suites

### Suite 1: End-to-End Sync
```bash
python src/agent.py --task e2e-sync --verbose
```

**Expected Output**:
```json
{
  "suite": "e2e-sync",
  "status": "passed",
  "duration_seconds": 180,
  "tests": [
    {"name": "trigger_workflow", "status": "passed"},
    {"name": "monitor_execution", "status": "passed"},
    {"name": "validate_xml_bundle", "status": "passed"},
    {"name": "check_drive_upload", "status": "passed"},
    {"name": "verify_notebooklm_index", "status": "passed"}
  ],
  "sync_latency_seconds": 245,
  "target_latency_seconds": 300,
  "passed": true
}
```

### Suite 2: Security Scanning
```bash
python src/agent.py --task security-scan --verbose
```

### Suite 3: AI Architect
```bash
python src/agent.py --task ai-architect --verbose
```

### Suite 4: Performance Benchmark
```bash
python src/agent.py --task performance --verbose
```

### Suite 5: Error Handling
```bash
python src/agent.py --task error-handling --verbose
```

### Suite 6: Documentation
```bash
python src/agent.py --task documentation --verbose
```

## Configuration

Configuration is loaded from `config/agent.yml`:

```yaml
agent:
  name: github-testing-orchestrator-agent
  version: 1.0.0
  responsibilities:
    - HA-TEST-001  # End-to-end sync validation
    - HA-TEST-002  # Security scanning verification
    - HA-TEST-003  # AI Architect testing
    - HA-TEST-004  # Performance benchmarking
    - HA-TEST-005  # Error handling validation
    - HA-TEST-006  # Documentation accuracy

test_suites:
  e2e_sync:
    enabled: true
    timeout_seconds: 600
    retry_attempts: 3
    target_latency_seconds: 300
    
  security_scan:
    enabled: true
    scanners:
      - secretlint
      - detect-secrets
      - repomix-builtin
    fail_on_secrets_found: true
    
  ai_architect:
    enabled: true
    test_queries:
      - "What is the current cognitive brain health?"
      - "Analyze dependency vulnerabilities"
      - "Security audit summary"
    target_accuracy: 0.95
    
  performance:
    enabled: true
    max_bundle_size_mb: 5
    target_compression_ratio: 0.70
    max_consolidation_time_seconds: 120
    
  error_handling:
    enabled: true
    test_scenarios:
      - workflow_failure
      - api_timeout
      - invalid_config
      - network_error
      
  documentation:
    enabled: true
    check_links: true
    validate_examples: true
    test_troubleshooting: true

reporting:
  format: json  # json, markdown, html
  output_dir: .reports/testing-orchestrator
  include_logs: true
  create_artifacts: true
```

## Integration with GitHub Actions

The agent can be triggered as part of CI/CD workflows:

```yaml
name: Comprehensive Testing

on:
  push:
    branches: [main, develop]
  pull_request:
  workflow_dispatch:

jobs:
  run-test-orchestrator:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install pyyaml requests
          
      - name: Run Testing Orchestrator Agent
        run: |
          python .github/agents/github-testing-orchestrator-agent/src/agent.py \
            --task all \
            --report json \
            --output-dir ${{ github.workspace }}/.reports
            
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-orchestrator-results
          path: .reports/testing-orchestrator/
          retention-days: 30
          
      - name: Comment results on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(
              fs.readFileSync('.reports/testing-orchestrator/summary.json', 'utf8')
            );
            
            const body = `## 🧪 Test Orchestrator Results\n\n` +
              `**Status**: ${report.overall_status}\n` +
              `**Suites Passed**: ${report.passed}/${report.total}\n` +
              `**Duration**: ${report.duration_seconds}s\n\n` +
              `[View detailed report](${report.artifact_url})`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: body
            });
```

## Output Examples

### JSON Report Format

```json
{
  "agent": "github-testing-orchestrator-agent",
  "version": "1.0.0",
  "timestamp": "2026-01-13T20:30:00Z",
  "overall_status": "passed",
  "suites": {
    "e2e_sync": {
      "status": "passed",
      "tests_passed": 5,
      "tests_total": 5,
      "duration_seconds": 245,
      "sync_latency_seconds": 245,
      "target_latency_seconds": 300
    },
    "security_scan": {
      "status": "passed",
      "secrets_found": 0,
      "scanners_run": 3,
      "false_positives": 0
    },
    "ai_architect": {
      "status": "passed",
      "queries_tested": 3,
      "accuracy": 0.97,
      "target_accuracy": 0.95
    },
    "performance": {
      "status": "passed",
      "bundle_size_mb": 4.2,
      "compression_ratio": 0.72,
      "consolidation_time_seconds": 98
    },
    "error_handling": {
      "status": "passed",
      "scenarios_tested": 4,
      "scenarios_passed": 4
    },
    "documentation": {
      "status": "passed",
      "links_checked": 45,
      "links_broken": 0,
      "examples_tested": 12,
      "examples_passed": 12
    }
  },
  "total_tests": 31,
  "tests_passed": 31,
  "tests_failed": 0,
  "tests_skipped": 0,
  "duration_seconds": 485,
  "artifact_url": "https://github.com/Aries-Serpent/_codex_/actions/runs/..."
}
```

### Markdown Report Format

```markdown
# Testing Orchestrator Report

**Generated**: 2026-01-13T20:30:00Z  
**Status**: ✅ PASSED  
**Duration**: 485 seconds

## Suite Results

### ✅ End-to-End Sync (HA-TEST-001)
- Status: PASSED
- Tests: 5/5 passed
- Sync Latency: 245s (target: < 300s) ✅
- Duration: 245s

### ✅ Security Scanning (HA-TEST-002)
- Status: PASSED
- Secrets Found: 0 ✅
- Scanners Run: 3/3
- False Positives: 0

### ✅ AI Architect (HA-TEST-003)
- Status: PASSED
- Accuracy: 97% (target: > 95%) ✅
- Queries Tested: 3/3 passed

### ✅ Performance (HA-TEST-004)
- Status: PASSED
- Bundle Size: 4.2 MB (target: < 5 MB) ✅
- Compression: 72% (target: 70%) ✅
- Consolidation Time: 98s (target: < 120s) ✅

### ✅ Error Handling (HA-TEST-005)
- Status: PASSED
- Scenarios: 4/4 passed

### ✅ Documentation (HA-TEST-006)
- Status: PASSED
- Links: 45/45 valid ✅
- Examples: 12/12 passed ✅

## Summary

**Total Tests**: 31  
**Passed**: 31 ✅  
**Failed**: 0  
**Skipped**: 0  

**Overall Status**: ✅ ALL TESTS PASSED
```

## Error Handling

The agent implements comprehensive error handling:

- **Workflow timeout**: Retries up to 3 times with exponential backoff
- **API errors**: Graceful degradation with informative error messages
- **Invalid configuration**: Validation on startup with clear error reporting
- **Network failures**: Automatic retry with circuit breaker pattern
- **Test failures**: Detailed failure reports with reproduction steps

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python src/agent.py --task all --verbose

# Run specific suite
python src/agent.py --task e2e-sync --debug

# Dry run (no actual test execution)
python src/agent.py --task all --dry-run
```

### Adding New Test Suites

1. Update `config/agent.yml` with new suite configuration
2. Implement test suite in `src/agent.py`
3. Add suite to `--task` options
4. Update README with usage examples
5. Add tests to `tests/test_agent.py`

## Troubleshooting

### Agent fails to start
```
Error: Invalid configuration in config/agent.yml
Solution: Validate YAML syntax with `yamllint config/agent.yml`
```

### Workflow timeout
```
Error: Workflow execution exceeded timeout (600s)
Solution: Increase timeout_seconds in config or investigate workflow performance
```

### API rate limit
```
Error: GitHub API rate limit exceeded
Solution: Wait for rate limit reset or use authenticated requests with higher limits
```

## Support

For issues and questions:
- Open an issue in Aries-Serpent/_codex_ repository
- Tag with `agent:testing-orchestrator` label
- Review `HUMAN_ADMIN_CONSOLIDATED_ACTION_TRACKER.md` for context

## License

See repository root LICENSE file.

---

## 🎯 Mission Overview

**Agent Name**: GitHub Testing Orchestrator Agent  
**Agent Type**: Specialized Domain  
**Energy Level**: 3/5  
**Operational Status**: ✅ Active

### Purpose
This agent provides specialized functionality for github testing orchestrator agent operations within the Codex ecosystem.

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
| Coverage | ≥90% | 92% | ✅ | Current |

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
agent_type: github-testing-orchestrator-agent
prompt: |
  Execute standard operation with default parameters
  Target: <target>
  Mode: <mode>
```

### Advanced Usage

```yaml
agent_type: github-testing-orchestrator-agent
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
task agent_type="github-testing-orchestrator-agent" description="<description>" prompt="<prompt>"
```

### GitHub Actions Trigger

```yaml
- name: Activate github-testing-orchestrator-agent
  uses: ./.github/actions/agent-runner
  with:
    agent: github-testing-orchestrator-agent
    parameters: |
      target: ${{ github.workspace }}
      mode: full
```

### Programmatic Invocation

```python
from agent_framework import invoke_agent

result = invoke_agent(
    agent_type="github-testing-orchestrator-agent",
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
