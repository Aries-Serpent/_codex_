# Code Style Guide

This document complements the automation enforced by `pre-commit`.

## Python

- Format code with **Black** (line length 100) and rely on **Ruff** to lint and fix
  additional issues, including import sorting via the `I` family of rules.
- Run **isort** for focused import ordering when working outside of Ruff automation.
- Run **mypy** locally before submitting security sensitive changes. Type coverage is
  progressively expanding; new modules should not disable type checking.

## Documentation

- Wrap Markdown at ~100 characters when practical.
- Prefer lists and tables for configuration changes so release notes can be generated
  mechanically.

## Testing

- Execute targeted `pytest` invocations in addition to the required `nox -s tests`
  session when authoring new modules. Keep tests deterministic and avoid external
  network calls.
