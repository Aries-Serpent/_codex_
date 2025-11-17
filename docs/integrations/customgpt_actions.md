# CustomGPT Actions for `_codex_` (Local, Offline-first)

This integration exposes minimal HTTP endpoints for CustomGPT **Actions** to:
1) list branches, 2) fetch files at a ref, 3) run lightweight search, 4) healthcheck.

## Getting Started
```bash
python3 tools/actions_server.py
# Server at http://localhost:8010
```text
Then load `actions/openapi.yaml` into your CustomGPT Action configuration.

### Security
- Provide `CODEX_GITHUB_TOKEN` (classic or fine-grained) for higher rate limits.
- Do not commit secrets; optionally use `.env` (see `.env.example`).

### Notes
- Local only; no CI runners required.
- Caching window ~60s avoids rate spikes during interactive sessions.
