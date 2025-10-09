"""Utilities to mint scoped GitHub tokens for Codex operational workflows.

This module provides a small CLI for working with GitHub App authentication.
The script is intentionally minimal but includes a handful of guardrails so it
is safe to execute inside the Codex automation environment. The tests exercise
behaviour such as argument parsing, allowlist validation and masking of secret
material, so keep those contracts stable when making changes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Tuple
from urllib.parse import urlparse

try:  # pragma: no cover - optional dependency for offline tests
    import requests
except ModuleNotFoundError:  # pragma: no cover - the CLI will guard on demand
    requests = None  # type: ignore[assignment]

API_VERSION = "2022-11-28"
DEFAULT_API_BASE = os.getenv("GITHUB_API_URL", "https://api.github.com")
USER_AGENT = "codex-ops-mint-token/1.0"


def _mask(secret: str, prefix: int = 4, suffix: int = 4) -> str:
    if not secret:
        return ""
    if len(secret) <= prefix + suffix:
        return "*" * len(secret)
    return f"{secret[:prefix]}…{secret[-suffix:]}"


def _read_app_private_key() -> str:
    """Return the GitHub App private key material.

    The Codex infrastructure supports three variants for specifying the key:
    inline via ``GITHUB_APP_PRIVATE_KEY_PEM`` (``\n`` escapes supported), the
    legacy ``GITHUB_APP_PRIVATE_KEY`` env or a file path exposed via
    ``GITHUB_APP_PRIVATE_KEY_PATH``. The helpers keep the legacy variable for
    backwards compatibility but encourage the new names.
    """

    pem_inline = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM") or os.getenv("GITHUB_APP_PRIVATE_KEY")
    if pem_inline:
        return pem_inline.replace("\\n", "\n")

    pem_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if pem_path:
        path = Path(pem_path)
        if path.exists():
            return path.read_text(encoding="utf-8")

    raise SystemExit(
        "Missing App private key. Provide GITHUB_APP_PRIVATE_KEY_PEM or "
        "GITHUB_APP_PRIVATE_KEY_PATH."
    )


def _assert_online_allowed() -> None:
    mode = os.getenv("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for network access")

    allowlist_raw = (
        os.getenv("CODEX_NET_ALLOWLIST") or os.getenv("CODEX_ALLOWLIST_HOSTS", "")
    ).strip()
    if not allowlist_raw:
        raise SystemExit("CODEX_NET_ALLOWLIST must include api.github.com for network access")

    allowed = {item.strip().lower() for item in allowlist_raw.split(",") if item.strip()}
    host = urlparse(DEFAULT_API_BASE).hostname or "api.github.com"
    if host.lower() not in allowed:
        raise SystemExit(f"{host} not present in CODEX_NET_ALLOWLIST")


def _mint_app_jwt(app_id: str | int, ttl: int = 540) -> str:
    try:
        import jwt  # type: ignore import-not-found
    except Exception as exc:  # pragma: no cover - import guard
        raise SystemExit("PyJWT is required to mint GitHub App tokens") from exc

    key = _read_app_private_key()
    app_id_str = str(app_id)
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": app_id_str}
    return jwt.encode(payload, key, algorithm="RS256")


@dataclass
class GitHubSession:
    token: str | None = None
    token_type: str = "Bearer"
    base_url: str = DEFAULT_API_BASE
    default_headers: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if requests is None:
            raise SystemExit("The 'requests' package is required for GitHubSession usage")
        self._session = requests.Session()
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": API_VERSION,
        }
        headers.update(self.default_headers)
        self._base_headers = headers

    # Public API ---------------------------------------------------------
    def post(self, path: str, **kwargs):
        return self._request("POST", path, **kwargs)

    def get(self, path: str, **kwargs):
        return self._request("GET", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)

    # Internal helpers ---------------------------------------------------
    def _request(self, method: str, path: str, **kwargs):
        url = self._resolve(path)
        headers = dict(self._base_headers)
        if self.token:
            headers["Authorization"] = f"{self.token_type} {self.token}"
        if "headers" in kwargs:
            extra = kwargs.pop("headers") or {}
            headers.update(extra)
        return self._session.request(method, url, headers=headers, **kwargs)

    def _resolve(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"


def _create_installation_body(
    repositories: Iterable[str] | None,
    permissions: Mapping[str, str] | None,
) -> Tuple[dict, bool]:
    body: dict[str, object] = {}
    scoping = False
    if repositories:
        repos_list = [repo.strip() for repo in repositories if repo.strip()]
        if repos_list:
            body["repositories"] = repos_list
            scoping = True
    if permissions:
        perms = {k: v for k, v in permissions.items() if k and v}
        if perms:
            body["permissions"] = perms
            scoping = True
    return body, scoping


def _build_app_session(app_id: str, api_base: str) -> GitHubSession:
    jwt_token = _mint_app_jwt(app_id)
    return GitHubSession(token=jwt_token, token_type="Bearer", base_url=api_base)


def _mint_installation_token(
    session: GitHubSession,
    installation_id: str,
    repositories: Iterable[str] | None = None,
    permissions: Mapping[str, str] | None = None,
) -> dict:
    body, scoping = _create_installation_body(repositories, permissions)
    response = session.post(
        f"/app/installations/{installation_id}/access_tokens",
        json=body if body else None,
        timeout=15,
    )
    if response.status_code != 201:
        raise SystemExit(
            "Failed to create installation access token: " f"{response.status_code} {response.text}"
        )
    data = response.json()
    masked = _mask(data.get("token", ""))
    output = {"token_masked": masked, "expires_at": data.get("expires_at")}
    if scoping:
        output["scoping"] = True
    print(json.dumps(output, indent=2))
    return data


def _revoke_installation_token(session: GitHubSession) -> None:
    response = session.delete("/installation/token", timeout=15)
    if response.status_code not in (202, 204):
        raise SystemExit(
            f"Failed to revoke installation token: {response.status_code} {response.text}"
        )
    print(json.dumps({"revoked": True}, indent=2))


def action_runner_registration_token(
    session: GitHubSession,
    owner: str | None,
    repo: str | None,
    org: str | None,
) -> None:
    if org and (owner or repo):
        raise SystemExit("Provide either org or owner/repo, not both")
    if repo and not owner:
        raise SystemExit("owner is required when repo is provided")
    if not ((owner and repo) or org):
        raise SystemExit("Provide owner/repo or org to scope the runner token")

    if org:
        path = f"/orgs/{org}/actions/runners/registration-token"
    else:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"

    response = session.post(path, timeout=15)
    if response.status_code != 201:
        raise SystemExit(
            "Failed to mint runner registration token: " f"{response.status_code} {response.text}"
        )

    data = response.json()
    token = data.get("token", "")
    masked = _mask(token)
    print(json.dumps({"token_masked": masked, "expires_at": data.get("expires_at")}, indent=2))


def action_print_rate_limit(session: GitHubSession) -> None:
    response = session.get("/rate_limit", timeout=10)
    if response.status_code != 200:
        raise SystemExit(f"Failed to fetch rate limit: {response.status_code} {response.text}")
    data = response.json()
    print(json.dumps({"rate_limit": data.get("resources", {})}, indent=2))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__ or "")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--app-id", default=os.getenv("GITHUB_APP_ID"))
    parser.add_argument("--installation-id", default=os.getenv("GITHUB_APP_INSTALLATION_ID"))
    parser.add_argument("--owner")
    parser.add_argument("--repo")
    parser.add_argument("--org")
    parser.add_argument("--repositories", nargs="*")
    parser.add_argument("--permissions", nargs="*")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-headers", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "command",
        choices=("mint", "runner-token", "revoke"),
        help="Operation to execute",
    )
    return parser


def _parse_permissions(items: Iterable[str] | None) -> Mapping[str, str]:
    if not items:
        return {}
    perms: dict[str, str] = {}
    for item in items:
        if ":" not in item:
            raise SystemExit("Permissions must be in scope:access form")
        scope, access = item.split(":", 1)
        perms[scope.strip()] = access.strip()
    return perms


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    scope_payload = {
        "owner": args.owner,
        "repo": args.repo,
        "org": args.org,
        "scoping_parsed": bool(args.org or (args.owner and args.repo)),
    }

    if args.dry_run:
        print(json.dumps(scope_payload, indent=2))
        return 0

    _assert_online_allowed()

    if not args.app_id:
        raise SystemExit("GITHUB_APP_ID must be provided")
    if not args.installation_id:
        raise SystemExit("GITHUB_APP_INSTALLATION_ID must be provided")

    app_session = _build_app_session(args.app_id, args.api_base)
    repositories = args.repositories or None
    permissions = _parse_permissions(args.permissions)

    if args.command == "mint":
        data = _mint_installation_token(
            app_session,
            args.installation_id,
            repositories=repositories,
            permissions=permissions,
        )
        token = data.get("token")
        if not token:
            raise SystemExit("Installation token missing from response")
        install_session = GitHubSession(token=token, base_url=args.api_base)
        if args.print_headers:
            try:
                action_print_rate_limit(install_session)
            except Exception as exc:  # pragma: no cover - best effort logging
                if args.verbose:
                    print(f"[warn] rate-limit print failed: {exc}", file=sys.stderr)
        return 0

    if args.command == "runner-token":
        data = _mint_installation_token(
            app_session,
            args.installation_id,
            repositories=repositories,
            permissions=permissions,
        )
        token = data.get("token")
        if not token:
            raise SystemExit("Installation token missing from response")
        install_session = GitHubSession(token=token, base_url=args.api_base)
        action_runner_registration_token(
            install_session, owner=args.owner, repo=args.repo, org=args.org
        )
        if args.print_headers:
            try:
                action_print_rate_limit(install_session)
            except Exception as exc:  # pragma: no cover - best effort logging
                if args.verbose:
                    print(f"[warn] rate-limit print failed: {exc}", file=sys.stderr)
        return 0

    if args.command == "revoke":
        data = _mint_installation_token(
            app_session,
            args.installation_id,
            repositories=repositories,
            permissions=permissions,
        )
        token = data.get("token")
        if not token:
            raise SystemExit("Installation token missing from response")
        install_session = GitHubSession(token=token, base_url=args.api_base)
        _revoke_installation_token(install_session)
        return 0

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
