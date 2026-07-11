# Monitoring Scripts

Automated workflow monitoring and artifact analysis for GitHub Actions.

## Setup

Install monitoring dependencies:

```bash
# Option 1: GitHub monitoring tools only
pip install -e ".[github]"

# Option 2: All monitoring tools (includes Prometheus, psutil, etc.)
pip install -e ".[monitoring]"
```

## Scripts

### artifact_monitor.py

Monitors GitHub Actions workflows and creates issues for failures.

**Requirements:** PyGithub >= 2.1.1

**Usage:**
```bash
# Check all workflows
python scripts/monitoring/artifact_monitor.py

# Check specific workflow
python scripts/monitoring/artifact_monitor.py --workflow test-suite.yml

# Dry run (no issues created)
python scripts/monitoring/artifact_monitor.py --dry-run

# Verbose output
python scripts/monitoring/artifact_monitor.py --verbose

# Specify custom config
python scripts/monitoring/artifact_monitor.py --config ./.codex/config/monitoring.yaml

# Specify state file location
python scripts/monitoring/artifact_monitor.py --state .codex/monitoring/state/monitor_state.json
```

**Environment Variables:**
- `GITHUB_TOKEN`: GitHub API token (required)
- `GITHUB_REPOSITORY`: Repository in format `owner/repo` (default: Aries-Serpent/_codex_)
- `CODEX_MASTER_KEY`: Optional fallback token for authenticated operations

**CLI Flags:**
- `--config PATH`: Path to monitoring configuration file (default: ./.codex/config/monitoring.yaml)
- `--state PATH`: Path to state file for tracking monitoring history (default: .codex/monitoring/state/monitor_state.json)
- `--dry-run`: Run without creating GitHub issues (testing mode)
- `--verbose`: Enable detailed logging output
- `--workflow NAME`: Monitor a specific workflow file only
- `--check`: Perform a single check and exit

### agent_orchestrator.py

Orchestrates multiple monitoring agents and coordinates their activities.

**Requirements:** PyGithub >= 2.1.1

**Usage:**
```bash
# Run agent orchestrator
python scripts/monitoring/agent_orchestrator.py

# With custom config
python scripts/monitoring/agent_orchestrator.py --config ./.codex/config/monitoring.yaml
```

### pattern_analyzer.py

Analyzes workflow failure patterns and identifies trends.

**Usage:**
```bash
# Analyze failure patterns
python scripts/monitoring/pattern_analyzer.py

# Generate trend report
python scripts/monitoring/pattern_analyzer.py --report
```

### issue_manager.py

Manages GitHub issues created by monitoring systems.

**Usage:**
```bash
# List monitoring-related issues
python scripts/monitoring/issue_manager.py list

# Close resolved issues
python scripts/monitoring/issue_manager.py close --issue-id 12345
```

## Configuration

See `./.codex/config/monitoring.yaml` for configuration options:

```yaml
monitoring:
  workflows:
    include_patterns:
      - "*"  # Monitor all workflows
    exclude_patterns:
      - "pages-*"  # Exclude GitHub Pages workflows

  failure_detection:
    consecutive_failures_threshold: 2  # Create issue after N consecutive failures
    rate_limit_margin: 500  # Reserve 500 API calls for safety
```

## Workflow Integration

The artifact monitoring workflow runs automatically every 3 hours and can be triggered manually:

```bash
# Trigger workflow manually
gh workflow run artifact-monitoring.yml -f dry_run=true

# Monitor the run
gh run watch

# Check logs
gh run view --log
```

## Development

### Testing Locally

```bash
# Install development dependencies
pip install -e ".[dev,github]"

# Set up test environment
export GITHUB_TOKEN="your_test_token"
export GITHUB_REPOSITORY="Aries-Serpent/_codex_"

# Run with dry-run mode
python scripts/monitoring/artifact_monitor.py --dry-run --verbose
```

### Configuration Validation

```bash
# Validate monitoring configuration
python validate_monitoring_config.py

# Expected output: ✅ Configuration validation PASSED!
```

## Troubleshooting

### PyGithub Not Found

```bash
# Install the github dependency group
pip install -e ".[github]"

# Verify installation
python -c "import github; print(f'PyGithub {github.__version__}')"
```

### Rate Limit Exceeded

The monitoring script automatically handles rate limits with exponential backoff. To check your current rate limit:

```bash
gh api rate_limit
```

### Configuration Errors

If you encounter configuration errors:

```bash
# Validate the config structure
python validate_monitoring_config.py

# Check YAML syntax
yamllint ./.codex/config/monitoring.yaml
```

## Security Considerations

- **Never commit tokens**: Use environment variables or GitHub Secrets
- **Rate limiting**: Monitor API usage to avoid hitting GitHub rate limits
- **Permissions**: Ensure GITHUB_TOKEN has `issues:write` and `actions:read` permissions

## Related Documentation

- [Monitoring Configuration](./.codex/config/monitoring.yaml)
- [Artifact Monitoring Workflow](./.github/workflows/artifact-monitoring.yml)
- [PyGithub Installation Plan](./.codex/plans/pygithub_installation_plan.md)
- [Phase 32 Continuation Prompt](.codex/cognitive_brain/PHASE_32_CONTINUATION_PROMPT.md)

## Support

For issues or questions:
- Check [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
- Review [PyGithub Documentation](https://pygithub.readthedocs.io/)
- Contact: @mbaetiong

---

**Version:** 1.0.0  
**Created:** 2026-01-26  
**Status:** ✅ Production Ready
