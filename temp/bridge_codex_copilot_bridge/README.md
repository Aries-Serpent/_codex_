
# Bridge: Codex ↔ Copilot Co-op (Shared Internal Tools API)

This repository provides a production-ready **bridge pattern** so **ChatGPT-Codex** and **GitHub Copilot** both call the **same Internal Tools API (ITA)**. It includes:

- **services/ita** — Minimal Internal Tools API (FastAPI) with contract-first `openapi.yaml`, idempotency, `dry_run`, and `confirm` gates.
- **agents/codex_client** — Codex tool-calling client (OpenAI Responses API), streaming + backoff + concurrency guard.
- **copilot/extension** — Starter for a GitHub Copilot **Extension** (GitHub App + service) that forwards chat intents to ITA.
- **mcp/server** — A future-ready **MCP** server skeleton exposing the same tools (no OAuth), for VS Code/Visual Studio Copilot integration.
- **ops/** — Policy/observability/threat-model stubs for governance.
- **tools/codex_safety** — Optional: safety hooks, ignore/attributes patterns to avoid giant diffs.

> Non-goals: There is **no public Copilot inference API**; neither Codex nor ITA call Copilot. Both agents call **this** API.

## Quickstart

### 1) Run the ITA (Internal Tools API)
```bash
cd services/ita
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
export ITA_API_KEY=$(python scripts/issue_api_key.py)
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
# health check: curl http://localhost:8080/healthz
```

### 2) Try the Codex client demo
```bash
cd agents/codex_client
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
export OPENAI_API_KEY=YOUR_KEY
export ITA_URL=http://localhost:8080
export ITA_API_KEY=THE_KEY_YOU_GENERATED
python -m codex_client.demo_plan_and_call
```

### 3) Run the Copilot Extension shim (forwards to ITA)
```bash
cd copilot/extension
npm install
export ITA_URL=http://localhost:8080
export ITA_API_KEY=THE_KEY_YOU_GENERATED
npm start
# POST from Copilot Extension would hit /ext/* which forwards to ITA
```

### 4) MCP (future) — placeholder server
See `mcp/server/README.md` and `mcp/mcp.json` for wiring.
