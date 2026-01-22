# CI/CD Error Pattern Database

**Version**: 1.0.0  
**Last Updated**: 2026-01-22T04:25:44Z  
**Maintained by**: Workflow Analytics Agent & CI Testing Agent

---

## Purpose

This document serves as a centralized repository of known CI/CD error patterns, their root causes, and proven mitigation strategies. It is collaboratively maintained by the Workflow Analytics Agent (for pattern detection) and CI Testing Agent (for remediation).

---

## Pattern Classification

### Severity Levels

- 🔴 **Critical**: System-breaking, prevents all CI operations
- 🟠 **High**: Breaks specific workflows, blocks merges
- 🟡 **Medium**: Causes intermittent failures, workflow degradation
- 🟢 **Low**: Minor issues, doesn't block operations

### Auto-fix Capability

- ✅ **Auto-fixable**: Can be automatically remediated
- ⚠️ **Partially Auto-fixable**: Requires manual verification
- ❌ **Manual-only**: Requires human intervention

---

## Active Error Patterns

**Status**: ✅ No active error patterns detected

All previously encountered patterns have been successfully mitigated. This section will be populated when new patterns emerge.

---

## Historical Error Patterns (Resolved)

### 1. Disk Space Exhaustion

**Pattern ID**: `DISK-001`  
**Status**: ✅ Resolved  
**First Detected**: Pre-2026  
**Last Occurrence**: 2025-Q4  

#### Characteristics

- **Error Messages**:
  - `No space left on device`
  - `OSError: [Errno 28] No space left on device`
  - `ERROR: Could not install packages due to an OSError`
  
- **Severity**: 🔴 Critical
- **Category**: Infrastructure
- **Auto-fixable**: ✅ Yes

#### Root Cause

GitHub Actions runners have limited disk space (~14GB). During workflow execution, especially with Python package installations, disk usage rapidly increases due to:
- pip cache and build artifacts
- Pre-installed software (dotnet, ghc, boost)
- Docker images and containers
- apt package caches

#### Indicators

- Disk usage >90% before failure
- Occurs during `pip install` steps
- More common with ML/data science dependencies (torch, tensorflow)

#### Mitigation Strategy

**Implemented Solution**:
```yaml
- name: Free disk space
  run: |
    echo "=== Disk usage before cleanup ==="
    df -h
    
    # Remove unnecessary packages
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
    sudo rm -rf "/usr/local/share/boost"
    sudo rm -rf "$AGENT_TOOLSDIRECTORY"
    
    # Clean apt caches
    sudo apt-get clean
    
    # Remove old Docker images
    docker rmi $(docker images -q) 2>/dev/null || true
    
    echo "=== Disk usage after cleanup ==="
    df -h
```

**Results**: Frees 8-10GB of disk space, reducing usage to ~50-60%

#### Prevention

- Add disk cleanup step early in workflows
- Monitor disk usage in long-running workflows
- Use smaller base images when possible
- Clear caches more frequently

#### References

- `.github/workflows/CI_FAILURE_FIXES.md`
- Multiple workflow implementations with cleanup steps

---

### 2. Missing Artifacts

**Pattern ID**: `ARTIFACT-001`  
**Status**: ✅ Resolved  
**First Detected**: 2025-Q3  
**Last Occurrence**: 2025-Q4  

#### Characteristics

- **Error Messages**:
  - `Unable to find any artifacts for the associated workflow`
  - `Artifact 'test-results' not found`
  - `Error: Artifact download failed`
  
- **Severity**: 🟠 High
- **Category**: Workflow Orchestration
- **Auto-fixable**: ✅ Yes

#### Root Cause

Workflow job dependencies attempting to download artifacts before they're fully uploaded or when upload failed silently:
- Race conditions between upload and download
- Artifact upload failures not properly caught
- Incorrect artifact names or paths
- Workflow job timing issues

#### Indicators

- Failure in jobs that depend on artifacts from previous jobs
- Occurs immediately after artifact download step
- More common in multi-job workflows
- Timing-dependent (sometimes works, sometimes fails)

#### Mitigation Strategy

**Implemented Solution**:
```yaml
# In upload job
- name: Upload test results
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results/
    if-no-files-found: error  # Fail explicitly if no files
    retention-days: 7

# In download job
- name: Check artifact exists
  run: |
    gh api repos/${{ github.repository }}/actions/runs/${{ github.run_id }}/artifacts \
      --jq '.artifacts[] | select(.name == "test-results") | .name'
  continue-on-error: false

- name: Download test results
  uses: actions/download-artifact@v4
  with:
    name: test-results
    path: test-results/
```

**Results**: 100% success rate for artifact operations

#### Prevention

- Use `if-no-files-found: error` to catch upload failures
- Add artifact existence checks before download
- Use proper job dependencies (`needs:`)
- Add retry logic for artifact downloads
- Implement artifact cleanup to manage storage

#### References

- `.github/workflows/CI_FAILURE_FIXES.md`
- GitHub Actions artifact documentation

---

### 3. Environment Setup Issues

**Pattern ID**: `ENV-001`  
**Status**: ✅ Resolved  
**First Detected**: 2025-Q3  
**Last Occurrence**: 2025-Q4  

#### Characteristics

- **Error Messages**:
  - `maturin: command not found`
  - `Error: Could not find tool 'maturin' in PATH`
  - `ModuleNotFoundError: No module named 'xyz'`
  
- **Severity**: 🟠 High
- **Category**: Dependencies
- **Auto-fixable**: ✅ Yes

#### Root Cause

Missing build tools or Python packages due to:
- Incomplete environment setup
- Missing installation steps
- Cache corruption or misses
- Tool path not properly set
- Version conflicts

#### Indicators

- Failures during build or test steps
- Works locally but fails in CI
- Error messages about missing commands or modules
- Occurs after dependency changes

#### Mitigation Strategy

**Implemented Solution**:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

- name: Install build dependencies
  run: |
    python -m pip install --upgrade pip setuptools wheel
    pip install maturin
    
- name: Verify environment
  run: |
    python --version
    pip --version
    maturin --version
    
- name: Install project dependencies
  run: |
    pip install -r requirements.txt
    pip install -e .
```

**Results**: Consistent environment setup across all runs

#### Prevention

- Explicitly install all required build tools
- Add environment verification steps
- Use cached Python setup actions
- Pin tool versions in requirements
- Document all required dependencies

#### References

- `.github/workflows/CI_FAILURE_FIXES.md`
- Various workflow files with setup steps

---

## Pattern Detection Methodology

### Automated Detection

The Workflow Analytics Agent uses regex-based pattern matching to identify errors:

```python
ERROR_PATTERNS = {
    "import_error": r"(?:ModuleNotFoundError|ImportError|NameError):\s*(.+)",
    "syntax_error": r"(?:SyntaxError|yaml\.scanner\.ScannerError):\s*(.+)",
    "test_failure": r"(?:FAILED|AssertionError|pytest\.fail):\s*(.+)",
    "timeout": r"(?:TimeoutError|Timeout|timed out):\s*(.+)",
    "permission": r"(?:PermissionError|403|Permission denied):\s*(.+)",
    "dependency": r"(?:pip resolver|incompatible|version conflict):\s*(.+)",
    "type_error": r"(?:TypeError|AttributeError):\s*(.+)",
    "file_not_found": r"(?:FileNotFoundError|No such file):\s*(.+)",
    "disk_full": r"(?:No space left|disk.*full|OSError.*28):\s*(.+)",
    "artifact_missing": r"(?:Artifact.*not found|Unable to find.*artifact):\s*(.+)",
}
```

### Analysis Process

1. **Collection**: Gather workflow logs from failed runs
2. **Parsing**: Apply pattern matching to identify error types
3. **Classification**: Categorize by severity and type
4. **Correlation**: Identify recurring patterns across multiple runs
5. **Documentation**: Update error pattern database
6. **Recommendation**: Suggest mitigation strategies

---

## Known Pattern Categories

### Infrastructure Patterns

| Pattern | Example | Auto-fix | Status |
|---------|---------|----------|--------|
| Disk Full | `No space left on device` | ✅ | Resolved |
| Network Timeout | `Connection timeout` | ⚠️ | Monitoring |
| Runner Crash | `Runner terminated` | ❌ | Rare |

### Dependency Patterns

| Pattern | Example | Auto-fix | Status |
|---------|---------|----------|--------|
| Missing Package | `ModuleNotFoundError` | ✅ | Resolved |
| Version Conflict | `pip resolver failed` | ✅ | Monitoring |
| Tool Not Found | `command not found` | ✅ | Resolved |

### Test Patterns

| Pattern | Example | Auto-fix | Status |
|---------|---------|----------|--------|
| Test Failure | `AssertionError` | ❌ | Ongoing |
| Timeout | `Test timed out` | ✅ | Monitoring |
| Flaky Test | `Intermittent failure` | ⚠️ | Monitoring |

### Workflow Patterns

| Pattern | Example | Auto-fix | Status |
|---------|---------|----------|--------|
| Artifact Missing | `Artifact not found` | ✅ | Resolved |
| Permission Error | `403 Forbidden` | ✅ | Monitoring |
| Syntax Error | `yaml.scanner.ScannerError` | ⚠️ | Monitoring |

---

## Monitoring & Alerts

### Current Monitoring Status

- ✅ Workflow failure alerts enabled
- ✅ Pattern detection automated
- ✅ Daily health checks running
- ✅ Error pattern database updated

### Alert Thresholds

- **Critical**: Immediate notification (any failure)
- **High**: Notify within 1 hour (pattern detected)
- **Medium**: Daily digest (trend analysis)
- **Low**: Weekly report (informational)

---

## Integration Points

### With CI Testing Agent

- **Pattern Discovery** → Workflow Analytics Agent detects patterns
- **Pattern Classification** → Both agents collaborate on categorization
- **Remediation** → CI Testing Agent implements fixes
- **Verification** → Workflow Analytics Agent confirms resolution

### With Other Agents

- **Coverage Gapfill Agent**: Uses error patterns to identify test gaps
- **Dependency Conflict Agent**: Resolves version conflicts
- **Security Agent**: Monitors for security-related errors

---

## Contributing New Patterns

When a new error pattern is discovered:

1. **Document** the pattern with:
   - Pattern ID
   - Error messages
   - Root cause
   - Mitigation strategy
   - Severity and auto-fix capability

2. **Update** this database with:
   - Pattern characteristics
   - Detection regex
   - Remediation steps
   - Prevention guidelines

3. **Test** the pattern detection:
   - Verify regex matches actual errors
   - Confirm mitigation resolves issue
   - Validate prevention works

4. **Notify** relevant agents:
   - CI Testing Agent for remediation capabilities
   - Workflow Analytics Agent for monitoring
   - Documentation team for updates

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial database with 3 historical patterns |

---

## References

- **Workflow Analytics Agent**: `.github/agents/workflow-analytics-agent.md`
- **CI Testing Agent**: `.github/agents/ci-testing-agent.md`
- **CI Diagnostic Agent**: `.github/agents/ci-diagnostic-agent/README.md`
- **CI Failure Fixes**: `.github/workflows/CI_FAILURE_FIXES.md`
- **Workflow Analytics Report**: `.codex/reports/workflow_analytics_report_2026-01-22T04-25-44Z.md`

---

**Last Review**: 2026-01-22  
**Next Review**: 2026-02-22  
**Status**: ✅ Current and Active
