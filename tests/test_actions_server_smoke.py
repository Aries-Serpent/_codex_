"""
Test Actions Server Smoke

Test module for actions server smoke.
"""

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest


def _get(port: int, path: str):
    url = f"http://127.0.0.1:{port}{path}"
    with urllib.request.urlopen(url, timeout=10) as r:  # nosec B310 -- loopback test server
        return r.status, json.loads(r.read().decode("utf-8"))


class _FakeGitHubResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


@pytest.mark.timeout(30)
def test_server_health_and_branches_smoke(tmp_path, monkeypatch):
    """Serve the real handler on an ephemeral loopback port; GitHub is faked.

    Previously this spawned ``tools/actions_server.py`` (moved to
    ``src/tools`` in 57cb3506ed) on fixed port 8010, polled it under
    ``freeze_time`` (so the wall-clock readiness loop never terminated), and
    hit the real GitHub API.  Binding port 0 in-process removes the port
    collision, start-up race, clock dependence and network dependence.
    """
    from tools import actions_server

    monkeypatch.setattr(actions_server, "CACHE_DIR", str(tmp_path))
    requested = []

    def fake_get(url, headers=None, timeout=None):
        requested.append(url)
        return _FakeGitHubResponse([{"name": "main"}, {"name": "dev"}])

    monkeypatch.setattr(actions_server.requests, "get", fake_get)

    server = ThreadingHTTPServer(("127.0.0.1", 0), actions_server.App)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, health = _get(port, "/healthz")
        assert status == 200, "healthz must return 200"
        assert health["ok"] is True, "healthz must report ok"
        assert isinstance(health["ts"], int), "healthz must report a timestamp"

        status, branches = _get(port, "/repo/branches?owner=Aries-Serpent&repo=_codex_")
        assert status == 200, "branches must return 200"
        assert branches == [{"name": "main"}, {"name": "dev"}], "branches payload mismatch"
        assert requested == [
            "https://api.github.com/repos/Aries-Serpent/_codex_/branches?per_page=100"
        ], "must query the GitHub branches endpoint exactly once"

        # Second call is served from the (tmp) cache, not GitHub.
        _, cached = _get(port, "/repo/branches?owner=Aries-Serpent&repo=_codex_")
        assert cached == branches, "cached payload mismatch"
        assert len(requested) == 1, "second call must hit the cache"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_assert_safe_github_url_requires_string():
    from tools import actions_server

    with pytest.raises(ValueError, match="must be a string"):
        actions_server._assert_safe_github_url(None)  # type: ignore[arg-type]


def test_gh_post_rejects_spoofed_github_url():
    from tools import actions_server

    with pytest.raises(ValueError, match="must target api.github.com"):
        actions_server.gh_post("https://api.github.com@evil.com/repos/owner/repo", {})
