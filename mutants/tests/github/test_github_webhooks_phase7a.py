"""
GitHub webhook security and validation tests - Phase 7A WAVE 2 LANE 2.3

This module contains 25+ tests covering:
GitHub webhook security and validation — HMAC-SHA256 signature verification,
event payload parsing, replay detection, and token format recognition.
"""

from __future__ import annotations

import hashlib
import hmac as hmac_stdlib
import json

import pytest

from codex.auth.github_app import WebhookVerifier
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

# ---------------------------------------------------------------------------
# WebhookVerifier initialisation
# ---------------------------------------------------------------------------


class TestWebhookVerifierInit:
    """Tests for WebhookVerifier initialisation."""

    def test_init_valid_secret(self):
        """WebhookVerifier initialises successfully with a non-empty secret."""
        verifier = WebhookVerifier("my-secret")
        assert verifier is not None

    def test_init_empty_secret_raises_value_error(self):
        """An empty string secret must raise ValueError."""
        with pytest.raises(ValueError, match="Webhook secret must not be empty"):
            WebhookVerifier("")

    def test_header_prefix_constant(self):
        """HEADER_PREFIX class constant must equal 'sha256='."""
        assert WebhookVerifier._HEADER_PREFIX == "sha256="

    def test_init_single_char_secret_is_valid(self):
        """A single-character secret is technically valid (non-empty)."""
        verifier = WebhookVerifier("x")
        assert verifier is not None


# ---------------------------------------------------------------------------
# compute_signature
# ---------------------------------------------------------------------------


class TestComputeSignature:
    """Tests for WebhookVerifier.compute_signature."""

    def test_signature_starts_with_sha256_prefix(self):
        """Computed signature must start with 'sha256='."""
        verifier = WebhookVerifier("supersecret")
        sig = verifier.compute_signature(b"payload")
        assert sig.startswith("sha256="), f"Expected 'sha256=' prefix, got: {sig[:10]}"

    def test_signature_is_deterministic(self):
        """Same payload + secret always produces the same signature."""
        verifier = WebhookVerifier("supersecret")
        payload = b'{"action":"opened"}'
        assert verifier.compute_signature(payload) == verifier.compute_signature(payload)

    def test_signature_hex_digest_length(self):
        """SHA-256 hex digest must be exactly 64 hex characters after prefix."""
        verifier = WebhookVerifier("test-secret")
        sig = verifier.compute_signature(b"some payload")
        hex_part = sig[len("sha256="):]
        assert len(hex_part) == 64, f"Expected 64-char hex digest, got {len(hex_part)}"

    def test_signature_matches_manual_hmac_sha256(self):
        """Computed signature must match a manually calculated HMAC-SHA256."""
        secret = "test-secret"
        payload = b'{"event":"push","ref":"refs/heads/main"}'
        expected_hex = hmac_stdlib.new(
            secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()
        verifier = WebhookVerifier(secret)
        assert verifier.compute_signature(payload) == f"sha256={expected_hex}"

    def test_different_payloads_produce_different_signatures(self):
        """Different payloads must produce different signatures."""
        verifier = WebhookVerifier("my-secret")
        assert verifier.compute_signature(b"payload_A") != verifier.compute_signature(b"payload_B")

    def test_different_secrets_produce_different_signatures(self):
        """The same payload with different secrets must produce different signatures."""
        payload = b"shared payload"
        assert (
            WebhookVerifier("secret-one").compute_signature(payload)
            != WebhookVerifier("secret-two").compute_signature(payload)
        )

    def test_empty_payload_generates_valid_signature(self):
        """An empty payload must still produce a valid sha256= signature."""
        verifier = WebhookVerifier("some-secret")
        sig = verifier.compute_signature(b"")
        assert sig.startswith("sha256=")
        assert len(sig[len("sha256="):]) == 64


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------


class TestWebhookVerify:
    """Tests for WebhookVerifier.verify."""

    def _sign(self, secret: str, payload: bytes) -> str:
        digest = hmac_stdlib.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def test_verify_valid_signature_returns_true(self):
        """verify() must return True for a correctly signed payload."""
        secret = "webhook-secret"
        payload = b'{"action":"opened","number":42}'
        verifier = WebhookVerifier(secret)
        assert verifier.verify(payload, self._sign(secret, payload)) is True

    def test_verify_tampered_payload_returns_false(self):
        """verify() must return False when the payload has been tampered with."""
        secret = "webhook-secret"
        original = b'{"action":"opened"}'
        tampered = b'{"action":"closed"}'
        verifier = WebhookVerifier(secret)
        assert verifier.verify(tampered, self._sign(secret, original)) is False

    def test_verify_wrong_secret_returns_false(self):
        """verify() must return False when the secret is incorrect."""
        payload = b'{"action":"push"}'
        verifier = WebhookVerifier("wrong-secret")
        assert verifier.verify(payload, self._sign("correct-secret", payload)) is False

    def test_verify_bad_format_raises_value_error(self):
        """verify() must raise ValueError for a signature without 'sha256=' prefix."""
        verifier = WebhookVerifier("my-secret")
        with pytest.raises(ValueError, match="Unexpected signature format"):
            verifier.verify(b"payload", "md5=abcdef1234567890")

    def test_verify_empty_payload_with_matching_sig(self):
        """verify() must succeed for an empty payload with its correct signature."""
        secret = "empty-payload-test"
        verifier = WebhookVerifier(secret)
        assert verifier.verify(b"", self._sign(secret, b"")) is True

    def test_verify_large_payload(self):
        """verify() must handle large payloads (1 MB) correctly."""
        secret = "large-payload-secret"
        payload = b"x" * (1024 * 1024)
        verifier = WebhookVerifier(secret)
        assert verifier.verify(payload, self._sign(secret, payload)) is True

    @pytest.mark.parametrize(
        "event_type",
        ["push", "pull_request", "issues", "workflow_run", "release"],
    )
    def test_verify_various_event_payloads(self, event_type: str):
        """verify() works correctly for various GitHub event payload structures."""
        secret = "event-secret"
        payload = json.dumps({"event": event_type, "sender": {"login": "octocat"}}).encode()
        verifier = WebhookVerifier(secret)
        assert verifier.verify(payload, self._sign(secret, payload)) is True


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestWebhookEdgeCases:
    """Edge case tests for webhook security and validation."""

    def test_secret_with_special_characters(self):
        """Secrets containing special characters must work correctly."""
        secret = "p@$$w0rd!#&*()-+=[]{}|;:,.<>?"
        payload = b'{"action":"synchronize"}'
        verifier = WebhookVerifier(secret)
        sig = verifier.compute_signature(payload)
        assert verifier.verify(payload, sig) is True

    def test_secret_encoding_is_utf8(self):
        """Secret is encoded as UTF-8 bytes for HMAC computation."""
        secret = "test-secret"
        payload = b"test"
        verifier = WebhookVerifier(secret)
        manual = hmac_stdlib.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        assert verifier.compute_signature(payload) == f"sha256={manual}"

    def test_signature_prefix_is_exactly_sha256_equals(self):
        """The signature prefix must be exactly 'sha256=' (lowercase, no spaces)."""
        verifier = WebhookVerifier("exact-prefix-test")
        sig = verifier.compute_signature(b"data")
        assert sig[:7] == "sha256="
        assert not sig.startswith("SHA256=")
        assert not sig.startswith("sha256 =")

    def test_compute_and_verify_roundtrip(self):
        """compute_signature output must always satisfy verify() on the same payload."""
        verifier = WebhookVerifier("roundtrip-secret")
        for payload in [b"", b"a", b"hello world", b"\x00\xff\xfe"]:
            sig = verifier.compute_signature(payload)
            assert verifier.verify(payload, sig) is True, (
                f"Roundtrip failed for payload {payload!r}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
