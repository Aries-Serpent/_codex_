# MCP (Model Context Protocol) Setup Guide

**Purpose:** Enable AI assistants to interact with GitHub repositories, run tests, and perform development tasks through standardized Model Context Protocol servers.

**Date:** Previous Cycle-12-18  
**Repository:** Aries-Serpent/_codex_

---

## What is MCP?

Model Context Protocol (MCP) is a standardized way for AI assistants to interact with external tools and services. It allows AI models to:
- Access GitHub repositories and APIs
- Run shell commands and tests
- Browse websites and documentation
- Search code and files
- Manage workflows and CI/CD

---

## Quick Setup (5 Minutes)

### For Claude Desktop (Recommended)

1. **Locate Configuration File:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. **Install Required Tools:**
   ```bash
   # Install Node.js (if not already installed)
   # macOS
   brew install node
   
   # Linux (Ubuntu/Debian)
   sudo apt install nodejs npm
   
   # Windows
   # Download from https://nodejs.org
   ```

3. **Install MCP Servers:**
   ```bash
   # GitHub MCP Server (for repository access)
   npm install -g @modelcontextprotocol/server-github
   
   # Playwright MCP Server (for browser automation)
   npm install -g @playwright/test
   npx playwright install
   ```

4. **Configure Claude Desktop:**
   
   Edit `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_TOKEN": "your_github_personal_access_token_here"
         }
       },
       "playwright": {
         "command": "npx",
         "args": ["-y", "@playwright/mcp-server"]
       },
       "bash": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-bash"]
       }
     }
   }
   ```

5. **Create GitHub Personal Access Token:**
   
   a. Go to https://github.com/settings/tokens
   
   b. Click "Generate new token (classic)"
   
   c. Name: "MCP Server Access"
   
   d. Select scopes:
      - ✅ `repo` (Full control of private repositories)
      - ✅ `workflow` (Update GitHub Action workflows)
      - ✅ `read:org` (Read org and team membership)
      - ✅ `project` (Access projects)
   
   e. Click "Generate token"
   
   f. Copy token and paste into config (replace `your_github_personal_access_token_here`)

6. **Restart Claude Desktop**

7. **Verify Setup:**
   
   In Claude Desktop, ask:
   ```
   Can you list the workflows in the Aries-Serpent/_codex_ repository?
   ```
   
   If configured correctly, Claude will use the GitHub MCP server to fetch workflow information.

---

## Detailed Configuration

### Full MCP Server Configuration

For comprehensive development capabilities, use this full configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"]
    },
    "bash": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-bash"],
      "env": {
        "ALLOWED_COMMANDS": "git,npm,python,pytest,pip,node,nox,ruff,black,mypy"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "/path/to/_codex_,/tmp"
      }
    },
    "search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "optional_brave_search_api_key"
      }
    }
  }
}
```

### Environment Variables Explained

**GitHub MCP Server:**
- `GITHUB_TOKEN`: Required. Personal access token for GitHub API access.

**Bash MCP Server:**
- `ALLOWED_COMMANDS`: Comma-separated list of allowed commands (security feature).
- `WORKING_DIRECTORY`: Optional. Default working directory for commands.

**Filesystem MCP Server:**
- `ALLOWED_DIRECTORIES`: Comma-separated list of directories the AI can access.

**Search MCP Server:**
- `BRAVE_API_KEY`: Optional. For web search capabilities.

---

## Security Best Practices

### 1. Token Security
- ✅ Use fine-grained tokens when possible
- ✅ Set token expiration (90 days recommended)
- ✅ Never commit tokens to repositories
- ✅ Rotate tokens regularly
- ❌ Don't share tokens

### 2. Filesystem Access
- ✅ Limit `ALLOWED_DIRECTORIES` to project directories and `/tmp`
- ✅ Never allow root directory `/`
- ✅ Review file access patterns regularly

### 3. Command Execution
- ✅ Use `ALLOWED_COMMANDS` to restrict bash operations
- ✅ Avoid allowing destructive commands (`rm -rf`, `sudo`, etc.)
- ✅ Review command execution logs

### 4. Repository Access
- ✅ Use read-only tokens for read-only operations
- ✅ Limit token scope to necessary repositories
- ✅ Monitor token usage in GitHub settings

---

## Troubleshooting

### Issue: "MCP server not found"
**Solution:**
```bash
# Ensure Node.js is installed
node --version
npm --version

# Install MCP servers globally
npm install -g @modelcontextprotocol/server-github
npm install -g @playwright/mcp-server
```

### Issue: "GitHub authentication failed"
**Solution:**
1. Verify token has correct scopes
2. Check token hasn't expired
3. Ensure token is correctly pasted in config (no extra spaces)
4. Test token manually:
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

### Issue: "Permission denied" for bash commands
**Solution:**
1. Check `ALLOWED_COMMANDS` includes the command
2. Verify working directory permissions
3. Restart Claude Desktop after config changes

### Issue: Configuration not loading
**Solution:**
1. Verify JSON syntax is valid (use JSONLint.com)
2. Check file path is correct for your OS
3. Ensure file encoding is UTF-8
4. Restart Claude Desktop completely (quit from menu bar)

---

## Testing Your Setup

### Test 1: GitHub Access
```
Ask Claude: "Can you list the open pull requests in Aries-Serpent/_codex_?"
```
Expected: List of PRs with titles, authors, and status.

### Test 2: File System Access
```
Ask Claude: "Can you show me the contents of pyproject.toml in the _codex_ repo?"
```
Expected: File contents displayed.

### Test 3: Code Search
```
Ask Claude: "Search for 'fastapi' in the _codex_ repository"
```
Expected: List of files containing 'fastapi'.

### Test 4: Workflow Access
```
Ask Claude: "What GitHub Actions workflows are defined in _codex_?"
```
Expected: List of workflow files with descriptions.

---

## Usage Examples

### Example 1: Review PR
```
"Review PR #2513 in Aries-Serpent/_codex_ and check if all CI jobs pass"
```

### Example 2: Debug Test Failure
```
"Check the failed test logs for job 58379623933 in _codex_ and tell me why it failed"
```

### Example 3: Search Codebase
```
"Find all files that import config_legacy in the _codex_ repository"
```

### Example 4: Analyze Workflow
```
"Show me the test-suite.yml workflow and explain what it does"
```

---

## Advanced Configuration

### Custom MCP Server for This Repository

Create a custom MCP server configuration for _codex_ development:

```json
{
  "mcpServers": {
    "codex-dev": {
      "command": "node",
      "args": ["/path/to/_codex_/scripts/mcp-server.js"],
      "env": {
        "CODEX_ROOT": "/path/to/_codex_",
        "PYTHON_VERSION": "3.11",
        "VIRTUAL_ENV": "/path/to/_codex_/.venv"
      }
    }
  }
}
```

This would require creating a custom MCP server script that:
- Understands _codex_ repository structure
- Can run tests with the correct environment
- Has access to project-specific tools (nox, pytest, etc.)

---

## Integration with IDE

### VS Code Integration (Future)
MCP support in VS Code is coming soon. Once available:

1. Install MCP extension from marketplace
2. Configure similar to Claude Desktop
3. Use in-editor AI assistance with repository context

### JetBrains Integration (Future)
Watch for MCP support in JetBrains IDEs.

---

## Maintenance

### Monthly Tasks
- [ ] Rotate GitHub personal access tokens
- [ ] Review MCP server logs for unusual activity
- [ ] Update MCP server packages:
  ```bash
  npm update -g @modelcontextprotocol/server-github
  npm update -g @playwright/mcp-server
  ```

### When Issues Arise
1. Check Claude Desktop logs:
   - **macOS:** `~/Library/Logs/Claude/`
   - **Windows:** `%APPDATA%\Claude\logs\`
   - **Linux:** `~/.config/Claude/logs/`

2. Verify MCP server versions:
   ```bash
   npm list -g | grep modelcontextprotocol
   ```

3. Test token validity:
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

---

## Resources

- **MCP Documentation:** https://modelcontextprotocol.io/
- **GitHub MCP Server:** https://github.com/modelcontextprotocol/servers
- **Claude Desktop Download:** https://claude.ai/download
- **GitHub Token Docs:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ MCP Quick Reference                             │
├─────────────────────────────────────────────────┤
│ Config File Location (macOS):                   │
│ ~/Library/Application Support/Claude/           │
│   claude_desktop_config.json                    │
│                                                  │
│ Required Token Scopes:                          │
│ ✓ repo                                          │
│ ✓ workflow                                      │
│ ✓ read:org                                      │
│                                                  │
│ Test Setup:                                     │
│ "List workflows in Aries-Serpent/_codex_"      │
│                                                  │
│ Restart Required:                               │
│ After any config changes                        │
└─────────────────────────────────────────────────┘
```

---

**Next Steps:**
1. Complete setup following Quick Setup section
2. Test with provided examples
3. Use MCP-enabled Claude for repository development
4. Maintain tokens and review security regularly

**Note:** This guide is specific to the Aries-Serpent/_codex_ repository but can be adapted for other projects.
