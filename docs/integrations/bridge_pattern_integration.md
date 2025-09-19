Got it—here’s a clean, **bridge-pattern blueprint** that lets **Codex** and **Copilot** “co-op” by hitting the **same internal tools** (HTTP services), plus a **drop-in Codex task prompt** you can paste into a Codex run. I’m grounding every design choice in current docs so it’s production-sane.

---

# Bridge Pattern: Codex ↔ (shared tools) ↔ Copilot

## 1) High-level architecture

* **Internal Tools API (ITA)**: your HTTP service(s) that expose org knowledge & actions (e.g., search KB, repo hygiene, test/lint, PR ops). This is the **single source of truth** both agents call.
* **Codex side**: call ITA via **OpenAI tool calling** (Responses API / Agents SDK). Keep stable schemas; stream; backoff; rate-limit. ([OpenAI Platform][1])
* **Copilot side** (two official paths):

  1. **Copilot Extensions**: build a Copilot “agent” backed by a **GitHub App** + your hosted service; Copilot Chat users invoke tools that call your ITA. ([GitHub Docs][2])
  2. **MCP (Model Context Protocol)**: ship an **MCP server** that exposes tools mapping 1:1 to your ITA. Register it in VS Code / Visual Studio so Copilot can call those tools. Note current constraints (e.g., Copilot coding agent supports **tools only**, not MCP “resources/prompts”; **no remote MCP servers that use OAuth**). Design auth accordingly (non-OAuth secrets or app-issued tokens). ([GitHub Docs][3])

**Why GitHub App over OAuth?** Fine-grained permissions, repo-scoped access, short-lived tokens → least privilege by default. Use OAuth only where you truly need user-scoped access. ([GitHub Docs][4])

---

## 2) Internal Tools API (ITA): contract & guardrails

* **Contract first**: publish an **OpenAPI** spec for endpoints like:

  * `POST /kb/search` → RAG search over internal docs
  * `POST /repo/hygiene` → lint/format/secret-scan a diff
  * `POST /tests/run` → run focused tests; return JUnit summary
  * `POST /git/create-pr` → create/update PR with labels/checklists
  * `GET /catalog/tools` → tool discovery for agents
* **Operational gates**:

  * **Idempotency keys** and **dry-run** mode for destructive ops.
  * **Safety confirmations** (e.g., “requires ‘confirm=true’” for `git/create-pr`).
  * **Rate limits + backoff headers** (mirror OpenAI’s retry discipline).
* **Auth**:

  * Server-to-server: **GitHub App** installation tokens for repo actions. ([GitHub Docs][4])
  * From Copilot (MCP): avoid OAuth (per constraint); issue **short-lived API keys** bound to org & repo. ([GitHub Docs][5])
* **Observability**: correlation IDs, structured logs, per-tool metrics & audit events.

---

## 3) Codex → ITA: tool calling patterns

* Use **OpenAI Responses API / Agents SDK tools** to describe each ITA endpoint (JSON Schema params; narrow, well-typed). Favor few, composable tools over mega-tools. ([OpenAI Platform][1])
* **Streaming** + **exponential backoff with jitter**; cap concurrency with a semaphore; raise `max_output_tokens` only when needed. (Same wrapper you’re already using.)
* **Structured outputs** (JSON Schema) for deterministic downstream handling when the model returns summaries/plans before calling tools. (Azure doc also frames structured outputs clearly.) ([Microsoft Learn][6])

---

## 4) Copilot → ITA, two supported routes

### A) Copilot Extensions (GitHub-native)

* **Create Extension & GitHub App**; host your agent service; map chat intents (slash commands or natural queries) to **the exact ITA endpoints** above. ([GitHub Docs][2])
* **Permissions**: grant the App the minimum repo scopes required (e.g., `contents:read`, `pull_requests:write` if you open PRs).
* **Dev loop**: GitHub provides an **extension debug CLI** to build/test from terminal. ([GitHub][7])

### B) MCP server (VS Code / Visual Studio)

* Implement tools mirroring ITA endpoints; **don’t rely on OAuth** (not supported for remote MCP). Use your short-lived API keys. ([GitHub Docs][5])
* Register via `mcp.json` (workspace or user). VS Code & Visual Studio docs cover configuration. ([Visual Studio Code][8])
* **Copilot coding agent limitations**: “tools only” (no MCP resources/prompts). Plan UI affordances accordingly. ([GitHub Docs][5])

---

## 5) Governance & safety

* **Human-in-the-loop**: destructive endpoints require explicit confirmation tokens; Copilot Extension should summarize intent & show a diff before calling ITA “write” actions.
* **Data boundaries**: ITA enforces repo/org allowlists; redact secrets from logs; attach user identity (from Copilot or IDE) to each call for audit.
* **Network**: Copilot endpoints & IDEs must reach your ITA; if your org firewalls Copilot, follow allowlist guidance. ([GitHub Docs][9])

---

## 6) Acceptance tests (minimum)

1. **Read-only flow** (both agents): `/kb/search` returns top-k with citations; latency < X ms P95.
2. **Repo-write flow** (both agents): propose PR → human confirm → `git/create-pr` opens PR with labels; PR body includes provenance (“via Codex” / “via Copilot”).
3. **Safety**: attempt disallowed repo; expect 403 + guidance.
4. **Resilience**: kill ITA mid-call; both agents retry per policy; surface user-safe error.

---

# Drop-in **Codex Task Prompt** (paste into a Codex session)

> Objective
> Implement a **bridge-pattern “Codex & Copilot co-op”** so both agents call the **same Internal Tools API (ITA)**. Deliver a working skeleton with contracts, clients, configs, and tests.
>
> Constraints
> 1) Use **Copilot Extensions** or **MCP** for Copilot; no direct Copilot inference API.  
> 2) If using MCP: coding agent supports tools only; no remote OAuth; use short-lived keys.  
> 3) Use a **GitHub App** for repo ops, not OAuth where possible.  
> 4) Codex calls ITA via **OpenAI tool calling**.
>
> Deliverables
> - `openapi.yaml`, ITA service with tests, Codex tool wrapper, either Copilot Extension or MCP server + `mcp.json`, and a README.
>
> Exit criteria
> - Both agents can: (1) fetch KB answers; (2) dry-run a PR; (3) open a PR only with confirm=true; with auditable logs.

References
- OpenAI Agents/Responses (tool calling). ([OpenAI Platform][1])
- Copilot Extensions. ([GitHub Docs][2])
- MCP with Copilot. ([GitHub Docs][3])
- GitHub App vs OAuth. ([GitHub Docs][4])
- Structured outputs. ([Microsoft Learn][6])
- MCP config in VS Code. ([VS Code][8])
- Copilot network allowlist. ([GitHub Docs][9])

[1]: https://platform.openai.com/docs/guides/agents-sdk?utm_source=chatgpt.com
[2]: https://docs.github.com/en/copilot/how-tos/use-copilot-extensions?utm_source=chatgpt.com
[3]: https://docs.github.com/en/copilot/concepts/about-mcp?utm_source=chatgpt.com
[4]: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps?utm_source=chatgpt.com
[5]: https://docs.github.com/en/copilot/concepts/coding-agent/mcp-and-coding-agent?utm_source=chatgpt.com
[6]: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/structured-outputs?utm_source=chatgpt.com
[7]: https://github.com/features/copilot/extensions?utm_source=chatgpt.com
[8]: https://code.visualstudio.com/docs/copilot/customization/mcp-servers?utm_source=chatgpt.com
[9]: https://docs.github.com/en/copilot/responsible-use/copilot-in-the-cli?utm_source=chatgpt.com
