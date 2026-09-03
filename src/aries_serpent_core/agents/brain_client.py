"""
from aries_serpent_core.logging.structured_logger import logger
Cognitive Brain CLI API Client — Copilot Agent API Request Tool
===============================================================

**Agent API request priority hierarchy:**

1. **Primary — MCP Server + Playwright**: Use GitHub MCP tools (``github-mcp-server-*``
   functions) and Playwright browser tools when available. These provide the richest,
   most structured access to GitHub and web resources with full auth handling.

2. **Secondary — CLI API Client** (this module / ``POST /api/request``):
   Use ``BrainClient.proxy_request()`` when MCP/Playwright tools are unavailable or
   insufficient for the required operation. This provides: auto GitHub auth injection,
   session audit logging, and consistent timeout/error handling through a single egress point.

3. **Fallback — direct urllib / requests / httpx**: Acceptable as a last resort when
   neither MCP nor the CLI API server is available (e.g., server not started, network
   constraint). Use sparingly and prefer one of the above tiers when possible.

Quick start (every session)
----------------------------
    from aries_serpent_core.agents.brain_client import BrainClient
from scripts.ci._token_resolver import get_token


    brain = BrainClient()             # auto-discovers URL from env / defaults
    brain.is_available()              # True when server is up → proceed

    # ── Making API requests (secondary mechanism via CLI API Client) ────────
    # GET  any URL
    resp = brain.proxy_request("GET", "https://api.github.com/repos/Aries-Serpent/_codex_")

    # GET  workflow runs
    resp = brain.proxy_request(
        "GET",
        "https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs",
        params={"per_page": "5"},
    )

    # POST / PUT / PATCH / DELETE — e.g. create a repo variable
    resp = brain.proxy_request(
        "POST",
        "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables",
        body={"name": "COPILOT_TEST_VAR", "value": "test_value"},
    )

    # Convenience wrappers (GitHub-specific)
    info = brain.github_repo_info("Aries-Serpent", "_codex_")
    runs = brain.github_workflow_runs("Aries-Serpent", "_codex_", per_page=10)

    # ── Shell commands ──────────────────────────────────────────────────────
    result = brain.run_command("git log --oneline -5")
    logger.info(result["stdout"])

    # ── Session history ─────────────────────────────────────────────────────
    history = brain.cli_history(limit=10)

All methods raise ``BrainClientError`` on network or HTTP errors so the
caller can handle them cleanly.

Server auto-start
-----------------
The FastAPI server (``cognitive_app/src/server/cli_api_server.py``) is
auto-started by ``copilot-setup-steps.yml`` before the agent session begins.
It listens on ``http://localhost:8765`` by default.  If it is not running,
call ``brain.is_available()`` first and handle the ``False`` case.

See ``docs/agent/COGNITIVE_APP_CONNECTION_GUIDE.md`` for the complete reference,
troubleshooting, and live audit results.

Environment variables
---------------------
CODEX_CLI_API_URL      Primary URL override (default: http://localhost:8765).
COPILOT_CLI_BASE_URL   Fallback URL override if CODEX_CLI_API_URL is not set.
CODEX_MASTER_KEY       Bearer token — auto-injected for api.github.com calls;
                       also required for memory endpoints (/api/memory/*).
CODEX_BACKUP_KEY       Fallback bearer token (used if CODEX_MASTER_KEY is absent).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from scripts.ci._token_resolver import get_token

# ── Default server URL ────────────────────────────────────────────────────────
_DEFAULT_URL = "http://localhost:8765"


class BrainClientError(RuntimeError):
    """Raised when the CLI API server returns an error or is unreachable."""


class BrainClient:
    """Synchronous HTTP client for the Cognitive Brain CLI & API Gateway.

    Parameters
    ----------
    base_url:
        Override the server base URL.  Defaults to the ``CODEX_CLI_API_URL``
        environment variable, falling back to ``http://localhost:8765``.
    timeout:
        Default socket timeout (seconds) for all requests.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        raw = (
            base_url
            or os.environ.get("CODEX_CLI_API_URL")
            or os.environ.get("COPILOT_CLI_BASE_URL")
            or _DEFAULT_URL
        ).strip()

        # Validation logic for SSRF protection (CWE-918)
        # URLs must be http or https only; all other schemes (file, ftp, data, etc.)
        # are dangerous and must be rejected outright.
        parsed = urllib.parse.urlparse(raw)

        # Detect if this is a bare "host:port" misidentified as a scheme by urlparse.
        # urlparse("localhost:8765") → scheme="localhost", netloc="", path="8765"
        # The key indicator: in a bare host:port, there's no "://" in the original URL.
        # Real schemes (http://, file://, data:, etc.) have either "://" or are followed
        # by content that looks like a scheme continuation (e.g., "data:text/html").
        has_url_scheme = parsed.scheme and (
            f"{parsed.scheme}://" in raw  # Real URL scheme with authority
            or parsed.scheme in ("data", "javascript", "vbscript", "file", "ftp", "gopher")
            # ^ Known dangerous schemes that don't use "://"
        )

        if has_url_scheme:
            # Explicit URL scheme provided; must be http or https
            scheme = parsed.scheme.lower()
            if scheme not in ("http", "https"):
                raise BrainClientError(
                    f"Invalid base URL for BrainClient ('{raw}'); expected an http:// or "
                    "https:// URL with a host.  Check the 'base_url' argument or the "
                    "CODEX_CLI_API_URL / COPILOT_CLI_BASE_URL environment variables."
                )
        else:
            # Bare host, host:port, or host/path — convert to http://
            if not raw.startswith("http://") and not raw.startswith("https://"):
                raw = f"http://{raw}"
            parsed = urllib.parse.urlparse(raw)

        # Final validation: must have http/https scheme and a valid host
        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https") or not parsed.netloc:
            raise BrainClientError(
                f"Invalid base URL for BrainClient ('{raw}'); expected an http:// or "
                "https:// URL with a host.  Check the 'base_url' argument or the "
                "CODEX_CLI_API_URL / COPILOT_CLI_BASE_URL environment variables."
            )

        self.base_url = raw.rstrip("/")
        self.timeout = timeout

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _safe_urlopen(req: urllib.request.Request, timeout: int) -> None:
        """Validate the request URL scheme is http/https then call urlopen.

        Bandit B310: urllib.request.urlopen is flagged when the URL scheme is
        not validated, as file:/ and custom schemes can be exploited.
        All BrainClient URLs are constructed from ``self.base_url`` (always
        http:// or https://) so this guard is defensive-in-depth.
        """
        scheme = urllib.parse.urlparse(req.full_url).scheme.lower()
        if scheme not in ("http", "https"):
            raise BrainClientError(
                f"Blocked request to disallowed URL scheme '{scheme}://' "
                f"(only http/https are permitted)"
            )
        return urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- req.full_url is validated above
            req, timeout=timeout
        )

    def _auth_header(self) -> dict[str, str]:
        """Return a Bearer auth header using the best available token.

        Token priority (highest → lowest):
        1. ``CODEX_MASTER_KEY``    — full PAT (repo scope); required for variables/secrets API
        2. ``CODEX_BACKUP_KEY``    — fallback PAT
        3. ``AGENT_GITHUB_TOKEN``  — stable alias for GITHUB_TOKEN exported by setup steps
        4. ``GITHUB_TOKEN``        — scoped installation token (actions:write)

        All four are exported to ``GITHUB_ENV`` by the
        "🔑 Export Auth Tokens" step in ``copilot-setup-steps.yml``.
        See ``docs/agent/COPILOT_TOKEN_GUIDE.md`` for the full reference.
        """
        token = (
            get_token(required_elevated=True)[0]
            or get_token(required_elevated=True)[0]
            or os.environ.get("AGENT_GITHUB_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
            or ""
        ).strip()
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _get(self, path: str, params: Optional[dict[str, str]] = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        headers = {"Accept": "application/json"}
        headers.update(self._auth_header())
        req = urllib.request.Request(url, headers=headers)
        try:
            with self._safe_urlopen(req, timeout=self.timeout) as resp:  # type: ignore[attr-defined]
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise BrainClientError(f"GET {path} failed: HTTP {exc.code}") from exc
        except OSError as exc:
            raise BrainClientError(f"GET {path} unreachable: {exc}") from exc

    def _post(
        self, path: str, body: Any, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        headers.update(self._auth_header())
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with self._safe_urlopen(req, timeout=self.timeout) as resp:  # type: ignore[attr-defined]
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode(errors="replace")
            raise BrainClientError(f"POST {path} failed: HTTP {exc.code} — {body_text}") from exc
        except OSError as exc:
            raise BrainClientError(f"POST {path} unreachable: {exc}") from exc

    def _delete(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json"}
        headers.update(self._auth_header())
        req = urllib.request.Request(url, headers=headers, method="DELETE")
        try:
            with self._safe_urlopen(req, timeout=self.timeout) as resp:  # type: ignore[attr-defined]
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise BrainClientError(f"DELETE {path} failed: HTTP {exc.code}") from exc
        except OSError as exc:
            raise BrainClientError(f"DELETE {path} unreachable: {exc}") from exc

    # ── Public API ────────────────────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Return the server health payload.

        Returns
        -------
        dict with keys: status, repo_root, timestamp, history_db.
        """
        return self._get("/api/health")

    def is_available(self) -> bool:
        """Return True if the CLI API server is reachable and healthy."""
        try:
            data = self.health()
            return data.get("status") == "ok"
        except BrainClientError:
            return False

    def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 30,
        env: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Execute a shell command via the server and return the result.

        Parameters
        ----------
        command: Shell command string to execute.
        cwd:     Working directory (defaults to repo root on the server).
        timeout: Command timeout in seconds.
        env:     Extra environment variables to merge.

        Returns
        -------
        dict with keys: command, stdout, stderr, returncode, duration_ms, cwd, timestamp.

        Raises
        ------
        BrainClientError if the command was blocked or the server errored.
        """
        payload: dict[str, Any] = {"command": command, "timeout": timeout}
        if cwd:
            payload["cwd"] = cwd
        if env:
            payload["env"] = env
        return self._post("/api/cli/run", payload)

    def cli_history(self, limit: int = 50) -> dict[str, Any]:
        """Return recent command history.

        Returns
        -------
        dict with keys: items (list of run records), total.
        """
        return self._get("/api/cli/history", params={"limit": str(limit)})

    def clear_history(self) -> dict[str, Any]:
        """Clear CLI command history (both in-memory and SQLite).

        Returns
        -------
        dict with key: cleared (bool).
        """
        return self._delete("/api/cli/history")

    def proxy_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, str]] = None,
        body: Any | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """Proxy an HTTP request through the server (secondary agent API mechanism).

        **Agent API priority hierarchy:**

        1. **Primary** — MCP Server tools (``github-mcp-server-*``) and Playwright.
           Use these first when available.
        2. **Secondary (this method)** — Route the call through the CLI API server.
           Preferred over direct HTTP when the server is running; provides auto GitHub
           auth injection, session audit logging, and consistent timeout handling.
        3. **Fallback** — Direct ``urllib`` / ``requests`` / ``httpx``.
           Use only when neither MCP nor the CLI server is available.

        When the target URL starts with ``https://api.github.com/`` and
        ``CODEX_MASTER_KEY`` is set, the server auto-injects the auth header.

        Parameters
        ----------
        method:  HTTP method — GET, POST, PUT, PATCH, DELETE, HEAD, or OPTIONS.
        url:     Full target URL (e.g. ``https://api.github.com/repos/owner/repo``).
        headers: Additional request headers (dict).  GitHub auth is injected automatically.
        params:  Query-string parameters (dict).  Appended to the URL before sending.
        body:    Request body (dict / list / str).  Serialised as JSON automatically.
        timeout: Per-request timeout in seconds (default 30).

        Returns
        -------
        dict with keys: status_code (int), headers (dict), body (any), error (str|None).

        Raises
        ------
        BrainClientError on network failure or when the proxy server itself returns 4xx/5xx.

        Examples
        --------
        # GitHub repo info
        resp = brain.proxy_request("GET", "https://api.github.com/repos/Aries-Serpent/_codex_")

        # GitHub Actions runs
        resp = brain.proxy_request(
            "GET",
            "https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs",
            params={"per_page": "1"},
        )

        # Create a repo variable
        resp = brain.proxy_request(
            "POST",
            "https://api.github.com/repos/Aries-Serpent/_codex_/actions/variables",
            body={"name": "COPILOT_TEST_VAR", "value": "hello_from_agent"},
        )

        # POST to any API
        resp = brain.proxy_request("POST", "https://api.example.com/data", body={"k": "v"})
        """
        payload: dict[str, Any] = {
            "method": method.upper(),
            "url": url,
            "timeout": timeout,
        }
        if headers:
            payload["headers"] = headers
        if params:
            payload["params"] = params
        if body is not None:
            payload["body"] = body
        return self._post("/api/request", payload)

    def memory_state(self) -> dict[str, Any]:
        """Return STM/LTM memory statistics (requires CODEX_MASTER_KEY).

        Returns
        -------
        dict with keys: stm_count, ltm_count, capacity, cache_hit_rate,
        compression_rate, patterns, timestamp.

        Raises
        ------
        BrainClientError on 401/503 when auth is not configured.
        """
        return self._get("/api/memory/state")

    def memory_search(self, query: str, limit: int = 20) -> dict[str, Any]:
        """Full-text search over STM + LTM entries (requires CODEX_MASTER_KEY).

        Parameters
        ----------
        query: Search string.
        limit: Maximum results to return.

        Returns
        -------
        dict with keys: items (list), total.
        """
        return self._get("/api/memory/search", params={"q": query, "limit": str(limit)})

    def ooda_metrics(self) -> dict[str, Any]:
        """Return OODA loop execution metrics.

        Returns
        -------
        dict with keys: metrics, timestamp.
        """
        return self._get("/api/ooda/metrics")

    def ooda_process(self, input_data: Any, context: Any | None = None) -> dict[str, Any]:
        """Route input through the OODA cognitive orchestrator.

        Parameters
        ----------
        input_data: Input dict/value to process.
        context:    Optional context dict.

        Returns
        -------
        dict with keys: success, output, metrics, errors.
        """
        payload: dict[str, Any] = {"input": input_data}
        if context is not None:
            payload["context"] = context
        return self._post("/api/ooda/process", payload)

    # ── Convenience helpers ───────────────────────────────────────────────────

    def git_status(self) -> str:
        """Return `git status --short` output as a string."""
        result = self.run_command("git status --short", timeout=10)
        return result.get("stdout", "").strip()

    def git_log(self, n: int = 10) -> list[str]:
        """Return the last N git log lines as a list."""
        result = self.run_command(f"git --no-pager log --oneline -{n}", timeout=10)
        return [line for line in result.get("stdout", "").splitlines() if line]

    def github_repo_info(
        self, owner: str = "Aries-Serpent", repo: str = "_codex_"
    ) -> dict[str, Any]:
        """Fetch basic GitHub repo metadata via the proxy endpoint.

        Returns
        -------
        The GitHub API repository object (dict).
        """
        resp = self.proxy_request("GET", f"https://api.github.com/repos/{owner}/{repo}")
        return resp.get("body", {})

    def github_workflow_runs(
        self,
        owner: str = "Aries-Serpent",
        repo: str = "_codex_",
        per_page: int = 5,
    ) -> list[dict[str, Any]]:
        """Fetch the most recent GitHub Actions workflow runs via the proxy.

        Returns
        -------
        List of workflow run objects.
        """
        resp = self.proxy_request(
            "GET",
            f"https://api.github.com/repos/{owner}/{repo}/actions/runs",
            params={"per_page": str(per_page)},
        )
        body = resp.get("body", {})
        return body.get("workflow_runs", []) if isinstance(body, dict) else []
