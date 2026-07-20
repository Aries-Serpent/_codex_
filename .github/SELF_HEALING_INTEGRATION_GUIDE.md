# Self-Healing CI Infrastructure Integration Guide

**Version:** 1.0.0  
**Last Updated:** 2026-07-20  
**AAIS Target:** Reliability Score +7 points (92.6 → 99.6+/100)

## Overview

The Self-Healing CI Infrastructure is a production-grade system that automatically:
1. **Detects** CI failures using pattern-based error classification
2. **Classifies** failures into recoverable vs. persistent categories
3. **Recovers** transient failures using exponential backoff retry logic
4. **Monitors** recovery success rates and MTTR (Mean Time To Recovery)
5. **Reports** telemetry for AAIS Reliability score calculation

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 GitHub Actions Workflow                  │
│            (.github/workflows/self-healing.yml)         │
└──────────────┬──────────────────────────────────────────┘
               │
        ┌──────┴──────┬────────────────┬──────────────┐
        │             │                │              │
    Detect         Analyze          Act          Validate
     Failures    (Classify)      (Recover)      (Contracts)
        │             │                │              │
        └─────┬───────┴────────────────┴──────────────┘
              │
        ┌─────▼─────────────────────────────────────┐
        │   Error Classification System              │
        │   (scripts/ci/error_classifier.py)        │
        │                                            │
        │  - Network errors (auto-recoverable)      │
        │  - Resource errors (backoff-recoverable)  │
        │  - Logic errors (escalate)                │
        │  - Timeout errors (backoff-recoverable)   │
        └─────┬────────────────────────────────────┘
              │
        ┌─────▼─────────────────────────────────────┐
        │   Automated Recovery System                │
        │   (scripts/ci/automated_recovery.py)      │
        │                                            │
        │  - Exponential backoff retry logic        │
        │  - Recovery attempt tracking              │
        │  - Success/failure recording              │
        └─────┬────────────────────────────────────┘
              │
        ┌─────▼─────────────────────────────────────┐
        │   Telemetry & Monitoring                  │
        │   (scripts/ci/telemetry_monitor.py)       │
        │                                            │
        │  - Success rate metrics                   │
        │  - MTTR calculation                       │
        │  - Health score (0-100)                   │
        │  - AAIS Reliability delta (+0 to +7 pts)  │
        └─────────────────────────────────────────┘
```

## Components

### 1. Error Classification System (`error_classifier.py`)

Classifies CI failures into predefined categories with recovery severity levels.

**Error Categories:**
- `NETWORK_TRANSIENT` - Connection issues, DNS failures
- `RESOURCE_EXHAUSTION` - Memory, disk space issues
- `TIMEOUT_EXCEEDED` - Process timeouts, slow tests
- `DEPENDENCY_CONFLICT` - Missing/conflicting dependencies
- `IMPORT_ERROR` - Module import failures
- `FLAKY_TEST` - Non-deterministic test failures
- `WORKFLOW_SYNTAX` - YAML/workflow definition errors
- `SECURITY_POLICY` - Permission/credential issues
- `LOGIC_ERROR` - Code bugs, logic failures
- `UNKNOWN` - Unclassified errors

**Recovery Severities:**
- `AUTO_RECOVERABLE` - Retry immediately (3 attempts, 5s delay)
- `BACKOFF_RECOVERABLE` - Retry with exponential backoff (3 attempts, 10-20s delay)
- `ESCALATE_REQUIRED` - Requires human review
- `CRITICAL` - Immediate escalation

**Usage:**
```python
from error_classifier import ErrorClassifier

classifier = ErrorClassifier()
signature = classifier.classify(error_text)

print(signature.category)      # NETWORK_TRANSIENT
print(signature.severity)       # AUTO_RECOVERABLE
print(signature.suggestions)    # ["Retry immediately", "Check network..."]
```

### 2. Automated Recovery System (`automated_recovery.py`)

Executes recovery attempts with adaptive retry strategies.

**Features:**
- Exponential backoff with jitter to prevent thundering herd
- Per-pattern retry configuration (max retries, base delay, multiplier)
- Command re-execution and diagnostics
- Comprehensive attempt logging
- MTTR calculation

**Exponential Backoff Formula:**
```
delay = base_delay * (multiplier ^ (attempt - 1))
delay_with_jitter = delay + random(0, delay * 0.1)
delay_capped = min(delay_with_jitter, max_delay)
```

**Recovery Modes:**
1. **Auto Recovery** (network transient)
   - Immediate retries without delay
   - Max 3 attempts
   - Used for: Connection refused, DNS failures, temporary unavailability

2. **Backoff Recovery** (resource/timeout)
   - Exponential backoff between attempts
   - Max 3 attempts with 10-20 second base delay
   - Multiplier: 2.0x per attempt
   - Used for: Timeouts, resource exhaustion, flaky tests

3. **Escalation** (logic/security errors)
   - No automatic retries
   - Immediate escalation to human review
   - Used for: Code bugs, YAML syntax errors, permission denied

**Usage:**
```python
from automated_recovery import AutomatedRecovery

recovery = AutomatedRecovery(max_retries=3)
success, report = recovery.recover_from_error(
    error_text="Connection refused...",
    command="pytest tests/quick"
)

print(f"Success: {success}")
print(f"Report: {report}")

# Generate metrics report
report_json = recovery.generate_report()
recovery.save_report("/tmp/recovery-report.json")
```

### 3. Telemetry & Monitoring (`telemetry_monitor.py`)

Collects, aggregates, and reports recovery metrics for AAIS scoring.

**Metrics Collected:**
- Total recovery attempts
- Successful vs. failed recoveries
- Recovery rate by pattern
- MTTR (Mean Time To Recovery) by pattern
- CI health score (0-100)
- Estimated AAIS Reliability delta (+0 to +7 points)

**Health Score Calculation:**
```
Health Score = Recovery_Rate_Score (0-50) + MTTR_Score (0-50)

Recovery_Rate_Score = (recovery_rate / 100) * 50
MTTR_Score = 50 * (1 - (mttr - 30) / 270)  [capped at 30-300s range]

Status Mapping:
- Excellent: 80-100 points
- Good: 60-80 points
- Fair: 40-60 points
- Poor: 0-40 points
```

**AAIS Reliability Impact:**
- Baseline (no self-healing): 0 point improvement
- Target metrics:
  - Recovery rate: 80%+ → +3.2 points
  - MTTR < 60 seconds → +3.8 points
  - Maximum improvement: +7 points

**Usage:**
```python
from telemetry_monitor import TelemetryCollector, MetricsReporter

collector = TelemetryCollector(".codex/telemetry")

# Record an attempt
attempt = {
    "pattern_id": "net-conn-refused",
    "severity": "auto_recoverable",
    "success": True,
    "delay_sec": 5,
    "timestamp": "2026-07-20T15:54:00Z"
}
collector.record_recovery_attempt(attempt)

# Analyze and generate dashboard
metrics = collector.analyze_metrics()
dashboard = collector.generate_dashboard()

# Generate markdown report
report = MetricsReporter.generate_markdown(metrics, dashboard)
print(report)
```

## Workflow Integration

### Self-Healing Workflow (.github/workflows/self-healing.yml)

The workflow executes in 5 stages with multi-lane orchestration and policy tier enforcement:

#### Stage 1: Lane Metadata Contract
- Validates input parameters
- Generates deterministic seed for reproducibility
- Creates input lock (SHA256) for artifact traceability
- Outputs: `lane_id`, `shard_id`, `lane_mode`, `input_lock_sha256`

#### Stage 2: Failure Detection (self-healing-detect)
- Retrieves recent workflow runs
- Extracts error signatures and stack traces
- Generates failure count and list
- Outputs: `failure_count`, `patterns_detected`

#### Stage 3: Pattern Analysis (self-healing-analyze)
- Classifies failures using error_classifier
- Generates remediation plan
- Evaluates policy tier constraints
- Outputs: `plan_generated`, `remediation_count`

#### Stage 4: Remediation (self-healing-act)
- Applies recovery actions based on policy tier
- Re-executes failed commands
- Records attempt metrics
- Outputs: `changes_applied`, `rollback_available`

#### Stage 5: Validation & Reporting
- Validates all contract artifacts
- Generates comprehensive summary
- Posts metrics to GitHub output
- Saves telemetry data

### Policy Tiers

Control what recovery actions are allowed:

```
T0 - Metadata-Only
├─ No automatic fixes
├─ Report and analyze only
└─ Used for: Investigation and validation

T1 - Safe-Fix (Default)
├─ Scripts and configuration changes
├─ Non-code modifications
├─ Retry logic and environment variables
└─ Used for: Most transient failures

T2 - Propose-Only
├─ Code modifications require approval
├─ Security-related changes need review
├─ Create PR for changes before applying
└─ Used for: Logic-error recovery attempts

T3 - Escalate
├─ Workflow/policy changes need governance
├─ Require human approval for all changes
├─ Full audit trail maintained
└─ Used for: Critical infrastructure changes
```

## Integration with iterative-self-healing-ci.yml

The existing iterative-self-healing-ci.yml workflow can invoke the enhanced self-healing.yml:

```yaml
# In iterative-self-healing-ci.yml
- name: Invoke enhanced self-healing
  uses: ./.github/workflows/self-healing.yml@refs/heads/main
  with:
    target_workflow: "Code Quality Coverage Suite"
    max_iterations: 3
    healing-policy-tier-max: T1
```

**Integration Points:**
1. **Pattern Detection** - Share failure patterns across workflows
2. **Metrics Aggregation** - Combine MTTR and success rates
3. **Recovery Coordination** - Avoid duplicate recovery attempts
4. **Escalation Routing** - Route persistent failures to appropriate agents

## Configuration

### Environment Variables

Set in GitHub Actions secrets or repository variables:

```bash
# Maximum recovery attempts per failure
CODEX_MAX_RECOVERY_ATTEMPTS=3

# Base delay for exponential backoff (seconds)
CODEX_RECOVERY_BASE_DELAY=10

# Exponential backoff multiplier
CODEX_RECOVERY_BACKOFF_MULTIPLIER=2.0

# Maximum MTTR threshold for "good" health (seconds)
CODEX_MTTR_TARGET=60

# Minimum recovery rate for "good" health (%)
CODEX_RECOVERY_RATE_TARGET=80

# Enable telemetry collection
CODEX_TELEMETRY_ENABLED=true

# Telemetry data retention (days)
CODEX_TELEMETRY_RETENTION_DAYS=30
```

### Workflow Inputs

When invoking self-healing.yml:

```yaml
- uses: ./.github/workflows/self-healing.yml
  with:
    target_workflow: "optional: specific workflow to heal"
    max_iterations: 5
    lane-id: "lane-self-healing"
    shard-id: "shard-0"
    lane-mode: "enabled"
    healing-policy-tier-max: "T1"
    deterministic-seed: "optional: for reproducibility"
    codeql-wave: "off"
```

## Success Criteria

The self-healing infrastructure is considered successful when:

### Immediate Metrics (Session)
- ✅ **Self-healing workflow executes** without errors
- ✅ **Error classification** accurately identifies 80%+ of failure types
- ✅ **Recovery attempts** logged and tracked
- ✅ **Telemetry** collected and dashboards generated

### Short-term Metrics (1 week)
- ✅ **Recovery rate**: 80%+ of transient failures auto-recovered
- ✅ **MTTR reduction**: 40%+ improvement vs. baseline
- ✅ **No false positives**: Zero escalations of recoverable errors
- ✅ **Policy compliance**: All policy tier rules enforced

### Long-term Metrics (1 month)
- ✅ **AAIS Reliability**: +5 to +7 points improvement
- ✅ **AAIS Composite**: 92.6 → 99.6+ / 100
- ✅ **CI health score**: 80-100 (excellent)
- ✅ **Stability**: Consistent recovery rate over time

## Monitoring and Observability

### Health Dashboard

Access the self-healing health dashboard:

```bash
# View telemetry dashboard
cat .codex/telemetry/dashboard.json

# Analyze metrics
python scripts/ci/telemetry_monitor.py --analyze --report markdown

# Record recovery attempt
python scripts/ci/telemetry_monitor.py --record recovery-attempt.json
```

### GitHub Actions Output

Each workflow run publishes metrics:

```
recovery_rate=85.5
mttr_seconds=12.3
health_score=89.7
reliability_delta=5.4
```

### Monitoring Queries

Track recovery patterns over time:

```bash
# Find top failure patterns
jq '.per_pattern | to_entries | sort_by(.value.total_attempts) | reverse' \
  .codex/telemetry/metrics-snapshots.json

# Calculate trend (last 24 hours)
jq '.hourly_trends | to_entries | tail(24)' \
  .codex/telemetry/metrics-snapshots.json

# Extract AAIS delta
jq '.aais_impact.reliability_score_delta' \
  .codex/telemetry/dashboard.json
```

## Testing and Validation

### Unit Tests

Test error classification:
```bash
python -m pytest tests/test_error_classifier.py -v
```

Test recovery logic:
```bash
python -m pytest tests/test_automated_recovery.py -v
```

Test telemetry:
```bash
python -m pytest tests/test_telemetry_monitor.py -v
```

### Integration Tests

Test workflow execution:
```bash
# Run self-healing workflow with test data
gh workflow run self-healing.yml \
  -f healing-policy-tier-max=T0 \
  -f lane-mode=enabled
```

### Stress Tests

Simulate multiple concurrent failures:
```bash
# Generate synthetic failure patterns
python scripts/ci/generate_failure_scenarios.py --count 100

# Verify recovery handling
python scripts/ci/stress_test_recovery.py
```

## Troubleshooting

### Issue: No failures detected

**Cause:** No recent workflow failures or detection not triggered
**Solution:**
1. Verify workflow has recent failures: `gh run list --workflow=pr-checks.yml`
2. Check detection job logs for errors
3. Validate GitHub token has sufficient permissions

### Issue: Recovery attempts not recorded

**Cause:** Telemetry collection disabled or permission issues
**Solution:**
1. Verify `CODEX_TELEMETRY_ENABLED=true`
2. Check `.codex/telemetry` directory permissions
3. Review telemetry job logs for errors

### Issue: Health score not improving

**Cause:** Recovery rate too low or MTTR too high
**Solution:**
1. Check top failing patterns: `jq '.per_pattern' .codex/telemetry/metrics-snapshots.json`
2. Analyze MTTR trends: `jq '.hourly_trends' .codex/telemetry/dashboard.json`
3. Review recovery suggestions for top patterns
4. Increase retry attempts or backoff delays if needed

### Issue: Policy tier enforcement failing

**Cause:** Invalid policy tier or permission constraints
**Solution:**
1. Verify policy tier input is one of: T0, T1, T2, T3
2. Check workflow permissions match policy requirements
3. Review policy enforcement logs in job output

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Error classification system
- ✅ Exponential backoff retry logic
- ✅ Telemetry collection
- ✅ Workflow integration

### Phase 2: Enhancement (Next)
- 🔄 Machine learning-based pattern detection
- 🔄 Predictive failure analysis
- 🔄 Custom recovery handlers per pattern
- 🔄 Advanced dashboarding and visualization

### Phase 3: Advanced (Future)
- ⬜ Multi-repository coordination
- ⬜ Distributed recovery orchestration
- ⬜ Self-learning pattern adaptation
- ⬜ Continuous AAIS optimization

## Support and Issues

- **Documentation:** See `.github/workflows/self-healing.md`
- **Issues:** Tag with `self-healing-ci`
- **Metrics:** Check `.codex/telemetry/dashboard.json`
- **Agents:** Route to `autonomous-test-healer-agent` for test-specific issues

## References

- **Error Patterns:** See `scripts/ci/error_classifier.py` (lines 35-100)
- **Recovery Strategies:** See `scripts/ci/automated_recovery.py` (lines 150-250)
- **Telemetry Schema:** See `scripts/ci/telemetry_monitor.py` (lines 1-50)
- **AAIS Scoring:** See `src/aries_serpent_core/skills/aais.py`
- **Self-Healing Workflow:** See `.github/workflows/self-healing.yml`
- **Iterative Healing:** See `.github/workflows/iterative-self-healing-ci.yml`
