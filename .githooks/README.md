# Git Hooks Setup

Configuration validation hooks for the _codex_ repository.

## Setup

Enable hooks:
```bash
git config core.hooksPath .githooks
```

## Available Hooks

- **pre-commit**: Validates Cargo.toml and other config files

## Usage

Hooks run automatically. To bypass:
```bash
git commit --no-verify
```

For help:
```
@copilot Use the Rust Configuration Validator agent
```
