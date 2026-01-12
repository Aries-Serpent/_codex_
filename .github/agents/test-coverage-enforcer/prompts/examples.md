# Test Coverage Enforcer Agent - Usage Examples

This document provides real-world scenarios and examples of using the Test Coverage Enforcer Agent.

## Table of Contents

1. [Example 1: PR Coverage Check](#example-1-pr-coverage-check)
2. [Example 2: Pre-commit Enforcement](#example-2-pre-commit-enforcement)
3. [Example 3: Auto-generate Missing Tests](#example-3-auto-generate-missing-tests)
4. [Example 4: Coverage Trend Analysis](#example-4-coverage-trend-analysis)
5. [Example 5: CI/CD Integration](#example-5-cicd-integration)
6. [Example 6: HTML Report Generation](#example-6-html-report-generation)

---

## Example 1: PR Coverage Check

**Scenario**: You want to check test coverage on every pull request and comment the results.

### Setup

Create `.github/workflows/pr-coverage.yml`:

```yaml
name: PR Coverage Check

on:
  pull_request:
    branches: [main, develop]

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
        run: |
          pip install -e ".[dev,test]"
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=json:coverage.json
      
      - name: Enforce coverage thresholds
        uses: ./.github/agents/test-coverage-enforcer
        with:
          check-coverage: true
          threshold: 80
          fail-below-threshold: false  # Don't fail, just report
          source-path: src
          output-format: text
```

### Expected Output

**PR Comment:**
```
## ✅ Test Coverage Report

**Status:** ✅ PASS
**Current Coverage:** 85.5%
**Threshold:** 80%

<details>
<summary>View Full Report</summary>

Coverage by File:
✓ src/module1.py: 95.0% line, 100.0% function
✓ src/module2.py: 82.0% line, 90.0% function
✗ src/module3.py: 65.0% line, 70.0% function

</details>
```

### Key Takeaways

- Sets `fail-below-threshold: false` to avoid blocking PRs
- Provides visibility without strict enforcement
- Generates automatic PR comments
- Helps reviewers see coverage impact

---

## Example 2: Pre-commit Enforcement

**Scenario**: Enforce coverage locally before allowing commits using pre-commit hooks.

### Setup

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: coverage-check
        name: Check Test Coverage
        entry: bash -c 'cd .github/agents/test-coverage-enforcer && python -m src.agent enforce --path src --threshold 75'
        language: system
        pass_filenames: false
        always_run: true
```

### Local Usage

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Now coverage is checked before every commit
git commit -m "Add new feature"
# → Runs coverage check
# → Blocks commit if coverage < 75%
```

### Expected Output

**When coverage is good:**
```bash
Check Test Coverage...................Passed
[main abc1234] Add new feature
```

**When coverage is low:**
```bash
Check Test Coverage...................Failed
- Coverage 72.0% is below threshold 75%
- Found 3 coverage gaps
```

### Key Takeaways

- Catches coverage issues before they reach CI/CD
- Provides immediate feedback to developers
- Can be bypassed with `--no-verify` if needed
- Customizable threshold per project

---

## Example 3: Auto-generate Missing Tests

**Scenario**: Automatically generate test templates for uncovered functions.

### Command

```bash
cd .github/agents/test-coverage-enforcer

# Analyze and generate suggestions
python -m src.agent generate-tests \
  --path src/calculator.py \
  --format text
```

### Input Code (src/calculator.py)

```python
def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract b from a"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Expected Output

```
Generated 4 test suggestions:

Priority 1: divide in src/calculator.py
  Impact: +25.0% coverage
  Test file: tests/test_calculator.py
  
Priority 2: multiply in src/calculator.py
  Impact: +20.0% coverage
  Test file: tests/test_calculator.py
  
Priority 3: subtract in src/calculator.py
  Impact: +15.0% coverage
  Test file: tests/test_calculator.py
  
Priority 4: add in src/calculator.py
  Impact: +15.0% coverage
  Test file: tests/test_calculator.py
```

### Generated Test Template

Create `tests/test_calculator.py`:

```python
def test_divide_basic():
    """Test divide basic functionality"""
    # TODO: Implement test for divide
    # from calculator import divide
    # result = divide(10, 2)
    # assert result == 5
    pass


def test_divide_edge_cases():
    """Test divide edge cases"""
    # TODO: Test edge cases for divide
    # Test division by zero
    # from calculator import divide
    # with pytest.raises(ValueError):
    #     divide(10, 0)
    pass
```

### Key Takeaways

- Automatically identifies untested functions
- Generates starter test templates
- Prioritizes based on impact and coverage
- Templates require manual refinement

---

## Example 4: Coverage Trend Analysis

**Scenario**: Track coverage changes over time to identify trends.

### Setup

Enable cognitive brain in config:

```yaml
# config/agent_config.yaml
cognitive_brain:
  enabled: true
  metrics:
    - coverage_percentage
    - gap_count
    - tests_generated
  reporting_interval: daily
  storage:
    type: sqlite
    path: .codex/sessions/agent_metrics.db
```

### Usage

```bash
# Run daily coverage check
python -m src.agent enforce --path src --threshold 80

# Coverage data is automatically stored in SQLite DB
# Accessible via cognitive brain queries
```

### Query Historical Data

```python
import sqlite3

# Connect to metrics database
conn = sqlite3.connect('.codex/sessions/agent_metrics.db')
cursor = conn.cursor()

# Query coverage trend
cursor.execute("""
    SELECT date, coverage_percentage, gap_count
    FROM coverage_metrics
    ORDER BY date DESC
    LIMIT 30
""")

results = cursor.fetchall()
for date, coverage, gaps in results:
    print(f"{date}: {coverage:.1f}% coverage, {gaps} gaps")
```

### Expected Output

```
2026-01-12: 85.5% coverage, 2 gaps
2026-01-11: 84.0% coverage, 3 gaps
2026-01-10: 82.5% coverage, 4 gaps
2026-01-09: 81.0% coverage, 5 gaps
...
```

### Visualization

```python
import matplotlib.pyplot as plt

dates = [r[0] for r in results]
coverage = [r[1] for r in results]

plt.plot(dates, coverage)
plt.xlabel('Date')
plt.ylabel('Coverage %')
plt.title('Coverage Trend - Last 30 Days')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('coverage_trend.png')
```

### Key Takeaways

- Tracks coverage changes over time
- Identifies upward or downward trends
- Helps measure improvement efforts
- Stored in SQLite for easy querying

---

## Example 5: CI/CD Integration

**Scenario**: Integrate coverage enforcement into a complete CI/CD pipeline.

### Full Pipeline Workflow

```yaml
name: Complete CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev,test]"
      
      - name: Run linters
        run: |
          ruff check src/
          black --check src/
          isort --check src/
      
      - name: Run tests
        run: |
          pytest tests/ -v --tb=short
      
      - name: Enforce coverage
        uses: ./.github/agents/test-coverage-enforcer
        id: coverage
        with:
          check-coverage: true
          threshold: 80
          fail-below-threshold: true
          auto-generate: true
          source-path: src
          output-format: json
          output-file: coverage-report.json
      
      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: coverage-report.json
      
      - name: Notify on failure
        if: steps.coverage.outputs.passed == 'false'
        uses: actions/github-script@v6
        with:
          script: |
            const coverage = '${{ steps.coverage.outputs.coverage-percentage }}';
            const threshold = '80';
            
            core.setFailed(`Coverage ${coverage}% is below threshold ${threshold}%`);
      
      - name: Deploy
        if: github.ref == 'refs/heads/main' && steps.coverage.outputs.passed == 'true'
        run: |
          echo "Deploying application..."
          # Deployment commands here
```

### Pipeline Flow

```
┌─────────────┐
│  Checkout   │
└──────┬──────┘
       │
┌──────▼──────┐
│ Setup Python│
└──────┬──────┘
       │
┌──────▼──────┐
│   Install   │
│Dependencies │
└──────┬──────┘
       │
┌──────▼──────┐
│ Run Linters │
└──────┬──────┘
       │
┌──────▼──────┐
│  Run Tests  │
└──────┬──────┘
       │
┌──────▼──────┐
│   Enforce   │
│  Coverage   │ ← Test Coverage Enforcer
└──────┬──────┘
       │
    ┌──▼──┐
    │Pass?│
    └─┬─┬─┘
  Yes │ │ No
      │ └────► Fail Build
      │
┌─────▼─────┐
│   Deploy  │
└───────────┘
```

### Key Takeaways

- Coverage enforcement is a gate before deployment
- Automatic test generation on failure
- Reports uploaded as artifacts
- Clear failure notifications

---

## Example 6: HTML Report Generation

**Scenario**: Generate a visual HTML coverage report for team review.

### Command

```bash
cd .github/agents/test-coverage-enforcer

python -m src.agent report \
  --path src \
  --format html \
  --output coverage_report.html
```

### Generated HTML Report

The agent generates a styled HTML report:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Coverage Enforcement Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        .pass { color: green; }
        .fail { color: red; }
    </style>
</head>
<body>
    <h1>Test Coverage Enforcement Report</h1>
    <p><strong>Total files:</strong> 5</p>
    <p><strong>Issues found:</strong> 2</p>
    
    <h2>Coverage by File</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Line Coverage</th>
            <th>Function Coverage</th>
            <th>Status</th>
        </tr>
        <tr>
            <td>src/module1.py</td>
            <td>95.0%</td>
            <td>100.0%</td>
            <td class="pass">PASS</td>
        </tr>
        ...
    </table>
</body>
</html>
```

### Usage in CI/CD

```yaml
- name: Generate HTML report
  run: |
    cd .github/agents/test-coverage-enforcer
    python -m src.agent report \
      --path src \
      --format html \
      --output coverage_report.html

- name: Upload HTML report
  uses: actions/upload-artifact@v3
  with:
    name: html-coverage-report
    path: .github/agents/test-coverage-enforcer/coverage_report.html

- name: Publish to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: .github/agents/test-coverage-enforcer
    destination_dir: coverage
```

### Access Report

```
https://your-org.github.io/your-repo/coverage/coverage_report.html
```

### Key Takeaways

- Visual, interactive HTML reports
- Can be published to GitHub Pages
- Easy to share with non-technical stakeholders
- Color-coded status indicators

---

## Quick Reference

### Common Commands

```bash
# Basic analysis
python -m src.agent analyze --path src/

# Enforce with custom threshold
python -m src.agent enforce --path src/ --threshold 85

# Generate test suggestions
python -m src.agent generate-tests --path src/

# Create JSON report
python -m src.agent report --path src/ --format json --output report.json

# Create HTML report
python -m src.agent report --path src/ --format html --output report.html
```

### Configuration Tips

```yaml
# Strict enforcement for production
thresholds:
  line: 90
  branch: 85
  function: 95
fail_build_below_threshold: true

# Lenient for development
thresholds:
  line: 70
  branch: 60
  function: 75
fail_build_below_threshold: false
auto_generate_tests: true
```

### Troubleshooting

**Issue**: "No coverage data available"
```bash
# Run tests with coverage first
pytest --cov=src --cov-report=json:coverage.json
# Then run enforcement
python -m src.agent enforce --path src/
```

**Issue**: "ModuleNotFoundError"
```bash
# Add agent to PYTHONPATH
export PYTHONPATH="${PWD}/.github/agents/test-coverage-enforcer:${PYTHONPATH}"
```

**Issue**: Too many suggestions generated
```yaml
# In config/agent_config.yaml
advanced:
  max_suggestions_per_file: 5
  min_confidence_threshold: 0.9
```

---

**For more examples, see:**
- [Advanced Patterns](advanced.md)
- [Main Prompts](main.md)
- [README](../README.md)
