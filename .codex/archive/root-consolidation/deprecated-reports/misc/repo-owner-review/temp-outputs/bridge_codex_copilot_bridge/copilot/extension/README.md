
# Copilot Extension (Starter)

This folder scaffolds a **GitHub Copilot Extension** that forwards Copilot Chat intents to the **Internal Tools API (ITA)**.
It assumes you will register a **GitHub App** with the minimum repo permissions needed (read contents, write pull_requests).

## Structure
- `extension_manifest.json` — conceptual manifest stub for commands/tools.
- `server/index.js` — minimal Node service exposing endpoints Copilot calls; it in turn calls ITA.
- `package.json` — deps/scripts.

> NOTE: Fill in your App credentials and deploy `server/` to an accessible URL. Wire the extension to those endpoints per official setup.
