# CI Failure Diagnostician Agent

> **Agent Type**: CI/CD Automation
> **Version**: 1.0.0
> **Status**: 🟢 ACTIVE

## Purpose

Auto-diagnose CI failures, classify as flaky/real/infrastructure, and suggest fixes.

## Classification Categories

- **flaky_test**: Intermittent failures, auto-retry
- **real_bug**: Actual code issues, flag for fix
- **infrastructure_issue**: CI environment problems
- **dependency_failure**: Package resolution issues
- **timeout**: Resource exhaustion

## Usage

```bash
python -m agents.ci_failure_diagnostician diagnose --run-id 12345678
```

See `agent.yaml` for configuration.
