# Test Coverage Enforcer Agent - Advanced Patterns

This document covers advanced usage patterns, best practices, and sophisticated integrations for the Test Coverage Enforcer Agent.

## Table of Contents

1. [Pattern 1: Custom Threshold Per Module](#pattern-1-custom-threshold-per-module)
2. [Pattern 2: Integration with Pre-commit Hooks](#pattern-2-integration-with-pre-commit-hooks)
3. [Pattern 3: Coverage-Driven Test Generation](#pattern-3-coverage-driven-test-generation)
4. [Pattern 4: Multi-Project Coverage Aggregation](#pattern-4-multi-project-coverage-aggregation)
5. [Pattern 5: Coverage Regression Detection](#pattern-5-coverage-regression-detection)
6. [Pattern 6: Performance Optimization for Large Codebases](#pattern-6-performance-optimization-for-large-codebases)

---

## Pattern 1: Custom Threshold Per Module

**Use Case**: Different parts of your codebase require different coverage levels (e.g., core logic needs 95%, utilities need 80%, scripts need 60%).

### Implementation

Create a custom wrapper script `scripts/enforce_coverage_custom.py`:

```python
#!/usr/bin/env python3
"""
Custom coverage enforcement with per-module thresholds
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer, EnforcementResult

# Define per-module thresholds
MODULE_THRESHOLDS = {
    'src/core': {'line': 95, 'branch': 90, 'function': 98},
    'src/utils': {'line': 80, 'branch': 75, 'function': 85},
    'src/scripts': {'line': 60, 'branch': 50, 'function': 70},
    'src/api': {'line': 90, 'branch': 85, 'function': 95},
}

def enforce_per_module():
    """Enforce coverage with per-module thresholds"""
    overall_passed = True
    results = {}
    
    for module_path, thresholds in MODULE_THRESHOLDS.items():
        print(f"\n{'='*80}")
        print(f"Enforcing coverage for: {module_path}")
        print(f"Thresholds: Line={thresholds['line']}%, "
              f"Branch={thresholds['branch']}%, "
              f"Function={thresholds['function']}%")
        print(f"{'='*80}\n")
        
        # Create agent with custom thresholds
        agent = TestCoverageEnforcer()
        agent.line_threshold = thresholds['line']
        agent.branch_threshold = thresholds['branch']
        agent.function_threshold = thresholds['function']
        
        # Enforce for this module
        result = agent.enforce_thresholds(Path(module_path))
        results[module_path] = result
        
        # Track overall pass/fail
        if not result.passed:
            overall_passed = False
        
        # Print result
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"\n{status}: {module_path}")
        print(f"  Coverage: {result.current_coverage:.1f}%")
        print(f"  Threshold: {result.threshold}%")
        print(f"  Gaps: {result.gaps_found}")
        
        if result.enforcement_actions:
            print(f"  Actions:")
            for action in result.enforcement_actions:
                print(f"    - {action}")
    
    # Overall summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    print(f"Total modules: {len(results)}")
    print(f"Passed: {sum(1 for r in results.values() if r.passed)}")
    print(f"Failed: {sum(1 for r in results.values() if not r.passed)}")
    print(f"\nOverall status: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
    
    # Exit with appropriate code
    sys.exit(0 if overall_passed else 1)

if __name__ == '__main__':
    enforce_per_module()
```

### GitHub Actions Integration

```yaml
name: Per-Module Coverage Enforcement

on:
  push:
    branches: [main]
  pull_request:

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e ".[dev,test]"
      
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=json:coverage.json
      
      - name: Enforce per-module coverage
        run: python scripts/enforce_coverage_custom.py
```

### Expected Output

```
================================================================================
Enforcing coverage for: src/core
Thresholds: Line=95%, Branch=90%, Function=98%
================================================================================

✅ PASSED: src/core
  Coverage: 96.5%
  Threshold: 95%
  Gaps: 0

================================================================================
Enforcing coverage for: src/utils
Thresholds: Line=80%, Branch=75%, Function=85%
================================================================================

❌ FAILED: src/utils
  Coverage: 75.0%
  Threshold: 80%
  Gaps: 3
  Actions:
    - Coverage 75.0% below threshold 80%
    - Found 3 coverage gaps

================================================================================
OVERALL SUMMARY
================================================================================
Total modules: 4
Passed: 3
Failed: 1

Overall status: ❌ FAILED
```

### Key Benefits

- Fine-grained control over coverage requirements
- Different standards for different code criticality
- Clear module-by-module reporting
- Flexible threshold management

---

## Pattern 2: Integration with Pre-commit Hooks

**Use Case**: Enforce coverage locally before code reaches CI/CD, providing immediate feedback to developers.

### Advanced Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
  # Standard pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  # Python code formatters
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  # Custom coverage enforcement
  - repo: local
    hooks:
      - id: coverage-check-changed-files
        name: Coverage Check (Changed Files Only)
        entry: bash -c 'python scripts/check_coverage_changed_files.py'
        language: system
        pass_filenames: false
        stages: [commit]
      
      - id: coverage-check-full
        name: Coverage Check (Full)
        entry: bash -c 'cd .github/agents/test-coverage-enforcer && python -m src.agent enforce --path src --threshold 80'
        language: system
        pass_filenames: false
        stages: [push]
```

### Smart Coverage Check Script

Create `scripts/check_coverage_changed_files.py`:

```python
#!/usr/bin/env python3
"""
Check coverage only for changed files (smart pre-commit)
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer

def get_changed_files():
    """Get list of changed Python files"""
    try:
        # Get staged files
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = result.stdout.strip().split('\n')
        
        # Filter Python files in src/
        python_files = [
            Path(f) for f in files
            if f.startswith('src/') and f.endswith('.py')
        ]
        
        return python_files
    except subprocess.CalledProcessError:
        return []

def check_changed_files_coverage():
    """Check coverage for only changed files"""
    changed_files = get_changed_files()
    
    if not changed_files:
        print("No Python files changed in src/")
        return True
    
    print(f"Checking coverage for {len(changed_files)} changed file(s):")
    for f in changed_files:
        print(f"  - {f}")
    
    agent = TestCoverageEnforcer()
    agent.line_threshold = 75  # Lower threshold for pre-commit
    
    all_passed = True
    
    for file_path in changed_files:
        # Run coverage for specific file
        result = agent.enforce_thresholds(file_path)
        
        if not result.passed:
            all_passed = False
            print(f"\n❌ {file_path}: {result.current_coverage:.1f}% (threshold: {result.threshold}%)")
            for action in result.enforcement_actions:
                print(f"  - {action}")
        else:
            print(f"✅ {file_path}: {result.current_coverage:.1f}%")
    
    if not all_passed:
        print("\n⚠️  Coverage too low for changed files")
        print("Run: pytest tests/ --cov=src -v")
        print("To bypass: git commit --no-verify")
    
    return all_passed

if __name__ == '__main__':
    passed = check_changed_files_coverage()
    sys.exit(0 if passed else 1)
```

### Usage

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install --hook-type pre-commit --hook-type pre-push

# Now coverage is checked automatically:

# On commit - checks only changed files
git commit -m "Update module"
# → Runs fast coverage check

# On push - checks full codebase
git push origin feature-branch
# → Runs full coverage enforcement

# Bypass if needed
git commit --no-verify -m "WIP: Need to push incomplete work"
```

### Key Benefits

- Fast feedback loop (< 5 seconds for changed files)
- Prevents low-coverage code from being committed
- Different thresholds for commit vs push
- Can be bypassed when necessary

---

## Pattern 3: Coverage-Driven Test Generation

**Use Case**: Automatically generate and run tests to achieve target coverage, iterating until threshold is met.

### Implementation

Create `scripts/coverage_driven_generation.py`:

```python
#!/usr/bin/env python3
"""
Coverage-driven test generation with iterative improvement
"""

import sys
from pathlib import Path
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer

def run_tests_with_coverage(source_path):
    """Run tests and collect coverage data"""
    subprocess.run(
        ['pytest', '--cov=' + str(source_path), '--cov-report=json:coverage.json'],
        check=False
    )

def generate_and_implement_tests(agent, source_path, max_iterations=5):
    """Iteratively generate and implement tests until threshold met"""
    
    target_threshold = agent.line_threshold
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"ITERATION {iteration}/{max_iterations}")
        print(f"{'='*80}\n")
        
        # Run tests and analyze coverage
        run_tests_with_coverage(source_path)
        reports = agent.analyze_coverage(source_path, Path('coverage.json'))
        
        # Check if threshold met
        total_lines = sum(r.total_lines for r in reports.values())
        covered_lines = sum(r.covered_lines for r in reports.values())
        current_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        
        print(f"Current coverage: {current_coverage:.1f}%")
        print(f"Target threshold: {target_threshold}%")
        
        if current_coverage >= target_threshold:
            print(f"\n✅ Target coverage achieved!")
            return True
        
        # Generate test suggestions
        suggestions = agent.generate_test_suggestions(reports)
        
        if not suggestions:
            print(f"\n⚠️  No more test suggestions available")
            print(f"Final coverage: {current_coverage:.1f}%")
            return False
        
        print(f"\nGenerated {len(suggestions)} test suggestions")
        
        # Implement top priority suggestions
        implemented = 0
        for suggestion in suggestions[:5]:  # Implement top 5
            print(f"\nImplementing: {suggestion.target_function} "
                  f"(Priority {suggestion.priority}, Impact +{suggestion.coverage_impact:.1f}%)")
            
            # Create test file if it doesn't exist
            test_file = suggestion.test_file
            if not test_file.exists():
                test_file.parent.mkdir(parents=True, exist_ok=True)
                test_file.write_text("import pytest\n\n")
            
            # Append test template
            with open(test_file, 'a') as f:
                f.write('\n' + suggestion.test_template + '\n')
            
            implemented += 1
            print(f"  ✓ Added tests to {test_file}")
        
        print(f"\nImplemented {implemented} test templates")
        print(f"Next iteration will run these tests...")
    
    print(f"\n⚠️  Maximum iterations ({max_iterations}) reached")
    print(f"Final coverage: {current_coverage:.1f}%")
    return False

def main():
    """Main entry point"""
    source_path = Path('src')
    
    agent = TestCoverageEnforcer()
    agent.line_threshold = 85
    agent.auto_generate = True
    
    print(f"Target: Achieve {agent.line_threshold}% coverage for {source_path}")
    
    success = generate_and_implement_tests(agent, source_path)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

### Usage

```bash
# Run coverage-driven generation
python scripts/coverage_driven_generation.py
```

### Expected Output

```
Target: Achieve 85% coverage for src

================================================================================
ITERATION 1/5
================================================================================

Current coverage: 72.0%
Target threshold: 85%

Generated 12 test suggestions

Implementing: process_data (Priority 1, Impact +8.5%)
  ✓ Added tests to tests/test_processor.py
Implementing: validate_input (Priority 1, Impact +7.2%)
  ✓ Added tests to tests/test_validator.py
Implementing: format_output (Priority 2, Impact +5.1%)
  ✓ Added tests to tests/test_formatter.py

Implemented 3 test templates
Next iteration will run these tests...

================================================================================
ITERATION 2/5
================================================================================

Current coverage: 80.3%
Target threshold: 85%

Generated 9 test suggestions

Implementing: handle_error (Priority 1, Impact +6.0%)
  ✓ Added tests to tests/test_error_handler.py
Implementing: log_event (Priority 2, Impact +4.5%)
  ✓ Added tests to tests/test_logger.py

Implemented 2 test templates
Next iteration will run these tests...

================================================================================
ITERATION 3/5
================================================================================

Current coverage: 86.1%
Target threshold: 85%

✅ Target coverage achieved!
```

### Key Benefits

- Automated test generation and implementation
- Iterative improvement toward target
- Prioritizes high-impact tests
- Stops when threshold is met

---

## Pattern 4: Multi-Project Coverage Aggregation

**Use Case**: Aggregate coverage across multiple related projects or microservices.

### Implementation

Create `scripts/aggregate_coverage.py`:

```python
#!/usr/bin/env python3
"""
Aggregate coverage across multiple projects
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer, CoverageReport

# Define projects to aggregate
PROJECTS = [
    {'name': 'API Server', 'path': 'projects/api-server/src'},
    {'name': 'Worker Service', 'path': 'projects/worker/src'},
    {'name': 'Database Layer', 'path': 'projects/database/src'},
    {'name': 'Shared Utils', 'path': 'projects/shared/src'},
]

def collect_project_coverage(project: Dict) -> Dict:
    """Collect coverage for a single project"""
    agent = TestCoverageEnforcer()
    reports = agent.analyze_coverage(Path(project['path']))
    
    total_lines = sum(r.total_lines for r in reports.values())
    covered_lines = sum(r.covered_lines for r in reports.values())
    coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
    
    return {
        'name': project['name'],
        'path': project['path'],
        'coverage': coverage,
        'total_lines': total_lines,
        'covered_lines': covered_lines,
        'files': len(reports),
    }

def aggregate_coverage():
    """Aggregate coverage across all projects"""
    print("Collecting coverage data from all projects...\n")
    
    results = []
    for project in PROJECTS:
        print(f"Analyzing: {project['name']}...")
        result = collect_project_coverage(project)
        results.append(result)
        print(f"  Coverage: {result['coverage']:.1f}%")
    
    # Calculate overall aggregate coverage
    total_lines = sum(r['total_lines'] for r in results)
    covered_lines = sum(r['covered_lines'] for r in results)
    aggregate_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
    
    # Generate report
    print(f"\n{'='*80}")
    print("AGGREGATED COVERAGE REPORT")
    print(f"{'='*80}\n")
    
    print(f"{'Project':<25} {'Coverage':<12} {'Lines':<15} {'Files':<8}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['name']:<25} "
              f"{result['coverage']:>6.1f}% "
              f"     {result['covered_lines']:>5}/{result['total_lines']:<5} "
              f"  {result['files']:>3}")
    
    print("-" * 80)
    print(f"{'OVERALL':<25} "
          f"{aggregate_coverage:>6.1f}% "
          f"     {covered_lines:>5}/{total_lines:<5} "
          f"  {sum(r['files'] for r in results):>3}")
    
    # Save JSON report
    report_data = {
        'projects': results,
        'aggregate': {
            'coverage': aggregate_coverage,
            'total_lines': total_lines,
            'covered_lines': covered_lines,
            'total_files': sum(r['files'] for r in results),
        }
    }
    
    output_file = Path('aggregate_coverage.json')
    output_file.write_text(json.dumps(report_data, indent=2))
    print(f"\nDetailed report saved to: {output_file}")
    
    # Check threshold
    threshold = 80.0
    if aggregate_coverage >= threshold:
        print(f"\n✅ Aggregate coverage {aggregate_coverage:.1f}% meets threshold {threshold}%")
        return True
    else:
        print(f"\n❌ Aggregate coverage {aggregate_coverage:.1f}% below threshold {threshold}%")
        return False

if __name__ == '__main__':
    passed = aggregate_coverage()
    sys.exit(0 if passed else 1)
```

### Expected Output

```
Collecting coverage data from all projects...

Analyzing: API Server...
  Coverage: 87.5%
Analyzing: Worker Service...
  Coverage: 82.0%
Analyzing: Database Layer...
  Coverage: 91.2%
Analyzing: Shared Utils...
  Coverage: 78.5%

================================================================================
AGGREGATED COVERAGE REPORT
================================================================================

Project                   Coverage     Lines           Files   
--------------------------------------------------------------------------------
API Server                  87.5%       875/1000         12
Worker Service              82.0%       656/800           8
Database Layer              91.2%       456/500           5
Shared Utils                78.5%       471/600           7
--------------------------------------------------------------------------------
OVERALL                     83.5%      2458/2900         32

Detailed report saved to: aggregate_coverage.json

✅ Aggregate coverage 83.5% meets threshold 80%
```

### Key Benefits

- Single view of multi-project coverage
- Identifies weak projects
- Overall vs per-project metrics
- JSON export for dashboards

---

## Pattern 5: Coverage Regression Detection

**Use Case**: Detect when coverage decreases between commits or PR branches.

### Implementation

Create `scripts/detect_coverage_regression.py`:

```python
#!/usr/bin/env python3
"""
Detect coverage regressions between branches
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer

def get_coverage_for_branch(branch_name, source_path):
    """Get coverage for a specific branch"""
    # Stash current changes
    subprocess.run(['git', 'stash'], check=False)
    
    # Checkout branch
    subprocess.run(['git', 'checkout', branch_name], check=True)
    
    # Run tests with coverage
    subprocess.run(
        ['pytest', '--cov=' + str(source_path), '--cov-report=json:coverage.json'],
        check=False
    )
    
    # Analyze coverage
    agent = TestCoverageEnforcer()
    reports = agent.analyze_coverage(source_path, Path('coverage.json'))
    
    total_lines = sum(r.total_lines for r in reports.values())
    covered_lines = sum(r.covered_lines for r in reports.values())
    coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
    
    return coverage

def detect_regression(base_branch='main', target_branch='HEAD', source_path='src'):
    """Detect coverage regression between branches"""
    print(f"Detecting coverage regression...")
    print(f"  Base branch: {base_branch}")
    print(f"  Target branch: {target_branch}")
    print(f"  Source path: {source_path}\n")
    
    # Get current branch
    current_branch = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()
    
    try:
        # Get base coverage
        print(f"Analyzing base branch ({base_branch})...")
        base_coverage = get_coverage_for_branch(base_branch, source_path)
        print(f"  Base coverage: {base_coverage:.1f}%\n")
        
        # Get target coverage
        print(f"Analyzing target branch ({current_branch})...")
        subprocess.run(['git', 'checkout', current_branch], check=True)
        subprocess.run(['git', 'stash', 'pop'], check=False)
        
        target_coverage = get_coverage_for_branch(current_branch, source_path)
        print(f"  Target coverage: {target_coverage:.1f}%\n")
        
        # Calculate regression
        regression = base_coverage - target_coverage
        regression_threshold = 2.0  # Alert if coverage drops > 2%
        
        print(f"{'='*80}")
        print("COVERAGE REGRESSION ANALYSIS")
        print(f"{'='*80}\n")
        print(f"Base ({base_branch}):   {base_coverage:.1f}%")
        print(f"Target ({current_branch}): {target_coverage:.1f}%")
        print(f"Change:         {'+' if regression < 0 else ''}{-regression:.1f}%")
        
        if regression > regression_threshold:
            print(f"\n❌ REGRESSION DETECTED: Coverage dropped by {regression:.1f}%")
            print(f"   (Threshold: {regression_threshold}%)")
            return False
        elif regression > 0:
            print(f"\n⚠️  Minor coverage decrease: {regression:.1f}%")
            print(f"   (Below threshold: {regression_threshold}%)")
            return True
        else:
            print(f"\n✅ Coverage improved by {-regression:.1f}%")
            return True
    
    finally:
        # Restore original branch
        subprocess.run(['git', 'checkout', current_branch], check=False)
        subprocess.run(['git', 'stash', 'pop'], check=False)

if __name__ == '__main__':
    passed = detect_regression()
    sys.exit(0 if passed else 1)
```

### GitHub Actions Integration

```yaml
name: Coverage Regression Check

on:
  pull_request:
    branches: [main]

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for branch comparison
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e ".[dev,test]"
      
      - name: Detect coverage regression
        run: python scripts/detect_coverage_regression.py
```

### Expected Output

```
Detecting coverage regression...
  Base branch: main
  Target branch: feature/new-api
  Source path: src

Analyzing base branch (main)...
  Base coverage: 85.5%

Analyzing target branch (feature/new-api)...
  Target coverage: 82.0%

================================================================================
COVERAGE REGRESSION ANALYSIS
================================================================================

Base (main):   85.5%
Target (feature/new-api): 82.0%
Change:         -3.5%

❌ REGRESSION DETECTED: Coverage dropped by 3.5%
   (Threshold: 2.0%)
```

### Key Benefits

- Automatically detects coverage drops
- Prevents quality regressions
- Configurable regression threshold
- Branch-to-branch comparison

---

## Pattern 6: Performance Optimization for Large Codebases

**Use Case**: Optimize coverage analysis for codebases with 100k+ lines of code.

### Optimization Strategies

#### 1. Parallel File Analysis

```python
# scripts/parallel_coverage_analysis.py

import concurrent.futures
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer

def analyze_file(file_path):
    """Analyze coverage for a single file"""
    agent = TestCoverageEnforcer()
    return agent.analyze_coverage(file_path)

def parallel_analyze(source_path, max_workers=8):
    """Analyze coverage in parallel"""
    # Get all Python files
    python_files = list(Path(source_path).rglob('*.py'))
    
    print(f"Analyzing {len(python_files)} files with {max_workers} workers...")
    
    all_reports = {}
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(analyze_file, f): f
            for f in python_files
        }
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                reports = future.result()
                all_reports.update(reports)
                print(f"  ✓ {file_path}")
            except Exception as e:
                print(f"  ✗ {file_path}: {e}")
    
    return all_reports
```

#### 2. Coverage Data Caching

```python
# scripts/cached_coverage_analysis.py

import hashlib
import json
import pickle
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer

CACHE_DIR = Path('.coverage_cache')

def get_file_hash(file_path):
    """Calculate SHA256 hash of file"""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()

def get_cached_coverage(file_path):
    """Get cached coverage if file hasn't changed"""
    CACHE_DIR.mkdir(exist_ok=True)
    
    file_hash = get_file_hash(file_path)
    cache_file = CACHE_DIR / f"{file_path.stem}_{file_hash}.pkl"
    
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    return None

def cache_coverage(file_path, report):
    """Cache coverage report"""
    CACHE_DIR.mkdir(exist_ok=True)
    
    file_hash = get_file_hash(file_path)
    cache_file = CACHE_DIR / f"{file_path.stem}_{file_hash}.pkl"
    
    with open(cache_file, 'wb') as f:
        pickle.dump(report, f)

def analyze_with_cache(source_path):
    """Analyze coverage with caching"""
    agent = TestCoverageEnforcer()
    python_files = list(Path(source_path).rglob('*.py'))
    
    cache_hits = 0
    cache_misses = 0
    
    for file_path in python_files:
        cached = get_cached_coverage(file_path)
        
        if cached:
            agent.reports[file_path] = cached
            cache_hits += 1
            print(f"  [CACHE] {file_path}")
        else:
            reports = agent.analyze_coverage(file_path)
            if file_path in reports:
                cache_coverage(file_path, reports[file_path])
            cache_misses += 1
            print(f"  [ANALYZE] {file_path}")
    
    print(f"\nCache stats: {cache_hits} hits, {cache_misses} misses")
    print(f"Cache hit rate: {(cache_hits/(cache_hits+cache_misses)*100):.1f}%")
    
    return agent.reports
```

#### 3. Incremental Analysis (Changed Files Only)

```python
# scripts/incremental_coverage_analysis.py

import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / '.github/agents/test-coverage-enforcer'))

from src.agent import TestCoverageEnforcer

def get_changed_files(base_branch='main'):
    """Get files changed since base branch"""
    result = subprocess.run(
        ['git', 'diff', '--name-only', f'{base_branch}...HEAD'],
        capture_output=True,
        text=True,
        check=True
    )
    
    files = result.stdout.strip().split('\n')
    return [Path(f) for f in files if f.endswith('.py')]

def incremental_analyze(source_path, base_branch='main'):
    """Analyze only changed files"""
    changed_files = get_changed_files(base_branch)
    
    print(f"Incremental analysis: {len(changed_files)} changed files")
    
    agent = TestCoverageEnforcer()
    
    for file_path in changed_files:
        if file_path.exists():
            print(f"  Analyzing: {file_path}")
            agent.analyze_coverage(file_path)
    
    return agent.reports
```

### Configuration for Large Codebases

```yaml
# config/agent_config.yaml (optimized)

advanced:
  # Enable parallel analysis
  parallel_analysis: true
  max_workers: 8
  
  # Enable aggressive caching
  cache_coverage_data: true
  cache_ttl_seconds: 86400  # 24 hours
  
  # Limit suggestions
  max_suggestions_per_file: 5
  max_total_suggestions: 50
  
  # Confidence filtering
  min_confidence_threshold: 0.9
  
  # Incremental mode
  incremental_analysis: true
  base_branch: main
  
  # Performance tuning
  chunk_size: 100  # Process files in chunks
  timeout_seconds: 300  # 5 min timeout per file
```

### Performance Comparison

| Approach | 100 Files | 1000 Files | 10000 Files |
|----------|-----------|------------|-------------|
| Sequential | 30s | 5m | 50m |
| Parallel (8 workers) | 8s | 1m | 12m |
| Cached (100% hit) | 2s | 10s | 1m |
| Incremental (10% changed) | 3s | 30s | 5m |

### Key Benefits

- 5-10x faster analysis with parallelization
- Near-instant results with caching
- Minimal analysis with incremental mode
- Configurable performance tuning

---

## Summary of Advanced Patterns

| Pattern | Use Case | Complexity | Impact |
|---------|----------|------------|--------|
| Custom Threshold Per Module | Different coverage requirements | Medium | High |
| Pre-commit Integration | Local enforcement before CI | Low | High |
| Coverage-Driven Generation | Automated test creation | High | Very High |
| Multi-Project Aggregation | Microservices/monorepos | Medium | Medium |
| Regression Detection | Prevent quality drops | Medium | High |
| Performance Optimization | Large codebases (100k+ LOC) | High | Very High |

---

**For more information:**
- [Main Prompts](main.md)
- [Usage Examples](examples.md)
- [README](../README.md)
- [CHANGELOG](../CHANGELOG.md)
