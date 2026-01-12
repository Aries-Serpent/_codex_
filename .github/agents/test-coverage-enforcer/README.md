# Test Coverage Enforcer Agent

> Enforces test coverage thresholds, identifies uncovered code paths, and automatically generates missing tests to maintain quality standards.

## Overview

The Test Coverage Enforcer Agent is a specialized GitHub Copilot agent designed to maintain high code quality through automated test coverage enforcement. It analyzes your codebase, identifies coverage gaps, enforces configurable thresholds, and can automatically generate test templates to improve coverage.

### Key Features

- **📊 Coverage Tracking**: Monitor line, branch, and function coverage metrics
- **🎯 Threshold Enforcement**: Enforce minimum coverage requirements in CI/CD pipelines
- **🧪 Test Generation**: Automatically generate test templates for uncovered code
- **📈 Trend Analysis**: Track coverage changes over time
- **🔍 Gap Detection**: Identify specific uncovered lines, branches, and functions
- **📝 Comprehensive Reporting**: Generate reports in text, JSON, and HTML formats
- **🧠 Cognitive Brain Integration**: Store metrics for long-term analysis

## Capabilities

| Capability | Description |
|------------|-------------|
| Coverage Tracking | Real-time monitoring of test coverage metrics |
| Threshold Enforcement | Automatic enforcement of coverage requirements |
| Test Generation | AI-powered test template generation |
| Trend Analysis | Historical coverage tracking and analysis |
| Gap Detection | Precise identification of uncovered code paths |
| Priority Calculation | Smart prioritization of testing efforts |

## Quick Start

### Installation

The agent is automatically available in the `_codex_` repository. No additional installation is required.

### Basic Usage

#### Analyze Coverage

```bash
cd .github/agents/test-coverage-enforcer
python -m src.agent analyze --path src/
```

#### Enforce Thresholds

```bash
python -m src.agent enforce --path src/ --threshold 80
```

#### Generate Test Suggestions

```bash
python -m src.agent generate-tests --path src/
```

#### Generate Reports

```bash
# Text report
python -m src.agent report --path src/ --format text

# JSON report
python -m src.agent report --path src/ --format json --output coverage.json

# HTML report
python -m src.agent report --path src/ --format html --output coverage.html
```

## GitHub Actions Integration

### Using as a Composite Action

Add to your workflow:

```yaml
name: Test Coverage Enforcement

on:
  push:
    branches: [main]
  pull_request:

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Enforce Coverage
        uses: ./.github/agents/test-coverage-enforcer
        with:
          check-coverage: true
          threshold: 80
          fail-below-threshold: true
          source-path: src
          output-format: html
```

### Workflow Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `check-coverage` | Whether to check coverage | `true` |
| `threshold` | Minimum coverage percentage | `80` |
| `auto-generate` | Generate test templates | `false` |
| `fail-below-threshold` | Fail build if below threshold | `true` |
| `source-path` | Path to source code | `src` |
| `config-path` | Path to config file | `config/agent_config.yaml` |
| `output-format` | Report format (text/json/html) | `text` |

### Workflow Outputs

| Output | Description |
|--------|-------------|
| `coverage-percentage` | Current overall coverage |
| `passed` | Whether enforcement passed |
| `issues-found` | Number of coverage issues |
| `suggestions-generated` | Number of test suggestions |

## Configuration

### Configuration File

Create `.github/agents/test-coverage-enforcer/config/agent_config.yaml`:

```yaml
thresholds:
  line: 80          # Minimum line coverage
  branch: 70        # Minimum branch coverage
  function: 85      # Minimum function coverage

auto_generate_tests: false
fail_build_below_threshold: true

reporting:
  formats: [text, json, html]
  output_directory: .coverage_reports

cognitive_brain:
  enabled: true
  metrics:
    - coverage_percentage
    - gap_count
    - tests_generated
```

### Customization Options

- **Thresholds**: Set different minimum coverage requirements
- **Auto-generation**: Enable/disable automatic test template creation
- **Build Behavior**: Choose whether to fail builds on low coverage
- **Reporting**: Configure output formats and locations
- **File Patterns**: Include/exclude specific files or directories

## File Structure

```
test-coverage-enforcer/
├── src/
│   ├── __init__.py
│   └── agent.py              # Main agent implementation
├── tests/
│   ├── __init__.py
│   ├── test_agent.py         # Unit tests (15+ tests)
│   └── test_integration.py   # Integration tests
├── config/
│   └── agent_config.yaml     # Default configuration
├── prompts/
│   ├── main.md              # Core agent prompt
│   ├── examples.md          # Usage examples
│   └── advanced.md          # Advanced patterns
├── agent.yaml               # GitHub Actions composite action
├── README.md                # This file
└── CHANGELOG.md             # Version history
```

## Component Reuse Strategy

The Test Coverage Enforcer Agent follows a component reuse strategy to maximize efficiency:

### Base Component (80% reuse)
- **Source**: `test-coverage-monitor` agent
- **Reused capabilities**:
  - Coverage data collection
  - Metric calculation
  - Report generation
  - File analysis

### Extensions
1. **test-alignment-fixer**: Auto-test generation capabilities
2. **integration-test-runner**: Enforcement workflow integration

This approach ensures:
- Consistent coverage tracking across agents
- Reduced maintenance burden
- Shared improvements benefit multiple agents
- Specialized enforcement and generation features

## CLI Reference

### Commands

```bash
# Analyze coverage
python -m src.agent analyze --path <path> [--threshold <percent>]

# Enforce thresholds
python -m src.agent enforce --path <path> [--threshold <percent>]

# Generate test suggestions
python -m src.agent generate-tests --path <path> [--format text|json]

# Generate report
python -m src.agent report --path <path> --format <format> [--output <file>]
```

### Options

- `--path`: Path to analyze (file or directory)
- `--threshold`: Coverage threshold percentage (default: from config)
- `--format`: Output format (text, json, html)
- `--output`: Output file path
- `--config`: Custom configuration file path

## Success Criteria

The agent achieves success when:

1. ✅ **Coverage Tracked**: All specified files are analyzed
2. ✅ **Thresholds Enforced**: Build fails when coverage < threshold
3. ✅ **Gaps Identified**: All uncovered code paths are detected
4. ✅ **Suggestions Generated**: Test templates provided for uncovered code
5. ✅ **Reports Generated**: Human-readable reports in requested format
6. ✅ **Metrics Stored**: Coverage data persisted for trend analysis

## Best Practices

1. **Set Realistic Thresholds**: Start with achievable coverage targets
2. **Gradual Improvement**: Increase thresholds incrementally
3. **Review Suggestions**: Manually review generated test templates
4. **Exclude Appropriately**: Exclude generated code and vendor files
5. **Monitor Trends**: Track coverage changes over time
6. **Integrate Early**: Add to CI/CD from project start

## Troubleshooting

### Common Issues

**Issue**: Coverage data not found
- **Solution**: Ensure pytest-cov is installed and tests are run first

**Issue**: Agent fails to import
- **Solution**: Check PYTHONPATH includes agent directory

**Issue**: Thresholds too strict
- **Solution**: Adjust thresholds in config file

**Issue**: Too many suggestions generated
- **Solution**: Increase threshold or set `max_suggestions_per_file` in config

## Related Documentation

- [Main Agent Prompts](prompts/main.md)
- [Usage Examples](prompts/examples.md)
- [Advanced Patterns](prompts/advanced.md)
- [Changelog](CHANGELOG.md)

## Support

For issues, questions, or contributions:
- Open an issue in the repository
- Review existing documentation
- Check CHANGELOG for recent changes

## License

Part of the Aries-Serpent/_codex_ project.

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-12  
**Maintained By**: Codex Team
