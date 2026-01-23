# GitHub Directory README

**⚠️ NOTICE**: This is NOT the main repository README. 

**For complete repository documentation, see**: [../README.md](../README.md)

This directory (`.github/`) contains GitHub-specific configuration files including:
- **Workflows**: CI/CD automation (`.github/workflows/`)
- **Actions**: Custom reusable actions (`.github/actions/`)
- **Agents**: Custom GitHub Copilot agents (`.github/agents/`)
- **Templates**: Issue and PR templates (`.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE/`)

---

## GitHub Actions Status

**Current State**: Workflows are enabled with appropriate guards

- Most workflows use `if: github.event_name == 'workflow_dispatch'` or similar guards
- Safety mechanisms in place (SAFE_MODE, autonomous_actions_enabled: false)
- Genesis Protocol awaiting secret injection by repository maintainer
- See [Genesis Setup Guide](../docs/admin/GENESIS_SETUP_GUIDE.md) for details

---

## Quick Links

- **Main Repository README**: [../README.md](../README.md)
- **Contributing Guide**: [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **Security Policy**: [../SECURITY.md](../SECURITY.md)
- **Agent Documentation**: [../AGENTS.md](../AGENTS.md)
- **Documentation Index**: [../docs/DOCUMENTATION_INDEX.md](../docs/DOCUMENTATION_INDEX.md)
