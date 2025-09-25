# Ubuntu CLI Integration Guide

This quickstart targets Ubuntu 24.04 LTS (the Codex universal base). It walks through preparing a
developer workstation or self-hosted runner so Codex and Copilot automations can reach the Internal
Tools API (ITA) bridge.

## Prerequisites

- Python 3.12+ (`sudo apt install python3 python3-venv python3-pip`)
- Node.js 20+ (`curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -` then
  `sudo apt install nodejs`)
- GitHub App credentials for Copilot write operations (optional until you enable `/git/create-pr`).

## 1. Launch the ITA service

```bash
cd /workspace/_codex_/services/ita
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
export ITA_API_KEY=$(python scripts/issue_api_key.py)
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```
`uvicorn` logs the request ID for every call. On Ubuntu you can background the process with
`systemd --user` units or `tmux` depending on operator preference.

## 2. Configure the Codex client

```bash
cd /workspace/_codex_/agents/codex_client
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
export ITA_URL=http://localhost:8080
export ITA_API_KEY=$ITA_API_KEY
# Optional when using the OpenAI Responses API demo
export OPENAI_API_KEY=sk-...
python -m codex_client.demo_plan_and_call --query "bridge quickstart" --run-tests tests/unit
```
The demo prints the knowledge base snippets, hygiene scan, optional test run, and PR simulation. All
network requests stay inside the Ubuntu host unless you point `ITA_URL` elsewhere.

## 3. Run the Copilot extension shim

```bash
cd /workspace/_codex_/copilot/extension
npm install
export ITA_URL=http://localhost:8080
export ITA_API_KEY=$ITA_API_KEY
npm start
```
The Express server listens on port `3978`. Configure your Copilot extension manifest or testing tool
to POST to `http://localhost:3978/ext/repo/hygiene` (and `/ext/tests/run`). Requests inherit the ITA
guardrails because the shim copies the headers and never stores credentials on disk.

## 4. Optional GitHub App wiring

When you are ready to perform write operations set the following variables in every shell that calls
the bridge:

```bash
export GITHUB_APP_ID=12345
export GITHUB_INSTALLATION_ID=67890
export GITHUB_PRIVATE_KEY_PEM="$(cat ~/keys/copilot-app.pem)"
```
The ITA will validate the configuration before attempting `/git/create-pr` with `confirm=true`.

## 5. Keep tooling aligned

- Pin dependencies using the provided lock files or `uv` workflow in the repository root.
- Re-run `pytest services/ita/tests` and `npm run lint --prefix copilot/extension` after upgrades.
- Read the [governance guide](governance.md) for policies that apply once you promote beyond a local
  Ubuntu sandbox.

