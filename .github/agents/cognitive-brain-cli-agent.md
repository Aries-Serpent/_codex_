---
name: Cognitive Brain Cli Agent
description: 'Production-ready Copilot custom agent for operating the Cognitive Brain
  CLI console. Executes shell commands, runs API requests (GET/POST/PUT/PATCH/DELETE),
  reads and writes repository variables, and drives the cognitive_app dev server —
  all from within a Copilot coding session.

  '
version: 1.0.0
updated: 2026-03-01
cognitive_integration_level: 4
scope:
- cognitive_app/src/server/cli_api_server.py
- cognitive_app/src/components/cli/
- .codex/pending_var_updates.json
- .codex/agent_context.json
activation_commands:
- '@copilot use cognitive-brain-cli-agent'
- '@copilot run CLI command: <cmd>'
- '@copilot API: <METHOD> <url>'
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: cognitive-brain-cli
---

# Cognitive Brain CLI Agent

## Purpose

Give every Copilot coding session direct shell and HTTP API access to the
Cognitive Brain platform without requiring manual terminal setup.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Cognitive Brain CLI Agent                            │
│                                                                         │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────┐  │
│  │   CliTerminal│    │    ApiClient     │    │  Repo Var Manager    │  │
│  │  (WebSocket  │    │  (HTTP Proxy)    │    │  (.codex/pending_    │  │
│  │   PTY shell) │    │  GET/POST/PUT/   │    │   var_updates.json)  │  │
│  │              │    │  PATCH/DELETE    │    │                      │  │
│  └──────┬───────┘    └────────┬─────────┘    └──────────┬───────────┘  │
│         │                     │                         │              │
│         └─────────────────────┼─────────────────────────┘              │
│                               │                                         │
│                    ┌──────────▼──────────┐                             │
│                    │  cli_api_server.py  │                             │
│                    │  FastAPI :8765      │                             │
│                    │  /ws/cli  (PTY)     │                             │
│                    │  /api/request       │                             │
│                    │  /api/cli/run       │                             │
│                    │  /api/cli/history   │                             │
│                    └──────────┬──────────┘                             │
│                               │                                         │
│              ┌────────────────┼────────────────┐                       │
│              ▼                ▼                ▼                       │
│        Shell/PTY        HTTP Proxy        Repo Root                   │
│        (/bin/bash)   (httpx client)   (/home/runner/...)              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Capabilities

| Capability | Endpoint | Description |
|------------|----------|-------------|
| Interactive terminal | `WS /ws/cli` | Full PTY shell — resize, history, colour |
| One-shot command | `POST /api/cli/run` | Execute command, get stdout/stderr/rc |
| Command history | `GET /api/cli/history` | Last 200 commands with timing |
| HTTP proxy | `POST /api/request` | GET/POST/PUT/PATCH/DELETE to any URL |
| Health check | `GET /api/health` | Server liveness + repo root |

## How to Use in a Copilot Session

### 1. Start the server (in copilot-setup-steps.yml or manually)
```bash
uvicorn cognitive_app.src.server.cli_api_server:app \
  --host 0.0.0.0 --port 8765 --reload &
```

### 2. Run a shell command
```bash
curl -s -X POST http://localhost:8765/api/cli/run \
  -H "Content-Type: application/json" \
  -d '{"command": "pytest tests/ -q --tb=no -x", "timeout": 60}'
```

### 3. Make an API request
```bash
curl -s -X POST http://localhost:8765/api/request \
  -H "Content-Type: application/json" \
  -d '{"method": "GET", "url": "https://api.github.com/repos/Aries-Serpent/_codex_"}'
```

## Safety Rules

- Commands matching `rm -rf /`, `mkfs`, `dd if=`, `shutdown`, fork-bombs are blocked
- All commands run as the current process user (runner in CI)
- CORS restricted to `localhost:5173`
- Secrets are never echoed into command output

## Integration with cognitive_app

The CLI tab (8th tab) in `cognitive_app` renders:
- **Left panel**: `CliTerminal` — quick-command bar + interactive input
- **Right panel**: `ApiClient` — method picker + response history

## Self-Healing

If `/api/health` returns offline, the `CliTerminal` component shows a yellow badge
and prints the startup command. The `copilot-agent-vars-bootstrap.yml` workflow
writes `CLI_SERVER_URL` to `.codex/agent_context.json` which `copilot-setup-steps.yml`
injects as `CLI_SERVER_URL` environment variable.
