# CI Testing Agent

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: Previous Cycle-12-31

## Overview

The CI Testing Agent is a specialized tool designed for debugging CI/CD pipeline issues, generating test scaffolds, validating coverage, and executing tests in isolated environments.

## Features

- **Test Generation**: Automatically generate test scaffolds for uncovered code
- **Coverage Validation**: Validate test coverage meets target thresholds
- **Sandbox Execution**: Execute tests in isolated environments with timeout and resource controls
- **CI Debugging**: Debug CI pipeline failures with detailed analysis
- **Artifact Reporting**: Generate JSON and Markdown reports of test results

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python cli.py --help
```

### Basic Usage

```bash
# Generate tests
python cli.py \
  --manifest manifest.yaml \
  --task '{"type": "generate_tests", "module": "mymodule", "threshold": 85}'

# Validate coverage
python cli.py \
  --manifest manifest.yaml \
  --task '{"type": "validate_coverage", "threshold": 85}'

# Execute tests
python cli.py \
  --manifest manifest.yaml \
  --task '{"type": "execute_tests", "command": "pytest", "args": ["tests/"]}'
```

## Directory Structure

```
ci-testing-agent/
├── agent/                      # Core agent modules
│   ├── generator.py            # Test scaffolding logic
│   ├── executor.py             # Sandbox command runner
│   ├── validator.py            # Coverage delta evaluator
│   └── reporter.py             # Artifact uploader & reporting
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests with mocked dependencies
│   ├── contract/               # Request/response schema validation
│   └── integration/            # End-to-end sandbox tests
├── docs/                       # Documentation
│   └── runbook.md              # Operations guide
├── cli.py                      # CLI entry point
├── manifest.yaml               # Agent configuration
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Container specification
```

## Task Types

### 1. Generate Tests

Generate test scaffolds for uncovered code paths.

```json
{
  "type": "generate_tests",
  "module": "codex.ingest",
  "threshold": 85,
  "output_dir": "tests"
}
```

### 2. Validate Coverage

Validate test coverage meets target threshold.

```json
{
  "type": "validate_coverage",
  "baseline": "baseline_coverage.txt",
  "threshold": 85,
  "modules": ["codex.ingest"]
}
```

### 3. Execute Tests

Execute tests in sandboxed environment.

```json
{
  "type": "execute_tests",
  "command": "pytest",
  "args": ["tests/", "-v"],
  "timeout": 300
}
```

### 4. Debug CI Failure

Debug CI pipeline failures.

```json
{
  "type": "debug_ci_failure",
  "command": "pytest",
  "args": ["tests/", "--tb=short"]
}
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=agent --cov-report=html
```

**Test Results**:
- ✅ 49 unit tests passing
- ✅ 11 contract tests passing
- ✅ 6 integration tests passing
- ✅ Total: 66/66 tests passing

## Docker Support

```bash
# Build image
docker build -t ci-testing-agent:latest .

# Run agent
docker run -v $(pwd):/workspace ci-testing-agent:latest \
  --manifest /workspace/manifest.yaml \
  --task '{"type": "generate_tests", "module": "mymodule"}'
```

## Documentation

- **[Runbook](docs/runbook.md)**: Complete operational guide
- **[Agent Documentation](../ci-testing-agent.md)**: Detailed agent specification
- **[Implementation Plan](../CI_TESTING_AGENT_IMPLEMENTATION_PLAN.md)**: Development roadmap

## Architecture

The agent follows a modular architecture with four core components:

```
┌─────────────┐
│   CLI       │  Entry point (cli.py)
└──────┬──────┘
       │
  ┌────┴────┬──────────┬───────────┐
  │         │          │           │
┌─▼───────┐ ┌▼────────┐ ┌▼────────┐ ┌▼────────┐
│Generator│ │Executor │ │Validator│ │Reporter │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

## Configuration

**manifest.yaml**:
```yaml
name: CI Testing Agent
version: 1.0.0
capabilities:
  - ci_pipeline_debugging
  - test_failure_analysis
  - import_path_resolution
runtime:
  python_version: "3.12"
  base_image: "python:3.12-slim"
```

## Requirements

- Python 3.12+
- pytest 8.0.0+
- pytest-cov 4.1.0+
- PyYAML 6.0+
- GitPython 3.1.0+

## Maintainers

- CI Testing Agent Team
- Contact: Submit GitHub Issues

## License

Part of the _codex_ repository.

---

**Status**: ✅ All systems operational  
**Last Test Run**: Previous Cycle-12-31  
**Test Coverage**: 66/66 tests passing
