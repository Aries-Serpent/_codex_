# Repository Secrets and Variables Inventory
> Generated: 2026-06-03T22:09:48Z | Author: mbaetiong
> Expanded by: Copilot Task Agent (2026-06-03T22:09:48Z)
> Variable Sync Pass: 2026-06-03T21:15:07Z (variables-only; secrets unchanged)
> Secrets/API Pass Attempt: 2026-06-03T21:32:23Z (**blocked**: GitHub Actions variables/secrets APIs returned `403 Resource not accessible by integration` for current token)
> Maintainer Manual Setup Runbook Added: 2026-06-03T21:47:19Z (explicit click-by-click fallback for all required surfaces)
> **EXPANDED EDITION**: 2026-06-04T02:41Z — comprehensive copilot-setup-steps.yml verification, gap analysis, and step-by-step maintainer setup instructions

## 🚧 Blocker Continuation: `403 Resource not accessible by integration` → Manual Maintainer Setup

Because API reads/writes are blocked for this session token, complete setup in GitHub UI using the exact steps below.

---

## 📋 TABLE OF CONTENTS

1. [Quick Start URLs](#0-open-required-pages-first-direct-urls)
2. [copilot-setup-steps.yml Verification](#copilot-setup-stepsyml-verification)
3. [Repository Variables Setup](#1-repository-variables-settingsvariablesactions)
4. [Repository Secrets Setup](#2-repository-secrets-settingssecretsactions)
5. [Environment Variables + Secrets](#3-environment-variables--secrets-aries_serpent_codex_)
6. [Organization Variables](#4-organization-variables-organizationssettingsvariablesactions)
7. [Organization Secrets](#5-organization-secrets-organizationssettingssecretsactions)
8. [Agents Variables (COPILOT Agent Settings)](#6-agents-variables-settingsvariablesagents)
9. [Agents Secrets (COPILOT Agent Settings)](#7-agents-secrets-settingssecretsagents)
10. [Post-Setup Validation](#8-immediate-post-setup-validation-ui)
11. [Complete Inventory Tables](#-complete-inventory-tables)
12. [Summary Statistics](#-summary-statistics)
13. [Execution Checklist](#-maintainer-execution-checklist)

---

## 🔍 copilot-setup-steps.yml Verification

### Variables Used by copilot-setup-steps.yml

The Copilot agent environment setup workflow (`.github/workflows/copilot-setup-steps.yml`) relies on the following repository variables. **ALL must be present** for the workflow to function correctly:

| Variable Name | Usage in Workflow | Required? | Default Fallback | Current Status |
|---------------|-------------------|-----------|------------------|----------------|
| `COPILOT_RUNNER_PROFILE` | Line 99: `runs-on: ${{ vars.COPILOT_RUNNER_PROFILE \|\| 'ubuntu-latest' }}` | No | `ubuntu-latest` | ✅ Listed in inventory |
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | Line 402: CI healer rate limit | No | none | ⚠️ **MISSING** - needs to be added |
| `CODEX_SWEEP_SKIP_MAIN` | Line 403: Skip main branch in sweep operations | No | none | ⚠️ **MISSING** - needs to be added |
| `CODEX_HEALER_SKIP_SKIPCI` | Line 404: Skip commits with [skip ci] | No | none | ⚠️ **MISSING** - needs to be added |
| `CODEX_CACHE_VERSION` | Line 406, 771: Cache key versioning | No | `v2` | ✅ Listed in inventory |
| `COPILOT_AGENT_STATE` | Line 407: Agent state tracking | No | none | ⚠️ **MISSING** - needs to be added |
| `CODEX_CI_LAST_GREEN_SHA` | Line 408: Last all-green commit SHA | No | none | ✅ Listed in inventory (automated) |

### Secrets Used by copilot-setup-steps.yml

| Secret Name | Usage in Workflow | Required? | Priority | Current Status |
|-------------|-------------------|-----------|----------|----------------|
| `CODEX_MASTER_KEY` | Lines 117, 118, 168, 169, 197, 198, 268, 336, 1108, 1113: Primary auth token for agent operations | **YES** | **CRITICAL** | ✅ Org secret |
| `CODEX_BACKUP_KEY` | Lines 118, 169, 198, 268, 336, 1113: Fallback auth token | **YES** | **CRITICAL** | ✅ Org secret |
| `GITHUB_TOKEN` | Line 170, fallback in token chains: Default workflow token | Auto-provided | N/A | ✅ Auto-injected |

### ⚠️ MISSING VARIABLES - IMMEDIATE ACTION REQUIRED

The following variables are **referenced in copilot-setup-steps.yml but NOT present in the current inventory**. Maintainer must create these NOW:

1. **`CODEX_MAX_HEALER_RUNS_PER_HOUR`**
   - **Purpose**: Rate limit for autonomous CI healer to prevent runaway healing loops
   - **Recommended value**: `3`
   - **Add at**: [Repository Variables](https://github.com/Aries-Serpent/_codex_/settings/variables/actions)

2. **`CODEX_SWEEP_SKIP_MAIN`**
   - **Purpose**: Boolean flag to skip main branch in automated sweep operations
   - **Recommended value**: `true`
   - **Add at**: [Repository Variables](https://github.com/Aries-Serpent/_codex_/settings/variables/actions)

3. **`CODEX_HEALER_SKIP_SKIPCI`**
   - **Purpose**: Boolean flag to skip commits marked `[skip ci]` in healer operations
   - **Recommended value**: `true`
   - **Add at**: [Repository Variables](https://github.com/Aries-Serpent/_codex_/settings/variables/actions)

4. **`COPILOT_AGENT_STATE`**
   - **Purpose**: Current agent state tracking (idle/active/blocked)
   - **Recommended value**: `idle`
   - **Add at**: [Repository Variables](https://github.com/Aries-Serpent/_codex_/settings/variables/actions)

---

### 0) Open required pages first (direct URLs)

1. Repository settings home: https://github.com/Aries-Serpent/_codex_/settings
2. Repository **Actions Variables**: https://github.com/Aries-Serpent/_codex_/settings/variables/actions
3. Repository **Actions Secrets**: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
4. Repository **Agents Variables**: https://github.com/Aries-Serpent/_codex_/settings/variables/agents
5. Repository **Agents Secrets**: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents
6. Repository **Environments list**: https://github.com/Aries-Serpent/_codex_/settings/environments
7. Environment page (`Aries_Serpent_codex_`): https://github.com/Aries-Serpent/_codex_/settings/environments/Aries_Serpent_codex_
8. Organization **Actions Variables**: https://github.com/organizations/Aries-Serpent/settings/variables/actions
9. Organization **Actions Secrets**: https://github.com/organizations/Aries-Serpent/settings/secrets/actions

### 0.5) ✅ Single-Source Copy/Paste Packs (Variables + Secrets)

Use this section as the **single maintainer execution source** for manual entry.

#### A) Pass-2 Missing Variables — validated expected values (ready to enter)

| Variable | Expected Value (ready for entry) | Why this value |
|---|---|---|
| `AGENT_HANDOFF_TIMEOUT_SECONDS` | `120` | Matches current runtime sync context and handoff baseline |
| `AUTONOMOUS_ACTIONS_ENABLED` | `true` | Current governance state in master guide |
| `AUTO_PROMOTE_TIER_ENABLED` | `true` | Current CI promotion setting in master guide |
| `CODEX_BACKUP_KEY_EXPIRY_DATE` | `2026-08-06` | Token-expiry monitor documented baseline date |
| `CODEX_CLI_API_URL` | `http://localhost:8765` | Current CLI API endpoint in master guide |
| `CODEX_GROUNDED_TIER1_COUNT` | `0` | Safe counter initialization for grounded telemetry |
| `CODEX_GROUNDED_TIER2_COUNT` | `0` | Safe counter initialization for grounded telemetry |
| `CODEX_LAST_TELEMETRY_DATE` | `2026-06-04` | ISO date seed for telemetry freshness tracking |
| `CODEX_MASTER_KEY_EXPIRY_DATE` | `2026-08-06` | Token-expiry monitor documented baseline date |
| `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | `90` | Current retention setting in master guide |
| `COGNITIVE_BRAIN_MEMORY_TIER` | `both` | Current cognitive memory tier in master guide |
| `COPILOT_AGENT_LAST_SESSION_ID` | `bootstrap-pending` | Placeholder until session workflows write active ID |
| `COPILOT_AGENT_SESSION_EXPIRES` | `1970-01-01T00:00:00Z` | Safe bootstrap placeholder until delegation workflow sets live expiry |
| `COPILOT_CLI_BASE_URL` | `http://localhost:8765` | Current Copilot CLI endpoint in master guide |
| `COPILOT_CLI_ENABLED` | `true` | Current Copilot CLI enablement in master guide |
| `COPILOT_SESSION_TTL_SECONDS` | `43200` | Delegation workflow default (12h) |
| `DEPLOY_ENV` | `development` | Repository deployment baseline |
| `EMBEDDING_INDEX_AUTO_REBUILD` | `true` | Current CI rebuild behavior in master guide |
| `WEBHOOK_RECEIVER_URL` | `https://<codespace-name>-8765.app.github.dev/webhook/github` | Canonical auto-set webhook receiver format |

#### B) Copy/Paste block — Repository Variables (Actions)

Paste these into: https://github.com/Aries-Serpent/_codex_/settings/variables/actions

```bash
CODEX_MAX_HEALER_RUNS_PER_HOUR=3
CODEX_SWEEP_SKIP_MAIN=true
CODEX_HEALER_SKIP_SKIPCI=true
COPILOT_AGENT_STATE=idle
AGENT_HANDOFF_TIMEOUT_SECONDS=120
AUTONOMOUS_ACTIONS_ENABLED=true
AUTO_PROMOTE_TIER_ENABLED=true
CODEX_BACKUP_KEY_EXPIRY_DATE=2026-08-06
CODEX_CLI_API_URL=http://localhost:8765
CODEX_GROUNDED_TIER1_COUNT=0
CODEX_GROUNDED_TIER2_COUNT=0
CODEX_LAST_TELEMETRY_DATE=2026-06-04
CODEX_MASTER_KEY_EXPIRY_DATE=2026-08-06
COGNITIVE_BRAIN_LTM_RETENTION_DAYS=90
COGNITIVE_BRAIN_MEMORY_TIER=both
COPILOT_AGENT_LAST_SESSION_ID=bootstrap-pending
COPILOT_AGENT_SESSION_EXPIRES=1970-01-01T00:00:00Z
COPILOT_CLI_BASE_URL=http://localhost:8765
COPILOT_CLI_ENABLED=true
COPILOT_SESSION_TTL_SECONDS=43200
DEPLOY_ENV=development
EMBEDDING_INDEX_AUTO_REBUILD=true
WEBHOOK_RECEIVER_URL=https://<codespace-name>-8765.app.github.dev/webhook/github
```

#### C) Copy/Paste block — Repository Secrets (Actions)

Paste names/values into: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions

```bash
OPENAI_API_KEY=<paste-secret>
CODEX_WEBHOOK_SECRET=<paste-secret>
_CODEX_BOT_RUNNER=<paste-secret>
CODEX_REPO_ID=928754154
CODEX_GHP_TOKEN_BASE64=<paste-secret>
CODEX_GHP_TOKEN_HEX=<paste-secret>
CODEX_GHP_TOKEN_SHA256=<paste-secret>
```

#### D) Copy/Paste block — Environment Secrets (`Aries_Serpent_codex_`)

Paste into: https://github.com/Aries-Serpent/_codex_/settings/environments/Aries_Serpent_codex_

```bash
CODEX_ENVIRONMENT_RUNNER=<paste-secret>
CODEX_RUNNER_SHA256=<paste-secret>
CODEX_RUNNER_TOKEN=<paste-secret>
```

#### E) Copy/Paste block — Organization Secrets

Paste into: https://github.com/organizations/Aries-Serpent/settings/secrets/actions
(then grant access to `Aries-Serpent/_codex_`)

```bash
CODEX_MASTER_KEY=<paste-secret>
CODEX_BACKUP_KEY=<paste-secret>
CODEX_ADMIN_KEY=<paste-secret>
_GITHUB_APP_PRIVATE_KEY=<paste-secret>
_GITHUB_APP_ID=<paste-secret>
_GITHUB_APP_INSTALLATION_ID=<paste-secret>
_GITHUB_APP_CLIENT_SECRET=<paste-secret>
RAG_OPENAI_KEY=<paste-secret>
HF_TOKEN=<paste-secret>
NPM_TOKEN=<paste-secret>
PYPI_TOKEN=<paste-secret>
CODECOV_TOKEN=<paste-secret>
_CODEX_ACTION_RUNNER=<paste-secret>
```

#### F) Copy/Paste block — Agents Variables + Secrets

- Agents Variables: https://github.com/Aries-Serpent/_codex_/settings/variables/agents
- Agents Secrets: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents

```bash
# Agents Variables (minimum must-have mirror set)
COPILOT_AGENT_MAX_AUTONOMY_LEVEL=D
COPILOT_AGENT_AUTH_ENABLED=true
COPILOT_AGENT_SESSION_RESTORE_ENABLED=true
COPILOT_AGENT_FIREWALL_ENABLED=true
COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS=<copy-from-repo-variable>
COPILOT_AGENT_PREFLIGHT_RULES=<copy-json-from-repo-variable>
COPILOT_WEC_SELECTION_MATRIX=<copy-json-from-repo-variable>

# Agents Secrets (minimum)
CODEX_MASTER_KEY=<link-org-secret>
CODEX_BACKUP_KEY=<link-org-secret>
OPENAI_API_KEY=<link-repo-secret>
```

---

### 1) Repository Variables (`/settings/variables/actions`)

**Direct URL**: https://github.com/Aries-Serpent/_codex_/settings/variables/actions

Click path: **Settings** → **Secrets and variables** → **Actions** → **Variables** → **New repository variable**.

#### ⚠️ CRITICAL: Add Missing Variables First

Before updating existing variables, **create these 4 MISSING variables** that are required by `copilot-setup-steps.yml`:

1. **`CODEX_MAX_HEALER_RUNS_PER_HOUR`**
   - Value: `3`
   - Click **New repository variable** → Name: `CODEX_MAX_HEALER_RUNS_PER_HOUR` → Value: `3` → **Add variable**

2. **`CODEX_SWEEP_SKIP_MAIN`**
   - Value: `true`
   - Click **New repository variable** → Name: `CODEX_SWEEP_SKIP_MAIN` → Value: `true` → **Add variable**

3. **`CODEX_HEALER_SKIP_SKIPCI`**
   - Value: `true`
   - Click **New repository variable** → Name: `CODEX_HEALER_SKIP_SKIPCI` → Value: `true` → **Add variable**

4. **`COPILOT_AGENT_STATE`**
   - Value: `idle`
   - Click **New repository variable** → Name: `COPILOT_AGENT_STATE` → Value: `idle` → **Add variable**

#### Update/Verify Existing Variables

Update these from latest inventory (automated variables updated by workflows):
- `CODEX_CI_FAILURE_RATE` (automated - verify current)
- `CODEX_CI_LAST_GREEN_SHA` (automated - verify current)
- `COGNITIVE_BRAIN_SESSION_NUMBER` (automated - verify current)
- `COPILOT_ACTIVE_SESSION` (automated - verify current)
- `COPILOT_AGENT_PREFLIGHT_RULES` (JSON - verify freshness)
- `COPILOT_WEC_SELECTION_MATRIX` (JSON - verify freshness)
- `COPILOT_WEC_TEMPLATE_DRIFT` (JSON - should show `count=0` after recent fixes)
- `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` (large allowlist - review and prune)
- `COPILOT_RUNNER_PROFILE` (verify: `ubuntu-latest-m` or leave unset for `ubuntu-latest` fallback)
- `CODEX_CACHE_VERSION` (verify: `v2`)

For each variable:
1. Click **New repository variable** (or click existing variable name to update).
2. Paste **Name**.
3. Paste **Value** from your source-of-truth export/current runtime policy.
4. Click **Add variable** (or **Update variable**).
5. Repeat until all listed items exist and are current.

#### Complete Repository Variables List (76 total)

**All 76 repository variables from the inventory should be present**. See [Complete Inventory Tables](#-complete-inventory-tables) section below for the full list.

### 2) Repository Secrets (`/settings/secrets/actions`)

**Direct URL**: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions

Click path: **Settings** → **Secrets and variables** → **Actions** → **Secrets** → **New repository secret**.

#### Step-by-Step Instructions

1. **Navigate** to https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
2. For each secret below, click **New repository secret** (or click existing secret name to update)

#### MUST-HAVE Repository Secrets (Priority: CRITICAL)

1. **`OPENAI_API_KEY`** ⭐ **CRITICAL**
   - Click **New repository secret**
   - Name: `OPENAI_API_KEY`
   - Secret: *(paste your OpenAI API key starting with `sk-proj-` or `sk-`)*
   - Click **Add secret**
   - Purpose: Required for LLM-powered features (RAG, embeddings, cognitive brain operations)

#### SHOULD-HAVE Repository Secrets (Priority: HIGH)

2. **`CODEX_WEBHOOK_SECRET`**
   - Click **New repository secret**
   - Name: `CODEX_WEBHOOK_SECRET`
   - Secret: *(generate with `openssl rand -hex 32` or similar)*
   - Click **Add secret**
   - Purpose: Validates incoming webhook payloads

3. **`_CODEX_BOT_RUNNER`**
   - Click **New repository secret**
   - Name: `_CODEX_BOT_RUNNER`
   - Secret: *(GitHub personal access token with `repo`, `workflow` scopes - or GitHub App installation token)*
   - Click **Add secret**
   - Purpose: Bot runner authentication token

4. **`CODEX_REPO_ID`**
   - Click **New repository secret**
   - Name: `CODEX_REPO_ID`
   - Secret: `928754154` *(your actual numeric repository ID; find via `gh api repos/Aries-Serpent/_codex_ --jq .id`)*
   - Click **Add secret**
   - Purpose: Used for API calls requiring numeric repo ID

#### MAY-HAVE Repository Secrets (Priority: OPTIONAL)

5. **`CODEX_GHP_TOKEN_BASE64`**
   - Click **New repository secret**
   - Name: `CODEX_GHP_TOKEN_BASE64`
   - Secret: *(base64-encoded GitHub personal access token for legacy workflows)*
   - Click **Add secret**
   - Purpose: Legacy encoding format - use only if specific workflows require it

6. **`CODEX_GHP_TOKEN_HEX`**
   - Click **New repository secret**
   - Name: `CODEX_GHP_TOKEN_HEX`
   - Secret: *(hex-encoded GitHub personal access token)*
   - Click **Add secret**
   - Purpose: Legacy encoding format - use only if specific workflows require it

7. **`CODEX_GHP_TOKEN_SHA256`**
   - Click **New repository secret**
   - Name: `CODEX_GHP_TOKEN_SHA256`
   - Secret: *(SHA256 hash of GitHub personal access token for verification workflows)*
   - Click **Add secret**
   - Purpose: Token verification in security-sensitive operations

#### Secret Rotation Policy

- **OPENAI_API_KEY**: Rotate every 90 days or immediately if compromised
- **CODEX_WEBHOOK_SECRET**: Rotate every 180 days
- **_CODEX_BOT_RUNNER**: Rotate every 90 days or when PAT expires
- **CODEX_REPO_ID**: Static - only update if repository is transferred
- **Encoded tokens**: Rotate when underlying token rotates

**Total Repository Secrets to Configure**: 7 (1 MUST + 3 SHOULD + 3 MAY optional)

---

### 3) Environment Variables + Secrets (`Aries_Serpent_codex_`)

**Direct URL**: https://github.com/Aries-Serpent/_codex_/settings/environments

Click path: **Settings** → **Environments** → **Aries_Serpent_codex_** (or create environment first if it doesn't exist).

#### Create Environment (if not exists)

1. Navigate to: https://github.com/Aries-Serpent/_codex_/settings/environments
2. If **Aries_Serpent_codex_** is not listed:
   - Click **New environment**
   - Name: `Aries_Serpent_codex_`
   - Click **Configure environment**
3. If it exists, click **Aries_Serpent_codex_** to open configuration

#### Environment Variables

Once inside the environment, scroll to **Environment variables** section:

1. **`CODEX_ENV_NODE_VERSION`**
   - Click **Add variable**
   - Name: `CODEX_ENV_NODE_VERSION`
   - Value: `22` *(or approved current LTS - check https://nodejs.org for latest LTS)*
   - Click **Add variable**

2. **`CODEX_ENV_PYTHON_VERSION`**
   - Click **Add variable**
   - Name: `CODEX_ENV_PYTHON_VERSION`
   - Value: `3.12` *(must match `pyproject.toml` requires-python)*
   - Click **Add variable**

3. **`CODEX_ENV_RUST_VERSION`**
   - Click **Add variable**
   - Name: `CODEX_ENV_RUST_VERSION`
   - Value: `1.92` *(or current stable from https://www.rust-lang.org)*
   - Click **Add variable**

4. **`CODEX_ENV_GO_VERSION`**
   - Click **Add variable**
   - Name: `CODEX_ENV_GO_VERSION`
   - Value: `1.21` *(or current stable from https://go.dev/dl)*
   - Click **Add variable**

5. **`CODEX_ENV_SWIFT_VERSION`**
   - Click **Add variable**
   - Name: `CODEX_ENV_SWIFT_VERSION`
   - Value: `5.9`
   - Click **Add variable**

6. **`CODEX_DB_PATH`**
   - Click **Add variable**
   - Name: `CODEX_DB_PATH`
   - Value: `.codex/logs.db`
   - Click **Add variable**
   - Note: `copilot-setup-steps.yml` overrides this to `.codex/session_logs.db` at runtime for Copilot sessions

7. **`CODEX_LOG_DB_PATH`**
   - Click **Add variable**
   - Name: `CODEX_LOG_DB_PATH`
   - Value: `.codex/logs.db`
   - Click **Add variable**

8. **`CODEX_SQLITE_POOL`**
   - Click **Add variable**
   - Name: `CODEX_SQLITE_POOL`
   - Value: `1`
   - Click **Add variable**

9. **`RUST_BACKTRACE`**
   - Click **Add variable**
   - Name: `RUST_BACKTRACE`
   - Value: `1`
   - Click **Add variable**

10. **`RUST_TEST_THREADS`**
    - Click **Add variable**
    - Name: `RUST_TEST_THREADS`
    - Value: `1`
    - Click **Add variable**

11. **`CARGO_TERM_COLOR`**
    - Click **Add variable**
    - Name: `CARGO_TERM_COLOR`
    - Value: `always`
    - Click **Add variable**

12. **`CODEX_BRIDGE_DIR`**
    - Click **Add variable**
    - Name: `CODEX_BRIDGE_DIR`
    - Value: `/tmp/codex_secure_bridge`
    - Click **Add variable**

13. **`CODEX_BRIDGE_OWNER_ONLY`**
    - Click **Add variable**
    - Name: `CODEX_BRIDGE_OWNER_ONLY`
    - Value: `true`
    - Click **Add variable**

**Total Environment Variables to Create**: 13

#### Environment Secrets

Scroll to **Environment secrets** section:

1. **`CODEX_ENVIRONMENT_RUNNER`**
   - Click **Add secret**
   - Name: `CODEX_ENVIRONMENT_RUNNER`
   - Secret: *(GitHub PAT with `repo` scope for environment-scoped workflows)*
   - Click **Add secret**

2. **`CODEX_RUNNER_SHA256`**
   - Click **Add secret**
   - Name: `CODEX_RUNNER_SHA256`
   - Secret: *(SHA256 hash of `CODEX_ENVIRONMENT_RUNNER` token for verification)*
   - Click **Add secret**

3. **`CODEX_RUNNER_TOKEN`**
   - Click **Add secret**
   - Name: `CODEX_RUNNER_TOKEN`
   - Secret: *(GitHub PAT or App token for runner operations)*
   - Click **Add secret**

**Total Environment Secrets to Create**: 3

#### Secret Rotation Schedule
- **CODEX_ENVIRONMENT_RUNNER**: Rotate every 90 days
- **CODEX_RUNNER_TOKEN**: Rotate every 90 days
- **CODEX_RUNNER_SHA256**: Update when `CODEX_ENVIRONMENT_RUNNER` rotates

---

### 4) Organization Variables (`/organizations/.../settings/variables/actions`)

**Direct URL**: https://github.com/organizations/Aries-Serpent/settings/variables/actions

Click path: **Org Settings** → **Secrets and variables** → **Actions** → **Variables** → **New organization variable**.

⚠️ **Note**: This section requires **organization owner** or **admin** privileges.

#### Step-by-Step Instructions

1. **Navigate** to https://github.com/organizations/Aries-Serpent/settings/variables/actions
2. **Verify repository access** for each existing organization variable
3. **Create new** organization variables if needed (currently all variables are repository-scoped in this codebase)

#### Current Status

As of the latest inventory (2026-06-03), **no organization-level variables** are configured for this repository. All variables are repository-scoped.

If you need to convert repository variables to organization-wide variables (to share across multiple repos):
1. Click **New organization variable**
2. Name: *(copy from repository variable)*
3. Value: *(copy from repository variable)*
4. Repository access: Select **Selected repositories** → Search `_codex_` → Select → **Add**
5. Click **Add variable**
6. Then delete the duplicate repository variable after confirming workflow compatibility

**Total Organization Variables to Create**: 0 (currently none; all are repo-scoped)

---

### 5) Organization Secrets (`/organizations/.../settings/secrets/actions`)

**Direct URL**: https://github.com/organizations/Aries-Serpent/settings/secrets/actions

Click path: **Org Settings** → **Secrets and variables** → **Actions** → **Secrets** → **New organization secret**.

⚠️ **Note**: This section requires **organization owner** or **admin** privileges.

#### Step-by-Step Instructions

1. **Navigate** to https://github.com/organizations/Aries-Serpent/settings/secrets/actions
2. For each secret below, click **New organization secret** (or click existing secret name to update)
3. **CRITICAL**: After creating/updating each secret, ensure repository access is granted to `Aries-Serpent/_codex_`

#### MUST-HAVE Organization Secrets (Priority: CRITICAL)

1. **`CODEX_MASTER_KEY`** ⭐ **CRITICAL - TOP PRIORITY**
   - Click **New organization secret** (or update existing)
   - Name: `CODEX_MASTER_KEY`
   - Secret: *(GitHub App installation token or PAT with `repo`, `workflow`, `admin:org`, `read:packages`, `write:packages` scopes)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: Primary authentication token for all critical operations - used in token fallback chain

2. **`CODEX_BACKUP_KEY`** ⭐ **CRITICAL**
   - Click **New organization secret** (or update existing)
   - Name: `CODEX_BACKUP_KEY`
   - Secret: *(Secondary GitHub App installation token or PAT with same scopes as CODEX_MASTER_KEY)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: Fallback authentication token when CODEX_MASTER_KEY fails

3. **`CODEX_ADMIN_KEY`**
   - Click **New organization secret** (or update existing)
   - Name: `CODEX_ADMIN_KEY`
   - Secret: *(GitHub PAT with admin-level scopes for sensitive operations)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: Administrative token for elevated privilege operations

#### SHOULD-HAVE Organization Secrets (Priority: HIGH)

4. **`_GITHUB_APP_PRIVATE_KEY`**
   - Click **New organization secret** (or update existing)
   - Name: `_GITHUB_APP_PRIVATE_KEY`
   - Secret: *(PEM-formatted private key from your GitHub App settings)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: Required for GitHub App JWT signing and installation token generation

5. **`_GITHUB_APP_ID`**
   - Click **New organization secret** (or update existing)
   - Name: `_GITHUB_APP_ID`
   - Secret: *(Numeric App ID from GitHub App settings, e.g., `123456`)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: GitHub App identifier

6. **`_GITHUB_APP_INSTALLATION_ID`**
   - Click **New organization secret** (or update existing)
   - Name: `_GITHUB_APP_INSTALLATION_ID`
   - Secret: *(Numeric installation ID for this org, find at https://github.com/organizations/Aries-Serpent/settings/installations)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: Links App to this organization installation

7. **`_GITHUB_APP_CLIENT_SECRET`**
   - Click **New organization secret** (or update existing)
   - Name: `_GITHUB_APP_CLIENT_SECRET`
   - Secret: *(Client secret from GitHub App OAuth settings)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: OAuth client secret for App authentication flows

#### MAY-HAVE Organization Secrets (Priority: OPTIONAL)

8. **`RAG_OPENAI_KEY`**
   - Click **New organization secret** (or update existing)
   - Name: `RAG_OPENAI_KEY`
   - Secret: *(OpenAI API key dedicated to RAG operations, starting with `sk-proj-` or `sk-`)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: Dedicated OpenAI key for RAG/embedding operations (isolated from main OPENAI_API_KEY)

9. **`HF_TOKEN`**
   - Click **New organization secret** (or update existing)
   - Name: `HF_TOKEN`
   - Secret: *(Hugging Face user access token from https://huggingface.co/settings/tokens)*
   - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
   - Click **Add secret** (or **Update secret**)
   - Purpose: Access gated models and private datasets on Hugging Face

10. **`PYPI_TOKEN`**
    - Click **New organization secret** (or update existing)
    - Name: `PYPI_TOKEN`
    - Secret: *(PyPI API token from https://pypi.org/manage/account/token/, starting with `pypi-`)*
    - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
    - Click **Add secret** (or **Update secret**)
    - Purpose: Publish Python packages to PyPI

11. **`NPM_TOKEN`**
    - Click **New organization secret** (or update existing)
    - Name: `NPM_TOKEN`
    - Secret: *(npm access token from https://www.npmjs.com/settings/*/tokens)*
    - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
    - Click **Add secret** (or **Update secret**)
    - Purpose: Publish Node.js packages to npm registry

12. **`CODECOV_TOKEN`**
    - Click **New organization secret** (or update existing)
    - Name: `CODECOV_TOKEN`
    - Secret: *(Codecov upload token from https://codecov.io/gh/Aries-Serpent/_codex_/settings)*
    - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
    - Click **Add secret** (or **Update secret**)
    - Purpose: Upload coverage reports to Codecov

13. **`_CODEX_ACTION_RUNNER`**
    - Click **New organization secret** (or update existing)
    - Name: `_CODEX_ACTION_RUNNER`
    - Secret: *(GitHub PAT for action runner operations)*
    - Repository access: **Selected repositories** → Search `_codex_` → Select → **Update selection**
    - Click **Add secret** (or **Update secret**)
    - Purpose: Runner-specific authentication token

#### Secret Rotation Policy

- **CODEX_MASTER_KEY**: Rotate every 90 days or when App token expires
- **CODEX_BACKUP_KEY**: Rotate every 90 days (offset by 45 days from MASTER_KEY)
- **CODEX_ADMIN_KEY**: Rotate every 60 days
- **_GITHUB_APP_PRIVATE_KEY**: Rotate every 365 days or if compromised
- **_GITHUB_APP_***: Update only when App configuration changes
- **RAG_OPENAI_KEY / OPENAI_API_KEY**: Rotate every 90 days
- **HF_TOKEN, PYPI_TOKEN, NPM_TOKEN, CODECOV_TOKEN**: Rotate every 180 days
- **_CODEX_ACTION_RUNNER**: Rotate every 90 days

**Total Organization Secrets to Configure**: 13 (3 MUST + 4 SHOULD + 6 MAY optional)

---
- `_GITHUB_APP_CLIENT_SECRET`
- `HF_TOKEN`
- `NPM_TOKEN`
- `PYPI_TOKEN`
- `_CODEX_ACTION_RUNNER`
- `CODECOV_TOKEN`

For each org secret:
1. Click secret name (or **New organization secret**).
2. Set/rotate value.
3. In **Repository access**, choose **Selected repositories** (or policy you require).
4. Ensure `Aries-Serpent/_codex_` is selected.
5. Save.

### 6) Agents Variables (`/settings/variables/agents`)

**Direct URL**: https://github.com/Aries-Serpent/_codex_/settings/variables/agents

Click path: **Settings** → **Secrets and variables** → **Copilot** (or **Agents**) → **Variables** → **New variable**.

#### Step-by-Step Instructions

1. **Navigate** to https://github.com/Aries-Serpent/_codex_/settings/variables/agents
2. Click the **Copilot** or **Agents** tab in the left sidebar under "Secrets and variables"
3. Click the **Variables** sub-tab
4. For each variable below, click **New variable**

#### MUST-HAVE Agent Variables (Priority: CRITICAL)

Create these variables one by one. Click **New variable** for each:

1. **`COPILOT_AGENT_MAX_AUTONOMY_LEVEL`**
   - Name: `COPILOT_AGENT_MAX_AUTONOMY_LEVEL`
   - Value: `D`
   - Click **Add variable**
   - Purpose: Governs maximum autonomy level for coding agent operations

2. **`COPILOT_AGENT_AUTH_ENABLED`**
   - Name: `COPILOT_AGENT_AUTH_ENABLED`
   - Value: `true`
   - Click **Add variable**
   - Purpose: Enforces authentication-gated write operations

3. **`COPILOT_AGENT_SESSION_RESTORE_ENABLED`**
   - Name: `COPILOT_AGENT_SESSION_RESTORE_ENABLED`
   - Value: `true`
   - Click **Add variable**
   - Purpose: Enables context and session restore capabilities

4. **`COPILOT_AGENT_FIREWALL_ENABLED`**
   - Name: `COPILOT_AGENT_FIREWALL_ENABLED`
   - Value: `true`
   - Click **Add variable**
   - Purpose: Enforces network boundary controls for agent operations

5. **`COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS`**
   - Name: `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS`
   - Value: *(copy current value from Repository Variables at https://github.com/Aries-Serpent/_codex_/settings/variables/actions)*
   - Click **Add variable**
   - Purpose: Network allowlist must be synchronized between Actions and Agents settings

6. **`COPILOT_AGENT_PREFLIGHT_RULES`**
   - Name: `COPILOT_AGENT_PREFLIGHT_RULES`
   - Value: *(copy current JSON value from Repository Variables)*
   - Click **Add variable**
   - Purpose: Mandatory preflight, token, and WEC rules for agent governance

7. **`COPILOT_WEC_SELECTION_MATRIX`**
   - Name: `COPILOT_WEC_SELECTION_MATRIX`
   - Value: *(copy current JSON value from Repository Variables)*
   - Click **Add variable**
   - Purpose: Required for WEC workflow selection logic

#### SHOULD-HAVE Agent Variables (Priority: HIGH)

8. **`COPILOT_WEC_TEMPLATE_DRIFT`**
   - Name: `COPILOT_WEC_TEMPLATE_DRIFT`
   - Value: *(copy current JSON from Repository Variables - should show `count=0` after recent fixes)*
   - Click **Add variable**

9. **`COPILOT_SESSION_TOOL_CAPABILITIES`**
   - Name: `COPILOT_SESSION_TOOL_CAPABILITIES`
   - Value: *(copy current JSON from Repository Variables)*
   - Click **Add variable**

10. **`COGNITIVE_BRAIN_INJECTION_ENABLED`**
    - Name: `COGNITIVE_BRAIN_INJECTION_ENABLED`
    - Value: `true`
    - Click **Add variable**

11. **`COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS`**
    - Name: `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS`
    - Value: `128000`
    - Click **Add variable**

12. **`COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE`**
    - Name: `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE`
    - Value: `0.75`
    - Click **Add variable**

13. **`COGNITIVE_BRAIN_ALLOWED_ACTORS`**
    - Name: `COGNITIVE_BRAIN_ALLOWED_ACTORS`
    - Value: `mbaetiong,github-actions[bot],copilot-swe-agent[bot],github-copilot[bot]`
    - Click **Add variable**

14. **`CODEX_COVERAGE_THRESHOLD`**
    - Name: `CODEX_COVERAGE_THRESHOLD`
    - Value: `80`
    - Click **Add variable**

15. **`CODEX_LINT_STRICT`**
    - Name: `CODEX_LINT_STRICT`
    - Value: `true`
    - Click **Add variable**

16. **`CODEX_CI_FAILURE_THRESHOLD`**
    - Name: `CODEX_CI_FAILURE_THRESHOLD`
    - Value: `10.0`
    - Click **Add variable**

17. **`CODEX_PYTHON_VERSION`**
    - Name: `CODEX_PYTHON_VERSION`
    - Value: `3.12`
    - Click **Add variable**

#### MAY-HAVE Agent Variables (Priority: OPTIONAL)

18. **`CODEX_LOG_LEVEL`**
    - Name: `CODEX_LOG_LEVEL`
    - Value: `INFO`
    - Click **Add variable**

**Total Agent Variables to Create**: 18 minimum (7 MUST + 11 SHOULD + 1 MAY optional)

---

### 7) Agents Secrets (`/settings/secrets/agents`)

**Direct URL**: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents

Click path: **Settings** → **Secrets and variables** → **Copilot** (or **Agents**) → **Secrets** → **New secret**.

#### Step-by-Step Instructions

1. **Navigate** to https://github.com/Aries-Serpent/_codex_/settings/secrets/agents
2. Click the **Copilot** or **Agents** tab in the left sidebar under "Secrets and variables"
3. Click the **Secrets** sub-tab
4. For each secret below, click **New secret**

⚠️ **IMPORTANT**: Most Agent Secrets are **organization secrets** that need to be **granted access** to the Copilot/Agents scope for this repository. You do NOT re-create them here - you **grant repository access** from the organization settings.

#### MUST-HAVE Agent Secrets (Priority: CRITICAL)

**These are Organization Secrets - Grant Access:**

1. **`CODEX_MASTER_KEY`** ⭐ **CRITICAL**
   - Navigate to: https://github.com/organizations/Aries-Serpent/settings/secrets/actions
   - Find `CODEX_MASTER_KEY` in the list
   - Click on it
   - Scroll to **Repository access** section
   - Click **Update selection** (if not already visible)
   - Ensure **"Selected repositories"** is chosen
   - Search for and select `Aries-Serpent/_codex_`
   - Click **Save**
   - **THEN** return to: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents
   - Click **New secret** → Name: `CODEX_MASTER_KEY` → **Add secret from organization secrets** → Select `CODEX_MASTER_KEY` → **Add secret**

2. **`CODEX_BACKUP_KEY`** ⭐ **CRITICAL**
   - Same process as CODEX_MASTER_KEY:
   - Navigate to org secrets, ensure repo access, then add to Agents secrets
   - Purpose: Fallback authentication token in the token chain

#### SHOULD-HAVE Agent Secrets (Priority: HIGH)

**Grant access for these Organization Secrets:**

3. **`CODEX_ADMIN_KEY`**
   - Organization secret - grant access to this repo
   - Add to Agents secrets scope

4. **`_GITHUB_APP_ID`**
   - Organization secret - grant access
   - Required for GitHub App authentication bundle

5. **`_GITHUB_APP_INSTALLATION_ID`**
   - Organization secret - grant access
   - Required for GitHub App installation token flow

6. **`_GITHUB_APP_PRIVATE_KEY`**
   - Organization secret - grant access
   - Required for JWT signing in App auth

7. **`_GITHUB_APP_CLIENT_SECRET`**
   - Organization secret - grant access
   - Required for OAuth/App client secret operations

**Repository Secrets to Add to Agents Scope:**

8. **`OPENAI_API_KEY`**
   - This is a **repository secret** (not org secret)
   - Navigate to: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
   - Note the current value indicator
   - **Then** at https://github.com/Aries-Serpent/_codex_/settings/secrets/agents:
   - Click **New secret** → Name: `OPENAI_API_KEY` → **Add from repository secrets** or **Create new**
   - If creating new, paste the same value used in Actions secrets
   - Click **Add secret**

#### MAY-HAVE Agent Secrets (Priority: OPTIONAL)

9. **`RAG_OPENAI_KEY`**
   - Organization secret - grant access if RAG operations needed

10. **`CODEX_WEBHOOK_SECRET`**
    - Repository secret - add to Agents scope if webhook-managing agent flows are used

11. **`_CODEX_BOT_RUNNER`**
    - Repository secret - add to Agents scope only for runner-management tasks

#### Verification

After adding all secrets, verify at https://github.com/Aries-Serpent/_codex_/settings/secrets/agents that you see:
- At minimum: `CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY`, `OPENAI_API_KEY`
- Ideally all 11 secrets listed above

**Total Agent Secrets to Configure**: 11 (2 MUST + 7 SHOULD + 2 MAY optional)

---

### 8) Post-Setup Validation: Verify copilot-setup-steps.yml Works

**Direct URL**: https://github.com/Aries-Serpent/_codex_/actions/workflows/copilot-setup-steps.yml

Click path: **Actions** → **Copilot Setup Steps** → **Run workflow** dropdown → **Run workflow**.

#### Validation Checklist

After completing all above sections, validate the configuration:

1. **Manual Trigger Test**:
   - Navigate to: https://github.com/Aries-Serpent/_codex_/actions/workflows/copilot-setup-steps.yml
   - Click **Run workflow** dropdown
   - Select branch: `main` (or current working branch)
   - Click **Run workflow** button
   - Wait for the workflow to complete (~2-5 minutes)

2. **Check workflow logs** for these success indicators:
   - ✅ `Environment profile set to: ubuntu-latest-m` (or `ubuntu-latest` if `COPILOT_RUNNER_PROFILE` not set)
   - ✅ `Installing system packages...` completes without errors
   - ✅ `Setting up Python 3.12...` completes
   - ✅ `Injecting CODEX_MASTER_KEY into session environment` (confirms secret available)
   - ✅ `Injecting CODEX_BACKUP_KEY into session environment` (confirms backup secret available)
   - ✅ `Loading Copilot session context...` (confirms agent variable access)
   - ✅ All steps show green checkmarks

3. **Verify no error messages** related to:
   - Missing variables (e.g., `vars.COPILOT_AGENT_STATE is undefined`)
   - Missing secrets (e.g., `secrets.CODEX_MASTER_KEY is empty`)
   - Permission errors (e.g., `403 Forbidden` or `Resource not accessible`)

4. **Expected Warnings** (these are OK):
   - `COPILOT_RUNNER_PROFILE not set, defaulting to ubuntu-latest` (if you didn't set this variable)
   - `GPU_OPT not set` (expected in CPU-only runners)

5. **If workflow fails**:
   - Click on the failed job → expand failed step
   - Check error message:
     - If `variable not found` → go back to section 1 or 6 and create the missing variable
     - If `secret not found` → go back to section 2, 3, 4, 5, or 7 and add the missing secret
     - If `permission denied` → check organization secret repository access grants
   - Fix the issue, then re-run the workflow

6. **Success Criteria**:
   - ✅ Workflow shows **green checkmark** overall
   - ✅ All setup steps completed
   - ✅ No missing variable/secret errors in logs
   - ✅ Agent environment loaded successfully

7. **UI Verification**:
   - Re-open each of the 7 URLs above (sections 1-7) and confirm all required names are present
   - Return to this file and update top timestamp block, counts in summary table, completion status in checklists

---

## 📊 Complete Inventory Tables

> This copy preserves the 2026-06-03 inventory baseline and is updated to the latest **variables-only** snapshot: **90 variables total** (14 environment + 76 repository). Secrets were not rotated/modified in this pass.

### Environment Variables (Aries_Serpent_codex_ Environment)

| Category | Count | Source Snapshot |
|---|---:|---|
| Environment Variables | 14 | 2026-06-03 variables refresh |

#### Maintainer Add/Update Notes — Environment Variables

| Item | Expected Action | Target Value / Rule | Reason |
|---|---|---|---|
| `CODEX_ENV_NODE_VERSION` | **UPDATE** (if stale) | `22` (or approved current LTS) | Current docs indicate `22`; prior inventory showed `18`. Keep aligned with workflow/runtime expectations. |
| `CODEX_ENV_PYTHON_VERSION` | VERIFY | `3.12` | Must stay aligned with `pyproject.toml` (`requires-python >=3.12`). |
| `CODEX_DB_PATH` and `CODEX_LOG_DB_PATH` | VERIFY | `CODEX_DB_PATH=.codex/session_logs.db`; `CODEX_LOG_DB_PATH=.codex/session_logs.db` | Keep the configured defaults aligned for logging tools, while noting that `copilot-setup-steps.yml` currently exports a runtime-only `CODEX_DB_PATH=${GITHUB_WORKSPACE}/.codex/codex.db` override inside Copilot sessions. |
| `RUST_TEST_THREADS` | VERIFY | `1` | Deterministic Rust test behavior in CI/sandbox. |

---

### Repository Variables

| Category | Count | Source Snapshot |
|---|---:|---|
| Repository Variables | 76 | 2026-06-03 variables refresh |

#### Maintainer Add/Update Notes — Repository Variables

| Item | Expected Action | Target Value / Rule | Reason |
|---|---|---|---|
| `CODEX_CI_FAILURE_RATE` | UPDATE (automated) | `<float>:<status>` | Confirm CI monitor keeps this fresh (currently very recent). |
| `CODEX_CI_LAST_GREEN_SHA` | UPDATE (automated) | valid git SHA | Must track latest all-green commit for triage decisions. |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | UPDATE (automated) | incrementing integer | Must increment per session lifecycle. |
| `COPILOT_ACTIVE_SESSION` | UPDATE (automated) | current session tuple | Must reflect active session state. |
| `COPILOT_AGENT_PREFLIGHT_RULES` | VERIFY JSON freshness | version/date + mandatory rules | Critical governance source for agent operations. |
| `COPILOT_WEC_SELECTION_MATRIX` | VERIFY JSON freshness | workflow mapping current to repo reality | Prevent WEC drift and checklist mismatch. |
| `COPILOT_WEC_TEMPLATE_DRIFT` | VERIFY + SYNC | `count=0` template mapping gaps (normalized `auto-approve-workflows.yml` → `auto-approve-workflows`) | Drift was remediated in `_WEC_ITEMS`; keep the repo variable and agent settings copy aligned to the current zero-drift state. |
| `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` | REVIEW/PRUNE/UPDATE | approved domains only | Large allowlist should be periodically pruned and normalized. |
| `COPILOT_RUNNER_PROFILE` | VERIFY | unset or valid runner label; workflow fallback is `ubuntu-latest` | `copilot-setup-steps.yml` reads this variable for larger-runner overrides, but now falls back safely to `ubuntu-latest` when the variable is absent. |

---

### Environment Secrets (Aries_Serpent_codex_ Environment)

| Category | Count | Source Snapshot |
|---|---:|---|
| Environment Secrets | 3 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Environment Secrets

| Secret | Expected Action | Rotation / Rule | Reason |
|---|---|---|---|
| `CODEX_ENVIRONMENT_RUNNER` | ROTATE/VERIFY | 90-day cadence | Environment runner auth hardening. |
| `CODEX_RUNNER_SHA256` | UPDATE on runner change | must match active runner binary | Integrity verification for runner payload. |
| `CODEX_RUNNER_TOKEN` | ROTATE | 90-day cadence or on exposure | Limit long-lived runner token risk. |

---

### Repository Secrets

| Category | Count | Source Snapshot |
|---|---:|---|
| Repository Secrets | 7 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Repository Secrets

| Secret | Expected Action | Rotation / Rule | Reason |
|---|---|---|---|
| `OPENAI_API_KEY` | ROTATE/VERIFY | 90-day cadence | LLM runtime secret hygiene. |
| `CODEX_WEBHOOK_SECRET` | ROTATE/VERIFY | on webhook infra change or 90-day | Protect webhook signature validation. |
| `_CODEX_BOT_RUNNER` | ROTATE/VERIFY | 90-day cadence | Bot runner token should not remain static. |
| `CODEX_GHP_TOKEN_BASE64` / `CODEX_GHP_TOKEN_HEX` | REVIEW necessity | keep one preferred encoding path | Reduce duplicate token encodings unless required for compatibility. |
| `CODEX_REPO_ID` | VERIFY | numeric repo ID current | Keep internal ID references consistent. |

---

### Organization Secrets

| Category | Count | Source Snapshot |
|---|---:|---|
| Organization Secrets | 13 | 2026-06-03T17:39:00Z |

#### Maintainer Add/Update Notes — Organization Secrets

| Secret | Expected Action | Rotation / Rule | Reason |
|---|---|---|---|
| `CODEX_MASTER_KEY` | **ROTATE/VERIFY PRIORITY** | 90-day cadence | Primary write token in auth chain. |
| `CODEX_BACKUP_KEY` | ROTATE/VERIFY | 90-day cadence | Fallback write token; must remain valid. |
| `CODEX_ADMIN_KEY` | ROTATE/VERIFY | 90-day cadence | Elevated operations token. |
| `_GITHUB_APP_PRIVATE_KEY` | ROTATE/VERIFY | app key rotation policy | Required for GitHub App JWT auth. |
| `_GITHUB_APP_CLIENT_SECRET` | ROTATE/VERIFY | app secret rotation policy | OAuth/App exchange integrity. |
| `HF_TOKEN`, `NPM_TOKEN`, `PYPI_TOKEN`, `_CODEX_ACTION_RUNNER`, `CODECOV_TOKEN` | REVIEW AGE + ROTATE as needed | follow provider policy | Aging secrets should be refreshed on schedule. |

---

## 🤖 Maintainer Required Additions — Agent Variables and Secrets

> Target UI for variables: https://github.com/Aries-Serpent/_codex_/settings/variables/agents  
> Target UI for secrets: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents

### Agent Variables (Copilot Agent Settings)

| Variable Name | Expected Value / Source | Action | Priority | Notes |
|---|---|---|---|---|
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | `D` | ADD/VERIFY | MUST | Governs max autonomy for coding agent. |
| `COPILOT_AGENT_AUTH_ENABLED` | `true` | ADD/VERIFY | MUST | Enforces auth-gated writes. |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `true` | ADD/VERIFY | MUST | Enables context/session restore. |
| `COPILOT_AGENT_FIREWALL_ENABLED` | `true` | ADD/VERIFY | MUST | Enforces network boundary controls. |
| `COPILOT_AGENT_FIREWALL_ALLOW_LIST_ADDITIONS` | repo-var current value | ADD/SYNC | MUST | Keep agent allowlist aligned with repo policy. |
| `COPILOT_AGENT_PREFLIGHT_RULES` | repo-var JSON | ADD/SYNC | MUST | Mandatory preflight, token, and WEC rules. |
| `COPILOT_WEC_SELECTION_MATRIX` | repo-var JSON | ADD/SYNC | MUST | Required for WEC workflow selection logic. |
| `COPILOT_WEC_TEMPLATE_DRIFT` | repo-var JSON | ADD/SYNC | SHOULD | Keeps agent aware of known template drift. |
| `COPILOT_SESSION_TOOL_CAPABILITIES` | repo-var JSON | ADD/SYNC | SHOULD | Agent capability map for guarded behavior. |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `true` | ADD/VERIFY | SHOULD | Enables cognitive brain injection controls. |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | `128000` | ADD/VERIFY | SHOULD | Context budget awareness for agents. |
| `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | `0.75` | ADD/VERIFY | SHOULD | Pattern injection threshold consistency. |
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `mbaetiong,github-actions[bot],copilot-swe-agent[bot],github-copilot[bot]` | ADD/SYNC | SHOULD | Restricts who can update memory/session context. |
| `CODEX_COVERAGE_THRESHOLD` | `80` | ADD/VERIFY | SHOULD | Useful for agent remediation decisions. |
| `CODEX_LINT_STRICT` | `true` | ADD/VERIFY | SHOULD | Keeps agent behavior aligned with strict lint policy. |
| `CODEX_CI_FAILURE_THRESHOLD` | `10.0` | ADD/VERIFY | SHOULD | Supports CI health triage logic. |
| `CODEX_PYTHON_VERSION` | `3.12` | ADD/VERIFY | SHOULD | Keeps agent runtime assumptions aligned. |
| `CODEX_LOG_LEVEL` | `INFO` | ADD/VERIFY | MAY | Optional but useful for consistent diagnostics. |

### Agent Secrets (Copilot Agent Settings)

| Secret Name | Source of Truth | Action | Priority | Notes |
|---|---|---|---|---|
| `CODEX_MASTER_KEY` | Org secret | ADD/GRANT/VERIFY | MUST | Primary write/auth token for agent operations. |
| `CODEX_BACKUP_KEY` | Org secret | ADD/GRANT/VERIFY | MUST | Required fallback in token chain. |
| `CODEX_ADMIN_KEY` | Org secret | ADD/GRANT/VERIFY | SHOULD | Needed for elevated admin workflows. |
| `OPENAI_API_KEY` | Repo secret | ADD/GRANT/VERIFY | SHOULD | Needed for LLM-backed tasks where applicable. |
| `RAG_OPENAI_KEY` | Org secret | ADD/GRANT/VERIFY | MAY | Needed for RAG-specific agent operations. |
| `CODEX_WEBHOOK_SECRET` | Repo secret | ADD/GRANT/VERIFY | MAY | Needed only for webhook-managing agent flows. |
| `_GITHUB_APP_ID` | Org secret | ADD/GRANT/VERIFY | SHOULD | GitHub App auth bundle member. |
| `_GITHUB_APP_INSTALLATION_ID` | Org secret | ADD/GRANT/VERIFY | SHOULD | GitHub App installation token flow. |
| `_GITHUB_APP_PRIVATE_KEY` | Org secret | ADD/GRANT/VERIFY | SHOULD | JWT signing for App auth. |
| `_GITHUB_APP_CLIENT_SECRET` | Org secret | ADD/GRANT/VERIFY | SHOULD | OAuth/App client secret requirements. |
| `_CODEX_BOT_RUNNER` | Repo secret | ADD/GRANT/VERIFY | MAY | Needed only for runner-management tasks. |

---

## 📈 Summary Statistics

| Category | Count |
|----------|-------|
| **Environment Variables** | 14 |
| **Repository Variables** | 76 |
| **Environment Secrets** | 3 |
| **Repository Secrets** | 7 |
| **Organization Secrets** | 13 |
| **TOTAL** | **113** |

---

## 🧠 Key Observations

### Most Recently Updated (from source snapshot)
- `CODEX_CI_FAILURE_RATE`
- `CODEX_CI_LAST_GREEN_SHA` (`8b5588da25a5d5f12ba8bd66cc37fa688fbc8e97`)
- `COGNITIVE_BRAIN_ALLOWED_ACTORS`
- `COGNITIVE_BRAIN_SESSION_NUMBER`
- `COPILOT_ACTIVE_SESSION`
- `COPILOT_AGENT_AUTH_ENABLED`

### Oldest Items Requiring Rotation/Audit Attention
- `AUDIT_RETENTION_DAYS` (stale policy review)
- `CODEX_AGENT_NAME`, `CODEX_API_VERSION`, `CODEX_NETWORK_MODE` (long-lived static config; verify intentional)
- Aged org secrets: `CODECOV_TOKEN`, `HF_TOKEN`, `NPM_TOKEN`, `PYPI_TOKEN`, `_CODEX_ACTION_RUNNER`

---

## 🔗 Quick Reference URLs (All-in-One)

Copy this section for fast access to all GitHub settings pages:

### Repository Settings
- **Repository Variables (Actions)**: https://github.com/Aries-Serpent/_codex_/settings/variables/actions
- **Repository Secrets (Actions)**: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
- **Agents Variables**: https://github.com/Aries-Serpent/_codex_/settings/variables/agents
- **Agents Secrets**: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents
- **Environments**: https://github.com/Aries-Serpent/_codex_/settings/environments
- **Environment `Aries_Serpent_codex_`**: https://github.com/Aries-Serpent/_codex_/settings/environments/Aries_Serpent_codex_

### Organization Settings (requires org owner/admin)
- **Organization Variables (Actions)**: https://github.com/organizations/Aries-Serpent/settings/variables/actions
- **Organization Secrets (Actions)**: https://github.com/organizations/Aries-Serpent/settings/secrets/actions
- **GitHub App Installations**: https://github.com/organizations/Aries-Serpent/settings/installations

### Workflow & Validation
- **Copilot Setup Steps Workflow**: https://github.com/Aries-Serpent/_codex_/actions/workflows/copilot-setup-steps.yml
- **All Actions Workflows**: https://github.com/Aries-Serpent/_codex_/actions
- **Recent Workflow Runs**: https://github.com/Aries-Serpent/_codex_/actions

### External Services (for secret/token generation)
- **OpenAI API Keys**: https://platform.openai.com/api-keys
- **Hugging Face Tokens**: https://huggingface.co/settings/tokens
- **PyPI Tokens**: https://pypi.org/manage/account/token/
- **npm Tokens**: https://www.npmjs.com/settings/*/tokens *(replace `*` with your npm username)*
- **Codecov Settings**: https://codecov.io/gh/Aries-Serpent/_codex_/settings
- **GitHub Personal Access Tokens**: https://github.com/settings/tokens
- **GitHub Apps**: https://github.com/settings/apps

---

## ▶️ What's Next (Post Variables-Only Pass)

- [ ] Execute **secrets pass** (repo/env/org) and refresh secret ages/rotation status. _(Blocked in-session by `403 Resource not accessible by integration`; requires elevated token/API scope.)_
- [x] Resolve `COPILOT_WEC_TEMPLATE_DRIFT` by adding the missing workflows to `_WEC_ITEMS` in `scripts/ci/session_wrapup_autofix.py` (`e-to-d-transition-gate.yml`, `d-capable-promotion-gate.yml`, `mcp-health.yml`).
- [ ] Re-run inventory export and replace all “placeholder JSON” references with the current exact values where required. _(Blocked in-session by the same API authorization limits.)_
- [ ] Reconcile `settings/variables/agents` against repo variables to ensure no drift between Actions Variables and Agents Variables pages. _(Blocked until repo/environment/org variable APIs are readable in-session.)_
- [ ] After secrets pass, regenerate summary totals and update this file’s timestamp block. _(Partially updated in this commit; full totals refresh pending successful secrets pass.)_

---

## ✅ Maintainer Execution Checklist

Use this checklist to systematically configure all secrets and variables:

### Phase 1: Critical Repository Setup (MUST DO FIRST)
- [ ] **1.1**: Create 4 MISSING repository variables (see section 1):
  - [ ] `CODEX_MAX_HEALER_RUNS_PER_HOUR` = `3`
  - [ ] `CODEX_SWEEP_SKIP_MAIN` = `true`
  - [ ] `CODEX_HEALER_SKIP_SKIPCI` = `true`
  - [ ] `COPILOT_AGENT_STATE` = `idle`
- [ ] **1.2**: Update repository variables with current values (see section 1 complete table)
- [ ] **1.3**: Create/rotate repository secrets (see section 2):
  - [ ] `OPENAI_API_KEY` ⭐ CRITICAL
  - [ ] `CODEX_WEBHOOK_SECRET`
  - [ ] `_CODEX_BOT_RUNNER`
  - [ ] `CODEX_REPO_ID`

### Phase 2: Environment Configuration
- [ ] **2.1**: Create or verify `Aries_Serpent_codex_` environment exists
- [ ] **2.2**: Add all 13 environment variables (see section 3)
- [ ] **2.3**: Add all 3 environment secrets (see section 3)

### Phase 3: Organization Secrets (Requires Org Owner/Admin)
- [ ] **3.1**: Create/verify organization secrets (see section 5):
  - [ ] `CODEX_MASTER_KEY` ⭐ TOP PRIORITY
  - [ ] `CODEX_BACKUP_KEY` ⭐ CRITICAL
  - [ ] `CODEX_ADMIN_KEY`
  - [ ] `_GITHUB_APP_PRIVATE_KEY`
  - [ ] `_GITHUB_APP_ID`
  - [ ] `_GITHUB_APP_INSTALLATION_ID`
  - [ ] `_GITHUB_APP_CLIENT_SECRET`
- [ ] **3.2**: Verify repository access for ALL org secrets includes `Aries-Serpent/_codex_`

### Phase 4: Agents Configuration (Copilot/Agents Scope)
- [ ] **4.1**: Create 18 Agents Variables (see section 6):
  - [ ] 7 MUST-HAVE variables
  - [ ] 11 SHOULD-HAVE variables
- [ ] **4.2**: Grant access to 11 Agents Secrets (see section 7):
  - [ ] 2 MUST-HAVE: `CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY`
  - [ ] 7 SHOULD-HAVE: GitHub App bundle + `OPENAI_API_KEY`
  - [ ] 2 MAY-HAVE: `RAG_OPENAI_KEY`, `CODEX_WEBHOOK_SECRET`

### Phase 5: Validation
- [ ] **5.1**: Manual workflow trigger test (see section 8)
  - Navigate to: https://github.com/Aries-Serpent/_codex_/actions/workflows/copilot-setup-steps.yml
  - Click **Run workflow** → Select `main` → **Run workflow**
  - Wait for completion (~2-5 minutes)
  - Verify green checkmark and no missing variable/secret errors
- [ ] **5.2**: Check all 7 settings URLs and verify all required names present:
  - [ ] Repository Variables: https://github.com/Aries-Serpent/_codex_/settings/variables/actions
  - [ ] Repository Secrets: https://github.com/Aries-Serpent/_codex_/settings/secrets/actions
  - [ ] Environment Variables/Secrets: https://github.com/Aries-Serpent/_codex_/settings/environments/Aries_Serpent_codex_
  - [ ] Organization Secrets: https://github.com/organizations/Aries-Serpent/settings/secrets/actions
  - [ ] Agents Variables: https://github.com/Aries-Serpent/_codex_/settings/variables/agents
  - [ ] Agents Secrets: https://github.com/Aries-Serpent/_codex_/settings/secrets/agents

### Phase 6: Post-Setup
- [ ] **6.1**: Document completion timestamp in this file
- [ ] **6.2**: Create GitHub issue tracking rotation schedule
- [ ] **6.3**: Set calendar reminders for secret rotations (90-day intervals for critical secrets)
- [ ] **6.4**: Link verification issue/PR in this file

---

## 📅 Secret Rotation Schedule Template

Copy this template to your issue tracker or calendar:

```
SECRET ROTATION SCHEDULE (2026-06-04 baseline)

CRITICAL (Every 90 days):
- 2026-09-02: Rotate CODEX_MASTER_KEY, CODEX_BACKUP_KEY, OPENAI_API_KEY
- 2026-12-01: Rotate CODEX_MASTER_KEY, CODEX_BACKUP_KEY, OPENAI_API_KEY
- 2027-03-01: Rotate CODEX_MASTER_KEY, CODEX_BACKUP_KEY, OPENAI_API_KEY

HIGH (Every 180 days):
- 2026-12-01: Rotate CODEX_WEBHOOK_SECRET, HF_TOKEN, PYPI_TOKEN, NPM_TOKEN, CODECOV_TOKEN

ANNUAL:
- 2027-06-04: Rotate _GITHUB_APP_PRIVATE_KEY (if not compromised earlier)
```

---
