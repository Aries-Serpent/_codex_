---
name: Cognitive OODA Loop Agent
description: Full OODA loop execution from PR comment or React frontend — wires OODAOrchestrator
  through FastAPI :8765; Phase 4 adds SQLiteMemory persistence and GitHub API auth
  forwarding
version: 2.0.0
updated: 2026-03-01
cognitive_integration_level: 5
aais_contribution: +5.0 points
batch: pr-3422
sprint: Sprint 3+4 (v1) → Phase 4 (v2)
ooda_endpoint: POST /api/ooda/process
metrics_endpoint: GET /api/ooda/metrics
memory_endpoint: GET /api/memory/state
improvement_area: CI_SELF_HEALING
pattern_id: P-047
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: cognitive-ooda-loop
---

# Cognitive OODA Loop Agent v2.0

> **Phase 4 upgrade**: Extended with `SQLiteMemory` persistence (STM/LTM),
> GitHub API auth header forwarding, and xterm.js PTY integration.
> Bridges the React frontend (`AgentOrchestrationPanel`) and the Python
> backend (`OODAOrchestrator`) through the FastAPI server at `:8765`.

## Activation

```
@copilot Use the Cognitive OODA Loop Agent to process: <input>
```

Or: `AgentOrchestrationPanel` → `POST /api/ooda/process`.

---

## Full Architecture (Phase 4)

```
┌─────────────────────────────────────────────────────────────────────┐
│             COGNITIVE OODA LOOP AGENT — PHASE 4 WIRING               │
│                                                                       │
│  Entry Points                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ PR comment   │  │ AgentOrch.   │  │ XtermTerminal.tsx         │   │
│  │ @copilot ... │  │ Panel (React)│  │ ws://localhost:8765/ws/cli│   │
│  └──────┬───────┘  └──────┬───────┘  └───────────────┬──────────┘   │
│         │                 │                           │               │
│         └────────┬────────┘           ┌──────────────┘               │
│                  │ POST               │ WebSocket PTY                 │
│                  ▼                    ▼                               │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  FastAPI cli_api_server.py — :8765                           │     │
│  │                                                              │     │
│  │  /api/ooda/process ──► CognitiveAppMain.process()            │     │
│  │       │                      │                               │     │
│  │       │              OODAOrchestrator.execute()               │     │
│  │       │                      │                               │     │
│  │       │              PhysicsOfThought.reason()                │     │
│  │       │                      │                               │     │
│  │       │              SQLiteMemory.store(key, result) ◄── P4.2│     │
│  │       │                      │                               │     │
│  │       ◄──────────────────────┘                               │     │
│  │       ActionResult { success, output, metrics, errors }       │     │
│  │                                                              │     │
│  │  /api/ooda/metrics ──► CognitiveAppMain.get_metrics()        │     │
│  │  /api/memory/state ──► stm_count, ltm_count, capacity ◄─P4.2│     │
│  │  /api/memory/search──► UNION stm_entries + ltm_entries ◄─P4.2│    │
│  │  /api/request      ──► httpx proxy + GitHub auth ◄──── P4.3  │     │
│  │  /ws/cli           ──► PTY subprocess (xterm.js) ◄───── P4.4 │     │
│  └──────────────────────────────┬──────────────────────────────┘     │
│                                  │                                    │
│  ┌───────────────────────────────▼──────────────────────────────┐    │
│  │  SQLite — CODEX_DB_PATH (~/.codex/cli_history.db)             │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐  │    │
│  │  │stm_entries │  │ltm_entries │  │cli_history             │  │    │
│  │  │key, value, │  │key, value, │  │command, stdout, stderr │  │    │
│  │  │metadata,   │  │metadata,   │  │returncode, duration_ms │  │    │
│  │  │access_count│  │confidence, │  │cwd, timestamp          │  │    │
│  │  │timestamp   │  │pattern_type│  └────────────────────────┘  │    │
│  │  └────────────┘  │timestamp   │                              │    │
│  │                  └────────────┘                              │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  React Frontend                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  VITE_CLI_API_URL=http://localhost:8765                        │    │
│  │  use-memory-system   → /api/memory/state + /api/memory/search │    │
│  │  use-agent-orch      → /api/ooda/process + /api/ooda/metrics  │    │
│  │  use-quantum-state   → /api/ooda/metrics (K1 factor)          │    │
│  │  XtermTerminal.tsx   → ws://localhost:8765/ws/cli             │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## OODA Loop Phases

### Observe
Collect raw input from the triggering context:
- PR comment text or `AgentOrchestrationPanel` task input
- Current CI health (`CODEX_CI_FAILURE_RATE` repo variable)
- Recent command history (`GET /api/cli/history`)
- Agent context (`.codex/agent_context.json`)
- **Phase 4**: STM memory state (`GET /api/memory/state`)

### Orient
Map input to improvement area and pattern IDs:
- Parse keywords against `.codex/patterns/ci_failure_patterns.yaml`
- Identify `ImprovementArea` (`CI_SELF_HEALING`, `ML_PATTERN_FEEDING`, etc.)
- **Phase 4**: Retrieve relevant context from SQLiteMemory STM/LTM

### Decide
`OODAOrchestrator.execute()` → `PhysicsOfThought.reason()`:
- Select action plan from planner
- Validate against guardrails (`.codex/guardrails.md`)
- **Phase 4**: Auto-init with `SQLiteMemory()` if `_orchestrator` is None

### Act
Execute the decided action; persist result:
```python
API_BASE_URL = os.environ.get("CODEX_CLI_API_URL", "http://localhost:8765")
result = requests.post(f"{API_BASE_URL}/api/ooda/process", json={
    "input": {"task": "fix CI health", "priority": "P1"},
    "context": {"ci_failure_rate": "30.7:critical", "branch": "main"}
})
# Phase 4: result is persisted to stm_entries by SQLiteMemory.store()
```

---

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

---

## React Frontend Integration (Phase 4 — real API)

```typescript
// cognitive_app/src/hooks/use-agent-orchestration.ts
const API_URL = import.meta.env.VITE_CLI_API_URL
             ?? import.meta.env.VITE_CODEX_API
             ?? 'http://localhost:8765';

// AgentOrchestrationPanel
const result = await fetch(`${API_URL}/api/ooda/process`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ input: userInput, context: sessionContext }),
});
const data = await result.json();
setMetrics(data.metrics);
```

---

## Codebase Alignment

| Component | Location | Phase |
|-----------|----------|-------|
| `ooda_process()` | `cli_api_server.py` | v1 (PR #3421) |
| `ooda_metrics()` | `cli_api_server.py` | v1 (PR #3421) |
| `SQLiteMemory` class | `cli_api_server.py` | v2 (PR #3422) |
| `memory_state()` | `cli_api_server.py` | v2 (PR #3422) |
| `memory_search()` | `cli_api_server.py` | v2 (PR #3422) |
| Auth forwarding | `api_proxy()` in `cli_api_server.py` | v2 (PR #3422) |
| `use-agent-orchestration.ts` | `cognitive_app/src/hooks/` | v2 (PR #3422) |
| `XtermTerminal.tsx` | `cognitive_app/src/components/cli/` | v2 (PR #3422) |
| `App.tsx` CLI tab | `cognitive_app/src/App.tsx` | v2 (PR #3422) |

---

## Constraints

| Constraint | Value |
|------------|-------|
| Destructive actions | Never (rm -rf, db drop, etc.) |
| Logging | All actions → `.codex/action_log.ndjson` |
| Max OODA iterations | 5 per session (anti-loop guard) |
| CI fallback | Graceful when `cognitive_brain.base` unavailable |
| Auth injection | Only for `api.github.com` — never for arbitrary URLs |
| Token exposure | Never log or return in response headers |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-01 | Initial — OODA endpoints, CognitiveAppMain wiring (PR #3421) |
| 2.0.0 | 2026-03-01 | Phase 4: SQLiteMemory persistence, GitHub auth forwarding, xterm.js wiring, full architecture diagram, codebase alignment table (PR #3422) |
