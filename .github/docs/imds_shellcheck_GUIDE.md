# IMDS ShellCheck Guide

## Overview

This guide explains how to use ShellCheck for linting IMDS shell scripts and maintaining code quality.

## Installation

### Ubuntu/Debian
```bash
sudo apt-get install shellcheck
```

### RHEL/CentOS
```bash
sudo yum install ShellCheck
```

### macOS
```bash
brew install shellcheck
```

## Usage

### Basic Linting

```bash
# Check single script
shellcheck .github/scripts/imds_diagnostic.sh

# Check all scripts
shellcheck .github/scripts/*.sh
```

### With Configuration

The repository includes `.shellcheckrc`:

```bash
# ShellCheck will automatically use .shellcheckrc
shellcheck .github/scripts/imds_diagnostic.sh
```

### CI Integration

The `shellcheck.yml` workflow automatically runs ShellCheck on all shell scripts in pull requests.

## Common Issues

### SC2086: Double quote to prevent globbing
```bash
# ❌ Bad
curl $url

# ✅ Good
curl "$url"
```

### SC2034: Variable unused
```bash
# Add comment to explain
# shellcheck disable=SC2034
unused_var="value"
```

### SC2155: Declare and assign separately
```bash
# ❌ Bad
local result=$(command)

# ✅ Good
local result
result=$(command)
```

## Configuration

See `.shellcheckrc` for project-specific configuration:

```
shell=bash
severity=warning
enable=all
```

## Best Practices

1. Always run ShellCheck before committing
2. Fix all errors and warnings
3. Document any disabled checks
4. Use shellcheck directives sparingly
5. Keep scripts POSIX-compliant where possible

## Resources

- [ShellCheck Wiki](https://github.com/koalaman/shellcheck/wiki)
- [ShellCheck Gallery](https://github.com/koalaman/shellcheck/wiki/Checks)

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15
