# CI Failure Resolution Agent

**Agent Name:** `ci-failure-resolution-agent`  
**Version:** 1.0.0  
**Created:** 2026-02-18  
**Purpose:** Autonomous CI failure diagnosis, resolution, and verification for GitHub Actions workflows

---

## 🎯 Agent Overview

This specialized agent automates the complete CI failure resolution lifecycle when a user provides links to failing GitHub Actions workflow runs. The agent fetches all artifacts and logs, identifies failure patterns, implements fixes, and validates using a self-test process that mirrors the failing checks.

### Core Capabilities

1. **Automated Log & Artifact Retrieval** - Fetch all CI logs and artifacts from GitHub Actions
2. **Failure Pattern Recognition** - Identify recurring patterns across multiple test failures
3. **Root Cause Analysis** - Diagnose underlying issues beyond surface-level symptoms
4. **Automated Fix Implementation** - Apply targeted fixes based on failure patterns
5. **Self-Validation** - Test fixes locally using CI-equivalent validation before push
6. **Comprehensive Documentation** - Track all failures, fixes, and validation results

---

## 📋 Agent Activation

### Trigger Patterns

The agent activates when the user provides:

```
@copilot Fix CI failures:
- https://github.com/Aries-Serpent/_codex_/actions/runs/22124253398/job/63950783741?pr=3248
- https://github.com/Aries-Serpent/_codex_/actions/runs/22124253398/job/63950783783?pr=3248
```

Or:

```
@copilot Review and fix failing checks for PR #3248
- Code scanning results / CodeQL
- Pre-Merge Validation / Final Pre-Merge Checks
- Resilient Validation Suite / validation (quick)
- Resilient Validation Suite / validation (slow)
```

### Activation Commands

- `@copilot ci-failure-resolution-agent [workflow_run_urls]`
- `@copilot fix-ci [pr_number]` (auto-detects failing checks)
- `@copilot analyze-ci-failures [workflow_run_urls]`

---

## 🔧 Agent Capabilities

### 1. Log & Artifact Retrieval

**Tools Used:**
- `github-mcp-server-actions_list` - List workflow runs
- `github-mcp-server-actions_get` - Get specific workflow/job details
- `github-mcp-server-get_job_logs` - Download job logs
- Custom artifact download via GitHub API

**Process:**
1. Parse workflow run URLs from user input
2. Extract run IDs and job IDs
3. Download all job logs (failed and passed for comparison)
4. Download all artifacts (test results, coverage reports, etc.)
5. Store locally in `.codex/ci_analysis/[run_id]/`

**Output:**
```
.codex/ci_analysis/22124253398/
├── logs/
│   ├── validation_quick_63950783741.log
│   ├── validation_slow_63950783783.log
│   └── pre_merge_validation_63918313164.log
├── artifacts/
│   ├── validation-results-quick/
│   ├── validation-results-slow/
│   └── coverage-report/
└── metadata.json
```

### 2. Failure Pattern Recognition

**Pattern Categories:**

| Pattern Type | Detection Method | Priority |
|--------------|------------------|----------|
| **Import/Dependency** | `ImportError`, `ModuleNotFoundError` | P0 (Critical) |
| **Protocol isinstance** | `isinstance.*Protocol`, missing `@runtime_checkable` | P1 (High) |
| **Timeout Issues** | `Timeout`, execution > threshold | P0 (Critical) |
| **Assertion Failures** | `AssertionError`, grouped by module | P2 (Medium) |
| **Type Errors** | `TypeError`, `AttributeError` | P1 (High) |
| **Mock Issues** | `MagicMock`, `spec=` problems | P2 (Medium) |
| **Test Infrastructure** | Fixture, conftest, collection errors | P0 (Critical) |

**Pattern Analysis:**
```python
def analyze_failure_patterns(log_content):
    """
    Extract and categorize failure patterns from CI logs.
    
    Returns:
    {
        'import_errors': [{'test': '...', 'module': '...', 'line': ...}],
        'protocol_errors': [{'test': '...', 'protocol': '...'}],
        'timeout_tests': [{'test': '...', 'duration': ...}],
        'assertion_failures': [{'test': '...', 'expected': '...', 'actual': '...'}],
        ...
    }
    """
```

### 3. Root Cause Diagnosis

**Diagnostic Process:**

1. **Failure Clustering** - Group similar failures together
2. **Dependency Analysis** - Identify missing or conflicting dependencies
3. **Code Path Tracing** - Trace failures to source code locations
4. **Historical Correlation** - Check if failures match known patterns in memory
5. **Impact Assessment** - Determine blast radius of each failure

**Diagnostic Report:**
```markdown
# CI Failure Diagnostic Report

**Run ID:** 22124253398  
**Date:** 2026-02-18T03:09:44Z  
**Total Failures:** 25

## Root Causes Identified

### RC-1: Missing @runtime_checkable on Protocol Classes (Priority: P1)
- **Affected Tests:** 3 (test_minilm_forward_shape, test_telemetry_ndjson_disable_env, test_telemetry_json_disable_env)
- **Root Cause:** Protocol classes used with isinstance() lack @runtime_checkable decorator
- **Fix Strategy:** Add @runtime_checkable decorator to all Protocol definitions
- **Estimated Fix Time:** 15 minutes

### RC-2: torch.__spec__ Not Set (Priority: P0)
- **Affected Tests:** 2 (test_build_codex_model_accepts_torch_dtype, test_build_codex_model_accepts_string_dtype)
- **Root Cause:** Test environment initialization issue with PyTorch
- **Fix Strategy:** Mock torch.__spec__ in conftest.py or update test setup
- **Estimated Fix Time:** 10 minutes

...
```

### 4. Automated Fix Implementation

**Fix Strategies by Pattern:**

#### Strategy 1: Protocol isinstance Fixes
```python
# File: src/codex/contracts.py
from typing import Protocol
# ADD:
from typing import runtime_checkable

# BEFORE:
class ConfigProtocol(Protocol):
    def get(self, key: str) -> Any: ...

# AFTER:
@runtime_checkable
class ConfigProtocol(Protocol):
    def get(self, key: str) -> Any: ...
```

#### Strategy 2: Import/Dependency Fixes
```python
# Detect missing imports
# Add try/except with pytest.skip for optional dependencies
try:
    import torch
except ImportError:
    pytest.skip("torch not installed", allow_module_level=True)
```

#### Strategy 3: Timeout Optimization
```yaml
# Increase workflow timeout
- name: Run validation
  timeout-minutes: 20  # Increased from 15

# Or add test markers
@pytest.mark.timeout(120)  # Extend timeout for slow test
def test_long_running_operation():
    ...
```

#### Strategy 4: Mock Fixes
```python
# BEFORE: MagicMock causes type issues
mock_torch = MagicMock()

# AFTER: Proper spec or manual mock
mock_torch = MagicMock(spec=torch)
mock_torch.__version__ = "2.0.0"
```

**Implementation Process:**
1. Generate fix code for each root cause
2. Apply fixes in priority order (P0 → P1 → P2)
3. Commit each category separately for traceability
4. Run self-validation after each commit

### 5. Self-Validation Process

**Using Self-CI Script:**

The agent uses the `.codex/scripts/self_ci_validation.sh` script to validate fixes before pushing:

```bash
# After implementing fixes
bash .codex/scripts/self_ci_validation.sh quick

# Analyze results
if [ $? -eq 0 ]; then
    echo "✅ Fixes validated - ready for CI push"
    git push
else
    echo "❌ Self-validation failed - investigating..."
    # Review self-CI report
    cat .codex/self_ci_reports/self_ci_quick_*.md
fi
```

**Validation Workflow:**

1. **Environment Check** - Verify Python version, dependencies match CI
2. **Test Collection** - Ensure all tests can be collected (no import errors)
3. **Targeted Test Run** - Run only tests that were failing
4. **Full Suite Run** - Run complete test group (quick/slow/integration)
5. **Regression Check** - Verify no new failures introduced
6. **Coverage Analysis** - Track progress toward coverage targets
7. **Timeout Validation** - Ensure execution time within CI limits

**Validation Report:**
```markdown
# Self-Validation Report

**Fix Category:** Protocol isinstance  
**Tests Fixed:** 3  
**Validation Status:** ✅ PASSED

## Before Fix
- Total Failures: 25
- Protocol Errors: 3
- Execution Time: 13m 24s

## After Fix
- Total Failures: 22 (-3) ✅
- Protocol Errors: 0 (-3) ✅
- Execution Time: 12m 58s ✅

## Regression Check
- New Failures: 0 ✅
- Tests Passing: 56/68 (82.4%)
- Progress: +3 tests toward Phase 2 target

## Recommendation
✅ Ready for CI push - all validations passed
```

### 6. Comprehensive Documentation

**Documentation Artifacts:**

1. **Failure Tracking Log**
   - `.codex/CI_FAILURE_TRACKING_LOG.md`
   - Chronological record of all failures and fixes

2. **Pattern Library**
   - `.codex/CI_FAILURE_PATTERNS.md`
   - Known patterns with fix strategies

3. **Fix Implementation Report**
   - `.codex/ci_analysis/[run_id]/fix_report.md`
   - Detailed report for each CI run

4. **Validation Results**
   - `.codex/self_ci_reports/self_ci_[group]_[timestamp].md`
   - Local validation results

5. **Memory Storage**
   - Store patterns in agent memory for future reference
   - Track success rate of fix strategies

---

## 🔄 Agent Workflow

### Complete Resolution Cycle

```mermaid
graph TD
    A[User Provides CI Failure Links] --> B[Parse URLs & Extract IDs]
    B --> C[Fetch Logs & Artifacts]
    C --> D[Analyze Failure Patterns]
    D --> E[Generate Diagnostic Report]
    E --> F[Identify Root Causes]
    F --> G[Prioritize Fixes P0→P1→P2]
    G --> H[Implement Fix Category 1]
    H --> I[Self-Validate Fix]
    I --> J{Validation Pass?}
    J -->|Yes| K[Commit Fix]
    J -->|No| L[Adjust Fix & Retry]
    L --> I
    K --> M{More Fix Categories?}
    M -->|Yes| H
    M -->|No| N[Final Full Suite Validation]
    N --> O[Push to GitHub]
    O --> P[Monitor New CI Run]
    P --> Q{CI Pass?}
    Q -->|Yes| R[Update Documentation & Complete]
    Q -->|No| S[Analyze New Failures]
    S --> C
```

### Detailed Steps

#### Step 1: Input Processing (2-3 minutes)

**Input:**
```
@copilot ci-failure-resolution-agent
- https://github.com/Aries-Serpent/_codex_/actions/runs/22124253398
```

**Actions:**
1. Parse GitHub Actions URLs
2. Extract repository, run ID, job IDs
3. Validate access to repository and workflows
4. Create analysis directory structure

**Output:**
```
📁 Analysis directory created: .codex/ci_analysis/22124253398/
🔍 Identified 4 failing jobs
✅ Repository access validated
```

#### Step 2: Log & Artifact Retrieval (3-5 minutes)

**Actions:**
1. Use GitHub MCP tools to download logs:
   ```python
   github-mcp-server-get_job_logs(
       owner="Aries-Serpent",
       repo="_codex_",
       job_id=63950783741,
       return_content=True,
       tail_lines=10000
   )
   ```

2. Download artifacts via GitHub API
3. Store all data locally
4. Generate metadata file

**Output:**
```
📥 Downloaded 4 job logs (Total: 2.3 MB)
📦 Downloaded 3 artifacts (Total: 15.7 MB)
💾 Metadata saved to metadata.json
```

#### Step 3: Pattern Analysis (5-7 minutes)

**Actions:**
1. Parse all log files for error patterns
2. Extract test names, error messages, stack traces
3. Categorize by pattern type
4. Cluster similar failures
5. Calculate priority scores

**Pattern Detection Code:**
```python
import re

PATTERNS = {
    'protocol_isinstance': re.compile(r"isinstance.*Protocol.*must be a type"),
    'import_error': re.compile(r"(ImportError|ModuleNotFoundError): (.+)"),
    'timeout': re.compile(r"Timeout.*(\d+)s"),
    'assertion': re.compile(r"AssertionError: assert (.+) == (.+)"),
    'attribute': re.compile(r"AttributeError: '(.+)' object has no attribute '(.+)'"),
}

def analyze_log(log_content):
    failures = []
    for line in log_content.split('\n'):
        for pattern_name, pattern_re in PATTERNS.items():
            match = pattern_re.search(line)
            if match:
                failures.append({
                    'type': pattern_name,
                    'line': line,
                    'groups': match.groups()
                })
    return failures
```

**Output:**
```
🔍 Pattern Analysis Complete
├── Protocol isinstance: 3 failures
├── Import errors: 2 failures
├── Timeout issues: 1 failure
├── Assertion failures: 12 failures
├── Attribute errors: 4 failures
└── Type errors: 3 failures

Total unique root causes: 8
```

#### Step 4: Root Cause Diagnosis (3-5 minutes)

**Actions:**
1. For each pattern, trace to source code
2. Check historical memory for similar issues
3. Identify dependencies between failures
4. Calculate impact and priority
5. Generate diagnostic report

**Diagnostic Algorithm:**
```python
def diagnose_root_cause(pattern_type, failures):
    """
    Diagnose root cause for a failure pattern.
    
    Returns:
    {
        'root_cause': str,
        'affected_tests': list,
        'source_files': list,
        'fix_strategy': str,
        'priority': str,
        'estimated_time': int
    }
    """
    if pattern_type == 'protocol_isinstance':
        # Find Protocol classes without @runtime_checkable
        protocols = find_protocol_classes(failures)
        return {
            'root_cause': f'Missing @runtime_checkable on {len(protocols)} Protocol classes',
            'affected_tests': [f['test'] for f in failures],
            'source_files': [p['file'] for p in protocols],
            'fix_strategy': 'Add @runtime_checkable decorator',
            'priority': 'P1',
            'estimated_time': 15
        }
    # ... more patterns
```

**Output:**
```markdown
# Diagnostic Report - 22124253398

## RC-1: Missing @runtime_checkable (P1)
- Affected: 3 tests
- Files: src/codex/contracts.py, src/codex/api.py
- Fix: Add @runtime_checkable decorator
- Time: 15 min

## RC-2: PyTorch __spec__ (P0)
- Affected: 2 tests
- Files: tests/test_codex_model_dtype.py
- Fix: Mock torch.__spec__ in conftest
- Time: 10 min
```

#### Step 5: Fix Implementation (20-40 minutes)

**Actions:**
1. Sort root causes by priority (P0 → P1 → P2)
2. For each root cause:
   a. Generate fix code
   b. Apply fix to source/test files
   c. Run self-validation
   d. If validation passes → commit
   e. If validation fails → adjust and retry (max 3 attempts)

**Fix Implementation Code:**
```python
def implement_fix(root_cause):
    """
    Implement fix for a diagnosed root cause.
    """
    fix_strategy = root_cause['fix_strategy']
    
    if fix_strategy == 'Add @runtime_checkable decorator':
        for file_path in root_cause['source_files']:
            add_runtime_checkable_decorator(file_path)
        
    elif fix_strategy == 'Mock torch.__spec__':
        update_conftest_with_torch_mock()
    
    # ... more strategies
    
    # Self-validate
    validation_result = run_self_validation(
        test_group='quick',
        targeted_tests=root_cause['affected_tests']
    )
    
    if validation_result['status'] == 'PASSED':
        commit_fix(root_cause)
        return {'status': 'SUCCESS', 'validation': validation_result}
    else:
        return {'status': 'FAILED', 'validation': validation_result}
```

**Output:**
```
🔧 Implementing fixes (Priority order)...

✅ RC-1 (P0): PyTorch __spec__ mock
   - Applied fix to tests/conftest.py
   - Self-validation: PASSED (2/2 tests fixed)
   - Committed: abc1234

✅ RC-2 (P1): @runtime_checkable decorators  
   - Applied fix to 2 files
   - Self-validation: PASSED (3/3 tests fixed)
   - Committed: def5678

⏭️  RC-3 (P2): Assertion logic (deferred - manual review needed)
```

#### Step 6: Full Validation (10-15 minutes)

**Actions:**
1. Run complete self-CI validation suite
2. Compare before/after metrics
3. Check for regressions
4. Verify coverage progress
5. Generate validation report

**Validation Command:**
```bash
bash .codex/scripts/self_ci_validation.sh quick
```

**Output:**
```
📊 Final Validation Results

Before Fixes:
- Total Failures: 25
- Tests Passing: 53/68 (77.9%)
- Execution Time: 13m 24s

After Fixes:
- Total Failures: 20 (-5) ✅
- Tests Passing: 58/68 (85.3%) ✅
- Execution Time: 12m 41s ✅

Regressions: 0 ✅
Coverage Progress: Phase 2 target achieved (85.3%)
```

#### Step 7: Push & Monitor (5-10 minutes)

**Actions:**
1. Push all commits to GitHub
2. Wait for CI workflow to trigger
3. Monitor workflow execution
4. If CI fails, download new logs and repeat cycle
5. If CI passes, update documentation and complete

**Monitoring Code:**
```bash
# Push changes
git push origin [branch]

# Monitor CI
gh run watch

# Check status
gh pr checks [pr_number]
```

**Output:**
```
🚀 Pushed 2 commits to copilot/sub-pr-3248-again
⏳ Monitoring CI run: 22125000000
✅ CI validation (quick): PASSED (10m 23s)
✅ CI validation (slow): PASSED (6m 14s)
✅ All checks passing - resolution complete
```

#### Step 8: Documentation & Completion (5 minutes)

**Actions:**
1. Update `.codex/CI_FAILURE_TRACKING_LOG.md`
2. Add patterns to `.codex/CI_FAILURE_PATTERNS.md`
3. Store learnings in agent memory
4. Generate completion report
5. Post summary comment to PR

**Completion Report:**
```markdown
# CI Failure Resolution - Complete ✅

**Run ID:** 22124253398  
**Resolution Time:** 45 minutes  
**Fixes Applied:** 5 root causes  
**Tests Fixed:** 5 (+7.4% coverage)

## Summary

Starting from 77.9% (53/68 tests), achieved 85.3% (58/68 tests) through:
- 2 Protocol isinstance fixes (P1)
- 1 PyTorch __spec__ mock (P0)
- 2 Assertion fixes (P2)

## CI Status
- ✅ Resilient Validation (quick): PASSED
- ✅ Resilient Validation (slow): PASSED
- ✅ All checks green

## Next Steps
- Ready for PR merge
- 10 tests remaining for future work
```

---

## 📊 Agent Metrics & Success Criteria

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Time to First Fix** | < 15 min | Time from activation to first commit |
| **Total Resolution Time** | < 60 min | Time to all fixes applied and validated |
| **Fix Success Rate** | > 80% | % of fixes that pass self-validation |
| **CI Pass Rate** | > 90% | % of pushed fixes that pass CI |
| **Regression Rate** | < 5% | % of fixes that introduce new failures |
| **Pattern Recognition** | > 95% | % of known patterns correctly identified |

### Success Criteria

**Must Have:**
- ✅ Fetch all logs and artifacts from provided URLs
- ✅ Identify at least 80% of failure patterns
- ✅ Implement fixes for P0 and P1 issues
- ✅ Self-validate all fixes before push
- ✅ Document all failures and resolutions
- ✅ Monitor CI after push

**Should Have:**
- ✅ Fix P2 issues when straightforward
- ✅ Store patterns in memory for future use
- ✅ Provide estimated time for each fix
- ✅ Generate actionable recommendations

**Nice to Have:**
- ⭐ Predict CI failures before push
- ⭐ Suggest preventive refactorings
- ⭐ Auto-create follow-up issues for complex problems

---

## 🧠 Memory & Learning

### Pattern Library Storage

**Storage Format:**
```json
{
  "pattern_id": "protocol_isinstance_001",
  "pattern_type": "Protocol isinstance",
  "detection_regex": "isinstance.*Protocol.*must be a type",
  "fix_strategy": "add_runtime_checkable_decorator",
  "success_rate": 0.95,
  "occurrences": 23,
  "last_seen": "2026-02-18T03:09:44Z",
  "example_fix": {
    "before": "class ConfigProtocol(Protocol):",
    "after": "@runtime_checkable\nclass ConfigProtocol(Protocol):"
  }
}
```

**Memory Integration:**
```python
# Store successful fix pattern
store_memory(
    subject="CI failure pattern - Protocol isinstance",
    fact="Protocol classes used with isinstance() require @runtime_checkable decorator. Affects 23 historical failures with 95% fix success rate.",
    citations="PR #3248 commits abc1234, def5678 (2026-02-18)",
    reason="This pattern repeats frequently across test suite. Storing fix strategy prevents future iterations and enables quick resolution.",
    category="testing_patterns"
)
```

### Learning Feedback Loop

1. **Pattern Detection Accuracy** - Track which patterns were correctly identified
2. **Fix Success Rate** - Measure which fix strategies work best
3. **Time Estimation** - Improve time estimates based on actual fix duration
4. **Regression Analysis** - Learn which fix types introduce regressions
5. **CI Correlation** - Compare self-validation results with actual CI outcomes

---

## 🔌 Integration Points

### GitHub MCP Tools

**Required Tools:**
- `github-mcp-server-actions_list` - List workflow runs
- `github-mcp-server-actions_get` - Get workflow/job details
- `github-mcp-server-get_job_logs` - Download job logs
- `github-mcp-server-list_pull_requests` - Get PR context
- `github-mcp-server-pull_request_read` - Read PR details

### Custom Scripts

**Self-CI Validation:**
- `.codex/scripts/self_ci_validation.sh` - Local CI simulation

**Pattern Analysis:**
- `.codex/scripts/ci_pattern_analyzer.py` - Pattern detection script

**Artifact Processing:**
- `.codex/scripts/process_ci_artifacts.sh` - Extract and analyze artifacts

### External APIs

**GitHub Actions API:**
- Download workflow run artifacts
- Rerun failed workflows
- Get workflow run usage statistics

---

## 🎓 Usage Examples

### Example 1: Quick Fix Cycle

```
User: @copilot Fix failing CI: https://github.com/Aries-Serpent/_codex_/actions/runs/22124253398

Agent:
✅ Activated CI Failure Resolution Agent
📥 Downloading logs from run 22124253398...
🔍 Analyzing 4 failed jobs...

Pattern Analysis Complete:
- Protocol isinstance: 3 failures (P1)
- PyTorch __spec__: 2 failures (P0)
- Timeout: 1 failure (P0)

Implementing fixes (priority order)...
✅ RC-1 (P0): PyTorch __spec__ mock - FIXED
✅ RC-2 (P1): @runtime_checkable - FIXED
⚠️  RC-3 (P0): Timeout - Manual investigation needed

Self-Validation Results:
- Tests fixed: 5/6 (83% success rate)
- New failures: 0
- Coverage: 58/68 (85.3%) ✅

🚀 Pushing fixes to GitHub...
⏳ Monitoring new CI run...
✅ CI PASSED - All checks green

📝 Resolution complete in 42 minutes
```

### Example 2: Complex Multi-Pattern Fix

```
User: @copilot ci-failure-resolution-agent analyze and fix PR #3248 failures

Agent:
✅ Detected 15 failing checks on PR #3248
📥 Fetching logs from 6 workflow runs...
🔍 Analyzing 25 test failures...

Root Causes Identified:
1. RC-1 (P0): Missing dependencies (5 tests)
2. RC-2 (P1): Protocol isinstance (3 tests)
3. RC-3 (P1): Mock issues (4 tests)
4. RC-4 (P2): Assertion logic (8 tests)
5. RC-5 (P2): Timeout (5 tests)

Fix Strategy:
- Phase 1: Dependencies + Protocol (P0-P1) → 8 tests
- Phase 2: Mocks (P1) → 4 tests
- Phase 3: Assertions (P2, manual review) → 8 tests

Executing Phase 1...
✅ Installed missing dependencies
✅ Added @runtime_checkable to 3 Protocols
✅ Self-validation: 8/8 tests passing
✅ Committed: Phase 1 fixes (12 tests, 80.9% coverage)

Executing Phase 2...
✅ Fixed MagicMock spec issues
✅ Self-validation: 4/4 tests passing
✅ Committed: Phase 2 fixes (16 tests, 85.3% coverage)

Phase 3 Analysis:
- 8 assertion failures require manual review
- Issues documented in .codex/ci_analysis/22124253398/deferred.md

🚀 Pushed 2 commits with 12 fixes
⏳ CI in progress...
✅ All checks passing

📝 Summary:
- Fixed: 12/25 tests (48% fix rate)
- Deferred: 8 tests for manual review
- Coverage: 58/68 (85.3%) - Phase 2 target achieved ✅
```

---

## 🛠️ Agent Configuration

### Configuration File

**Location:** `.github/agents/ci-failure-resolution-agent.md`

**Settings:**
```yaml
agent_name: ci-failure-resolution-agent
version: 1.0.0
priority: P0
auto_activate: false  # Manual activation only
max_fix_attempts: 3
validation_required: true
auto_push: false  # Require user confirmation before push

thresholds:
  max_resolution_time: 60  # minutes
  min_fix_success_rate: 0.8
  max_regression_rate: 0.05
  ci_timeout_warning: 780  # seconds (13 minutes)

patterns:
  enabled: all
  custom_patterns_file: .codex/ci_failure_patterns.json

self_validation:
  script: .codex/scripts/self_ci_validation.sh
  required_test_groups:
    - quick
  optional_test_groups:
    - slow
    - integration

documentation:
  tracking_log: .codex/CI_FAILURE_TRACKING_LOG.md
  pattern_library: .codex/CI_FAILURE_PATTERNS.md
  analysis_dir: .codex/ci_analysis/

notifications:
  post_pr_comment: true
  ping_on_completion: true
  ping_on_failure: true
```

---

## 📚 Documentation Requirements

### Tracking Log Format

**File:** `.codex/CI_FAILURE_TRACKING_LOG.md`

```markdown
# CI Failure Tracking Log

## Run 22124253398 - 2026-02-18T03:09:44Z

**PR:** #3248  
**Branch:** 0D_base_  
**Triggering Commit:** abc1234

### Failures (25 total)

#### Protocol isinstance (3 tests)
- test_minilm_forward_shape
- test_telemetry_ndjson_disable_env
- test_telemetry_json_disable_env

**Root Cause:** Missing @runtime_checkable  
**Fix:** Added decorator to 3 Protocol classes  
**Commit:** def5678  
**Status:** ✅ FIXED  
**Validation:** Self-CI passed, CI passed

...
```

### Pattern Library Format

**File:** `.codex/CI_FAILURE_PATTERNS.md`

```markdown
# CI Failure Pattern Library

## Pattern: Protocol isinstance Error

**ID:** protocol_isinstance_001  
**Priority:** P1  
**Detection:** `isinstance.*Protocol.*must be a type`  
**Occurrences:** 23 (15 fixed, 95% success rate)

### Description
Protocol classes used with isinstance() checks fail unless decorated with @runtime_checkable.

### Fix Strategy
1. Locate Protocol class definition
2. Add import: `from typing import runtime_checkable`
3. Add decorator: `@runtime_checkable` above class definition

### Example
```python
# Before
from typing import Protocol

class ConfigProtocol(Protocol):
    def get(self, key: str) -> Any: ...

# After
from typing import Protocol, runtime_checkable

@runtime_checkable
class ConfigProtocol(Protocol):
    def get(self, key: str) -> Any: ...
```

### Historical Fixes
- PR #3248 (2026-02-18): 3 occurrences - abc1234
- PR #3178 (2026-02-15): 2 occurrences - xyz9876
```

---

## 🚀 Deployment & Activation

### Setup Steps

1. **Create Agent File:**
   ```bash
   cp .github/agents/ci-failure-resolution-agent.md .github/agents/
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements-ci-agent.txt
   chmod +x .codex/scripts/self_ci_validation.sh
   ```

3. **Configure GitHub Access:**
   - Ensure GitHub MCP server is configured
   - Verify workflow read permissions

4. **Test Agent:**
   ```bash
   @copilot ci-failure-resolution-agent test-mode
   ```

### Activation

**Manual Activation:**
```
@copilot ci-failure-resolution-agent [workflow_run_urls]
```

**Auto-Detection Activation:**
```
@copilot fix-ci [pr_number]
```

---

## 📈 Future Enhancements

### Version 1.1 (Next Quarter)

- **Predictive Failure Detection** - Analyze code changes to predict CI failures
- **Parallel Fix Execution** - Apply multiple independent fixes simultaneously
- **Smart Retry Logic** - Auto-retry flaky test failures
- **Performance Profiling** - Identify and optimize slow tests

### Version 2.0 (Future)

- **ML-Based Pattern Recognition** - Use machine learning for pattern detection
- **Auto-Refactoring** - Suggest code refactorings to prevent failures
- **Cross-Repo Learning** - Share patterns across multiple repositories
- **Visual Dashboard** - Real-time failure tracking and metrics

---

## 📞 Support & Escalation

**For Complex Issues:**
- Escalate to: @mbaetiong
- Create issue with tag: [CI-AGENT-HELP]
- Include: Run ID, logs, attempted fixes

**For Pattern Additions:**
- Submit PR to `.codex/ci_failure_patterns.json`
- Include: Detection regex, fix strategy, examples

**For Agent Updates:**
- Submit PR to `.github/agents/ci-failure-resolution-agent.md`
- Include: Version bump, changelog entry

---

## ✅ Agent Activation Checklist

Before activating this agent, ensure:

- [ ] GitHub MCP server is configured and accessible
- [ ] Self-CI validation script exists and is executable
- [ ] Repository has write access for commits
- [ ] CI workflows are configured and running
- [ ] Tracking log and pattern library files exist
- [ ] Agent has been tested in dry-run mode

---

**Agent Status:** ✅ READY FOR DEPLOYMENT  
**Last Updated:** 2026-02-18T04:00:00Z  
**Maintainer:** GitHub Copilot + Human Oversight (@mbaetiong)
