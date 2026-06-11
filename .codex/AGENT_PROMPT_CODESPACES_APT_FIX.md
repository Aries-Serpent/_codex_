# PROMPT: Codespaces Prebuild APT State Failure — End-to-End Implementation

> **Status**: READY FOR COPILOT AGENT EXECUTION  
> **Generated**: 2026-06-04T04:30:00Z | Author: @mbaetiong  
> **Target**: Aries-Serpent/_codex_ | Commit: a8101576dd6abe2ac9c63dcc07a6f08b8ee778f9  
> **Workflow Reference**: [Job 79446195236](https://github.com/Aries-Serpent/_codex_/actions/runs/26929477931/job/79446195236)

---

## 📋 Executive Summary

The GitHub Codespaces prebuild is failing during the `onCreateCommand` phase with error `1309 (UnifiedContainersErrorPrebuilTemplateOnCreateFailed)`. Root cause: APT package list directory (`/var/lib/apt/lists/partial`) has permission issues or doesn't exist during container prebuild initialization, causing `apt-get update` to fail with exit code 100.

**Solution**: Repair APT state atomically before package operations, add retry logic, and document new repository/organization variables required for Codespaces environment consistency.

---

## 🎯 Implementation Goals

### Primary Goal
Fix the `.devcontainer/scripts/on-create.sh` script to handle APT state corruption gracefully during prebuild, ensuring:
1. APT lists directory is cleaned and recreated with correct permissions
2. `apt-get update` succeeds with built-in retry logic
3. Package installation completes without cascading failures
4. Cleanup occurs safely only after successful operations

### Secondary Goals
1. **Document required Codespaces environment variables** in repo/org variable inventory
2. **Add new variables to existing variable tracking documents** (MUST/SHOULD/MAY categories)
3. **Update `.devcontainer/devcontainer.json`** to reference new variables where applicable
4. **Ensure all changes are idempotent** and work in both root and non-root container contexts

---

## 📊 Investigation Summary

### Error Evidence (from Job Logs)

```
2026-06-04T04:08:56.7184319Z E: List directory /var/lib/apt/lists/partial is missing. - Acquire (13: Permission denied)
2026-06-04T04:08:56.7273230Z onCreateCommand from devcontainer.json failed with exit code 100.
2026-06-04T04:08:56.7308876Z Error: Command failed: /bin/sh -c bash .devcontainer/scripts/on-create.sh
2026-06-04T04:08:58.0813945Z ##[error]Process completed with exit code 1.
```

### Failing Script Location
- **File**: `.devcontainer/scripts/on-create.sh`
- **Issue Line**: 34–47 (lines that attempt `apt-get update` and package installation)
- **Trigger**: Devcontainer lifecycle — `onCreateCommand` phase (runs once during prebuild)

### Current Script Behavior
1. Lines 34–47: Attempts `apt-get update` + install without checking APT state
2. Line 48: Aggressively removes `/var/lib/apt/lists/*` after installation
3. **Problem**: If `apt-get update` fails, APT state becomes corrupted; subsequent runs fail because lists directory is missing

### Files Inspected
- ✅ `.devcontainer/scripts/on-create.sh` (current implementation)
- ✅ `.devcontainer/devcontainer.json` (lifecycle command configuration)
- ✅ `docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md` (variable inventory)
- ✅ `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` (variable patterns)
- ✅ `docs/admin/integration/GITHUB_ENVIRONMENT_SETUP.md` (Codespaces env setup)
- ✅ `.codex/runtime_variables.md` (variable naming conventions)
- ✅ `.codex/CRITICAL_REPOSITORY_VARIABLES.md` (critical variable list)

---

## 🔧 SOLUTION: FIX (Primary Implementation Path)

### Step 1: Update `.devcontainer/scripts/on-create.sh`

**Action**: Replace the current script with the patched version that includes APT state repair and retry logic.

**File**: `.devcontainer/scripts/on-create.sh`  
**Change Type**: Full replacement with backward compatibility

**Pseudo-code**:
```
1. Resolve sudo (existing logic, keep as-is)
2. Print banner (existing logic, keep as-is)
3. [NEW] Repair APT state atomically:
   - Remove corrupted APT state (lists, cache)
   - Create missing directories with correct permissions
   - Run `apt-get clean` to clear any locked resources
4. [NEW] Update APT with retry logic:
   - Try `apt-get update`
   - If fails, reset state and retry once
   - Exit with explicit error if retry fails
5. Install packages (keep existing package list, add error handling)
6. Cleanup APT lists (move after retry block, ensure cleanup only on success)
7. Configure Git LFS (existing logic, keep as-is)
8. Create runtime directories (existing logic, keep as-is)
9. Print completion message (existing logic, keep as-is)
```

---

### Step 2: Add/Update Repository Variables

**Scope**: Repository-level variables for Codespaces environment consistency

**New Variables to Add** (or update if existing):

| Variable Name | Category | Type | MUST/SHOULD/MAY | Value | Purpose |
|---------------|----------|------|-----------------|-------|---------|
| `CODESPACES_APT_UPDATE_RETRY` | Container Setup | Boolean | SHOULD | `true` | Enable APT update retry logic in on-create.sh |
| `CODESPACES_APT_CLEANUP_AGGRESSIVE` | Container Setup | Boolean | MAY | `true` | Aggressively clean APT lists after install (existing behavior) |
| `CODEX_DEVCONTAINER_WORKSPACE` | Workspace Config | String | SHOULD | `/workspaces/_codex_` | Canonical workspace path for Codespaces (mirrors CODESPACE_VSCODE_FOLDER) |
| `CODEX_DEVCONTAINER_PYTHON_VERSION` | Runtime Config | String | MUST | `3.12` | Python version for devcontainer (MUST match pyproject.toml) |
| `CODEX_DEVCONTAINER_NODE_VERSION` | Runtime Config | String | SHOULD | `22` | Node.js version for devcontainer (from devcontainer.json) |
| `CODEX_DEVCONTAINER_RUST_VERSION` | Runtime Config | String | MAY | `stable` | Rust version for devcontainer features |
| `CODEX_SESSION_LOG_DIR` | Logging Config | String | MUST | `/workspaces/_codex_/.codex/sessions` | Session log directory (in-container path) |
| `CODEX_DB_PATH` | Database Config | String | MUST | `/workspaces/_codex_/.codex/codex.db` | SQLite database path for Codespaces (Copilot session context) |
| `CODEX_SQLITE_POOL` | Database Config | Integer | SHOULD | `1` | Enable per-session SQLite connection pooling (prevents lock contention) |
| `CODEX_CLI_API_URL` | Network Config | URL | MUST | `http://localhost:8765` | Cognitive Brain CLI API server URL (matches hardcoded value in copilot-setup-steps.yml) |

**Location to Add**:
- File: `https://github.com/Aries-Serpent/_codex_/settings/variables/actions` (GitHub UI)
- Or: Auto-add via `scripts/ops/codex_repo_admin_bootstrap.py` if variable sync workflow exists

**Decision Points** (mark in `.codex/CRITICAL_REPOSITORY_VARIABLES.md`):
- ✅ Add to `CRITICAL_REPOSITORY_VARIABLES.md` § "Codespaces Container Setup" section
- ✅ Add to `runtime_variables.md` with narrative documentation
- ✅ Add to `REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` with implementation instructions
- ✅ Reference in `docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md` (if it exists)

---

### Step 3: Update Documentation

**Files to Update**:

#### 3.1 `.codex/CRITICAL_REPOSITORY_VARIABLES.md`
Add new section after existing "Environment & Deployment" section:

```markdown
## 10. Codespaces Container Setup (NEW)

These variables control the devcontainer lifecycle and ensure Copilot agents
in Codespaces have consistent runtime configuration across prebuilds and rebuilds.

| Variable | MUST/SHOULD/MAY | Default | Purpose |
|----------|-----------------|---------|---------|
| `CODESPACES_APT_UPDATE_RETRY` | SHOULD | `true` | Enable retry logic when apt-get update fails during prebuild |
| `CODESPACES_APT_CLEANUP_AGGRESSIVE` | MAY | `true` | Aggressively clean APT lists after installation (safe for transient containers) |
| `CODEX_DEVCONTAINER_WORKSPACE` | SHOULD | `/workspaces/_codex_` | Canonical workspace path (mirrors CODESPACE_VSCODE_FOLDER env var) |
| `CODEX_DEVCONTAINER_PYTHON_VERSION` | MUST | `3.12` | Python version (MUST match pyproject.toml requires-python) |
| `CODEX_DEVCONTAINER_NODE_VERSION` | SHOULD | `22` | Node.js version for cognitive_app builds |
| `CODEX_DEVCONTAINER_RUST_VERSION` | MAY | `stable` | Rust toolchain version for container features |
| `CODEX_SESSION_LOG_DIR` | MUST | `/workspaces/_codex_/.codex/sessions` | Session log SQLite directory (in-container, not repo root) |
| `CODEX_DB_PATH` | MUST | `/workspaces/_codex_/.codex/codex.db` | SQLite database path for Copilot agent context (in-container) |
| `CODEX_SQLITE_POOL` | SHOULD | `1` | Enable SQLite connection pooling (prevents lock contention in concurrent sessions) |
| `CODEX_CLI_API_URL` | MUST | `http://localhost:8765` | Cognitive Brain CLI API endpoint (used by copilot-setup-steps.yml) |

**Implementation**: These variables are consumed by:
1. `.devcontainer/scripts/on-create.sh` — APT state repair + retry logic
2. `.devcontainer/scripts/update-content.sh` — Python/pip setup
3. `.devcontainer/scripts/post-create.sh` — Agent context injection
4. `.github/workflows/copilot-setup-steps.yml` — Corresponding CI environment setup
```

#### 3.2 `.codex/runtime_variables.md`
Add section under "Development Environment" → "Codespaces Configuration":

```markdown
### Codespaces-Specific Configuration

When running in GitHub Codespaces, the following variables control container setup:

**Container Lifecycle** (set at prebuild time):
- `CODESPACES_APT_UPDATE_RETRY` - If `true`, `.devcontainer/scripts/on-create.sh` retries apt-get update on failure
- `CODESPACES_APT_CLEANUP_AGGRESSIVE` - If `true`, aggressively remove APT cache after package install

**Workspace & Paths** (must reflect in-container mounts):
- `CODEX_DEVCONTAINER_WORKSPACE` - Canonical workspace path; defaults to `/workspaces/_codex_`
- `CODEX_SESSION_LOG_DIR` - Session log directory; defaults to `.codex/sessions` relative to workspace
- `CODEX_DB_PATH` - SQLite database path; defaults to `.codex/codex.db` relative to workspace

**Runtime & Versions** (must match system setup):
- `CODEX_DEVCONTAINER_PYTHON_VERSION` - Python version; MUST match `pyproject.toml`
- `CODEX_DEVCONTAINER_NODE_VERSION` - Node.js version for cognitive_app builds
- `CODEX_DEVCONTAINER_RUST_VERSION` - Rust toolchain version

**Database & Concurrency**:
- `CODEX_SQLITE_POOL` - Set to `1` to enable connection pooling (recommended for Codespaces where multiple sessions may connect)
- `CODEX_DB_PATH` - Path to SQLite DB; MUST be in `.codex/` (mounted as named volume for persistence)

**API Networking**:
- `CODEX_CLI_API_URL` - Cognitive Brain CLI API endpoint; defaults to `http://localhost:8765`
```

#### 3.3 `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md`
Add subsection under "Phase 1: Immediate Setup":

```markdown
### Codespaces Prebuild Variables (NEW)

Set these variables to ensure Codespaces prebuilds succeed and Copilot agents
have a consistent runtime environment:

**Via GitHub UI** (Settings → Secrets and variables → Actions → Variables):
1. [ ] `CODESPACES_APT_UPDATE_RETRY` = `true`
2. [ ] `CODESPACES_APT_CLEANUP_AGGRESSIVE` = `true`
3. [ ] `CODEX_DEVCONTAINER_WORKSPACE` = `/workspaces/_codex_`
4. [ ] `CODEX_DEVCONTAINER_PYTHON_VERSION` = `3.12`
5. [ ] `CODEX_DEVCONTAINER_NODE_VERSION` = `22`
6. [ ] `CODEX_SESSION_LOG_DIR` = `/workspaces/_codex_/.codex/sessions`
7. [ ] `CODEX_DB_PATH` = `/workspaces/_codex_/.codex/codex.db`
8. [ ] `CODEX_SQLITE_POOL` = `1`
9. [ ] `CODEX_CLI_API_URL` = `http://localhost:8765`

**Via `gh` CLI** (if already authenticated):
```bash
gh variable set CODESPACES_APT_UPDATE_RETRY --body "true"
gh variable set CODESPACES_APT_CLEANUP_AGGRESSIVE --body "true"
gh variable set CODEX_DEVCONTAINER_WORKSPACE --body "/workspaces/_codex_"
gh variable set CODEX_DEVCONTAINER_PYTHON_VERSION --body "3.12"
gh variable set CODEX_DEVCONTAINER_NODE_VERSION --body "22"
gh variable set CODEX_SESSION_LOG_DIR --body "/workspaces/_codex_/.codex/sessions"
gh variable set CODEX_DB_PATH --body "/workspaces/_codex_/.codex/codex.db"
gh variable set CODEX_SQLITE_POOL --body "1"
gh variable set CODEX_CLI_API_URL --body "http://localhost:8765"
```
```

---

### Step 4: Update `.devcontainer/devcontainer.json` (Optional but Recommended)

**Action**: Add comments referencing new variables and update the containerEnv to use them.

**Changes**:
- Add comment block linking to `.codex/CRITICAL_REPOSITORY_VARIABLES.md` § "Codespaces Container Setup"
- Update `containerEnv` to reference variables (using `${{ vars.VARIABLE_NAME }}` syntax is NOT available in devcontainer.json; values must be hardcoded or injected at build time, but we document the mapping)
- Add container build args or environment file references

**Pseudo-code**:
```json
{
  "name": "Codex — Copilot Agent Workspace",

  // ── REFERENCE: Variables control this container setup ──────────────────────
  // See: .codex/CRITICAL_REPOSITORY_VARIABLES.md § "Codespaces Container Setup"
  // Variables: CODESPACES_APT_UPDATE_RETRY, CODEX_DEVCONTAINER_PYTHON_VERSION, etc.
  // Note: devcontainer.json does NOT support ${{ vars.* }} syntax; values are
  // hardcoded here and documented in the variable inventory.
  // ──────────────────────────────────────────────────────────────────────────

  "image": "ghcr.io/aries-serpent/codex/preview-dev:latest",
  ...
  "containerEnv": {
    // Python (values correspond to CODEX_DEVCONTAINER_PYTHON_VERSION repo var)
    "PYTHONUNBUFFERED": "1",
    "PYTHONPATH": "/workspaces/_codex_/src",
    "PIP_NO_INPUT": "1",

    // Session & Database (values correspond to repo variables)
    "CODEX_SESSION_LOG_DIR": "/workspaces/_codex_/.codex/sessions",
    "CODEX_DB_PATH": "/workspaces/_codex_/.codex/codex.db",
    "CODEX_SQLITE_POOL": "1",
    "CODEX_CLI_API_URL": "http://localhost:8765",
    ...
  },
  ...
  "onCreateCommand": "bash .devcontainer/scripts/on-create.sh",
  ...
}
```

---

## 📋 Implementation Checklist

### Phase 1: Script Fix (Primary)
- [ ] **A1**: Create patched version of `.devcontainer/scripts/on-create.sh` with APT state repair + retry logic
- [ ] **A2**: Test locally: `devcontainer up --workspace-folder /path/to/_codex_` (verify on-create succeeds)
- [ ] **A3**: Commit and push to feature branch

### Phase 2: Variable Documentation
- [ ] **B1**: Update `.codex/CRITICAL_REPOSITORY_VARIABLES.md` with new "Codespaces Container Setup" section
- [ ] **B2**: Update `.codex/runtime_variables.md` with "Codespaces-Specific Configuration" subsection
- [ ] **B3**: Update `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` with setup instructions
- [ ] **B4**: Verify all cross-references are accurate (links, section numbers)

### Phase 3: Repository Variables Configuration
- [ ] **C1**: Create 9 new repository variables (via GitHub UI or `gh` CLI)
  - `CODESPACES_APT_UPDATE_RETRY`, `CODESPACES_APT_CLEANUP_AGGRESSIVE`, `CODEX_DEVCONTAINER_WORKSPACE`, etc.
- [ ] **C2**: Verify variables are visible at: https://github.com/Aries-Serpent/_codex_/settings/variables/actions
- [ ] **C3**: Document variable creation in a comment/issue for audit trail

### Phase 4: Devcontainer Configuration
- [ ] **D1**: Update `.devcontainer/devcontainer.json` with reference comments and mapping documentation
- [ ] **D2**: Ensure `containerEnv` values align with repo variable defaults
- [ ] **D3**: Verify comments link to variable documentation

### Phase 5: Verification & Testing
- [ ] **E1**: Trigger new Codespaces prebuild from Actions UI
- [ ] **E2**: Verify `onCreateCommand` completes successfully (check job logs)
- [ ] **E3**: Verify APT lists exist in container: `ls -la /var/lib/apt/lists/ | head -20`
- [ ] **E4**: Test Copilot agent context injection in new Codespace

### Phase 6: Documentation & Communication
- [ ] **F1**: Update `docs/agent/CODESPACE_COPILOT_AGENT_GUIDE.md` (if exists) with new variable references
- [ ] **F2**: Create/update troubleshooting guide for APT failures
- [ ] **F3**: Document rollback plan (if needed)

---

## 🔒 Important Implementation Considerations

### Idempotency & Safety
- The APT repair logic (rm -rf + mkdir) MUST be idempotent — safe to run multiple times
- Retry logic MUST NOT mask genuine failures (e.g., network down) — log explicitly
- Cleanup MUST ONLY occur after successful package installation

### Sudo Detection
- Script already handles cases where `sudo` is unavailable (non-root containers)
- APT repair MUST work in both root and non-root contexts
- Test both: `RUN ./on-create.sh` (as root in Dockerfile) and `RUN --user nonroot ./on-create.sh` (non-root)

### Volume Mounts
- `.devcontainer/devcontainer.json` mounts volumes for:
  - Pip cache: `source=codex-pipcache,target=/home/codex/.cache/pip`
  - SQLite DB: `source=codex-db,target=/home/codex/.codex`
  - Agent venv: `source=codex-agent-venv,target=/workspaces/_codex_/.venv_agent`
  - npm cache: `source=codex-npm-cache,target=/home/codex/.npm`
- APT state repair (in `/var/lib/apt`) does NOT conflict with these mounts (different paths)

### Error Tolerance
- Lines marked `2>/dev/null || true` suppress errors intentionally (known non-critical operations)
- APT retry section MUST NOT silently fail — use explicit error messages
- Log every step of retry logic (helps with future debugging)

---

## 🎯 Copilot Agent Task Description

**For Copilot Cloud Agent**: Execute the following end-to-end task with autonomy.

```
1. IMPLEMENT: Patch .devcontainer/scripts/on-create.sh
   - Add APT state repair before apt-get update
   - Add retry logic (max 2 attempts) for apt-get update
   - Ensure cleanup occurs only after successful operations
   - Maintain backward compatibility with existing logic
   - Follow existing code style and error handling patterns

2. DOCUMENT: Add/update repository variables
   - Create 9 new repository variables at GitHub UI Settings → Variables
   - OR document in a new file: .codex/CODESPACES_VARIABLES_BOOTSTRAP.sh (script to auto-create)
   - Ensure all variables are set to documented default values
   - Cross-reference in existing variable documentation files

3. UPDATE: Variable documentation files
   - .codex/CRITICAL_REPOSITORY_VARIABLES.md — add § "Codespaces Container Setup"
   - .codex/runtime_variables.md — add § "Codespaces-Specific Configuration"
   - docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md — add setup instructions
   - Ensure all links and cross-references are accurate

4. ENHANCE: .devcontainer/devcontainer.json
   - Add reference comments linking to variable documentation
   - Update containerEnv to match repo variable defaults
   - Verify all path values align (no conflicts)

5. VERIFY: Test the fix end-to-end
   - Create feature branch with all changes
   - Open pull request with detailed description
   - Document any breaking changes or migration steps
   - NO MERGE — wait for human review and Codespaces prebuild test
```

---

## ✅ Acceptance Criteria

1. **Codespaces prebuild succeeds** — Job 79446195236 equivalent completes without error 1309
2. **APT state is healthy** — `/var/lib/apt/lists/` exists with correct permissions
3. **Package installation succeeds** — All packages from on-create.sh are installed
4. **Retry logic works** — If first apt-get update fails, retry succeeds (logs show retry attempt)
5. **All variables documented** — 9 new Codespaces variables are visible in repo variable list
6. **Documentation is complete** — All 4 variable documentation files are updated with cross-references
7. **Backward compatible** — Existing workflows and scripts continue to work without modification

---

## 🔗 Key References

- **Investigation Report**: Internal analysis (above)
- **Job URL**: https://github.com/Aries-Serpent/_codex_/actions/runs/26929477931/job/79446195236
- **Workflow File**: `.github/workflows/dynamic/codespaces/create_codespaces_prebuilds`
- **Error Code**: 1309 (UnifiedContainersErrorPrebuilTemplateOnCreateFailed)
- **Commit**: a8101576dd6abe2ac9c63dcc07a6f08b8ee778f9

---

## 🚀 Next Steps (After Copilot Execution)

1. Review pull request for code quality and completeness
2. Verify all variables are set at: https://github.com/Aries-Serpent/_codex_/settings/variables/actions
3. Trigger manual Codespaces prebuild via Actions UI to test
4. Monitor Job logs for success completion
5. Merge feature branch once verification passes
6. (Optional) Create follow-up issue for automated variable sync workflow (`repo-var-sync-schedule.yml` mentioned in docs)
