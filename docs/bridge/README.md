# Bridge: Codex ↔ Copilot Co-op (Shared Internal Tools API)

This bridge pattern enables ChatGPT-Codex and GitHub Copilot to call the same Internal Tools API (ITA). The repository includes
shared service code, agent clients, and operational documentation so that both assistants can operate through a unified,
auditable backend.

## Components

- **services/ita** – FastAPI implementation of the Internal Tools API with contract-first OpenAPI definitions, idempotency,
  `dry_run`, and `confirm` gates.
- **agents/codex_client** – Codex-oriented client that wraps the ITA with retries, streaming-ready responses, and concurrency
  guards.
- **copilot/extension** – Starter GitHub Copilot extension shim (GitHub App + service) that forwards chat intents to the ITA.
- **mcp/server** – Future-ready MCP server skeleton exposing the same tools (no OAuth) for VS Code/Visual Studio Copilot
  integration.
- **ops/** – Policy, observability, and threat-model stubs for governance.
- **tools/codex_safety** – Optional safety hooks and ignore/attribute patterns to avoid noisy diffs.

> Non-goals: There is no public Copilot inference API; neither Codex nor the ITA call Copilot. Both agents call this API.

## Quickstart

### 1. Run the ITA (Internal Tools API)

```bash
cd services/ita
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
export ITA_API_KEY=$(python scripts/issue_api_key.py)
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
# health check
curl -H "X-API-Key: $ITA_API_KEY" -H "X-Request-Id: demo" http://localhost:8080/healthz
```

### 2. Try the Codex client demo

```bash
cd agents/codex_client
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
export OPENAI_API_KEY=YOUR_KEY
export ITA_URL=http://localhost:8080
export ITA_API_KEY=$ITA_API_KEY
python -m codex_client.demo_plan_and_call --query "Search bridge docs"
```

### 3. Run the Copilot extension shim (forwards to ITA)

```bash
cd copilot/extension
npm install
export ITA_URL=http://localhost:8080
export ITA_API_KEY=$ITA_API_KEY
npm start
# POST requests from the Copilot extension will hit /ext/* and forward to the ITA
```

### 4. MCP (future) — placeholder server

See `mcp/server/README.md` and `mcp/mcp.json` for wiring guidance.

## Licensing

MIT License © 2025. See `LICENSE` for details.
