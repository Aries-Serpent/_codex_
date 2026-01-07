# CI Testing Agent Runbook

## Overview

The CI Testing Agent is a specialized tool for debugging CI/CD pipeline issues, generating test scaffolds, validating coverage, and executing tests in isolated environments.

**Version**: 1.0.0  
**Last Updated**: 2024-12-31

---

## Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Task Types](#task-types)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Architecture

### Components

```
┌─────────────────┐
│    cli.py       │  Entry point
└────────┬────────┘
         │
    ┌────┴────┬───────────┬────────────┐
    │         │           │            │
┌───▼────┐ ┌─▼────────┐ ┌▼─────────┐ ┌▼─────────┐
│Generator│ │ Executor │ │Validator │ │ Reporter │
└─────────┘ └──────────┘ └──────────┘ └──────────┘
```

**TestGenerator** (`agent/generator.py`)
- Extracts functions from source code using AST
- Generates test scaffolds with AAA pattern
- Checks for existing test coverage

**SandboxExecutor** (`agent/executor.py`)
- Executes commands in isolated environment
- Manages timeouts and resource limits
- Validates command safety

**CoverageValidator** (`agent/validator.py`)
- Parses coverage reports
- Computes coverage deltas
- Identifies coverage gaps

**ArtifactReporter** (`agent/reporter.py`)
- Generates JSON and Markdown reports
- Creates summaries and artifacts
- Integrates with GitHub (placeholders)

---

## Installation

### Local Installation

```bash
cd .github/agents/ci-testing-agent

# Install dependencies
pip install -r requirements.txt

# Verify installation
python cli.py --help
```

### Docker Installation

```bash
cd .github/agents/ci-testing-agent

# Build image
docker build -t ci-testing-agent:latest .

# Test image
docker run ci-testing-agent:latest --help
```

---

## Usage

### Direct Invocation

```bash
python cli.py \
  --manifest manifest.yaml \
  --task '{"type": "generate_tests", "module": "codex.ingest", "threshold": 85}' \
  --workspace /path/to/repo
```

### Docker Invocation

```bash
docker run \
  -v /path/to/repo:/workspace \
  ci-testing-agent:latest \
  --manifest /workspace/manifest.yaml \
  --task '{"type": "generate_tests", "module": "codex.ingest"}' \
  --workspace /workspace
```

### GitHub Copilot Integration

```
@copilot use ci-testing-agent to generate tests for module codex.ingest
```

---

## Task Types

### 1. Generate Tests

Generate test scaffolds for uncovered code paths.

**Request**:
```json
{
  "type": "generate_tests",
  "module": "codex.ingest",
  "threshold": 85,
  "output_dir": "tests"
}
```

**Response**:
```json
{
  "status": "success",
  "files_generated": 5,
  "test_files": [
    {
      "path": "tests/test_func.py",
      "content": "...",
      "function": "func_name",
      "source_file": "src/module.py"
    }
  ],
  "module": "codex.ingest",
  "threshold": 85
}
```

**Example**:
```bash
python cli.py \
  --manifest manifest.yaml \
  --task '{"type": "generate_tests", "module": "codex.ingest", "threshold": 85}'
```

---

### 2. Validate Coverage

Validate test coverage meets target threshold.

**Request**:
```json
{
  "type": "validate_coverage",
  "baseline": "baseline_coverage.txt",
  "threshold": 85,
  "modules": ["codex.ingest", "codex.process"]
}
```

**Response**:
```json
{
  "status": "success",
  "baseline_coverage": 80.0,
  "current_coverage": 87.5,
  "delta": 7.5,
  "threshold": 85,
  "meets_threshold": true,
  "gaps": [],
  "module_coverage": {
    "module1.py": 90.0,
    "module2.py": 85.0
  }
}
```

**Example**:
```bash
python cli.py \
  --manifest manifest.yaml \
  --task '{"type": "validate_coverage", "threshold": 85, "baseline": "baseline.txt"}'
```

---

### 3. Execute Tests

Execute test commands in sandboxed environment.

**Request**:
```json
{
  "type": "execute_tests",
  "command": "pytest",
  "args": ["tests/", "-v", "--cov"],
  "env": {"PYTHONPATH": "/workspace/src"},
  "timeout": 300
}
```

**Response**:
```json
{
  "status": "success",
  "returncode": 0,
  "stdout": "Test output...",
  "stderr": "",
  "command": "pytest tests/ -v --cov"
}
```

**Example**:
```bash
python cli.py \
  --manifest manifest.yaml \
  --task '{"type": "execute_tests", "command": "pytest", "args": ["tests/"]}'
```

---

### 4. Debug CI Failure

Debug CI pipeline failures by executing and analyzing tests.

**Request**:
```json
{
  "type": "debug_ci_failure",
  "command": "pytest",
  "args": ["tests/", "--tb=short", "-x"],
  "workflow_run_id": 12345
}
```

**Response**:
```json
{
  "status": "failure",
  "returncode": 1,
  "stdout": "...",
  "stderr": "ImportError: No module named 'X'",
  "command": "pytest tests/ --tb=short -x",
  "task_type": "debug_ci_failure"
}
```

---

## Configuration

### Manifest Structure

```yaml
name: CI Testing Agent
version: 1.0.0
description: Agent for CI/CD debugging

capabilities:
  - ci_pipeline_debugging
  - test_failure_analysis
  - import_path_resolution

runtime:
  python_version: "3.12"
  base_image: "python:3.12-slim"
  dependencies:
    - pytest>=8.0.0
    - pytest-cov>=4.1.0

entry_point: cli.py
```

### Environment Variables

- `PYTHONPATH`: Python module search path
- `CODEX_ENV_*`: Environment-specific configuration
- `GITHUB_TOKEN`: GitHub API authentication (for integrations)

---

## Troubleshooting

### Import Errors

**Symptom**: `ImportError: No module named 'X'`

**Solutions**:
1. Check PYTHONPATH is set correctly
2. Verify module is installed: `pip list | grep X`
3. Check package structure in `pyproject.toml`
4. Ensure src/ layout is configured properly

**Example Fix**:
```bash
export PYTHONPATH="/workspace/src:${PYTHONPATH}"
python cli.py --task '...'
```

---

### Timeout Issues

**Symptom**: Command times out after 300s

**Solutions**:
1. Increase timeout in task: `"timeout": 600`
2. Reduce test scope: limit to specific modules
3. Use parallel execution: `pytest -n auto`

**Example**:
```json
{
  "type": "execute_tests",
  "command": "pytest",
  "args": ["tests/unit/"],
  "timeout": 600
}
```

---

### Coverage Calculation

**Symptom**: Coverage not calculated correctly

**Solutions**:
1. Ensure coverage.json is generated: `pytest --cov-report=json`
2. Check baseline file format matches expected pattern
3. Verify modules are being tested

**Debug Commands**:
```bash
# Generate coverage manually
pytest --cov=src --cov-report=term --cov-report=json

# Check coverage.json
cat coverage.json | jq '.totals.percent_covered'
```

---

### Missing Test Files

**Symptom**: Test generation produces no files

**Solutions**:
1. Verify module path exists in src/
2. Check module contains public functions (not starting with _)
3. Ensure functions aren't already tested

**Debug**:
```python
from agent.generator import TestGenerator
gen = TestGenerator(workspace=Path("."))
functions = gen._extract_functions(Path("src/module"))
print(functions)
```

---

## Maintenance

### Updating Dependencies

```bash
# Update requirements.txt
pip install --upgrade pytest pytest-cov

# Regenerate requirements.txt
pip freeze > requirements.txt

# Rebuild Docker image
docker build -t ci-testing-agent:latest .
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Contract tests
pytest tests/contract/ -v

# Integration tests
pytest tests/integration/ -v

# All tests
pytest tests/ -v --cov=agent --cov-report=html
```

### Monitoring

**Key Metrics**:
- Task success rate
- Average execution time
- Coverage improvement delta
- Test generation count

**Log Locations**:
- JSON reports: `.reports/report_*.json`
- Markdown summaries: `.reports/summary_*.md`
- Latest summary: `.reports/summary_latest.md`

### Version Updates

1. Update `__version__` in `agent/__init__.py`
2. Update `version` in `manifest.yaml`
3. Update CHANGELOG.md
4. Tag release: `git tag v1.x.x`
5. Rebuild Docker image with new tag

---

## Advanced Usage

### Parallel Test Execution

```json
{
  "type": "execute_tests",
  "command": "pytest",
  "args": ["-n", "4", "tests/"]
}
```

### Custom Coverage Modules

```json
{
  "type": "validate_coverage",
  "threshold": 90,
  "modules": [
    "codex.ingest",
    "codex.process",
    "codex.export"
  ]
}
```

### Generating HTML Reports

```python
from agent.validator import CoverageValidator

validator = CoverageValidator(workspace=Path("."))
report_path = validator.generate_coverage_report()
print(f"Report: {report_path}")
```

---

## Contact

**Maintainer**: CI Testing Agent Team  
**Issues**: Submit via GitHub Issues  
**Documentation**: `.github/agents/ci-testing-agent.md`

---

## References

- [CI Testing Agent Documentation](../ci-testing-agent.md)
- [Implementation Plan](../CI_TESTING_AGENT_IMPLEMENTATION_PLAN.md)
- [pytest Documentation](https://docs.pytest.org/)
- [coverage.py Documentation](https://coverage.readthedocs.io/)
