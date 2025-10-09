"""Mint short-lived GitHub App installation tokens with optional scoping.

The script is intentionally lightweight and offline-friendly: it only performs
network calls when executed without ``--dry-run`` and after verifying that the
Codex runtime permits outbound connections to ``api.github.com``.

It supports three actions once a token has been minted:

* ``print-rate-limit`` – inspect rate-limit buckets.
* ``probe-repo`` – sanity check repository reachability.
* ``runner-token`` – request a self-hosted runner registration token.

Example::

    python scripts/ops/codex_mint_tokens_per_run.py --action print-rate-limit \
        --repos owner/private-repo --permissions contents=read --print-headers

The script relies on the following environment variables:

``GITHUB_APP_ID``
    Identifier of the GitHub App.
``GITHUB_APP_INSTALLATION_ID``
    Target installation identifier.
``GITHUB_APP_PRIVATE_KEY``
    PEM-encoded private key for minting the App JWT.

The optional ``CODEX_NET_MODE`` and ``CODEX_NET_ALLOWLIST`` variables gate
outbound access to the GitHub API; real network calls require
``CODEX_NET_MODE=online_allowlist`` and ``api.github.com`` in the allowlist.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Mapping, Tuple
from urllib.parse import urlparse

try:  # pragma: no cover - optional dependency installed via [ops]
    import requests
except ModuleNotFoundError:  # pragma: no cover - provide a helpful stub for dry environments
    import types

    def _missing(*_: object, **__: object) -> None:
        raise ModuleNotFoundError(
            "requests is required; install codex-ml with the [ops] extra to enable network calls"
        )

    class _StubSession:
        def request(self, *args: object, **kwargs: object) -> None:
            _missing(*args, **kwargs)

        def close(self) -> None:  # pragma: no cover - no-op for stub
            return None

    requests = types.SimpleNamespace(
        post=_missing,
        get=_missing,
        delete=_missing,
        put=_missing,
        patch=_missing,
        request=_missing,
        Session=lambda: _StubSession(),
    )

API_VERSION = "2022-11-28"
DEFAULT_API_BASE = os.getenv("GITHUB_API_URL", "https://api.github.com")
USER_AGENT = "codex-ops-mint-token/1.0"


@dataclass(slots=True)
class GitHubSession:
    """Thin wrapper over requests with preset headers."""

    auth: str
    api_base: str = DEFAULT_API_BASE

    def __post_init__(self) -> None:
        if not self.auth:
            raise ValueError("auth is required for GitHubSession")
        if not self.auth.lower().startswith(("token ", "bearer ", "basic ")):
            self.auth = f"token {self.auth}"
        session_factory = getattr(requests, "Session", None)
        self._session = session_factory() if callable(session_factory) else None

    def __enter__(self) -> "GitHubSession":  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        self.close()

    def close(self) -> None:
        if self._session and hasattr(self._session, "close"):
            self._session.close()

    def _headers(self, extra: Mapping[str, str] | None = None) -> Mapping[str, str]:
        base = {
            "Authorization": self.auth,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        }
        if extra:
            merged = dict(base)
            merged.update(extra)
            return merged
        return base

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.api_base.rstrip('/')}/{path.lstrip('/')}"

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object] | None = None,
        json: Mapping[str, object] | None = None,
        data: object | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 10,
    ):
        url = self._url(path)
        hdrs = self._headers(headers)
        if self._session is not None:
            return self._session.request(
                method,
                url,
                params=params,
                json=json,
                data=data,
                headers=hdrs,
                timeout=timeout,
            )
        return requests.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            headers=hdrs,
            timeout=timeout,
        )

    def get(self, path: str, *, timeout: float = 10, params: Mapping[str, object] | None = None):
        return self.request("GET", path, timeout=timeout, params=params)

    def post(
        self,
        path: str,
        *,
        timeout: float = 10,
        json: Mapping[str, object] | None = None,
        data: object | None = None,
    ):
        return self.request("POST", path, timeout=timeout, json=json, data=data)

    def put(
        self,
        path: str,
        *,
        timeout: float = 10,
        json: Mapping[str, object] | None = None,
        data: object | None = None,
    ):
        return self.request("PUT", path, timeout=timeout, json=json, data=data)

    def patch(
        self,
        path: str,
        *,
        timeout: float = 10,
        json: Mapping[str, object] | None = None,
        data: object | None = None,
    ):
        return self.request("PATCH", path, timeout=timeout, json=json, data=data)

    def delete(self, path: str, *, timeout: float = 10):
        return self.request("DELETE", path, timeout=timeout)


@dataclass(frozen=True, slots=True)
class TokenScope:
    """Scope descriptor for installation access tokens."""

    repositories: tuple[str, ...]
    permissions: Mapping[str, str]

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.repositories:
            payload["repositories"] = list(self.repositories)
        if self.permissions:
            payload["permissions"] = dict(self.permissions)
        return payload


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--action", choices=["print-rate-limit", "probe-repo", "runner-token"], required=True
    )
    p.add_argument("--owner", help="Repository owner (for repo-scoped actions)")
    p.add_argument("--repo", help="Repository name (for repo-scoped actions)")
    p.add_argument("--org", help="Organization name (for org runner tokens)")
    p.add_argument("--verbose", action="store_true", help="Print masked token info")
    p.add_argument("--dry-run", action="store_true", help="Validate env/scoping without network")
    p.add_argument(
        "--repos",
        help="Comma-separated repositories to scope the installation token (owner/name,owner2/name2)",
    )
    p.add_argument(
        "--permissions",
        help="Comma-separated permissions as key=level pairs (e.g. contents=read,actions=write)",
    )
    p.add_argument(
        "--revoke-on-exit",
        action="store_true",
        help="Revoke the installation token before exiting",
    )
    p.add_argument(
        "--print-headers",
        action="store_true",
        help="Print rate-limit buckets after executing the main action",
    )
    return p


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _mask(secret: str, prefix: int = 4, suffix: int = 4) -> str:
    if not secret:
        return ""
    if len(secret) <= prefix + suffix:
        return "*" * len(secret)
    return f"{secret[:prefix]}…{secret[-suffix:]}"


def _assert_online_allowed() -> None:
    mode = os.getenv("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for network access")
    allowlist_raw = os.getenv("CODEX_NET_ALLOWLIST", "").strip()
    if not allowlist_raw:
        raise SystemExit("CODEX_NET_ALLOWLIST must include api.github.com for network access")
    allowed = {item.strip().lower() for item in allowlist_raw.split(",") if item.strip()}
    host = urlparse(DEFAULT_API_BASE).hostname or "api.github.com"
    if host.lower() not in allowed:
        raise SystemExit(f"{host} not present in CODEX_NET_ALLOWLIST")


def _mint_app_jwt(app_id: str | int, ttl: int = 540) -> str:
    import jwt  # PyJWT

    key = os.getenv("GITHUB_APP_PRIVATE_KEY")
    if not key:
        raise SystemExit("GITHUB_APP_PRIVATE_KEY not set")
    app_id_str = str(app_id)
    now = int(time.time())
    payload = {
        "iat": now - 60,  # allow for minor clock skew
        "exp": now + ttl,
        "iss": app_id_str,
    }
    return jwt.encode(payload, key, algorithm="RS256")


def _build_install_token_body(repos_csv: str | None, perms_csv: str | None) -> dict:
    body: dict[str, object] = {}
    if repos_csv:
        repos = [part.strip() for part in repos_csv.split(",") if part.strip()]
        if repos:
            body["repositories"] = repos
    if perms_csv:
        permissions: dict[str, str] = {}
        for raw in perms_csv.split(","):
            raw = raw.strip()
            if not raw:
                continue
            if "=" not in raw:
                raise SystemExit(f"Invalid permissions entry: {raw}")
            key, level = raw.split("=", 1)
            permissions[key.strip()] = level.strip()
        if permissions:
            body["permissions"] = permissions
    return body


def create_installation_access_token(
    session: GitHubSession,
    installation_id: str | int,
    scope: TokenScope,
    extra: Mapping[str, object] | None = None,
) -> Mapping[str, object]:
    body = scope.to_payload()
    if extra:
        body.update(extra)
    resp = session.post(
        f"/app/installations/{installation_id}/access_tokens",
        json=body,
        timeout=15,
    )
    if resp.status_code != 201:
        raise SystemExit(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    return resp.json()


def _exchange_installation_token(
    app_jwt: str,
    installation_id: str | int,
    *,
    body: Mapping[str, object] | None = None,
) -> Tuple[str, str | None]:
    scope = TokenScope(tuple(), {})
    with GitHubSession(f"Bearer {app_jwt}") as session:
        data = create_installation_access_token(session, installation_id, scope, extra=body)
    token = data.get("token")
    if not token:
        raise SystemExit("Installation token response missing token")
    return token, data.get("expires_at")


def _revoke_installation_token(installation_token: str) -> None:
    url = f"{DEFAULT_API_BASE.rstrip('/')}/installation/token"
    headers = {
        "Authorization": f"token {installation_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": USER_AGENT,
    }
    resp = requests.delete(url, headers=headers, timeout=10)
    if resp.status_code not in (202, 204):
        raise RuntimeError(f"revoke failed: {resp.status_code} {resp.text}")


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


def action_print_rate_limit(session: GitHubSession) -> None:
    resp = session.get("/rate_limit")
    if resp.status_code != 200:
        raise SystemExit(f"rate-limit query failed: {resp.status_code} {resp.text}")
    data = resp.json()
    print(json.dumps(data, indent=2, sort_keys=True))


def action_probe_repo(session: GitHubSession, owner: str, repo: str) -> None:
    resp = session.get(f"/repos/{owner}/{repo}")
    if resp.status_code != 200:
        raise SystemExit(f"probe failed: {resp.status_code} {resp.text}")
    data = resp.json()
    summary = {
        "full_name": data.get("full_name"),
        "private": data.get("private"),
        "default_branch": data.get("default_branch"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


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
            raise SystemExit("--owner and --repo required for repo runner tokens")
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    resp = session.post(path, timeout=15)
    if resp.status_code != 201:
        raise SystemExit(f"runner-token request failed: {resp.status_code} {resp.text}")
    data = resp.json()
    token = data.get("token", "")
    masked = _mask(token)
    print(
        json.dumps(
            {"token": token, "masked": masked, "expires_at": data.get("expires_at")}, indent=2
        )
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    app_id = os.getenv("GITHUB_APP_ID")
    inst_id = os.getenv("GITHUB_APP_INSTALLATION_ID")

    if args.dry_run:
        if not app_id or not inst_id:
            print(
                "[dry-run] Missing GITHUB_APP_ID or GITHUB_APP_INSTALLATION_ID",
                file=sys.stderr,
            )
            return 2
        _build_install_token_body(args.repos, args.permissions)
        print(
            json.dumps(
                {
                    "ok": True,
                    "mode": "dry-run",
                    "app_id_set": True,
                    "installation_id_set": True,
                    "scoping_parsed": True,
                }
            )
        )
        return 0

    if not app_id or not inst_id:
        raise SystemExit("GITHUB_APP_ID and GITHUB_APP_INSTALLATION_ID must be set")

    _assert_online_allowed()
    app_jwt = _mint_app_jwt(app_id)
    body = _build_install_token_body(args.repos, args.permissions)
    token, expires_at = _exchange_installation_token(app_jwt, inst_id, body=body)

    if args.verbose:
        print(f"[info] Installation token: {_mask(token)} exp={expires_at}")

    session = GitHubSession(token)

    try:
        if args.action == "print-rate-limit":
            action_print_rate_limit(session)
        elif args.action == "probe-repo":
            if not (args.owner and args.repo):
                raise SystemExit("--owner and --repo are required for action probe-repo")
            action_probe_repo(session, args.owner, args.repo)
        elif args.action == "runner-token":
            action_runner_registration_token(session, args.owner, args.repo, args.org)

        if args.print_headers:
            try:
                action_print_rate_limit(session)
            except Exception as exc:  # pragma: no cover - best-effort logging
                if args.verbose:
                    print(f"[warn] rate-limit print failed: {exc}", file=sys.stderr)
    finally:
        if args.revoke_on_exit:
            try:
                _revoke_installation_token(token)
                if args.verbose:
                    print("[info] revoked installation token")
            except Exception as exc:  # pragma: no cover - user opted-in to revoke
                print(f"[warn] revoke failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
