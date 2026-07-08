"""
Tests for the GitHub App package.

Covers GitHubAppConfig, GitHubApp (JWT + token exchange), WebhookVerifier,
and the build_app_manifest helper.  Network calls are mocked so the suite
runs fully offline.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import unittest.mock as mock

import pytest  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

from codex.auth.exceptions import AuthenticationError
from codex.auth.github_app import (
    GitHubApp,
    GitHubAppConfig,
    InstallationToken,
    WebhookVerifier,
    _b64url,
    _b64url_bytes,
    _parse_iso8601,
    _resolve_github_token,
    build_app_manifest,
)

# ---------------------------------------------------------------------------
# RSA key fixture — 2048-bit key generated once for the whole test session
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def rsa_private_key_pem() -> str:
    """Generate a throwaway RSA-2048 private key (PEM) for tests."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


@pytest.fixture
def app_config(rsa_private_key_pem) -> GitHubAppConfig:
    return GitHubAppConfig(
        app_id=12345,
        private_key_pem=rsa_private_key_pem,
        webhook_secret="test-webhook-secret",
    )


@pytest.fixture
def github_app(app_config) -> GitHubApp:
    return GitHubApp(app_config)


# ---------------------------------------------------------------------------
# GitHubAppConfig
# ---------------------------------------------------------------------------


class TestGitHubAppConfig:

    def test_valid_config(self, rsa_private_key_pem):
        cfg = GitHubAppConfig(app_id=1, private_key_pem=rsa_private_key_pem)
        assert cfg.app_id == 1, "app_id is not valid"

    def test_invalid_app_id_raises(self, rsa_private_key_pem):
        with pytest.raises(ValueError, match="positive integer"):
            GitHubAppConfig(app_id=0, private_key_pem=rsa_private_key_pem)

    def test_missing_private_key_raises(self):
        with pytest.raises(ValueError, match="valid PEM-encoded"):
            GitHubAppConfig(app_id=1, private_key_pem="not-a-pem-key")

    def test_custom_api_base_url(self, rsa_private_key_pem):
        cfg = GitHubAppConfig(
            app_id=1,
            private_key_pem=rsa_private_key_pem,
            api_base_url="https://github.example.com/api/v3",
        )
        assert cfg.api_base_url == "https://github.example.com/api/v3", "api_base_url is not valid"


# ---------------------------------------------------------------------------
# JWT generation
# ---------------------------------------------------------------------------


class TestGenerateJWT:

    def test_jwt_has_three_segments(self, github_app):
        jwt = github_app.generate_jwt()
        parts = jwt.split(".")
        assert len(parts) == 3, "Parts must not be empty"

    def test_jwt_header_is_rs256(self, github_app):
        jwt = github_app.generate_jwt()
        header_b64 = jwt.split(".")[0]
        # Pad to multiple of 4
        padding = "=" * (-len(header_b64) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64 + padding))
        assert header["alg"] == "RS256", "Condition must be true"
        assert header["typ"] == "JWT", "Condition must be true"

    def test_jwt_payload_contains_iss(self, github_app):
        jwt = github_app.generate_jwt()
        payload_b64 = jwt.split(".")[1]
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
        assert payload["iss"] == str(github_app._config.app_id), "Condition must be true"

    def test_jwt_expiry_respected(self, github_app):
        jwt = github_app.generate_jwt(expiry_seconds=300)
        payload_b64 = jwt.split(".")[1]
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
        now = int(time.time())
        # exp should be roughly now + 300 (allow ±120 s for slow machines + back-date)
        assert payload["exp"] - now < 360, "now is not valid"

    def test_jwt_expiry_exceeds_max_raises(self, github_app):
        with pytest.raises(ValueError, match="expiry_seconds must"):
            github_app.generate_jwt(expiry_seconds=601)

    def test_jwt_signature_is_base64url(self, github_app):
        jwt = github_app.generate_jwt()
        sig = jwt.split(".")[2]
        # Should only contain base64url characters
        assert all(
            c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in sig
        ), "Condition must be true"


# ---------------------------------------------------------------------------
# Installation token (mocked HTTP)
# ---------------------------------------------------------------------------


class TestInstallationToken:

    def _make_mock_response(self, token: str, expires_delta: int = 3600) -> mock.MagicMock:
        from datetime import datetime, timedelta, timezone

        expires = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        body = json.dumps(
            {
                "token": token,
                "expires_at": expires.isoformat().replace("+00:00", "Z"),
                "permissions": {"contents": "read"},
                "repository_selection": "all",
            }
        ).encode("utf-8")
        resp = mock.MagicMock()
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = mock.MagicMock(return_value=False)
        return resp

    def test_fetch_installation_token(self, github_app):
        mock_resp = self._make_mock_response("ghs_testtoken123")
        with mock.patch("urllib.request.urlopen", return_value=mock_resp):
            token = github_app.get_installation_token(installation_id=999)
        assert token.token == "ghs_testtoken123", "token is not valid"
        assert token.installation_id == 999, "installation_id is not valid"
        assert token.permissions == {"contents": "read"}, "Content must not be empty"

    def test_token_cached(self, github_app):
        mock_resp = self._make_mock_response("ghs_cached")
        with mock.patch("urllib.request.urlopen", return_value=mock_resp) as m:
            github_app.get_installation_token(installation_id=777)
            github_app.get_installation_token(installation_id=777)
        # Should only have been fetched once
        assert m.call_count == 1, "Count must be greater than zero"

    def test_force_refresh_bypasses_cache(self, github_app):
        mock_resp = self._make_mock_response("ghs_refreshed")
        with mock.patch("urllib.request.urlopen", return_value=mock_resp) as m:
            github_app.get_installation_token(installation_id=888)
            github_app.get_installation_token(installation_id=888, force_refresh=True)
        assert m.call_count == 2, "Count must be greater than zero"

    def test_expired_token_refetched(self, github_app):
        mock_resp1 = self._make_mock_response("ghs_expired", expires_delta=-1)
        mock_resp2 = self._make_mock_response("ghs_new")
        with mock.patch("urllib.request.urlopen", side_effect=[mock_resp1, mock_resp2]):
            github_app.get_installation_token(installation_id=555)
            t2 = github_app.get_installation_token(installation_id=555)
        assert t2.token == "ghs_new", "token is not valid"

    def test_http_error_raises_auth_error(self, github_app):
        import urllib.error

        with (
            mock.patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.HTTPError(
                    url="", code=401, msg="Unauthorized", hdrs=None, fp=None
                ),
            ),
            pytest.raises(AuthenticationError, match="HTTP 401"),
        ):
            github_app.get_installation_token(installation_id=1)


# ---------------------------------------------------------------------------
# InstallationToken.is_expired
# ---------------------------------------------------------------------------


class TestInstallationTokenExpiry:

    def test_not_expired(self):
        t = InstallationToken(
            token="x",
            expires_at=time.time() + 3600,
            installation_id=1,
        )
        assert t.is_expired() is False, "Condition must be true"

    def test_expired(self):
        t = InstallationToken(
            token="x",
            expires_at=time.time() - 1,
            installation_id=1,
        )
        assert t.is_expired() is True, "Condition must be true"

    def test_expires_within_buffer(self):
        t = InstallationToken(
            token="x",
            expires_at=time.time() + 30,  # expires in 30 s
            installation_id=1,
        )
        assert t.is_expired(buffer_seconds=60) is True, "Condition must be true"


# ---------------------------------------------------------------------------
# WebhookVerifier
# ---------------------------------------------------------------------------


class TestWebhookVerifier:

    def test_compute_signature_format(self):
        v = WebhookVerifier("my-secret")
        sig = v.compute_signature(b"hello")
        assert sig.startswith("sha256="), "Condition must be true"

    def test_verify_valid_payload(self):
        secret = "webhook-secret-123"
        payload = b'{"action": "opened"}'
        # Compute expected signature
        expected_digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        header = f"sha256={expected_digest}"

        v = WebhookVerifier(secret)
        assert v.verify(payload, header) is True

    def test_verify_tampered_payload(self):
        v = WebhookVerifier("webhook-secret-123")
        payload = b'{"action": "opened"}'
        sig = v.compute_signature(payload)
        tampered = b'{"action": "closed"}'
        assert v.verify(tampered, sig) is False

    def test_verify_wrong_secret(self):
        payload = b"test-body"
        v_correct = WebhookVerifier("correct-secret")
        sig = v_correct.compute_signature(payload)
        v_wrong = WebhookVerifier("wrong-secret")
        assert v_wrong.verify(payload, sig) is False

    def test_verify_bad_header_format_raises(self):
        v = WebhookVerifier("secret")
        with pytest.raises(ValueError, match="sha256="):
            v.verify(b"payload", "md5=abcd1234")

    def test_empty_secret_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            WebhookVerifier("")

    def test_verify_empty_payload(self):
        v = WebhookVerifier("secret")
        sig = v.compute_signature(b"")
        assert v.verify(b"", sig) is True


# ---------------------------------------------------------------------------
# build_app_manifest
# ---------------------------------------------------------------------------


class TestBuildAppManifest:

    def test_returns_dict(self):
        m = build_app_manifest(
            name="codex-bot",
            url="https://example.com",
            webhook_url="https://example.com/webhook",
        )
        assert isinstance(m, dict)

    def test_required_fields_present(self):
        m = build_app_manifest(
            name="codex-bot",
            url="https://example.com",
            webhook_url="https://example.com/webhook",
        )
        assert m["name"] == "codex-bot", "Condition must be true"
        assert m["url"] == "https://example.com", "Condition must be true"
        assert m["hook_attributes"]["url"] == "https://example.com/webhook", "Condition must be true"
        assert "default_events" in m, "Condition must be true"
        assert "default_permissions" in m, "Condition must be true"

    def test_default_events_non_empty(self):
        m = build_app_manifest("x", "https://x.com", "https://x.com/wh")
        assert len(m["default_events"]) > 0, "Collection must not be empty"

    def test_default_permissions_non_empty(self):
        m = build_app_manifest("x", "https://x.com", "https://x.com/wh")
        assert "contents" in m["default_permissions"], "Content must not be empty"

    def test_description_truncated_to_255(self):
        m = build_app_manifest("x", "https://x.com", "https://x.com/wh", description="A" * 300)
        assert len(m["description"]) == 255, "Collection must not be empty"

    def test_custom_events(self):
        m = build_app_manifest("x", "https://x.com", "https://x.com/wh", default_events=["push"])
        assert m["default_events"] == ["push"], "Condition must be true"

    def test_custom_permissions(self):
        m = build_app_manifest(
            "x", "https://x.com", "https://x.com/wh", default_permissions={"issues": "write"}
        )
        assert m["default_permissions"] == {"issues": "write"}, "Condition must be true"

    def test_public_flag(self):
        m = build_app_manifest("x", "https://x.com", "https://x.com/wh", public=True)
        assert m["public"] is True, "Condition must be true"

    def test_callback_urls(self):
        m = build_app_manifest(
            "x",
            "https://x.com",
            "https://x.com/wh",
            callback_urls=["https://x.com/cb1", "https://x.com/cb2"],
        )
        assert "https://x.com/cb1" in m["callback_urls"], "Condition must be true"
        assert m["redirect_url"] == "https://x.com/cb1", "Condition must be true"

    def test_setup_url_included_when_provided(self):
        m = build_app_manifest(
            "x", "https://x.com", "https://x.com/wh", setup_url="https://x.com/setup"
        )
        assert m["setup_url"] == "https://x.com/setup", "Condition must be true"

    def test_no_setup_url_by_default(self):
        m = build_app_manifest("x", "https://x.com", "https://x.com/wh")
        assert "setup_url" not in m, "Condition must be true"

    def test_serialisable_to_json(self):
        m = build_app_manifest("codex-bot", "https://example.com", "https://example.com/webhook")
        # Should not raise
        encoded = json.dumps(m)
        assert "codex-bot" in encoded, "Condition must be true"


# ---------------------------------------------------------------------------
# Private utilities
# ---------------------------------------------------------------------------


class TestUtilities:

    def test_b64url_no_padding(self):
        result = _b64url("hello")
        assert "=" not in result, "Result must not be empty"

    def test_b64url_bytes_no_padding(self):
        result = _b64url_bytes(b"\x00\x01\x02")
        assert "=" not in result, "Result must not be empty"

    def test_parse_iso8601_utc_z(self):
        ts = _parse_iso8601("2024-01-15T12:00:00Z")
        from datetime import datetime, timezone

        expected = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp()
        assert abs(ts - expected) < 2, "Condition must be true"

    def test_parse_iso8601_empty_fallback(self):
        ts = _parse_iso8601("")
        assert ts > time.time(), "ts must be greater than zero"

    def test_parse_iso8601_invalid_fallback(self):
        with pytest.raises(ValueError):
            _parse_iso8601("not-a-date")


# ---------------------------------------------------------------------------
# Token-resolution fallback chain
# ---------------------------------------------------------------------------


class TestResolveGitHubToken:
    """Tests for CODEX_MASTER_KEY → CODEX_BACKUP_KEY → fallback chain."""

    def test_master_key_first(self, monkeypatch):
        monkeypatch.setenv("CODEX_MASTER_KEY", "master-token")
        monkeypatch.setenv("CODEX_BACKUP_KEY", "backup-token")
        tokens = _resolve_github_token()
        assert tokens[0] == ("master-token", "CODEX_MASTER_KEY")
        assert tokens[1] == ("backup-token", "CODEX_BACKUP_KEY")

    def test_backup_key_present_when_master_absent(self, monkeypatch):
        monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
        monkeypatch.setenv("CODEX_BACKUP_KEY", "backup-only")
        # _resolve_github_token returns [(value, name), ...]; swap for name→value lookup
        tokens = {name: value for value, name in _resolve_github_token()}
        assert tokens["CODEX_MASTER_KEY"] == "", "Condition must be true"
        assert tokens["CODEX_BACKUP_KEY"] == "backup-only", "Condition must be true"

    def test_fallback_uses_backup_on_401(self, github_app, monkeypatch):
        """pat_api_get retries with CODEX_BACKUP_KEY when master returns 401."""
        import urllib.error

        monkeypatch.setenv("CODEX_MASTER_KEY", "bad-master-key")
        monkeypatch.setenv("CODEX_BACKUP_KEY", "good-backup-key")
        monkeypatch.delenv("AGENT_GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        good_response_body = json.dumps({"id": 1, "name": "test-repo"}).encode()
        good_resp = mock.MagicMock()
        good_resp.read.return_value = good_response_body
        good_resp.__enter__ = lambda s: s
        good_resp.__exit__ = mock.MagicMock(return_value=False)

        call_count = 0

        def side_effect(req, timeout=30):
            nonlocal call_count
            call_count += 1
            auth = req.get_header("Authorization")
            if "bad-master-key" in auth:
                raise urllib.error.HTTPError(
                    url="", code=401, msg="Unauthorized", hdrs=None, fp=None
                )
            return good_resp

        with mock.patch("urllib.request.urlopen", side_effect=side_effect):
            result = github_app.pat_api_get("https://api.github.com/repos/Aries-Serpent/_codex_")

        assert result["name"] == "test-repo", "Result must not be empty"
        assert call_count == 2, "Count must be greater than zero"

    def test_all_tokens_fail_raises(self, github_app, monkeypatch):
        """pat_api_get raises AuthenticationError when all tokens are exhausted."""
        import urllib.error

        for var in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "AGENT_GITHUB_TOKEN", "GITHUB_TOKEN"):
            monkeypatch.setenv(var, "bad-token")

        def side_effect(req, timeout=30):
            raise urllib.error.HTTPError(url="", code=403, msg="Forbidden", hdrs=None, fp=None)

        with mock.patch("urllib.request.urlopen", side_effect=side_effect):
            with pytest.raises(AuthenticationError, match="exhausted"):
                github_app.pat_api_get("https://api.github.com/repos/Aries-Serpent/_codex_")
