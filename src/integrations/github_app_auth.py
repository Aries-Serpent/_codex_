from __future__ import annotations

import os
import time
from pathlib import Path

import requests

try:
    import jwt  # pyjwt
except Exception as e:  # pragma: no cover
    jwt = None  # type: ignore


GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")
API_VERSION = "2022-11-28"


class AuthError(RuntimeError):
    pass


def _read_private_key() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError("Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH).")


def mint_app_jwt(app_id: str | int, ttl: int = 540) -> str:
    """
    Mint a short‑lived GitHub App JWT (Bearer) for authenticating as the App.
    """
    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def exchange_installation_token(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    import requests

    url = f"{DEFAULT_API_BASE}/app/installations/{installation_id}/access_tokens"
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
    """
    Create a short‑lived registration token for a self‑hosted runner.
    Requires admin permission at repo or org scope.
    """
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