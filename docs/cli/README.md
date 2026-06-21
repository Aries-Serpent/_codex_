# CLI Documentation

This directory contains documentation for the command-line interface (CLI) tools provided by _codex_.

## Contents

### CLI Reference
- **[CLI Overview](../CLI.md)** - Introduction to CLI tools
- **[CLI Status Audit](./status_audit.md)** - Complete CLI status
- **[Dataset CLI](./dataset_cli.md)** - Dataset management commands
- **[Minimal Workflow](./minimal_train_eval_workflow.md)** - Quick start workflow

### Getting Started
- CLI installation instructions
- Basic usage examples
- Configuration files
- Environment setup

### Advanced Topics
- Advanced command options
- Custom scripts
- Automation
- Integration with CI/CD

## Quick Reference

### Common Commands

```bash
# Show help
codex --help

# Initialize project
codex init

# Run training
codex train --config config.yaml

# Evaluate model
codex evaluate --model model.pth

# Deploy model
codex deploy --model model.pth
```

### Command Structure

All CLI commands follow the pattern:
```
codex <command> <subcommand> [options] [arguments]
```

### Global Options

- `--help` / `-h`: Show help message
- `--version` / `-V`: Show version
- `--verbose` / `-v`: Enable verbose output
- `--config`: Specify configuration file
- `--debug`: Enable debug mode

## CLI Tools

### Main Tool: codex
Core functionality for model training, evaluation, and deployment.

### Cognitive Brain Console
Interactive console for prompt engineering and testing.

### MCP Packager
Package management and distribution tool.

## Tutorials

### Getting Started
1. [Installation Instructions](README.md)
2. [Status Audit](./status_audit.md)
3. [Dataset CLI](./dataset_cli.md)
4. [Minimal Workflow](./minimal_train_eval_workflow.md)

### Advanced Usage
1. [Status and Audit Information](./status_audit.md)
2. [Dataset Management](./dataset_cli.md)
3. [Workflow Examples](./minimal_train_eval_workflow.md)

## Troubleshooting

### Common Issues

**Command not found**
```bash
# Verify installation
pip list | grep codex

# Reinstall if needed
pip install -e .
```

**Configuration errors**
- Check configuration file syntax (YAML format)
- Verify all required fields are present
- Review documentation for field requirements

**Output issues**
- Use `--verbose` flag for detailed output
- Check log files in `.codex/logs/`
- Enable debug mode with `--debug`

## Environment Variables

Key environment variables for CLI:
- `CODEX_HOME`: Base directory for codex files (default: `~/.codex`)
- `CODEX_CONFIG`: Default configuration file path
- `CODEX_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CODEX_PARALLEL_JOBS`: Number of parallel jobs

## Best Practices

- Use configuration files for reproducibility
- Enable verbose output when troubleshooting
- Keep logs for audit purposes
- Use version-specific commands when needed
- Test commands in dry-run mode first

## Related Documentation

- [Configuration Guide](../configuration/)
- [API Reference](../api/)
- [Deployment Guide](../deployment/)
- [Development Guide](../development/)

## Maintenance

Last updated: 2026-06-20
Status: Active
Owner: @mbaetiong

For CLI issues, check troubleshooting section or open an issue on GitHub.
