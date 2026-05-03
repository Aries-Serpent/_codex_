"""
GitHub Actions Variable Manager — Copilot Agent Tool
=====================================================

Manage GitHub Actions **repository**, **environment**, and **organization**
variables from within a Copilot Coding Agent session.

Token priority (resolved automatically at runtime):
  1. CODEX_MASTER_KEY    — full PAT (repo scope); supports all variable APIs
  2. CODEX_BACKUP_KEY    — fallback PAT
  3. AGENT_GITHUB_TOKEN  — stable alias for GITHUB_TOKEN (setup steps export)
  4. GITHUB_TOKEN        — scoped installation token (actions: write)

Mechanism priority (see docs/agent/COPILOT_TOKEN_GUIDE.md):
  1. Primary   — MCP Server tools (when available)
  2. Secondary — CLI API Server via BrainClient (when server is running at :8765)
  3. Fallback  — direct urllib calls (always available)

Usage examples
--------------
Python API::

    from scripts.tools.variable_manager import VariableManager

    vm = VariableManager()

    # Repo variables
    vm.list_repo_vars("Aries-Serpent", "_codex_")
    vm.create_repo_var("Aries-Serpent", "_codex_", "COPILOT_TEST_VAR", "hello_agent")
    vm.update_repo_var("Aries-Serpent", "_codex_", "COPILOT_TEST_VAR", "updated_value")
    vm.get_repo_var("Aries-Serpent", "_codex_", "COPILOT_TEST_VAR")
    vm.delete_repo_var("Aries-Serpent", "_codex_", "COPILOT_TEST_VAR")

    # Environment variables
    vm.list_env_vars("Aries-Serpent", "_codex_", "production")
    vm.create_env_var("Aries-Serpent", "_codex_", "production", "MY_ENV_VAR", "val")

    # Org variables
    vm.list_org_vars("Aries-Serpent")
    vm.create_org_var("Aries-Serpent", "MY_ORG_VAR", "val", visibility="all")

CLI::

    python scripts/tools/variable_manager.py list   repo Aries-Serpent _codex_
    python scripts/tools/variable_manager.py create repo Aries-Serpent _codex_ COPILOT_TEST_VAR hello
    python scripts/tools/variable_manager.py update repo Aries-Serpent _codex_ COPILOT_TEST_VAR new_val
    python scripts/tools/variable_manager.py get    repo Aries-Serpent _codex_ COPILOT_TEST_VAR
    python scripts/tools/variable_manager.py delete repo Aries-Serpent _codex_ COPILOT_TEST_VAR
    python scripts/tools/variable_manager.py list   env  Aries-Serpent _codex_ production
    python scripts/tools/variable_manager.py list   org  Aries-Serpent
    python scripts/tools/variable_manager.py test         # live end-to-end test

"""

from __future__ import annotations

import argparse
import json

# Safe JSON parser for external/untrusted inputs (GitHub API responses).
try:
    import sys as _sys
    _sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[2] / "src"))
    from codex.utils.json_safe import safe_json_loads as _safe_json_loads
except Exception:  # pragma: no cover
    def _safe_json_loads(text: Any, *, source: str = "<unknown>", **kwargs: Any) -> Any:  # type: ignore[misc]
        """Fallback when codex.utils.json_safe is unavailable.

        The ``source`` parameter is accepted for API compatibility but ignored
        here because the stdlib :func:`json.loads` does not support it.
        """
        return json.loads(text, **kwargs)
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Optional BrainClient import (secondary mechanism) ─────────────────────────
try:
    from codex.agents.brain_client import BrainClient, BrainClientError  # type: ignore

    _BRAIN_CLIENT_AVAILABLE = True
except ImportError:
    _BRAIN_CLIENT_AVAILABLE = False

_GH_API = "https://api.github.com"
_GH_API_VERSION = "2022-11-28"


# ─────────────────────────────────────────────────────────────────────────────
# Token resolution
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_token() -> Tuple[str, str]:
    """Return (token, source_name) for the best available GitHub auth token.

    Priority:
        1. CODEX_MASTER_KEY   — full PAT (repo scope); works with all variable APIs
        2. CODEX_BACKUP_KEY   — fallback PAT
        3. AGENT_GITHUB_TOKEN — GITHUB_TOKEN exported by copilot-setup-steps.yml
        4. GITHUB_TOKEN       — raw Actions installation token
    """
    for env_name in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY",
                     "AGENT_GITHUB_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(env_name, "").strip()
        if val:
            return val, env_name
    return "", "NONE"


# ─────────────────────────────────────────────────────────────────────────────
# Low-level GitHub API helper
# ─────────────────────────────────────────────────────────────────────────────

class GitHubAPIError(Exception):
    """Raised when the GitHub API returns a non-2xx status."""
    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


def _gh_request(
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
    brain: Optional[Any] = None,
) -> Tuple[int, Any]:
    """Make a GitHub API request.

    Uses BrainClient (secondary) when available and server is up; falls back
    to direct urllib (fallback mechanism).

    Returns (status_code, response_body).
    """
    url = f"{_GH_API}{path}"
    tok, _src = _resolve_token() if token is None else (token, "explicit")

    # ── Secondary: BrainClient / CLI API Server ────────────────────────────
    if brain is not None or (_BRAIN_CLIENT_AVAILABLE and _brain_available()):
        bc = brain or BrainClient()
        try:
            resp = bc.proxy_request(
                method,
                url,
                headers={"Authorization": f"Bearer {tok}"} if tok else None,
                body=body,
            )
            return resp.get("status_code", 0), resp.get("body")
        except BrainClientError:
            logger.debug("Suppressed exception in handler", exc_info=True)
    # ── Fallback: direct urllib ────────────────────────────────────────────
    headers: Dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": _GH_API_VERSION,
    }
    if tok:
        headers["Authorization"] = f"Bearer {tok}"

    data: Optional[bytes] = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:  # nosec B310
            raw = resp.read()
            return resp.status, _safe_json_loads(raw, source=url) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body_err = _safe_json_loads(raw, source=f"{url} (error body)")
        except Exception:
            body_err = raw.decode(errors="replace")
        raise GitHubAPIError(exc.code, str(body_err)) from exc


def _brain_available() -> bool:
    """Return True if the CLI API server is reachable."""
    if not _BRAIN_CLIENT_AVAILABLE:
        return False
    try:
        bc = BrainClient()
        return bc.is_available()
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# VariableManager
# ─────────────────────────────────────────────────────────────────────────────

class VariableManager:
    """CRUD operations for GitHub Actions repo / env / org variables.

    Parameters
    ----------
    token:  Optional explicit GitHub token. When ``None``, resolved automatically
            via ``_resolve_token()`` (CODEX_MASTER_KEY → … → GITHUB_TOKEN).
    brain:  Optional ``BrainClient`` instance for the secondary mechanism. When
            ``None``, auto-detected if the server is running at :8765.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        brain: Optional[Any] = None,
    ) -> None:
        self.token, self.token_source = _resolve_token() if token is None else (token, "explicit")
        self.brain = brain
        if not self.token:
            print(
                "⚠️  No GitHub token found. "
                "Set CODEX_MASTER_KEY, AGENT_GITHUB_TOKEN, or GITHUB_TOKEN.",
                file=sys.stderr,
            )

    # ── Repo variables ─────────────────────────────────────────────────────

    def list_repo_vars(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List all repository variables. Returns list of variable dicts."""
        status, body = _gh_request(
            "GET", f"/repos/{owner}/{repo}/actions/variables",
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(200,))
        return body.get("variables", [])  # type: ignore[union-attr]

    def get_repo_var(self, owner: str, repo: str, name: str) -> Dict[str, Any]:
        """Get a single repository variable by name."""
        status, body = _gh_request(
            "GET", f"/repos/{owner}/{repo}/actions/variables/{name}",
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(200,))
        return body  # type: ignore[return-value]

    def create_repo_var(
        self, owner: str, repo: str, name: str, value: str
    ) -> int:
        """Create a repository variable. Returns HTTP status (201 on success)."""
        status, body = _gh_request(
            "POST", f"/repos/{owner}/{repo}/actions/variables",
            body={"name": name, "value": value},
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(201,))
        return status

    def update_repo_var(
        self, owner: str, repo: str, name: str, value: str
    ) -> int:
        """Update an existing repository variable. Returns HTTP status (204)."""
        status, body = _gh_request(
            "PATCH", f"/repos/{owner}/{repo}/actions/variables/{name}",
            body={"name": name, "value": value},
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(204,))
        return status

    def delete_repo_var(self, owner: str, repo: str, name: str) -> int:
        """Delete a repository variable. Returns HTTP status (204)."""
        status, body = _gh_request(
            "DELETE", f"/repos/{owner}/{repo}/actions/variables/{name}",
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(204,))
        return status

    # ── Environment variables ──────────────────────────────────────────────

    def list_env_vars(
        self, owner: str, repo: str, environment: str
    ) -> List[Dict[str, Any]]:
        """List all variables for a repository environment."""
        status, body = _gh_request(
            "GET",
            f"/repos/{owner}/{repo}/environments/{environment}/variables",
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(200,))
        return body.get("variables", [])  # type: ignore[union-attr]

    def create_env_var(
        self, owner: str, repo: str, environment: str, name: str, value: str
    ) -> int:
        """Create a variable in a repository environment."""
        status, body = _gh_request(
            "POST",
            f"/repos/{owner}/{repo}/environments/{environment}/variables",
            body={"name": name, "value": value},
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(201,))
        return status

    def update_env_var(
        self, owner: str, repo: str, environment: str, name: str, value: str
    ) -> int:
        """Update an existing environment variable."""
        status, body = _gh_request(
            "PATCH",
            f"/repos/{owner}/{repo}/environments/{environment}/variables/{name}",
            body={"name": name, "value": value},
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(204,))
        return status

    def delete_env_var(
        self, owner: str, repo: str, environment: str, name: str
    ) -> int:
        """Delete an environment variable."""
        status, body = _gh_request(
            "DELETE",
            f"/repos/{owner}/{repo}/environments/{environment}/variables/{name}",
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(204,))
        return status

    # ── Organization variables ─────────────────────────────────────────────

    def list_org_vars(self, org: str) -> List[Dict[str, Any]]:
        """List all organization variables visible to the authenticated token."""
        status, body = _gh_request(
            "GET", f"/orgs/{org}/actions/variables",
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(200,))
        return body.get("variables", [])  # type: ignore[union-attr]

    def create_org_var(
        self,
        org: str,
        name: str,
        value: str,
        visibility: str = "all",
        selected_repository_ids: Optional[List[int]] = None,
    ) -> int:
        """Create an organization variable.

        Parameters
        ----------
        visibility: "all" | "private" | "selected"
        """
        payload: Dict[str, Any] = {
            "name": name,
            "value": value,
            "visibility": visibility,
        }
        if selected_repository_ids:
            payload["selected_repository_ids"] = selected_repository_ids
        status, body = _gh_request(
            "POST", f"/orgs/{org}/actions/variables",
            body=payload,
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(201,))
        return status

    def update_org_var(
        self,
        org: str,
        name: str,
        value: str,
        visibility: str = "all",
    ) -> int:
        """Update an existing organization variable."""
        status, body = _gh_request(
            "PATCH", f"/orgs/{org}/actions/variables/{name}",
            body={"name": name, "value": value, "visibility": visibility},
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(204,))
        return status

    def delete_org_var(self, org: str, name: str) -> int:
        """Delete an organization variable."""
        status, body = _gh_request(
            "DELETE", f"/orgs/{org}/actions/variables/{name}",
            token=self.token, brain=self.brain,
        )
        _check(status, body, expected=(204,))
        return status

    # ── Convenience: run end-to-end test ──────────────────────────────────

    def run_live_test(self, owner: str = "Aries-Serpent", repo: str = "_codex_") -> None:
        """Run a full create → verify → update → verify → delete cycle.

        Creates ``COPILOT_DELEGATION_TEST`` repo variable, verifies each step,
        and always cleans up — even on failure.
        """
        var_name = "COPILOT_DELEGATION_TEST"
        initial_value = "delegation_active_W118"
        updated_value = "delegation_verified_W118"

        tok, src = _resolve_token()
        print(f"\n{'═'*60}")
        print(" LIVE VARIABLE MANAGEMENT TEST — Delegation Active")
        print(f" Token source : {src} ({len(tok)} chars)")
        print(f" Target       : {owner}/{repo}")
        print(f" Variable     : {var_name}")
        print(f"{'═'*60}\n")

        results: List[Tuple[str, str, str]] = []

        def record(op: str, ok: bool, detail: str = "") -> None:
            status = "✅" if ok else "❌"
            results.append((op, status, detail))
            print(f"  {status} {op:<40} {detail}")

        # 1 ── List (before)
        try:
            before = self.list_repo_vars(owner, repo)
            existing = [v["name"] for v in before]
            record("LIST repo vars (before)", True,
                   f"total={len(before)}, {var_name}_exists={var_name in existing}")
        except GitHubAPIError as exc:
            record("LIST repo vars (before)", False, str(exc))
            _print_summary(results)
            return

        # Clean up any stale test variable before starting
        if var_name in existing:
            try:
                self.delete_repo_var(owner, repo, var_name)
                record("DELETE stale test var (pre-cleanup)", True, "")
            except GitHubAPIError:
                logger.debug("Suppressed exception in handler", exc_info=True)
        # 2 ── Create
        try:
            self.create_repo_var(owner, repo, var_name, initial_value)
            record("CREATE repo var", True, f"name={var_name} value={initial_value!r}")
        except GitHubAPIError as exc:
            record("CREATE repo var", False, str(exc))
            _print_summary(results)
            return

        # 3 ── Verify created
        try:
            v = self.get_repo_var(owner, repo, var_name)
            ok = v.get("value") == initial_value
            record("GET repo var (verify create)", ok,
                   f"value={v.get('value')!r} match={ok}")
        except GitHubAPIError as exc:
            record("GET repo var (verify create)", False, str(exc))

        # 4 ── Update
        try:
            self.update_repo_var(owner, repo, var_name, updated_value)
            record("UPDATE repo var (PATCH)", True, f"new_value={updated_value!r}")
        except GitHubAPIError as exc:
            record("UPDATE repo var", False, str(exc))

        # 5 ── Verify update
        try:
            v = self.get_repo_var(owner, repo, var_name)
            ok = v.get("value") == updated_value
            record("GET repo var (verify update)", ok,
                   f"value={v.get('value')!r} match={ok}")
        except GitHubAPIError as exc:
            record("GET repo var (verify update)", False, str(exc))

        # 6 ── Delete (always)
        try:
            self.delete_repo_var(owner, repo, var_name)
            record("DELETE repo var (cleanup)", True, "")
        except GitHubAPIError as exc:
            record("DELETE repo var (cleanup)", False, str(exc))

        # 7 ── Verify deleted
        try:
            self.get_repo_var(owner, repo, var_name)
            record("GET repo var (verify delete)", False, "var still exists!")
        except GitHubAPIError as exc:
            if exc.status == 404:
                record("GET repo var (verify delete)", True, "404 — variable gone ✅")
            else:
                record("GET repo var (verify delete)", False, str(exc))

        _print_summary(results)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _check(status: int, body: Any, expected: Tuple[int, ...]) -> None:
    if status not in expected:
        msg = body.get("message", str(body)) if isinstance(body, dict) else str(body)
        raise GitHubAPIError(status, msg)


def _print_summary(results: List[Tuple[str, str, str]]) -> None:
    passed = sum(1 for _, s, _ in results if s == "✅")
    total = len(results)
    print(f"\n{'─'*60}")
    print(f"  Result: {passed}/{total} operations passed")
    if passed == total:
        print("  🟢 ALL TESTS PASSED — delegation token working correctly")
    else:
        failed = [op for op, s, _ in results if s == "❌"]
        print(f"  🔴 FAILURES: {failed}")
        print("  See docs/agent/COPILOT_TOKEN_GUIDE.md for troubleshooting")
    print(f"{'─'*60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="variable_manager",
        description="GitHub Actions variable manager for Copilot agent sessions",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # ── test ──────────────────────────────────────────────────────────────
    t = sub.add_parser("test", help="Run live end-to-end test")
    t.add_argument("--owner", default="Aries-Serpent")
    t.add_argument("--repo", default="_codex_")

    # ── list ──────────────────────────────────────────────────────────────
    ls = sub.add_parser("list", help="List variables")
    ls.add_argument("scope", choices=["repo", "env", "org"])
    ls.add_argument("owner")
    ls.add_argument("repo_or_org")
    ls.add_argument("extra", nargs="?", help="environment name (env scope only)")

    # ── get ───────────────────────────────────────────────────────────────
    g = sub.add_parser("get", help="Get a single variable")
    g.add_argument("scope", choices=["repo", "env"])
    g.add_argument("owner")
    g.add_argument("repo")
    g.add_argument("name")
    g.add_argument("--env", dest="environment", help="environment (env scope)")

    # ── create ────────────────────────────────────────────────────────────
    c = sub.add_parser("create", help="Create a variable")
    c.add_argument("scope", choices=["repo", "env", "org"])
    c.add_argument("owner")
    c.add_argument("repo_or_org")
    c.add_argument("name")
    c.add_argument("value")
    c.add_argument("--env", dest="environment", help="environment (env scope)")
    c.add_argument("--visibility", default="all",
                   choices=["all", "private", "selected"],
                   help="org variable visibility")

    # ── update ────────────────────────────────────────────────────────────
    u = sub.add_parser("update", help="Update a variable")
    u.add_argument("scope", choices=["repo", "env", "org"])
    u.add_argument("owner")
    u.add_argument("repo_or_org")
    u.add_argument("name")
    u.add_argument("value")
    u.add_argument("--env", dest="environment", help="environment (env scope)")
    u.add_argument("--visibility", default="all")

    # ── delete ────────────────────────────────────────────────────────────
    d = sub.add_parser("delete", help="Delete a variable")
    d.add_argument("scope", choices=["repo", "env", "org"])
    d.add_argument("owner")
    d.add_argument("repo_or_org")
    d.add_argument("name")
    d.add_argument("--env", dest="environment", help="environment (env scope)")

    return p


def main(argv: Optional[List[str]] = None) -> int:  # noqa: C901
    parser = _build_parser()
    args = parser.parse_args(argv)
    vm = VariableManager()

    try:
        if args.command == "test":
            vm.run_live_test(args.owner, args.repo)
            return 0

        if args.command == "list":
            if args.scope == "repo":
                rows = vm.list_repo_vars(args.owner, args.repo_or_org)
            elif args.scope == "env":
                env_name = args.extra or ""
                rows = vm.list_env_vars(args.owner, args.repo_or_org, env_name)
            else:
                rows = vm.list_org_vars(args.repo_or_org)
            print(json.dumps(rows, indent=2))

        elif args.command == "get":
            if args.scope == "repo":
                result = vm.get_repo_var(args.owner, args.repo, args.name)
            else:
                result = vm.list_env_vars(
                    args.owner, args.repo, args.environment or ""
                )
            print(json.dumps(result, indent=2))

        elif args.command == "create":
            if args.scope == "repo":
                vm.create_repo_var(args.owner, args.repo_or_org, args.name, args.value)
            elif args.scope == "env":
                vm.create_env_var(
                    args.owner, args.repo_or_org,
                    args.environment or "", args.name, args.value,
                )
            else:
                vm.create_org_var(args.repo_or_org, args.name, args.value,
                                   args.visibility)
            print(f"✅ Created {args.scope} variable: {args.name}")

        elif args.command == "update":
            if args.scope == "repo":
                vm.update_repo_var(args.owner, args.repo_or_org, args.name, args.value)
            elif args.scope == "env":
                vm.update_env_var(
                    args.owner, args.repo_or_org,
                    args.environment or "", args.name, args.value,
                )
            else:
                vm.update_org_var(args.repo_or_org, args.name, args.value,
                                   args.visibility)
            print(f"✅ Updated {args.scope} variable: {args.name}")

        elif args.command == "delete":
            if args.scope == "repo":
                vm.delete_repo_var(args.owner, args.repo_or_org, args.name)
            elif args.scope == "env":
                vm.delete_env_var(
                    args.owner, args.repo_or_org,
                    args.environment or "", args.name,
                )
            else:
                vm.delete_org_var(args.repo_or_org, args.name)
            print(f"✅ Deleted {args.scope} variable: {args.name}")

    except GitHubAPIError as exc:
        print(f"❌ GitHub API error: {exc}", file=sys.stderr)
        if exc.status == 403:
            print(
                "   Token lacks permission. Required: CODEX_MASTER_KEY (repo scope)\n"
                "   See docs/agent/COPILOT_TOKEN_GUIDE.md#permission-matrix",
                file=sys.stderr,
            )
        elif exc.status == 401:
            print(
                "   Token is invalid or expired.\n"
                "   Current token source: " + _resolve_token()[1],
                file=sys.stderr,
            )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
