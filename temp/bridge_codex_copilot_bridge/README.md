# Bridge Pattern Skeleton — Codex ↔ Copilot via Internal Tools API (ITA)
> Scope: Minimal, non-invasive scaffold placed under temp/bridge_codex_copilot_bridge  
> Constraints: no dep pin changes, no network in tests, reuse tools/codex_safety/openai_wrapper.py

Layout
``` text
temp/bridge_codex_copilot_bridge/
├─ services/ita/
│  ├─ openapi.yaml
│  └─ app/
│     └─ main.py
├─ agents/codex_client/
│  ├─ toolspecs/
│  │  ├─ kb_search.json
│  │  ├─ repo_hygiene.json
│  │  ├─ tests_run.json
│  │  └─ git_create_pr.json
│  └─ client/
│     └─ openai_tools.py
├─ mcp/
│  ├─ server/
│  │  └─ main.py
│  └─ examples/
│     └─ mcp.json
└─ README.md (this file)
```
Notes
- ITA is a stub FastAPI app exposing 4 endpoints with deterministic responses for local smoke tests.
- Tool specs mirror the ITA contract (JSON Schema params) to be consumable by tool-calling LLMs.
- MCP is optional and intentionally minimal here; wire-up can be done later in an IDE context.
- Client calls should use tools/codex_safety/openai_wrapper.py for streaming/backoff if you build demos.
