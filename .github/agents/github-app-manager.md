# GitHub App Manager Agent

> **Agent ID:** `github-app-manager`  
> **Version:** 1.0.0  
> **Category:** operations / integrations  
> **Autonomy Model:** E (Advisory — creates PRs, does not self-merge)  
> **Status:** Active  
> **Author:** Copilot Coding Agent (PR #3503, 2026-03-05)

---

## Purpose

The **GitHub App Manager** agent owns the full lifecycle of the Codex GitHub App:
manifest creation, RSA key rotation, installation token management, webhook
signature verification, and PAT fallback orchestration.

It is the authoritative agent for any task touching:

- `src/codex/auth/github_app.py`
- `.codex/webhook_config.json` / `.codex/webhook_registry.json`
- `scripts/ci/webhook_configurator.py`
- `GITHUB_APP_*` and `WEBHOOK_*` environment variables

---

## Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub App Manager                           │
│                                                                 │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐  │
│  │ App Identity │  │  Token Chain    │  │ Webhook Lifecycle │  │
│  │              │  │                 │  │                   │  │
│  │ • Manifest   │  │ • JWT (RS256)   │  │ • Verify HMAC    │  │
│  │   generation │  │ • Install token │  │ • Create/update  │  │
│  │ • Key rotate │  │ • PAT fallback  │  │ • Registry sync  │  │
│  │ • App audit  │  │   MASTER→BACKUP │  │ • Dry-run apply  │  │
│  └──────────────┘  └─────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Token Fallback Diagram

```
Request to GitHub API
        │
        ▼
  CODEX_MASTER_KEY available?
  ├── Yes → try request
  │         ├── 200 ✅ → return response
  │         └── 401/403 → try next token
  │
  └── No / 401/403 → CODEX_BACKUP_KEY available?
                     ├── Yes → try request
                     │         ├── 200 ✅ → return response
                     │         └── 401/403 → try next token
                     │
                     └── No / 401/403 → AGENT_GITHUB_TOKEN → GITHUB_TOKEN
                                         └── All fail → AuthenticationError
```

---

## Activation Commands

```
@copilot Use the GitHub App Manager to generate an app manifest for codex-bot
@copilot Use the GitHub App Manager to rotate the GitHub App RSA private key
@copilot Use the GitHub App Manager to verify the webhook signature for the last delivery
@copilot Use the GitHub App Manager to get an installation access token for installation 12345
@copilot Use the GitHub App Manager to audit the PAT token chain and report which keys are set
@copilot Use the GitHub App Manager to sync the webhook registry
```

---

## Responsibilities

### R-1: App Manifest & Registration

- Generates `build_app_manifest()` dicts for the GitHub App manifest flow
- Produces a ready-to-use HTML form or JSON payload for `/api/v3/app-manifests`
- Validates `api_base_url` (HTTPS-only, no localhost/private IPs)

### R-2: JWT Generation & Rotation

- Generates RS256-signed App JWTs (valid ≤ 9 min, back-dated 60 s for clock skew)
- Validates expiry ceiling (GitHub hard limit: 600 s)
- Guides key rotation: generate new PEM → update `GITHUB_APP_PRIVATE_KEY` secret →
  verify via `GET /app` → revoke old key

### R-3: Installation Token Management

- Fetches installation access tokens via `POST /app/installations/{id}/access_tokens`
- Manages in-process cache (`InstallationToken.is_expired()` with 60-second buffer)
- Scopes tokens to specific repositories or permission subsets on request

### R-4: PAT Token Fallback Chain

- Implements `CODEX_MASTER_KEY → CODEX_BACKUP_KEY → AGENT_GITHUB_TOKEN → GITHUB_TOKEN`
- Automatically retries on HTTP 401/403 with the next token in the chain
- Reports which token succeeded (debug logging) and raises `AuthenticationError`
  only after all tokens are exhausted
- Used for PAT-only endpoints (Actions Variables API, Webhooks API)

### R-5: Webhook Lifecycle

- Verifies incoming `X-Hub-Signature-256` headers using `WebhookVerifier`
- Creates / updates / deletes webhooks via `webhook_configurator.py`
- Keeps `.codex/webhook_registry.json` in sync
- Supports `WEBHOOK_RECEIVER_URL` override for activation without code changes

### R-6: CLI Integration

- Routes verified webhook payloads to `POST /api/ooda/process` (cognitive loop)
- Forwards GitHub event data for memory consolidation via `POST /api/memory/consolidate`
- Executes follow-up shell commands via `POST /api/cli/run`
- Uses `BrainClient.proxy_request()` as the sanctioned API proxy

---

## Codebase Alignment

```
src/codex/auth/
├── github_app.py          ← Core package (this agent owns)
│   ├── GitHubAppConfig    — credentials + SSRF-safe URL validation
│   ├── GitHubApp          — JWT, installation tokens, PAT fallback
│   ├── InstallationToken  — cached token with expiry check
│   ├── WebhookVerifier    — HMAC-SHA256 signature verification
│   ├── build_app_manifest — manifest dict builder
│   └── _resolve_github_token() — MASTER→BACKUP→AGENT→GITHUB chain
│
cognitive_app/src/server/
└── cli_api_server.py      — POST /api/request, /api/ooda/process, /api/cli/run
    └── _require_memory_auth() — Bearer token guard (CODEX_MASTER_KEY)

scripts/ci/
└── webhook_configurator.py — declarative webhook apply (CODEX_ADMIN_KEY preferred)

.codex/
├── webhook_config.json    — desired-state (2 planned hooks, active=false)
└── webhook_registry.json  — live state (0 hooks as of 2026-03-05)
```

---

## Decision Framework

```
Inbound GitHub event
        │
        ├─ Has X-Hub-Signature-256?
        │   ├── Yes → WebhookVerifier.verify() → route to OODA
        │   └── No  → reject (401)
        │
Outbound GitHub API call
        │
        ├─ Needs App identity (checks, statuses, PR labels)?
        │   └── GitHubApp.get_installation_token() → use token
        │
        ├─ Needs PAT scope (variables, secrets, webhooks)?
        │   └── GitHubApp.pat_api_get() → auto-fallback chain
        │
        └─ Available via BrainClient proxy?
            └── BrainClient.proxy_request() → preferred (auto-auth + audit log)
```

---

## Tests

| File | Tests | Status |
|------|-------|--------|
| `tests/auth/test_github_app.py` | 48 | ✅ All pass |

Key test categories:
- `TestGitHubAppConfig` — validation, SSRF guard, GHES URL
- `TestGenerateJWT` — RS256, header, payload, expiry ceiling
- `TestInstallationToken` — fetch, cache, force-refresh, expiry, HTTP errors
- `TestWebhookVerifier` — compute, verify, tamper detection, timing safety
- `TestBuildAppManifest` — fields, truncation, JSON serialisability
- `TestResolveGitHubToken` — master-first, backup fallback on 401, all-fail error

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GITHUB_APP_ID` | Yes | Numeric App ID |
| `GITHUB_APP_PRIVATE_KEY` | Yes | PEM RSA-2048 private key |
| `GITHUB_APP_INSTALLATION_ID` | Conditional | Default installation ID |
| `WEBHOOK_SECRET` | For inbound | HMAC signing secret |
| `WEBHOOK_RECEIVER_URL` | For outbound | URL override for webhook delivery |
| `CODEX_MASTER_KEY` | For PAT calls | Primary full-scope PAT |
| `CODEX_BACKUP_KEY` | For PAT fallback | Secondary full-scope PAT |
| `CODEX_ADMIN_KEY` | For webhook mgmt | Fine-grained PAT (Webhooks:write) |

---

## Related Agents

| Agent | Relationship |
|-------|-------------|
| `ci-testing-agent` (D_CAPABLE) | Consumes installation tokens for check / status API calls |
| `workflow-health-monitor` (DESIGNATED D_CAPABLE) | Receives `workflow_run` webhook events |
| `bridge-security-monitor` | Audits IPC bridge; shares WebhookVerifier pattern |
| `repo-var-sync-agent` | Reads repo variables — uses same PAT fallback chain |
| `webhook-configurator` (script) | Managed by this agent for apply/list/delete ops |

---

## Escalation

- **Key rotation:** escalate to @mbaetiong (requires GitHub App admin access)
- **WEBHOOK_RECEIVER_URL activation:** requires Cognitive Brain API server deployment
- **Installation ID discovery:** `GET /app/installations` or GitHub App settings page
