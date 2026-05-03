#!/usr/bin/env python3
"""
Minimal offline-first HTTP server to back CustomGPT Actions for _codex_.
Uses GitHub REST (token optional) and local cache. No CI, no secrets committed.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import urllib.request as _urllib_request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import quote

import requests

try:
    # Optional: reuse shared client utilities if importable
    from codex_bridge.github_client import (
        most_recent_branch as gh_most_recent_branch,
    )
except Exception:  # pragma: no cover - fallback
    gh_most_recent_branch = None

OWNER = os.getenv("CODEX_GH_OWNER", "Aries-Serpent")
REPO = os.getenv("CODEX_GH_REPO", "_codex_")
TOKEN = os.getenv("CODEX_GITHUB_TOKEN", "")
BASE = "https://api.github.com"
CACHE_DIR = os.getenv("CODEX_CACHE_DIR", ".codex/cache")
os.makedirs(CACHE_DIR, exist_ok=True)

_log = logging.getLogger(__name__)

# ── SSRF prevention ────────────────────────────────────────────────────────────
# Validate owner/repo/path parameters to prevent partial SSRF via URL path injection.
# Allowed characters: alphanumeric, hyphen, underscore, dot (GitHub conventions).
_SAFE_REPO_COMPONENT_RE = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9._\-]{0,99}$')
# Branch names: allow alphanumeric, hyphen, underscore, dot, slash (for nested branches)
# but no leading slash, double dots, or path-traversal sequences.
_SAFE_BRANCH_RE = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9._/\-]{0,199}$')


def _validate_repo_component(value: str, name: str) -> None:
    """Reject owner/repo values that do not match GitHub's safe naming rules.

    Prevents partial SSRF where a crafted owner/repo value contains path-separating
    characters (e.g. ``../../evil``) that could redirect the HTTP request to an
    unintended GitHub API path.
    """
    if not _SAFE_REPO_COMPONENT_RE.match(value):
        raise ValueError(
            f"Invalid {name!r} value {value!r}: must contain only alphanumeric, "
            "hyphen, underscore, or dot characters (no path separators)"
        )


def _validate_file_path(path: str) -> None:
    """Reject paths that contain traversal sequences or absolute references.

    Normalises URL percent-encoding (e.g. ``%2e%2e`` or ``.%2e``) before
    checking so that encoded traversal sequences are caught.
    """
    # Decode percent-encoded characters before checking
    from urllib.parse import unquote as _unquote
    decoded = _unquote(path)
    parts = decoded.replace("\\", "/").split("/")
    if ".." in parts or decoded.startswith("/"):
        raise ValueError(
            f"Invalid path {path!r}: path traversal sequences ('..') and "
            "absolute paths are not permitted"
        )


def _validate_ref(ref: str) -> None:
    """Reject ref values that do not match the safe branch name pattern.

    Prevents partial SSRF where a crafted ref value contains path-traversal
    or other unsafe sequences that could redirect the HTTP request to an
    unintended GitHub API path.

    Note: the explicit ``".." in ref`` check is required because
    ``_SAFE_BRANCH_RE`` allows individual dot characters (e.g. ``v1.0``)
    and slashes (for nested branches), so a sequence like ``foo..bar``
    would pass the regex but is still a path-traversal pattern.
    """
    if not _SAFE_BRANCH_RE.match(ref) or ".." in ref:
        raise ValueError(
            f"Invalid ref value {ref!r}: must contain only alphanumeric, "
            "hyphen, underscore, dot, or slash characters (no path traversal)"
        )


def _auth_headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def _cache_path(key: str) -> str:
    return os.path.join(
        CACHE_DIR,
        hashlib.sha1(key.encode(), usedforsecurity=False).hexdigest() + ".json",  # nosec B324 - Not for security, cache key only
    )


def _cache_get(key: str) -> Any | None:
    p = _cache_path(key)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            _log.warning(
                "Malformed cache entry at %s (expected dict, got %s); treating as cache miss",
                p, type(obj).__name__,
            )
            return None
        # Backwards compatibility: older cache files may not have a per-entry TTL
        raw_ttl = obj.get("ttl", 60)
        try:
            ttl = float(raw_ttl)
        except (TypeError, ValueError):
            _log.warning(
                "Malformed cache entry at %s (non-numeric 'ttl': %r); treating as cache miss",
                p, raw_ttl,
            )
            return None
        ts = obj.get("ts")
        if ts is None or not isinstance(ts, (int, float)):
            _log.warning(
                "Malformed cache entry at %s (missing or invalid 'ts'); treating as cache miss",
                p,
            )
            return None
        if time.time() - ts >= ttl:
            # Treat expired entries as cache misses
            return None
        return obj.get("data")
    return None


def _cache_set(key: str, data: Any, ttl: int = 60) -> None:
    # naive cache with timestamp; actions are human-in-the-loop so short TTL is fine
    obj = {"ts": time.time(), "ttl": ttl, "data": data}
    p = _cache_path(key)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def gh_get(url: str):
    r = requests.get(url, headers=_auth_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def list_branches(owner: str, repo: str):
    _validate_repo_component(owner, "owner")
    _validate_repo_component(repo, "repo")
    key = f"branches:{owner}/{repo}"
    c = _cache_get(key)
    if c is not None:
        return c
    data = gh_get(f"{BASE}/repos/{owner}/{repo}/branches?per_page=100")
    _cache_set(key, data)
    return data


def get_file_text(owner: str, repo: str, ref: str, path: str) -> str:
    # Validate inputs to prevent partial SSRF (CodeQL alerts #10639, #10640):
    # unvalidated owner/repo/path values can inject path separators that escape
    # the intended GitHub URL structure.
    _validate_repo_component(owner, "owner")
    _validate_repo_component(repo, "repo")
    _validate_ref(ref)
    _validate_file_path(path)
    # Use raw endpoint; fallback to contents API
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{quote(ref)}/{quote(path)}"
    r = requests.get(raw, timeout=30)
    if r.status_code == 200 and r.text:
        return r.text
    meta = gh_get(f"{BASE}/repos/{owner}/{repo}/contents/{quote(path)}?ref={quote(ref)}")
    if isinstance(meta, dict) and meta.get("encoding") == "base64":
        import base64

        return base64.b64decode(meta["content"]).decode("utf-8", errors="replace")
    return json.dumps(meta, ensure_ascii=False)


def code_search(owner: str, repo: str, q: str, ref: str = "main"):
    _validate_repo_component(owner, "owner")
    _validate_repo_component(repo, "repo")
    # GitHub code search requires qualifiers
    # NOTE: basic search endpoint respects rate limits; TOKEN recommended.
    query = quote(f"{q} repo:{owner}/{repo} ref:{ref}")
    url = f"{BASE}/search/code?q={query}&per_page=10"
    data = gh_get(url)
    hits = []
    for it in data.get("items", []):
        path = it.get("path")
        # Fetch a small preview window if text file
        try:
            content = get_file_text(owner, repo, ref, path)
        except Exception:
            content = ""
        snippet = content[:2000]
        hits.append({"path": path, "preview": snippet})
    return {"count": len(hits), "items": hits}


def gh_post(url: str, payload: dict[str, Any]) -> Any:
    """POST *payload* to the GitHub API and return the parsed JSON response.

    The *url* must start with the expected :data:`BASE` constant to prevent
    SSRF-class attacks where a crafted caller could redirect the POST to an
    arbitrary host.
    """
    if not url.startswith(BASE):
        raise ValueError(f"gh_post: URL must start with {BASE!r}, got {url!r}")
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = _urllib_request.Request(
        url,
        data=data,
        headers={**_auth_headers(), "Content-Type": "application/json"},
        method="POST",
    )
    with _urllib_request.urlopen(req, timeout=30) as resp:  # nosec B310
        return json.loads(resp.read())


def create_branch(owner: str, repo: str, branch: str, sha: str) -> dict[str, Any]:
    """Create *branch* pointing at *sha* via the GitHub Refs API (IMP-011)."""
    _validate_repo_component(owner, "owner")
    _validate_repo_component(repo, "repo")
    # Validate branch name before embedding it in the URL path.
    if branch.startswith("refs/"):
        branch_part = branch[len("refs/heads/"):] if branch.startswith("refs/heads/") else branch
    else:
        branch_part = branch
    if not _SAFE_BRANCH_RE.match(branch_part) or ".." in branch_part:
        raise ValueError(
            f"Invalid branch name {branch!r}: must contain only alphanumeric, "
            "hyphen, underscore, dot, or slash characters (no traversal sequences)"
        )
    ref = f"refs/heads/{branch}" if not branch.startswith("refs/") else branch
    return gh_post(f"{BASE}/repos/{owner}/{repo}/git/refs", {"ref": ref, "sha": sha})


def open_pull_request(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str,
    body: str = "",
    draft: bool = False,
) -> dict[str, Any]:
    """Open a pull request (IMP-011)."""
    _validate_repo_component(owner, "owner")
    _validate_repo_component(repo, "repo")
    return gh_post(
        f"{BASE}/repos/{owner}/{repo}/pulls",
        {"title": title, "head": head, "base": base, "body": body, "draft": draft},
    )


def merge_branches(
    owner: str,
    repo: str,
    base: str,
    head: str,
    commit_message: str = "",
) -> dict[str, Any]:
    """Server-side merge of *head* into *base* (IMP-011)."""
    _validate_repo_component(owner, "owner")
    _validate_repo_component(repo, "repo")
    payload: dict[str, Any] = {"base": base, "head": head}
    if commit_message:
        payload["commit_message"] = commit_message
    return gh_post(f"{BASE}/repos/{owner}/{repo}/merges", payload)


class App(BaseHTTPRequestHandler):
    def _ok(self, body: Any, code=200):
        b = body if isinstance(body, (str, bytes)) else json.dumps(body, ensure_ascii=False)
        if isinstance(b, str):
            b = b.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        from urllib.parse import parse_qs, urlparse

        u = urlparse(self.path)
        qs = parse_qs(u.query)
        if u.path == "/healthz":
            return self._ok({"ok": True, "ts": int(time.time())})
        if u.path == "/repo/branches":
            owner = qs.get("owner", [OWNER])[0]
            repo = qs.get("repo", [REPO])[0]
            return self._ok(list_branches(owner, repo))
        if u.path == "/repo/files":
            owner = qs.get("owner", [OWNER])[0]
            repo = qs.get("repo", [REPO])[0]
            ref = qs.get("ref", ["main"])[0]
            path = qs.get("path", ["README.md"])[0]
            return self._ok(
                {"path": path, "ref": ref, "content": get_file_text(owner, repo, ref, path)}
            )
        if u.path == "/repo/search":
            owner = qs.get("owner", [OWNER])[0]
            repo = qs.get("repo", [REPO])[0]
            ref = qs.get("ref", ["main"])[0]
            q = qs.get("q", [""])[0]
            return self._ok(code_search(owner, repo, q, ref))
        if u.path == "/repo/most_recent_branch":
            owner = qs.get("owner", [OWNER])[0]
            repo = qs.get("repo", [REPO])[0]
            if gh_most_recent_branch is not None:
                name = gh_most_recent_branch(owner, repo)
            else:
                # Fallback: return default branch only
                name = "main"
            return self._ok({"owner": owner, "repo": repo, "branch": name})
        return self._ok({"error": "not found"}, 404)

    def do_POST(self):
        """Write endpoints for branch/PR/merge lifecycle operations (IMP-011).

        The ``owner`` and ``repo`` are always taken from the server-configured
        :data:`OWNER` / :data:`REPO` environment variables — they are **never**
        read from the request body.  This prevents any user-controlled data from
        flowing into the GitHub API URL path (CodeQL partial-SSRF guard).
        """
        from urllib.parse import urlparse

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 1_048_576:  # 1 MB guard against DoS
            return self._ok(
                {
                    "error": (
                        "Request body exceeds 1 MB limit. "
                        "Please reduce payload size or contact administrator for a limit increase."
                    )
                },
                413,
            )
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body: dict[str, Any] = json.loads(raw_body) if raw_body.strip() else {}
        except json.JSONDecodeError as exc:
            return self._ok({"error": f"invalid JSON body: {exc}"}, 400)

        # owner and repo come exclusively from the server environment —
        # they are NEVER read from the request body to prevent SSRF.
        owner: str = OWNER
        repo: str = REPO

        u = urlparse(self.path)
        try:
            if u.path == "/repo/branches":
                # body: {branch, sha}
                branch = body.get("branch", "")
                sha = body.get("sha", "")
                if not branch or not sha:
                    return self._ok({"error": "branch and sha are required"}, 400)
                return self._ok(create_branch(owner, repo, branch, sha), 201)

            if u.path == "/repo/pulls":
                # body: {title, head, base?, body?, draft?}
                title = body.get("title", "")
                head = body.get("head", "")
                base = body.get("base", "main")
                if not title or not head:
                    return self._ok({"error": "title and head are required"}, 400)
                return self._ok(
                    open_pull_request(
                        owner, repo, title, head, base,
                        body=body.get("body", ""),
                        draft=bool(body.get("draft", False)),
                    ),
                    201,
                )

            if u.path == "/repo/merges":
                # body: {base, head, commit_message?}
                base = body.get("base", "")
                head = body.get("head", "")
                if not base or not head:
                    return self._ok({"error": "base and head are required"}, 400)
                return self._ok(
                    merge_branches(owner, repo, base, head, body.get("commit_message", "")),
                    201,
                )

        except ValueError as exc:
            return self._ok({"error": str(exc)}, 400)
        except Exception as exc:  # pragma: no cover
            return self._ok({"error": f"internal error: {exc}"}, 500)

        return self._ok({"error": "not found"}, 404)


if __name__ == "__main__":
    port = int(os.getenv("CODEX_ACTIONS_PORT", "8010"))
    print(f"[actions_server] Serving on http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), App).serve_forever()
