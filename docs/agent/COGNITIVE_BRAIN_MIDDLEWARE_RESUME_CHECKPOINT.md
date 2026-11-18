# Cognitive Brain Middleware Resume Checkpoint

Checkpoint date: 2026-11-18
Source branch at start: `0D_base_`
Source HEAD: `f188b8277a897db4bc1fbe844270077854acf08d`
Primary plan: `docs/agent/COGNITIVE_BRAIN_MIDDLEWARE_AUTOPILOT_PLAN.md`

## Session Progress

1. Built a redacted maintainer capability probe and VS Code tasks.
2. Started the Codespace Cognitive Brain on loopback port 8765.
3. Added capability discovery and deterministic read/write route planning.
4. Reviewed recent work using CodeQL-pattern, rubber-duck, and adversarial logic.
5. Implemented Security Gate 1:
   - authenticated CLI, credential-bearing proxy, CLI history, and WebSocket routes;
   - retired `/api/github/token` with 410;
   - server-classified actions and truthful verified-state routing;
   - blocked proxy redirects;
   - restricted BrainClient credential forwarding to approved origins;
   - sanitized probe remotes and restricted probe origins;
   - added PID/workspace/startup-nonce process ownership.
6. Added a 14-family GitHub azimuth write-permission matrix with reversible preflight,
   adversarial, live-probe, reconciliation, and rollback criteria.
7. Verified one live Contents write without changing a ref:
   - HTTP 201;
   - unreferenced blob SHA `54a0b0652b8066ac0e4c96d68776409abb5f55fe`;
   - `main` remained a normal unchanged ref.
8. Installed checksum-verified `gh` 2.83.0 in `$HOME/.local/bin` and verified actor
   `mbaetiong` plus repository push/admin metadata.
9. Reconciled the supplied GitHub/Cognitive Brain screenshots:
   - configured `CODEX_MASTER_KEY` returns 401;
   - configured `CODEX_BACKUP_KEY` returns 401;
   - `GITHUB_TOKEN` returns 200 for actor `mbaetiong`;
   - browser PAT export is disabled;
   - the Cognitive Brain UI uses a 15-minute HttpOnly session cookie for HTTP and
     WebSocket access.

## Current Verified State

- Live Cognitive Brain: `http://127.0.0.1:8765/api/health`
- Startup tracks the actual listener PID and emits a matching startup nonce.
- UI session: POST `/api/session` from an allowed origin -> HttpOnly cookie.
- Unauthenticated CLI: 401.
- Raw token endpoint: 410.
- Foreign UI session origin: 403.
- GitHub CLI: installed and authenticated for read operations.
- Repository read permissions: PR, Actions, checks, deployments, releases, repository -> 200.
- Code Scanning and Secret Scanning reads: 403.
- Default azimuth mode is dry-run and cannot execute writes.
- Only Contents has task-safe live write evidence; all other write families remain
  explicitly unverified/dry-run.

## Validation at Checkpoint

- 18 routing/UI-session/security tests passed.
- 5 azimuth permission tests passed.
- 46 existing BrainClient tests passed.
- Ruff passed for focused changed Python files.
- Black passed for focused changed Python files.
- Python and shell syntax checks passed.
- VS Code TypeScript diagnostics report no errors in changed frontend files.
- `git diff --check` passed.
- Full frontend build and Playwright E2E were not run because Node/npm and browser
  dependencies are absent from the active Codespace.

## Remaining Work

1. Implement secure route execution only after operation-specific authorization,
   idempotency, rollback, and state revalidation exist.
2. Add hosted task-scoped reversible write proofs for PR, issue/discussion, Actions,
   Checks, Statuses, Releases, Deployments, Variables, Secrets, Webhooks, Security
   Events, and Administration. Continue after genuine denials where another route is
   permitted; never infer success from repository role metadata.
3. Restore Node 22/npm through the devcontainer feature/rebuild and run `npm ci`,
   TypeScript, ESLint, Vitest, build, and Playwright desktop/mobile smoke.
4. Register MCP in the active VS Code/Copilot host and prove handshake/list/call/write
   behavior. Current MCP state is documented/prototype, not host-exposed.
5. Reconcile VS Code extension installation/activation for Copilot, Chat, Actions,
   Playwright, Python, and Debugpy.
6. Complete clean create/rebuild/restart/concurrent-restart Codespace acceptance.
7. Add a real hosted CodeQL or local CodeQL/SAST result. Current evidence is a
   CodeQL-pattern/adversarial review; no local CodeQL database/CLI was available.

## Resume Commands

```bash
cd /workspaces/_codex_
git fetch origin
git status --short
git branch --show-current
python3.12 scripts/autonomous/maintainer_probe.py
.venv/bin/python scripts/autonomous/credential_probe.py
PYTHONPATH=src .venv/bin/python -m pytest \
  --confcutdir=tests/self_improvement \
  -o addopts='--strict-markers --import-mode=importlib' \
  -q tests/self_improvement/test_routing.py \
  tests/self_improvement/test_routing_api.py
PYTHONPATH=. .venv/bin/python -m pytest \
  --confcutdir=tests/autonomous \
  -o addopts='--strict-markers --import-mode=importlib' \
  -q tests/autonomous/test_github_permission_matrix.py
```

Do not reset, stash, rebase, force-push, rotate secrets, bypass server controls,
claim write proof from role metadata, or expose credentials in logs/browser assets.

## Copyable Resume Prompt

```text
Resume the Aries-Serpent/_codex_ Cognitive Brain AUTOPILOT implementation from the current task branch. Read docs/agent/COGNITIVE_BRAIN_MIDDLEWARE_AUTOPILOT_PLAN.md and docs/agent/COGNITIVE_BRAIN_MIDDLEWARE_RESUME_CHECKPOINT.md first. Preserve all existing dirty work and use the branch/commit from the checkpoint; do not reset, stash, rebase, or force-push.

The current implementation already contains capability discovery, fail-closed server-owned routing, authenticated CLI/proxy/history/WebSocket operations, a 15-minute HttpOnly UI session, raw-token endpoint retirement, redirect/SSRF reduction, BrainClient origin gating, PID/cwd/startup-nonce process ownership, Codespace portability, a credential probe, gh installation, and a 14-family azimuth write matrix. One Contents blob write was verified without changing a ref. Both CODEX_* tokens return 401; GITHUB_TOKEN authenticates as mbaetiong. Code/Secret Scanning reads return 403. All other write families remain dry-run/unverified.

Continue from Security/Route Gate 1 in this order:
1. Verify worktree, branch, HEAD, live Cognitive Brain health, UI session, and focused tests.
2. Implement operation state, request digest, idempotency, and secure /api/routes/execute; bind legacy operations to the plan.
3. Complete task-scoped reversible GitHub write probes in safe order: status/Contents, PR, issues/discussions, Actions/Checks, variables, releases/deployments, then security/admin surfaces only when live server controls permit them.
4. Restore Node 22/npm through the devcontainer route, run npm ci/typecheck/lint/Vitest/build, install Playwright browsers, and validate desktop/mobile UI.
5. Register and verify MCP host exposure, handshake/listTools/callTool, then one reversible write through the Cognitive Brain policy boundary.
6. Run real hosted PR/check/security reconciliation and report exact server-side denials without fabricating permissions.

Use rubber-duck invariants and adversarial tests for every sink. Never print secrets, place PATs in Vite/browser variables, weaken checks, bypass approvals/branch/environment controls, or claim that repository role metadata proves a write scope. Commit task-related changes, push the checkpoint/task branch, and provide commit/branch/PR/check evidence. Local tests do not establish hosted CI or mergeability.
```
