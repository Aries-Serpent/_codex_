# Cognitive Brain — Phase 23 Objectives

**Generated:** 2026-03-05  
**Session:** S114 (end-of-session handoff)  
**Phase:** 23 — GitHub App Activation & Codespace Deployment  
**Prerequisites:** Phase 22 Complete ✅, S114 Complete ✅  
**Owner:** GitHub Copilot Agents  
**Next Session:** S115

---

## Mission Statement

Activate the GitHub App and Codespace infrastructure introduced in S114, integrate
the new auth package into the Cognitive Brain's OODA loop, and close the remaining
coverage + deployment gaps.

---

## Objective 1: Activate GHCR Preview Image

**Priority:** P1 (Critical Path)  
**Timeline:** 1 iteration  
**Status:** 🔄 Ready — awaiting merge to `main`

### Tasks

1. **Merge PR #3503 to `main`**
   - Triggers `build-preview-image.yml` automatically
   - Pushes `ghcr.io/aries-serpent/_codex_/preview:latest`
   - Pushes `ghcr.io/aries-serpent/_codex_/preview-dev:latest`

2. **Verify GHCR packages are public (or codex-readable)**
   - Settings → Packages → `_codex_/preview` → Package visibility
   - Required for Codespace image pull to work without auth

3. **Update `copilot-setup-steps.yml` to pull from GHCR**
   ```yaml
   # Replace current pip-install-from-scratch with:
   - name: "🐳 Pull pre-baked preview image"
     run: docker pull ghcr.io/aries-serpent/_codex_/preview:latest
   ```
   Expected saving: ~3 min per agent session (current cold install time)

### Success Criteria

- [ ] `ghcr.io/aries-serpent/_codex_/preview:latest` exists and is pullable
- [ ] `docker run … /api/health` returns `{"status":"ok"}`
- [ ] Smoke-test in `build-preview-image.yml` passes

---

## Objective 2: Configure Codespace Secrets

**Priority:** P1  
**Timeline:** 1 admin action  
**Status:** ⏳ Awaiting @mbaetiong

### Tasks (Admin — @mbaetiong)

Set the following secrets at org level:
- **Settings → Codespaces → Secrets → New secret** (org-scoped)

| Secret | How to get |
|--------|-----------|
| `CODEX_MASTER_KEY` | github.com/settings/tokens → Classic PAT, `repo` scope |
| `CODEX_BACKUP_KEY` | Same as above, second token |
| `CODEX_ADMIN_KEY` | Fine-grained PAT, `Webhooks:write` permission |
| `GITHUB_APP_ID` | github.com/settings/apps → App settings page |
| `GITHUB_APP_PRIVATE_KEY` | App settings → Private keys → Generate a private key |
| `GITHUB_APP_INSTALLATION_ID` | `GET /app/installations` with App JWT |
| `WEBHOOK_SECRET` | Generate: `python3 -c "import secrets; print(secrets.token_hex(32))"` |

### Success Criteria

- [ ] `post-create.sh` reports all 7 tokens as ✅ when Codespace starts
- [ ] `pat_api_get()` returns 200 in Codespace terminal

---

## Objective 3: Auth Coverage Gap-Fill

**Priority:** P2  
**Timeline:** 2-3 iterations  
**Status:** 🔄 Not started

Current auth coverage: ~85% (estimated — exact metric pending CI run)

### Files needing additional tests

| File | Current Coverage | Target |
|------|-----------------|--------|
| `src/codex/auth/github_app.py` | ~82% | 90% |
| `src/codex/auth/authenticator.py` | ~88% | 92% |
| `src/codex/auth/user_store.py` | ~91% | 95% |

### Tasks

1. Add tests for `GitHubApp.get_app_info()` and `list_installations()`
2. Add tests for `GitHubApp.pat_api_get()` network error paths
3. Add edge-case tests for `WebhookVerifier` (Unicode payload, very large body)
4. Add tests for `Authenticator.admin_reset_password()` with session revocation
5. Run `nox -s coverage` and enforce 90% threshold for `src/codex/auth/`

### Success Criteria

- [ ] `pytest --cov=src/codex/auth --cov-report=term` reports ≥90%
- [ ] No branch in auth package with 0% coverage

---

## Objective 4: Webhook Activation

**Priority:** P2  
**Timeline:** Post Cognitive Brain API deployment  
**Status:** ⏳ Blocked — waiting for API server deployment

### Blocker

`WEBHOOK_RECEIVER_URL` requires a public HTTPS endpoint. The Cognitive Brain API
server must be deployed (Kubernetes / Render / Railway / etc.) first.

### Tasks (when unblocked)

1. Deploy `ghcr.io/aries-serpent/_codex_/preview:latest` to cloud
2. Set `WEBHOOK_RECEIVER_URL` repo variable to deployed URL
3. Run: `python scripts/ci/webhook_configurator.py --apply`
4. Verify `.codex/webhook_registry.json` shows 2 live hooks
5. Test delivery: `gh api /repos/Aries-Serpent/_codex_/hooks/{id}/test`

### Expected Result

```json
// .codex/webhook_registry.json after activation
{
  "live_hooks": [
    {"name": "cognitive-brain-ci-feedback", "active": true, "id": 12345},
    {"name": "runner-health-notification",  "active": true, "id": 12346}
  ]
}
```

---

## Objective 5: OODA Loop — GitHub Event Integration

**Priority:** P3  
**Timeline:** 3-5 iterations  
**Status:** 🔄 Design phase

Connect verified webhook payloads → Cognitive Brain OODA loop:

```python
# webhook_handler.py (new, Objective 5)
from codex.auth.github_app import WebhookVerifier
from codex.agents.brain_client import BrainClient

verifier = WebhookVerifier(secret=os.environ["WEBHOOK_SECRET"])
brain    = BrainClient()

async def handle_github_event(payload: bytes, signature: str, event_type: str):
    if not verifier.verify(payload, signature):
        raise HTTPException(401)
    event = json.loads(payload)
    return brain.ooda_process(
        input_data={"event": event, "event_type": event_type},
        context={"source": "github_webhook", "session": S114},
    )
```

### Tasks

1. Create `cognitive_app/src/handlers/webhook_handler.py`
2. Register route `POST /webhook/github` in `cli_api_server.py`
3. Add `WebhookVerifier` as FastAPI dependency
4. Wire `workflow_run` events to `workflow-health-monitor` agent
5. Wire `pull_request` events to `ci-testing-agent`

---

## Objective 6: D_CAPABLE Promotion — `workflow-health-monitor`

**Priority:** P3  
**Timeline:** After 2026-04-04 (observation window closes)  
**Status:** ⏳ On schedule

Per ADR-20260305-fourth-d-capable-evaluation.md:
- C4 observation window: 2026-03-05 → 2026-04-04 ✅ (in progress)
- C8 @mbaetiong sign-off: ✅ received 2026-03-05

**Action required after 2026-04-04:**
1. Update `AGENT_REGISTRY.yaml` — `workflow-health-monitor` → `D_CAPABLE`
2. Update `AGENT_REGISTRY.yaml` version → 2.0.0
3. Advance `owner-approval-guard` to DESIGNATED (5th D_CAPABLE candidate)

---

## Phase 23 Summary

```
Priority  Objective                          Status    Owner
────────  ─────────────────────────────────  ────────  ─────────────
P1        GHCR image activation              🔄 ready  Copilot (after merge)
P1        Codespace secrets config           ⏳ admin  @mbaetiong
P2        Auth coverage gap-fill (90%)       🔄 next   Copilot (S115)
P2        Webhook activation                 ⏳ infra  @mbaetiong + Copilot
P3        OODA webhook integration           🔄 plan   Copilot (S116)
P3        D_CAPABLE workflow-health-monitor  ⏳ time   Copilot (post 2026-04-04)
```
