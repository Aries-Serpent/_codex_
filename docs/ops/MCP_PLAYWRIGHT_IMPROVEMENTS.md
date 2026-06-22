# GitHub MCP Service & Playwright Enhancement Plan

**Last Updated:** 2026-06-22

> **Status:** ✅ Active  
> **Created:** S174 (2026-03-21)  
> **Owner:** @mbaetiong  
> **Tracking PR:** `copilot/update-ci-failure-rate-and-confirm-transition`

---

## Executive Summary

This document identifies concrete improvements across all integration surfaces for the
GitHub MCP Service and Playwright automation stack. Eight enhancement areas are
identified covering: write-capable API client (`GitHubMCPPoster`), Playwright auth
and HAR replay, MCP server real-mode execution, CLI tooling gaps, cognitive brain
integration, rate-limit resilience, security hardening, and observability.

---

## 1. GitHub MCP Service — Write Capability Gaps

### Current State
`GitHubMCPPoster` (`src/codex/github/mcp_poster.py`) exposes only:
- `post_pr_comment()` / `post_pr_comment_from_file()`
- `create_discussion()` / `post_session_summary_discussion()`
- `set_repo_variable()`

### Gap
No method exists to:
- Create a branch ref (`POST /repos/{owner}/{repo}/git/refs`)
- Open a pull request (`POST /repos/{owner}/{repo}/pulls`)
- List/filter pull requests (`GET /repos/{owner}/{repo}/pulls`)
- Merge a branch (`POST /repos/{owner}/{repo}/merges`)
- Push a commit (via Git Data API: blobs → trees → commits → refs)

This gap was encountered during S174 when the agent needed to push `0D_base_` to GitHub.
The only available mechanism was `report_progress`, which is hardcoded to the PR branch.

### Improvements

**IMP-001 — Add write methods to `GitHubMCPPoster`**

```python
# src/codex/github/mcp_poster.py

def create_ref(self, repo: str, ref: str, sha: str) -> dict[str, Any]:
    """Create a branch reference on GitHub.

    Parameters
    ----------
    repo : str
        ``"owner/repo"`` format.
    ref : str
        Full ref name, e.g. ``"refs/heads/0D_base_"``.
    sha : str
        40-character commit SHA the new ref should point to.
    """
    self._require_token()
    url = f"{_GITHUB_API}/repos/{repo}/git/refs"
    return self._post(url, {"ref": ref, "sha": sha})

def create_pull_request(
    self,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str,
    draft: bool = False,
) -> dict[str, Any]:
    """Open a pull request.

    Parameters
    ----------
    head : str
        Branch name for the head (source) of the PR.
    base : str
        Branch name for the base (target) of the PR.
    """
    self._require_token()
    url = f"{_GITHUB_API}/repos/{repo}/pulls"
    return self._post(url, {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
        "draft": draft,
    })

def list_pull_requests(
    self,
    repo: str,
    state: str = "open",
    head: str = "",
    base: str = "",
) -> list[dict[str, Any]]:
    """List pull requests with optional head/base filters."""
    self._require_token()
    params = f"state={state}&per_page=100"
    if head:
        params += f"&head={head}"
    if base:
        params += f"&base={base}"
    url = f"{_GITHUB_API}/repos/{repo}/pulls?{params}"
    import urllib.request
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {self._token}", "Accept": _ACCEPT,
                 "X-GitHub-Api-Version": _API_VERSION},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
        return __import__("json").loads(resp.read())

def merge_branch(
    self,
    repo: str,
    base: str,
    head: str,
    commit_message: str = "",
) -> dict[str, Any]:
    """Merge *head* into *base* via GitHub's server-side merge API.

    This creates the merge commit on GitHub without requiring a local
    git clone or push — ideal for autonomous agent branch management.
    """
    self._require_token()
    url = f"{_GITHUB_API}/repos/{repo}/merges"
    payload: dict[str, Any] = {"base": base, "head": head}
    if commit_message:
        payload["commit_message"] = commit_message
    return self._post(url, payload)
```

**IMP-002 — Git Data API for autonomous commits**

Add `commit_files()` method that uses the Git Data API
(`POST /repos/{owner}/{repo}/git/blobs` → trees → commits → PATCH refs)
to push file changes without a local `git push`. This closes the
"agent can only push via `report_progress`" constraint.

**IMP-003 — Retry + rate-limit back-off**

The current `_request()` has no retry logic. GitHub API returns HTTP 403 (secondary
rate limit) and HTTP 429 (primary rate limit). Add exponential back-off:

```python
import time

def _request_with_retry(
    self, method: str, url: str, payload: dict[str, Any],
    max_retries: int = 3, backoff_base: float = 1.0,
) -> dict[str, Any]:
    for attempt in range(max_retries):
        try:
            return self._request(method, url, payload)
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429) and attempt < max_retries - 1:
                retry_after = int(exc.headers.get("Retry-After", backoff_base * (2 ** attempt)))
                logger.warning("Rate-limited (%d). Retrying in %ds…", exc.code, retry_after)
                time.sleep(retry_after)
            else:
                raise
```

---

## 2. GitHub MCP Service — Real-Mode Execution

### Current State
`.github/copilot-cascade/mcp_server.py` — `_execute_real()` is a **placeholder**:

```python
async def _execute_real(self, request: MCPRequest, server: MCPServer) -> MCPResponse:
    # Real execution logic would go here
    # This is a placeholder that simulates real execution
    await asyncio.sleep(0.1)
    # For now, return mock data but mark as real execution
```

### Improvement — IMP-004: Wire real MCP protocol transport

Replace the placeholder with actual MCP JSON-RPC 2.0 transport:

```python
async def _execute_real(self, request: MCPRequest, server: MCPServer) -> MCPResponse:
    """Execute via MCP JSON-RPC 2.0 over stdio or HTTP/SSE."""
    import aiohttp
    payload = {
        "jsonrpc": "2.0",
        "id": request.request_id,
        "method": f"tools/{request.capability}",
        "params": request.payload,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            server.url,
            json=payload,
            headers={"Authorization": f"Bearer {server.auth_token}"},
            timeout=aiohttp.ClientTimeout(total=server.timeout),
        ) as resp:
            resp.raise_for_status()
            body = await resp.json()
            if "error" in body:
                raise RuntimeError(f"MCP error: {body['error']}")
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="success",
                data=body.get("result"),
            )
```

**IMP-005 — Capability registry with schema validation**

Extend `MCPServer.capabilities` from `List[str]` to `List[CapabilitySpec]` where
`CapabilitySpec` includes input/output JSON Schema, enabling static validation of
requests before network round-trips.

---

## 3. Playwright — Authentication & GitHub Integration

### Current State
`PlaywrightScraper._authenticate()` attempts cookie injection via a GitHub API
token but the method is incomplete — it does not actually inject cookies.

`cognitive_app/playwright.config.ts` has no authentication setup; tests that
need GitHub token access rely on `VITE_GITHUB_TOKEN` env var at build time.

### Improvement — IMP-006: Storage-state-based auth for Playwright

```typescript
// cognitive_app/playwright.config.ts  (enhancement)
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  globalSetup: './e2e/global-setup.ts',  // NEW: runs once before all tests

  use: {
    storageState: 'playwright/.auth/github.json',  // reuse authenticated session
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
  },
  // ... existing config
});
```

```typescript
// cognitive_app/e2e/global-setup.ts  (NEW)
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Inject GitHub token as localStorage item used by cognitive app
  await page.goto(baseURL!);
  await page.evaluate((token: string) => {
    localStorage.setItem('github_token', token);
  }, process.env.VITE_GITHUB_TOKEN || '');

  // Save storage state (cookies + localStorage) for all tests
  await page.context().storageState({ path: 'playwright/.auth/github.json' });
  await browser.close();
}

export default globalSetup;
```

**IMP-007 — HAR replay for offline CI**

The `har-capture.spec.ts` records API interactions but `playwright.config.ts` has
no HAR replay configured for CI runs (where the backend is unavailable). Add:

```typescript
use: {
  // In CI, replay from HAR instead of hitting live backend
  ...(process.env.CI ? {
    serviceWorkers: 'block',
    // Route all backend requests to HAR file
  } : {}),
},
```

And add a `har-replay.spec.ts` that validates the app works entirely from the
pre-recorded HAR cache — enabling the GitHub Pages deployment to be fully tested
in CI without a live backend.

---

## 4. Playwright — Security Scraper Improvements

### Current State (`scripts/security/playwright_scraper.py`)
- `_authenticate()` method has no implementation for cookie injection
- No retry logic for transient GitHub UI changes
- Selector constants (`_ALERT_ROW_SELECTOR`, etc.) hard-coded without fallback
- No HAR recording for scrape session replay/debugging

### Improvement — IMP-008: Cookie injection via CDP

```python
def _authenticate(self, page: "Page") -> bool:
    """Inject GitHub session cookie via Chrome DevTools Protocol."""
    if not self.github_token:
        return False

    # Exchange PAT for session cookie via GitHub OAuth device flow
    # OR inject directly as Authorization header via CDP Network interception
    page.route("https://github.com/**", lambda route: route.continue_(
        headers={**route.request.headers, "Authorization": f"token {self.github_token}"}
    ))
    return True
```

**IMP-009 — Resilient selector strategy**

```python
_ALERT_SELECTORS = [
    "div[data-testid='code-scanning-alert-row']",   # primary (2026 UI)
    "li[data-testid*='code-scanning']",              # fallback (2025 UI)
    "div.js-code-scanning-alert-row",                # legacy
    "table.js-navigation-container tr.js-navigation-item",  # table layout
]

def _find_alert_rows(self, page: "Page"):
    for selector in _ALERT_SELECTORS:
        rows = page.query_selector_all(selector)
        if rows:
            return rows
    return []
```

---

## 5. CLI Tooling Gaps

### Current State
`python -m codex.github.mcp_poster` CLI supports:
- `post-comment` — post PR comment
- `post-session-summary` — create Discussion
- `set-variable` — set repo variable

### Gap
No CLI commands for:
- `create-branch` — create a ref (needed for 0D_base_ recreation)
- `create-pr` — open a pull request
- `merge-branch` — server-side branch merge

### Improvement — IMP-010: Extend CLI parser

```python
# src/codex/github/mcp_poster.py  (additions to _build_parser)

# create-branch subcommand
branch_p = sub.add_parser("create-branch", help="Create a branch ref on GitHub")
branch_p.add_argument("--repo",  required=True)
branch_p.add_argument("--ref",   required=True, help="e.g. refs/heads/0D_base_")
branch_p.add_argument("--sha",   required=True, help="Commit SHA to point to")

# create-pr subcommand
pr_p = sub.add_parser("create-pr", help="Open a pull request")
pr_p.add_argument("--repo",   required=True)
pr_p.add_argument("--title",  required=True)
pr_p.add_argument("--body",   default="")
pr_p.add_argument("--head",   required=True)
pr_p.add_argument("--base",   required=True, default="main")
pr_p.add_argument("--draft",  action="store_true")

# merge-branch subcommand
merge_p = sub.add_parser("merge-branch", help="Server-side branch merge")
merge_p.add_argument("--repo",    required=True)
merge_p.add_argument("--base",    required=True)
merge_p.add_argument("--head",    required=True)
merge_p.add_argument("--message", default="")
```

**IMP-011 — `actions_server.py` write endpoints**

Add POST endpoints to `tools/actions_server.py`:
- `POST /repo/branches` — create branch
- `POST /repo/pulls` — open PR
- `POST /repo/merges` — server-side merge

Enabling the CustomGPT Actions interface to drive branch lifecycle operations.

---

## 6. Cognitive Brain Integration

### Current State
`mcp_session_bridge.py` injects cognitive brain context into MCP sessions for
authorised actors. The `AgentBrainAPI` is called at session start (`PLAN` phase)
but there is no integration for:
- Branch/PR lifecycle events triggering pattern recording
- Automatic session-number increment on `create_ref()` calls
- Cognitive brain audit when `create_pull_request()` is called

### Improvement — IMP-012: MCP lifecycle hooks for branch/PR events

```python
# src/codex/github/mcp_poster.py  (enhancement)

def create_ref(self, repo: str, ref: str, sha: str) -> dict[str, Any]:
    result = self._raw_create_ref(repo, ref, sha)
    # Notify cognitive brain AfterMath cycle
    self._report_to_brain(
        step_id=f"CREATE-REF-{ref.split('/')[-1]}",
        outcome="success",
        notes=f"Created {ref} @ {sha[:8]} in {repo}",
    )
    return result

def _report_to_brain(self, step_id: str, outcome: str, notes: str) -> None:
    """Non-blocking cognitive brain pattern recording."""
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.getcwd(), "src"))
        from codex.cognitive.agent_brain_api import AgentBrainAPI, ImprovementArea
        api = AgentBrainAPI(agent_id="mcp-poster")
        api.report_completion(
            area=ImprovementArea.CI_CD,
            step_id=step_id,
            outcome=outcome,
            notes=notes,
        )
    except Exception:
        pass  # fail-open — cognitive brain enrichment is optional
```

**IMP-013 — Cognitive-brain-aware `detect-checkbox` job**

In `agent-auth-delegation.yml`, add a step in `activate-delegation` that calls
`AgentBrainAPI.get_session_context()` to inject the latest pattern library into
the `@copilot continue` comment body. This ensures the resumed agent session
has fresh cognitive brain context immediately — currently only `session_bootstrap.py`
does this and only when `CODEX_MASTER_KEY` is available.

---

## 7. MCP Configuration — Multi-Environment Hardening

### Current State (`.copilot-space/mcp.example.json`)
Single `codex-main-staging` server. `ITA_API_KEY` placeholder must be manually
replaced. No health-check or fallback server defined.

### Improvement — IMP-014: Multi-target MCP config with health checks

```json
{
  "mcpServers": {
    "github-primary": {
      "command": "python",
      "args": ["-m", "src.mcp.server.http", "--config", "codex_capability_map.yaml"],
      "env": {
        "MCP_API_KEY": "${env:CODEX_MCP_API_KEY:-dev-key}",
        "MCP_OFFLINE": "false",
        "MCP_HEALTH_CHECK_INTERVAL_S": "60"
      },
      "metadata": { "branch": "main", "maturity_level": 4 }
    },
    "github-fallback": {
      "command": "python",
      "args": ["-m", "src.mcp.server.http", "--config", "codex_capability_map.yaml", "--offline"],
      "env": { "MCP_OFFLINE": "true" },
      "metadata": { "role": "offline-fallback", "maturity_level": 3 }
    }
  },
  "routing": {
    "strategy": "primary-with-fallback",
    "health_check_timeout_ms": 5000
  }
}
```

---

## 8. Observability & Testing

### Current State
- `src/mcp/metrics/mcp_metrics.py` — `MetricCollector` exists but not wired to any
  workflow or CI gate
- No integration test for the full `agent-auth-delegation` → `@copilot continue`
  pipeline
- `playwright-results.json` generated but not uploaded to GitHub Actions artifacts

### Improvement — IMP-015: MCP metrics CI gate

```yaml
# .github/workflows/mcp-health.yml  (NEW)
- name: Check MCP metric thresholds
  run: |
    python - <<'EOF'
    from src.mcp.metrics.mcp_metrics import MetricCollector
    mc = MetricCollector()
    summary = mc.get_summary("mcp.request.latency_ms")
    if summary and summary.avg_value > 500:
        raise SystemExit(f"MCP avg latency {summary.avg_value:.0f}ms exceeds 500ms threshold")
    EOF
```

**IMP-016 — Upload Playwright results as CI artifacts**

```yaml
# cognitive_app GitHub Actions workflow  (addition)
- name: Upload Playwright report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-report-${{ github.run_id }}
    path: |
      cognitive_app/playwright-report/
      cognitive_app/playwright-results.json
    retention-days: 30
```

**IMP-017 — End-to-end delegation test fixture**

```python
# tests/github/test_mcp_poster_delegation.py  (NEW)

def test_create_ref_and_pr_roundtrip(respx_mock):
    """GitHubMCPPoster can create a branch and open a PR in one session."""
    respx_mock.post("https://api.github.com/repos/Aries-Serpent/_codex_/git/refs").mock(
        return_value=httpx.Response(201, json={"ref": "refs/heads/0D_base_", "object": {"sha": "abc123"}})
    )
    respx_mock.post("https://api.github.com/repos/Aries-Serpent/_codex_/pulls").mock(
        return_value=httpx.Response(201, json={"number": 9999, "html_url": "..."})
    )

    poster = GitHubMCPPoster(token="test-token")
    ref = poster.create_ref("Aries-Serpent/_codex_", "refs/heads/0D_base_", "abc123")
    pr  = poster.create_pull_request(
        "Aries-Serpent/_codex_", "S174 promotion", "...", "0D_base_", "main"
    )

    assert ref["ref"] == "refs/heads/0D_base_"
    assert pr["number"] == 9999
```

---

## Implementation Priority

| IMP-ID | Description | Effort | Priority |
|--------|-------------|--------|----------|
| IMP-001 | `GitHubMCPPoster` write methods (`create_ref`, `create_pull_request`, etc.) | S | ✅ DONE S175 |
| IMP-004 | MCP real-mode JSON-RPC transport | M | ✅ DONE S175 |
| IMP-010 | CLI `create-branch`, `create-pr`, `merge-branch` commands | S | ✅ DONE S175 |
| IMP-003 | Retry + rate-limit back-off | S | ✅ DONE S175 |
| IMP-006 | Playwright storage-state auth | S | ✅ DONE S175 |
| IMP-012 | Cognitive brain branch/PR lifecycle hooks | M | ✅ DONE S175 |
| IMP-013 | Cognitive-brain context in `@copilot continue` | S | ✅ DONE S175 |
| IMP-007 | HAR replay for offline CI | M | ✅ DONE S177 |
| IMP-009 | Resilient selector strategy in scraper | S | ✅ DONE S176 |
| IMP-011 | `actions_server.py` POST endpoints | M | ✅ DONE S176 |
| IMP-014 | Multi-target MCP config with health checks | L | ✅ DONE S177 |
| IMP-015 | MCP metrics CI gate | S | ✅ DONE S177 |
| IMP-016 | Upload Playwright results as CI artifacts | S | ✅ DONE S177 |
| IMP-017 | End-to-end delegation test fixture | M | ✅ DONE S176 |
| IMP-008 | Playwright CDP cookie injection | M | ✅ DONE S178 |
| IMP-005 | Capability schema validation | L | ✅ DONE S178 |
| IMP-002 | Git Data API autonomous commits | L | ✅ DONE S178 |

**Effort key:** S = < 1 hour | M = 1–4 hours | L = 4–8 hours
**All IMP items complete as of S178.  IMP backlog is fully closed.**

---

## Cross-References

- `src/codex/github/mcp_poster.py` — primary GitHubMCPPoster implementation
- `.github/copilot-cascade/mcp_server.py` — MCP server integration (placeholder real-mode)
- `scripts/security/playwright_scraper.py` — Playwright-based security scraper
- `cognitive_app/playwright.config.ts` — E2E test configuration
- `cognitive_app/e2e/har-capture.spec.ts` — HAR capture spec
- `src/codex/cognitive/mcp_session_bridge.py` — cognitive brain MCP session hook
- `.copilot-space/mcp.example.json` — MCP server configuration example
- `tools/actions_server.py` — CustomGPT Actions HTTP server (read-only currently)
- `.codex/docs/INTEGRATION_BRANCH_MODEL.md` — 0D_base_ promotion flow
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` — S174 session entry
