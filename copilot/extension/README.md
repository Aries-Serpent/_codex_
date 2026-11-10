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

## Dependency validation

Use the committed lockfile with a supported Node.js version:

```bash
npm ci
npm ls --all
npm run lint
npm test
```

The Node test runner starts the real shim and a disposable local ITA stub using
synthetic configuration and OS-assigned ports (`PORT=0`); the startup message
reports the actual bound port. Tests cover both forwarding routes, request headers,
upstream errors, body limits and missing-configuration startup failures. No
production ITA service or API key is required.
