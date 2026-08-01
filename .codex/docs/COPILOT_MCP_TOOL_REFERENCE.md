# Copilot Agent MCP Tool Reference

> **Source of truth:** live MCP server log at `/home/runner/work/_temp/cca-mcp-debug-logs/mcp-server.log`
> and agent definitions at `/home/runner/work/_temp/copilot-developer-action-main/dist/definitions/`
>
> **Action runtime:** `@github/copilot-developer-action v0.0.1`  
> **MCP SDK:** `@modelcontextprotocol/sdk ^1.27.1`  
> **Playwright MCP:** `@playwright/mcp@0.0.40`  
> **GitHub MCP server:** remote `https://api.individual.githubcopilot.com/mcp/readonly`  
> **Last verified:** 2026-08-01 (S1485 / PR #5415)
> **Related strategy docs:** [`MCP_INTEGRATION_MASTER_PLAN.md`](./MCP_INTEGRATION_MASTER_PLAN.md), [`MCP_CAPABILITY_MATRIX.md`](./MCP_CAPABILITY_MATRIX.md), [`CUSTOM_AGENT_MCP_INTEGRATION_AUDIT.md`](./CUSTOM_AGENT_MCP_INTEGRATION_AUDIT.md)

---

## How the MCP layer works in this repo

Every Copilot coding agent session spins up a **local MCP aggregator** (Node.js process,
`index.js`) that connects to two external MCP servers and exposes a merged tool list on
`http://127.0.0.1:2301`:

```
Copilot agent process
  └─ MCP aggregator :2301
       ├─ playwright    (local subprocess: npx @playwright/mcp@0.0.40)  → 21 tools
       └─ github-mcp-server  (remote HTTPS: api.individual.githubcopilot.com/mcp/readonly)  → 36 tools
```

On top of that, a set of **built-in tools** are compiled into `index.js` itself and
always available regardless of external connectivity.

---

## Complete Tool Inventory

### Server 1 — `playwright` (21 tools)

All tools prefixed `playwright-browser_` in the agent's tool-call syntax.

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to a URL |
| `browser_navigate_back` | Browser back button |
| `browser_snapshot` | Accessibility snapshot (preferred over screenshot for actions) |
| `browser_take_screenshot` | PNG/JPEG screenshot of viewport or element |
| `browser_click` | Click an element (single or double, with modifiers) |
| `browser_type` | Type text into an editable element |
| `browser_fill_form` | Fill multiple form fields at once |
| `browser_select_option` | Select from a `<select>` dropdown |
| `browser_hover` | Hover over an element |
| `browser_drag` | Drag-and-drop between two elements |
| `browser_press_key` | Press a keyboard key (e.g. `Enter`, `ArrowDown`) |
| `browser_evaluate` | Run JavaScript on page or element |
| `browser_wait_for` | Wait for text to appear/disappear or a timeout |
| `browser_handle_dialog` | Accept or dismiss alerts/confirms/prompts |
| `browser_file_upload` | Upload a file via `<input type="file">` |
| `browser_console_messages` | Return all browser console messages |
| `browser_network_requests` | Return all network requests since page load |
| `browser_resize` | Resize the browser window |
| `browser_tabs` | List, create, close, or select a browser tab |
| `browser_close` | Close the browser page |
| `browser_install` | Install the browser (fallback if not present) |

**Startup config used in this repo:**
```
npx @playwright/mcp@0.0.40
  --viewport-size 1280,720
  --output-dir /tmp/playwright-logs
  --allowed-origins localhost;localhost:*;127.0.0.1;127.0.0.1:*
```

> **Tip:** Use `browser_snapshot` instead of `browser_take_screenshot` when you need to
> interact with elements — snapshot returns the accessibility tree which gives you `ref`
> values for `browser_click`, `browser_type`, etc.

---

### Server 2 — `github-mcp-server` (36 tools)

Runtime registration uses `github-mcp-server/<tool>`; the agent API exposes the
equivalent callable name with the `github-mcp-server-` prefix.
Mode: **read-only** (`/mcp/readonly` endpoint).

#### Actions / CI

| Tool | Key params | Purpose |
|------|-----------|---------|
| `actions_list` | `method`, `owner`, `repo`, `resource_id`, `per_page`, `workflow_runs_filter`, `workflow_jobs_filter` | List workflows, runs, jobs, or artifacts |
| `actions_get` | `method`, `owner`, `repo`, `resource_id` | Get a single workflow, run, job, or artifact |
| `get_job_logs` | `owner`, `repo`, `job_id` OR `run_id` + `failed_only`, `return_content`, `tail_lines` | Download CI log content |

**`actions_list` method values:**
- `list_workflows` — all workflows in repo
- `list_workflow_runs` — runs for a workflow or all runs in repo
- `list_workflow_jobs` — jobs in a specific run
- `list_workflow_run_artifacts` — artifacts for a run

**`actions_get` method values:**
- `get_workflow` — single workflow by ID or filename
- `get_workflow_run` — single run by ID
- `get_workflow_job` — single job by ID
- `get_workflow_run_usage` — CPU/billing minutes for a run
- `get_workflow_run_logs_url` — presigned log URL (prefer `get_job_logs` instead)
- `download_workflow_run_artifact` — artifact download

#### Issues & PRs

| Tool | Key params | Purpose |
|------|-----------|---------|
| `issue_read` | `method`, `owner`, `repo`, `issue_number` | Read issue details, comments, labels, sub-issues |
| `list_issues` | `owner`, `repo`, `state`, `labels`, `orderBy`, `direction`, `since`, `perPage` | List issues with filters |
| `search_issues` | `query`, `owner`, `repo`, `sort`, `order`, `perPage` | Search issues (scoped to `is:issue`) |
| `list_issue_fields` | `owner`, optional `repo` | List custom issue fields and select options |
| `list_issue_types` | `owner`, optional `repo` | List issue types for an org or repository |
| `pull_request_read` | `method`, `owner`, `repo`, `pullNumber` | Read PR details, diff, files, reviews, comments, checks |
| `list_pull_requests` | `owner`, `repo`, `state`, `base`, `head`, `sort`, `direction`, `perPage` | List PRs |
| `search_pull_requests` | `query`, `owner`, `repo`, `sort`, `order`, `perPage` | Search PRs (scoped to `is:pr`) |

**`pull_request_read` method values:**
- `get` — full PR metadata
- `get_diff` — unified diff of changes
- `get_files` — list of changed files
- `get_commits` — commits on the pull request
- `get_status` — combined commit status
- `get_review_comments` — review threads with metadata
- `get_reviews` — PR reviews
- `get_comments` — general PR comments (bot + human)
- `get_check_runs` — CI check runs for head commit ← **use this for §0 pre-session review**

#### Code & Commits

| Tool | Key params | Purpose |
|------|-----------|---------|
| `get_file_contents` | `owner`, `repo`, `path`, `ref`, `sha` | Read file/directory from any ref |
| `get_commit` | `owner`, `repo`, `sha`, `detail`, `page`, `perPage` | Inspect a commit with optional stats or full patch |
| `list_commits` | `owner`, `repo`, `sha`, `author`, `page`, `perPage` | List commits on a branch |
| `list_branches` | `owner`, `repo`, `page`, `perPage` | List branches |
| `search_code` | `query`, `sort`, `order`, `page`, `perPage` | Full-text code search across GitHub |
| `search_commits` | `query`, `sort`, `order`, `page`, `perPage` | Search commit messages on default branches |

#### Releases & Tags

| Tool | Key params | Purpose |
|------|-----------|---------|
| `get_latest_release` | `owner`, `repo` | Get the latest release |
| `get_release_by_tag` | `owner`, `repo`, `tag` | Get a specific release |
| `list_releases` | `owner`, `repo`, `page`, `perPage` | List releases |
| `get_tag` | `owner`, `repo`, `tag` | Get a specific git tag |
| `list_tags` | `owner`, `repo`, `page`, `perPage` | List git tags |

#### Security

| Tool | Key params | Purpose |
|------|-----------|---------|
| `list_code_scanning_alerts` | `owner`, `repo`, `state`, `severity`, `ref`, `tool_name` | List CodeQL/SARIF alerts |
| `get_code_scanning_alert` | `owner`, `repo`, `alertNumber` | Get a single code scanning alert |
| `list_secret_scanning_alerts` | `owner`, `repo`, `state`, `resolution`, `secret_type` | List secret scanning alerts |
| `get_secret_scanning_alert` | `owner`, `repo`, `alertNumber` | Get a single secret scanning alert |

#### Discussions

| Tool | Key params | Purpose |
|------|-----------|---------|
| `get_discussion` | `owner`, `repo`, `discussionNumber` | Get one discussion |
| `get_discussion_comments` | `owner`, `repo`, `discussionNumber`, `includeReplies`, `perPage`, `after` | Get discussion comments and optional replies |
| `list_discussion_categories` | `owner`, optional `repo` | List discussion categories |
| `list_discussions` | `owner`, optional `repo`, `category`, `orderBy`, `direction`, `perPage`, `after` | List discussions |

#### Discovery

| Tool | Key params | Purpose |
|------|-----------|---------|
| `search_repositories` | `query`, `sort`, `order`, `page`, `perPage`, `minimal_output` | Search GitHub repos |
| `search_users` | `query`, `sort`, `order`, `page`, `perPage` | Search GitHub users |
| `get_label` | `owner`, `repo`, `name` | Get a label |
| `list_label` | `owner`, `repo` | List repository labels |
| `list_repository_collaborators` | `owner`, `repo`, `affiliation`, `page`, `perPage` | List collaborators and affiliations |
| `web_search` | `query` | AI-powered web search with citations |

---

### Built-in tools (always available, compiled into agent)

These are not served by an external MCP server — they are part of the agent runtime itself.

#### File system

| Tool | Purpose |
|------|---------|
| `view` | Read a file with line numbers, or list a directory (2 levels) |
| `create` | Create a new file (fails if exists) |
| `edit` | Replace an exact string in a file — **surgical, one occurrence** |
| `glob` | Find files by glob pattern |
| `grep` | Ripgrep-powered content search with context, count, and file modes |

#### Shell

| Tool | Purpose |
|------|---------|
| `bash` | Run a bash command (`mode: sync` or `async`, optional `detach: true`) |
| `write_bash` | Send input to a running async bash session |
| `read_bash` | Read output from a running async bash session |
| `stop_bash` | Terminate a bash session |
| `list_bash` | List all active bash sessions |

#### Session / PR management

| Tool | Purpose |
|------|---------|
| `report_progress` | `git add . && git commit && git push` + update PR description with checklist |
| `reply_to_comment` | Post a reply to a specific PR comment thread (by `comment_id`) |
| `store_memory` | Persist a fact to long-term session memory (cross-session) |

#### Code quality

| Tool | Purpose |
|------|---------|
| `code_review` | Run the built-in code review agent against current changes |
| `codeql_checker` | Run CodeQL security analysis on changed files |
| `gh-advisory-database` | Check a dependency version against the GitHub Advisory DB |
| `search_code_subagent` | Semantic code search using natural language |

#### Sub-agents (spawn a sub-process agent)

The `task` tool launches one of several specialized agents defined in
`dist/definitions/`:

| Agent type | Model | Purpose |
|-----------|-------|---------|
| `explore` | claude-haiku-4.5 | Fast codebase Q&A; grep/glob/view/bash; safe to parallelize |
| `task` | claude-haiku-4.5 | Run commands (tests, builds, lints); returns brief summary on success, full output on failure |
| `general-purpose` | claude-sonnet-4.x | Full toolset in a subprocess; for complex multi-step tasks |
| `research` | claude-sonnet-4.6 | GitHub search + web; exhaustive research answers |
| `code-review` | claude-sonnet-4.5 | High-signal-to-noise code review; never modifies files |

Plus all **custom agents** defined in `.github/agents/` (54 in this repo — see `.codex/archive/deprecated/AGENTS.md`).

#### Web

| Tool | Purpose |
|------|---------|
| `web_fetch` | Fetch a URL and return markdown or raw HTML |

---

## Pre-session §0 checklist (mandatory per CODEBASE_AGENCY_POLICY.md)

Run these **three calls in parallel** at the start of every session:

```python
# 1. All PR comments (bot directives live here)
github-mcp-server-pull_request_read(method="get_comments",   owner="Aries-Serpent", repo="_codex_", pullNumber=ACTIVE_PR)
# 2. All CI check runs (failing checks to fix)
github-mcp-server-pull_request_read(method="get_check_runs", owner="Aries-Serpent", repo="_codex_", pullNumber=ACTIVE_PR)
# 3. Recent commits (understand current branch state)
bash(command="git log --oneline -5")
```

---

## Proven patterns for this repo

### CI failure triage (most common task)

```python
# Step 1 — find failing run IDs
runs = github-mcp-server-actions_list(
    method="list_workflow_runs", owner="Aries-Serpent", repo="_codex_",
    workflow_runs_filter={"status": "completed", "branch": BRANCH}, per_page=10
)
# Step 2 — get logs for the failed run
logs = github-mcp-server-get_job_logs(
    owner="Aries-Serpent", repo="_codex_",
    run_id=FAILED_RUN_ID, failed_only=True, return_content=True, tail_lines=200
)
```

### mypy ratchet (ongoing task)

```bash
# Count current errors
python3 -m mypy src/ --no-error-summary --ignore-missing-imports 2>&1 | grep "error:" | wc -l
# Breakdown by category
python3 -m mypy src/ --no-error-summary --ignore-missing-imports 2>&1 \
  | grep "error:" | sed 's/.*\[/[/' | sort | uniq -c | sort -rn | head -15
# Update baseline after fixing
echo "NEW_COUNT" > .mypy_baseline
```

Current baseline: **1008** (S46). Next target: **< 940**.
Remaining high-volume categories: `[attr-defined]`×298, `[assignment]`×193.

### Incremental commit rhythm

```python
report_progress(
    commitMessage="fix(S46): description of change",
    prDescription="- [x] completed item\n- [ ] pending item"
)
```

Push every 15–20 minutes of work. Never let unstaged changes accumulate across multiple
logical units.

---

## Critical anti-patterns (learned from failures)

### ❌ Dropping lines with over-broad `edit` old_str

When adding `# type: ignore[...]` to a line that's followed by an indented block,
**always include the following line** in `old_str` so it is preserved in `new_str`.

```python
# WRONG — drops `if track in {"A", "B"}:` (caused syntax error in policy.py S46)
edit(old_str='        ra_links: list[str] = ["RA-1", "RA-3"]',
     new_str='        ra_links: list[str] = ["RA-1", "RA-3"]  # type: ignore[no-redef]')

# CORRECT — preserves the if-block
edit(old_str='        ra_links: list[str] = ["RA-1", "RA-3"]\n        if track in {"A", "B"}:',
     new_str='        ra_links: list[str] = ["RA-1", "RA-3"]  # type: ignore[no-redef]\n        if track in {"A", "B"}:')
```

### ❌ Downloading binaries to the repo root

`.gitignore` line 426 blocks `actionlint` from being committed, but it's cleaner
to always download to `/tmp/`:

```bash
curl -fsSL https://github.com/rhysd/actionlint/releases/download/v1.7.7/\
actionlint_1.7.7_linux_amd64.tar.gz | tar xz -C /tmp actionlint
/tmp/actionlint .github/workflows/*.yml
```

### ❌ Removing `@pytest.mark.skip` without implementing the function

Always implement the missing function first, then remove the skip decorator.
Removing the skip first produces a failing test that blocks CI.

---

## Related documents

| Document | Path | Notes |
|----------|------|-------|
| Codebase Agency Policy | `.codex/CODEBASE_AGENCY_POLICY.md` | §0 pre-session rule — mandatory |
| CI Auto-Fix System | `.codex/docs/CI_AUTO_FIX_SYSTEM.md` | 8 auto-fix patterns, JSON output |
| MCP Workflow Recipes | `.codex/docs/MCP_WORKFLOW_RECIPES.md` | GitHub Actions + Playwright workflows |
| Custom Agent MCP Audit | `.codex/docs/CUSTOM_AGENT_MCP_INTEGRATION_AUDIT.md` | 54 agents × MCP gap analysis |
| Agent Definitions | `/home/runner/work/_temp/copilot-developer-action-main/dist/definitions/` | Live YAML; re-read each session |
| MCP Server Log | `/home/runner/work/_temp/cca-mcp-debug-logs/mcp-server.log` | Live tool registration log |
| src/mcp Developer Guide | `docs/mcp/MCP_DEVELOPER_GUIDE.md` | `src/mcp/` module (not this layer) |
