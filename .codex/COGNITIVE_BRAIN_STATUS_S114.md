# Cognitive Brain Status — Session S114

**Date:** 2026-03-05  
**Session:** S114  
**PR:** #3503 — Add user authentication system + GitHub App package + Codespace config  
**Status:** ✅ Complete  
**Health Score:** 100/100 (AAIS V5.0)  
**Prev Session:** S113 — `COPILOT_AGENT_AUTH_BYPASS_TOOLS` scope filter

---

## What Changed (S114)

### New Components Delivered

| Component | File | Description |
|-----------|------|-------------|
| `User` + `PasswordHasher` + `UserStore` | `src/codex/auth/user_store.py` | User identity, PBKDF2-SHA256 hashing, in-memory CRUD store |
| `Authenticator` + `LoginResult` | `src/codex/auth/authenticator.py` | Full login/logout/MFA/password-change service |
| `GitHubApp` + `GitHubAppConfig` | `src/codex/auth/github_app.py` | RS256 JWT, installation tokens, PAT fallback chain |
| `InstallationToken` | `src/codex/auth/github_app.py` | Cached token with 60-second expiry buffer |
| `WebhookVerifier` | `src/codex/auth/github_app.py` | HMAC-SHA256 `X-Hub-Signature-256` verifier |
| `build_app_manifest()` | `src/codex/auth/github_app.py` | GitHub App manifest dict builder |
| `_resolve_github_token()` | `src/codex/auth/github_app.py` | MASTER→BACKUP→AGENT→GITHUB PAT fallback chain |
| `pat_api_get()` | `src/codex/auth/github_app.py` | PAT-authenticated GET with auto-retry on 401/403 |
| github-app-manager agent | `.github/agents/github-app-manager.md` | New production Copilot agent |
| Codespace devcontainer | `.devcontainer/devcontainer.json` | Full Copilot-agent Codespace config |
| Lifecycle scripts (×5) | `.devcontainer/scripts/` | on-create, update-content, post-create, post-start, post-attach |
| Preview Dockerfile | `Dockerfile.preview` | Multi-stage: preview / preview-dev targets |
| Build workflow | `.github/workflows/build-preview-image.yml` | GHCR push + smoke-test |
| Documentation (×4) | `docs/agent/` + `docs/plans/` | GITHUB_APP_CLI_MAPPING, CODESPACE_COPILOT_AGENT_GUIDE, custom-preview-image |
| Test suite | `tests/auth/` | 111 tests across user_store, authenticator, github_app |

### Token Fallback Chain (new capability)

```
GitHub API call
      │
      ▼  Try 1
CODEX_MASTER_KEY ──→ 200 OK ✅
      │ 401/403
      ▼  Try 2
CODEX_BACKUP_KEY ──→ 200 OK ✅
      │ 401/403
      ▼  Try 3
AGENT_GITHUB_TOKEN → 200 OK ✅
      │ 401/403
      ▼  Try 4
GITHUB_TOKEN ──────→ 200 OK ✅
      │ 401/403
      ▼
AuthenticationError("All PAT tokens exhausted")
```

### Codespace ↔ Actions Parity (new)

Every phase of `copilot-setup-steps.yml` now has a Codespace equivalent:

| Actions Phase | Codespace Script | Runs When |
|---------------|-----------------|-----------|
| Phase 1+2 (system) | `on-create.sh` | Container created (once) |
| Phase 3+4 (pip/node/rust) | `update-content.sh` | Each rebuild / branch switch |
| Phase 5+6 (env + auth) | `post-create.sh` | After first update-content |
| Phase 7 (CLI server) | `post-start.sh` | Every container start |
| (banner) | `post-attach.sh` | Every terminal attach |

### Test Coverage

| File | Tests | Status |
|------|-------|--------|
| `tests/auth/test_user_store.py` | 34 | ✅ All pass |
| `tests/auth/test_authenticator.py` | 25 | ✅ All pass |
| `tests/auth/test_github_app.py` | 52 | ✅ All pass (incl. token-fallback) |
| **Total new** | **111** | ✅ |

---

## Cognitive Brain Mapping Update

### Integration Points (new in S114)

```
Cognitive Brain
├── src/codex/auth/                    ← NEW: full auth package
│   ├── github_app.py                  ← GitHub App integration
│   │   └── pat_api_get()             ← uses MASTER→BACKUP chain
│   ├── authenticator.py               ← login / MFA / sessions
│   └── user_store.py                  ← user identity store
│
├── .devcontainer/                     ← NEW: Codespace config
│   ├── devcontainer.json              ← master config (8 secrets declared)
│   └── scripts/                       ← 5 lifecycle scripts
│       └── post-start.sh             ← starts CLI API :8765
│
├── cognitive_app/src/server/          ← EXISTING (unchanged)
│   └── cli_api_server.py             ← API gateway, receives webhook events
│
└── src/codex/agents/
    └── brain_client.py                ← EXISTING (proxy + same token chain)
```

### Agent Registry Update

New agent added: `github-app-manager` (v1.0.0, production, operations/integrations)

```yaml
# Addition to AGENT_REGISTRY.yaml
- id: github-app-manager
  name: GitHub App Manager
  version: 1.0.0
  file: github-app-manager.md
  status: active
  maturity: production
  category: operations
  subcategory: integrations
  capability_tags:
    - github_app_jwt
    - installation_tokens
    - webhook_verification
    - pat_token_fallback
    - app_manifest
    - codespace_config
```

---

## Next: S115 — Phase 23 Objectives

See `.codex/cognitive_brain/COGNITIVE_BRAIN_PHASE_23_OBJECTIVES.md`

**Top priorities for S115:**
1. Activate GHCR image build (needs first push to `main`)
2. Configure Codespaces secrets at org level (`CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY`)
3. Coverage gap-fill targeting auth package (target: 90%+)
4. Deploy Cognitive Brain API server to activate webhooks
5. Set `WEBHOOK_RECEIVER_URL` repo variable to activate hooks
