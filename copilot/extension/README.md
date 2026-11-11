# Copilot Extension Shim

This folder scaffolds a GitHub Copilot extension service that forwards Copilot Chat intents to the Internal Tools API (ITA). The
service acts as a minimal HTTP bridge so that Copilot can reuse the same backend as ChatGPT-Codex.

## Structure

- `extension_manifest.json` – Conceptual manifest stub describing extension commands.
- `server/index.js` – Express server that forwards extension invocations to the ITA.
- `package.json` – Local development dependencies and scripts.

## Quickstart

```bash
cd copilot/extension
npm install
export ITA_URL=http://localhost:8080
export ITA_API_KEY=... # issued by services/ita/scripts/issue_api_key.py
npm start
```text
Once the server is running, configure the Copilot extension to target the exposed endpoints (default port `3978`). Each incoming
request is validated, logged, and replayed to the ITA with the required headers. Add authentication secrets via environment
variables rather than source control.

> **Note:** Fill in your GitHub App credentials and deploy `server/` to an accessible URL when promoting beyond local testing.

## Regression checks

Run `npm ci`, `npm run lint`, and `npm test` from this directory. The Node
built-in test runner starts the real CommonJS server and an ITA stub on
OS-assigned loopback ports, with synthetic configuration and an isolated working
directory. It checks forwarding, request IDs, error responses, missing
configuration, and the existing 1 MiB JSON limit. No production service or API
key is required. `HOST=127.0.0.1 PORT=0` can also be used for manual local checks;
the startup message reports the actual bound port.
