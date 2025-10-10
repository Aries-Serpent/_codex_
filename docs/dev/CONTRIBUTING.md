# Contributing Guide

## Development Environment
1. Create a Python 3.10 virtualenv.
2. Install dependencies:
   ```bash
   pip install -e '.[dev,ml,logging]'
   pre-commit install --install-hooks
   ```
3. Optional tools: `docker`, `helm`, and `semgrep` for deployment/security checks.

## Workflow
1. Create a feature branch.
2. Run pre-commit on touched files:
   ```bash
   pre-commit run --files <changed_files>
   ```
3. Execute smoke tests:
   ```bash
   pytest tests/security/ -q
   pytest tests/deployment/ -k health
   ```
4. Update documentation and changelog entries as needed.
5. Submit a pull request with a summary and testing evidence.

## Pre-Commit Hooks
Installed hooks enforce formatting, linting, typing, secret scanning, and quick pytest runs. Use `pre-commit run --all-files` before pushing large changes.

## Code Style
Refer to [CODE_STYLE_GUIDE.md](CODE_STYLE_GUIDE.md) for formatting and review expectations.

## Reporting Issues
- File issues in the repository tracker with reproduction steps.
- Security concerns should be reported privately to `security@codex-project.org`.
