# Guide: Resolving GH CLI Issues in GitHub Actions

> Generated: 2025-12-27 | Author: mbaetiong

To use GitHub CLI (gh) within GitHub Actions workflows, the most important step is to ensure authentication by setting the GH_TOKEN environment variable. This enables gh commands to interact securely with GitHub's API during the workflow. Below is an overview of the process and how to resolve common issues related to GH_TOKEN:

## 1. GitHub CLI in Actions

- The GitHub CLI is pre-installed on all GitHub-hosted runners, so you can directly call `gh` in your workflow steps without additional setup[[1]](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-github-cli)[[2]](https://www.polpiella.dev/how-to-use-the-github-cli-from-github-actions-workflows).

## 2. Authenticating with GH_TOKEN

- Assign the environment variable `GH_TOKEN` to `${{ secrets.GITHUB_TOKEN }}` for any step using GitHub CLI. Example:
  ```yaml
  steps:
    - run: gh issue create --title "Example issue" --body "Issue details."
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```
- You can set this globally (for the whole workflow), at the job level, or for individual steps—the most secure approach is per step, but job/workflow-level is more convenient for multiple commands[[3]](https://josh-ops.com/posts/gh-auth-login-in-actions/)[[4]](https://stackoverflow.com/questions/77841655/gh-auth-login-with-token-token-asks-to-paste-token).

## 3. Permissions Issues with GH_TOKEN

- By default, GITHUB_TOKEN is read-only. If you need to perform actions like pushing commits or creating pull requests, set higher permissions:
  ```yaml
  permissions:
    contents: write
    pull-requests: write
  ```
- If you encounter permission errors (e.g., "insufficient privileges"), check the permissions block at the top of your workflow and adjust as needed[[2]](https://www.polpiella.dev/how-to-use-the-github-cli-from-github-actions-workflows)[[4]](https://stackoverflow.com/questions/77841655/gh-auth-login-with-token-token-asks-to-paste-token).

## 4. Common Authentication Pitfalls

- Do not use other token names (like PAT); the GitHub CLI inside Actions expects GH_TOKEN.
- You do not need to run `gh auth login` interactively—if you set GH_TOKEN, gh automatically authenticates.
- If you run into issues where `gh` prompts you to "run gh auth login," it usually means GH_TOKEN is missing or misnamed in the environment variables[[3]](https://josh-ops.com/posts/gh-auth-login-in-actions/)[[4]](https://stackoverflow.com/questions/77841655/gh-auth-login-with-token-token-asks-to-paste-token).

## 5. Example Using gh Workflow Commands

You can run and manage workflows from the CLI both locally and within Actions. For example:
  ```yaml
  steps:
    - run: gh workflow run test.yml --ref main
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```
- The `gh workflow`, `gh run`, and other commands allow advanced workflow management directly from Actions or your terminal[[5]](https://blogs.reliablepenguin.com/2025/07/15/automating-github-actions-workflows-with-the-gh-cli)[[6]](https://commandmasters.com/commands/gh-workflow-common/)[[7]](https://cli.github.com/manual/gh_workflow).

## Fallback: Using GitHub MCP Tools

When GH CLI is not available in the current environment (e.g., Copilot Agent sessions without GH_TOKEN configured), use the GitHub MCP (Model Context Protocol) tools instead:

### Available GitHub MCP Tools

```python
# List workflow runs
github-mcp-server-actions_list(
    method="list_workflow_runs",
    owner="Aries-Serpent",
    repo="_codex_",
    resource_id="workflow-file.yml"
)

# Get workflow run details
github-mcp-server-actions_get(
    method="get_workflow_run",
    owner="Aries-Serpent",
    repo="_codex_",
    resource_id="<run_id>"
)

# List jobs in a workflow run
github-mcp-server-actions_list(
    method="list_workflow_jobs",
    owner="Aries-Serpent",
    repo="_codex_",
    resource_id="<run_id>"
)
```

### Example: Checking CI Status

```python
# Instead of: gh run list --branch main --limit 10
# Use GitHub MCP:

workflow_runs = github-mcp-server-actions_list(
    method="list_workflow_runs",
    owner="Aries-Serpent",
    repo="_codex_",
    resource_id="ci.yml",
    per_page=10
)

# Parse results
for run in workflow_runs["workflow_runs"]:
    print(f"Run {run['id']}: {run['conclusion']}")
```

### When to Use Each Approach

| Scenario | Tool | Notes |
|----------|------|-------|
| In GitHub Actions | `gh` CLI | Fastest, native integration |
| Local development | `gh` CLI | Requires authentication |
| Copilot Agent | GitHub MCP tools | No GH_TOKEN needed |
| API rate limits | GitHub MCP tools | Better error handling |

---

## References

- [Official docs: Using GitHub CLI in workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-github-cli)[[1]](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-github-cli)  
- [Automate tasks with gh CLI in GitHub Actions](https://www.polpiella.dev/how-to-use-the-github-cli-from-github-actions-workflows)[[2]](https://www.polpiella.dev/how-to-use-the-github-cli-from-github-actions-workflows)  
- [How to use gh auth login in Actions (best practices)](https://josh-ops.com/posts/gh-auth-login-in-actions/)[[3]](https://josh-ops.com/posts/gh-auth-login-in-actions/)  
- [Workflow and permissions troubleshooting (Stack Overflow)](https://stackoverflow.com/questions/77841655/gh-auth-login-with-token-token-asks-to-paste-token)[[4]](https://stackoverflow.com/questions/77841655/gh-auth-login-with-token-token-asks-to-paste-token)  
- [Managing workflows via CLI](https://commandmasters.com/commands/gh-workflow-common/)[[6]](https://commandmasters.com/commands/gh-workflow-common/)

---

**Last Updated**: 2025-12-27  
**Maintainer**: @mbaetiong
