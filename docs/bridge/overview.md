# Internal Tools API Bridge Overview

The **Codex ↔ Copilot bridge** gives every automation surface—ChatGPT-Codex, GitHub Copilot, and
future MCP agents—a single, auditable backend. The Internal Tools API (ITA) concentrates every
privileged action behind a contract-first FastAPI service so that new clients only need to bring
authentication and request routing.

## Why a bridge?

| Challenge | Bridge answer |
| --- | --- |
| Codex and Copilot historically called independent scripts with diverging guardrails. | Ship one API that owns the safety gates and operational semantics. |
| Platform parity was difficult: new tools had to be re-implemented twice. | Clients talk to ITA, so features land once and become available everywhere. |
| Governance required manual reviews of bespoke scripts. | The contract, tests, and docs in this repository provide a repeatable baseline. |

## Core components

The bridge is split into small, purpose-built packages. Each client can be deployed on Ubuntu
workstations or CI runners without bespoke setup beyond the documented dependencies.

| Path | Purpose |
| --- | --- |
| `services/ita` | FastAPI application that implements the OpenAPI contract. Includes an API key store, request tracing, idempotent write flows, and contract tests. |
| `agents/codex_client` | Python client consumed by Codex CLI tooling. Handles retries, validation, and streaming-friendly JSON payloads. |
| `copilot/extension` | Express shim for GitHub Copilot extensions. It forwards `/ext/*` calls to ITA with the correct headers and logging. |
| `copilot/app` | Documentation for the GitHub App scopes and environment variables required for write access. |
| `mcp/server` | Placeholder Model Context Protocol server that will expose the same tools to IDE-integrated Copilot agents. |
| `ops/threat_model` | STRIDE snapshot that enumerates the shared trust assumptions and mitigations. |
| `tools/codex_safety` | Optional hooks that keep large binaries and oversized diffs from slipping into pull requests. |

## Request flow

1. A client (Codex CLI, Copilot extension, or MCP server) issues a call with `X-API-Key` and
   `X-Request-Id` headers.
2. The ITA middleware authenticates the API key, stores the hashed key in the request context, and
   injects the correlation ID into the response headers.
3. Router functions fan out to purpose-specific helpers:
   - `/kb/search` → in-memory knowledge snippets that reference onboarding docs.
   - `/repo/hygiene` → static lint/format/secret heuristics.
   - `/tests/run` → synthetic execution harness simulating deterministic and flaky runs.
   - `/git/create-pr` → guarded pull-request simulation that honours `confirm`/`dry_run` semantics.
4. Clients present the responses back to users or upstream automations.

The end-to-end interaction works the same on Ubuntu developer machines, self-hosted runners, and
CI containers because every component only requires standard tooling (`python`, `node`, `uvicorn`,
`npm`).

## Getting started

1. Follow the [Ubuntu CLI integration guide](ubuntu_cli.md) to install Python and Node tooling and
   export the required environment variables.
2. Launch the ITA locally with `uvicorn app.main:app --reload` from `services/ita`.
3. Run the Codex demo client (`python -m codex_client.demo_plan_and_call`) to see a complete plan.
4. Start the Copilot extension shim (`npm start` inside `copilot/extension`) to expose `/ext/*`
   routes.

Every change to the contract should be reflected in `services/ita/openapi.yaml` and validated by the
contract tests under `services/ita/tests`. Clients intentionally depend on the generated schema so
that breaking changes surface quickly during development.

