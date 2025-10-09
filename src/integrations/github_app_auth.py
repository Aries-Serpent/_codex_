from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Mapping, MutableMapping
from urllib.parse import urlparse

import requests

try:  # pragma: no cover - optional dependency for JWT minting
    import jwt  # pyjwt
except Exception:  # pragma: no cover - defer error until minting
    jwt = None  # type: ignore


GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")
DEFAULT_API_BASE = GITHUB_API_BASE  # Backwards compatibility alias
API_VERSION = "2022-11-28"


class AuthError(RuntimeError):
    """Errors raised when GitHub authentication cannot be established."""


def _read_private_key() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def mint_app_jwt(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def exchange_installation_token(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def create_runner_registration_token(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def _github_api_host(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def _allowlisted_hosts(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def assert_online_allowlisted(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def build_auth_header_from_env(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"
