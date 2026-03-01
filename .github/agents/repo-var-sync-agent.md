---
name: Repo Var Sync Agent
description: Keeps `.codex/agent_context.json` bidirectionally in sync with GitHub Actions repository variables (COPILOT_* / CODEX_*)
version: 1.0.0
updated: 2026-03-01
cognitive_integration_level: 3
aais_contribution: +2.5 points
batch: pr-3421
sprint: Sprint 4
---

# Repo Var Sync Agent v1.0

> **Sprint 4 agent**: Ensures `.codex/agent_context.json` and GitHub Actions repo variables
> (`COPILOT_*` / `CODEX_*`) are always in sync. Runs as part of `copilot-agent-vars-bootstrap.yml`
> and can be triggered manually for drift detection.

## Activation

```
@copilot Use the Repo Var Sync Agent to sync agent_context.json with repo variables
```

## Architecture

```
Direction A (vars → file):   GitHub API repo vars  →  .codex/agent_context.json
Direction B (file → vars):   .codex/agent_context.json  →  GitHub API PATCH/POST
Drift detection:             diff both sources → report mismatches
```

## Responsibilities

### Direction A — Variables → File (bootstrap sync)
Used by `copilot-agent-vars-bootstrap.yml` to inject context at session start:

```python
import os, json, requests

token  = os.environ["CODEX_MASTER_KEY"]
owner  = "Aries-Serpent"
repo   = "_codex_"
url    = f"https://api.github.com/repos/{owner}/{repo}/actions/variables"
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

resp = requests.get(url, headers=headers)
vars_data = {v["name"]: v["value"] for v in resp.json().get("variables", [])}

# Write only COPILOT_* and CODEX_* prefixed vars
context = {k: v for k, v in vars_data.items()
           if k.startswith(("COPILOT_", "CODEX_"))}

os.makedirs(".codex", exist_ok=True)
with open(".codex/agent_context.json", "w") as f:
    json.dump(context, f, indent=2)
print(f"Wrote {len(context)} variables to .codex/agent_context.json")
```

### Direction B — File → Variables (propagate local changes)
When an agent updates `.codex/agent_context.json` and the change should persist:

```python
# For each key in agent_context.json:
# 1. Try PATCH (update existing)
# 2. Fall back to POST (create new)
for key, value in context.items():
    r = requests.patch(f"{url}/{key}", json={"value": str(value)}, headers=headers)
    if r.status_code == 404:
        requests.post(url, json={"name": key, "value": str(value)}, headers=headers)
```

### Drift Detection
Compares file vs API and reports any key/value mismatches:

```
DRIFT REPORT:
  Missing in file:    CODEX_NEW_VAR
  Missing in API:     CODEX_OLD_LOCAL_ONLY
  Value mismatch:     CODEX_CI_FAILURE_RATE file=8.2:ok API=30.7:critical
```

## Integration Points
- `copilot-agent-vars-bootstrap.yml` — runs Direction A on every PR push
- `copilot-setup-steps.yml` — injects file into GITHUB_ENV (reads Direction A output)
- `agent-var-writer.yml` — autonomous variable writing (Direction B)
- `ci-health-monitor.yml` — updates `CODEX_CI_FAILURE_RATE` (Direction B single var)

## Tools Used
- `bash` — curl/python3 API calls
- `view` / `edit` — read/write `.codex/agent_context.json`
- `github-mcp-server-actions_get` — read existing variable values

## Constraints
- Never write secrets to `.codex/agent_context.json` (plain-text file)
- Only sync `COPILOT_*` and `CODEX_*` prefixed variables
- Always use `CODEX_MASTER_KEY` for write operations; fall back to `CODEX_BACKUP_KEY`
- Rate limit: max 10 API calls per sync operation
