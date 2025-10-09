"""Utilities for minting short-lived GitHub tokens for Codex ops workflows."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

API_VERSION = "2022-11-28"
DEFAULT_API_BASE = os.getenv("GITHUB_API_URL", "https://api.github.com")
USER_AGENT = "codex-ops-mint-token/1.0"


@dataclass(frozen=True)
class TokenScope:
    """Represents the optional scoping payload for an installation token."""

    repositories: tuple[str, ...]
    permissions: Mapping[str, str]

    def as_request_payload(self) -> Mapping[str, object]:
        payload: dict[str, object] = {}
        if self.repositories:
            payload["repositories"] = list(self.repositories)
        if self.permissions:
            payload["permissions"] = dict(self.permissions)
        return payload


def _mask(secret: str, prefix: int = 4, suffix: int = 4) -> str:
    if not secret:
        return ""
    if len(secret) <= prefix + suffix:
        return "*" * len(secret)
    return f"{secret[:prefix]}…{secret[-suffix:]}"


def _read_app_private_key() -> str:
    """Load the GitHub App private key from inline env or a file path."""

    pem_inline = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM") or os.getenv("GITHUB_APP_PRIVATE_KEY")
    if pem_inline:
        return pem_inline.replace("\\n", "\n")
    pem_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if pem_path:
        key_path = Path(pem_path)
        if key_path.exists():
            return key_path.read_text(encoding="utf-8")
    raise SystemExit(
        "Missing App private key. Provide GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH."
    )


def _parse_permissions(values: Iterable[str]) -> Mapping[str, str]:
    perms: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise SystemExit(f"Invalid permission entry '{raw}'. Expected key=value.")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise SystemExit(f"Invalid permission entry '{raw}'.")
        perms[key] = value
    return perms


def _parse_repositories(values: Iterable[str]) -> tuple[str, ...]:
    repos = []
    for raw in values:
        trimmed = raw.strip()
        if not trimmed:
            continue
        repos.append(trimmed)
    return tuple(repos)


def _parse_scope(args: argparse.Namespace) -> TokenScope:
    permissions = _parse_permissions(args.permissions or ())
    repos = _parse_repositories(args.repositories or ())
    return TokenScope(repositories=repos, permissions=permissions)


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
    import jwt  # PyJWT

    key = _read_app_private_key()
    app_id_str = str(app_id)
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + ttl,
        "iss": app_id_str,
    }
    return jwt.encode(payload, key, algorithm="RS256")


class GitHubResponse:
    """Lightweight HTTP response wrapper for GitHub API calls."""

    def __init__(self, status_code: int, text: str, headers: Mapping[str, str]) -> None:
        self.status_code = status_code
        self.text = text
        self.headers = dict(headers)

    def json(self) -> Mapping[str, object]:
        if not self.text:
            return {}
        return json.loads(self.text)


class GitHubSession:
    """Minimal HTTP client for GitHub with Codex defaults."""

    def __init__(
        self,
        base_url: str = DEFAULT_API_BASE,
        *,
        auth: str | None = None,
        default_headers: Mapping[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self._default_headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
        if auth:
            self._default_headers["Authorization"] = auth
        if default_headers:
            self._default_headers.update(default_headers)

    def _resolve(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def request(self, method: str, path: str, *, timeout: int = 15, **kwargs) -> GitHubResponse:
        headers = kwargs.pop("headers", {})
        merged = dict(self._default_headers)
        merged.update(headers)
        data = None
        if "json" in kwargs:
            payload = kwargs.pop("json")
            merged.setdefault("Content-Type", "application/json")
            data = json.dumps(payload).encode("utf-8")
        elif "data" in kwargs:
            data = kwargs.pop("data")
        request = Request(self._resolve(path), data=data, headers=merged, method=method)
        try:
            with urlopen(request, timeout=timeout) as response:  # type: ignore[arg-type]
                body = response.read().decode("utf-8")
                status = response.status
                headers_map = dict(response.headers.items())
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            status = exc.code
            headers_map = dict(exc.headers.items()) if exc.headers else {}
        return GitHubResponse(status, body, headers_map)

    def get(self, path: str, *, timeout: int = 15, **kwargs) -> GitHubResponse:
        return self.request("GET", path, timeout=timeout, **kwargs)

    def post(self, path: str, *, timeout: int = 15, **kwargs) -> GitHubResponse:
        return self.request("POST", path, timeout=timeout, **kwargs)

    def delete(self, path: str, *, timeout: int = 15, **kwargs) -> GitHubResponse:
        return self.request("DELETE", path, timeout=timeout, **kwargs)

    def close(self) -> None:
        return None

    def __enter__(self) -> "GitHubSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _expect_status(response: GitHubResponse, expected: int, context: str) -> None:
    if response.status_code != expected:
        raise SystemExit(
            f"GitHub API call failed ({context}): {response.status_code} {response.text}"
        )


def create_installation_access_token(
    session: GitHubSession,
    installation_id: str | int,
    scope: TokenScope,
    *,
    timeout: int = 15,
) -> Mapping[str, object]:
    payload = scope.as_request_payload()
    response = session.post(
        f"/app/installations/{installation_id}/access_tokens",
        json=payload or {},
        timeout=timeout,
    )
    _expect_status(response, 201, "create access token")
    return response.json()


def revoke_installation_token(api_base: str, token: str, *, timeout: int = 15) -> None:
    if not token:
        return
    with GitHubSession(api_base, auth=f"token {token}") as session:
        response = session.delete("/installation/token", timeout=timeout)
        if response.status_code not in (204, 404):
            raise SystemExit(
                f"Failed to revoke installation token: {response.status_code} {response.text}"
            )


def action_runner_registration_token(
    session: GitHubSession,
    owner: str | None,
    repo: str | None,
    org: str | None,
) -> None:
    if org:
        path = f"/orgs/{org}/actions/runners/registration-token"
    else:
        if not owner or not repo:
            raise SystemExit("owner and repo are required when org is not provided")
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    resp = session.post(path, timeout=15)
    _expect_status(resp, 201, "runner registration token")
    data = resp.json()
    token = data.get("token", "")
    masked = _mask(token)
    print(
        json.dumps(
            {"token_masked": masked, "expires_at": data.get("expires_at")},
            indent=2,
            ensure_ascii=False,
        )
    )


def action_print_rate_limit(session: GitHubSession) -> None:
    response = session.get("/rate_limit", timeout=10)
    _expect_status(response, 200, "rate limit")
    data = response.json()
    core = data.get("resources", {}).get("core", {})
    print(json.dumps({"rate_limit": core}, indent=2, ensure_ascii=False))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mint GitHub installation tokens scoped per run.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="GitHub API base URL")
    parser.add_argument("--app-id", default=os.getenv("GITHUB_APP_ID"), help="GitHub App ID")
    parser.add_argument(
        "--installation-id",
        default=os.getenv("GITHUB_APP_INSTALLATION_ID"),
        help="GitHub App installation ID",
    )
    parser.add_argument(
        "--repositories",
        nargs="*",
        default=(),
        help="Optional list of repositories to scope the installation token",
    )
    parser.add_argument(
        "--permissions",
        nargs="*",
        default=(),
        help="Optional permission entries (format: key=value)",
    )
    parser.add_argument(
        "--runner",
        action="store_true",
        help="Request a self-hosted runner registration token using the installation token",
    )
    parser.add_argument("--owner", help="Repository owner (required for --runner without --org)")
    parser.add_argument("--repo", help="Repository name (required for --runner without --org)")
    parser.add_argument("--org", help="Organization slug for organization-wide runner tokens")
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse inputs without hitting the GitHub API"
    )
    parser.add_argument(
        "--print-headers",
        action="store_true",
        help="Print GitHub rate-limit headers after main operation",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose logging for optional steps")
    parser.add_argument("--timeout", type=int, default=15, help="Timeout (seconds) for API calls")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    scope = _parse_scope(args)
    scoping_payload = {
        "repositories": list(scope.repositories),
        "permissions": dict(scope.permissions),
    }
    if args.dry_run:
        print(
            json.dumps(
                {"dry_run": True, "scoping_parsed": True, "scoping": scoping_payload},
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if not args.app_id:
        raise SystemExit("GitHub App ID not provided (set GITHUB_APP_ID or pass --app-id)")
    if not args.installation_id:
        raise SystemExit(
            "GitHub App installation ID not provided (set GITHUB_APP_INSTALLATION_ID or pass --installation-id)"
        )

    _assert_online_allowed()

    app_jwt = _mint_app_jwt(args.app_id)
    api_base = args.api_base

    with GitHubSession(api_base, auth=f"Bearer {app_jwt}") as app_session:
        token_data = create_installation_access_token(
            app_session,
            args.installation_id,
            scope,
            timeout=args.timeout,
        )
        installation_token = token_data.get("token", "")
        masked_token = _mask(installation_token)
        print(
            json.dumps(
                {
                    "installation_token_masked": masked_token,
                    "expires_at": token_data.get("expires_at"),
                    "scoping": scoping_payload,
                },
                indent=2,
                ensure_ascii=False,
            )
        )

        runner_session: GitHubSession | None = None
        try:
            if args.runner:
                runner_session = GitHubSession(api_base, auth=f"token {installation_token}")
                action_runner_registration_token(
                    runner_session,
                    owner=args.owner,
                    repo=args.repo,
                    org=args.org,
                )
        finally:
            if runner_session:
                runner_session.close()

        try:
            if args.print_headers:
                action_print_rate_limit(app_session)
        except Exception as exc:  # pragma: no cover - best effort logging
            if args.verbose:
                print(f"[warn] rate-limit print failed: {exc}", file=sys.stderr)

    try:
        revoke_installation_token(api_base, installation_token, timeout=args.timeout)
    except Exception as exc:  # pragma: no cover - optional hygiene
        if args.verbose:
            print(f"[warn] revoke failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
