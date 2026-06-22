# CLI API Reference

**Last Updated:** 2026-06-22

**Version:** 1.0.0 | **Release Date:** 2026-06-22

## Overview

The Codex CLI provides command-line interfaces for:

- Training models
- Running evaluations
- Managing datasets
- Experiment tracking
- Configuration management

## Main CLI Entry Points

### codex.cli

Main CLI module providing command-line interface entry points.

For detailed CLI documentation, see:

- [CLI Module](../cli.md) - CLI implementation details
- [Reference CLI](../reference/cli.md) - CLI reference documentation
- [API Index](index.md) - Main API documentation index

## Usage

```bash
# View available commands
python -m codex.cli --help

# Train a model
python -m codex.cli train --config configs/train.yaml

# Run evaluation
python -m codex.cli eval --model-path models/best.pt

# Manage datasets
python -m codex.cli dataset --list
```

## Related Documentation

- [CLI Implementation](../cli.md)
- [Reference Documentation](../reference/cli.md)
- [Unified Training](../dev/unified_training.md) - Training guide
- [PEFT Configuration](../guides/peft_configuration.md) - Configuration reference
