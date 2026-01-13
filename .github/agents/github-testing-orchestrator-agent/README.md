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
