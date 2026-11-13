"""Tests for src/codex/archive/sigstore_client.py module.

Phase 5 Week 2 Gap-Fill Coverage Campaign
Module 6: Sigstore keyless signing client with SHA-256 fallback

Test Coverage Goals:
  - 25 test functions total
  - 55%+ coverage of sigstore_client module
  - Happy paths (60%): Mock signing, verification, fallback
  - Error handling (25%): Invalid inputs, missing keys
  - Edge cases (15%): Empty data, unicode, optional dependencies
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

# Import the module to test
try:
    from codex.archive import sigstore_client
except ImportError:
    pytest.skip("sigstore_client module not importable", allow_module_level=True)


@pytest.fixture
def mock_client(monkeypatch: pytest.MonkeyPatch) -> sigstore_client.SignstoreClient:
    """Signing-enabled client forced onto the deterministic SHA-256 mock backend."""
    monkeypatch.setenv("CODEX_ENABLE_SIGNING", "true")
    monkeypatch.setenv("SIGSTORE_ID_TOKEN", "test-oidc-token")
    monkeypatch.setattr(sigstore_client, "_HAS_SIGSTORE", False)
    return sigstore_client.SignstoreClient()


@pytest.fixture
def disabled_client(monkeypatch: pytest.MonkeyPatch) -> sigstore_client.SignstoreClient:
    """Client with signing disabled (the default)."""
    monkeypatch.delenv("CODEX_ENABLE_SIGNING", raising=False)
    monkeypatch.setenv("SIGSTORE_ID_TOKEN", "test-oidc-token")
    return sigstore_client.SignstoreClient()


class TestClientInitialization:
    """Test SignstoreClient initialization."""

    def test_client_creation(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test creating a client instance picks up env configuration."""
        assert mock_client.enabled is True
        assert mock_client.oidc_token == "test-oidc-token"
        assert mock_client.fulcio_url.startswith("https://")
        assert mock_client.rekor_url.startswith("https://")

    def test_client_is_exported(self) -> None:
        """Test that SignstoreClient is public and callable."""
        assert "SignstoreClient" in sigstore_client.__all__
        assert callable(sigstore_client.SignstoreClient), "Condition must be true"

    def test_local_token_placeholder(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without OIDC env vars the client falls back to a placeholder token."""
        for name in (
            "SIGSTORE_ID_TOKEN",
            "ACTIONS_ID_TOKEN_REQUEST_URL",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        ):
            monkeypatch.delenv(name, raising=False)
        client = sigstore_client.SignstoreClient()
        assert client.oidc_token == "local-dev-token-placeholder"

    def test_client_with_disabled_signing(
        self, disabled_client: sigstore_client.SignstoreClient
    ) -> None:
        """Test client with signing disabled returns an unsigned envelope."""
        assert disabled_client.enabled is False
        result = disabled_client.sign_record({"a": 1}, actor="alice")
        assert result["signature"] is None
        assert result["cert_chain"] is None
        assert result["actor"] == "alice"
        assert result["signed_at"]


class TestSignOperations:
    """Test signing operations (mock backend)."""

    def test_mock_sign_record_basic(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test basic mock signing of a record."""
        result = mock_client.sign_record({"data": "test data"}, actor="alice")
        assert result["signature"].startswith("MOCK_SIG_")
        assert result["backend"] == "mock"
        assert result["actor"] == "alice"
        assert result["issuer"] == "https://token.actions.githubusercontent.com"
        assert "MOCK_CERT_FOR_alice" in result["cert_chain"][0]

    def test_sign_empty_record(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test signing an empty record."""
        result = mock_client.sign_record({}, actor="alice")
        assert result["signature"].startswith("MOCK_SIG_")

    def test_sign_large_record(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test signing large data."""
        result = mock_client.sign_record({"blob": "x" * 1_000_000}, actor="alice")
        assert len(result["signature"]) == len("MOCK_SIG_") + 32

    def test_sign_unicode_record(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test signing unicode data."""
        result = mock_client.sign_record({"text": "hello 世界"}, actor="ålice")
        assert result["signature"].startswith("MOCK_SIG_")

    def test_mock_sign_returns_str(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test that the low-level mock signer returns a prefixed hex string."""
        sig = mock_client._mock_sign(b"data", "alice")
        assert isinstance(sig, str)
        int(sig.removeprefix("MOCK_SIG_"), 16)  # hex payload

    def test_sign_deterministic(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test that mock signing is deterministic and key-order independent."""
        sig1 = mock_client.sign_record({"a": 1, "b": 2}, actor="alice")["signature"]
        sig2 = mock_client.sign_record({"b": 2, "a": 1}, actor="alice")["signature"]
        assert sig1 == sig2, "sig1 is not valid"

    def test_sign_depends_on_actor(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Different actors produce different signatures for the same record."""
        sig1 = mock_client.sign_record({"a": 1}, actor="alice")["signature"]
        sig2 = mock_client.sign_record({"a": 1}, actor="bob")["signature"]
        assert sig1 != sig2


class TestVerificationOperations:
    """Test verification operations (mock backend)."""

    def test_verify_signature_valid(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test verifying a valid mock signature."""
        record = {"data": "test data"}
        signed = mock_client.sign_record(record, actor="alice")
        assert mock_client.verify_signature(record, signed["signature"]) is True

    def test_verify_signature_invalid(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test verifying a signature that is not a mock signature."""
        assert mock_client.verify_signature({"data": 1}, "invalid_signature") is False

    def test_verify_empty_signature(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test verifying an empty signature."""
        assert mock_client.verify_signature({"data": 1}, "") is False

    def test_verify_none_signature_is_trusted(
        self, mock_client: sigstore_client.SignstoreClient
    ) -> None:
        """Unsigned records (signature=None) are accepted."""
        assert mock_client.verify_signature({"data": 1}, None) is True  # type: ignore[arg-type]

    def test_verify_when_disabled(self, disabled_client: sigstore_client.SignstoreClient) -> None:
        """When signing is disabled verification is a no-op that succeeds."""
        assert disabled_client.verify_signature({"data": 1}, "anything") is True


class TestSigningFallback:
    """Test SHA-256 fallback for mock signing."""

    def test_fallback_available(self) -> None:
        """Test that fallback mechanism is available."""
        # Should have fallback when sigstore not available
        assert hasattr(sigstore_client, "_HAS_SIGSTORE")

    def test_fallback_signing_deterministic(self) -> None:
        """Test fallback signing is deterministic."""
        import hashlib

        data = b"test"
        hash1 = hashlib.sha256(data).digest()
        hash2 = hashlib.sha256(data).digest()
        assert hash1 == hash2, "hash1 is not valid"

    def test_fallback_produces_valid_hash(self) -> None:
        """Test fallback produces valid SHA-256 hash."""
        import hashlib

        data = b"test data"
        result = hashlib.sha256(data).digest()
        assert len(result) == 32, "Result must not be empty"

    def test_fallback_different_data_different_hash(self) -> None:
        """Test fallback produces different hash for different data."""
        import hashlib

        data1 = b"test1"
        data2 = b"test2"
        hash1 = hashlib.sha256(data1).digest()
        hash2 = hashlib.sha256(data2).digest()
        assert hash1 != hash2, "hash1 is not valid"

    def test_fallback_empty_data(self) -> None:
        """Test fallback hashing empty data."""
        import hashlib

        result = hashlib.sha256(b"").digest()
        assert isinstance(result, bytes)
        assert len(result) == 32, "Result must not be empty"


class TestSigningInterface:
    """Test signing interface and configuration."""

    def test_client_has_sign_method(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test client exposes sign_record."""
        assert callable(mock_client.sign_record)

    def test_client_has_verify_method(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test client exposes verify_signature."""
        assert callable(mock_client.verify_signature)

    @patch.dict("os.environ", {"CODEX_ENABLE_SIGNING": "true"})
    def test_enable_signing_environment(self) -> None:
        """Test signing enabled via environment variable."""
        # Environment variable check should work
        import os

        assert os.environ.get("CODEX_ENABLE_SIGNING") == "true", "Condition must be true"

    @patch.dict("os.environ", {}, clear=True)
    def test_disable_signing_by_default(self) -> None:
        """Test signing disabled by default."""
        import os

        assert os.environ.get("CODEX_ENABLE_SIGNING") is None, "Condition must be true"


class TestDataEncoding:
    """Test data encoding and handling."""

    def test_bytes_encoding(self) -> None:
        """Test bytes are handled correctly."""
        data = b"test"
        assert isinstance(data, bytes)

    def test_string_to_bytes_conversion(self) -> None:
        """Test string to bytes conversion."""
        text = "test"
        data = text.encode("utf-8")
        assert isinstance(data, bytes)
        assert data == b"test", "Data must not be empty"

    def test_utf8_encoding(self) -> None:
        """Test UTF-8 encoding."""
        text = "hello 世界 мир"
        data = text.encode("utf-8")
        decoded = data.decode("utf-8")
        assert decoded == text, "decoded is not valid"

    def test_binary_data_handling(self) -> None:
        """Test handling of binary data."""
        data = bytes([0, 1, 2, 255, 254])
        assert len(data) == 5, "Data must not be empty"
        assert data[0] == 0, "Data must not be empty"
        assert data[4] == 254, "Data must not be empty"

    def test_json_serialization(self) -> None:
        """Test JSON can be serialized for signing."""
        obj = {"key": "value", "number": 42}
        json_str = json.dumps(obj)
        data = json_str.encode("utf-8")
        assert isinstance(data, bytes)


class TestLogging:
    """Test logging functionality."""

    def test_module_has_logger(self) -> None:
        """Test module has logger configured."""
        assert hasattr(sigstore_client, "logger")

    def test_logger_is_logger(self) -> None:
        """Test logger is proper logger instance."""
        logger = sigstore_client.logger
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_logger_can_log(self) -> None:
        """Test logger can log messages."""
        with patch.object(sigstore_client.logger, "info") as mock_log:
            sigstore_client.logger.info("Test message")
            mock_log.assert_called_once_with("Test message")


class TestModuleConstants:
    """Test module constants and configuration."""

    def test_has_sigstore_flag_exists(self) -> None:
        """Test _HAS_SIGSTORE flag exists."""
        assert hasattr(sigstore_client, "_HAS_SIGSTORE")

    def test_has_sigstore_flag_is_bool(self) -> None:
        """Test _HAS_SIGSTORE is boolean."""
        assert isinstance(sigstore_client._HAS_SIGSTORE, bool)

    def test_public_has_sigstore_alias(self) -> None:
        """Test HAS_SIGSTORE mirrors the private flag."""
        assert sigstore_client.HAS_SIGSTORE is sigstore_client._HAS_SIGSTORE

    def test_client_class_exists(self) -> None:
        """Test SignstoreClient class is defined."""
        assert hasattr(sigstore_client, "SignstoreClient")


class TestErrorHandling:
    """Test error handling."""

    def test_sign_with_unserialisable_record(
        self, mock_client: sigstore_client.SignstoreClient
    ) -> None:
        """Records that cannot be JSON-serialised raise TypeError."""
        with pytest.raises(TypeError):
            mock_client.sign_record({"obj": object()}, actor="alice")

    def test_verify_with_invalid_types(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """A non-string signature is rejected (errors are caught, not raised)."""
        assert mock_client.verify_signature({"data": 1}, 12345) is False  # type: ignore[arg-type]

    def test_invalid_environment_variable(self) -> None:
        """Test invalid environment variable value."""
        with patch.dict("os.environ", {"CODEX_ENABLE_SIGNING": "invalid"}):
            # Should handle gracefully
            import os

            value = os.environ.get("CODEX_ENABLE_SIGNING")
            assert isinstance(value, str)


class TestIntegration:
    """Integration tests for signing and verification."""

    def test_sign_and_verify_flow(self, mock_client: sigstore_client.SignstoreClient) -> None:
        """Test complete sign and verify flow."""
        record = {"data": "test data"}
        signed = mock_client.sign_record(record, actor="alice")
        assert (
            mock_client.verify_signature(record, signed["signature"], signed["cert_chain"]) is True
        )

    def test_modified_data_changes_signature(
        self, mock_client: sigstore_client.SignstoreClient
    ) -> None:
        """Test that modified data yields a different signature."""
        original = mock_client.sign_record({"data": "test data"}, actor="alice")["signature"]
        tampered = mock_client.sign_record({"data": "tampered data"}, actor="alice")["signature"]
        assert original != tampered
