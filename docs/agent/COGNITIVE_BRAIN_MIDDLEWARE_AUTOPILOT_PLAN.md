# Cognitive Brain Middleware AUTOPILOT Plan

**Purpose:** Make the active Codespace-hosted Cognitive Brain the middleware control
plane for Aries-Serpent/_codex_ while keeping the implementation independent of
any generated Codespace name.

## 1. Current Verified State

At plan revision time, the active environment is a Codespace named
`glorious-dollop-qgg97744x5whxrx4`. This name is evidence, not configuration.
The process at PID 23807/29671 and the current listener are not addressed by that
name. The Cognitive Brain is bound to loopback port 8765 and discovered through
`CODEX_CLI_API_URL`, `COPILOT_CLI_BASE_URL`, or the local default.

Verified:

- `GITHUB_TOKEN` authenticates as `mbaetiong` for the `/user` endpoint.
- The Cognitive Brain API is healthy on `127.0.0.1:8765`.
- `/api/capabilities` returns server-observed adapter states.
- `/api/routes/plan` plans read operations and keeps write operations dry-run-only.
- `BrainClient` exposes capability discovery and route planning.
- Workspace-local startup runs under simulated future Codespace names.
- Hosted webhook/variable/port synchronization is disabled unless explicitly enabled.
- Eight focused middleware tests pass.

Not yet verified or installed:

- A task-scoped hosted write through GitHub CLI; `gh` read access is verified
- Node.js/npm runtime in the current Codespace (frontend TypeScript diagnostics pass,
  but full frontend build/E2E execution remains blocked)
- Playwright package and browser binaries
- Live write scopes for each credential class
- Hosted MCP exposure and MCP write tools
- GitHub PR and Actions write permissions
- Required-check, merge, release, and deployment permissions
- VS Code Copilot, Copilot Chat, Actions, Playwright, Python, and Debugpy extension exposure

### Implementation Status (2026-11-18)

Security Gate 1 is implemented locally:

- action metadata, not the caller's `mutating` field, classifies route risk;
- unknown or destructive action/capability pairs deny without a preferred adapter;
- documented/installed/exposed adapters cannot silently become operation-verified;
- `/api/cli/run`, credential-injecting GitHub proxy calls, proxy mutations, and CLI
  history require operation authentication;
- `/ws/cli` rejects missing/invalid bearer credentials before accepting a shell;
- `/api/github/token` returns 410 and no longer exports reusable GitHub credentials;
- proxy redirects are disabled and 3xx responses are rejected;
- `BrainClient` forwards credentials only to approved loopback or configured HTTPS
  origins, and capability/health/plan discovery is unauthenticated;
- Git remote output is sanitized and probe origins are allowlisted;
- startup verifies the process command, workspace cwd, PID, and health nonce before
  reporting success;
- the devcontainer resolves the checked-in `.config/Dockerfile.preview` and image
  identity, while update-content now creates one canonical workspace `.venv`;
- `gh` 2.83.0 was checksum-verified and installed user-locally; live repository reads
  report actor `mbaetiong`, `push/admin=true`, PR/Actions/checks/deployments/releases
  reads 200, and Code/Secret Scanning reads 403;
- the read-only credential probe reports both configured `CODEX_*` tokens as 401 and
  `GITHUB_TOKEN` as authenticated; no write capability is claimed.

Screenshot reconciliation:

- The GitHub fine-grained PAT screens in the supplied screenshots are treated as
  server credential inventory, not browser configuration. Expired `CODEX_*` values
  are confirmed by live `/user` 401 responses and are never copied into Vite variables.
- The Cognitive Brain web app bootstraps a short-lived HttpOnly `codex_ui_session`
  from an allowed localhost/Codespace origin. HTTP operations use
  `credentials: include`, and the PTY WebSocket authenticates the cookie plus origin.
- Direct browser writes are disabled. If the middleware is unavailable, the app may
  fall back only to unauthenticated HTTPS GET reads; it must not forward an
  Authorization header or use a browser-visible GitHub token.
- `/api/github/token`, `VITE_GITHUB_TOKEN`, and raw PAT harvesting remain incompatible
  with the target model. GitHub operations are executed server-side after route,
  permission, idempotency, and evidence preflight.

Focused evidence: 46 existing BrainClient tests plus 18 middleware/security tests pass.
The current remaining external blockers are Node/npm/Playwright runtime installation,
live MCP host registration/write tools, and task-scoped hosted write verification.

## 2. Codespace Identity Invariants

1. No active implementation file may contain the current generated Codespace name.
2. `CODESPACE_NAME` is accepted only at runtime for a temporary forwarded URL,
   capability evidence, or a log-safe environment report.
3. Workspace resolution uses `CODESPACE_VSCODE_FOLDER`, then the repository root
   derived from the lifecycle script, then the normal checkout location.
4. The Cognitive Brain endpoint uses environment configuration and loopback as
   fallback. Application clients must not derive endpoints from the Codespace name.
5. VS Code settings use `${workspaceFolder}` where VS Code expansion is supported.
6. Startup must be rerunnable with a different `CODESPACE_NAME`; an identity change
   must not require code, workflow, or MCP configuration edits.
7. Hosted mutations during local startup are disabled by default. Set
   `CODEX_SYNC_CODESPACE_WEBHOOKS=true` only for an explicitly authorized webhook
   synchronization run.
8. The maintainer probe records `name_is_runtime_evidence_only: true` and never
   treats a generated name, cached variable, or historical report as permission.

## 3. Cognitive Brain Middleware Architecture

The Cognitive Brain is the active Codespace middleware control plane. MCP is one
protocol adapter into and out of this layer.

```text
Ingress adapters
  Copilot tools | REST/BrainClient | VS Code tasks | webhooks | MCP | Playwright
        |
        v
Capability registry and server-observed health
        |
        v
Policy / authority / OODA decision
        |
        v
Route planner: MCP -> VS Code -> CLI -> REST/GraphQL -> local API -> Playwright
        |
        v
Dispatcher, normalized evidence, retry and rollback
        |
        v
Objective state: planned -> verified -> complete/partial/denied/rolled_back
```

### 3.1 Stable Route API

- `GET /api/health`: liveness only.
- `GET /api/capabilities`: route catalog, installed/exposed/verified state, no secret values.
- `POST /api/routes/plan`: fail-closed dry planning; mutations remain execution-disabled.
- `POST /api/routes/execute`: future authenticated and idempotent execution endpoint.
- `GET /api/routes/{operation_id}`: future state, evidence, and reconciliation endpoint.
- `POST /api/routes/{operation_id}/rollback`: future task-owned rollback endpoint.
- `GET /api/health/deep`: future adapter-level readiness.

Route requests carry:

- operation and capability
- target and action
- read/write class and risk class
- adapter and credential profile
- idempotency key
- trace and resume cursor
- policy result and expected evidence

### 3.2 Adapter Responsibilities

| Adapter | Responsibility |
|---|---|
| `github_mcp` | Preferred structured GitHub read and later write operations |
| `vscode_github` | PR extension operations available to the active VS Code session |
| `vscode_actions` | Actions extension reads and permitted controls |
| `vscode_scm` | Source Control state, branch, commit, and diff discovery |
| `git` | Local repository mutation and transport |
| `gh` | GitHub CLI, API, PR, and workflow fallback |
| `rest_graphql` | Direct GitHub operation fallback with operation-specific auth |
| `playwright_mcp` / `playwright_cli` | UI verification and genuine UI-only fallback |
| `brain_cli` / `brain_api` | Codespace-local command/API bridge with policy enforcement |

### 3.3 Security Boundary

Before `/api/routes/execute` is implemented:

- authenticate command, proxy, memory, route execution, and credential-bearing paths;
- stop returning reusable raw GitHub tokens from `/api/github/token`;
- infer scopes from live GitHub responses, not environment-variable names;
- retain SSRF, shell, path, CORS, rate-limit, and secret-redaction controls;
- require an operation-specific policy profile and idempotency key;
- keep force-push, secret rotation, branch deletion, approval bypass, and check weakening forbidden;
- route no secret value into arbitrary adapter subprocess arguments or logs.

## 4. Systematic Capability Closure

### 4.1 GitHub CLI

**Preferred repair:** rebuild the Codespace so the configured GitHub CLI devcontainer
feature is actually installed.

**Fallback:** install a user-local `gh` binary into `$HOME/.local/bin`.

**Final fallback:** use REST/GraphQL through the Cognitive Brain or direct authorized
API clients. This preserves functionality but records CLI absence as a gap.

Validation:

1. Record `command -v gh` and version.
2. Supply `GH_TOKEN` only to the probe process.
3. Run `gh auth status`, `gh api user`, and repository permission reads.
4. Read PR, Actions, checks, and workflow metadata.
5. Use `gh` for a reversible task branch/PR operation during the approved implementation.

Done when installed, exposed, authenticated, and operation-specific read/write
results are evidenced.

### 4.2 Node.js/npm

**Preferred repair:** devcontainer Node 22 feature and Codespace rebuild.

**Fallback:** supported user-local Node 22 binary or version manager.

Validation:

1. Compare Node version to all active `engines` ranges.
2. Validate npm version and lockfile consistency.
3. Run `npm ci` in `cognitive_app` without lockfile churn.
4. Run TypeScript, ESLint, Vitest, and production build.
5. Install browser binaries only after the Node dependency graph is healthy.

### 4.3 Playwright MCP and Repository Playwright

**Preferred browser protocol:** Playwright MCP, but only after live host discovery.

**Preferred local fallback:** `cognitive_app` `@playwright/test` and installed browsers.

**Final fallback:** API/UI verification report with an exact environment blocker.

Validation:

1. Verify package and browser inventory.
2. Run one Chromium smoke test.
3. Run desktop and mobile acceptance tests.
4. Run Firefox/WebKit where supported.
5. Capture screenshot and trace on failure.
6. Use Playwright for UI-only operations; preserve API/CLI priority for mutations.

### 4.4 Live Credential and Write Scope Verification

Implemented `scripts/autonomous/credential_probe.py` without printing secrets. It
includes an azimuth mode over 14 write permission families and the operation matrix in
`scripts/autonomous/github_permission_matrix.py`.

Azimuth is a 360-degree validation loop, not a list of assumed scopes:

1. **North - identity and scope metadata:** actor, token source, repository role,
   classic OAuth headers, accepted scopes, and credential failures.
2. **East - preflight:** read the exact endpoint, required checks, environment,
   branch/ruleset, current state, and required credential class.
3. **South - adversarial write attempt:** omit or spoof client mutation flags,
   reject unknown actions, test 401/403/404/410, and confirm no unrelated fallback.
4. **West - reversible live probe:** perform only the task-owned operation with a
   unique idempotency marker and capture the external ID/URL/check state.
5. **Center - reconciliation and rollback:** verify the expected external state,
   restore/close/delete/mark inactive where possible, and record terminal evidence.
6. **Outer ring - rubber-duck trace:** name the invariant, identify who decides
   authorization, trace credential and target, identify the sink, and state the
   cheapest test that disproves the implementation.

Current azimuth evidence (2026-11-18):

- `CODEX_MASTER_KEY`: configured but `/user` returns 401; no read or write verified.
- `CODEX_BACKUP_KEY`: configured but `/user` returns 401; no read or write verified.
- `GITHUB_TOKEN`: authenticates as `mbaetiong`; repository role is admin/push/pull.
- Contents: **live write verified** by creating an unreferenced Git blob (HTTP 201,
  SHA `54a0b0652b8066ac0e4c96d68776409abb5f55fe`) with no visible ref change.
- PR, Actions, Checks, Issues, Statuses, Releases, Deployments, Discussions,
  Variables, Secrets, Webhooks, Security Events, and Administration remain dry-run.
- Code Scanning and Secret Scanning reads currently return 403 even though repository
  metadata reports administrative permissions; scope/role metadata is not write proof.

All 14 domains remain represented in the default read-only azimuth report. Only the
Contents blob probe is opt-in `--live-safe-probes`; every other domain requires its
own task-owned reversible target and blocked-by controls.

Credential classes:

- GitHub App installation
- classic PAT
- fine-grained PAT
- Codespace `GITHUB_TOKEN`
- VS Code GitHub account

Probe sequence:

1. Identify the active source and authenticated actor.
2. Capture classic scope headers when applicable.
3. Read installation/application permissions for GitHub App tokens.
4. Exercise operation-specific read endpoints for fine-grained tokens.
5. Verify Contents, PR, Issues, Actions, Checks, Security, Discussions, Deployments,
   Variables, Secrets, Webhooks, and Administration separately.
6. Perform each reversible write proof only during a real task-owned objective.
7. Normalize 401/403/404/410 denials and continue every permitted fallback.
8. A role/permission metadata field may permit preflight but cannot set `write_verified`.
9. Completion requires an operation result, reconciliation, and rollback/terminal-state
   evidence for every attempted domain.

A credential name is never considered proof of a scope.

Permission-family execution order:

1. **Contents and Statuses:** task-owned SHA; dangling object/no-op status.
2. **Pull Requests:** task branch, draft PR, update, check reconciliation, close.
3. **Issues/Discussions:** only a uniquely marked probe and close/terminal-state review.
4. **Actions/Checks:** dedicated no-op workflow and task-commit check only; no generic
   production dispatch.
5. **Variables:** create/update/delete a task-prefixed variable and verify 404.
6. **Secrets/Webhooks/Administration:** elevated, operation-specific adapter; create
   disabled resources where supported, delete/restore, exact denial otherwise.
7. **Deployments/Releases:** draft/inactive task resources only, delete where supported,
   with environment/owner/server controls intact.
8. **Security Events:** never synthesize an alert; only a task-owned test alert with a
   captured original state may be dismissed/restored.


### 4.5 MCP Exposure and Writes

1. Consolidate `MCPToolRegistry`, server `ToolRegistry`, and JSON-RPC listing.
2. Expose the same Cognitive Brain capability catalog through MCP.
3. Add tool schemas, risk class, credential profile, idempotency, and rollback class.
4. Add HTTP/JSON-RPC and stdio entrypoints using secret-free workspace registration.
5. Route `tools/call` through the same policy and evidence path as `/api/routes/*`.
6. Initially register read tools, then reversible branch/PR/Actions writes.
7. Verify unauthorized, schema-invalid, policy-denied, retry, resume, and rollback paths.

Done means the live VS Code/Copilot host discovers and invokes the tool. Checked-in
MCP code alone is not completion evidence.

### 4.6 Hosted PR and Actions Permissions

Use this read chain:

```text
GitHub MCP -> VS Code PR/Actions extension -> gh -> REST/GraphQL -> Playwright UI
```

Use this write chain:

```text
Cognitive Brain route plan -> live permission preflight -> authorized adapter
-> external result verification -> evidence and rollback state
```

Verify separately:

- PR read/create/update/comment/thread access
- approval/CODEOWNERS limitations
- branch protection and required checks
- workflow run/job/log/artifact/check access
- dispatch/retry/cancel permissions for owned objectives
- merge methods and environment protection
- release, deployment, and security-alert boundaries

Only hosted check conclusions establish hosted CI state. Local tests establish only
local validation.

## 5. VS Code/Codespace Contract

The repository must retain and validate:

- `.devcontainer/devcontainer.json`
- `.devcontainer/scripts/on-create.sh`
- `.devcontainer/scripts/update-content.sh`
- `.devcontainer/scripts/post-create.sh`
- `.devcontainer/scripts/post-start.sh`
- `.devcontainer/scripts/post-attach.sh`
- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/launch.json`
- `.vscode/extensions.json`
- `.github/instructions/*`
- `.github/agents/*` active customizations
- `.github/prompts/*` active prompts
- `scripts/autonomous/maintainer_probe.py`

Every Codespace session should have native tasks for:

- redacted maintainer capability discovery;
- local-only Cognitive Brain startup;
- middleware routing tests;
- MCP health/smoke;
- credential permission discovery;
- focused GitHub read validation;
- frontend and Playwright smoke;
- YAML/actionlint and security checks.

Recommended extension installation is configuration, not proof of installation.
The probe must report each extension as recommended, installed, exposed, or unavailable.

## 6. Dependency-Ordered Roadmap

### Phase A: Portable Startup and Evidence - In Progress

Files:

- `.devcontainer/scripts/post-start.sh`
- `scripts/autonomous/maintainer_probe.py`
- `.devcontainer/devcontainer.json`
- `.vscode/settings.json`
- `.vscode/extensions.json`
- `.vscode/tasks.json`

Acceptance:

- startup works with at least two simulated Codespace names;
- current name appears only in runtime evidence;
- Cognitive Brain process is tracked and healthy;
- hosted startup mutations remain disabled by default;
- probe, middleware tests, and VS Code JSON validation pass.

### Phase B: Secure Route Execution

Files:

- `cognitive_app/src/server/cli_api_server.py`
- `src/aries_serpent_core/agents/brain_client.py`
- `src/codex/cognitive_brain/routing.py`
- new middleware policy, adapter, evidence, and operation-state modules
- focused security and routing tests

Acceptance:

- all mutating and credential-bearing routes authenticate;
- dry plan and execute are distinct;
- server emits no token or secret values;
- one read-only GitHub operation executes and records a trace;
- writes remain blocked pending operation-specific permission proof.

### Phase C: Toolchain and Live Permission Closure

Files:

- `.devcontainer/*`
- `scripts/autonomous/credential_probe.py`
- `scripts/autonomous/maintainer_probe.py`
- startup and permission tests

Acceptance:

- `gh`, Node/npm, and Playwright are installed/exposed or carry precise denial evidence;
- credential source and operation permissions are recorded;
- no scope is inferred from a variable name.

### Phase D: Unified MCP

Files:

- `src/mcp/registry.py`
- `src/mcp/server/*`
- Cognitive Brain adapter contract
- workspace MCP configuration after supported registration is verified

Acceptance:

- MCP and REST discover the same tools;
- one reversible read/write call traverses policy, adapter, evidence, and result;
- denied and transient failures do not claim success.

### Phase E: Hosted PR/Actions Autonomy

Files:

- `scripts/autonomous/github_adapters.py`
- `scripts/autonomous/checks.py`
- `scripts/autonomous/pr.py`
- `scripts/autonomous/worktree.py`
- `.github/workflows/autonomous-agent.yml`

Acceptance:

- one real task branch, push, PR, check poll, and post-result verification completes;
- actual hosted state is reconciled;
- branch/approval/environment controls remain authoritative.

### Phase F: Browser and Deployment Closure

Acceptance:

- desktop/mobile Playwright validation is reproducible;
- Playwright MCP and CLI fallback are distinguished;
- release/deployment occurs only after live policy, checks, artifacts, and environment
  approvals permit it.

## 7. End-to-End Acceptance Scenario

1. A new Codespace is created with an unrelated generated name.
2. Lifecycle hooks resolve the checkout root dynamically.
3. The Cognitive Brain starts locally and tracks its own PID.
4. VS Code tasks load the workspace interpreter and run capability discovery.
5. The middleware reports each adapter as documented, installed, exposed, verified,
   unavailable, or denied.
6. A read-only GitHub objective selects the first working route.
7. Live permissions are probed for the required operation.
8. A task branch, patch, PR, and checks are processed through the first available adapter.
9. Check runs, review state, and merge policy are reconciled from hosted GitHub state.
10. A permitted low-risk PR is merged and post-merge state is verified.
11. A server denial, if genuine, is recorded with the exact operation and prerequisite;
    all permitted alternatives have already run.

## 8. Evidence and Completion

Completion evidence must include:

- current checkout HEAD and dirty-state snapshot;
- Codespace name marked runtime-only;
- workspace resolution source;
- capability and extension matrix;
- authenticated actor and redacted credential source;
- route selection and fallback attempts;
- external operation IDs and URLs;
- local and hosted validation results;
- exact denials and required server-side controls;
- rollback pointer and final complete/partial/failed state.

No archived report, cached capability flag, or checked-in variable is accepted as
proof of live credentials, MCP exposure, permissions, checks, mergeability, or deployment.
