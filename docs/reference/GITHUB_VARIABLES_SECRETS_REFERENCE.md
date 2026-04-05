# Reference: GitHub Variables & Secrets — All Scopes, All Methods

> **Generated:** 2026-04-05 | **Author:** mbaetiong | **Verified against upstream:** 2026-04-05  
> **Sources:** [Actions Secrets](https://docs.github.com/en/rest/actions/secrets) · [Actions Variables](https://docs.github.com/en/rest/actions/variables) · [Dependabot Secrets](https://docs.github.com/en/rest/dependabot/secrets) · [Codespaces Secrets](https://docs.github.com/en/rest/codespaces/secrets) · [GitHub CLI](https://cli.github.com/manual/) · [MCP Server](https://github.com/github/github-mcp-server)  
> **Wired for:** GitHub Copilot Coding Agent, Cognitive Brain CB connector, `wec_enforcer.py`, `agent-auth-delegation.yml`

---

## Scope Coverage Matrix

| Scope | Variables | Secrets | Dependabot Secrets | Codespaces Secrets |
|---|---|---|---|---|
| **Repository** | ✅ | ✅ | ✅ | ✅ |
| **Organization** | ✅ | ✅ | ✅ | ✅ |
| **Environment** | ✅ | ✅ | ✗ | ✗ |
| **User (Codespaces)** | ✗ | ✅ | ✗ | ✅ |

---

## 1. REST API

> Requires PAT with `repo`, `admin:org`, or `codespace` scopes as appropriate.  
> **Secrets** require sodium-sealed encryption before PUT — fetch the public key first:  
> `GET /repos/{owner}/{repo}/actions/secrets/public-key`  
> **API version header:** `X-GitHub-Api-Version: 2026-03-10`

### 1a. Repository Scope

#### Variables

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/repos/{owner}/{repo}/actions/variables` |
| Get | `GET` | `/repos/{owner}/{repo}/actions/variables/{name}` |
| Create | `POST` | `/repos/{owner}/{repo}/actions/variables` |
| Update | `PATCH` | `/repos/{owner}/{repo}/actions/variables/{name}` |
| Delete | `DELETE` | `/repos/{owner}/{repo}/actions/variables/{name}` |

#### Secrets (Actions)

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/repos/{owner}/{repo}/actions/secrets` |
| Get | `GET` | `/repos/{owner}/{repo}/actions/secrets/{secret_name}` |
| Create / Update | `PUT` | `/repos/{owner}/{repo}/actions/secrets/{secret_name}` |
| Delete | `DELETE` | `/repos/{owner}/{repo}/actions/secrets/{secret_name}` |
| Get Public Key | `GET` | `/repos/{owner}/{repo}/actions/secrets/public-key` |

#### Secrets (Dependabot)

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/repos/{owner}/{repo}/dependabot/secrets` |
| Get | `GET` | `/repos/{owner}/{repo}/dependabot/secrets/{secret_name}` |
| Create / Update | `PUT` | `/repos/{owner}/{repo}/dependabot/secrets/{secret_name}` |
| Delete | `DELETE` | `/repos/{owner}/{repo}/dependabot/secrets/{secret_name}` |
| Get Public Key | `GET` | `/repos/{owner}/{repo}/dependabot/secrets/public-key` |

#### Secrets (Codespaces)

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/repos/{owner}/{repo}/codespaces/secrets` |
| Get | `GET` | `/repos/{owner}/{repo}/codespaces/secrets/{secret_name}` |
| Create / Update | `PUT` | `/repos/{owner}/{repo}/codespaces/secrets/{secret_name}` |
| Delete | `DELETE` | `/repos/{owner}/{repo}/codespaces/secrets/{secret_name}` |
| Get Public Key | `GET` | `/repos/{owner}/{repo}/codespaces/secrets/public-key` |

---

### 1b. Organization Scope

#### Variables

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/orgs/{org}/actions/variables` |
| Get | `GET` | `/orgs/{org}/actions/variables/{name}` |
| Create | `POST` | `/orgs/{org}/actions/variables` |
| Update | `PATCH` | `/orgs/{org}/actions/variables/{name}` |
| Delete | `DELETE` | `/orgs/{org}/actions/variables/{name}` |
| List selected repos | `GET` | `/orgs/{org}/actions/variables/{name}/repositories` |
| Set selected repos | `PUT` | `/orgs/{org}/actions/variables/{name}/repositories` |

#### Secrets (Actions)

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/orgs/{org}/actions/secrets` |
| Get | `GET` | `/orgs/{org}/actions/secrets/{secret_name}` |
| Create / Update | `PUT` | `/orgs/{org}/actions/secrets/{secret_name}` |
| Delete | `DELETE` | `/orgs/{org}/actions/secrets/{secret_name}` |
| Get Public Key | `GET` | `/orgs/{org}/actions/secrets/public-key` |
| List selected repos | `GET` | `/orgs/{org}/actions/secrets/{secret_name}/repositories` |
| Set selected repos | `PUT` | `/orgs/{org}/actions/secrets/{secret_name}/repositories` |
| Add repo to secret | `PUT` | `/orgs/{org}/actions/secrets/{secret_name}/repositories/{repository_id}` |
| Remove repo from secret | `DELETE` | `/orgs/{org}/actions/secrets/{secret_name}/repositories/{repository_id}` |

#### Secrets (Dependabot)

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/orgs/{org}/dependabot/secrets` |
| Get | `GET` | `/orgs/{org}/dependabot/secrets/{secret_name}` |
| Create / Update | `PUT` | `/orgs/{org}/dependabot/secrets/{secret_name}` |
| Delete | `DELETE` | `/orgs/{org}/dependabot/secrets/{secret_name}` |
| Get Public Key | `GET` | `/orgs/{org}/dependabot/secrets/public-key` |
| List selected repos | `GET` | `/orgs/{org}/dependabot/secrets/{secret_name}/repositories` |
| Set selected repos | `PUT` | `/orgs/{org}/dependabot/secrets/{secret_name}/repositories` |

#### Secrets (Codespaces)

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/orgs/{org}/codespaces/secrets` |
| Get | `GET` | `/orgs/{org}/codespaces/secrets/{secret_name}` |
| Create / Update | `PUT` | `/orgs/{org}/codespaces/secrets/{secret_name}` |
| Delete | `DELETE` | `/orgs/{org}/codespaces/secrets/{secret_name}` |
| Get Public Key | `GET` | `/orgs/{org}/codespaces/secrets/public-key` |
| List selected repos | `GET` | `/orgs/{org}/codespaces/secrets/{secret_name}/repositories` |
| Set selected repos | `PUT` | `/orgs/{org}/codespaces/secrets/{secret_name}/repositories` |

---

### 1c. Environment Scope

> Uses `repository_id` (numeric), not `owner/repo`.  
> Get `repository_id`: `gh repo view OWNER/REPO --json databaseId --jq '.databaseId'`

#### Variables

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/repositories/{repository_id}/environments/{environment_name}/variables` |
| Get | `GET` | `/repositories/{repository_id}/environments/{environment_name}/variables/{name}` |
| Create | `POST` | `/repositories/{repository_id}/environments/{environment_name}/variables` |
| Update | `PATCH` | `/repositories/{repository_id}/environments/{environment_name}/variables/{name}` |
| Delete | `DELETE` | `/repositories/{repository_id}/environments/{environment_name}/variables/{name}` |

#### Secrets

| Operation | Method | Endpoint |
|---|---|---|
| List | `GET` | `/repositories/{repository_id}/environments/{environment_name}/secrets` |
| Get | `GET` | `/repositories/{repository_id}/environments/{environment_name}/secrets/{secret_name}` |
| Create / Update | `PUT` | `/repositories/{repository_id}/environments/{environment_name}/secrets/{secret_name}` |
| Delete | `DELETE` | `/repositories/{repository_id}/environments/{environment_name}/secrets/{secret_name}` |
| Get Public Key | `GET` | `/repositories/{repository_id}/environments/{environment_name}/secrets/public-key` |

---

### 1d. User Scope (Codespaces only)

| Operation | Method | Endpoint |
|---|---|---|
| List user secrets | `GET` | `/user/codespaces/secrets` |
| Get user secret | `GET` | `/user/codespaces/secrets/{secret_name}` |
| Create / Update user secret | `PUT` | `/user/codespaces/secrets/{secret_name}` |
| Delete user secret | `DELETE` | `/user/codespaces/secrets/{secret_name}` |
| Get public key | `GET` | `/user/codespaces/secrets/public-key` |
| List selected repos | `GET` | `/user/codespaces/secrets/{secret_name}/repositories` |
| Set selected repos | `PUT` | `/user/codespaces/secrets/{secret_name}/repositories` |

---

### 1e. Canonical curl Patterns

```bash
# Read a repo variable (CODEX_MASTER_KEY token)
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $CODEX_MASTER_KEY" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables/COPILOT_AGENT_STATE

# Create / update a repo variable
curl -L -X PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $CODEX_MASTER_KEY" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables/COPILOT_AGENT_STATE \
  -d '{"name":"COPILOT_AGENT_STATE","value":"ACTIVE"}'

# Get public key (required before encrypting secrets)
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $CODEX_MASTER_KEY" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  https://api.github.com/repos/Aries-Serpent/_codex_/actions/secrets/public-key
```

---

## 2. GitHub CLI (`gh`)

> Docs: `gh secret set --help` / `gh variable set --help`  
> Install: <https://cli.github.com>  
> Auth: `gh auth login` or set `GITHUB_TOKEN` / `GH_TOKEN` env var

### 2a. Secrets

```bash
# Repository secret (default when inside a repo)
gh secret set SECRET_NAME --repo OWNER/REPO
echo "value" | gh secret set SECRET_NAME --repo OWNER/REPO

# Organization secret
gh secret set SECRET_NAME --org MY_ORG
gh secret set SECRET_NAME --org MY_ORG --visibility all          # all repos
gh secret set SECRET_NAME --org MY_ORG --visibility private      # private repos only
gh secret set SECRET_NAME --org MY_ORG --repos "repo1,repo2"    # selected repos

# Environment secret
gh secret set SECRET_NAME --env ENVIRONMENT_NAME --repo OWNER/REPO

# Dependabot secret (repo)
gh secret set SECRET_NAME --dependabot --repo OWNER/REPO

# Dependabot secret (org)
gh secret set SECRET_NAME --dependabot --org MY_ORG

# Codespaces secret (org)
gh secret set SECRET_NAME --codespaces --org MY_ORG

# Codespaces secret (user)
gh secret set SECRET_NAME --codespaces --user

# List secrets
gh secret list --repo OWNER/REPO
gh secret list --org MY_ORG
gh secret list --env ENVIRONMENT_NAME --repo OWNER/REPO

# Delete
gh secret delete SECRET_NAME --repo OWNER/REPO
```

### 2b. Variables

```bash
# Repository variable
gh variable set VAR_NAME --repo OWNER/REPO
gh variable set VAR_NAME --body "value" --repo OWNER/REPO

# Organization variable
gh variable set VAR_NAME --org MY_ORG
gh variable set VAR_NAME --org MY_ORG --visibility all
gh variable set VAR_NAME --org MY_ORG --repos "repo1,repo2"

# Environment variable
gh variable set VAR_NAME --env ENVIRONMENT_NAME --repo OWNER/REPO

# List variables
gh variable list --repo OWNER/REPO
gh variable list --org MY_ORG
gh variable list --env ENVIRONMENT_NAME --repo OWNER/REPO

# Delete
gh variable delete VAR_NAME --repo OWNER/REPO
```

> ⚠️ **Note:** Codespaces and Dependabot scopes are **not** supported for `gh variable` — only for `gh secret`.

### 2c. Patterns Used in This Repository

```bash
# Read a repo variable (used in agent-auth-delegation.yml, copilot-agent-checkin.yml)
gh api /repos/Aries-Serpent/_codex_/actions/variables/COPILOT_AGENT_STATE --jq '.value'

# Write a repo variable (canonical pattern from GITHUB_API_COPILOT_AGENT_REFERENCE.md)
gh api PATCH /repos/Aries-Serpent/_codex_/actions/variables/COPILOT_AGENT_STATE \
  -f name='COPILOT_AGENT_STATE' \
  -f value='ACTIVE'

# Increment a counter variable (pattern from agent-auth-delegation.yml)
CURRENT=$(gh api /repos/$REPO/actions/variables/COGNITIVE_BRAIN_SESSION_NUMBER --jq '.value // "0"')
NEXT=$((CURRENT + 1))
gh api PATCH /repos/$REPO/actions/variables/COGNITIVE_BRAIN_SESSION_NUMBER \
  -f name='COGNITIVE_BRAIN_SESSION_NUMBER' \
  -f value="$NEXT"

# Cancel a workflow run (used in wec_enforcer.py --cancel-unchecked)
gh api POST /repos/$REPO/actions/runs/$RUN_ID/cancel

# Dispatch a workflow (used in wec_enforcer.py --dispatch-checked)
gh workflow run validate.yml --repo OWNER/REPO --ref BRANCH
```

---

## 3. GitHub MCP Server

> Official image: `ghcr.io/github/github-mcp-server`  
> Remote endpoint: `https://api.githubcopilot.com/mcp/`  
> Source: <https://github.com/github/github-mcp-server>  
> Config guide: <https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md>

### 3a. Available Toolsets

| Toolset | Covers | Default? |
|---|---|---|
| `context` | `get_me`, repo context | ✅ |
| `issues` | Create/update/read issues | ✅ |
| `pull_requests` | Create/update/read PRs, reviews, comments | ✅ |
| `repos` | File content, branches, commits, releases | ✅ |
| `users` | User lookup | ✅ |
| `actions` | Workflow runs, jobs, artifacts | ❌ opt-in |
| `secret_protection` | Secret scanning alerts (GHAS, read-only) | ❌ opt-in |
| `dependabot` | Dependabot alerts (read-only) | ❌ opt-in |
| `code_security` | Code scanning alerts (read-only) | ❌ opt-in |
| `discussions` | GitHub Discussions read/write | ❌ opt-in |
| `notifications` | Notification management | ❌ opt-in |

### 3b. ⚠️ Critical Gap — Secrets/Variables CRUD not available via MCP

As of 2026-04-05, the GitHub MCP Server does **not** include tools to create, update, or delete Actions variables, Actions secrets, Dependabot secrets, or Codespaces secrets. Use the REST API or `gh` CLI for write operations on secrets and variables.

| Operation | REST API | CLI (`gh`) | MCP Server |
|---|---|---|---|
| Repo Actions variable (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Repo Actions secret (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Org Actions variable (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Org Actions secret (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Environment variable (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Environment secret (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Dependabot secret (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Codespaces secret (CRUD) | ✅ Full | ✅ Full | ❌ Not supported |
| Secret scanning alerts (read) | ✅ | ✅ | ✅ (`secret_protection`) |
| Dependabot alerts (read) | ✅ | ✅ | ✅ (`dependabot`) |
| Workflow runs/jobs (read) | ✅ | ✅ | ✅ (`actions`) |
| PR comments (write) | ✅ | ✅ | ✅ (`pull_requests`) |

### 3c. MCP Server Configuration — Remote (VS Code / Copilot)

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

With specific toolsets:
```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "X-MCP-Toolsets": "repos,issues,pull_requests,actions,secret_protection"
      }
    }
  }
}
```

### 3d. MCP Server Configuration — Local (Docker)

```bash
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="$CODEX_MASTER_KEY" \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests,actions,secret_protection,dependabot" \
  ghcr.io/github/github-mcp-server
```

### 3e. MCP Configuration Options Reference

| Option | Remote (header) | Local (flag / env var) |
|---|---|---|
| Select toolsets | `X-MCP-Toolsets: issues,repos` | `--toolsets=issues,repos` / `GITHUB_TOOLSETS` |
| Select individual tools | `X-MCP-Tools: get_me,pull_request_read` | `--tools=...` / `GITHUB_TOOLS` |
| Exclude tools | `X-MCP-Exclude-Tools: merge_pull_request` | `--exclude-tools=...` / `GITHUB_EXCLUDE_TOOLS` |
| Read-only mode | `X-MCP-Readonly: true` | `--read-only` / `GITHUB_READ_ONLY` |
| Insiders mode | `X-MCP-Insiders: true` | `--insiders` / `GITHUB_INSIDERS` |
| Lockdown mode | `X-MCP-Lockdown: true` | `--lockdown-mode` / `GITHUB_LOCKDOWN_MODE` |
| Dynamic discovery | N/A | `--dynamic-toolsets` / `GITHUB_DYNAMIC_TOOLSETS` |

### 3f. This Repository's MCP Wiring

From `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` (verified 2026-04-05):

```
MCP aggregator :2301
  ├─ playwright  (npx @playwright/mcp@0.0.40)      → 21 tools
  └─ github-mcp-server (api.individual.githubcopilot.com/mcp/readonly) → 28 tools
```

> **Note:** The repo's live MCP connection uses the `/mcp/readonly` endpoint.  
> Write operations (posting comments, dispatching workflows, updating variables) must use  
> `CODEX_MASTER_KEY || CODEX_BACKUP_KEY` via direct REST API calls or `gh` CLI.

---

## 4. Required PAT Scopes by Operation

| Operation | Required Scope(s) |
|---|---|
| Repo Actions secrets (read/write) | `repo` |
| Repo Actions variables (read/write) | `repo` |
| Org Actions secrets (read/write) | `admin:org` |
| Org Actions variables (read/write) | `admin:org` |
| Environment secrets/variables | `repo` |
| Dependabot secrets (repo) | `repo` |
| Dependabot secrets (org) | `admin:org` |
| Codespaces secrets (user) | `codespace` |
| Codespaces secrets (org) | `admin:org` |
| Secret scanning alerts (read) | `security_events` or `repo` |
| Cancel workflow run | `repo` + `actions:write` |
| Dispatch workflow | `repo` + `actions:write` |

### Token Hierarchy for This Repository

| Priority | Token | Scopes | Use for |
|---|---|---|---|
| 1st | `secrets.CODEX_MASTER_KEY` | `repo` + `workflow` + `actions:write` | Variable writes, workflow dispatch/cancel, force-push |
| 2nd | `secrets.CODEX_BACKUP_KEY` | `repo` + `workflow` | Same as above when MASTER_KEY unavailable |
| 3rd | `github.token` | `contents:read`, `pull-requests:write` | Read-only ops, posting comments |

```yaml
# Canonical pattern — always use this token chain
env:
  GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
```

---

## 5. Encryption Pattern for Secrets (REST API)

Secrets must be encrypted with the repository or org public key using libsodium before PUT:

```python
import base64
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
from cryptography.hazmat.bindings._rust import openssl as rust_openssl

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    """Encrypt a secret value using the repo/org public key (libsodium sealed box)."""
    from nacl.public import PublicKey, SealedBox
    pk = PublicKey(base64.b64decode(public_key_b64))
    box = SealedBox(pk)
    encrypted = box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

# Then PUT: {"encrypted_value": encrypted, "key_id": key_id}
```

> In GitHub Actions workflows, use `gh secret set` instead — it handles encryption automatically.

---

## References

- [REST API: Actions Secrets](https://docs.github.com/en/rest/actions/secrets)
- [REST API: Actions Variables](https://docs.github.com/en/rest/actions/variables)
- [REST API: Dependabot Secrets](https://docs.github.com/en/rest/dependabot/secrets)
- [REST API: Codespaces Secrets](https://docs.github.com/en/rest/codespaces/secrets)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub MCP Server README](https://github.com/github/github-mcp-server/blob/main/README.md)
- [MCP Server Configuration](https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md)
- [This repo: GITHUB_API_COPILOT_AGENT_REFERENCE.md](docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md)
- [This repo: COPILOT_MCP_TOOL_REFERENCE.md](.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md)
