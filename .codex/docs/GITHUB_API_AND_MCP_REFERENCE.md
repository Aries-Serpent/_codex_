# GitHub API & MCP Reference — Cognitive Brain Knowledge Entry

> **Last verified:** 2026-08-01 | **Runtime inventory verified**  
> **Loaded by:** CB session injector, agent-auth-delegation.yml cognitive-preflight job  
> **Primary doc:** `docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md`

This file is the Cognitive Brain's entry point for GitHub API and MCP server knowledge.
Agents MUST read `docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md` for the full
reference. This file provides a quick-access summary and wiring map.

---

## Quick-Access: Token Chain (always use this)

```yaml
GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
```

---

## Quick-Access: Variable / Secret Operations

```bash
# READ a repo variable
gh api /repos/Aries-Serpent/_codex_/actions/variables/VAR_NAME --jq '.value'

# WRITE a repo variable
gh api PATCH /repos/Aries-Serpent/_codex_/actions/variables/VAR_NAME \
  -f name='VAR_NAME' -f value='new_value'

# SET a secret (handles encryption automatically)
gh secret set SECRET_NAME --repo Aries-Serpent/_codex_

# CANCEL a workflow run
gh api POST /repos/Aries-Serpent/_codex_/actions/runs/$RUN_ID/cancel

# DISPATCH a workflow
gh workflow run workflow.yml --repo Aries-Serpent/_codex_ --ref BRANCH
```

---

## API Scope Coverage Summary

| Scope | Variables | Secrets | Dependabot | Codespaces |
|---|---|---|---|---|
| Repository | ✅ REST + CLI | ✅ REST + CLI | ✅ REST + CLI | ✅ REST + CLI |
| Organization | ✅ REST + CLI | ✅ REST + CLI | ✅ REST + CLI | ✅ REST + CLI |
| Environment | ✅ REST + CLI | ✅ REST + CLI | ✗ | ✗ |
| User | ✗ | ✗ | ✗ | ✅ REST + CLI |

---

## MCP Server: Critical Gap

**The GitHub MCP Server does NOT support Secrets/Variables CRUD.**  
Use REST API or `gh` CLI for all secret/variable write operations.

The Copilot runtime currently exposes **35 read-only GitHub MCP tools** for Actions,
code, commits, discussions, issues, labels, pull requests, releases, search,
security, tags, and users, plus standalone `web_search`. The supplied startup
inventory groups these as 36 research capabilities. Availability does not imply
write access.

---

## Full Reference Documents

| Document | Path | Content |
|---|---|---|
| **Variables & Secrets Reference** | `docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md` | Complete REST API tables, CLI patterns, MCP config |
| **Copilot Agent API Reference** | `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | Token hierarchy, repo variables, PR body protocol |
| **MCP Tool Reference** | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | Live inventory (21 Playwright MCP + 35 GitHub MCP + `web_search`) |
| **Research Inventory** | `.codex/docs/MCP_GITHUB_CAPABILITIES.md` | Exact supplied 36-name inventory and runtime topology |
| **MCP Capabilities Reference** | `docs/mcp/MCP_CAPABILITIES_REFERENCE.md` | Internal MCP server implementation |
| **GitHub MCP Capabilities** | `docs/reference/GITHUB_MCP_CAPABILITIES_DOCUMENTATION.md` | External GitHub MCP server capabilities |
| **MCP Developer Guide** | `docs/mcp/MCP_DEVELOPER_GUIDE.md` | Integration patterns |
| **Dependabot Management** | `.codex/docs/DEPENDABOT_MANAGEMENT_STRATEGY.md` | Dependabot PR workflow |

---

## Upstream Sources (inventory reverified 2026-08-01)

- [REST API: Actions Secrets](https://docs.github.com/en/rest/actions/secrets)
- [REST API: Actions Variables](https://docs.github.com/en/rest/actions/variables)
- [REST API: Dependabot Secrets](https://docs.github.com/en/rest/dependabot/secrets)
- [REST API: Codespaces Secrets](https://docs.github.com/en/rest/codespaces/secrets)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub MCP Server README](https://github.com/github/github-mcp-server/blob/main/README.md)
- [MCP Server Configuration](https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md)
