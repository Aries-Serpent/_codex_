# Internal Tools API (Codex ↔ Copilot Bridge)

The Internal Tools API (ITA) is a FastAPI application that gives both ChatGPT-Codex and GitHub Copilot a common, audited set of
backend capabilities. The service implements the contract defined in [`openapi.yaml`](openapi.yaml) and adds lightweight safety
guards such as request tracing, API key enforcement, idempotency toggles, and confirmation gates for destructive operations.

## Features

- **Contract-first**: the application adheres to the OpenAPI contract and ships a regression test that keeps the implementation
  in sync.
- **Agent-friendly**: every endpoint supports request tracing via `X-Request-Id` and can operate in `dry_run` mode.
- **Secure by default**: API keys are required, and destructive write operations use `confirm=true` semantics.
- **Operator ergonomics**: a helper script issues short-lived API keys and stores their hashes outside version control.

## Quickstart

```bash
cd services/ita
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .

# Issue a short-lived key (stored under runtime/api_keys.json) and export it for the server/client session
export ITA_API_KEY=$(python scripts/issue_api_key.py)

# Optionally expose a specific path for keys shared across shells
# export ITA_API_KEYS_PATH=$PWD/runtime/api_keys.json

# Launch the service
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
# Sanity check
curl -H "X-API-Key: $ITA_API_KEY" -H "X-Request-Id: demo" http://localhost:8080/healthz
```

## Development

- Run the unit tests with `pytest` or `nox -s tests` from the repository root.
- Keep the [`openapi.yaml`](openapi.yaml) document in sync with new or changed endpoints. The contract test will fail if a path
  is missing.
- Use the codified request/response models in `app.models` to extend the API safely.

## Directory Layout

```
services/ita/
├── app/                # FastAPI application, routers, models, and security helpers
├── openapi.yaml        # Contract shared across Codex, Copilot, and future MCP integrations
├── runtime/            # Local-only storage for hashed API keys (ignored by git)
├── scripts/            # Operational helpers (e.g., issuing API keys)
└── tests/              # Regression and contract tests
```
