# CLI Tools

Command-line interface tools for CODEX operations.

## Overview

This module provides CLI utilities for:
- Configuration management
- Session logging
- Environment provisioning
- Task execution

## Usage

```bash
python -m codex.cli --help
```

## Available Commands

### Configuration
- `config` - Manage configuration settings
- `init` - Initialize new CODEX project

### Logging
- `log` - View and manage session logs
- `query` - Query conversation transcripts

### Environment
- `env` - Manage environment variables
- `setup` - Setup development environment

## Module Structure

```
src/cli/
├── __init__.py
├── config.py
├── logging.py
└── environment.py
```

## Development

See [Development Guide](../../docs/DEVELOPMENT.md) for contributing guidelines.

## Related Documentation

- [Audit Pipeline](../../src/codex_ml/cli/audit_pipeline.py)
- [Session Logger](../codex/logging/session_logger.py)
- [Configuration Guide](../../docs/CONFIGURATION.md)
