# GitHub Copilot Agent: Coverage Enhancement Prompt

## Comprehensive Reusable Prompt for Raising Test Coverage to 100%

Use this prompt template to instruct GitHub Copilot Agent to systematically raise test coverage from any level below 99% to 100%.

---

## 🎯 MASTER PROMPT

```
@copilot You are tasked with raising test coverage for this repository to 100%. Follow this systematic approach:

## PHASE 1: ANALYSIS

1. **Run coverage analysis** to identify all files with coverage below 99%:
   ```bash
   coverage run -m pytest tests/ -q
   coverage report --show-missing --fail-under=0 | grep -E "^\S.*\s+[0-9]+\s+" | awk '$NF != "100%" {print $0}' | sort -t'%' -k1 -n
   coverage html -d htmlcov
   ```

2. **Categorize files by coverage gap**:
   - **Critical (0-25%)**: Requires comprehensive test suite creation
   - **Low (25-50%)**: Needs significant test expansion
   - **Medium (50-75%)**: Requires targeted test additions
   - **High (75-99%)**: Needs edge case and branch coverage
   - **Near-Complete (99%+)**: Final polish only

3. **Identify uncovered code patterns**:
   - Missing branch coverage (if/else, try/except)
   - Unexercised function parameters
   - Error handling paths
   - Edge cases and boundary conditions
   - Private/internal methods

## PHASE 2: TEST GENERATION STRATEGY

For each uncovered file, apply these test creation patterns:

### A. Function-Level Coverage

For each uncovered function:
```python
def test_{function_name}_basic():
    """Test {function_name} with typical inputs"""
    # Arrange
    input_data = create_typical_input()
    expected = calculate_expected_output()
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected

def test_{function_name}_edge_cases():
    """Test {function_name} edge cases"""
    # Test empty input
    # Test None input
    # Test boundary values
    # Test maximum values
    pass

def test_{function_name}_error_handling():
    """Test {function_name} error paths"""
    with pytest.raises(ExpectedError):
        function_name(invalid_input)
```

### B. Branch Coverage

For each uncovered branch:
```python
def test_{function_name}_branch_true():
    """Exercise the True branch of condition"""
    pass

def test_{function_name}_branch_false():
    """Exercise the False branch of condition"""
    pass
```

### C. Class Coverage

For each class:
```python
class Test{ClassName}:
    """Complete coverage for {ClassName}"""
    
    def test_init_default(self):
        """Test default initialization"""
        pass
    
    def test_init_with_params(self):
        """Test parameterized initialization"""
        pass
    
    def test_all_public_methods(self):
        """Test all public methods"""
        pass
    
    def test_properties(self):
        """Test property getters/setters"""
        pass
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        pass
```

## PHASE 3: EXECUTION CHECKLIST

For each file below 99% coverage:

- [ ] Identify all uncovered lines using `coverage report --show-missing`
- [ ] Create test file if not exists: `tests/{path}/test_{filename}.py`
- [ ] Add imports and fixtures
- [ ] Write tests for each uncovered function
- [ ] Write tests for each uncovered branch
- [ ] Write tests for error handling paths
- [ ] Run coverage to verify: `coverage run -m pytest tests/{path}/test_{filename}.py -v`
- [ ] Iterate until 100% achieved

## PHASE 4: SPECIFIC FILE TEMPLATES

### Template for 0% Coverage Files (No Tests)

```python
"""
Comprehensive tests for {module_name}

Target: 100% coverage
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from {module_path} import (
    # Import all public symbols
)

# === Fixtures ===

@pytest.fixture
def sample_instance():
    """Create a sample instance for testing"""
    return ClassName()

@pytest.fixture
def mock_dependency():
    """Mock external dependencies"""
    with patch('{module_path}.external_dep') as mock:
        yield mock

# === Unit Tests ===

class TestClassName:
    """Tests for ClassName"""
    
    def test_init(self):
        """Test initialization"""
        obj = ClassName()
        assert obj is not None
    
    def test_method_normal_case(self):
        """Test method with normal inputs"""
        pass
    
    def test_method_edge_case(self):
        """Test method edge cases"""
        pass
    
    def test_method_error_case(self):
        """Test method error handling"""
        pass

# === Integration Tests ===

class TestIntegration:
    """Integration tests"""
    pass
```

### Template for Low Coverage Files (25-50%)

Focus on:
1. Untested methods
2. Missing branch coverage
3. Error paths

### Template for Medium Coverage Files (50-75%)

Focus on:
1. Complex method paths
2. Conditional branches
3. Exception handlers

### Template for High Coverage Files (75-99%)

Focus on:
1. Edge cases
2. Boundary conditions
3. Rare code paths
4. Default parameter values

## PHASE 5: COMMON PATTERNS

### Mocking External Dependencies

```python
@patch('module.external_service')
def test_with_mocked_service(mock_service):
    mock_service.return_value = expected_data
    result = function_under_test()
    assert result == expected_output
```

### Testing Exceptions

```python
def test_raises_on_invalid_input():
    with pytest.raises(ValueError, match="expected message"):
        function_under_test(invalid_input)
```

### Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Testing File Operations

```python
def test_file_operations(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    result = read_file(test_file)
    assert result == "content"
```

### Testing CLI Commands

```python
from click.testing import CliRunner

def test_cli_command():
    runner = CliRunner()
    result = runner.invoke(cli_command, ['--arg', 'value'])
    assert result.exit_code == 0
```

## PHASE 6: PRIORITY ORDER

Address files in this order:
1. **Core business logic** (highest impact)
2. **Public APIs** (user-facing)
3. **Utility functions** (widely used)
4. **CLI/Entry points** (integration)
5. **Internal helpers** (supporting code)

## PHASE 7: VALIDATION

After adding tests:

```bash
# Run full coverage check
coverage run -m pytest tests/ -v
coverage report --show-missing --fail-under=100

# Generate HTML report for review
coverage html -d htmlcov

# Verify no regressions
pytest tests/ -v --tb=short
```

## DELIVERABLES

For each file enhanced:
1. New or updated test file
2. Coverage increase documented
3. All tests passing
4. No regressions introduced

## CONSTRAINTS

- Do NOT modify source code to increase coverage (except fixing bugs)
- Do NOT skip or exclude code from coverage
- Do NOT use `# pragma: no cover` unless absolutely necessary
- DO use mocking for external dependencies
- DO maintain test isolation
- DO follow existing test patterns in repository
```

---

## 📋 FILE-SPECIFIC PROMPTS

### For Specific Low-Coverage Files

```
@copilot Raise coverage for `{file_path}` to 100%.

Current coverage: {X}%
Missing lines: {line_numbers}

Steps:
1. Analyze the file structure and identify all functions/classes
2. For each uncovered line, determine what test would exercise it
3. Create tests in `tests/{corresponding_test_path}`
4. Run: `coverage run -m pytest tests/{test_file} -v`
5. Verify 100% coverage achieved

Focus areas:
- Lines {missing_lines}: {brief_description_of_what_those_lines_do}
```

### For Module-Wide Coverage

```
@copilot Achieve 100% coverage for the `{module_name}` module.

Files to cover:
- {file1}: current {X1}%
- {file2}: current {X2}%
- {file3}: current {X3}%

Create comprehensive test files under `tests/{module}/` following existing patterns.
```

---

## 🔧 AUTOMATION SCRIPTS

### Generate Coverage Gap Report

```python
#!/usr/bin/env python3
"""Generate prioritized coverage gap report for Copilot Agent"""
import subprocess
import json

def get_coverage_gaps():
    """Extract files with coverage < 100%"""
    result = subprocess.run(
        ['coverage', 'json', '-o', '-'],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    
    gaps = []
    for file, info in data['files'].items():
        coverage = info['summary']['percent_covered']
        if coverage < 100:
            gaps.append({
                'file': file,
                'coverage': coverage,
                'missing_lines': info['missing_lines'],
                'missing_branches': info.get('missing_branches', [])
            })
    
    return sorted(gaps, key=lambda x: x['coverage'])

if __name__ == '__main__':
    for gap in get_coverage_gaps():
        print(f"{gap['file']}: {gap['coverage']:.1f}% - Missing: {gap['missing_lines'][:5]}...")
```

### Batch Test Generation Prompt

```
@copilot Generate tests for all files in the following list to achieve 100% coverage:

{paste_output_from_gap_report}

For each file:
1. Create corresponding test file
2. Cover all missing lines
3. Handle all branches
4. Test error conditions
5. Verify with coverage run
```

---

## 📊 TRACKING TEMPLATE

| File | Before | After | Test File | Status |
|------|--------|-------|-----------|--------|
| src/module/file.py | 45% | 100% | tests/module/test_file.py | ✅ |
| src/other/file.py | 0% | 100% | tests/other/test_file.py | ✅ |

---

## 🚀 QUICK START

Copy and paste this to start:

```
@copilot I need to raise test coverage to 100% for this repository.

Current state:
- Run `coverage report --show-missing` to see gaps
- Total coverage is currently below the 100% target

Your task:
1. Identify all files with coverage < 100%
2. For each file, create comprehensive tests
3. Use mocking for external dependencies
4. Follow existing test patterns in the repository
5. Validate each file reaches 100% before moving to next
6. Report progress after each file

Start with the files that have 0% coverage, then work up to higher coverage files.

Begin by running coverage analysis and listing all files that need tests.
```

---

## 📝 NOTES

- This prompt is designed for the Aries-Serpent/_codex_ repository
- Adjust paths and patterns based on your project structure
- For large codebases, process files in batches
- Use `pytest-cov` for inline coverage during development
- Consider parallel test execution for speed: `pytest -n auto`
