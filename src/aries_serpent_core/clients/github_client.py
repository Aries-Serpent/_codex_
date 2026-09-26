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
import re
import time
from typing import Any
from urllib.parse import quote, urlsplit

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
    if not isinstance(url, str) or not url:
        raise ValueError("GitHub client URL must be a non-empty string")
    if any(ch in url for ch in ("\x00", "\n", "\r", "\t")):
        raise ValueError("GitHub client URL contains invalid control characters")
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
    if hostname_lower in {"localhost", "localhost.localdomain", "127.0.0.1", "0.0.0.0"}:
        raise ValueError(f"GitHub client URL host is not public: {hostname_lower}")
    if re.search(r"[\\\x00-\x1f\x7f]", parsed.path):
        raise ValueError("GitHub client URL path contains control characters")
    return url


def _safe_repo_component(value: str, *, field_name: str) -> str:
    """Validate repository path components for traversal and injection attempts."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"GitHub client URL {field_name} cannot be empty")
    if value.startswith("/") or value.endswith("/"):
        raise ValueError(f"GitHub client URL {field_name} must be a relative path component")
    if value in {".", ".."} or ".." in value or "\\" in value:
        raise ValueError(f"GitHub client URL {field_name} contains invalid path traversal characters")
    if any(ch in value for ch in ("\x00", "\n", "\r", "\t")):
        raise ValueError(f"GitHub client URL {field_name} contains invalid control characters")
    return value


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
    validated = _validated_url(url)
    r = requests.get(validated, headers=_auth_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def list_branches(owner: str = OWNER, repo: str = REPO) -> list[dict[str, Any]]:
    safe_owner = _safe_repo_component(owner, field_name="owner")
    safe_repo = _safe_repo_component(repo, field_name="repo")
    key = f"branches:{safe_owner}/{safe_repo}"
    c = cache_get(key, ttl=60)
    if c is not None:
        return c
    data = gh_get(f"{BASE}/repos/{safe_owner}/{safe_repo}/branches?per_page=100")
    cache_set(key, data)
    return data


def get_text(owner: str, repo: str, ref: str, path: str) -> str:
    clean_owner = _safe_repo_component(owner, field_name="owner")
    clean_repo = _safe_repo_component(repo, field_name="repo")
    clean_ref = _safe_repo_component(ref, field_name="ref")
    clean_path = _safe_repo_component(path.strip("/"), field_name="path")
    raw = f"https://raw.githubusercontent.com/{clean_owner}/{clean_repo}/{clean_ref}/{quote(clean_path, safe='/')}"
    r = requests.get(_validated_url(raw), timeout=30)
    if r.status_code == 200 and r.text:
        return r.text
    meta = gh_get(f"{BASE}/repos/{clean_owner}/{clean_repo}/contents/{quote(clean_path, safe='/')}?ref={quote(clean_ref)}")
    if isinstance(meta, dict) and meta.get("encoding") == "base64":
        return base64.b64decode(meta["content"]).decode("utf-8", errors="replace")
    return json.dumps(meta, ensure_ascii=False)


def code_search(owner: str, repo: str, q: str, ref: str = "main") -> dict[str, Any]:
    safe_owner = _safe_repo_component(owner, field_name="owner")
    safe_repo = _safe_repo_component(repo, field_name="repo")
    safe_ref = _safe_repo_component(ref, field_name="ref")
    query = quote(f"{q} repo:{safe_owner}/{safe_repo} ref:{safe_ref}")
    url = f"{BASE}/search/code?q={query}&per_page=10"
    return gh_get(url)


def most_recent_branch(owner: str = OWNER, repo: str = REPO) -> str:
    """
    Determine the most recently updated branch by commit date.
    Intended for low-frequency, human-in-the-loop usage.
    """
    import datetime

    safe_owner = _safe_repo_component(owner, field_name="owner")
    safe_repo = _safe_repo_component(repo, field_name="repo")
    branches = list_branches(safe_owner, safe_repo)
    best_name = "main"
    best_ts: datetime.datetime | None = None
    for b in branches:
        name = b.get("name")
        commit = b.get("commit") or {}
        sha = commit.get("sha")
        if not sha or not name:
            continue
        if not re.fullmatch(r"[0-9a-fA-F]{40,64}", str(sha)):
            continue
        url = f"{BASE}/repos/{safe_owner}/{safe_repo}/commits/{sha}"
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
