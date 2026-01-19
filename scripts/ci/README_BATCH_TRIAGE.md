# Batch CI Failure Triage Tool

## Overview

The Batch CI Failure Triage Tool automates the analysis of multiple post-merge CI/test failures, groups them by root cause, and generates actionable remediation suggestions. This tool addresses the challenge of managing high volumes of unresolved CI failures by providing consolidated triage reports and automated remediation recommendations.

## Features

- **Batch Analysis**: Analyze multiple CI failures simultaneously
- **Intelligent Grouping**: Group failures by root cause, workflow, severity, or failure type
- **Pattern Detection**: Automatically detect common failure patterns using the self-healing engine
- **Remediation Suggestions**: Generate actionable recommendations for each group
- **Multiple Input Methods**: Load failures from GitHub issues, CSV files, or workflow run IDs
- **Multiple Output Formats**: Generate reports in Markdown or JSON format
- **GitHub Integration**: Fetch workflow logs and issue data directly from GitHub

## Installation

The tool is part of the _codex_ repository and requires the following dependencies:

```bash
pip install pyyaml click
```

For GitHub API access, install GitHub CLI:

```bash
# On macOS
brew install gh

# On Linux
# See: https://github.com/cli/cli#installation
```

## Usage

### CLI Command (Integrated)

The tool is integrated into the codex CLI:

```bash
# Using issue numbers
python -m codex batch-triage --issues 2905,2906,2907,2908,2909,2910,2912,2913,2914,2915

# Using CSV file
python -m codex batch-triage --from-file scripts/ci/links_extraction.csv

# With JSON output
python -m codex batch-triage --from-file scripts/ci/links_extraction.csv --json --output report.json

# Group by different strategies
python -m codex batch-triage --issues 2905,2906 --group-by workflow
python -m codex batch-triage --issues 2905,2906 --group-by severity
```

### Direct Script Execution

```bash
# Basic usage with CSV file
python scripts/ci/batch_triage.py --from-file scripts/ci/links_extraction.csv

# Using issue numbers
python scripts/ci/batch_triage.py --issues 2905,2906,2907,2908,2909,2910,2912,2913,2914,2915

# Using workflow run IDs
python scripts/ci/batch_triage.py --workflow-runs 21145572518,21145583258,21145592938

# JSON output
python scripts/ci/batch_triage.py --from-file scripts/ci/links_extraction.csv --json --output report.json

# Different grouping strategies
python scripts/ci/batch_triage.py --from-file scripts/ci/links_extraction.csv --group-by severity
python scripts/ci/batch_triage.py --from-file scripts/ci/links_extraction.csv --group-by workflow
python scripts/ci/batch_triage.py --from-file scripts/ci/links_extraction.csv --group-by failure_type
```

### GitHub Actions Workflow

The tool can be triggered automatically via GitHub Actions:

```bash
# Navigate to: Actions → Batch CI Failure Triage → Run workflow

# Or via GitHub CLI
gh workflow run batch-ci-triage.yml \
  -f issue_numbers="2905,2906,2907,2908,2909,2910,2912,2913,2914,2915" \
  -f group_by="root_cause" \
  -f create_issue="true"
```

The workflow also runs daily on a schedule to check for new failures.

## CSV Input Format

The CSV file should have the following columns:

```csv
Issue #,Issue URL,Failed Workflow Run,Self-Healing Analysis Run
2915,https://github.com/Aries-Serpent/_codex_/issues/2915,https://github.com/Aries-Serpent/_codex_/actions/runs/21145689720,https://github.com/Aries-Serpent/_codex_/actions/runs/21145825936
2914,https://github.com/Aries-Serpent/_codex_/issues/2914,https://github.com/Aries-Serpent/_codex_/actions/runs/21145669711,https://github.com/Aries-Serpent/_codex_/actions/runs/21145823013
```

Alternative column names are also supported:
- `issue_num` instead of `Issue #`
- `issue_url` instead of `Issue URL`
- `workflow_run` instead of `Failed Workflow Run`
- `analysis_run` instead of `Self-Healing Analysis Run`

## Output Format

### Markdown Report

The markdown report includes:

1. **Executive Summary**: Overview of total failures and severity distribution
2. **Grouped Failures**: Failures grouped by the selected strategy with:
   - Root cause description
   - Severity level
   - Affected issues
   - Common patterns
   - Remediation suggestions
3. **Individual Failure Details**: Detailed information for each failure

Example:

```markdown
# Batch CI Failure Triage Report

**Generated:** 2026-01-19 19:30:00 UTC
**Repository:** Aries-Serpent/_codex_
**Total Failures:** 10
**Groups Identified:** 3

## Executive Summary

### Failures by Severity
- 🔴 **CRITICAL**: 2 failures
- 🟠 **HIGH**: 5 failures
- 🟡 **MEDIUM**: 3 failures

## Grouped Failures

### GROUP_1: Missing module: pytest-timeout

**Severity:** HIGH | **Count:** 5 failures

**Affected Issues:**
- #2915 - [Link](https://github.com/Aries-Serpent/_codex_/issues/2915)
- #2914 - [Link](https://github.com/Aries-Serpent/_codex_/issues/2914)
...

**Recommended Actions:**
1. Install missing module: pytest-timeout
2. Update requirements.txt with missing dependencies
3. Run dependency audit
```

### JSON Report

The JSON report provides structured data for programmatic consumption:

```json
{
  "generated_at": "2026-01-19T19:30:00",
  "repository": "Aries-Serpent/_codex_",
  "total_failures": 10,
  "total_groups": 3,
  "groups": [
    {
      "group_id": "group_1",
      "root_cause": "Missing module: pytest-timeout",
      "severity": "high",
      "failure_count": 5,
      "failures": [...],
      "common_patterns": [...],
      "remediation_suggestions": [...]
    }
  ],
  "failures": [...]
}
```

## Grouping Strategies

### root_cause (default)
Groups failures by their root cause (e.g., "Missing module", "Test failure", "Import error")

### workflow
Groups failures by the workflow that failed (e.g., "CI", "RAG Module Tests", "Rust-Python Hybrid Swarm CI/CD")

### severity
Groups failures by severity level (critical, high, medium, low)

### failure_type
Groups failures by failure type (test_failure, import_error, build_failure, etc.)

## Integration with Self-Healing System

The batch triage tool integrates with the existing self-healing infrastructure:

- **Pattern Detection**: Uses `agents/self_healing.py` for pattern matching
- **Remediation Engine**: Leverages `src/codex_ml/utils/self_healing.py` for suggestions
- **Learning System**: Results can feed back into the cognitive brain learning system

## Environment Variables

- `GITHUB_TOKEN` or `GH_TOKEN`: GitHub API token for fetching workflow data
  - Required for accessing workflow logs and issue data
  - Automatically available in GitHub Actions

## Exit Codes

- `0`: Success
- `1`: Error (missing input, analysis failure, etc.)

## Examples

### Example 1: Triage Recent Post-Merge Failures

```bash
# Create CSV with recent failures
cat > recent_failures.csv << EOF
Issue #,Issue URL,Failed Workflow Run
2915,https://github.com/Aries-Serpent/_codex_/issues/2915,https://github.com/Aries-Serpent/_codex_/actions/runs/21145689720
2914,https://github.com/Aries-Serpent/_codex_/issues/2914,https://github.com/Aries-Serpent/_codex_/actions/runs/21145669711
EOF

# Run triage
python scripts/ci/batch_triage.py --from-file recent_failures.csv --output recent_triage.md
```

### Example 2: Group by Severity for Prioritization

```bash
python scripts/ci/batch_triage.py \
  --from-file scripts/ci/links_extraction.csv \
  --group-by severity \
  --output priority_report.md
```

### Example 3: Generate JSON for Automation

```bash
python scripts/ci/batch_triage.py \
  --from-file scripts/ci/links_extraction.csv \
  --json \
  --output triage_data.json

# Process JSON with jq
jq '.groups[] | select(.severity == "critical")' triage_data.json
```

## Troubleshooting

### GitHub CLI Not Found

If you get "gh: command not found":

```bash
# Install GitHub CLI
# macOS: brew install gh
# Linux: See https://github.com/cli/cli#installation

# Authenticate
gh auth login
```

### Missing Logs

If logs cannot be fetched:
- Ensure `GITHUB_TOKEN` or `GH_TOKEN` is set
- Check that workflow runs are accessible
- Verify repository permissions

### Import Errors

If self-healing modules cannot be imported:
- Install the package: `pip install -e .`
- Ensure you're running from the repository root
- The tool will fallback to basic pattern matching if imports fail

## Architecture

```
scripts/ci/batch_triage.py
├── BatchTriageEngine
│   ├── fetch_workflow_logs()      # Get logs from GitHub
│   ├── fetch_issue_data()         # Get issue metadata
│   ├── analyze_failure()          # Analyze individual failure
│   ├── group_failures()           # Group by strategy
│   └── generate_report()          # Create markdown/JSON output
│
├── Integration with agents/self_healing.py
│   ├── SelfHealingEngine.diagnose()
│   ├── Pattern detection
│   └── Remediation suggestions
│
└── Output Formats
    ├── Markdown report
    └── JSON data
```

## Contributing

To enhance the batch triage tool:

1. Add new failure patterns to `agents/self_healing.py`
2. Implement new grouping strategies in `BatchTriageEngine.group_failures()`
3. Extend remediation logic in `_generate_group_remediations()`
4. Add new output formats

## Related Documentation

- [Self-Healing CI Documentation](.github/workflows/self-healing.md)
- [CI Failure Analysis](../../docs/ops/triage_status_failures.md)
- [Self-Healing Engine](../../agents/self_healing.py)

## Author

Codex Team

## Last Updated

2026-01-19
