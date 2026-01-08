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
- The `gh workflow`, `gh run`, and other commands allow advanced workflow management directly from Actions or your terminal[[5]](https://blogs.reliablepenguin.com/2024/07/15/automating-github-actions-workflows-with-the-gh-cli)[[6]](https://commandmasters.com/commands/gh-workflow-common/)[[7]](https://cli.github.com/manual/gh_workflow).

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

# Alternatives for Checking Workflow Runs (Extended Guide)

> Updated: 2025-12-27T12:00:00Z

When `gh` CLI is unavailable or you want more control, use these alternative methods:

## Quick Comparison Table

| Method | Best for | Authentication | Tools |
|--------|----------|----------------|-------|
| REST API (curl) | Quick shell checks in any runner | GITHUB_TOKEN or PAT | curl + jq |
| Octokit (JS/TS) | Node/npm steps, richer logic | GITHUB_TOKEN or PAT | @octokit/rest |
| @actions/github | Steps inside GitHub Actions workflows | GITHUB_TOKEN | actions/github-script |
| Python (requests/PyGithub) | Python-based steps or scripts | GITHUB_TOKEN or PAT | requests, PyGithub |
| Cached API data / artifacts | Offline analysis or rate-limited scenarios | No runtime auth needed | upload/download-artifact |

## Core REST API Endpoints

| Purpose | Endpoint | Query Params |
|---------|----------|--------------|
| List workflow runs | `GET /repos/{owner}/{repo}/actions/runs` | branch, event, status, per_page, page |
| List runs for workflow | `GET /repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs` | branch, status, per_page |
| Get workflow run | `GET /repos/{owner}/{repo}/actions/runs/{run_id}` | - |
| List jobs for run | `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs` | per_page |
| Rerun workflow | `POST /repos/{owner}/{repo}/actions/runs/{run_id}/rerun` | - |
| Cancel workflow | `POST /repos/{owner}/{repo}/actions/runs/{run_id}/cancel` | - |

## Practical Examples

### 1. Detect gh and Fallback to curl

```bash
if command -v gh >/dev/null 2>&1 && [ -n "$GH_TOKEN" ]; then
  gh run list --branch "$BRANCH" --limit 10 --json databaseId,status,conclusion,name,createdAt,workflowName
else
  echo "gh CLI not available — using REST API"
  curl -s \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=10" \
  | jq '.workflow_runs[] | {id: .id, name: .name, status: .status, conclusion: .conclusion, created_at: .created_at, workflow: .workflow_name}'
fi
```

### 2. Find Runs with action_required Status

```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=50" \
| jq '.workflow_runs | map(select(.status=="completed" and (.conclusion == null or .conclusion=="action_required")))'
```

### 3. List Runs for Specific Workflow

```bash
# Using workflow filename
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/workflows/ci.yml/runs?branch=$BRANCH&per_page=20"
```

### 4. Node.js + Octokit

```javascript
const { Octokit } = require("@octokit/rest");
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

async function listRuns(owner, repo, branch) {
  const res = await octokit.actions.listWorkflowRunsForRepo({
    owner,
    repo,
    branch,
    per_page: 20
  });
  return res.data.workflow_runs;
}

// Usage
const runs = await listRuns("Aries-Serpent", "_codex_", "main");
console.log(runs.map(r => ({ 
  id: r.id, 
  name: r.name, 
  status: r.status, 
  conclusion: r.conclusion 
})));
```

### 5. GitHub Actions Step using github-script

```yaml
- name: Check workflow runs
  uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    script: |
      const runs = await github.rest.actions.listWorkflowRunsForRepo({
        owner: context.repo.owner,
        repo: context.repo.repo,
        branch: process.env.BRANCH || context.ref.replace('refs/heads/',''),
        per_page: 10
      });
      
      const runData = runs.data.workflow_runs.map(r => ({
        id: r.id,
        name: r.name,
        status: r.status,
        conclusion: r.conclusion,
        created_at: r.created_at
      }));
      
      console.log(JSON.stringify(runData, null, 2));
      
      // Check for action_required
      const actionRequired = runData.filter(r => r.conclusion === 'action_required');
      if (actionRequired.length > 0) {
        core.warning(`Found ${actionRequired.length} runs requiring action`);
      }
```

### 6. Python with requests

```python
import os
import requests

def list_workflow_runs(owner, repo, branch, token):
    """List workflow runs using GitHub REST API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    params = {
        "branch": branch,
        "per_page": 10
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    runs = response.json().get("workflow_runs", [])
    return runs

# Usage
token = os.environ['GITHUB_TOKEN']
runs = list_workflow_runs("Aries-Serpent", "_codex_", "main", token)
for run in runs:
    print(f"Run {run['id']}: {run['name']} - {run['status']} ({run['conclusion']})")
```

### 7. Python with PyGithub

```python
from github import Github
import os

g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo("Aries-Serpent/_codex_")

# Note: PyGithub has limited Actions API support
# For full control, use requests library with REST API directly
```

## Permissions and Tokens

### In GitHub Actions Workflows

```yaml
permissions:
  actions: read        # For listing/reading runs
  contents: read       # For checking out code
  
# For rerun/cancel operations:
permissions:
  actions: write
  contents: read
```

### Using the Token

```yaml
steps:
  - name: Check runs with curl
    run: |
      curl -s -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
        -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/${{ github.repository }}/actions/runs"
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Fallback Strategies

### Save API Snapshot as Artifact

```yaml
jobs:
  capture-ci-state:
    runs-on: ubuntu-latest
    steps:
      - name: Snapshot workflow runs
        run: |
          curl -s -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/repos/${{ github.repository }}/actions/runs?branch=${{ github.ref_name }}&per_page=100" \
            > runs.json
      
      - name: Upload snapshot
        uses: actions/upload-artifact@v4
        with:
          name: workflow-runs-snapshot
          path: runs.json
          retention-days: 7

  analyze-offline:
    needs: capture-ci-state
    runs-on: ubuntu-latest
    steps:
      - name: Download snapshot
        uses: actions/download-artifact@v4
        with:
          name: workflow-runs-snapshot
      
      - name: Analyze runs offline
        run: |
          jq '.workflow_runs | map(select(.conclusion == "action_required"))' runs.json
```

## Rerun and Cancel Operations

### Rerun a Workflow

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun"
```

### Cancel a Workflow

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/cancel"
```

## Troubleshooting Checklist

When investigating CI issues without gh CLI:

1. **Detect gh availability**
   ```bash
   command -v gh && [ -n "$GH_TOKEN" ] || echo "Fallback to REST API"
   ```

2. **List runs with curl + jq**
   ```bash
   curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
     "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH" \
   | jq '.workflow_runs[] | select(.conclusion == "action_required")'
   ```

3. **Inspect failed/pending jobs**
   ```bash
   curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
     "https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/jobs" \
   | jq '.jobs[] | select(.conclusion != "success")'
   ```

4. **Check environment protection** (if action_required)
   - Review protected environments in repository settings
   - Check required reviewers and approvals
   - Inspect deployment protection rules

5. **Save snapshot for offline analysis**
   ```bash
   curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
     "https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID" \
     > run-$RUN_ID.json
   ```

## Complete Workflow Example

```yaml
name: CI Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

permissions:
  actions: read
  contents: read

jobs:
  check-ci-health:
    runs-on: ubuntu-latest
    steps:
      - name: Detect gh CLI availability
        id: detect
        run: |
          if command -v gh >/dev/null 2>&1 && [ -n "$GH_TOKEN" ]; then
            echo "method=gh" >> $GITHUB_OUTPUT
          else
            echo "method=api" >> $GITHUB_OUTPUT
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Check runs with gh
        if: steps.detect.outputs.method == 'gh'
        run: |
          gh run list --repo ${{ github.repository }} --limit 20 --json status,conclusion,name
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Check runs with API
        if: steps.detect.outputs.method == 'api'
        run: |
          curl -s -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/repos/${{ github.repository }}/actions/runs?per_page=20" \
          | jq '.workflow_runs[] | {name, status, conclusion, created_at}'
      
      - name: Find action_required runs
        run: |
          curl -s -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/repos/${{ github.repository }}/actions/runs?per_page=50" \
          | jq '.workflow_runs | map(select(.conclusion == "action_required")) | length' \
          | xargs -I {} echo "Found {} runs requiring action"
```

## Additional Resources

- [GitHub Actions REST API Reference](https://docs.github.com/en/rest/actions)
- [Octokit.js Documentation](https://octokit.github.io/rest.js/)
- [GitHub Actions Toolkit](https://github.com/actions/toolkit)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)

---

**Last Updated**: 2025-12-27  
**Maintainer**: @mbaetiong
