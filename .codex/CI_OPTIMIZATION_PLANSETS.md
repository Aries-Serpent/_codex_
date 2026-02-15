# CI Optimization Plansets - PR #3248 Analysis
> Generated: 2026-02-15T10:30:00Z  
> Updated: 2026-02-15T11:15:00Z (Phase 1 IMPLEMENTED)  
> Based on: CI_FAILURE_PATTERN_ANALYSIS.md  
> Scope: Large codebase CI optimization for _codex_ repository

---

## 🎯 Implementation Status

**Phase 1: Foundation Components** - ✅ **IMPLEMENTED** (2026-02-15)
- ✅ PR Size Analyzer Workflow (`.github/workflows/pr-size-analyzer.yml`)
- ✅ Telemetry Collection Script (`scripts/ci/collect_telemetry.py`)
- ✅ Auto-Fix with Rollback (`scripts/ci/auto_fix_with_rollback.py`)
- ✅ Coverage Timeout Guards (`.github/workflows/coverage-with-timeout.yml`)
- ✅ Validation Test Suite (53+ tests in `tests/ci/`)

**Commit:** `2bb06bfc` - "feat: Implement Phase 1 CI optimization components (all 5 components)"  
**Documentation:** [`docs/ci/IMPLEMENTATION_LOG.md`](../docs/ci/IMPLEMENTATION_LOG.md)

**Phase 2: Core Improvements** - ✅ **IMPLEMENTED** (2026-02-15)
- ✅ Progressive Validation Suite (`.github/workflows/progressive-validation.yml`)
- ✅ Workflow Orchestrator (`scripts/ci/workflow_orchestrator.py`)
- ✅ Telemetry Collection Workflow (`.github/workflows/telemetry-collection.yml`)
- ✅ Test Suite (27+ tests in `tests/ci/test_workflow_orchestrator.py`)

**Commit:** `e369c2b` - "feat: Implement Phase 2 core improvements (progressive validation + telemetry orchestration)"  
**Documentation:** Updated in [`docs/ci/IMPLEMENTATION_LOG.md`](../docs/ci/IMPLEMENTATION_LOG.md)

---

## Overview

This document provides 5 comprehensive plansets for optimizing CI workflows based on patterns identified in PR #3248 failure analysis. Each planset includes problem statement, solution design, implementation steps, success metrics, and risk mitigation.

**Planset Priority**:
1. 🔴 **Planset 1** - Auto-Fix Loop Resolution (CRITICAL - blocks merges) - ✅ **Phase 1 COMPLETE**
2. 🔴 **Planset 3** - Coverage Generation Optimization (CRITICAL - resource exhaustion) - ✅ **Phase 1 COMPLETE**
3. 🟠 **Planset 2** - Test Infrastructure Stabilization (HIGH - systemic failures) - ✅ **Phase 2 COMPLETE**
4. 🟡 **Planset 4** - File System Operation Optimization (MEDIUM - large PR impact) - ⏳ Phase 3
5. 🟡 **Planset 5** - Large PR Workflow Strategy (MEDIUM - architectural) - ✅ **Phase 1 COMPLETE**

---

## Planset 1: Auto-Fix Detection-Remediation Loop Resolution 🔴

### Problem Statement

**Current State**:
- Auto-fix workflows detect linting/formatting issues
- But fail to apply fixes automatically
- 100% failure rate across 3 analyzed runs
- Blocks PR merges requiring manual intervention

**Impact**:
- **User Friction**: Manual fixes required despite automation
- **Merge Delay**: PRs blocked unnecessarily
- **Token Waste**: Auto-fix runs but doesn't deliver value

### Root Cause Analysis

**Hypothesis** (ordered by likelihood):
1. **Git state conflicts**: Auto-fix can't commit changes due to detached HEAD or dirty working tree
2. **Permission issues**: Script can't write to files or push changes
3. **Edge case handling**: Remediation logic encounters unexpected file formats
4. **Exit code logic**: Script exits with failure even when fixes applied

**Evidence Needed**:
- Full job logs from failed auto-fix runs
- Git state inspection at failure point
- File permission checks
- Script error messages

### Solution Design

**Architecture**:
```
┌─────────────────────────────────────────┐
│  Auto-Fix Workflow (Enhanced)           │
├─────────────────────────────────────────┤
│  1. Pre-Flight Checks                   │
│     - Git state validation              │
│     - File permissions check            │
│     - Branch protection status          │
│                                         │
│  2. Issue Detection (existing)          │
│     - Run ruff, black, isort            │
│     - Collect issues                    │
│                                         │
│  3. Remediation (ENHANCED)              │
│     - Apply fixes with error handling   │
│     - Validate each fix                 │
│     - Rollback on failure               │
│                                         │
│  4. Commit & Push (ENHANCED)            │
│     - Create commit with detailed msg   │
│     - Push with retry logic             │
│     - Update PR status                  │
│                                         │
│  5. Verification                        │
│     - Re-run checks                     │
│     - Confirm clean state               │
│     - Report success/failure            │
└─────────────────────────────────────────┘
```

### Implementation Steps

#### Phase 1: Diagnostics (Phase 1, Steps 1-2)

**Step 1.1**: Add comprehensive logging to existing auto-fix script
```python
# scripts/ci/auto_fix_common_issues.py
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def apply_fixes():
    logger.info("Starting fix application")
    logger.debug(f"Git state: {get_git_status()}")
    logger.debug(f"Working directory: {os.getcwd()}")
    # ... existing logic with debug logs
```

**Step 1.2**: Capture full job logs for next auto-fix failure
- Use GitHub Actions artifact to store full log
- Add log level escalation on error

**Step 1.3**: Analyze failure logs
- Identify exact failure point
- Determine root cause category
- Document edge cases

#### Phase 2: Fix Implementation (Phase 1, Steps 3-5)

**Step 2.1**: Add pre-flight checks
```python
def pre_flight_checks():
    """Validate environment before attempting fixes"""
    checks = {
        'git_clean': is_git_clean(),
        'writable': are_files_writable(),
        'branch_valid': is_branch_valid(),
    }
    
    if not all(checks.values()):
        logger.error(f"Pre-flight failed: {checks}")
        return False
    
    return True
```

**Step 2.2**: Enhance remediation logic with error handling
```python
def apply_fix_with_rollback(file_path, fix_fn):
    """Apply fix with automatic rollback on error"""
    backup = create_backup(file_path)
    
    try:
        fix_fn(file_path)
        validate_syntax(file_path)  # Ensure file still valid
        return True
    except Exception as e:
        logger.error(f"Fix failed for {file_path}: {e}")
        restore_backup(backup)
        return False
```

**Step 2.3**: Improve commit/push logic
```python
def commit_and_push_fixes(changed_files):
    """Commit with retry logic and detailed messages"""
    if not changed_files:
        logger.info("No changes to commit")
        return True
    
    try:
        subprocess.run(['git', 'add'] + changed_files, check=True)
        subprocess.run([
            'git', 'commit', '-m',
            f'auto-fix: Applied fixes to {len(changed_files)} files\n\n' +
            '\n'.join(f'- {f}' for f in changed_files)
        ], check=True)
        
        # Retry push up to 3 times
        for attempt in range(3):
            try:
                subprocess.run(['git', 'push'], check=True)
                return True
            except subprocess.CalledProcessError:
                if attempt < 2:
                    time.sleep(5)
                    continue
                raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Commit/push failed: {e}")
        return False
```

#### Phase 3: Testing (Phase 2, Steps 1-2)

**Step 3.1**: Create test harness
```bash
# scripts/ci/test_auto_fix.sh
#!/bin/bash
# Test auto-fix in isolated environment

git checkout -b test-auto-fix
# Introduce known fixable issues
echo "import os" >> test_file.py  # Unused import
echo "x=1" >> test_file.py  # Missing spaces

# Run auto-fix
python scripts/ci/auto_fix_common_issues.py

# Verify fixes applied
if grep "import os" test_file.py; then
    echo "FAIL: Unused import not fixed"
    exit 1
fi

if grep "x=1" test_file.py; then
    echo "FAIL: Spacing not fixed"
    exit 1
fi

echo "PASS: Auto-fix working correctly"
```

**Step 3.2**: Test edge cases
- Syntax errors after fix application
- Git conflicts
- Permission denied scenarios
- Large file handling

#### Phase 4: Deployment (Phase 2, Steps 3-5)

**Step 4.1**: Update workflow YAML
```yaml
# .github/workflows/auto-fix.yml
name: Auto-Fix Common CI Issues

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  auto-fix:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Ensure write permission
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.CODEX_MASTER_KEY }}
          fetch-depth: 0  # Full history for better git operations
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff black isort
      
      - name: Run pre-flight checks
        run: python scripts/ci/auto_fix_common_issues.py --pre-flight
      
      - name: Apply fixes
        run: python scripts/ci/auto_fix_common_issues.py --apply
        continue-on-error: true  # Don't fail workflow on fix failure
      
      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: auto-fix-logs
          path: auto_fix.log
```

**Step 4.2**: Gradual rollout
- Deploy to test branch first
- Monitor 5-10 PRs
- Adjust based on success rate
- Roll out to all PRs

### Success Metrics

**Quantitative**:
- Auto-fix success rate: Target 90%+ (from current 0%)
- Mean time to fix: <2 minutes
- False positive rate: <5%

**Qualitative**:
- Zero manual fixes required for auto-fixable issues
- No complaints about auto-fix breaking code
- Positive user feedback on automation

**Monitoring**:
```python
# Add to auto-fix script
metrics = {
    'run_id': os.environ.get('GITHUB_RUN_ID'),
    'issues_detected': len(detected_issues),
    'fixes_applied': len(applied_fixes),
    'success': all_fixes_successful,
    'duration_seconds': end_time - start_time,
}

# Log to monitoring system
log_metrics('auto_fix', metrics)
```

### Risk Mitigation

**Risk 1**: Auto-fix breaks code
- **Mitigation**: Syntax validation after each fix
- **Rollback**: Automatic restore from backup
- **Detection**: Run tests after auto-fix

**Risk 2**: Git conflicts from concurrent pushes
- **Mitigation**: Retry logic with exponential backoff
- **Fallback**: Mark PR for manual review if retries exhausted

**Risk 3**: Permission issues
- **Mitigation**: Pre-flight permission check
- **Documentation**: Clear error messages for misconfiguration

### Cost-Benefit Analysis

**Implementation Cost**:
- Development: 3-5 steps (1 developer)
- Testing: 2-3 steps
- Total: ~1 phase engineering effort

**Benefit**:
- Eliminates manual fixes: ~15 min per iteration → 0 min
- Faster PR merges: ~30 min saved per iteration
- Better developer experience: Reduced frustration

**ROI**: Positive after ~20 iterations

---

## Planset 2: Test Infrastructure Stabilization 🟠

### Problem Statement

**Current State**:
- Resilient Validation Suite showing 100% failure rate
- Multiple test categories failing simultaneously (slow, integration, quick, documentation)
- Indicates systemic issue, not isolated test failures

**Impact**:
- No test coverage validation possible
- Unknown test pass/fail status
- Potential for shipping broken code

### Root Cause Analysis

**Hypothesis**:
1. **Import/dependency conflicts**: Tests can't import required modules
2. **conftest.py issues**: Shared fixtures breaking all test types
3. **Environment setup**: Missing system dependencies or wrong Python version
4. **Optional dependencies**: Tests failing when torch/transformers not available

**Evidence**:
- All test categories affected (not isolated)
- Failure pattern consistent across commits
- Likely happens early in test bootstrap phase

### Solution Design

**Architecture**: Progressive Test Isolation

```
┌───────────────────────────────────────────┐
│  Test Execution Strategy (Layered)        │
├───────────────────────────────────────────┤
│  Layer 1: Smoke Tests (Fast, No Deps)    │
│   - Import tests                          │
│   - Basic unit tests                      │
│   - Syntax validation                     │
│   ✓ Must pass before proceeding           │
│                                           │
│  Layer 2: Unit Tests (Module Isolated)    │
│   - Per-module test suites               │
│   - Mock external dependencies           │
│   - Parallel execution                    │
│   ⚠ Can partially fail                    │
│                                           │
│  Layer 3: Integration Tests               │
│   - Cross-module tests                   │
│   - Real dependencies                     │
│   - Sequential execution                  │
│   ⚠ Allowed to be flaky                   │
│                                           │
│  Layer 4: Slow Tests (Resource Intensive) │
│   - ML model tests                       │
│   - Large dataset tests                   │
│   - Performance tests                     │
│   ⚠ Optional on large PRs                 │
└───────────────────────────────────────────┘
```

### Implementation Steps

#### Phase 1: Diagnostic Collection (Phase 1)

**Step 1.1**: Add early failure detection
```python
# conftest.py
import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def pytest_sessionstart(session):
    """Log environment at test start"""
    logger.info("=" * 60)
    logger.info("Test Session Starting")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Path: {sys.path}")
    logger.info(f"CWD: {os.getcwd()}")
    
    # Test critical imports
    try:
        import torch
        logger.info(f"Torch: {torch.__version__}")
    except ImportError:
        logger.warning("Torch not available")
    
    try:
        import transformers
        logger.info(f"Transformers: {transformers.__version__}")
    except ImportError:
        logger.warning("Transformers not available")
    
    logger.info("=" * 60)
```

**Step 1.2**: Identify failing test category
```bash
# Run each category individually to isolate failure
pytest tests/ -m "quick" -v
pytest tests/ -m "slow" -v
pytest tests/ -m "integration" -v
```

#### Phase 2: Fix Implementation (Phase 2-3)

**Step 2.1**: Implement test layer separation
```yaml
# .github/workflows/resilient-validation.yml
name: Resilient Validation Suite

on: [pull_request]

jobs:
  smoke-tests:
    name: "Layer 1: Smoke Tests"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install pytest
      - run: pytest tests/ -m "smoke" --maxfail=1
      # Fail fast if imports broken
  
  unit-tests:
    name: "Layer 2: Unit Tests"
    needs: smoke-tests
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false  # Continue even if some fail
      matrix:
        module: [core, utils, mcp, rag, tokenization]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-test.txt
      - run: pytest tests/${{ matrix.module }}/ --maxfail=5
  
  integration-tests:
    name: "Layer 3: Integration Tests"
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/integration/ --maxfail=3
  
  slow-tests:
    name: "Layer 4: Slow Tests"
    needs: unit-tests
    runs-on: ubuntu-latest
    if: github.event.pull_request.changed_files < 100  # Skip on large PRs
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-ml-cpu.txt
      - run: pytest tests/ -m "slow" --timeout=600
```

**Step 2.2**: Add optional dependency handling
```python
# tests/utils/test_helpers.py
import pytest

def skip_if_missing(*packages):
    """Skip test if required packages not available"""
    missing = []
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        pytest.skip(f"Missing packages: {missing}")

# Usage in tests:
def test_torch_functionality():
    skip_if_missing('torch', 'transformers')
    import torch
    # ... test code
```

#### Phase 3: Parallel Execution (Phase 3)

**Step 3.1**: Implement pytest-xdist
```bash
# requirements-test.txt
pytest-xdist>=3.0

# Run tests in parallel
pytest tests/ -n auto  # Auto-detect CPU count
```

**Step 3.2**: Add test sharding for CI
```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: pytest tests/ --shard=${{ matrix.shard }}/4
```

### Success Metrics

**Target**:
- Smoke tests: 100% pass rate
- Unit tests: 95%+ pass rate
- Integration tests: 90%+ pass rate
- Slow tests: 85%+ pass rate (acceptable flakiness)

**Execution Time**:
- Smoke: <2 min
- Unit (parallel): <10 min
- Integration: <15 min
- Slow: <30 min

### Risk Mitigation

**Risk**: Test isolation breaks integration coverage
- **Mitigation**: Layer 3 runs full integration suite
- **Validation**: Smoke + Unit + Integration = comprehensive coverage

**Risk**: Parallel execution causes race conditions
- **Mitigation**: Isolate test data, use unique temp directories
- **Detection**: Monitor for flaky tests

---

## Planset 3: Coverage Generation Optimization 🔴

### Problem Statement

**Current State**:
- Coverage Report Generation job cancelled mid-execution
- 100% failure rate (2/2 runs analyzed)
- Other quality checks (linting) succeed
- Indicates timeout or resource exhaustion

**Impact**:
- No coverage metrics for PRs
- Can't track coverage trends
- Risk of coverage regression

### Root Cause Analysis

**Hypothesis** (ordered by likelihood):
1. **pytest-cov timeout**: Coverage collection hanging on large modules with complex imports
2. **Memory exhaustion**: Coverage data structure too large for runner
3. **Infinite loop**: Test code with infinite loop only triggered during coverage
4. **File I/O bottleneck**: Writing coverage data to disk too slow

**Evidence**:
- Job cancelled (not failed) = GitHub Actions timeout
- Other jobs in suite succeed = not a code issue
- Consistent across commits = environmental

### Solution Design

**Architecture**: Incremental Coverage with Caching

```
┌─────────────────────────────────────────┐
│  Coverage Strategy (Optimized)          │
├─────────────────────────────────────────┤
│  1. Change Detection                    │
│     - Identify changed files in PR      │
│     - Map to affected test files        │
│     - Focus coverage on changed areas   │
│                                         │
│  2. Incremental Coverage                │
│     - Run coverage only on PR changes   │
│     - Merge with baseline coverage      │
│     - Report delta (not full coverage)  │
│                                         │
│  3. Parallel Collection                 │
│     - Split tests into shards           │
│     - Collect coverage per shard        │
│     - Combine at end                    │
│                                         │
│  4. Timeout Protection                  │
│     - Set aggressive timeouts per shard │
│     - Skip problematic modules          │
│     - Report partial coverage           │
└─────────────────────────────────────────┘
```

### Implementation Steps

#### Phase 1: Timeout Protection (Phase 1, Steps 1-2)

**Step 1.1**: Add per-shard timeouts
```yaml
# .github/workflows/code-quality.yml
jobs:
  coverage:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Workflow-level timeout
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - name: Run coverage shard
        run: |
          timeout 420 pytest tests/ \  # 7 min per shard
            --cov=src \
            --cov-report=xml:coverage-${{ matrix.shard }}.xml \
            --shard=${{ matrix.shard }}/4
        continue-on-error: true  # Don't fail if one shard times out
      
      - name: Upload partial coverage
        uses: actions/upload-artifact@v3
        with:
          name: coverage-shard-${{ matrix.shard }}
          path: coverage-${{ matrix.shard }}.xml
```

**Step 1.2**: Combine partial results
```python
# scripts/ci/combine_coverage.py
from coverage import Coverage

def combine_shards(shard_files):
    """Combine coverage from multiple shards"""
    cov = Coverage()
    
    for shard_file in shard_files:
        if os.path.exists(shard_file):
            cov.combine([shard_file])
        else:
            print(f"Warning: Missing shard {shard_file}")
    
    cov.save()
    cov.xml_report(outfile='coverage-combined.xml')
    
    # Calculate coverage %
    total = cov.report()
    return total
```

#### Phase 2: Incremental Coverage (Phase 1, Steps 3-5)

**Step 2.1**: Detect changed files
```bash
# scripts/ci/detect_changes.sh
#!/bin/bash
# Get changed Python files in PR

git fetch origin main
git diff --name-only origin/main...HEAD | grep '\.py$' > changed_files.txt

# Map to test files
python scripts/ci/map_tests_to_changes.py changed_files.txt > tests_to_run.txt
```

**Step 2.2**: Run targeted coverage
```bash
# Only run tests for changed files
pytest $(cat tests_to_run.txt) --cov=src --cov-report=xml
```

**Step 2.3**: Calculate coverage delta
```python
# scripts/ci/coverage_delta.py
def calculate_delta(baseline_coverage, pr_coverage):
    """Calculate coverage change"""
    delta = {}
    
    for file in pr_coverage:
        baseline_pct = baseline_coverage.get(file, 0)
        pr_pct = pr_coverage.get(file, 0)
        delta[file] = pr_pct - baseline_pct
    
    return delta
```

#### Phase 3: Module Exclusion (Phase 2)

**Step 3.1**: Identify problematic modules
```bash
# Run coverage on each module individually
for module in src/*/; do
    echo "Testing $module"
    timeout 60 pytest tests/ --cov=$module || echo "$module TIMEOUT"
done
```

**Step 3.2**: Configure coverage exclusions
```ini
# .coveragerc
[run]
omit =
    */tests/*
    */experiments/*
    # Add modules that timeout:
    # src/problematic_module/*
```

### Success Metrics

**Target**:
- Coverage collection success rate: 95%+
- Collection time: <15 min (from current timeout at 30+ min)
- Coverage delta reported: 100% of PRs

**Quality**:
- Coverage accuracy: ±2% of full coverage run
- False positive rate: <1%

### Risk Mitigation

**Risk**: Incremental coverage misses regressions
- **Mitigation**: Run full coverage per-phase on main branch
- **Validation**: Compare incremental vs full per-session

**Risk**: Shard timeouts cause incomplete data
- **Mitigation**: Report partial coverage with warning
- **Fallback**: Manual coverage check for critical PRs

---

## Planset 4: File System Operation Optimization 🟡

### Problem Statement

**Current State**:
- Art_Root Organization Validation timing out
- Pre-Move Validation job cancelled
- Subsequent validation steps skipped
- 100% failure rate (2/2 runs)

**Impact**:
- File integrity not verified before large refactors
- Risk of broken imports after merge
- Incomplete validation of file moves

### Root Cause Analysis

**Hypothesis**:
1. **O(n²) complexity**: Validation logic checking every file against every other file
2. **Blocking I/O**: Synchronous file operations on large directory tree
3. **No early termination**: Validation continues even after finding issues

**Evidence**:
- Timeout (not failure) = computation taking too long
- Pre-move phase = initial file system scan
- Large codebase with 1000+ Python files

### Solution Design

**Architecture**: Async File Operations with Smart Caching

```
┌──────────────────────────────────────────┐
│  File Validation (Optimized)             │
├──────────────────────────────────────────┤
│  1. File System Cache                    │
│     - Build file tree once               │
│     - Cache inode/stat information       │
│     - Reuse across validation steps      │
│                                          │
│  2. Async I/O                            │
│     - Use asyncio for file operations    │
│     - Parallel validation checks         │
│     - Non-blocking directory traversal   │
│                                          │
│  3. Smart Filtering                      │
│     - Only validate changed files        │
│     - Skip .git, node_modules, __pycache__│
│     - Early termination on critical errors│
│                                          │
│  4. Progress Reporting                   │
│     - Real-time progress updates         │
│     - Timeout warnings                   │
│     - Estimated completion time          │
└──────────────────────────────────────────┘
```

### Implementation Steps

#### Phase 1: Async File Operations (Phase 1)

**Step 1.1**: Convert to async
```python
# scripts/validation/root_org_validator.py
import asyncio
import aiofiles
from pathlib import Path

async def validate_file_async(file_path: Path):
    """Async file validation"""
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()
        # Validation logic
        return validate_content(content)

async def validate_directory_async(dir_path: Path):
    """Validate all files in directory concurrently"""
    files = list(dir_path.rglob('*.py'))
    
    # Process files in parallel (limit concurrency)
    semaphore = asyncio.Semaphore(50)  # Max 50 concurrent
    
    async def bounded_validate(file_path):
        async with semaphore:
            return await validate_file_async(file_path)
    
    tasks = [bounded_validate(f) for f in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

**Step 1.2**: Add progress reporting
```python
from tqdm.asyncio import tqdm

async def validate_with_progress(files):
    """Validate with progress bar"""
    with tqdm(total=len(files)) as pbar:
        for file in files:
            result = await validate_file_async(file)
            pbar.update(1)
            yield result
```

#### Phase 2: Smart Caching (Phase 1-2)

**Step 2.1**: Build file system cache
```python
# scripts/validation/fs_cache.py
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class FileInfo:
    path: Path
    size: int
    mtime: float
    is_python: bool

class FileSystemCache:
    def __init__(self, root: Path):
        self.root = root
        self._cache = {}
        self._build_cache()
    
    def _build_cache(self):
        """Build cache of all relevant files"""
        for path in self.root.rglob('*'):
            if self._should_cache(path):
                stat = os.stat(path)
                self._cache[path] = FileInfo(
                    path=path,
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    is_python=path.suffix == '.py'
                )
    
    def _should_cache(self, path: Path) -> bool:
        """Filter out irrelevant paths"""
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv'}
        return not any(part in exclude_dirs for part in path.parts)
    
    def get_python_files(self):
        """Get all cached Python files"""
        return [info for info in self._cache.values() if info.is_python]
```

**Step 2.2**: Use cache for validation
```python
async def validate_with_cache(cache: FileSystemCache):
    """Use cache to avoid repeated file system access"""
    python_files = cache.get_python_files()
    
    # Now validate only the filtered list
    results = await validate_directory_async(
        [f.path for f in python_files]
    )
    
    return results
```

#### Phase 3: Change-Based Validation (Phase 2)

**Step 3.1**: Detect changed files in PR
```python
def get_changed_files():
    """Get files changed in PR"""
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'origin/main...HEAD'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')

def validate_only_changes():
    """Validate only changed files"""
    changed = get_changed_files()
    changed_python = [f for f in changed if f.endswith('.py')]
    
    # Validate changed files + their imports
    all_to_validate = changed_python + get_import_dependencies(changed_python)
    
    return validate_files(all_to_validate)
```

### Success Metrics

**Target**:
- Validation completion rate: 95%+
- Validation time: <5 min (from current timeout at 30+ min)
- False positive rate: <2%

**Performance**:
- Files/second: 100+ (from current <10)
- Memory usage: <500 MB
- CPU usage: <80%

### Risk Mitigation

**Risk**: Async validation misses serial dependencies
- **Mitigation**: Validate imports after file validation
- **Test**: Comprehensive integration tests

**Risk**: Cache staleness
- **Mitigation**: Rebuild cache if files change during validation
- **Detection**: Compare mtime before/after

---

## Planset 5: Large PR Workflow Strategy 🟡

### Problem Statement

**Current State**:
- All workflows run on every PR, regardless of size
- Large PRs (100+ files) trigger all validation suites
- No differentiation between small bug fixes and major refactors
- Resource waste on comprehensive checks for small changes

**Impact**:
- Slow feedback for large PRs
- Resource exhaustion
- Developer frustration
- CI queue backlog

### Root Cause Analysis

**Current Workflow Triggers**:
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
```

**Problem**: No size-based differentiation

### Solution Design

**Architecture**: Progressive Validation Strategy

```
┌────────────────────────────────────────────┐
│  PR Size-Based Workflow Strategy           │
├────────────────────────────────────────────┤
│  Small PR (<20 files changed)              │
│   ✓ Full validation suite                  │
│   ✓ All tests                              │
│   ✓ Full coverage                          │
│   ⏱ Fast feedback: <15 min                 │
│                                            │
│  Medium PR (20-100 files)                  │
│   ✓ Smoke + Unit tests                     │
│   ✓ Incremental coverage                   │
│   ⚠ Integration tests (optional)           │
│   ⏱ Medium feedback: <30 min               │
│                                            │
│  Large PR (100+ files)                     │
│   ✓ Smoke tests only                       │
│   ✓ Critical path coverage                 │
│   ⚠ Full suite: nightly or on-demand       │
│   ⏱ Quick feedback: <10 min                │
│   📝 Manual: Request full validation        │
│                                            │
│  Refactor PR (500+ files)                  │
│   ✓ Import validation                      │
│   ✓ Syntax checks                          │
│   ⚠ Smoke tests per module                 │
│   📝 Manual: Staged validation             │
│   ⏱ Minimal: <5 min                        │
└────────────────────────────────────────────┘
```

### Implementation Steps

#### Phase 1: PR Size Detection (Phase 1)

**Step 1.1**: Create PR analyzer action
```yaml
# .github/workflows/pr-analyzer.yml
name: PR Analyzer

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  analyze:
    runs-on: ubuntu-latest
    outputs:
      pr_size: ${{ steps.size.outputs.category }}
      changed_files: ${{ steps.size.outputs.count }}
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Analyze PR size
        id: size
        run: |
          CHANGED=$(git diff --name-only origin/main...HEAD | wc -l)
          echo "count=$CHANGED" >> $GITHUB_OUTPUT
          
          if [ $CHANGED -lt 20 ]; then
            echo "category=small" >> $GITHUB_OUTPUT
          elif [ $CHANGED -lt 100 ]; then
            echo "category=medium" >> $GITHUB_OUTPUT
          elif [ $CHANGED -lt 500 ]; then
            echo "category=large" >> $GITHUB_OUTPUT
          else
            echo "category=refactor" >> $GITHUB_OUTPUT
          fi
```

#### Phase 2: Conditional Workflows (Phase 1-2)

**Step 2.1**: Update validation workflows
```yaml
# .github/workflows/resilient-validation.yml
name: Resilient Validation Suite

on:
  pull_request:

jobs:
  check-pr-size:
    uses: ./.github/workflows/pr-analyzer.yml
  
  smoke-tests:
    needs: check-pr-size
    runs-on: ubuntu-latest
    # Always run smoke tests
    steps:
      - run: pytest tests/ -m "smoke"
  
  full-unit-tests:
    needs: check-pr-size
    if: needs.check-pr-size.outputs.pr_size == 'small'
    # Only on small PRs
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/ --cov
  
  targeted-tests:
    needs: check-pr-size
    if: needs.check-pr-size.outputs.pr_size == 'medium'
    # Medium PRs: Test changed modules only
    runs-on: ubuntu-latest
    steps:
      - run: |
          python scripts/ci/detect_changes.sh > changed_files.txt
          pytest $(cat changed_files.txt)
  
  minimal-validation:
    needs: check-pr-size
    if: needs.check-pr-size.outputs.pr_size == 'large' || needs.check-pr-size.outputs.pr_size == 'refactor'
    # Large PRs: Import checks only
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/ci/validate_imports.py
```

#### Phase 3: On-Demand Full Validation (Phase 2)

**Step 3.1**: Add workflow dispatch trigger
```yaml
# .github/workflows/full-validation-on-demand.yml
name: Full Validation (On-Demand)

on:
  workflow_dispatch:
    inputs:
      pr_number:
        description: 'PR number to validate'
        required: true

jobs:
  full-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          ref: refs/pull/${{ github.event.inputs.pr_number }}/head
      
      - name: Run full test suite
        run: pytest tests/ --cov --timeout=3600
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: ${{ github.event.inputs.pr_number }},
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Full validation complete! ✅'
            })
```

**Step 3.2**: Add bot comment for large PRs
```yaml
# In PR analyzer workflow
- name: Comment on large PRs
  if: steps.size.outputs.category == 'large' || steps.size.outputs.category == 'refactor'
  uses: actions/github-script@v6
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: `
          This PR has ${changed_files} changed files (Large/Refactor category).
          
          **Validation Strategy**:
          - ✓ Smoke tests: Running automatically
          - ⚠ Full test suite: Skipped (run manually if needed)
          
          **To run full validation**:
          Go to Actions → Full Validation (On-Demand) → Run workflow → Enter PR #${context.issue.number}
          
          **Or** comment \`/validate-full\` to trigger automatically.
        `
      })
```

#### Phase 4: Artifact Collection Strategy (Phase 3)

**Step 4.1**: Collect logs based on PR size
```yaml
- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: validation-logs-pr${{ github.event.number }}
    path: |
      test-results/
      coverage-reports/
      logs/
    retention-days: ${{ needs.check-pr-size.outputs.pr_size == 'small' && 7 || 30 }}
    # Small PRs: 7-iteration retention, Large PRs: 30-iteration retention
```

**Step 4.2**: Smart artifact retention
```python
# scripts/ci/artifact_cleanup.py
def calculate_retention(pr_size, test_results):
    """Calculate artifact retention period"""
    base_retention = {
        'small': 7,
        'medium': 14,
        'large': 30,
        'refactor': 60,
    }
    
    retention = base_retention[pr_size]
    
    # Extend if tests failed
    if test_results['failed'] > 0:
        retention *= 2
    
    return min(retention, 90)  # Max 90-iteration retention
```

### Success Metrics

**Target**:
- Small PR feedback: <15 min (currently 30+ min)
- Large PR feedback: <10 min (currently timeout)
- Resource utilization: 40% reduction
- Developer satisfaction: 80%+ positive feedback

**Cost Savings**:
- Estimated: 50% reduction in GitHub Actions minutes
- Per-Session: ~$200-300 savings (for enterprise plan)

### Risk Mitigation

**Risk**: Missing issues in large PRs
- **Mitigation**: On-demand full validation available
- **Policy**: Require full validation before merge for large PRs

**Risk**: Developers bypass validation
- **Mitigation**: Required status checks for smoke tests
- **Enforcement**: Branch protection rules

---

## Implementation Roadmap

### Phase 1: Critical Fixes
- [ ] **Step 1-2**: Planset 1 diagnostics (auto-fix logging)
- [ ] **Step 3-4**: Planset 3 Phase 1 (coverage timeout protection)
- [ ] **Step 5**: Planset 2 diagnostics (test infrastructure)

### Phase 2: Core Improvements
- [ ] **Step 1-2**: Planset 1 implementation (auto-fix fix)
- [ ] **Step 3-4**: Planset 3 Phase 2 (incremental coverage)
- [ ] **Step 5**: Planset 5 Phase 1 (PR size detection)

### Phase 3: Advanced Optimizations
- [ ] **Step 1-2**: Planset 2 implementation (test layering)
- [ ] **Step 3-4**: Planset 4 implementation (async validation)
- [ ] **Step 5**: Planset 5 Phase 2 (conditional workflows)

### Phase 4: Polish & Monitoring
- [ ] **Step 1-2**: Testing and bug fixes
- [ ] **Step 3**: Documentation
- [ ] **Step 4**: Monitoring dashboards
- [ ] **Step 5**: Retrospective and lessons learned

---

## Monitoring & Observability

### Metrics to Track

**Workflow Success Rates**:
```python
# scripts/ci/metrics.py
metrics_to_track = {
    'auto_fix_success_rate': "% of auto-fix runs that successfully apply fixes",
    'test_pass_rate': "% of test runs that pass",
    'coverage_collection_success': "% of coverage runs that complete",
    'average_feedback_time': "Mean time from push to first CI result",
    'resource_utilization': "GitHub Actions minutes consumed per iteration",
}
```

**Dashboard**:
- Grafana/Prometheus setup tracking CI metrics
- Per-Phase reports on improvement trends
- Alert on regression

### Continuous Improvement

**Per-Phase Review**:
- Analyze failed runs
- Identify new patterns
- Adjust plansets as needed

**Per-Session Retrospective**:
- Review metrics against targets
- Gather developer feedback
- Plan next optimizations

---

## Appendix: Tool & Technology Recommendations

### Testing
- `pytest`: Test framework
- `pytest-xdist`: Parallel execution
- `pytest-cov`: Coverage collection
- `pytest-timeout`: Timeout protection

### CI/CD
- GitHub Actions: Workflow orchestration
- `actions/cache`: Dependency caching
- `actions/upload-artifact`: Log/report storage

### Monitoring
- GitHub Actions insights: Built-in metrics
- Custom logging: structured JSON logs
- Alerting: GitHub Actions failure notifications

### Development
- `pre-commit`: Local validation before push
- `nox`: Test environment management
- `tox`: Multi-environment testing

---

**Document Status**: COMPLETE  
**Last Updated**: 2026-02-15T10:30:00Z  
**Next Steps**: Begin Phase 1 implementation (Plansets 1 & 3 diagnostics)
