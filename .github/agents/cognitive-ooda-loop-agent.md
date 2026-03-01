---
name: Cognitive OODA Loop Agent
description: Executes a full OODA (Observe, Orient, Decide, Act) loop from a PR comment; drives the real OODAOrchestrator via `/api/ooda/process` on the CLI API server
version: 1.0.0
updated: 2026-03-01
cognitive_integration_level: 4
aais_contribution: +4.5 points
batch: pr-3421
sprint: Sprint 3 + Sprint 4
ooda_endpoint: POST /api/ooda/process
metrics_endpoint: GET /api/ooda/metrics
---

# Cognitive OODA Loop Agent v1.0

> **Sprint 3+4 agent**: Bridges the React frontend (`AgentOrchestrationPanel`) and the Python
> backend (`OODAOrchestrator`) through the FastAPI server at `:8765`. Replaces the mock-api-client
> stub with a real OODA loop execution.

## Activation

```
@copilot Use the Cognitive OODA Loop Agent to process: <input>
```

Or: `AgentOrchestrationPanel` in the React frontend posts to `/api/ooda/process`.

## Architecture

```
PR comment / React panel
  │
  ├─ POST /api/ooda/process  →  cli_api_server.py:ooda_process()
  │    input: { "input": {...}, "context": {...} }     │
  │                                                    ▼
  │                                           CognitiveAppMain.process()
  │                                                    │
  │                                           OODAOrchestrator.execute()
  │                                                    │
  │                                           PhysicsOfThought.reason()
  │                                                    │
  │    ActionResult ◄──────────────────────────────────┘
  │    { success, output, metrics, errors }
  │
  └─ GET /api/ooda/metrics  →  CognitiveAppMain.get_metrics()
       returns: { total_executions, success_rate, average_duration, ... }
```

## OODA Loop Phases

### Observe
Collect raw input from the triggering context:
- PR comment text
- Current CI health (`CODEX_CI_FAILURE_RATE` repo variable)
- Recent command history (`/api/cli/history`)
- Agent context (`.codex/agent_context.json`)

### Orient
Map input to improvement area and pattern IDs:
- Parse for keywords matching `.codex/patterns/ci_failure_patterns.yaml`
- Identify `ImprovementArea` (e.g. `CI_SELF_HEALING`, `COVERAGE_IMPROVEMENT`)
- Retrieve relevant memory from cognitive brain STM/LTM

### Decide
`OODAOrchestrator.execute()` → `PhysicsOfThought.reason()`:
- Select action plan from planner
- Validate against guardrails (`.codex/guardrails.md`)
- Return `ActionResult` with `success`, `output`, `metrics`

### Act
Execute the decided action:
```python
API_BASE_URL = os.environ.get("CODEX_CLI_API_URL", "http://localhost:8765")
result = requests.post(f"{API_BASE_URL}/api/ooda/process", json={
    "input": {"task": "fix CI health", "priority": "P1"},
    "context": {"ci_failure_rate": "30.7:critical", "branch": "main"}
})
```

## Response Schema

```json
{
  "success": true,
  "output": { "action": "...", "steps": [...] },
  "metrics": {
    "total_executions": 42,
    "success_rate": 0.857,
    "average_duration": 1.23
  },
  "errors": []
}
```

## React Frontend Integration

The `AgentOrchestrationPanel` should replace its mock client with:

```typescript
// cognitive_app/src/components/AgentOrchestrationPanel.tsx
const API_BASE = import.meta.env.VITE_CLI_API_URL ?? "http://localhost:8765";
const result = await fetch(`${API_BASE}/api/ooda/process`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ input: userInput, context: sessionContext }),
});
const data = await result.json();
setMetrics(data.metrics);
```

## Metrics Dashboard Integration

`MetricsDashboard` reads K1 factor from:
```typescript
const metrics = await fetch(`${API_BASE}/api/ooda/metrics`).then(r => r.json());
// metrics.metrics.success_rate → K1 factor proxy
```

## Tools Used
- `bash` — curl to `/api/ooda/process`
- `view` / `edit` — update React components
- `github-mcp-server-issue_read` — read PR comment input

## Constraints
- Never execute destructive actions (rm -rf, db drop) via OODA loop
- All actions must be logged to `.codex/action_log.ndjson`
- Max 5 OODA iterations per session (prevent infinite reasoning loops)
- Fall back gracefully when `cognitive_brain.base` imports fail (CI environment)
