"""
Tests for src/codex/agents/brain_client.py

Covers:
- URL resolution order (CODEX_CLI_API_URL → COPILOT_CLI_BASE_URL → default)
- _auth_header() with/without env vars, strip() on whitespace
- is_available() via mocked urlopen
- run_command(), proxy_request(), memory_state(), memory_search() with mock responses
- BrainClientError raised on HTTP errors and network errors
- Convenience helpers: git_status, git_log, github_repo_info, github_workflow_runs
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from codex.agents.brain_client import _DEFAULT_URL, BrainClient, BrainClientError

# All env vars consulted by BrainClient._auth_header() — must be excluded
# in tests that assert "no auth header".
_AUTH_ENV_VARS = frozenset(
    {
        "CODEX_MASTER_KEY",
        "CODEX_BACKUP_KEY",
        "AGENT_GITHUB_TOKEN",
        "GITHUB_TOKEN",
    }
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(body: Any, status: int = 200) -> MagicMock:
    """Return a mock response object compatible with urllib.request.urlopen."""
    raw = json.dumps(body).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = raw
    mock_resp.status = status
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def _http_error(code: int, msg: str = "Error") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="http://x",
        code=code,
        msg=msg,
        hdrs=None,
        fp=BytesIO(b"error body"),  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------


class TestUrlResolution:
    def test_explicit_base_url_wins(self) -> None:
        b = BrainClient(base_url="http://custom:9999")
        assert b.base_url == "http://custom:9999", "base_url is not valid"

    def test_explicit_base_url_strips_trailing_slash(self) -> None:
        b = BrainClient(base_url="http://custom:9999/")
        assert b.base_url == "http://custom:9999", "base_url is not valid"

    def test_codex_cli_api_url_env_var(self) -> None:
        with patch.dict(os.environ, {"CODEX_CLI_API_URL": "http://env-url:8000"}, clear=False):
            b = BrainClient()
        assert b.base_url == "http://env-url:8000", "base_url is not valid"

    def test_copilot_cli_base_url_fallback(self) -> None:
        env = {"COPILOT_CLI_BASE_URL": "http://copilot-url:7777"}
        with patch.dict(os.environ, env, clear=False):
            # Ensure CODEX_CLI_API_URL is not set
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("CODEX_CLI_API_URL", None)
                b = BrainClient()
        assert b.base_url == "http://copilot-url:7777", "base_url is not valid"

    def test_default_url_when_no_env(self) -> None:
        env_copy = {
            k: v
            for k, v in os.environ.items()
            if k not in ("CODEX_CLI_API_URL", "COPILOT_CLI_BASE_URL")
        }
        with patch.dict(os.environ, env_copy, clear=True):
            b = BrainClient()
        assert b.base_url == _DEFAULT_URL, "base_url is not valid"

    def test_codex_cli_api_url_takes_priority_over_copilot(self) -> None:
        env = {
            "CODEX_CLI_API_URL": "http://primary:8765",
            "COPILOT_CLI_BASE_URL": "http://secondary:7777",
        }
        with patch.dict(os.environ, env, clear=False):
            b = BrainClient()
        assert b.base_url == "http://primary:8765", "base_url is not valid"


# ---------------------------------------------------------------------------
# _auth_header
# ---------------------------------------------------------------------------


class TestAuthHeader:
    def test_master_key_used_when_set(self) -> None:
        with patch.dict(
            os.environ, {"CODEX_MASTER_KEY": "masterkey123", "CODEX_BACKUP_KEY": ""}, clear=False
        ):
            b = BrainClient(base_url="http://x")
            hdr = b._auth_header()
        assert hdr == {"Authorization": "Bearer masterkey123"}, "hdr is not valid"

    def test_backup_key_fallback(self) -> None:
        env_copy = {k: v for k, v in os.environ.items() if k != "CODEX_MASTER_KEY"}
        env_copy["CODEX_BACKUP_KEY"] = "backupkey456"
        with patch.dict(os.environ, env_copy, clear=True):
            b = BrainClient(base_url="http://x")
            hdr = b._auth_header()
        assert hdr == {"Authorization": "Bearer backupkey456"}, "hdr is not valid"

    def test_empty_when_no_keys(self) -> None:
        env_copy = {k: v for k, v in os.environ.items() if k not in _AUTH_ENV_VARS}
        with patch.dict(os.environ, env_copy, clear=True):
            b = BrainClient(base_url="http://x")
            hdr = b._auth_header()
        assert hdr == {}, "hdr is not valid"

    def test_whitespace_only_key_ignored(self) -> None:
        env_copy = {k: v for k, v in os.environ.items() if k not in _AUTH_ENV_VARS}
        env_copy.update({"CODEX_MASTER_KEY": "   ", "CODEX_BACKUP_KEY": ""})
        with patch.dict(os.environ, env_copy, clear=True):
            b = BrainClient(base_url="http://x")
            hdr = b._auth_header()
        assert hdr == {}, "hdr is not valid"

    def test_master_key_stripped(self) -> None:
        with patch.dict(
            os.environ, {"CODEX_MASTER_KEY": "  trimmed  ", "CODEX_BACKUP_KEY": ""}, clear=False
        ):
            b = BrainClient(base_url="http://x")
            hdr = b._auth_header()
        assert hdr == {"Authorization": "Bearer trimmed"}, "hdr is not valid"


# ---------------------------------------------------------------------------
# is_available
# ---------------------------------------------------------------------------


class TestIsAvailable:
    def test_true_when_server_healthy(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response({"status": "ok"})):
            assert b.is_available() is True, "Condition must be true"

    def test_false_when_server_returns_non_ok(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response({"status": "degraded"})):
            assert b.is_available() is False, "Condition must be true"

    def test_false_when_network_error(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=OSError("refused")):
            assert b.is_available() is False, "Condition must be true"

    def test_false_when_http_error(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=_http_error(503)):
            assert b.is_available() is False, "Condition must be true"


# ---------------------------------------------------------------------------
# health()
# ---------------------------------------------------------------------------


class TestHealth:
    def test_returns_health_dict(self) -> None:
        payload = {
            "status": "ok",
            "repo_root": "/repo",
            "timestamp": "2026-03-04T00:00:00",
            "history_db": "/db",
        }
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(payload)):
            result = b.health()
        assert result["status"] == "ok", "Result must not be empty"
        assert result["repo_root"] == "/repo", "Result must not be empty"

    def test_raises_on_http_error(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=_http_error(500)):
            with pytest.raises(BrainClientError, match="HTTP 500"):
                b.health()

    def test_raises_on_network_error(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
            with pytest.raises(BrainClientError, match="unreachable"):
                b.health()


# ---------------------------------------------------------------------------
# run_command()
# ---------------------------------------------------------------------------


class TestRunCommand:
    def _run_response(self, cmd: str, stdout: str = "", rc: int = 0) -> dict:
        return {
            "command": cmd,
            "stdout": stdout,
            "stderr": "",
            "returncode": rc,
            "duration_ms": 5.0,
            "cwd": "/repo",
            "timestamp": "2026-03-04T00:00:00",
        }

    def test_basic_command(self) -> None:
        b = BrainClient(base_url="http://x")
        payload = self._run_response("git status --short", "M file.py")
        with patch("urllib.request.urlopen", return_value=_make_response(payload)):
            result = b.run_command("git status --short")
        assert result["stdout"] == "M file.py", "Result must not be empty"
        assert result["returncode"] == 0, "Result must not be empty"

    def test_passes_cwd_and_env(self) -> None:
        b = BrainClient(base_url="http://x")
        payload = self._run_response("echo hi", "hi")
        captured_body = {}

        def fake_urlopen(req, timeout=None):
            body = json.loads(req.data.decode())
            captured_body.update(body)
            return _make_response(payload)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            b.run_command("echo hi", cwd="/tmp", env={"FOO": "bar"})

        assert captured_body["cwd"] == "/tmp", "Condition must be true"
        assert captured_body["env"] == {"FOO": "bar"}, "Condition must be true"

    def test_raises_on_http_error(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=_http_error(400)):
            with pytest.raises(BrainClientError, match="HTTP 400"):
                b.run_command("bad command")


# ---------------------------------------------------------------------------
# proxy_request()
# ---------------------------------------------------------------------------


class TestProxyRequest:
    def _proxy_response(self, status: int = 200, body: Any = None) -> dict:
        return {
            "status_code": status,
            "headers": {},
            "body": body or {},
            "duration_ms": 100.0,
            "url": "https://api.github.com/repos/x",
            "method": "GET",
        }

    def test_get_request(self) -> None:
        b = BrainClient(base_url="http://x")
        payload = self._proxy_response(200, {"name": "_codex_"})
        with patch("urllib.request.urlopen", return_value=_make_response(payload)):
            result = b.proxy_request("GET", "https://api.github.com/repos/Aries-Serpent/_codex_")
        assert result["status_code"] == 200, "Result must not be empty"
        assert result["body"]["name"] == "_codex_", "Result must not be empty"

    def test_method_uppercased(self) -> None:
        b = BrainClient(base_url="http://x")
        captured_body = {}

        def fake_urlopen(req, timeout=None):
            body = json.loads(req.data.decode())
            captured_body.update(body)
            return _make_response(self._proxy_response(200))

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            b.proxy_request("get", "https://example.com")

        assert captured_body["method"] == "GET", "Condition must be true"

    def test_passes_params_and_body(self) -> None:
        b = BrainClient(base_url="http://x")
        captured_body = {}

        def fake_urlopen(req, timeout=None):
            body = json.loads(req.data.decode())
            captured_body.update(body)
            return _make_response(self._proxy_response(201))

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            b.proxy_request("POST", "https://example.com", params={"p": "1"}, body={"key": "val"})

        assert captured_body["params"] == {"p": "1"}, "Condition must be true"
        assert captured_body["body"] == {"key": "val"}, "Condition must be true"

    def test_raises_on_http_error(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=_http_error(502)):
            with pytest.raises(BrainClientError, match="HTTP 502"):
                b.proxy_request("GET", "https://example.com")


# ---------------------------------------------------------------------------
# memory_state() — auth required
# ---------------------------------------------------------------------------


class TestMemoryState:
    def test_returns_memory_dict(self) -> None:
        payload = {
            "stm_count": 5,
            "ltm_count": 2,
            "capacity": 1000,
            "cache_hit_rate": 0.4,
            "compression_rate": 0.28,
            "patterns": [],
            "timestamp": "2026-03-04T00:00:00",
        }
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(payload)):
            result = b.memory_state()
        assert result["stm_count"] == 5, "Result must not be empty"
        assert result["ltm_count"] == 2, "Result must not be empty"

    def test_raises_on_401(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=_http_error(401)):
            with pytest.raises(BrainClientError, match="HTTP 401"):
                b.memory_state()

    def test_raises_on_503_no_auth_configured(self) -> None:
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", side_effect=_http_error(503)):
            with pytest.raises(BrainClientError, match="HTTP 503"):
                b.memory_state()


# ---------------------------------------------------------------------------
# memory_search()
# ---------------------------------------------------------------------------


class TestMemorySearch:
    def test_url_encodes_query(self) -> None:
        b = BrainClient(base_url="http://x")
        captured_urls = []

        def fake_urlopen(req, timeout=None):
            captured_urls.append(req.full_url)
            return _make_response({"items": [], "total": 0})

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            b.memory_search("D_CAPABLE test", limit=10)

        assert len(captured_urls) == 1, "Captured_urls must not be empty"
        assert "D_CAPABLE+test" in captured_urls[0] or "D_CAPABLE%20test" in captured_urls[0], "Condition must be true"
        assert "limit=10" in captured_urls[0], "Condition must be true"

    def test_returns_items(self) -> None:
        payload = {"items": [{"key": "k1", "value": "v1", "tier": "stm"}], "total": 1}
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(payload)):
            result = b.memory_search("k1")
        assert result["total"] == 1, "Result must not be empty"
        assert result["items"][0]["key"] == "k1", "Result must not be empty"


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


class TestConvenienceHelpers:
    def test_git_status_returns_string(self) -> None:
        payload = {
            "command": "git status --short",
            "stdout": "M src/foo.py\n",
            "stderr": "",
            "returncode": 0,
            "duration_ms": 5.0,
            "cwd": "/repo",
            "timestamp": "2026-03-04T00:00:00",
        }
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(payload)):
            result = b.git_status()
        assert result == "M src/foo.py", "Result must not be empty"

    def test_git_log_returns_list(self) -> None:
        payload = {
            "command": "git --no-pager log --oneline -5",
            "stdout": "abc1234 First commit\ndef5678 Second commit\n",
            "stderr": "",
            "returncode": 0,
            "duration_ms": 6.0,
            "cwd": "/repo",
            "timestamp": "2026-03-04T00:00:00",
        }
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(payload)):
            result = b.git_log(5)
        assert isinstance(result, list)
        assert len(result) == 2, "Result must not be empty"
        assert "abc1234" in result[0], "Result must not be empty"

    def test_github_repo_info_extracts_body(self) -> None:
        proxy_payload = {
            "status_code": 200,
            "headers": {},
            "body": {"name": "_codex_", "default_branch": "main"},
            "duration_ms": 200.0,
            "url": "https://api.github.com/repos/x/_codex_",
            "method": "GET",
        }
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(proxy_payload)):
            result = b.github_repo_info()
        assert result["name"] == "_codex_", "Result must not be empty"
        assert result["default_branch"] == "main", "Result must not be empty"

    def test_github_workflow_runs_extracts_list(self) -> None:
        proxy_payload = {
            "status_code": 200,
            "headers": {},
            "body": {"workflow_runs": [{"id": 1, "name": "CI", "conclusion": "success"}]},
            "duration_ms": 200.0,
            "url": "https://api.github.com/repos/x/_codex_/actions/runs",
            "method": "GET",
        }
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(proxy_payload)):
            result = b.github_workflow_runs(per_page=1)
        assert len(result) == 1, "Result must not be empty"
        assert result[0]["name"] == "CI", "Result must not be empty"

    def test_github_workflow_runs_empty_on_bad_body(self) -> None:
        proxy_payload = {
            "status_code": 200,
            "headers": {},
            "body": "not a dict",
            "duration_ms": 10.0,
            "url": "https://x",
            "method": "GET",
        }
        b = BrainClient(base_url="http://x")
        with patch("urllib.request.urlopen", return_value=_make_response(proxy_payload)):
            result = b.github_workflow_runs()
        assert result == [], "Result must not be empty"


# ---------------------------------------------------------------------------
# URL validation in __init__
# ---------------------------------------------------------------------------


class TestBaseUrlValidation:
    def test_bare_host_port_normalised_to_http(self) -> None:
        b = BrainClient(base_url="localhost:8765")
        assert b.base_url == "http://localhost:8765", "base_url is not valid"

    def test_invalid_scheme_raises(self) -> None:
        with pytest.raises(BrainClientError, match="Invalid base URL"):
            BrainClient(base_url="ftp://bad-scheme:8765")

    def test_no_netloc_raises(self) -> None:
        with pytest.raises(BrainClientError, match="Invalid base URL"):
            BrainClient(base_url="http://")

    def test_valid_https_accepted(self) -> None:
        b = BrainClient(base_url="https://remote-brain.example.com:9000")
        assert b.base_url == "https://remote-brain.example.com:9000", "base_url is not valid"


# ---------------------------------------------------------------------------
# Auth header actually sent on requests (regression guard)
# ---------------------------------------------------------------------------


class TestAuthHeaderSentOnRequests:
    """Verify that Authorization is included in the outgoing Request when a
    key is configured.  These tests catch the regression where _auth_header()
    was defined but never applied in _get / _post / _delete."""

    def _capture_headers(self, response_body: Any):
        """Return (captured_headers, mock side-effect) pair."""
        captured: list = []

        def fake_urlopen(req, timeout=None):
            captured.append(dict(req.headers))
            return _make_response(response_body)

        return captured, fake_urlopen

    def test_memory_state_sends_auth_header(self) -> None:
        payload = {
            "stm_count": 1,
            "ltm_count": 0,
            "capacity": 100,
            "cache_hit_rate": 0.0,
            "compression_rate": 0.0,
            "patterns": [],
            "timestamp": "2026-03-04T00:00:00",
        }
        captured, fake = self._capture_headers(payload)
        with patch.dict(os.environ, {"CODEX_MASTER_KEY": "secretkey"}, clear=False):
            b = BrainClient(base_url="http://x")
            with patch("urllib.request.urlopen", side_effect=fake):
                b.memory_state()
        assert len(captured) == 1, "Captured must not be empty"
        # urllib capitalises the first letter of each header word
        auth = captured[0].get("Authorization") or captured[0].get("authorization")
        assert auth == "Bearer secretkey", "auth is not valid"

    def test_memory_search_sends_auth_header(self) -> None:
        captured, fake = self._capture_headers({"items": [], "total": 0})
        with patch.dict(os.environ, {"CODEX_MASTER_KEY": "searchkey"}, clear=False):
            b = BrainClient(base_url="http://x")
            with patch("urllib.request.urlopen", side_effect=fake):
                b.memory_search("test query")
        assert len(captured) == 1, "Captured must not be empty"
        auth = captured[0].get("Authorization") or captured[0].get("authorization")
        assert auth == "Bearer searchkey", "auth is not valid"

    def test_no_auth_header_when_no_key(self) -> None:
        captured, fake = self._capture_headers({"status": "ok"})
        env_copy = {k: v for k, v in os.environ.items() if k not in _AUTH_ENV_VARS}
        with patch.dict(os.environ, env_copy, clear=True):
            b = BrainClient(base_url="http://x")
            with patch("urllib.request.urlopen", side_effect=fake):
                b.health()
        assert len(captured) == 1, "Captured must not be empty"
        auth = captured[0].get("Authorization") or captured[0].get("authorization")
        assert auth is None, "auth is not valid"

    def test_backup_key_sent_when_master_absent(self) -> None:
        payload = {
            "stm_count": 0,
            "ltm_count": 0,
            "capacity": 100,
            "cache_hit_rate": 0.0,
            "compression_rate": 0.0,
            "patterns": [],
            "timestamp": "2026-03-04T00:00:00",
        }
        captured, fake = self._capture_headers(payload)
        env_copy = {k: v for k, v in os.environ.items() if k != "CODEX_MASTER_KEY"}
        env_copy["CODEX_BACKUP_KEY"] = "backuptoken"
        with patch.dict(os.environ, env_copy, clear=True):
            b = BrainClient(base_url="http://x")
            with patch("urllib.request.urlopen", side_effect=fake):
                b.memory_state()
        assert len(captured) == 1, "Captured must not be empty"
        auth = captured[0].get("Authorization") or captured[0].get("authorization")
        assert auth == "Bearer backuptoken", "auth is not valid"
