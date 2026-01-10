# GitHub Actions Log Fetcher

Complete implementation for fetching GitHub Actions logs via MCP, CLI, and API.

## Overview

This implementation provides three interfaces for fetching logs from GitHub Actions:
1. **CLI** - Command-line interface for terminal usage
2. **API** - REST API endpoints for programmatic access
3. **MCP** - Model Context Protocol tools for AI agent integration

## Features

- ✅ Fetch check run logs by ID
- ✅ Fetch workflow job logs by ID
- ✅ List check runs for a git reference (commit, branch, tag)
- ✅ Multiple output formats (text, JSON)
- ✅ Comprehensive error handling
- ✅ Rate limit handling
- ✅ Authentication support via `GITHUB_TOKEN`

## Prerequisites

1. **GitHub Token**: Set the `GITHUB_TOKEN` environment variable:
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

2. **Dependencies**: Ensure required packages are installed:
   ```bash
   pip install httpx pydantic fastapi
   ```

## Usage

### 1. CLI Usage

#### Fetch Check Run Logs

```bash
# Basic usage
codex github-logs check-run Aries-Serpent _codex_ 59990656344

# Save to file
codex github-logs check-run Aries-Serpent _codex_ 59990656344 -o logs.txt

# Get as JSON
codex github-logs check-run Aries-Serpent _codex_ 59990656344 -f json
```

#### Fetch Job Logs

```bash
# Basic usage
codex github-logs job Aries-Serpent _codex_ 12345678

# Save to file
codex github-logs job Aries-Serpent _codex_ 12345678 -o job-logs.txt
```

#### List Check Runs

```bash
# List all check runs for a commit
codex github-logs list-check-runs Aries-Serpent _codex_ b6b52590b9551c4d29b90ea122d885ef83cd0d8d

# List only completed check runs
codex github-logs list-check-runs Aries-Serpent _codex_ main --status completed

# Filter by name
codex github-logs list-check-runs Aries-Serpent _codex_ main --name "CI Tests"
```

### 2. API Usage

#### Start the API Server

```bash
# Using FastAPI directly
uvicorn codex.api.app:app --reload

# Or integrate into existing FastAPI app
from codex.api.github_logs import router
app.include_router(router)
```

#### API Endpoints

**Get Check Run Logs**
```bash
curl "http://localhost:8000/github/check-runs/59990656344/logs?owner=Aries-Serpent&repo=_codex_" \
  -H "Authorization: Bearer $GITHUB_TOKEN"
```

**Get Job Logs**
```bash
curl "http://localhost:8000/github/jobs/12345678/logs?owner=Aries-Serpent&repo=_codex_" \
  -H "Authorization: Bearer $GITHUB_TOKEN"
```

**List Check Runs**
```bash
curl "http://localhost:8000/github/check-runs?owner=Aries-Serpent&repo=_codex_&ref=b6b52590b9551c4d29b90ea122d885ef83cd0d8d" \
  -H "Authorization: Bearer $GITHUB_TOKEN"
```

#### API Response Format

**Check Run Logs Response:**
```json
{
  "check_run_id": 59990656344,
  "owner": "Aries-Serpent",
  "repo": "_codex_",
  "check_run_name": "Test Coverage",
  "check_run_status": "completed",
  "check_run_conclusion": "success",
  "check_run_url": "https://github.com/Aries-Serpent/_codex_/runs/59990656344",
  "logs": "2024-01-10T12:00:00Z Starting job...\n..."
}
```

### 3. MCP Usage

#### Python Integration

```python
from mcp.tools.github_logs import fetch_check_run_logs, list_check_runs

# Fetch check run logs
result = fetch_check_run_logs({
    "owner": "Aries-Serpent",
    "repo": "_codex_",
    "check_run_id": 59990656344
})

if result["success"]:
    print(result["logs"])
else:
    print(f"Error: {result['error']}")

# List check runs
result = list_check_runs({
    "owner": "Aries-Serpent",
    "repo": "_codex_",
    "ref": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
    "status": "completed"
})

for run in result["check_runs"]:
    print(f"{run['id']}: {run['name']} - {run['conclusion']}")
```

#### AI Agent Integration

The MCP tools can be registered with AI agents for autonomous log fetching:

```python
from mcp.tools.github_logs import GITHUB_LOGS_TOOLS

# Register tools with your MCP server
for tool_name, tool_config in GITHUB_LOGS_TOOLS.items():
    mcp_server.register_tool(
        name=tool_config["name"],
        description=tool_config["description"],
        function=tool_config["function"],
        schema=tool_config["schema"]
    )
```

## Implementation Details

### Architecture

```
┌─────────────────┐
│   GitHub API    │
└────────┬────────┘
         │
┌────────▼─────────────────────────────────┐
│  services/github/client.py               │
│  - GitHubClient (async)                  │
│  - GitHubClientSync (sync wrapper)       │
│  - Check run methods                     │
│  - Job log methods                       │
└────────┬─────────────────────────────────┘
         │
         ├───────────────┬─────────────────┬
         │               │                 │
┌────────▼──────┐ ┌──────▼──────┐  ┌──────▼────────┐
│  CLI Interface │ │ API Endpoints│  │  MCP Tools    │
│  cli_github    │ │  api/github  │  │  mcp/tools/   │
│  _logs.py      │ │  _logs.py    │  │  github_logs  │
└────────────────┘ └──────────────┘  └───────────────┘
```

### Files Created/Modified

1. **GitHub Client Extensions** (`src/services/github/`)
   - `types.py` - Added `CheckRun`, `CheckRunStatus`, `CheckRunConclusion` types
   - `client.py` - Added `get_check_run`, `list_check_runs_for_ref`, `get_check_run_logs` methods

2. **CLI Implementation** (`src/codex/`)
   - `cli_github_logs.py` - Complete CLI with check-run, job, and list-check-runs commands
   - `cli.py` - Registered github-logs command group

3. **API Implementation** (`src/codex/api/`)
   - `github_logs.py` - FastAPI router with 3 endpoints

4. **MCP Implementation** (`src/mcp/tools/`)
   - `github_logs.py` - MCP tool functions and schemas

5. **Documentation** (`docs/`)
   - `GITHUB_LOGS_FETCHER.md` - This file

### Error Handling

All interfaces handle common errors:
- **404 Not Found** - Check run or job doesn't exist
- **401 Unauthorized** - Invalid or missing GitHub token
- **429 Rate Limit** - GitHub API rate limit exceeded
- **403 Forbidden** - Insufficient permissions
- **500 Server Error** - Other unexpected errors

### Rate Limiting

The GitHub client automatically tracks rate limits and includes retry logic with exponential backoff.

## Target Use Case: Fetching Specific Commit Check Logs

To fetch logs from the specific commit mentioned in the requirements:

**Commit**: `b6b52590b9551c4d29b90ea122d885ef83cd0d8d`  
**Check Run ID**: `59990656344`  
**Repository**: `Aries-Serpent/_codex_`

### CLI Method
```bash
codex github-logs check-run Aries-Serpent _codex_ 59990656344
```

### API Method
```bash
curl "http://localhost:8000/github/check-runs/59990656344/logs?owner=Aries-Serpent&repo=_codex_"
```

### MCP Method
```python
from mcp.tools.github_logs import fetch_check_run_logs

result = fetch_check_run_logs({
    "owner": "Aries-Serpent",
    "repo": "_codex_",
    "check_run_id": 59990656344
})
print(result["logs"])
```

## Testing

### Unit Tests

Create tests in `tests/services/github/test_github_logs.py`:

```python
import pytest
from services.github.client import GitHubClientSync

@pytest.fixture
def github_client():
    return GitHubClientSync()

def test_get_check_run(github_client):
    check_run = github_client.get_check_run(
        "Aries-Serpent",
        "_codex_",
        59990656344
    )
    assert check_run.id == 59990656344
    assert check_run.name is not None

def test_get_check_run_logs(github_client):
    logs = github_client.get_check_run_logs(
        "Aries-Serpent",
        "_codex_",
        59990656344
    )
    assert isinstance(logs, str)
    assert len(logs) > 0
```

### Integration Tests

Test CLI commands:
```bash
# Test check run logs
codex github-logs check-run Aries-Serpent _codex_ 59990656344 -o /tmp/test-logs.txt
test -f /tmp/test-logs.txt && echo "✓ CLI test passed"

# Test list check runs
codex github-logs list-check-runs Aries-Serpent _codex_ b6b52590b9551c4d29b90ea122d885ef83cd0d8d
```

## Security Considerations

1. **Token Storage**: Never commit `GITHUB_TOKEN` to version control
2. **Token Permissions**: Use fine-grained tokens with minimal required scopes:
   - `actions:read` - Read workflow runs and logs
   - `checks:read` - Read check runs
3. **Rate Limiting**: Implement caching to avoid excessive API calls
4. **Error Messages**: Avoid exposing sensitive information in error messages

## Future Enhancements

- [ ] Add caching for frequently accessed logs
- [ ] Support for downloading multiple check run logs in batch
- [ ] Integration with existing logging infrastructure
- [ ] WebSocket streaming for real-time log updates
- [ ] Support for filtering logs by timestamp or keywords
- [ ] Export logs in multiple formats (HTML, PDF)
- [ ] Integration with monitoring and alerting systems

## Troubleshooting

### Common Issues

**Problem**: `GitHub authentication failed`  
**Solution**: Ensure `GITHUB_TOKEN` is set and valid

**Problem**: `check run logs not found`  
**Solution**: Check runs may not have associated logs if they haven't run yet or logs have expired

**Problem**: `Rate limit exceeded`  
**Solution**: Wait for rate limit reset or use authenticated requests (higher limit)

**Problem**: `Module not found: httpx`  
**Solution**: Install dependencies: `pip install httpx pydantic`

## Support

For issues or questions:
1. Check the GitHub Issues page
2. Review the API documentation
3. Contact the maintainers

## License

MIT License - See LICENSE file for details
