# Autonomous Artifact Monitoring System - Architecture

**Version**: 1.0.0  
**Status**: Production Ready (Phases 1-5 Complete)  
**Last Updated**: 2026-01-22

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Integration Points](#integration-points)
6. [State Management](#state-management)
7. <!-- BROKEN ANCHOR: [Error Handling & Reliability](#error-handling--reliability) -->
8. <!-- BROKEN ANCHOR: [Security & Privacy](#security--privacy) -->
9. <!-- BROKEN ANCHOR: [Performance & Scalability](#performance--scalability) -->
10. [Future Enhancements](#future-enhancements)

---

## System Overview

The **Autonomous Artifact Monitoring System** provides continuous health monitoring of GitHub Actions workflows with intelligent pattern recognition and agent orchestration for automated failure analysis and remediation guidance.

### Key Capabilities

- **Automated Monitoring**: Scheduled checks every 3 hours of 95 workflows (30 producing artifacts)
- **Pattern Recognition**: Matches against 30+ error signatures across 8 categories
- **Agent Orchestration**: Routes failures to 6+ specialized agents for deep analysis
- **Issue Management**: Auto-creates rich issues with diagnostic links, deduplicates, auto-closes on recovery
- **CLI Interface**: Human-friendly command-line tool for manual operation
- **Self-Awareness**: Meta-monitoring creates issues if monitoring workflow itself fails

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  External Triggers                                           │
│  • GitHub Actions Scheduler (cron: every 3 hours)            │
│  • Manual Workflow Dispatch (workflow_dispatch)              │
│  • CLI Manual Invocation (human admin)                       │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Entry Point Layer                                           │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  artifact_monitor.py (Core Monitoring Engine)        │   │
│  │  • GitHub API Client (PyGithub)                      │   │
│  │  • Workflow run retrieval & status tracking          │   │
│  │  • Rate limit handling with exponential backoff      │   │
│  │  • State persistence (JSON + GitHub artifacts)       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  artifact_monitor_cli.py (CLI Wrapper)               │   │
│  │  • Interactive commands (check, report, test)        │   │
│  │  • Rich terminal output (ANSI colors, tables)        │   │
│  │  • Dry-run mode for testing                          │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Analysis Layer                                              │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  pattern_analyzer.py (Pattern Recognition)           │   │
│  │  • Regex-based log parsing                           │   │
│  │  • 30+ error signatures with confidence scoring      │   │
│  │  • Statistical flakiness detection                   │   │
│  │  • Category classification                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  agent_orchestrator.py (Agent Routing)               │   │
│  │  • Category-based agent selection                    │   │
│  │  • Multi-agent orchestration                         │   │
│  │  • Recommendation aggregation                        │   │
│  │  • Confidence-weighted routing                       │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Action Layer                                                │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  issue_manager.py (Issue Lifecycle)                  │   │
│  │  • Create issues with rich formatting                │   │
│  │  • Deduplication (24-hour window)                    │   │
│  │  • Update with new failures                          │   │
│  │  • Auto-close after recovery                         │   │
│  │  • Label management                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  table_generator.py (Rich Formatting)                │   │
│  │  • Summary tables with metrics                       │   │
│  │  • Diagnostic link tables (logs, artifacts, rerun)   │   │
│  │  • Run history tables                                │   │
│  │  • Comparison tables (current vs last success)       │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Integration Layer                                           │
│                                                               │
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │  Specialized Agents  │  Cognitive Brain (Phase 6)   │   │
│  │  • CI Testing        │  • Monitoring Sensor         │   │
│  │  • Dependency        │  • Action Proposals          │   │
│  │  • Coverage          │  • Self-Healing Loop         │   │
│  │  • Security          │  • Confidence Learning       │   │
│  │  • Hygiene           │                              │   │
│  │  • Documentation     │                              │   │
│  └──────────────────────┴──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Storage & State                                             │
│  • .codex/monitoring/state/monitor_state.json (local)        │
│  • GitHub Actions Artifacts (90-day retention)               │
│  • .codex/monitoring/logs/ (operational logs)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Core Monitoring Engine (`artifact_monitor.py`)

**Purpose**: Central orchestrator for workflow monitoring

**Key Classes**:
- `ArtifactMonitor`: Main monitoring class
- `WorkflowRun`: Data class for workflow run information
- `MonitorState`: Persistent state management

**Responsibilities**:
- Fetch workflow runs via GitHub API
- Detect status changes (success ↔ fail)
- Calculate failure rates and flakiness
- Manage rate limits with exponential backoff
- Persist state across runs

**Configuration**:
- Workflow filter (monitor specific workflows)
- Consecutive failure threshold (default: 2)
- Recovery threshold (default: 3)
- Flakiness detection window (default: 20 runs)

### 2. Pattern Analyzer (`pattern_analyzer.py`)

**Purpose**: Intelligent error pattern recognition

**Key Classes**:
- `PatternAnalyzer`: Pattern matching engine
- `ErrorSignature`: Pattern definition with metadata
- `PatternMatch`: Match result with confidence score

**Pattern Database**: `.codex/monitoring/patterns/error_signatures.yaml`
- 30+ signatures across 8 categories
- Regex patterns with capture groups
- Confidence base scores
- Suggested fixes per pattern
- Agent routing hints

**Detection Methods**:
1. **Regex Matching**: Fast pattern matching against logs
2. **Statistical Analysis**: Flakiness detection via failure rate analysis
3. **Confidence Scoring**: Weighted scoring based on pattern specificity

### 3. Agent Orchestrator (`agent_orchestrator.py`)

**Purpose**: Route failures to specialized agents

**Key Classes**:
- `AgentOrchestrator`: Central routing logic
- `AgentRecommendation`: Structured agent response
- `MultiAgentResult`: Aggregated multi-agent analysis

**Routing Map**:
```python
{
    "test": "ci-testing-agent",
    "dependency": "dependency-conflict-agent",
    "coverage": "coverage-gapfill-agent",
    "security": "security-agent",
    "lint": "repository-hygiene-agent",
    "documentation": "documentation-quality-agent"
}
```

**Features**:
- Confidence-based agent selection
- Multi-agent orchestration (max 3 agents per failure)
- Recommendation aggregation
- Fallback suggestions when agents unavailable

### 4. Issue Manager (`issue_manager.py`)

**Purpose**: GitHub Issue lifecycle management

**Key Classes**:
- `IssueManager`: Issue CRUD operations
- `IssueTemplate`: Rich issue formatting
- `DeduplicationEngine`: Duplicate detection

**Issue Lifecycle**:
1. **Create**: On N consecutive failures (default: 2)
2. **Update**: Add new failure instances, update metrics
3. **Close**: After M consecutive successes (default: 3)
4. **Deduplicate**: Merge similar failures within 24-hour window

**Issue Format**:
- Workflow name and status
- Failure rate and last success timestamp
- Pattern analysis with confidence scores
- Diagnostic link table (logs, artifacts, debug, rerun)
- Agent analysis section with recommendations
- Related patterns and historical failures

### 5. CLI Wrapper (`artifact_monitor_cli.py`)

**Purpose**: Human-friendly command-line interface

**Commands**:
- `check`: Run monitoring checks (all or specific workflows)
- `report`: Generate failure report with statistics (7 iteration default)
- `test-patterns`: Test pattern matching against log files
- `interactive`: REPL-style troubleshooting interface

**Features**:
- Rich terminal output with ANSI colors
- Formatted tables for metrics and status
- Dry-run mode for testing
- Progress indicators
- Error handling with helpful messages

---

## Data Flow

### Scheduled Monitoring Flow

```
1. GitHub Actions Scheduler (cron: every 3 hours)
   ↓
2. Workflow triggers: .github/workflows/artifact-monitoring.yml
   ↓
3. artifact_monitor.py loads state from artifact/local JSON
   ↓
4. Fetch workflow runs via GitHub API (with rate limit handling)
   ↓
5. For each workflow run:
   a. Check status change (success → fail, fail → success)
   b. Calculate consecutive failures/successes
   c. Detect flakiness (if enabled)
   ↓
6. pattern_analyzer.py analyzes logs (if failure detected)
   a. Match against 30+ error signatures
   b. Calculate confidence scores
   c. Classify by category
   ↓
7. agent_orchestrator.py routes to specialized agents
   a. Select agent(s) based on category and confidence
   b. Aggregate recommendations
   ↓
8. issue_manager.py manages issue lifecycle
   a. Create issue (if threshold met)
   b. Update existing issue (if duplicate)
   c. Close issue (if recovered)
   ↓
9. table_generator.py formats issue content
   a. Summary tables
   b. Diagnostic links
   c. Agent analysis section
   ↓
10. Save updated state to artifact + local JSON
    ↓
11. Generate job summary with metrics
```

### Manual CLI Flow

```
1. Human Admin runs: python scripts/agents/artifact_monitor_cli.py check
   ↓
2. CLI loads configuration from .codex/config/monitoring.yaml
   ↓
3. Delegates to artifact_monitor.py (same flow as scheduled)
   ↓
4. Displays results in rich terminal format (colored tables)
   ↓
5. Dry-run mode: logs actions without creating issues
```

---

## Integration Points

### GitHub API Integration

**Endpoints Used**:
- `GET /repos/{owner}/{repo}/actions/workflows` - List workflows
- `GET /repos/{owner}/{repo}/actions/workflows/{id}/runs` - Get workflow runs
- `GET /repos/{owner}/{repo}/actions/runs/{id}/logs` - Download logs
- `GET /repos/{owner}/{repo}/actions/runs/{id}/artifacts` - List artifacts
- `GET /repos/{owner}/{repo}/issues` - List/create/update issues
- `POST /repos/{owner}/{repo}/issues` - Create issue
- `PATCH /repos/{owner}/{repo}/issues/{number}` - Update issue

**Authentication**:
- GitHub Actions: `GITHUB_TOKEN` (automatic)
- CLI: `CODEX_MASTER_KEY` or personal access token

**Rate Limit Handling**:
- Check remaining requests before operations
- Exponential backoff on rate limit errors
- Conditional requests with ETags (caching)
- Reserve 500 request buffer

### Specialized Agent Integration

**Agent Invocation**:
- Agents are documented in `.github/agents/`
- CLI wrapper: `scripts/agents/{agent_name}_cli.py`
- Orchestrator constructs invocation context
- Results parsed and aggregated

**Agent Context**:
```python
{
    "failure_category": "test",
    "confidence": 0.85,
    "log_excerpt": "...",
    "pattern_match": {...},
    "workflow_context": {...}
}
```

### Cognitive Brain Integration (Phase 6 - Planned)

**Sensor Module**: `scripts/cognitive/sensors/monitoring_sensor.py`
- Exposes monitoring state to Cognitive Brain
- Provides failure history and patterns
- Enables autonomous decision-making

**Action Proposal**:
- Cognitive Brain proposes fixes based on patterns
- Confidence threshold for auto-execution (0.8+)
- Human approval for high-risk actions

**Self-Healing Loop**:
1. Monitor detects failure
2. Pattern analyzer identifies root cause
3. Cognitive Brain proposes fix
4. (Optional) Auto-execute low-risk fixes
5. Validate fix effectiveness
6. Update confidence scores

---

## State Management

### Local State

**File**: `.codex/monitoring/state/monitor_state.json`

**Schema**:
```json
{
  "version": "1.0.0",
  "last_run": "2026-01-22T07:00:00Z",
  "workflows": {
    "test-comprehensive.yml": {
      "last_status": "success",
      "consecutive_failures": 0,
      "consecutive_successes": 5,
      "failure_rate": 0.05,
      "last_failure": "2026-01-20T12:00:00Z",
      "open_issue_number": null
    }
  },
  "metrics": {
    "total_checks": 150,
    "failures_detected": 8,
    "issues_created": 3,
    "issues_closed": 2,
    "patterns_matched": 15
  }
}
```

### GitHub Actions Artifact

**Name**: `artifact-monitor-state`  
**Retention**: 90 iterations  
**Purpose**: Persist state across workflow runs

**Upload/Download**:
```yaml
- name: Save State
  uses: actions/upload-artifact@v4
  with:
    name: artifact-monitor-state
    path: .codex/monitoring/state/monitor_state.json
    retention-days: 90
```

### State Synchronization

1. **Workflow Start**: Download artifact (if exists) OR load local JSON
2. **Monitoring Run**: Update state in memory
3. **Workflow End**: Upload artifact AND save local JSON (dual persistence)

---

## Error Handling & Reliability

### Failure Modes

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| **GitHub API Rate Limit** | Check `X-RateLimit-Remaining` header | Exponential backoff, conditional requests |
| **Network Timeout** | HTTP timeout exceptions | Retry with backoff (max 3 attempts) |
| **State Corruption** | JSON parsing errors | Fallback to backup, reinitialize state |
| **Pattern Match Error** | Regex compilation errors | Log error, skip pattern, continue |
| **Agent Unavailable** | Import/execution errors | Use fallback suggestions |
| **Issue Creation Failure** | GitHub API errors | Log failure, retry next run |
| **Monitoring Workflow Failure** | Self-awareness check | Create meta-issue for human review |

### Retry Strategy

```python
max_retries = 3
backoff_multiplier = 2
initial_delay = 1  # second

for attempt in range(max_retries):
    try:
        result = api_call()
        break
    except RateLimitError:
        delay = initial_delay * (backoff_multiplier ** attempt)
        sleep(delay)
    except NetworkError:
        if attempt == max_retries - 1:
            log_error()
            raise
```

### Meta-Monitoring

**Self-Awareness**: Monitoring workflow monitors itself
- If monitoring workflow fails, create issue: "Monitoring System Failure"
- Include failure logs and diagnostic information
- Alert human admin for manual intervention

---

## Security & Privacy

### Security Measures

1. **Token Management**:
   - Use GitHub-provided `GITHUB_TOKEN` (limited scope)
   - Store `CODEX_MASTER_KEY` as repository secret
   - Never log or expose tokens

2. **Secret Scrubbing** (Phase 6):
   - PII scrubber integration before logging
   - Redact sensitive patterns in logs
   - GDPR/CCPA compliance

3. **Permissions**:
   - Workflow: `contents: read`, `issues: write`, `actions: read`
   - Minimal necessary permissions

4. **Input Validation**:
   - Sanitize workflow names and filters
   - Validate configuration schema
   - Escape special characters in regex patterns

### Privacy Considerations

- **Log Handling**: Logs may contain sensitive information
  - Scrub before storage (Phase 6)
  - Limited retention (90 iterations)
  - Access control via GitHub permissions

- **Issue Content**: Public issues may expose failures
  - Option to create private issues (configuration)
  - Redact sensitive patterns

---

## Performance & Scalability

### Current Performance

- **Workflows Monitored**: 95 (30 producing artifacts)
- **Polling Interval**: Every 3 hours (8 runs/day)
- **API Requests per Run**: ~100-200 (depending on workflow count)
- **Execution Time**: 2-5 minutes per run
- **Rate Limit Usage**: <5% of hourly quota

### Scalability Considerations

1. **Workflow Count**:
   - Current: 95 workflows
   - Limit: ~500 workflows (GitHub API rate limits)
   - Mitigation: Workflow filtering, caching, conditional requests

2. **Polling Frequency**:
   - Current: Every 3 hours (8 runs/day)
   - Maximum: Every 15 minutes (96 runs/day) - requires caching
   - Trade-off: Freshness vs API usage

3. **Log Volume**:
   - Pattern matching on large logs (>10MB) may be slow
   - Mitigation: Stream processing, selective log downloading

4. **State Size**:
   - JSON state grows with workflow history
   - Mitigation: Periodic cleanup, rolling window (30 iterations)

### Optimization Strategies

- **Caching**: Use ETags for conditional requests
- **Parallelization**: Process workflows concurrently (thread pool)
- **Incremental Processing**: Only check recent runs (last 24 hours)
- **Pattern Indexing**: Compile regex patterns once at startup

---

## Future Enhancements

### Phase 6: Cognitive Brain Integration

- **Sensor Module**: Expose monitoring state to Cognitive Brain
- **Autonomous Action Proposals**: AI-driven fix suggestions
- **Self-Healing Loop**: Validate fix effectiveness and learn
- **Confidence Learning**: Adjust pattern confidence based on outcomes

### Phase 7: Testing & Validation

- **Unit Tests**: Comprehensive pytest suite
- **Integration Tests**: End-to-end workflow testing
- **Security Scanning**: CodeQL analysis
- **Performance Benchmarking**: Load testing with 500+ workflows

### Future Enhancements (Post-Phase 7)

1. **Advanced Analytics**:
   - Trend analysis (failure rate over time)
   - Correlation detection (related failures)
   - Predictive modeling (failure prediction)

2. **Notification Channels**:
   - Slack integration
   - Email alerts
   - Discord webhooks

3. **Dashboard**:
   - Web-based monitoring dashboard
   - Real-time status visualization
   - Historical trend charts

4. **Custom Patterns**:
   - User-defined pattern creation
   - Pattern effectiveness metrics
   - Community pattern sharing

5. **Multi-Repository Support**:
   - Monitor workflows across multiple repositories
   - Cross-repository failure correlation
   - Organization-wide health dashboard

---

## Configuration

**Primary Config**: `.codex/config/monitoring.yaml`  
**Pattern Database**: `.codex/monitoring/patterns/error_signatures.yaml`  
**Workflow Inventory**: `.codex/monitoring/workflow_inventory.json`

See configuration files for detailed settings and options.

---

## Deployment

### Prerequisites

- GitHub repository with Actions enabled
- Python 3.8+ with `PyGithub`, `PyYAML` packages
- GitHub token with `repo`, `workflow`, `issues:write` permissions

### Setup Steps

1. **Install Dependencies**:
   ```bash
   pip install PyGithub PyYAML requests
   ```

2. **Configure Secrets**:
   - Add `CODEX_MASTER_KEY` to repository secrets (GitHub UI)

3. **Enable Workflow**:
   - Workflow: `.github/workflows/artifact-monitoring.yml`
   - Set `if: true` (remove workflow guard if present)

4. **Test Dry-Run**:
   ```bash
   python scripts/agents/artifact_monitor_cli.py check --dry-run
   ```

5. **Verify Scheduled Execution**:
   - Wait for cron trigger (every 3 hours)
   - Check workflow runs in GitHub Actions UI

---

## Maintenance

### Regular Tasks

- **per-phase**: Review open monitoring issues
- **Monthly**: Audit pattern effectiveness (accuracy metrics)
- **Quarterly**: Update error signature database with new patterns

### Monitoring Health Checks

- **State File Size**: Should be <1MB (cleanup if larger)
- **API Usage**: Should be <50% of rate limit
- **Issue Volume**: <10 open monitoring issues (investigate if more)
- **Pattern Match Rate**: >70% of failures should match patterns

---

## References

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **PyGithub Docs**: https://pygithub.readthedocs.io/
- **Pattern Signature Database**: `.codex/monitoring/patterns/error_signatures.yaml`
- **Configuration Reference**: `.codex/config/monitoring.yaml`
- **Agent Specification**: `.github/agents/artifact-monitor-agent.md`

---

**Document Version**: 1.0.0  
**Architecture Status**: ✅ Production Ready  
**Next Review**: After Phase 6 completion
