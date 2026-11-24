"""Probe GitHub repository access without repository mutations or credential output.

Run: python -m scripts.ci.github_auth_preflight --repo OWNER/REPO
Output is always JSON. Successful reads never establish write authority or protected approval.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
from contextlib import redirect_stdout
from typing import Any
from urllib.parse import quote

from scripts.ci._token_resolver import (
    CANONICAL_HIERARCHY,
    resolve_app_id,
    resolve_app_installation_id,
    resolve_app_private_key,
)
from scripts.ci.approve_pending_runs import AppTokenRevocationError, _gh, _mint_app_token
from scripts.ci.github_rate_limit import quota_status

READ_ONLY_APP_PERMISSIONS = {
    "actions": "read",
    "administration": "read",
    "environments": "read",
}


def inspect_access(repo: str, environment: str, branch: str) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or any(
        re.fullmatch(r"\.+", part) for part in repo.split("/")
    ):
        raise ValueError("Expected an OWNER/REPO repository slug")
    # quote() leaves dot segments intact, which would redirect the API path.
    if any(value in ("", ".", "..") for value in (environment, branch)):
        raise ValueError("Environment and branch must be nonempty names, not dot segments")
    prefix = f"/repos/{repo}"
    env_path = f"{prefix}/environments/{quote(environment, safe='')}"
    endpoints = {
        "branch_protection": (
            f"{prefix}/branches/{quote(branch, safe='')}/protection",
            "administration:read",
        ),
        "environment_secret_key": (f"{env_path}/secrets/public-key", "environments:read"),
        "environment_marker_metadata": (
            f"{env_path}/secrets/OWNER_APPROVAL_PROTECTED",
            "environments:read",
        ),
        "actions_permissions": (f"{prefix}/actions/permissions", "administration:read"),
        "workflow_runs": (f"{prefix}/actions/runs?per_page=1", "actions:read"),
    }
    candidates = [
        (name, os.environ.get(name, "").strip())
        for name in (*CANONICAL_HIERARCHY, "CODEX_ADMIN_KEY")
    ]
    app_id, _ = resolve_app_id()
    private_key, _ = resolve_app_private_key()
    installation_id, _ = resolve_app_installation_id()
    app_values = [app_id, private_key, installation_id]
    app_status = "incomplete-configuration" if any(app_values) else "not-configured"
    if app_id and installation_id and not private_key:
        app_status = "private-key-not-pem"
    if all(app_values):
        ambient_repo = os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY")
        if not app_values[1].lstrip().startswith("-----BEGIN "):
            app_status = "private-key-not-pem"
        elif ambient_repo and ambient_repo.casefold() != repo.casefold():
            app_status = "repository-scope-mismatch"
        else:
            try:
                with redirect_stdout(sys.stderr):
                    app_token = _mint_app_token(
                        *app_values, repo=repo, permissions=READ_ONLY_APP_PERMISSIONS
                    )
                app_status = "verified-installation" if app_token else "mint-failed"
                if app_token:
                    candidates.insert(0, ("cognitive-brain-app", app_token))
            except AppTokenRevocationError:
                # Fail closed: never fall back to other credentials while a
                # rejected broader-scope token may remain active.
                app_status = "rejected-token-revoke-failed"
                candidates = []
            except (urllib.error.URLError, TimeoutError, OSError):
                app_status = "transport-error"
    routes: list[dict[str, Any]] = []
    seen: set[str] = set()
    verified_reads = {name: False for name in endpoints}
    app_token_value = (
        candidates[0][1] if candidates and candidates[0][0] == "cognitive-brain-app" else ""
    )
    try:
        _probe_routes(candidates, prefix, endpoints, routes, seen, verified_reads)
    finally:
        if app_token_value:
            try:
                status, _ = _gh("DELETE", "/installation/token", app_token_value)
                app_revoked = status == 204
            except (urllib.error.URLError, TimeoutError, OSError):
                app_revoked = False
            app_status = app_status if app_revoked else "verified-installation-revoke-failed"
    return {
        "repository": repo,
        "environment": environment,
        "branch": branch,
        "app_route": app_status,
        "routes": routes,
        "rate_limit": quota_status(),
        "verified_reads": verified_reads,
        "write_authority": "unverified; no repository mutations performed",
        "protected_approval": "unverified; requires protected runtime evidence",
    }


def _probe_routes(
    candidates: list[tuple[str, str]],
    prefix: str,
    endpoints: dict[str, tuple[str, str]],
    routes: list[dict[str, Any]],
    seen: set[str],
    verified_reads: dict[str, bool],
) -> None:
    for source, token in candidates:
        if not token or token in seen:
            continue
        seen.add(token)
        route: dict[str, Any] = {"source": source, "probes": []}
        try:
            status, _ = _gh("GET", prefix, token)
            route["repository_http_status"] = status
            if status == 200:
                for name, (path, permission) in endpoints.items():
                    status, _ = _gh("GET", path, token)
                    route["probes"].append(
                        {
                            "operation": name,
                            "path": path,
                            "http_status": status,
                            "required_read_permission": permission,
                        }
                    )
                    verified_reads[name] |= status == 200
        except (urllib.error.URLError, TimeoutError, OSError):
            route["transport_error"] = True
        routes.append(route)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--environment", default="owner-approval")
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()
    try:
        result = inspect_access(args.repo, args.environment, args.branch)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    if result["app_route"].endswith("revoke-failed"):
        return 1
    return 0 if all(result["verified_reads"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
