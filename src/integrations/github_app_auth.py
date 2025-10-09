from __future__ import annotations

import os
import re
import time
from pathlib import Path


API_VERSION = os.getenv("GITHUB_API_VERSION", "2022-11-28")
DEFAULT_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")


def _host_from_base(base: str) -> str:
    match = re.match(r"^https?://([^/]+)/?", base)
    return match.group(1) if match else ""


def assert_online_allowlisted() -> None:
    mode = os.getenv("CODEX_NET_MODE", "offline")
    allow = {h.strip() for h in os.getenv("CODEX_ALLOWLIST_HOSTS", "").split(",") if h.strip()}
    host = _host_from_base(DEFAULT_API_BASE)
    if mode != "online_allowlist" or host not in allow:
        raise SystemExit(
            "Online mode not permitted. "
            "Set CODEX_NET_MODE=online_allowlist and include api.github.com (or your host) in CODEX_ALLOWLIST_HOSTS."
        )


def _read_app_private_key() -> str:
    pem_inline = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem_inline:
        return pem_inline.replace("\\n", "\n")
    pem_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if pem_path and Path(pem_path).exists():
        return Path(pem_path).read_text(encoding="utf-8")
    raise SystemExit(
        "Missing app private key (GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def mint_app_jwt(app_id: str | int, ttl: int = 540) -> str:
    import jwt  # type: ignore

    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_app_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def exchange_installation_token(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    import requests

    url = f"{DEFAULT_API_BASE}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    response = requests.post(url, headers=headers, timeout=15)
    if response.status_code != 201:
        raise SystemExit(
            f"Installation token exchange failed: {response.status_code} {response.text}"
        )
    data = response.json()
    return data["token"], data.get("expires_at")


def build_auth_header_from_env() -> str:
    """Prefer GitHub App flow when available; fall back to GITHUB_TOKEN."""

    app_id = os.getenv("GITHUB_APP_ID")
    inst_id = os.getenv("GITHUB_APP_INSTALLATION_ID")
    pat = os.getenv("GITHUB_TOKEN")
    if app_id and inst_id:
        assert_online_allowlisted()
        jwt_token = mint_app_jwt(app_id)
        inst_token, _ = exchange_installation_token(jwt_token, inst_id)
        return f"token {inst_token}"
    if pat:
        assert_online_allowlisted()
        return f"token {pat}"
    raise SystemExit(
        "No auth: set App creds (GITHUB_APP_ID + GITHUB_APP_INSTALLATION_ID + key) or GITHUB_TOKEN."
    )
