# GitHub App Design-Pattern Gap Analysis

**Last Updated:** 2026-06-22

**Produced by:** copilot-swe-agent (W-098d, PR #3494)
**Date:** 2026-03-04
**Reference:** [About creating GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps)

---

## Summary

The GitHub documentation defines four GitHub App design patterns. This document
maps each pattern to the current implementation state in this repository and
identifies what is complete vs. what remains to be done.

| Pattern | Code Layer | Operational Layer | Overall |
|---------|-----------|-------------------|---------|
| 1. Act on behalf of a user (user-to-server) | ✅ Complete | ⚠️ App not registered | ⚠️ Partial |
| 2. Act on its own behalf (server-to-server) | ✅ Complete | ⚠️ App not registered | ⚠️ Partial |
| 3. Respond to webhooks | ✅ Complete | ⚠️ No live receiver URL | ⚠️ Partial |
| 4. Take certain actions (permissions) | ✅ Complete | ⚠️ App not registered | ⚠️ Partial |

**Root cause of all gaps:** The GitHub App has not been registered yet.
Once registered via `scripts/ci/github_app_bootstrap.py`, all four patterns
become operational.

---

## Pattern 1 — Acts on behalf of a user (user access token / user-to-server)

### What it means

The app authenticates with a **user access token** obtained through the OAuth
authorization code flow. The app is limited by both the app's permissions and
the authorizing user's permissions.

### ✅ What is implemented

| File | What it provides |
|------|-----------------|
| `src/codex/auth/oauth_manager.py` | Full OAuth2 authorization-code flow with PKCE support; `OAuthManager.create_github_config()`, `initiate_flow()`, `exchange_code()`, `refresh_token()`, `get_user_info()` |
| `src/codex/auth/token_manager.py` | JWT token lifecycle (issue, validate, rotate, revoke) |
| `src/codex/auth/middleware.py` | FastAPI/Starlette auth middleware (JWT, API key, OAuth methods) |
| `examples/authentication/01_oauth_flow.py` | OAuth flow usage example |
| `examples/authentication/04_complete_flow.py` | Complete auth flow demo (GitHub OAuth + MFA + token management) |
| `tests/auth/test_oauth_flow.py` | OAuth flow tests |

### ⚠️ What is missing

- **GitHub App not registered** — `GITHUB_APP_ID`, `GITHUB_CLIENT_ID`,
  `GITHUB_CLIENT_SECRET` are still placeholder env vars; the App must be
  registered via `scripts/ci/github_app_bootstrap.py --generate-manifest-url`
  before the OAuth callback URL is functional.
- `src/integrations/github_app_auth.py` does not expose a
  `get_user_info_with_user_token()` helper — callers must use `OAuthManager`
  directly.

### Action required

```bash
# Step 1: Admin generates App manifest URL (browser action)
python scripts/ci/github_app_bootstrap.py --generate-manifest-url

# Step 2: Admin completes registration in browser, receives one-time code
# Step 3: Convert code → credentials
python scripts/ci/github_app_bootstrap.py --convert-code <ONE_TIME_CODE>
```

---

## Pattern 2 — Acts on its own behalf (installation access token / server-to-server)

### What it means

The app authenticates with an **installation access token**, exchanged from
a short-lived App JWT (RS256). The app is limited only by its configured
permissions, not by any user's permissions.

### ✅ What is implemented

| File | What it provides |
|------|-----------------|
| `tools/github/app_token.py` | `build_app_jwt()` + `exchange_installation_token()` (stdlib only, no external deps for JWT build) |
| `src/integrations/github_app_auth.py` | `mint_app_jwt()`, `exchange_installation_token()`, `create_runner_registration_token()` |
| `.github/agents/github_app/app.py` | `CodexReviewerApp._generate_jwt()` + `_get_installation_token()` |
| `scripts/ci/github_app_bootstrap.py` | Full App registration bootstrap via Manifest API |
| `tests/github/test_app_token.py` | JWT build + header/payload validation |
| `tests/github/test_app_token_cli.py` | CLI token helper tests |

### ⚠️ What is missing

- **GitHub App not registered** — `GITHUB_APP_ID`, `GITHUB_APP_INSTALLATION_ID`
  are unset. All helper functions will `raise AuthError` / `raise SystemExit`
  until the App is registered and credentials stored in `.codex/github_app/`.
- `GITHUB_APP_INSTALLATION_ID` is not documented in
  `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` — should be added
  alongside `GITHUB_APP_ID`.

---

## Pattern 3 — Responds to webhooks

### What it means

The app subscribes to GitHub events (push, pull_request, issue_comment, etc.)
and receives HTTP POST payloads to a registered URL. Payloads are authenticated
with `X-Hub-Signature-256` (HMAC-SHA256).

### ✅ What is implemented

| File | What it provides |
|------|-----------------|
| `.github/agents/github_app/app.py` | Flask `/webhook` endpoint with `X-Hub-Signature-256` HMAC verification; handles `pull_request`, `pull_request_review`, `issue_comment` events |
| `scripts/ci/webhook_configurator.py` | Declarative webhook CRUD (create, update, delete, list) via REST API; stores state in `.codex/webhook_registry.json`; idempotent |
| `scripts/space_traversal/webhooks.py` | Generic webhook delivery with HMAC signing + retry/backoff |
| `tests/space_traversal/test_webhooks.py` | Webhook delivery tests |

### ⚠️ What is missing

- **No live webhook receiver deployed** — `hook_attributes.url` in
  `APP_MANIFEST` (see `scripts/ci/github_app_bootstrap.py`) defaults to
  `https://placeholder.example.com/github-hook`. A real server (e.g., a Cloud
  Run instance running `CodexReviewerApp`) must be deployed and the URL updated
  via `github_app_bootstrap.py --update-webhook <URL>`.
- **`CODEX_WEBHOOK_SECRET`** must be set after App registration.

### Action required

```bash
# After registering the App:
export WEBHOOK_RECEIVER_URL="https://your-receiver.example.com/github"
python scripts/ci/github_app_bootstrap.py --update-webhook "$WEBHOOK_RECEIVER_URL"

# To programmatically manage webhooks:
python scripts/ci/webhook_configurator.py --apply .codex/webhook_config.json
```

---

## Pattern 4 — Can take certain actions (permissions)

### What it means

When registering the GitHub App, specific permissions are configured (e.g.,
`contents: write`, `pull_requests: write`). These determine what the app can
do via the GitHub API and what webhook events it can receive.

### ✅ What is implemented

| File | What it provides |
|------|-----------------|
| `scripts/ci/github_app_bootstrap.py` | `APP_MANIFEST["default_permissions"]` — `contents: write`, `issues: write`, `pull_requests: write`, `actions: write`, `metadata: read`, `administration: read` |
| `scripts/ci/github_app_bootstrap.py` | `APP_MANIFEST["default_events"]` — `push`, `pull_request`, `issue_comment`, `pull_request_review_comment`, `workflow_run`, `issues`, `check_run` |
| `.github/workflows/*.yml` | Explicit `permissions:` blocks (e.g., `contents: read`, `pull-requests: write`) on all workflows |
| `agent-auth-delegation.yml` | Granular per-job permission scoping |

### ⚠️ What is missing

- **App permissions take effect only after registration.** The manifest is
  defined but not applied.
- `administration: read` in `APP_MANIFEST` may exceed the principle of least
  privilege. This permission allows the App to read repository settings,
  deploy keys, and repository metadata — it does **not** grant write/admin
  access, but it should still be removed if the App only needs to read
  code and post comments. **Audit before registration**: if runner
  registration tokens (`create_runner_registration_token()`) are not
  needed at app level, remove this permission from the manifest.

---

## Overall Gap: GitHub App Registration

All four patterns share a **single root-cause gap**: the GitHub App has not
been registered.

### Registration checklist

- [ ] Admin runs `python scripts/ci/github_app_bootstrap.py --generate-manifest-url`
- [ ] Admin opens generated URL in browser while signed in as org owner
- [ ] Admin authorizes → receives one-time code
- [ ] Admin runs `python scripts/ci/github_app_bootstrap.py --convert-code <CODE>`
- [ ] `.codex/github_app/app_credentials.json` created (app_id, client_id)
- [ ] `.codex/github_app/private_key.pem` created (keep secret, never commit)
- [ ] Repo variables set: `GITHUB_APP_ID`, `GITHUB_APP_INSTALLATION_ID`
- [ ] Secrets set: `GITHUB_APP_PRIVATE_KEY_PEM` (or path), `CODEX_WEBHOOK_SECRET`
- [ ] Webhook receiver deployed and URL registered
- [ ] `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` set for user-to-server OAuth

### Environment variable mapping

| Variable | Pattern | Source |
|----------|---------|--------|
| `GITHUB_APP_ID` | 1, 2, 3, 4 | `app_credentials.json` after registration |
| `GITHUB_APP_INSTALLATION_ID` | 2 | GitHub App → Installations |
| `GITHUB_APP_PRIVATE_KEY_PEM` | 2 | `private_key.pem` after registration (store as secret) |
| `GITHUB_CLIENT_ID` | 1 | `app_credentials.json` after registration |
| `GITHUB_CLIENT_SECRET` | 1 | `app_credentials.json` after registration (store as secret) |
| `CODEX_WEBHOOK_SECRET` | 3 | Set during App registration webhook config |

---

*Last updated: 2026-03-04 (W-098d, PR #3494)*
