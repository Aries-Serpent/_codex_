# GitHub API Rate-Limit Awareness Guide

> **Audience:** Copilot Coding Agent sessions, CI scripts, custom agents  
> **Last updated:** 2026-05-07 — PR #4323 Session 5 hardening

---

## The Problem (Why Agents Hit Rate Limits Repeatedly)

GitHub enforces per-token, per-resource rate limits with **fixed hourly windows**.

| Symptom | Root cause |
|---------|-----------|
| `list_code_scanning_alerts` 403 → retry → 403 again | Same window, quota already 0 |
| Rate limit resets "in 19m", retried after 3m → 403 again | Did not wait for actual reset epoch |
| CI script calls API → MCP tool calls API → both 403 | Two separate tools sharing the same token pool |

**Key insight:** A failed API call still consumes one request from your quota. Never
retry before `x-ratelimit-reset` epoch.

---

## Token Pools (They Are NOT the Same)

| Token | Pool | Limit | Notes |
|-------|------|------:|-------|
| `CODEX_MASTER_KEY` | `core` REST | 5 000/hr | Full scope incl. `security_events` |
| `CODEX_BACKUP_KEY` | `core` REST | 5 000/hr | Fallback |
| Copilot sandbox token | `core` REST | 5 000/hr shared | Used by MCP tools (`list_code_scanning_alerts`) |
| `GITHUB_TOKEN` (workflow) | `core` REST | 1 000/hr | Actions installation token |
| Any token | `code_scanning` | separate pool | `/code-scanning/alerts` endpoint |

**The MCP `list_code_scanning_alerts` tool uses the Copilot sandbox token** — a
different credential from `CODEX_MASTER_KEY`. Both can be exhausted independently.

---

## Mandatory Pre-Call Protocol (Agent Rule)

**Before any GitHub API call or MCP tool invocation:**

```bash
# Step 1 — Check rate limits (writes .codex/rate_limit_state.json)
python scripts/ci/github_api_trickle.py --status
# Exit 0 = ready, Exit 1 = ALL tokens exhausted → do NOT proceed

# Step 2 — If exit 1, read the reset time and wait
python -c "
import json, time
s = json.load(open('.codex/rate_limit_state.json'))
print('All exhausted. Reset at:', s['earliest_reset_human'])
print('Wait seconds:', max(0, s['earliest_reset_epoch'] - int(time.time())))
"

# Step 3 — For code-scanning alerts, use the trickle fetcher (not MCP tool):
python scripts/ci/github_api_trickle.py --resource code-scanning-alerts --state open
```

---

## When to Skip the Check

| Situation | Action |
|-----------|--------|
| `.codex/rate_limit_state.json` exists and is < 60 s old | Re-use cached state — skip network probe |
| `"ok": true` in cached state | Proceed with API call |
| `"ok": false` in cached state | Wait until `earliest_reset_epoch` |
| `--offline` mode or no token available | Skip check; log warning |

---

## Fetching Code-Scanning Alerts (The Right Way)

```bash
# ✅ CORRECT — uses token rotation, rate-limit checks, exponential backoff:
python scripts/ci/github_api_trickle.py --resource code-scanning-alerts --state open

# ✅ With CODEX_MASTER_KEY explicitly:
CODEX_MASTER_KEY="$CODEX_MASTER_KEY" \
  python scripts/ci/github_api_trickle.py --resource code-scanning-alerts

# ✅ Raw gh CLI (uses CODEX_MASTER_KEY if set as GH_TOKEN):
GH_TOKEN="$CODEX_MASTER_KEY" \
  gh api -H "Accept: application/vnd.github+json" \
  "/repos/Aries-Serpent/_codex_/code-scanning/alerts?state=open&per_page=100" \
  --paginate > /tmp/alerts.json

# ❌ WRONG — MCP tool; uses sandbox token; no retry/backoff; no token rotation:
# (Do not call list_code_scanning_alerts if .codex/rate_limit_state.json shows ok=false)
```

---

## Rate-Limit State File Format

Written to `.codex/rate_limit_state.json` by `github_api_trickle.py --status`:

```json
{
  "ok": false,
  "core_ready": false,
  "security_ready": false,
  "tokens": [
    {
      "slot": 1,
      "pools": {
        "core": {
          "remaining": 0,
          "limit": 5000,
          "reset_epoch": 1746665064,
          "reset_human": "00:04:24 UTC",
          "wait_secs": 628,
          "ready": false
        },
        "code_scanning": {
          "remaining": 0,
          "limit": 30,
          "reset_epoch": 1746665064,
          "reset_human": "00:04:24 UTC",
          "wait_secs": 628,
          "ready": false
        }
      }
    }
  ],
  "earliest_reset_epoch": 1746665064,
  "earliest_reset_human": "00:04:24 UTC",
  "checked_at": "2026-05-06T23:53:56+00:00"
}
```

---

## session_bootstrap.py D-00 Gate

`session_bootstrap.py` now runs a rate-limit gate at session start (D-00):

1. Checks `.codex/rate_limit_state.json` — re-uses if < 60 s old
2. Probes all tokens via `github_api_trickle.status()`
3. If all exhausted: appends a **blocking warning** to the bootstrap report
4. Agents must read the warning and wait before any GitHub API call

---

## Quick Reference

```bash
# Check before EVERY GitHub API call:
python scripts/ci/github_api_trickle.py --status && echo "✅ Ready" || echo "🔴 Wait"

# See exactly when each pool resets:
python scripts/ci/github_api_trickle.py --status --json | \
  python3 -c "import sys,json; s=json.load(sys.stdin); print('Reset:', s['earliest_reset_human'])"

# List all open CodeQL alerts (rate-limit-safe):
python scripts/ci/github_api_trickle.py --resource code-scanning-alerts

# Legacy probe (full token scope check):
python scripts/ci/session_access_probe.py
```

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/ci/github_api_trickle.py` | Rate-limit-aware trickle fetcher; use for all code-scanning calls |
| `scripts/ci/session_access_probe.py` | Full token scope + rate-limit probe |
| `scripts/ci/github_rate_limit_helper.js` | JS rate-limit detector for github-script workflow steps |
| `.codex/rate_limit_state.json` | Cached rate-limit state (written by `--status`) |
| `src/services/github/client.py` | Async GitHub client with header-based rate-limit tracking |
| `src/mcp/rate_limit.py` | Token-bucket limiter for MCP server (server-side, not GitHub API) |
