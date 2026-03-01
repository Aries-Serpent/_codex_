# 🧠 Tailored Copilot Coding Agent Prompt
# Aries-Serpent/_codex_ — Maximising Agent Capability
#
# USAGE: Paste this prompt when assigning an issue to @copilot, or as the
#        opening message in a /copilot session.  It injects full codebase
#        context so the agent operates at maximum effectiveness.
#
# ─────────────────────────────────────────────────────────────────────────────

You are working in the **Aries-Serpent/_codex_** repository — a production-grade
Python + TypeScript monorepo for the **Codex Cognitive Brain** system.

## 🗺 Repository Map (memorise this)

```
_codex_/
├── src/codex/           Python core: cognitive, rag, api, cli, logging, zendesk
├── src/codex_ml/        ML layer: AST, embeddings, telemetry server
├── src/cognitive_brain/ OODA loop base classes (Planner, MemoryInterface, PhysicsOfThought)
├── cognitive_app/       React 19 + Vite + Tailwind — the Cognitive Brain Console UI
│   ├── src/components/quantum-viz/   30+ quantum visualisation components
│   ├── src/components/cli/           CliTerminal + ApiClient (WebSocket PTY + HTTP proxy)
│   ├── src/lib/                      codex-api-client.ts, mock-api-client.ts, spark-llm-client.ts
│   └── src/server/cli_api_server.py  FastAPI: /ws/cli (PTY), /api/request (proxy), /api/cli/run
├── scripts/ci/          collect_telemetry.py, safe_git_show.sh, pre_flight_check.py
├── .github/workflows/   89 workflows — ALL have branch-scoped concurrency + timeouts
├── .codex/              Cognitive brain memory, agent auth session, pending var updates
│   ├── docs/WORKFLOW_BEST_PRACTICES.md   authoritative workflow reference
│   ├── docs/GROUNDED_VS_SOFT_ENFORCEMENT.md
│   └── pending_var_updates.json          agent autonomous variable requests
└── tests/               pytest — run with `nox -s tests` or `pytest tests/ -x -q`
```

## ⚙️ Environment & Toolchain

| Tool | Command |
|------|---------|
| Format   | `black src/ tests/` |
| Lint     | `ruff check src/ tests/ --fix` |
| Types    | `mypy src/` |
| Tests    | `nox -s tests` OR `pytest tests/ -x -q` |
| Pre-commit | `pre-commit run --files <changed_files>` |
| Frontend build | `cd cognitive_app && npm run build` |
| Frontend dev   | `cd cognitive_app && npm run dev` |
| CLI server     | `uvicorn cognitive_app.src.server.cli_api_server:app --port 8765 --reload` |

## 🔑 Variable & Secret Access

| Name | Scope | Purpose |
|------|-------|---------|
| `CODEX_MASTER_KEY` | Repository secret | GitHub PAT — repo write, variables write, workflow dispatch |
| `CODEX_BACKUP_KEY` | Repository secret | Fallback PAT |
| `GITHUB_TOKEN`     | Workflow token   | Read-only inside agent runtime |
| `vars.*`           | Repo variables   | Non-sensitive config — readable in setup steps |
| `COPILOT_AGENT_AUTH_ENABLED` | Repo variable | `true` when agent delegation is active (TTL 4h) |
| `COPILOT_AGENT_SESSION_EXPIRES` | Repo variable | ISO timestamp for session expiry |

**To write a repo variable autonomously:**
1. Write `.codex/pending_var_updates.json` in your commit
2. Post `@agent-var-writer apply` as a PR comment
3. `agent-var-writer.yml` validates the session token and applies it via `CODEX_MASTER_KEY`

## 🏗 Cognitive Brain Console (cognitive_app)

The app is a **React 19 + Vite + Tailwind + Radix UI** SPA with these tabs:

| Tab | Component | What it does |
|-----|-----------|-------------|
| Dashboard | MetricsDashboard | Live K1, coherence, quantum advantage metrics |
| Code | CodeGenerator | LLM-backed code generation |
| Demo | InteractiveDemo | Execute generated code in-browser |
| Quantum | QuantumVisualizer | Decision superposition viewer |
| Memory | MemoryManagementDashboard | STM/LTM explorer |
| Agents | AgentOrchestrationPanel | Live agent status, task queue |
| Physics | QuantumDecisionEngine | Physics-of-thought paradigms |
| **CLI** | **CliTerminal + ApiClient** | **Shell terminal + HTTP API client** |

Adding a new tab:
```tsx
// 1. In App.tsx — add TabsTrigger + TabsContent
// 2. Import component from src/components/<category>/
// 3. Match grid-cols-N in TabsList
```

## 🤖 Agent Empowerment Rules

1. **NEVER stop after one commit.** Keep working until all checklist items are ✅
2. **Always check `/tmp` and `git ls-files --others --ignored --exclude-standard`** before finalising
3. **Use `report_progress` frequently** — commit small verified chunks
4. **Grounded-first**: Every policy with a workflow gate is GROUNDED. Soft = advisory only.
5. **Concurrency template** for every new workflow:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
     cancel-in-progress: true  # false for deployment workflows
   ```
6. **Timeout template** by category: utility=10min, standard=30min, coverage=45min, heavy=60min
7. **For CI failures**: Use `github-mcp-server-get_job_logs` → diagnose → fix → verify YAML parses

## 📐 Code Style

- Python: Black + Ruff + isort. Type-annotate everything. Docstrings on all public APIs.
- TypeScript: Functional components. Tailwind utility classes. Radix UI primitives. `@phosphor-icons/react` for icons.
- YAML: Never use bare `<<` (YAML merge key conflict). Use `base64 -d | python3` pattern for embedded scripts.
- Avoid heredocs (`<< 'EOF'`) inside GitHub Actions `run: |` blocks — use `base64` encoding or write helper scripts in a prior `run:` step.

## 🔍 Key Patterns in this Codebase

```python
# Cognitive brain entry point
from cognitive_app.src.orchestrator import process_through_cognitive_app
result = process_through_cognitive_app({"input": "...", "type": "task"})

# Repo variable write (autonomous)
import json, pathlib
updates = {"COPILOT_AGENT_STATE": "active", "LAST_SESSION_ID": session_id}
pathlib.Path(".codex/pending_var_updates.json").write_text(json.dumps(updates, indent=2))
# Then commit + comment "@agent-var-writer apply"
```

```typescript
// CLI server one-shot command
const result = await fetch('http://localhost:8765/api/cli/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ command: 'git status --short', timeout: 10 })
});

// HTTP API proxy
const resp = await fetch('http://localhost:8765/api/request', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ method: 'GET', url: 'https://api.github.com/repos/Aries-Serpent/_codex_' })
});
```

## 📋 Current PR Status (copilot/investigate-ci-failure-rate)

- ✅ 89/89 workflows: branch-scoped concurrency + timeouts
- ✅ GROUNDED enforcement: REQ-7 commit-count gate, session-incremental-summary-reminder
- ✅ CLI server: FastAPI `/ws/cli` (PTY) + `/api/request` (proxy) + `/api/cli/run`
- ✅ Frontend: CliTerminal + ApiClient wired into cognitive_app as 8th tab
- ✅ WORKFLOW_BEST_PRACTICES.md: comprehensive reference document
- ✅ ci-health-monitor.yml: all YAML parse errors fixed (base64 script pattern)
- ✅ Repo-vars injection workflow: `copilot-agent-vars-bootstrap.yml`

**Contact:** @mbaetiong — escalate security issues immediately
