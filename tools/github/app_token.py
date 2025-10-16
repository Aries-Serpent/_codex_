#!/usr/bin/env python3

"""
GitHub App token helper (local/offline-safe for JWT build; network calls are opt-in).

Generates a short-lived (≤1h) installation access token when provided with:
  - GITHUB_APP_ID               (int)
  - GITHUB_APP_INSTALLATION_ID  (int)
  - GITHUB_APP_PRIVATE_KEY_PATH or GITHUB_APP_PRIVATE_KEY (PEM)

Notes:
- JWT is RS256 and valid ≤10 minutes; the installation token is typically ≤1 hour.
  See GitHub docs for details.
- This script only performs a network call if --print-installation-token is passed.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import time
import urllib.request

_JWT_SPEC = importlib.util.find_spec("jwt")
jwt = importlib.import_module("jwt") if _JWT_SPEC is not None else None

GITHUB_API = os.environ.get("GITHUB_API", "https://api.github.com")


def _read_private_key() -> bytes:
    pem = os.environ.get("GITHUB_APP_PRIVATE_KEY", "")
    key_path = os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH", "")
    if pem:
        return pem.encode("utf-8")
    if key_path:
        with open(key_path, "rb") as fh:
            return fh.read()
    raise SystemExit("[app_token] Set GITHUB_APP_PRIVATE_KEY or GITHUB_APP_PRIVATE_KEY_PATH")


def build_app_jwt(app_id: str, now: int | None = None, ttl_seconds: int = 540) -> str:
    """
    Build an RS256 JWT for the GitHub App (valid ≤10 minutes).
    """
    now = int(time.time()) if now is None else int(now)
    payload = {
        "iat": now - 60,  # issued 60s in the past for clock skew
        "exp": now + int(ttl_seconds),
        "iss": app_id,  # App ID
    }
    if jwt is None:
        raise SystemExit(
            "[app_token] Missing dependency 'PyJWT'. Install with: python -m pip install pyjwt"
        )
    key = _read_private_key()
    token = jwt.encode(payload, key, algorithm="RS256")
    if isinstance(token, bytes):
        token = token.decode("ascii")
    return token


def exchange_installation_token(
    jwt_token: str, installation_id: str
) -> tuple[str, dict[str, object]]:
    """
    Exchange App JWT → installation access token (network call).
    """
    url = f"{GITHUB_API}/app/installations/{installation_id}/access_tokens"
    req = urllib.request.Request(  # noqa: S310 (GitHub API endpoint)
        url=url,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {jwt_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        data=b"{}",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (controlled URL)
        body = json.loads(resp.read().decode("utf-8"))
        return body.get("token", ""), body


def main() -> int:
    p = argparse.ArgumentParser(
        prog="app_token",
        description="GitHub App token helper (build JWT and optionally fetch installation token)",
    )
    p.add_argument("--print-jwt", action="store_true", help="Print App JWT to stdout")
    p.add_argument(
        "--print-installation-token",
        action="store_true",
        help="Exchange JWT for installation token (network call)",
    )
    p.add_argument(
        "--app-id",
        default=os.environ.get("GITHUB_APP_ID", ""),
        help="GitHub App ID (env GITHUB_APP_ID)",
    )
    p.add_argument(
        "--installation-id",
        default=os.environ.get("GITHUB_APP_INSTALLATION_ID", ""),
        help="Installation ID (env GITHUB_APP_INSTALLATION_ID)",
    )
    args = p.parse_args()

    if not args.app_id:
        raise SystemExit("[app_token] missing --app-id or env GITHUB_APP_ID")
    if args.print_installation_token and not args.installation_id:
        raise SystemExit("[app_token] missing --installation-id or env GITHUB_APP_INSTALLATION_ID")

    token = build_app_jwt(args.app_id)
    if args.print_jwt:
        print(token)
    if args.print_installation_token:
        inst, _raw = exchange_installation_token(token, args.installation_id)
        if not inst:
            raise SystemExit("[app_token] did not receive installation token")
        print(inst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
