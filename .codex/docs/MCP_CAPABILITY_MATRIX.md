# MCP Capability Matrix: Historical General Catalog

> **Generated**: 2026-02-17T11:19:53Z
> **Repository**: Aries-Serpent/_codex_
> **Purpose**: Historical upstream/general catalog of MCP ideas and use cases
> **Status**: Historical; not the current Copilot runtime inventory
>
> **Current runtime source:** `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` documents
> 35 read-only GitHub MCP tools, 21 Playwright MCP tools, and standalone
> `web_search` as observed on 2026-08-01. This file mixes configurable upstream,
> built-in, and historical write-capable surfaces and must not be used to infer
> current-session availability or permissions.

---

## Executive Summary

This retained catalog describes a broad historical design space for Model Context
Protocol tools and adjacent agent capabilities. Its counts are not a current runtime
contract. It includes:

- **100+ MCP tools** across 10 categories
- **Runtime requirements** for each tool type
- **Network access needs** and security considerations
- **Secrets management** requirements
- **Recommended use cases** with examples

---

## Table of Contents

1. [MCP Tool Categories](#mcp-tool-categories)
2. [Capability Matrix](#capability-matrix)
3. [Runtime Requirements](#runtime-requirements)
4. [Network & Security](#network--security)
5. [Configuration Recipes](#configuration-recipes)
6. [Use Case Examples](#use-case-examples)

---

## MCP Tool Categories

### 1. Repository Tools (15+ tools)
**Purpose**: Access and manage repository structure, code, and files

**Key Tools**:
- `get_file_contents` - Read file/directory contents
- `search_code` - Search code across all repos
- `search_repositories` - Find repos by criteria
- `list_commits` - View commit history
- `get_commit` - Get commit details with diffs
- `list_branches` - List repository branches
- `list_tags` - List git tags

**Runtime**: Node.js 18+, GitHub MCP Server
**Network**: GitHub API access required
**Secrets**: `GITHUB_TOKEN` (read scope minimum)

---

### 2. Pull Request Tools (20+ tools)
**Purpose**: Manage PR lifecycle, reviews, and comments

**Key Tools**:
- `list_pull_requests` - List PRs with filters
- `search_pull_requests` - Search PRs by criteria
- `pull_request_read` (7 methods):
  - `get` - Get PR details
  - `get_diff` - Get PR diff
  - `get_status` - Get build status
  - `get_files` - List changed files
  - `get_review_comments` - Get review threads
  - `get_reviews` - Get PR reviews
  - `get_comments` - Get PR comments
- `github-coding-agent-create-pull-request` - Create PRs
- `githubwrite` - Merge PRs, update branches
- **Post PR comments** (via `githubwrite` natural language)

**Runtime**: Node.js 18+, GitHub MCP Server
**Network**: GitHub API access required
**Secrets**: `GITHUB_TOKEN` (write scope for mutations)

---

### 3. Issue Tools (12+ tools)
**Purpose**: Issue tracking, labeling, and management

**Key Tools**:
- `list_issues` - List issues with filters
- `search_issues` - Search issues by query
- `issue_read` (4 methods):
  - `get` - Get issue details
  - `get_comments` - Get issue comments
  - `get_sub_issues` - Get sub-issues
  - `get_labels` - Get labels
- `github-issue` - Create/update issues
- **Post issue comments** (via MCP tools)

**Runtime**: Node.js 18+, GitHub MCP Server
**Network**: GitHub API access required
**Secrets**: `GITHUB_TOKEN` (write scope for mutations)

---

### 4. CI/CD & Actions Tools (18+ tools)
**Purpose**: Monitor workflows, access logs, manage builds

**Key Tools**:
- `actions_list` (4 methods):
  - `list_workflows` - List all workflows
  - `list_workflow_runs` - List workflow runs
  - `list_workflow_jobs` - List jobs in a run
  - `list_workflow_run_artifacts` - List artifacts
- `actions_get` (6 methods):
  - `get_workflow` - Get workflow details
  - `get_workflow_run` - Get run details
  - `get_workflow_job` - Get job details
  - `download_workflow_run_artifact` - Download artifacts
  - `get_workflow_run_usage` - Get usage metrics
  - `get_workflow_run_logs_url` - Get log URLs
- `get_job_logs` - Retrieve job logs with filtering

**Runtime**: Node.js 18+, GitHub MCP Server
**Network**: GitHub API + Actions Log API access
**Secrets**: `GITHUB_TOKEN` (actions:read minimum)

---

### 5. Security & Scanning Tools (8+ tools)
**Purpose**: Security alerts, vulnerability management

**Key Tools**:
- `list_code_scanning_alerts` - List code scanning alerts
- `get_code_scanning_alert` - Get alert details
- `list_secret_scanning_alerts` - List secret alerts
- `get_secret_scanning_alert` - Get secret alert details

**Runtime**: Node.js 18+, GitHub MCP Server
**Network**: GitHub Security API access
**Secrets**: `GITHUB_TOKEN` (security_events:read)

---

### 6. Browser Automation Tools (Playwright)
**Purpose**: E2E testing, UI automation, visual validation

**Key Tools**:
- `playwright-browser_navigate` - Navigate to URL
- `playwright-browser_click` - Click elements
- `playwright-browser_type` - Type text
- `playwright-browser_snapshot` - Capture accessibility snapshot
- `playwright-browser_take_screenshot` - Screenshots
- `playwright-browser_fill_form` - Fill forms
- `playwright-browser_evaluate` - Execute JavaScript

**Runtime**: Playwright 1.57+, Chromium/Firefox/WebKit browsers
**Network**: Target URLs (can be localhost)
**Secrets**: None (unless target requires auth)

---

### 7. File System Tools (Local Development)
**Purpose**: Read/write files, search file system

**Key Tools**:
- `view` - Read files/directories
- `create` - Create new files
- `edit` - Edit existing files
- `grep` - Search file contents (ripgrep)
- `glob` - Find files by pattern

**Runtime**: Local file system access
**Network**: None
**Secrets**: None

---

### 8. Shell Execution Tools
**Purpose**: Run commands, tests, builds

**Key Tools**:
- `bash` - Execute shell commands (sync/async/detached)
- `write_bash` - Send input to async commands
- `read_bash` - Read output from async commands
- `stop_bash` - Stop async commands
- `list_bash` - List active bash sessions

**Runtime**: Bash shell, command-line tools
**Network**: Depends on commands executed
**Secrets**: Environment variables as needed

---

### 9. Specialized Agent Tools
**Purpose**: Custom agents for specific tasks

**Available Agents**: 54 total (see .codex/archive/deprecated/AGENTS.md for full list)

**Categories**:
- CI/CD & Build (18 agents)
- Testing (12 agents)
- Security (6 agents)
- Documentation (6 agents)
- RAG/ML (4 agents)
- Session Management (2 agents)

**Runtime**: Varies by agent
**Network**: Varies by agent
**Secrets**: Per agent requirements

---

### 10. Web & Search Tools
**Purpose**: Web fetching, search, external APIs

**Key Tools**:
- `web_fetch` - Fetch web pages as markdown/HTML
- `web_search` - AI-powered web search with citations

**Runtime**: HTTP client
**Network**: Internet access required
**Secrets**: API keys for some services

---

## Capability Matrix

| MCP Tool/Category | Can Run | Required Runtime | Network Needs | Secrets Required | Recommended Use Cases |
|------------------|---------|------------------|---------------|------------------|----------------------|
| **Repository Tools** | ✅ Yes | Node.js 18+, GitHub MCP | GitHub API | `GITHUB_TOKEN` (read) | Code exploration, file reading, commit analysis |
| **Pull Request Tools** | ✅ Yes | Node.js 18+, GitHub MCP | GitHub API | `GITHUB_TOKEN` (write for mutations) | PR review, commenting, merging, status checks |
| **Issue Tools** | ✅ Yes | Node.js 18+, GitHub MCP | GitHub API | `GITHUB_TOKEN` (write for mutations) | Issue triage, labeling, project management |
| **CI/CD & Actions** | ✅ Yes | Node.js 18+, GitHub MCP | GitHub API + Actions | `GITHUB_TOKEN` (actions:read) | Workflow monitoring, log analysis, debugging CI |
| **Security Scanning** | ✅ Yes | Node.js 18+, GitHub MCP | GitHub Security API | `GITHUB_TOKEN` (security_events) | Vulnerability detection, alert triage |
| **Playwright Browser** | ✅ Yes | Playwright 1.57+, Browsers | Target URLs (localhost OK) | None (unless target needs auth) | E2E testing, UI validation, screenshots |
| **File System** | ✅ Yes | Local file access | None | None | Code editing, file management, search |
| **Shell Execution** | ✅ Yes | Bash, CLI tools | Varies by command | Env vars as needed | Tests, builds, automation scripts |
| **Specialized Agents** | ✅ Yes | Agent-specific | Agent-specific | Agent-specific | Task-specific automation (see .codex/archive/deprecated/AGENTS.md) |
| **Web & Search** | ✅ Yes | HTTP client | Internet | API keys (optional) | Documentation lookup, research, external data |
| **`agentAssignment` (GraphQL)** | ⚠️ Limited | GitHub Copilot Workspace | GitHub GraphQL API | `GITHUB_TOKEN` + Copilot access | Create Copilot Agent tasks (Workspace UI only) |
| **`create_pull_request_with_copilot` (REST)** | ⚠️ Limited | GitHub Copilot API | GitHub REST API | `GITHUB_TOKEN` + Copilot access | Automated PR creation with agent instructions |

---

## Runtime Requirements

### Minimum Requirements

**Node.js Environment**:
- Node.js 18+ (LTS recommended)
- npm 9+ or yarn 1.22+
- TypeScript 5.7+ (for typed MCP clients)

**Python Environment** (for _codex_ specific):
- Python 3.11+ (repository standard)
- pip 24+
- Virtual environment recommended

**Browsers** (for Playwright):
- Chromium (default)
- Firefox (optional)
- WebKit (optional)
- System: 2GB RAM minimum, 4GB recommended

**GitHub Access**:
- GitHub account with repo access
- Personal Access Token (PAT) or GitHub App
- Appropriate permissions (read/write/admin)

---

### Installation Commands

#### GitHub MCP Server
```bash
# Install globally
npm install -g @modelcontextprotocol/server-github

# Or use npx (recommended)
npx -y @modelcontextprotocol/server-github
```

#### Playwright MCP Server
```bash
# Install Playwright
npm install -D @playwright/test@1.57.0

# Install browsers
npx playwright install
npx playwright install-deps

# Or install specific browser only
npx playwright install chromium
```

#### Bash MCP Server
```bash
npm install -g @modelcontextprotocol/server-bash
```

#### Python Dependencies (for _codex_)
```bash
# Core requirements
pip install -r requirements.txt

# Development requirements
pip install -r requirements-dev.txt

# Test requirements
pip install -r requirements-test.txt
```

---

## Network & Security

### Network Access Patterns

**GitHub MCP Server**:
- **Endpoints**: `https://api.github.com/*`
- **Protocols**: HTTPS/443
- **Rate Limits**: 5,000 requests/hour (authenticated)
- **Caching**: Conditional requests with ETags

**Playwright**:
- **Endpoints**: Target application URLs
- **Protocols**: HTTP/HTTPS, WebSocket
- **Localhost**: Common for dev servers (`:5173`, `:8000`, etc.)
- **External**: Only if testing production sites

**Web Tools**:
- **Endpoints**: Varies by use case
- **Protocols**: HTTP/HTTPS
- **Rate Limits**: Per service
- **Caching**: HTTP cache headers

---

### Secrets Management

**Required Secrets**:

1. **`GITHUB_TOKEN`** (mandatory for GitHub MCP)
   - **Type**: Personal Access Token (classic) or Fine-grained
   - **Scopes Required**:
     - `repo` (full control) for private repos
     - `public_repo` for public repos only
     - `workflow` to manage Actions
     - `read:org` for org access
   - **Security**: Never commit, rotate every 90 days
   - **Storage**: GitHub Secrets, `.env.local`, secure vault

2. **`CODEX_GHP_TOKEN_BASE64`** (_codex_ specific)
   - **Type**: Base64-encoded encrypted GitHub token
   - **Purpose**: Secure token storage for CI/CD
   - **Security**: Encrypted with `CODEX_MASTER_KEY`

3. **`CODEX_MASTER_KEY`** (_codex_ specific)
   - **Type**: Encryption key for token decryption
   - **Purpose**: Decrypt `CODEX_GHP_TOKEN_BASE64`
   - **Security**: Never commit, GitHub Secrets only

4. **API Keys** (optional, per service)
   - Brave Search API (for web search)
   - Custom MCP servers

---

### Security Best Practices

**Token Security**:
- ✅ Use fine-grained tokens when possible
- ✅ Set expiration (90 days recommended)
- ✅ Minimum required scopes only
- ✅ Rotate tokens regularly
- ❌ Never commit tokens to repos
- ❌ Never share tokens between users

**File System Access**:
- ✅ Limit allowed directories
- ✅ Validate file paths
- ✅ Sandbox untrusted code
- ❌ Never allow root directory access

**Command Execution**:
- ✅ Whitelist allowed commands
- ✅ Validate command arguments
- ✅ Log all executions
- ❌ Never allow arbitrary code execution
- ❌ Never run destructive commands without confirmation

**Network Access**:
- ✅ Use HTTPS for external requests
- ✅ Verify SSL certificates
- ✅ Implement rate limiting
- ❌ Never expose credentials in URLs
- ❌ Never trust user-provided URLs without validation

---

## Configuration Recipes

See separate files:
- [Playwright Configuration Recipe](./MCP_PLAYWRIGHT_RECIPE.md)
- [GitHub Actions MCP Workflows](./MCP_WORKFLOW_RECIPES.md)
- [agentAssignment Payload Examples](./MCP_AGENT_ASSIGNMENT_EXAMPLES.md)
- [Package.json MCP Integration](./MCP_PACKAGE_JSON_RECIPE.md)

---

## Use Case Examples

### Use Case 1: E2E Test Automation in CI/CD

**Scenario**: Run Playwright e2e tests in GitHub Actions with MCP context

**Required Tools**:
- Playwright browser tools
- GitHub Actions tools (for log access)
- File system tools (for test files)

**Workflow**:
1. Install Playwright via `bash` tool
2. Configure playwright.config.ts via `create`/`edit`
3. Execute tests via `bash` (async mode)
4. Monitor test execution via `read_bash`
5. Upload artifacts via GitHub Actions integration
6. Access test logs via `get_job_logs`

**Example Command**:
```bash
# Via bash tool
npm run test:e2e:chromium -- --reporter=json --output-file=results.json
```

**Network**: localhost:5173 (dev server)
**Secrets**: None (unless app requires auth)
**Runtime**: 5-15 minutes depending on test count

---

### Use Case 2: Automated PR Review with Copilot Agent

**Scenario**: Review PR #3248, check CI status, post review comments

**Required Tools**:
- `pull_request_read` (multiple methods)
- `actions_list` and `get_job_logs`
- `githubwrite` (for posting comments)
- `grep` and `view` (for code analysis)

**Workflow**:
1. Fetch PR details: `pull_request_read(method='get', owner='Aries-Serpent', repo='_codex_', pullNumber=3248)`
2. Get changed files: `pull_request_read(method='get_files', ...)`
3. Analyze code locally: `view` and `grep` tools
4. Check CI status: `pull_request_read(method='get_status', ...)`
5. Get failed job logs: `get_job_logs(job_id=..., failed_only=true)`
6. Post review comments: `githubwrite(query="Post comment on PR #3248...")`

**Network**: GitHub API
**Secrets**: `GITHUB_TOKEN` (write)
**Runtime**: 30 seconds - 2 minutes

---

### Use Case 3: Debug CI Failure with Log Analysis

**Scenario**: Investigate failed workflow run, identify root cause

**Required Tools**:
- `actions_list` (list workflow runs)
- `get_job_logs` (retrieve logs)
- `grep` (search error patterns)
- `view` (examine relevant files)

**Workflow**:
1. List recent runs: `actions_list(method='list_workflow_runs', owner='...', repo='...', workflow_id='...')`
2. Get failed job logs: `get_job_logs(owner='...', repo='...', run_id=..., failed_only=true)`
3. Search for error patterns: Parse logs and use `grep` to find code references
4. Examine failing code: `view` files mentioned in errors
5. Propose fix based on analysis

**Network**: GitHub API + Actions API
**Secrets**: `GITHUB_TOKEN` (actions:read)
**Runtime**: 1-5 minutes

---

### Use Case 4: Create Copilot Agent Task (agentAssignment)

**Scenario**: Create a new Copilot Agent task in GitHub Copilot Workspace

**Required Tools**:
- `agentAssignment` (GraphQL mutation)
- OR `create_pull_request_with_copilot` (REST endpoint)

**Workflow (GraphQL)**:
```graphql
mutation {
  agentAssignment(input: {
    repositoryId: "R_kgDOPjJ9Hg",
    title: "Fix test failures in PR #3248",
    description: """
    Address all 25 test failures in PR #3248 following the Investigation Protocol:

    1. Analyze failure logs
    2. Identify root causes
    3. Apply systematic fixes
    4. Validate with pytest
    5. Update documentation
    """,
    instructions: "Use systematic fix patterns from .codex/PR_3248_RESOLUTION_PATTERNS.md",
    files: [
      "tests/cognitive_brain/quantum/test_memory_errors.py",
      "tests/cli/test_train_probe_json_schema.py"
    ]
  }) {
    agentRun {
      id
      status
      repositoryName
    }
  }
}
```

**Network**: GitHub GraphQL API
**Secrets**: `GITHUB_TOKEN` (Copilot access required)
**Runtime**: Immediate creation, execution varies
**Limitations**: Only available in GitHub Copilot Workspace UI

---

### Use Case 5: Security Alert Triage

**Scenario**: List all open security alerts, prioritize by severity

**Required Tools**:
- `list_code_scanning_alerts`
- `list_secret_scanning_alerts`
- `get_code_scanning_alert` (for details)

**Workflow**:
1. List code scanning alerts: `list_code_scanning_alerts(owner='...', repo='...', state='open')`
2. Filter by severity: Parse response, focus on `critical` and `high`
3. Get alert details: `get_code_scanning_alert(owner='...', repo='...', alertNumber=...)`
4. Search codebase for affected code: `grep` and `view`
5. Propose remediation based on alert recommendations

**Network**: GitHub Security API
**Secrets**: `GITHUB_TOKEN` (security_events:read)
**Runtime**: 30 seconds - 2 minutes

---

## Advanced Topics

### Custom MCP Servers

**Creating a Custom MCP Server for _codex_**:

1. **Define server capabilities** (`mcp-server.js`):
```javascript
import { MCPServer } from '@modelcontextprotocol/sdk';

const server = new MCPServer({
  name: 'codex-mcp-server',
  version: '1.0.0',
  capabilities: {
    tools: [
      {
        name: 'run_codex_tests',
        description: 'Run pytest tests with coverage',
        inputSchema: {
          type: 'object',
          properties: {
            test_path: { type: 'string' },
            coverage_threshold: { type: 'number' }
          }
        }
      }
    ]
  }
});

server.setRequestHandler('tools/run_codex_tests', async (params) => {
  // Implementation
});

await server.connect();
```

2. **Configure in MCP client** (Claude Desktop, VS Code):
```json
{
  "mcpServers": {
    "codex-dev": {
      "command": "node",
      "args": ["/path/to/_codex_/scripts/mcp-server.js"],
      "env": {
        "CODEX_ROOT": "/path/to/_codex_",
        "PYTHON_VERSION": "3.11"
      }
    }
  }
}
```

---

### MCP in GitHub Actions

**Example Workflow** (see `.github/workflows/examples/copilot-with-mcp.yml`):
```yaml
jobs:
  copilot-with-mcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up MCP context
        run: |
          # MCP server runs as service container
          # Agent can access via http://localhost:8080

      - name: Execute Copilot task
        env:
          MCP_ENDPOINT: http://localhost:8080
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Agent execution with MCP context
```

---

## Troubleshooting

### Common Issues

**Issue 1: "GitHub authentication failed"**

**Symptoms**: 401/403 errors when using GitHub MCP tools

**Solutions**:
1. Verify `GITHUB_TOKEN` is set correctly
2. Check token has required scopes
3. Ensure token hasn't expired
4. Test token manually:
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

---

**Issue 2: "Playwright browsers not installed"**

**Symptoms**: `browserType.launch: Executable doesn't exist`

**Solutions**:
1. Install browsers: `npx playwright install`
2. Install system dependencies: `npx playwright install-deps`
3. Verify installation: `npx playwright --version`

---

**Issue 3: "MCP server not responding"**

**Symptoms**: Timeout errors, connection refused

**Solutions**:
1. Check server is running: `curl http://localhost:8080/health`
2. Verify correct port configuration
3. Check server logs for errors
4. Restart MCP server

---

**Issue 4: "Rate limit exceeded"**

**Symptoms**: 429 Too Many Requests

**Solutions**:
1. Use authenticated requests (higher limits)
2. Implement exponential backoff
3. Cache responses when possible
4. Spread requests over time

---

## References

**Official Documentation**:
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [Playwright Documentation](https://playwright.dev/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)

**_codex_ Specific**:
- [MCP Setup Guide](../../docs/MCP_SETUP_GUIDE.md)
- [GitHub MCP Capabilities](../../docs/reference/GITHUB_MCP_CAPABILITIES_DOCUMENTATION.md)
- [.codex/archive/deprecated/AGENTS.md](../../.codex/archive/deprecated/AGENTS.md)
- [CODEBASE_AGENCY_POLICY.md](../CODEBASE_AGENCY_POLICY.md)

---

## Document Metadata

**Version**: 1.0.0
**Last Updated**: 2026-02-17T11:19:53Z
**Maintained By**: GitHub Copilot Agent
**Review Cycle**: Quarterly or when capabilities change
**Status**: ✅ Production-Ready

---

**Next Steps**:
1. Review configuration recipes in companion documents
2. Set up MCP servers following security best practices
3. Test MCP capabilities with simple use cases
4. Integrate MCP into CI/CD workflows
5. Create custom agents for repository-specific tasks

**Questions?** See troubleshooting section or create an issue.
