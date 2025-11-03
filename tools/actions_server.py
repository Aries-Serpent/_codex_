#!/usr/bin/env python3
"""
Minimal offline-first HTTP server to back CustomGPT Actions for _codex_.
Uses GitHub REST (token optional) and local cache. No CI, no secrets committed.
"""
from __future__ import annotations
import os, json, time, hashlib
from typing import Dict, Any
from urllib.parse import quote
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

try:
    # Optional: reuse shared client utilities if importable
    from src.codex_bridge.github_client import most_recent_branch as gh_most_recent_branch
except Exception:  # pragma: no cover - fallback
    gh_most_recent_branch = None

OWNER = os.getenv("CODEX_GH_OWNER", "Aries-Serpent")
REPO  = os.getenv("CODEX_GH_REPO", "_codex_")
TOKEN = os.getenv("CODEX_GITHUB_TOKEN", "")
BASE  = "https://api.github.com"
CACHE_DIR = os.getenv("CODEX_CACHE_DIR", ".codex/cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def _auth_headers() -> Dict[str, str]:
    h = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h

def _cache_get(key: str) -> Any | None:
    p = os.path.join(CACHE_DIR, hashlib.sha1(key.encode()).hexdigest()+".json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def _cache_set(key: str, data: Any, ttl: int = 60) -> None:
    # naive cache with timestamp; actions are human-in-the-loop so short TTL is fine
    obj = {"ts": time.time(), "data": data}
    p = os.path.join(CACHE_DIR, hashlib.sha1(key.encode()).hexdigest()+".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def gh_get(url: str):
    r = requests.get(url, headers=_auth_headers(), timeout=30)
    r.raise_for_status()
    return r.json()

def list_branches(owner: str, repo: str):
    key = f"branches:{owner}/{repo}"
    c = _cache_get(key)
    if c and time.time() - c["ts"] < 60:
        return c["data"]
    data = gh_get(f"{BASE}/repos/{owner}/{repo}/branches?per_page=100")
    _cache_set(key, data)
    return data

def get_file_text(owner: str, repo: str, ref: str, path: str) -> str:
    # Use raw endpoint; fallback to contents API
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{quote(ref)}/{path}"
    r = requests.get(raw, timeout=30)
    if r.status_code == 200 and r.text:
        return r.text
    meta = gh_get(f"{BASE}/repos/{owner}/{repo}/contents/{quote(path)}?ref={quote(ref)}")
    if isinstance(meta, dict) and meta.get("encoding") == "base64":
        import base64
        return base64.b64decode(meta["content"]).decode("utf-8", errors="replace")
    return json.dumps(meta, ensure_ascii=False)

def code_search(owner: str, repo: str, q: str, ref: str = "main"):
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

class App(BaseHTTPRequestHandler):
    def _ok(self, body: Any, code=200):
        b = body if isinstance(body, (str, bytes)) else json.dumps(body, ensure_ascii=False)
        if isinstance(b, str): b = b.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        u = urlparse(self.path); qs = parse_qs(u.query)
        if u.path == "/healthz":
            return self._ok({"ok": True, "ts": int(time.time())})
        if u.path == "/repo/branches":
            owner = qs.get("owner", [OWNER])[0]; repo = qs.get("repo", [REPO])[0]
            return self._ok(list_branches(owner, repo))
        if u.path == "/repo/files":
            owner = qs.get("owner", [OWNER])[0]; repo = qs.get("repo", [REPO])[0]
            ref = qs.get("ref", ["main"])[0]; path = qs.get("path", ["README.md"])[0]
            return self._ok({"path": path, "ref": ref, "content": get_file_text(owner, repo, ref, path)})
        if u.path == "/repo/search":
            owner = qs.get("owner", [OWNER])[0]; repo = qs.get("repo", [REPO])[0]
            ref = qs.get("ref", ["main"])[0]; q = qs.get("q", [""])[0]
            return self._ok(code_search(owner, repo, q, ref))
        if u.path == "/repo/most_recent_branch":
            owner = qs.get("owner", [OWNER])[0]; repo = qs.get("repo", [REPO])[0]
            if gh_most_recent_branch is not None:
                name = gh_most_recent_branch(owner, repo)
            else:
                # Fallback: return default branch only
                name = "main"
            return self._ok({"owner": owner, "repo": repo, "branch": name})
        return self._ok({"error": "not found"}, 404)

if __name__ == "__main__":
    port = int(os.getenv("CODEX_ACTIONS_PORT", "8010"))
    print(f"[actions_server] Serving on http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), App).serve_forever()
