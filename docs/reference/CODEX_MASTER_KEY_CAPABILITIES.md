# CODEX_MASTER_KEY Capabilities Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.0

> **Generated:** 2026-06-29
> **Last Updated: 2026-06-29
> **Scope Count:** 23 total scopes
> **Processes:** 10 core workflows documented
> **Test Coverage:** 100% scope coverage with 50+ API operations

## Overview

The `CODEX_MASTER_KEY` is a GitHub Personal Access Token (PAT) with 23 OAuth scopes that governs critical repository automation, agent autonomy, and infrastructure management in the Aries-Serpent/_codex_ repository.

This document provides complete scope-to-operation mapping, per-process API endpoint reference, rate limit matrices, and token fallback hierarchy.

---

## Part 1: Complete Scope Authority (23 Scopes)

### Core Scopes (5)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `repo` | Full control of private repositories | Code CRUD, branch protection, commit creation, file updates, branch management |
| `workflow` | Update GitHub Actions workflows | Approve runs, cancel runs, dispatch workflows, modify workflow permissions |
| `admin:org` | Full control of organization resources | Manage teams, members, projects, org-level variables |
| `delete_repo` | Delete repositories | Repository deletion (dangerous, use with care) |
| `admin:repo_hook` | Full control of repository webhooks | Create, read, update, delete webhooks at repository level |

### Key Management Scopes (9)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `admin:public_key` | Full control of user public keys | Manage all user public keys |
| `write:public_key` | Write user public keys | Create, update user public keys |
| `read:public_key` | Read user public keys | List, retrieve user public keys |
| `admin:gpg_key` | Full control of public user GPG keys | Manage all GPG keys |
| `write:gpg_key` | Write public user GPG keys | Create, update GPG keys |
| `read:gpg_key` | Read public user GPG keys | List, retrieve GPG keys |
| `admin:ssh_signing_key` | Full control of public user SSH signing keys | Manage SSH signing keys |
| `write:ssh_signing_key` | Write public user SSH signing keys | Create, update SSH signing keys |
| `read:ssh_signing_key` | Read public user SSH signing keys | List, retrieve SSH signing keys |

### Organization Scopes (2)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `admin:org_hook` | Full control of organization hooks | Create, read, update, delete org webhooks |
| `manage_runners:org` | Manage organization runners and runner groups | Configure self-hosted runners for org |

### User & Collaboration Scopes (5)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `user` | Update ALL user data | Modify user profile, email, preferences |
| `read:user` | Read ALL user profile data | Access user information |
| `user:email` | Access user email addresses (read-only) | Retrieve user email |
| `notifications` | Access notifications | Read, modify GitHub notifications |
| `gist` | Create gists | Create, read, update, delete gists |

### Discussion & Team Scopes (2)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `write:discussion` | Read and write team discussions | Post, edit team discussions |
| `read:discussion` | Read team discussions | View team discussion content |

### Enterprise Scopes (3)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `admin:enterprise` | Full control of enterprises | Manage enterprise settings |
| `manage_runners:enterprise` | Manage enterprise runners and runner groups | Configure enterprise runners |
| `read:enterprise` | Read enterprise profile data | Access enterprise information |

### Package Registry Scopes (3)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `write:packages` | Upload packages to GitHub Package Registry | Publish npm, Docker, Maven, PyPI packages |
| `read:packages` | Download packages from GitHub Package Registry | Install/pull packages |
| `delete:packages` | Delete packages from GitHub Package Registry | Remove package versions |

### Audit & Security Scopes (2)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `audit_log` | Full control of audit log | Read and filter organization audit logs |
| `read:audit_log` | Read access of audit log | Access audit log entries |

### Codespace Scopes (2)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `codespace` | Full control of codespaces | Create, manage codespace instances |
| `codespace:secrets` | Ability to create, read, update, and delete codespace secrets | Manage codespace-level secrets |

### Network & Project Scopes (4)

| Scope | Permission | Operations |
|-------|-----------|-----------|
| `write:network_configurations` | Write org hosted compute network configurations | Modify network settings |
| `read:network_configurations` | Read org hosted compute network configurations | View network configuration |
| `project` | Full control of projects | Create, read, update, delete org/repo projects |
| `read:project` | Read access of projects | View project details |

---

## Part 2: Process Scope Mapping

### Process 1: Repository Variable Management (`repo` scope)

**Scope Required:** `repo`

**Operations:**
- `GET /repos/{owner}/{repo}/actions/variables` — List repo variables
- `GET /repos/{owner}/{repo}/actions/variables/{name}` — Get variable
- `POST /repos/{owner}/{repo}/actions/variables` — Create variable
- `PATCH /repos/{owner}/{repo}/actions/variables/{name}` — Update variable
- `DELETE /repos/{owner}/{repo}/actions/variables/{name}` — Delete variable
- `GET /orgs/{org}/actions/variables` — List org variables
- `POST /orgs/{org}/actions/variables` — Create org variable
- `GET /repos/{owner}/{repo}/environments/{env}/variables` — List env variables

**Current Usage:** 27+ variables tracked in `.codex/agent_context.json`

### Process 2: Workflow Approval & Dispatch (`workflow` scope)

**Scope Required:** `workflow`

**Operations:**
- `GET /repos/{owner}/{repo}/actions/runs` — List workflow runs
- `POST /repos/{owner}/{repo}/actions/runs/{run_id}/approve` — Approve run
- `POST /repos/{owner}/{repo}/actions/runs/{run_id}/cancel` — Cancel run
- `POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` — Dispatch workflow
- `GET /repos/{owner}/{repo}/actions/runs/{run_id}/timing` — Get run timing

**Critical Path:** Approving pending workflow runs

### Process 3: Secrets Management (`repo` scope for encryption)

**Scope Required:** `repo`

**Operations:**
- `GET /repos/{owner}/{repo}/actions/secrets/public-key` — Get public key for encryption
- `PUT /repos/{owner}/{repo}/actions/secrets/{name}` — Create/update secret (with encryption)
- `DELETE /repos/{owner}/{repo}/actions/secrets/{name}` — Delete secret
- `GET /repos/{owner}/{repo}/dependabot/secrets/public-key` — Dependabot public key
- `GET /repos/{owner}/{repo}/codespaces/secrets/public-key` — Codespaces public key

**Special Requirement:** Secrets must be encrypted with repository public key using Sodium sealing

### Process 4: Package Registry (`write:packages`, `read:packages`, `delete:packages` scopes)

**Scopes Required:** `write:packages`, `read:packages`, `delete:packages`

**Operations:**
- `GET /repos/{owner}/{repo}/packages` — List packages
- `GET /repos/{owner}/{repo}/packages/{package_id}` — Get package details
- `GET /repos/{owner}/{repo}/packages/{package_id}/versions` — List versions
- `DELETE /repos/{owner}/{repo}/packages/{package_id}/versions/{version_id}` — Delete version
- Package publishing via npm.pkg.github.com, ghcr.io, etc.

### Process 5: Organization Management (`admin:org`, `manage_runners:org` scopes)

**Scopes Required:** `admin:org`, `manage_runners:org`

**Operations:**
- `GET /orgs/{org}/teams` — List teams
- `POST /orgs/{org}/teams` — Create team
- `PATCH /orgs/{org}/teams/{team_slug}` — Update team
- `DELETE /orgs/{org}/teams/{team_slug}` — Delete team
- `GET /orgs/{org}/members` — List members
- `PUT /orgs/{org}/members/{username}` — Add member
- `DELETE /orgs/{org}/members/{username}` — Remove member

### Process 6: Repository Webhooks (`admin:repo_hook` scope)

**Scope Required:** `admin:repo_hook`

**Operations:**
- `GET /repos/{owner}/{repo}/hooks` — List webhooks
- `POST /repos/{owner}/{repo}/hooks` — Create webhook
- `PATCH /repos/{owner}/{repo}/hooks/{hook_id}` — Update webhook
- `DELETE /repos/{owner}/{repo}/hooks/{hook_id}` — Delete webhook

### Process 7: PR & Issue Operations (`repo` scope)

**Scope Required:** `repo`

**Operations:**
- `POST /repos/{owner}/{repo}/issues/{number}/comments` — Comment on PR/issue
- `PATCH /repos/{owner}/{repo}/pulls/{number}` — Update PR body
- `POST /repos/{owner}/{repo}/issues/{number}/labels` — Add labels
- `POST /repos/{owner}/{repo}/pulls/{number}/requested_reviewers` — Request review
- `PUT /repos/{owner}/{repo}/pulls/{number}/merge` — Merge PR

### Process 8: Security Management (`audit_log`, `read:audit_log` scopes)

**Scopes Required:** `audit_log` or `read:audit_log`

**Operations:**
- `GET /repos/{owner}/{repo}/code-scanning/alerts` — List CodeQL alerts
- `PATCH /repos/{owner}/{repo}/code-scanning/alerts/{number}` — Dismiss alert
- `GET /repos/{owner}/{repo}/secret-scanning/alerts` — List secret scanning alerts
- `GET /orgs/{org}/audit-log` — Access organization audit log

### Process 9: Token & Auth Management (`repo`, `admin:org` scopes)

**Scopes Required:** `repo`, `admin:org`

**Operations:**
- `GET /user` — Get authenticated user (verify token scopes)
- `GET /orgs/{org}/actions/permissions` — Get workflow permissions
- Token rotation, delegation, and lifecycle management
- Rate limit header inspection and management

### Process 10: Agent Autonomy Framework (All scopes coordinated)

**Scopes Required:** All 23 scopes (coordinated through token broker)

**Operations:**
- Token resolution hierarchy: MASTER BACKUP GH_TOKEN GITHUB_TOKEN
- Role-based access control: observer contributor admin
- Session-level token delegation
- Rate limit coordination across agents
- Concurrent authorization handling

---

## Part 3: Rate Limit Matrices

### Primary Rate Limits (CODEX_MASTER_KEY)

| Limit Type | Quota | Reset Period | Exception |
|-----------|-------|--------------|-----------|
| API Requests | 60 | 1 hour | Authenticated requests, higher tier |
| Search Queries | 30 | 1 minute | Separate rate limit |
| GraphQL Queries | Varies | 1 hour | Variable costs based on query |
| GitHub App Requests | 15,000 | 1 hour | For GitHub Apps with high rates |

### Secondary Rate Limits (Surge Limits)

| Condition | Behavior | Recovery |
|-----------|----------|----------|
| 1000+ requests/hour | 403 Forbidden | Wait until hour resets |
| Rapid sequential requests | 403 Forbidden | Exponential backoff recommended |
| Malformed requests | Immediate ban | 10-30 minute cooldown |

### Response Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1234567890 (Unix timestamp)
```

---

## Part 4: Token Fallback Hierarchy

```
Priority | Token | Scopes | When |
---------|-------|--------|------|
1st | CODEX_MASTER_KEY | repo + workflow + actions:write | Normal operations |
2nd | CODEX_BACKUP_KEY | repo + workflow | MASTER_KEY unavailable |
3rd | GH_TOKEN | Any configured scopes | Explicit override |
4th | GITHUB_TOKEN | Limited scopes | Fallback (likely insufficient) |
```

**Canonical Fallback Pattern:**
```yaml
env:
  GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
```

---

## Part 5: Error Response Reference

| Status | Error | Meaning | Resolution |
|--------|-------|---------|-----------|
| 401 | `Bad credentials` | Token missing, invalid, or expired | Refresh token, check expiration |
| 403 | `Resource not accessible by integration` | Insufficient scope | Verify token has required scope |
| 404 | `Not Found` | Resource doesn't exist | Verify resource ID and path |
| 409 | `Conflict` | Resource already exists or concurrent modification | Retry or update |
| 422 | `Validation Failed` | Invalid request format | Check payload structure |
| 429 | `API rate limit exceeded` | Rate limit hit | Implement backoff, wait for reset |

---

## Part 6: Best Practices

1. **Token Security:**
 - Never log token values
 - Rotate CODEX_MASTER_KEY quarterly
 - Keep CODEX_BACKUP_KEY in separate secure location

2. **Rate Limiting:**
 - Implement exponential backoff: 1s, 2s, 4s, 8s...
 - Monitor X-RateLimit-Remaining before operations
 - Batch operations when possible

3. **Error Handling:**
 - Retry transient errors (429, 5xx)
 - Escalate permission errors (403) to admin
 - Log all API errors for audit trail

4. **Scope Management:**
 - Use minimum required scopes for each operation
 - Document scope requirements for each script
 - Audit token scope usage periodically

---

## References

- Full REST API docs: [docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md](GITHUB_VARIABLES_SECRETS_REFERENCE.md)
- Testing guide: [docs/testing/CODEX_MASTER_KEY_TEST_GUIDE.md](../testing/CODEX_MASTER_KEY_TEST_GUIDE.md)
- Token API reference: [docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md](../ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md)
