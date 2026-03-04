"""
Cognitive Brain CLI API Client
==============================
Thin synchronous wrapper around the FastAPI CLI/API Gateway server
(``cognitive_app/src/server/cli_api_server.py``) that Copilot Coding Agents
can import and call directly during an active session.

The server is auto-started by ``copilot-setup-steps.yml`` before the agent
session begins; it listens on ``http://localhost:8765`` by default.

Usage inside a Copilot session
-------------------------------
    from codex.agents.brain_client import BrainClient

    brain = BrainClient()
    health = brain.health()
    result = brain.run_command("git status --short")
    response = brain.proxy_request("GET", "https://api.github.com/repos/Aries-Serpent/_codex_")

All methods raise ``BrainClientError`` on network or HTTP errors so the
caller can handle them cleanly.

Environment variables
---------------------
CODEX_CLI_API_URL   Override the default server URL (default: http://localhost:8765).
CODEX_MASTER_KEY    Bearer token for authenticated memory endpoints.
CODEX_BACKUP_KEY    Fallback bearer token (used if CODEX_MASTER_KEY is absent).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

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
        self.base_url = (
            base_url
            or os.environ.get("CODEX_CLI_API_URL")
            or os.environ.get("COPILOT_CLI_BASE_URL")
            or _DEFAULT_URL
        ).rstrip("/")
        self.timeout = timeout

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _safe_urlopen(req: urllib.request.Request, timeout: int):  # type: ignore[return]
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
        return urllib.request.urlopen(req, timeout=timeout)  # nosec B310

    def _auth_header(self) -> Dict[str, str]:
        """Return a Bearer auth header if CODEX_MASTER_KEY / CODEX_BACKUP_KEY is set."""
        token = (
            os.environ.get("CODEX_MASTER_KEY") or os.environ.get("CODEX_BACKUP_KEY") or ""
        ).strip()
        return {"Authorization": f"Bearer {token}"} if token else {}

    def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with self._safe_urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())  # type: ignore[return-value]
        except urllib.error.HTTPError as exc:
            raise BrainClientError(f"GET {path} failed: HTTP {exc.code}") from exc
        except OSError as exc:
            raise BrainClientError(f"GET {path} unreachable: {exc}") from exc

    def _post(
        self, path: str, body: Any, extra_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with self._safe_urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())  # type: ignore[return-value]
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode(errors="replace")
            raise BrainClientError(
                f"POST {path} failed: HTTP {exc.code} — {body_text}"
            ) from exc
        except OSError as exc:
            raise BrainClientError(f"POST {path} unreachable: {exc}") from exc

    def _delete(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="DELETE")
        try:
            with self._safe_urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())  # type: ignore[return-value]
        except urllib.error.HTTPError as exc:
            raise BrainClientError(f"DELETE {path} failed: HTTP {exc.code}") from exc
        except OSError as exc:
            raise BrainClientError(f"DELETE {path} unreachable: {exc}") from exc

    # ── Public API ────────────────────────────────────────────────────────────

    def health(self) -> Dict[str, Any]:
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
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
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
        payload: Dict[str, Any] = {"command": command, "timeout": timeout}
        if cwd:
            payload["cwd"] = cwd
        if env:
            payload["env"] = env
        return self._post("/api/cli/run", payload)

    def cli_history(self, limit: int = 50) -> Dict[str, Any]:
        """Return recent command history.

        Returns
        -------
        dict with keys: items (list of run records), total.
        """
        return self._get("/api/cli/history", params={"limit": str(limit)})

    def clear_history(self) -> Dict[str, Any]:
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
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        body: Any = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Proxy an HTTP request through the server and return the response.

        Useful for calling external APIs (e.g. GitHub REST API) from within
        the agent session.  When the target is ``api.github.com`` and
        ``CODEX_MASTER_KEY`` is set, the server auto-injects the auth header.

        Parameters
        ----------
        method:  HTTP method (GET, POST, PUT, PATCH, DELETE).
        url:     Full URL to proxy the request to.
        headers: Optional request headers.
        params:  Optional query parameters.
        body:    Optional request body (dict / list / str).
        timeout: Request timeout in seconds.

        Returns
        -------
        dict with keys: status_code, headers, body, duration_ms, url, method.
        """
        payload: Dict[str, Any] = {
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

    def memory_state(self) -> Dict[str, Any]:
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

    def memory_search(self, query: str, limit: int = 20) -> Dict[str, Any]:
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

    def ooda_metrics(self) -> Dict[str, Any]:
        """Return OODA loop execution metrics.

        Returns
        -------
        dict with keys: metrics, timestamp.
        """
        return self._get("/api/ooda/metrics")

    def ooda_process(self, input_data: Any, context: Any = None) -> Dict[str, Any]:
        """Route input through the OODA cognitive orchestrator.

        Parameters
        ----------
        input_data: Input dict/value to process.
        context:    Optional context dict.

        Returns
        -------
        dict with keys: success, output, metrics, errors.
        """
        payload: Dict[str, Any] = {"input": input_data}
        if context is not None:
            payload["context"] = context
        return self._post("/api/ooda/process", payload)

    # ── Convenience helpers ───────────────────────────────────────────────────

    def git_status(self) -> str:
        """Return `git status --short` output as a string."""
        result = self.run_command("git status --short", timeout=10)
        return result.get("stdout", "").strip()

    def git_log(self, n: int = 10) -> List[str]:
        """Return the last N git log lines as a list."""
        result = self.run_command(f"git --no-pager log --oneline -{n}", timeout=10)
        return [line for line in result.get("stdout", "").splitlines() if line]

    def github_repo_info(
        self, owner: str = "Aries-Serpent", repo: str = "_codex_"
    ) -> Dict[str, Any]:
        """Fetch basic GitHub repo metadata via the proxy endpoint.

        Returns
        -------
        The GitHub API repository object (dict).
        """
        resp = self.proxy_request("GET", f"https://api.github.com/repos/{owner}/{repo}")
        return resp.get("body", {})  # type: ignore[return-value]

    def github_workflow_runs(
        self,
        owner: str = "Aries-Serpent",
        repo: str = "_codex_",
        per_page: int = 5,
    ) -> List[Dict[str, Any]]:
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
