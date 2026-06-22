# Custom Preview Image Plan

**Last Updated:** 2026-06-22

> **Status:** ✅ Implemented (PR #3503 W-126, 2026-03-05)  
> **Owner:** github-app-manager agent  
> **Related:** `Dockerfile.preview`, `.devcontainer/devcontainer.json`,
> `.github/workflows/build-preview-image.yml`

---

## Objective

Provide a production-ready, GHCR-hosted container image that lets GitHub use
the Cognitive Brain CLI API server for preview environments — covering:

1. **GitHub Codespaces** — one-click dev environment via `.devcontainer/`
2. **GitHub Actions ubuntu-latest-m custom image** — ships pre-warmed Python
   deps for faster Copilot Agent session startup
3. **Local preview / CI smoke-test** — `docker run -p 8765:8765 …`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Dockerfile.preview  (multi-stage)                                  │
│                                                                     │
│  ┌──────────────────┐   ┌──────────────────┐  ┌─────────────────┐ │
│  │  preview-base    │   │    preview       │  │  preview-dev    │ │
│  │  Python 3.12     │──▶│  non-root        │  │  + full tooling │ │
│  │  + build deps    │   │  + health check  │◀─┤  + test suite   │ │
│  │  + pip install   │   │  + EXPOSE 8765   │  │  + ruff/mypy    │ │
│  └──────────────────┘   └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
         │                        │                      │
         ▼                        ▼                      ▼
  CI build cache         GHCR :latest            GHCR :latest-dev
                    ghcr.io/aries-serpent/   ghcr.io/aries-serpent/
                    _codex_/preview:latest   _codex_/preview-dev:latest
```

---

## Build & Push Workflow

File: `.github/workflows/build-preview-image.yml`

| Trigger | Action |
|---------|--------|
| Push to `main` (Dockerfile.preview / src / cognitive_app changed) | Build + push `preview` and `preview-dev` tags |
| Pull request | Build only (no push) + smoke-test |
| `workflow_dispatch` | Manual build with optional tag override |

### Smoke Test

The `preview` target is smoke-tested after every build:

```bash
docker run -d -p 18765:8765 ghcr.io/aries-serpent/_codex_/preview:latest
curl -sf http://localhost:18765/api/health   # must return {"status":"ok"}
```

---

## Image Contents

### `preview` (production)

| Component | Source |
|-----------|--------|
| Python 3.12-slim base | Docker Hub official |
| `uvicorn[standard]` | pyproject.toml |
| `fastapi` | pyproject.toml |
| `httpx` | pyproject.toml |
| `cryptography >= 42` | pyproject.toml — required by `github_app.py` |
| `src/codex/auth/` | Editable install — user auth + GitHub App |
| `cognitive_app/src/server/cli_api_server.py` | FastAPI server on `:8765` |

### `preview-dev` (development / Codespaces)

Everything in `preview`, plus:

- `pytest`, `ruff`, `black`, `mypy`, `ipython`
- `pre-commit`, `detect-secrets`
- Full test suite (`tests/`)
- VS Code extensions wired via `.devcontainer/devcontainer.json`

---

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `CODEX_MASTER_KEY` | For GitHub API | — | Primary PAT |
| `CODEX_BACKUP_KEY` | Fallback | — | Tried on 401/403 |
| `GITHUB_APP_ID` | For App JWT | — | Numeric App ID |
| `GITHUB_APP_PRIVATE_KEY` | For App JWT | — | PEM RSA-2048 |
| `WEBHOOK_SECRET` | For webhooks | — | HMAC secret |
| `CODEX_DB_PATH` | Always | `/home/codex/.codex/codex.db` | SQLite history |
| `CODEX_SESSION_LOG_DIR` | Always | `/home/codex/.codex/sessions` | Session logs |

---

## GitHub Codespaces — Quick Start

1. Open PR / repo on GitHub
2. Click **Code → Codespaces → Create codespace on this branch**
3. Codespaces builds from `.devcontainer/devcontainer.json` (uses `preview-dev` image)
4. Server auto-starts on port 8765 (`postStartCommand`)
5. Verify: `curl -s http://localhost:8765/api/health`

Secrets are mapped via the **Codespaces Secrets** UI (Settings → Codespaces).

---

## Activation Checklist

- [x] `Dockerfile.preview` — multi-stage, non-root, health-checked
- [x] `.devcontainer/devcontainer.json` — Codespaces config with secrets mapping
- [x] `.github/workflows/build-preview-image.yml` — CI build + push + smoke-test
- [x] GHCR package permissions — `packages: write` in workflow
- [ ] **Admin action required:** Enable Codespaces for `Aries-Serpent/_codex_` (org setting)
- [ ] **Admin action required:** Add `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`,
      `CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY`, `WEBHOOK_SECRET` as Codespaces secrets
- [ ] First successful push to `main` to publish `:latest` tags to GHCR

---

## Next Steps (Post-Deployment)

1. Update `copilot-setup-steps.yml` to pull from `ghcr.io/aries-serpent/_codex_/preview:latest`
   instead of installing deps from scratch (saves ~3 min per session)
2. Pin ubuntu-latest-m custom image to the GHCR digest once stable
3. Add Trivy vulnerability scan to the build workflow
