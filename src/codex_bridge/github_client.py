"""
Github Client Module

This module provides functionality for github client.

Usage:
    from codex_bridge.github_client import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import time
from typing import Any
from urllib.parse import urlsplit

import requests

logger = logging.getLogger(__name__)

OWNER = os.getenv("CODEX_GH_OWNER", "Aries-Serpent")
REPO = os.getenv("CODEX_GH_REPO", "_codex_")
TOKEN = os.getenv("CODEX_GITHUB_TOKEN", "")
BASE = "https://api.github.com"
_ALLOWED_HTTP_HOSTS = {"api.github.com", "raw.githubusercontent.com", "github.com"}
CACHE_DIR = os.getenv("CODEX_CACHE_DIR", ".codex/cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _auth_headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def _cache_path(key: str) -> str:
    return os.path.join(
        CACHE_DIR,
        hashlib.sha256(key.encode()).hexdigest() + ".json",
    )


def _validated_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("GitHub client only allows absolute https URLs")
    if parsed.username or parsed.password:
        raise ValueError("GitHub client URL must not include embedded credentials")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("GitHub client URL must have a valid hostname")
    hostname_lower = hostname.lower()
    if hostname_lower not in _ALLOWED_HTTP_HOSTS:
        raise ValueError(f"GitHub client URL host not allowlisted: {hostname_lower}")
    return url


def cache_get(key: str, ttl: int) -> Any | None:
    p = _cache_path(key)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        obj = json.load(f)
    if time.time() - obj.get("ts", 0) <= ttl:
        return obj.get("data")
    return None


def cache_set(key: str, data: Any) -> None:
    p = _cache_path(key)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"ts": time.time(), "data": data}, f, ensure_ascii=False)


def gh_get(url: str) -> Any:
    r = requests.get(_validated_url(url), headers=_auth_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def list_branches(owner: str = OWNER, repo: str = REPO) -> list[dict[str, Any]]:
    key = f"branches:{owner}/{repo}"
    c = cache_get(key, ttl=60)
    if c is not None:
        return c
    data = gh_get(f"{BASE}/repos/{owner}/{repo}/branches?per_page=100")
    cache_set(key, data)
    return data


def get_text(owner: str, repo: str, ref: str, path: str) -> str:
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    r = requests.get(_validated_url(raw), timeout=30)
    if r.status_code == 200 and r.text:
        return r.text
    meta = gh_get(f"{BASE}/repos/{owner}/{repo}/contents/{path}?ref={ref}")
    if isinstance(meta, dict) and meta.get("encoding") == "base64":
        return base64.b64decode(meta["content"]).decode("utf-8", errors="replace")
    return json.dumps(meta, ensure_ascii=False)


def code_search(owner: str, repo: str, q: str, ref: str = "main") -> dict[str, Any]:
    from urllib.parse import quote

    query = quote(f"{q} repo:{owner}/{repo} ref:{ref}")
    url = f"{BASE}/search/code?q={query}&per_page=10"
    return gh_get(url)


def most_recent_branch(owner: str = OWNER, repo: str = REPO) -> str:
    """
    Determine the most recently updated branch by commit date.
    Intended for low-frequency, human-in-the-loop usage.
    """
    import datetime

    branches = list_branches(owner, repo)
    best_name = "main"
    best_ts: datetime.datetime | None = None
    for b in branches:
        name = b.get("name")
        commit = b.get("commit") or {}
        sha = commit.get("sha")
        if not sha or not name:
            continue
        url = f"{BASE}/repos/{owner}/{repo}/commits/{sha}"
        data = gh_get(url)
        # Prefer committer date, fall back to author
        commit_obj = data.get("commit", {})
        meta = commit_obj.get("committer") or commit_obj.get("author") or {}
        date_str = meta.get("date")
        if not date_str:
            continue
        try:
            ts = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:  # pragma: no cover - defensive  # nosec B112
            continue
        if best_ts is None or ts > best_ts:
            best_ts = ts
            best_name = name
    return best_name
