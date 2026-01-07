# Guide: Zendesk App Builder (AI Builder) — Key Limitations and Codex Mitigations
> Generated: 2025-10-31 16:17:26 | Author: mbaetiong

 Roles: [Primary] Educator, [Secondary] Navigator   Energy: 5/5 

This guide distills the core limitations when building with Zendesk App Builder’s AI agent variant and maps each to recommended mitigations using the Codex codebase. It extends the Zendesk App Builder: Complete Known Limitations Outline with AI-specific considerations.

## 1) High-level summary (AI Builder vs classic App Builder)

| Area | Classic App Builder Limitation | AI Builder “Agent” Specifics | Why This Matters |
|---|---|---|---|
| Runtime | Client-side only, no custom backend | AI agent orchestration still constrained to front-end context and Zendesk proxies | Server logic must live outside; use an integration tier (e.g., Codex services/ITA) |
| APIs | Proxying via Zendesk; rate limits | Model/tool calls must respect platform quotas; long chains can hit limits | Plan idempotent, cached, rate-limited operations |
| UI Surface | Tight spaces (Sidebar/Topbar); no fullscreen | Conversational UIs need focused, chunked interactions; limited persistent state | Break tasks into tool-backed steps; avoid long, multi-modal render |
| Data | No first-party DB; scoped to agent permissions | AI agent context limited; no long-term memory by default | Externalize session memory/notes via secure service if needed |
| Realtime | No WebSockets/SSE | LLM responses are request/response; streaming often unavailable | Provide progress tokens via backend and periodic polling |
| Security | CSP, credential storage, PII handling | Prompt injection and data leakage risks increase | Tool boundaries, allowlists, and prompt hardening are essential |

## 2) Location constraints for AI agent UIs

| Location | UI Constraints | AI-Specific Impact | Recommendation |
|---|---|---|---|
| Ticket Sidebar | ~300–500px width, single column, scrolling | Long agent–LLM threads and rich evidence don’t fit well | Use concise turns; link out to evidence; keep actions atomic |
| Topbar | Small, transient popover | Conversations can be lost on blur | Avoid multi-step flows here; use for quick lookups only |
| Navbar | Wider but chrome persists; less ticket context | Good for dashboards, configuration, multi-step admin tasks | Prefer Navbar for admin/ops assistants and batch tools |

## 3) AI Builder agent: common limitations and mitigations

| Limitation | Impact | Codex-oriented Mitigation | Owner |
|---|---|---|---|
| No server-side execution | Complex logic cannot run in-app | Route all “tools” to a single Internal Tools API (services/ita) and fan-out from there | Platform Eng |
| Proxy-only external calls | Some APIs need IP allowlists/CORS alignment | Whitelist Zendesk proxy IPs; have ITA call target systems; centralize secrets | Platform Eng / Sec |
| Rate limits (Zendesk + external) | Tool chains can exceed quotas | Implement retry with backoff, budget accounting, and dedupe in ITA; cache reads | Platform Eng |
| Ephemeral agent state | Lost context across steps | Persist minimal session context server-side keyed by conversation/session IDs | Platform Eng |
| No real-time push | UX stalls on long jobs | ITA runs async jobs; agent polls status endpoints; show “job-ids” and progress | Platform Eng |
| OAuth/token handling | Can’t store secrets client-side | ITA holds tokens; short-lived credentials; rotate via vault | Sec / Platform Eng |
| Prompt injection | Risky tool execution | Strict tool allowlists, argument schemas, server-side validation, safety checks | App Team / Sec |
| Determinism | Non-deterministic outputs | Constrain with tool-first design, few-shot prompts, server assertions; record evidence | App Team |
| Large outputs | UI clipping, timeouts | Store artifacts in object store and return links; pagination | Platform Eng |
| PII/compliance | Data handling risk | Redact in transit; minimize scope; log to evidence store with access control | Sec / Compliance |

## 4) Tooling contract for AI agent (recommended)

Define a small set of high-value, safe tools the AI agent can call. Back each with ITA endpoints that implement validation, retries, and evidence logging.

| Tool Name | Purpose | ITA Endpoint (example) | Notes |
|---|---|---|---|
| zendesk.diff | Compute diff between desired/current resource JSON | POST /zendesk/diff | Idempotent; size caps; returns operations summary |
| zendesk.plan | Normalize diff to executable plan | POST /zendesk/plan | Pure function; version the planner |
| zendesk.apply | Execute plan with dry-run support | POST /zendesk/apply | Writes JSONL evidence; returns apply receipt |
| zendesk.snapshot | Export current config | GET /zendesk/snapshot?resource=... | Paginates and caches |
| docs.catalog | Get local doc references | GET /docs/zendesk/catalog | Powered by offline docs snapshots |
| ops.metrics | Expose counters/histograms | GET /ops/metrics?namespace=zendesk | Surfaces `zendesk_*` instruments |

Design rules:
- One tool → one deterministic endpoint.
- Strict JSON schemas; reject unknown fields.
- Return compact payloads plus optional evidence URIs.

## 5) Prompt and UX patterns for the AI agent

| Pattern | Rationale | Example |
|---|---|---|
| Tool-first intent | Reduce hallucination, encourage structured actions | “If change is requested, call zendesk.diff → zendesk.plan → zendesk.apply(dry_run=true)” |
| Chunked context | Avoid long messages in Sidebar; keep latency predictable | “Summarize changes in ≤8 bullets; attach evidence link” |
| Strict function args | Protect from prompt injection | “Only accept resource ∈ {triggers, views, …}. Reject otherwise.” |
| Idempotent retries | Handle transient failures | Client retries on 429/5xx; ITA dedupes via request-id |
| Evidence-by-link | Don’t render large JSON in UI | Return `evidence_uri` pointing to artifact store |
| Guardrails | Refuse unsafe operations | “If plan includes delete of >N items, require human confirm” |

## 6) Evidence, metrics, and governance

| Artifact | Where | Purpose | Access |
|---|---|---|---|
| Evidence JSONL | .codex/evidence/ (or ITA store) | Immutable trail of dry-run/apply | Restricted |
| Metrics | `zendesk_api_calls_total`, `zendesk_apply_*`, `zendesk_diff_operations`, `zendesk_rate_limit_retries_total` | SLOs, throttling visibility | Read-only to ops |
| Snapshots | snapshot/<env>/<ts> | Rollback anchor, review | Read-mostly |
| Docs cache | docs/vendors/zendesk/YYYY-MM-DD | Reference parity, air‑gapped review | Public to team |

## 7) Risk matrix (AI agent-specific)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Rate-limit cascades during apply | Medium | High | Budget operations; preflight; staged apply with checkpoints |
| Prompt injection triggers privileged tool | Medium | High | Tool gating, server validation, refuse-by-default, least privilege |
| Evidence leak in UI | Low | High | Never inline secrets; link to protected artifacts; redact |
| Long-running job timeouts | Medium | Medium | Async jobs; progress polling; resumable apply |
| Schema drift with Zendesk API | Medium | Medium | Routine docs snapshot; compatibility tests; canary env |

## 8) Minimal SLA targets (internal)

| Metric | Target |
|---|---|
| Apply success ratio | ≥ 99% per plan |
| Rate-limit retries per run | ≤ 3 median |
| Time-to-diff | ≤ 3s for typical payloads |
| Time-to-apply (N<100 ops) | ≤ 60s P95 |
| Evidence availability | 100% within 1 min of run |

## 9) Next steps

| Task | Owner | Due |
|---|---|---|
| Define AI tools spec and JSON schemas | App Team |  |
| Stand up ITA endpoints (diff/plan/apply/snapshot) | Platform Eng |  |
| Wire metrics to dashboard | Ops |  |
| Add redaction layer + evidence store | Sec / Platform Eng |  |
| Create Sidebar UX for small-step flows | App Team |  |
| Draft QA plan for rate limits and rollback | QA |  |
