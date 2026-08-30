"""Tests for security.providers.github_provider.GitHubTokenProvider.

All network calls are mocked — no live GitHub API traffic.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from security.providers.base import (
    ProviderConfig,
    ProviderType,
    RotationResult,
    SecretMetadata,
    SecretType,
    ValidationError,
)
from security.providers.github_provider import (
    _GITHUB_TOKEN_RE,
    _KNOWN_INSTALLATION_PERMISSIONS,
    GitHubTokenProvider,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_GHP = "ghp_" + "A" * 36  # classic PAT format
_FAKE_GHS = "ghs_" + "B" * 36  # installation token format


def _make_provider(token: str = _FAKE_GHP, **extra) -> GitHubTokenProvider:
    config = ProviderConfig(
        ProviderType.GITHUB,
        api_url="https://api.github.com",
        token=token,
        **extra,
    )
    return GitHubTokenProvider(config)


def _mock_response(status_code: int, json_data=None, text: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = text
    return resp


# ---------------------------------------------------------------------------
# Token regex
# ---------------------------------------------------------------------------


class TestGitHubTokenRegex:
    @pytest.mark.parametrize(
        "token",
        [
            "ghp_" + "A" * 36,
            "gho_" + "B" * 36,
            "ghs_" + "C" * 36,
            "ghu_" + "D" * 36,
            "ghr_" + "E" * 36,
            "a" * 40,  # 40-hex-char classic
        ],
    )
    def test_valid_tokens_match(self, token: str) -> None:
        assert _GITHUB_TOKEN_RE.match(token) is not None, "Value must be initialized"

    @pytest.mark.parametrize(
        "token",
        [
            "short",
            "ghp_tooshort",
            "not_a_token",
            "",
            "xyz_" + "A" * 36,
        ],
    )
    def test_invalid_tokens_no_match(self, token: str) -> None:
        assert _GITHUB_TOKEN_RE.match(token) is None, "Condition must be true"


# ---------------------------------------------------------------------------
# Known installation permissions
# ---------------------------------------------------------------------------


class TestKnownPermissions:
    def test_contains_common_permissions(self) -> None:
        assert "contents" in _KNOWN_INSTALLATION_PERMISSIONS, "Content must not be empty"
        assert "issues" in _KNOWN_INSTALLATION_PERMISSIONS, "Condition must be true"
        assert "pull_requests" in _KNOWN_INSTALLATION_PERMISSIONS, "Condition must be true"
        assert "actions" in _KNOWN_INSTALLATION_PERMISSIONS, "Condition must be true"
        assert "secrets" in _KNOWN_INSTALLATION_PERMISSIONS, "Condition must be true"

    def test_pat_scopes_not_included(self) -> None:
        # PAT-style scopes should not be in installation permissions
        assert "repo" not in _KNOWN_INSTALLATION_PERMISSIONS, "Condition must be true"
        assert "workflow" not in _KNOWN_INSTALLATION_PERMISSIONS, "Condition must be true"


# ---------------------------------------------------------------------------
# GitHubTokenProvider — construction
# ---------------------------------------------------------------------------


class TestGitHubTokenProviderConstruction:
    def test_provider_type(self) -> None:
        p = _make_provider()
        assert p.provider_type == ProviderType.GITHUB, "provider_type is not valid"

    def test_token_from_config(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        assert p.token == _FAKE_GHP, "token is not valid"

    def test_api_url_default(self) -> None:
        config = ProviderConfig(ProviderType.GITHUB, token=_FAKE_GHP)
        p = GitHubTokenProvider(config)
        assert p.api_url == "https://api.github.com", "api_url is not valid"

    def test_api_url_override(self) -> None:
        config = ProviderConfig(
            ProviderType.GITHUB,
            token=_FAKE_GHP,
            api_url="https://api.github.example.com",
        )
        p = GitHubTokenProvider(config)
        assert p.api_url == "https://api.github.example.com", "api_url is not valid"

    def test_token_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_TOKEN", _FAKE_GHP)
        config = ProviderConfig(ProviderType.GITHUB)
        p = GitHubTokenProvider(config)
        assert p.token == _FAKE_GHP, "token is not valid"

    def test_no_token_logs_warning(self, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        config = ProviderConfig(ProviderType.GITHUB)
        import logging

        with caplog.at_level(logging.WARNING, logger="security.providers.github_provider"):
            GitHubTokenProvider(config)
        assert any("not configured" in r.message.lower() for r in caplog.records), "Condition must be true"


# ---------------------------------------------------------------------------
# validate_secret
# ---------------------------------------------------------------------------


class TestValidateSecret:
    def test_no_token_raises_validation_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        config = ProviderConfig(ProviderType.GITHUB)
        p = GitHubTokenProvider(config)
        p.token = None
        with pytest.raises(ValidationError, match="No token provided"):
            p.validate_secret("tok-id")

    def test_invalid_format_returns_false(self) -> None:
        p = _make_provider(token="invalid_format")
        # Patch requests so it never hits network
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = _mock_response(200)
            result = p.validate_secret("tok-id", secret_value="not_a_real_token")
        assert result is False, "Result must not be empty"

    def test_valid_format_api_200_returns_true(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = _mock_response(200)
            result = p.validate_secret("tok-id")
        assert result is True, "Result must not be empty"

    def test_api_401_returns_false(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = _mock_response(401)
            result = p.validate_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_api_403_returns_false(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = _mock_response(403)
            result = p.validate_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_api_unexpected_status_returns_true(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = _mock_response(500)
            result = p.validate_secret("tok-id")
        assert result is True, "Result must not be empty"

    def test_network_error_degrades_gracefully(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.side_effect = ConnectionError("network down")
            result = p.validate_secret("tok-id")
        assert result is True, "Result must not be empty"

    def test_no_requests_lib_format_only(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = p.validate_secret("tok-id")
        assert result is True, "Result must not be empty"

    def test_explicit_secret_value_overrides_token(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = _mock_response(200)
            # Use explicit secret_value with valid format
            result = p.validate_secret("tok-id", secret_value=_FAKE_GHS)
        assert result is True, "Result must not be empty"

    def test_expired_token_returns_false(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        past = datetime.now(UTC) - timedelta(days=1)
        with patch.object(p, "get_expiration", return_value=past):
            with patch("security.providers.github_provider._requests"):
                result = p.validate_secret("tok-id")
        assert result is False, "Result must not be empty"


# ---------------------------------------------------------------------------
# get_secret_metadata
# ---------------------------------------------------------------------------


class TestGetSecretMetadata:
    def test_returns_secret_metadata(self) -> None:
        p = _make_provider()
        meta = p.get_secret_metadata("my-token")
        assert isinstance(meta, SecretMetadata)
        assert meta.secret_id == "my-token", "secret_id is not valid"
        assert meta.secret_type == SecretType.TOKEN, "secret_type is not valid"
        assert meta.provider == ProviderType.GITHUB, "provider is not valid"

    def test_expires_at_in_future(self) -> None:
        p = _make_provider()
        meta = p.get_secret_metadata("tok")
        assert meta.expires_at is not None, "expires_at must be initialized"
        assert meta.expires_at > datetime.now(UTC), "expires_at must be greater than zero"

    def test_has_scopes(self) -> None:
        p = _make_provider()
        meta = p.get_secret_metadata("tok")
        assert isinstance(meta.scopes, list)
        assert len(meta.scopes) > 0, "Collection must not be empty"


# ---------------------------------------------------------------------------
# get_expiration
# ---------------------------------------------------------------------------


class TestGetExpiration:
    def test_returns_datetime(self) -> None:
        p = _make_provider()
        exp = p.get_expiration("tok")
        assert isinstance(exp, datetime)

    def test_returns_none_on_exception(self) -> None:
        p = _make_provider()
        with patch.object(p, "get_secret_metadata", side_effect=RuntimeError("fail")):
            result = p.get_expiration("tok")
        assert result is None, "Result must not be empty"


# ---------------------------------------------------------------------------
# get_scopes
# ---------------------------------------------------------------------------


class TestGetScopes:
    def test_returns_list(self) -> None:
        p = _make_provider()
        scopes = p.get_scopes("tok")
        assert isinstance(scopes, list)

    def test_returns_empty_on_exception(self) -> None:
        p = _make_provider()
        with patch.object(p, "get_secret_metadata", side_effect=RuntimeError("fail")):
            result = p.get_scopes("tok")
        assert result == [], "Result must not be empty"


# ---------------------------------------------------------------------------
# create_token
# ---------------------------------------------------------------------------


class TestCreateToken:
    def test_no_installation_id_returns_failure(self) -> None:
        p = _make_provider()
        with patch.dict(os.environ, {}, clear=True):
            # Remove GITHUB_APP_INSTALLATION_ID from env
            os.environ.pop("GITHUB_APP_INSTALLATION_ID", None)
            result = p.create_token("test-token", scopes=["contents"])
        assert result.success is False, "Result must not be empty"
        assert "installation_id" in result.error_message.lower(), "Result must not be empty"

    def test_no_token_returns_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        config = ProviderConfig(
            ProviderType.GITHUB,
            api_url="https://api.github.com",
            installation_id="123",
        )
        p = GitHubTokenProvider(config)
        p.token = None
        result = p.create_token("test-token", scopes=["contents"])
        assert result.success is False, "Result must not be empty"
        assert "bearer token" in result.error_message.lower(), "Result must not be empty"

    def test_no_requests_returns_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = p.create_token("test-token", scopes=["contents"])
        assert result.success is False, "Result must not be empty"
        assert "requests" in result.error_message.lower(), "Result must not be empty"

    def test_invalid_permission_name_returns_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        result = p.create_token("test-token", scopes=["repo", "workflow"])
        assert result.success is False, "Result must not be empty"
        assert "Invalid installation permission" in result.error_message, "Result must not be empty"

    def test_successful_creation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        mock_resp = _mock_response(
            201,
            json_data={"token": _FAKE_GHS, "id": 42, "expires_at": "2030-01-01T00:00:00Z"},
        )
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.post.return_value = mock_resp
            result = p.create_token("test-token", scopes=["contents", "issues"])
        assert result.success is True, "Result must not be empty"
        assert result.new_secret_value == _FAKE_GHS, "Result must not be empty"
        assert result.new_secret_id == "42", "Result must not be empty"

    def test_api_error_status_returns_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        mock_resp = _mock_response(422, text="Unprocessable Entity")
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.post.return_value = mock_resp
            result = p.create_token("test-token", scopes=["contents"])
        assert result.success is False, "Result must not be empty"
        assert "422" in result.error_message, "Result must not be empty"

    def test_network_error_returns_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.post.side_effect = ConnectionError("timeout")
            result = p.create_token("test-token", scopes=["contents"])
        assert result.success is False, "Result must not be empty"

    def test_201_with_no_token_field_returns_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        mock_resp = _mock_response(201, json_data={"id": 99})  # no "token" key
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.post.return_value = mock_resp
            result = p.create_token("test-token", scopes=["contents"])
        assert result.success is False, "Result must not be empty"

    def test_empty_scopes_allowed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        mock_resp = _mock_response(201, json_data={"token": _FAKE_GHS, "id": 1})
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.post.return_value = mock_resp
            result = p.create_token("test-token", scopes=[])
        assert result.success is True, "Result must not be empty"


# ---------------------------------------------------------------------------
# update_token_scopes
# ---------------------------------------------------------------------------


class TestUpdateTokenScopes:
    def test_no_requests_returns_false(self) -> None:
        p = _make_provider()
        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = p.update_token_scopes("inst-123", ["contents"])
        assert result is False, "Result must not be empty"

    def test_no_token_returns_false(self) -> None:
        config = ProviderConfig(ProviderType.GITHUB, api_url="https://api.github.com")
        p = GitHubTokenProvider(config)
        p.token = None
        result = p.update_token_scopes("inst-123", ["contents"])
        assert result is False, "Result must not be empty"

    def test_success_200(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider()
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.patch.return_value = _mock_response(200)
            result = p.update_token_scopes("123", ["contents"])
        assert result is True, "Result must not be empty"

    def test_success_204(self) -> None:
        p = _make_provider(installation_id="123")
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.patch.return_value = _mock_response(204)
            result = p.update_token_scopes("123", ["issues"])
        assert result is True, "Result must not be empty"

    def test_api_error_returns_false(self) -> None:
        p = _make_provider(installation_id="123")
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.patch.return_value = _mock_response(403)
            result = p.update_token_scopes("123", ["contents"])
        assert result is False, "Result must not be empty"

    def test_exception_returns_false(self) -> None:
        p = _make_provider(installation_id="123")
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.patch.side_effect = OSError("network")
            result = p.update_token_scopes("123", ["contents"])
        assert result is False, "Result must not be empty"


# ---------------------------------------------------------------------------
# revoke_secret
# ---------------------------------------------------------------------------


class TestRevokeSecret:
    def test_no_token_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        config = ProviderConfig(ProviderType.GITHUB)
        p = GitHubTokenProvider(config)
        result = p.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_no_requests_returns_false(self) -> None:
        p = _make_provider(token=_FAKE_GHS)
        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = p.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_classic_pat_returns_false(self) -> None:
        p = _make_provider(token=_FAKE_GHP)
        result = p.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_installation_token_success(self) -> None:
        p = _make_provider(token=_FAKE_GHS)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.delete.return_value = _mock_response(204)
            result = p.revoke_secret("tok-id")
        assert result is True, "Result must not be empty"

    def test_installation_token_200_success(self) -> None:
        p = _make_provider(token=_FAKE_GHS)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.delete.return_value = _mock_response(200)
            result = p.revoke_secret("tok-id")
        assert result is True, "Result must not be empty"

    def test_installation_token_api_error_returns_false(self) -> None:
        p = _make_provider(token=_FAKE_GHS)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.delete.return_value = _mock_response(401)
            result = p.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"

    def test_exception_returns_false(self) -> None:
        p = _make_provider(token=_FAKE_GHS)
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.delete.side_effect = ConnectionError("timeout")
            result = p.revoke_secret("tok-id")
        assert result is False, "Result must not be empty"


# ---------------------------------------------------------------------------
# list_secrets
# ---------------------------------------------------------------------------


class TestListSecrets:
    def test_no_token_returns_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        config = ProviderConfig(ProviderType.GITHUB)
        p = GitHubTokenProvider(config)
        result = p.list_secrets()
        assert result == [], "Result must not be empty"

    def test_no_requests_returns_empty(self) -> None:
        p = _make_provider()
        with patch("security.providers.github_provider.HAS_REQUESTS", False):
            result = p.list_secrets()
        assert result == [], "Result must not be empty"

    def test_success_200_returns_metadata(self) -> None:
        p = _make_provider()
        mock_resp = _mock_response(200, json_data={"login": "testuser"})
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            result = p.list_secrets()
        assert len(result) == 1, "Result must not be empty"
        meta = result[0]
        assert isinstance(meta, SecretMetadata)
        assert meta.tags["github_login"] == "testuser", "Condition must be true"

    def test_api_error_returns_empty(self) -> None:
        p = _make_provider()
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = _mock_response(401)
            result = p.list_secrets()
        assert result == [], "Result must not be empty"

    def test_exception_returns_empty(self) -> None:
        p = _make_provider()
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.side_effect = OSError("no network")
            result = p.list_secrets()
        assert result == [], "Result must not be empty"

    def test_filter_tags_accepted(self) -> None:
        p = _make_provider()
        mock_resp = _mock_response(200, json_data={"login": "user"})
        with patch("security.providers.github_provider._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            result = p.list_secrets(filter_tags={"env": "prod"})
        assert len(result) == 1, "Result must not be empty"


# ---------------------------------------------------------------------------
# rotate_secret
# ---------------------------------------------------------------------------


class TestRotateSecret:
    def test_rotation_delegates_to_create_and_returns_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        new_token = _FAKE_GHS
        create_result = RotationResult(
            success=True,
            old_secret_id="",
            new_secret_id="999",
            new_secret_value=new_token,
        )
        with patch.object(p, "create_token", return_value=create_result):
            result = p.rotate_secret("my-token")
        assert result.success is True, "Result must not be empty"
        assert result.new_secret_value == new_token, "Result must not be empty"

    def test_rotation_with_revoke_old(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "123")
        p = _make_provider(installation_id="123")
        create_result = RotationResult(
            success=True,
            old_secret_id="",
            new_secret_id="1",
            new_secret_value=_FAKE_GHS,
        )
        with patch.object(p, "create_token", return_value=create_result):
            with patch.object(p, "revoke_secret", return_value=True) as mock_revoke:
                result = p.rotate_secret("my-token", revoke_old=True)
        assert result.success is True, "Result must not be empty"
        mock_revoke.assert_called_once_with("my-token")

    def test_rotation_failure_propagates(self) -> None:
        p = _make_provider()
        create_result = RotationResult(
            success=False,
            old_secret_id="",
            error_message="cannot create",
        )
        with patch.object(p, "create_token", return_value=create_result):
            result = p.rotate_secret("my-token")
        assert result.success is False, "Result must not be empty"
        assert result.error_message == "cannot create", "Result must not be empty"

    def test_rotation_exception_returns_failure(self) -> None:
        p = _make_provider()
        with patch.object(p, "get_secret_metadata", side_effect=RuntimeError("boom")):
            result = p.rotate_secret("my-token")
        assert result.success is False, "Result must not be empty"
        assert "boom" in result.error_message, "Result must not be empty"
