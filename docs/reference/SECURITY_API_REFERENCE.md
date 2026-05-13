# Security API Reference — `Aries-Serpent/_codex_`

> **Audience:** Copilot Cloud / Coding Agents  
> **Purpose:** Canonical call-set for security-alert triage, CodeQL remediation, and codebase-wide quality enforcement  
> **Updated:** 2026-05-13 | Author: @mbaetiong  
> **API version:** `X-GitHub-Api-Version: 2022-11-28`

---

## Quick-Start: Five Calls That Rebuild the Security Overview

Run these in order at the start of **every** session before triaging or remediating any alert.

```bash
# 1 – Repo metadata (default branch, features)
gh api /repos/Aries-Serpent/_codex_

# 2 – Community health + security policy presence
gh api /repos/Aries-Serpent/_codex_/community/profile

# 3 – Open Dependabot (vulnerability) alerts
gh api "/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&per_page=100&page=1"

# 4 – Open CodeQL / code-scanning alerts
gh api "/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&per_page=100&page=1"

# 5 – Open secret-scanning alerts
gh api "/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=open&per_page=100&page=1"
```

> **Agent rule:** always paginate (`per_page=100`) to get exact counts, not just page-1 estimates.

---

## Base Conventions

| Header | Value |
|--------|-------|
| `Accept` | `application/vnd.github+json` |
| `X-GitHub-Api-Version` | `2022-11-28` |
| `Authorization` | `Bearer $GH_TOKEN` (use `CODEX_MASTER_KEY` for write ops) |
| Token chain | `CODEX_MASTER_KEY \|\| CODEX_BACKUP_KEY \|\| github.token` |

> ⚠️ `github.token` (installation token) returns **HTTP 403** on secrets/variables API.  
> Always use `CODEX_MASTER_KEY` for anything beyond read-only alert listing.

---

## Dependabot Alerts

### Recommended Calls

| Purpose | Call |
|---------|------|
| All open alerts (paginated) | `/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&per_page=100&page=1` |
| Triage by recency | `/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&sort=updated&direction=desc` |
| Critical only | `/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&severity=critical` |
| High only | `/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&severity=high` |
| pip ecosystem | `/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&ecosystem=pip` |
| Dismissed (audit trail) | `/repos/Aries-Serpent/_codex_/dependabot/alerts?state=dismissed` |
| Fixed (resolved) | `/repos/Aries-Serpent/_codex_/dependabot/alerts?state=fixed` |

### Single Alert Drill-Down

```
/repos/Aries-Serpent/_codex_/dependabot/alerts/{alert_number}
```

### Severity Values

`critical` · `high` · `medium` · `low`

### Ecosystem Values (for `?ecosystem=`)

`pip` · `npm` · `maven` · `nuget` · `rubygems` · `go` · `rust` · `composer`

---

## Code Scanning (CodeQL) Alerts

### Recommended Calls

| Purpose | Call |
|---------|------|
| All open alerts (paginated) | `/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&per_page=100&page=1` |
| CodeQL only | `/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&tool_name=CodeQL` |
| Error severity | `/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&severity=error` |
| Warning severity | `/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&severity=warning` |
| Main branch scope | `/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&ref=refs/heads/main` |
| PR scope | `/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&ref=refs/pull/{pr}/merge` |
| Newest first | `/repos/Aries-Serpent/_codex_/code-scanning/alerts?sort=created&direction=desc` |
| Analysis provenance | `/repos/Aries-Serpent/_codex_/code-scanning/analyses?ref=refs/heads/main` |
| Default CodeQL setup | `/repos/Aries-Serpent/_codex_/code-scanning/default-setup` |

### Single Alert Drill-Down

```
/repos/Aries-Serpent/_codex_/code-scanning/alerts/{alert_number}
```

### Severity Values

`critical` · `high` · `medium` · `low` · `error` · `warning` · `note`

### Common CodeQL Rule IDs (Python)

| Rule ID | Description | Fix Pattern |
|---------|-------------|-------------|
| `py/unused-import` | Import bound but never used | Remove import or add to `__all__` |
| `py/unused-global-variable` | Module-level var assigned, never read | Remove, export via `__all__`, or use it |
| `py/ineffectual-statement` | Statement with no effect (e.g. `...` after docstring) | Remove the `...` |
| `py/import-self` | Module imports itself | Use `importlib.import_module()` |
| `py/shell-command-injection` | `os.popen()` with dynamic input | Replace with `subprocess` + list args |
| `py/sql-injection` | String-formatted SQL | Use parameterised queries |
| `py/path-injection` | Unsanitised path from user input | Validate/sanitise before use |
| `py/clear-text-storage-sensitive-data` | Secrets written to disk/log unencrypted | Hash or redact before storage |

---

## Secret Scanning Alerts

### Recommended Calls

| Purpose | Call |
|---------|------|
| All open (paginated) | `/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=open&per_page=100&page=1` |
| Active/confirmed secrets | `/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=open&validity=active` |
| Unknown validity (triage) | `/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=open&validity=unknown` |
| GitHub PAT detector | `/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=open&secret_type=github_pat` |
| AWS key detector | `/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=open&secret_type=aws_access_key_id` |
| Resolved (audit) | `/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=resolved` |

### Per-Alert Location Evidence

```
/repos/Aries-Serpent/_codex_/secret-scanning/alerts/{alert_number}/locations
```

Returns file path, commit SHA, and line numbers — required for evidence during remediation.

### Validity Values

`active` · `inactive` · `unknown`

### Resolution Values

`false_positive` · `wont_fix` · `revoked` · `pattern_edited` · `pattern_deleted` · `used_in_tests`

---

## Security Policy & Community Health

| Purpose | Call |
|---------|------|
| Policy presence + health % | `/repos/Aries-Serpent/_codex_/community/profile` |
| Root SECURITY.md | `/repos/Aries-Serpent/_codex_/contents/SECURITY.md` |
| `.github/SECURITY.md` | `/repos/Aries-Serpent/_codex_/contents/.github/SECURITY.md` |
| `docs/SECURITY.md` | `/repos/Aries-Serpent/_codex_/contents/docs/SECURITY.md` |
| Discover `.github/` files | `/repos/Aries-Serpent/_codex_/contents/.github` |

**Policy resolution chain (check in order):**

1. `GET /community/profile` → check `.files.security` (not null = policy exists)
2. `GET /contents/.github/SECURITY.md` → most common GitHub-standard path
3. `GET /contents/SECURITY.md` → root-level fallback
4. `GET /contents/docs/SECURITY.md` → docs folder fallback

---

## Repository Advisories

| Purpose | Call |
|---------|------|
| Published advisories | `/repos/Aries-Serpent/_codex_/security-advisories?state=published&per_page=100&page=1` |
| Draft advisories | `/repos/Aries-Serpent/_codex_/security-advisories?state=draft` |
| All advisories | `/repos/Aries-Serpent/_codex_/security-advisories` |

---

## Severity-Oriented Triage Patterns

Use these as the first step when a PR introduces dependencies or code changes:

```bash
# Critical + High Dependabot — must fix before merge
gh api "/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&severity=critical"
gh api "/repos/Aries-Serpent/_codex_/dependabot/alerts?state=open&severity=high"

# Critical + High CodeQL — must fix before merge
gh api "/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&severity=critical"
gh api "/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&severity=high"

# Active confirmed secrets — immediate action required
gh api "/repos/Aries-Serpent/_codex_/secret-scanning/alerts?state=open&validity=active"
```

---

## Branch-Aware Validation

Run these when checking a specific PR or branch, replacing `{branch}` and `{pr}`:

```bash
# Code scanning scoped to main
gh api "/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&ref=refs/heads/main"

# Code scanning scoped to a PR
gh api "/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&ref=refs/pull/{pr}/merge"

# Analysis runs on main (provenance audit)
gh api "/repos/Aries-Serpent/_codex_/code-scanning/analyses?ref=refs/heads/main"
```

---

## Known API Gaps (No Public Parity)

| UI Section | Best Approximation | Gap |
|------------|-------------------|-----|
| Malware | `/dependabot/alerts` | No dedicated public "malware" endpoint |
| Code quality (standard) | None with stable parity | Internal/feature-specific source |
| Code quality (AI findings) | None with stable parity | No stable public repo endpoint |

---

## MCP Tool Mapping

When operating inside a Copilot session with GitHub MCP tools available, prefer these over raw `gh api` calls:

| Task | MCP Tool | Parameters |
|------|----------|------------|
| List CodeQL alerts | `github-mcp-server-list_code_scanning_alerts` | `owner`, `repo`, `state=open`, `tool_name=CodeQL` |
| Get single CodeQL alert | `github-mcp-server-get_code_scanning_alert` | `owner`, `repo`, `alertNumber` |
| List secret alerts | `github-mcp-server-list_secret_scanning_alerts` | `owner`, `repo`, `state=open` |
| Get single secret alert | `github-mcp-server-get_secret_scanning_alert` | `owner`, `repo`, `alertNumber` |

> MCP tools **do not** support Dependabot alert listing or secrets/variables CRUD.  
> Use `gh api` or the REST API directly for those.

---

## Recommended Session Startup Sequence

Run this sequence at the start of any security-remediation session:

| Step | Call | Purpose |
|-----:|------|---------|
| 1 | `GET /repos/Aries-Serpent/_codex_` | Default branch, feature flags |
| 2 | `GET /community/profile` | Policy health check |
| 3 | `GET /dependabot/alerts?state=open&per_page=100&page=1` | Vulnerability count |
| 4 | `GET /code-scanning/alerts?state=open&per_page=100&page=1` | Code scanning count |
| 5 | `GET /secret-scanning/alerts?state=open&per_page=100&page=1` | Secret count |
| 6 | `GET /security-advisories?state=published&per_page=100&page=1` | Advisory count |
| 7 | `GET /code-scanning/alerts?state=open&severity=critical` | Critical prioritisation |
| 8 | `GET /code-scanning/analyses?per_page=100&page=1` | Scanner provenance |
