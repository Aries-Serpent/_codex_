# Copilot Agent Firewall Configuration

> **Version:** 1.0.0  
> **Last Updated:** 2025-12-17

## Overview

This document describes the firewall allowlist configuration required for the GitHub Copilot coding agent to function properly in this repository.

## Required Firewall Allowlist

The following URLs/hosts must be added to the custom allowlist in this repository's [Copilot coding agent settings](https://github.com/Aries-Serpent/_codex_/settings/copilot/coding_agent) (admins only):

### GitHub API Access

| Host | Purpose |
|------|---------|
| `api.github.com` | Required for accessing issue comments, PR comments, and other GitHub API operations |

### Package Managers

| Host | Purpose |
|------|---------|
| `pypi.org` | Python Package Index for pip install |
| `files.pythonhosted.org` | Python package downloads |
| `astral.sh` | UV package manager installer |

### Other Services

| Host | Purpose |
|------|---------|
| `objects.githubusercontent.com` | GitHub raw file downloads |
| `raw.githubusercontent.com` | GitHub raw content access |

## Alternative: Actions Setup Steps

Instead of adding URLs to the allowlist, you can configure [Actions setup steps](https://docs.github.com/en/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent) to set up the environment before the firewall is enabled.

### Example Setup Step

```yaml
# .github/actions/copilot-setup-steps/action.yml
name: Copilot Setup Steps
description: Pre-firewall environment setup for Copilot agent

runs:
  using: composite
  steps:
    - name: Install dependencies
      shell: bash
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
```

## Troubleshooting

If you see firewall blocking errors like:

```
I tried to connect to the following addresses, but was blocked by firewall rules:
- https://api.github.com/repos/Aries-Serpent/_codex_/issues/comments/...
```

### Resolution Options

1. **For Repository Admins**: Add the blocked host to the allowlist in [Copilot coding agent settings](https://github.com/Aries-Serpent/_codex_/settings/copilot/coding_agent)

2. **For Contributors**: Request an admin to add the required host to the allowlist

3. **Use Setup Steps**: Configure pre-firewall setup in `.github/actions/copilot-setup-steps/action.yml`

## Security Considerations

- Only allowlist hosts that are necessary for the Copilot agent to function
- Review the allowlist periodically to remove unused entries
- The firewall is in place to prevent unauthorized network access from the agent sandbox
- All network operations should be auditable and traceable

## References

- [GitHub Copilot coding agent documentation](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-for-pull-requests)
- [Customizing the development environment](https://docs.github.com/en/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent)
