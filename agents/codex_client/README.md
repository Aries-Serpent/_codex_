# Codex Client (Bridge Agent)

This package provides a small orchestration layer for ChatGPT-Codex agents that need to interact with the Internal Tools API
(ITA). It wraps HTTP access with retry/backoff behaviour, exposes structured request models, and offers a demo command that
illustrates the end-to-end flow described in the bridge README.

## Installation

```bash
cd agents/codex_client
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```
## Usage

1. Export the ITA connection information:
   ```bash
   export ITA_URL=http://localhost:8080
   export ITA_API_KEY=... # issued by services/ita/scripts/issue_api_key.py
   export OPENAI_API_KEY=... # optional, only required when using OpenAI tool-calling in the demo
   ```
2. Run the demo driver:
   ```bash
   python -m codex_client.demo_plan_and_call --query "Search bridge docs" --run-tests tests/unit
# Append --confirm to perform a non-simulated PR call
   ```
The demo script performs the following steps:

- Queries the `/kb/search` endpoint for relevant snippets.
- Invokes `/repo/hygiene` with a synthetic diff to demonstrate guardrails.
- Executes `/tests/run` for the provided targets.
- Prints a report summarizing the simulated actions.

## Code Map

``` text
codex_client/
├── bridge.py          # HTTP client with retry/backoff and response validation
├── config.py          # Environment-driven configuration helpers
├── demo_plan_and_call.py  # Runnable script showing how a Codex agent would orchestrate calls
└── models.py          # Pydantic models shared between client components
```
The package is intentionally lightweight so it can be embedded directly into Codex function-calling scaffolds or invoked as a
CLI helper within existing workflows.
