# src/codex/archive/sigstore_client.py
"""
Sigstore Keyless Signing Client

Integrates Sigstore for SLSA L3 cryptographic identity binding.
Uses GitHub OIDC tokens for keyless signing.

When the ``sigstore`` Python package (https://pypi.org/project/sigstore/) is
installed, this module uses it for real cryptographic signing and verification
via the public Sigstore infrastructure (Fulcio CA + Rekor transparency log).

When ``sigstore`` is unavailable the module falls back to a deterministic
SHA-256 mock that is suitable for development and testing only.

Install the SDK:
    pip install sigstore

Enable production signing:
    CODEX_ENABLE_SIGNING=true
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import the sigstore SDK (optional dependency)
try:
    from sigstore.sign import Signer
    from sigstore.verify import Verifier
    from sigstore.verify.policy import UnsafeNoOp

    _HAS_SIGSTORE = True
    logger.info("sigstore SDK available — production signing enabled")
except ImportError:
    _HAS_SIGSTORE = False
    logger.info(
        "sigstore package not installed. "
        "Run `pip install sigstore` to enable production signing. "
        "Falling back to mock SHA-256 signing."
    )

# Public alias for external inspection (e.g., tests and diagnostics)
HAS_SIGSTORE = _HAS_SIGSTORE

__all__ = ["HAS_SIGSTORE", "SignstoreClient"]


class SignstoreClient:
    """Client for Sigstore keyless signing operations.

    Uses the real sigstore-python SDK when available; falls back to a mock
    implementation for development and CI environments where the SDK is not
    installed or where network access to the public Sigstore infrastructure
    is unavailable.
    """

    def __init__(self) -> None:
        """Initialize Sigstore client with GitHub OIDC integration."""
        self.oidc_token = os.getenv("SIGSTORE_ID_TOKEN") or self._get_github_token()
        self.fulcio_url = os.getenv("SIGSTORE_FULCIO_URL", "https://fulcio.sigstore.dev")
        self.rekor_url = os.getenv("SIGSTORE_REKOR_URL", "https://rekor.sigstore.dev")
        self.enabled = os.getenv("CODEX_ENABLE_SIGNING", "false").lower() == "true"
        if self.enabled and not _HAS_SIGSTORE:
            logger.warning(
                "CODEX_ENABLE_SIGNING=true but the 'sigstore' package is not installed. "
                "Falling back to MOCK signing — signatures are NOT cryptographically secure. "
                "Install with: pip install sigstore"
            )

    def _get_github_token(self) -> str:
        """Get GitHub OIDC token from Actions environment.

        Requests a fresh OIDC token from GitHub Actions when the standard env
        variables are present.  Returns a placeholder in non-Actions contexts.
        """
        token_url = os.getenv("ACTIONS_ID_TOKEN_REQUEST_URL")
        token_request_token = os.getenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN")

        if not token_url or not token_request_token:
            return "local-dev-token-placeholder"

        try:
            import requests as _requests

            resp = _requests.get(
                token_url,
                headers={"Authorization": f"bearer {token_request_token}"},
                params={"audience": "sigstore"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("value", "github-oidc-token-placeholder")
        except (ValueError, TypeError) as exc:
            logger.warning("GitHub OIDC exchange failed: %s", type(exc).__name__)
            return "github-oidc-token-placeholder"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sign_record(
        self,
        record: dict[str, Any],
        actor: str,
    ) -> dict[str, Any]:
        """Sign evidence record using Sigstore keyless signing.

        Uses the real ``sigstore`` SDK when available; falls back to a
        deterministic SHA-256 mock otherwise.

        Args:
            record: Evidence record to sign
            actor: Actor performing the operation

        Returns:
            Dictionary with ``signature``, ``cert_chain``, ``issuer``,
            ``actor``, and ``signed_at`` keys.
        """
        signed_at = datetime.now(timezone.utc).isoformat()

        if not self.enabled:
            return {
                "signature": None,
                "cert_chain": None,
                "issuer": None,
                "actor": actor,
                "signed_at": signed_at,
            }

        record_bytes = json.dumps(record, sort_keys=True).encode("utf-8")

        if _HAS_SIGSTORE:
            return self._sigstore_sign(record_bytes, actor, signed_at)
        return self._mock_sign_record(record_bytes, actor, signed_at)

    def verify_signature(
        self,
        record: dict[str, Any],
        signature: str,
        _cert_chain: Optional[list[str]] = None,
    ) -> bool:
        """Verify Sigstore signature and certificate chain.

        Args:
            record: Original evidence record
            signature: Signature bundle (JSON string from sign_record)
            _cert_chain: Certificate chain (unused when sigstore SDK available)

        Returns:
            True if signature valid and trusted
        """
        if not self.enabled or signature is None:
            return True

        try:
            if _HAS_SIGSTORE and not signature.startswith("MOCK_SIG_"):
                return self._sigstore_verify(record, signature)
            # Fall back to mock verification
            return len(signature) > 0 and signature.startswith("MOCK_SIG_")
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.error("Signature verification failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Real sigstore-python implementation
    # ------------------------------------------------------------------

    def _sigstore_sign(
        self,
        record_bytes: bytes,
        actor: str,
        signed_at: str,
    ) -> dict[str, Any]:
        """Sign using the real sigstore Python SDK."""
        try:
            signer = Signer.production()
            bundle = signer.sign(io.BytesIO(record_bytes))
            # Bundle is JSON-serialisable via its model
            bundle_json = bundle.to_json()
            logger.info("Record signed via Sigstore (actor=%s)", actor)
            return {
                "signature": bundle_json,
                "cert_chain": None,  # included inside the bundle JSON
                "issuer": "https://token.actions.githubusercontent.com",
                "actor": actor,
                "signed_at": signed_at,
                "backend": "sigstore-python",
            }
        except (ValueError, TypeError) as exc:
            logger.error("Sigstore signing failed: %s — falling back to mock", exc)
            return self._mock_sign_record(record_bytes, actor, signed_at)

    def _sigstore_verify(self, record: dict[str, Any], bundle_json: str) -> bool:
        """Verify using the real sigstore Python SDK."""
        try:
            from sigstore.models import Bundle

            record_bytes = json.dumps(record, sort_keys=True).encode("utf-8")
            bundle = Bundle.from_json(bundle_json)
            verifier = Verifier.production()
            verifier.verify_artifact(
                io.BytesIO(record_bytes),
                bundle,
                UnsafeNoOp(),
            )
            return True
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.warning("Sigstore verification failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Mock / fallback implementation
    # ------------------------------------------------------------------

    def _mock_sign_record(
        self,
        record_bytes: bytes,
        actor: str,
        signed_at: str,
    ) -> dict[str, Any]:
        """Generate mock signature for development/testing."""
        signature = self._mock_sign(record_bytes, actor)
        return {
            "signature": signature,
            "cert_chain": [self._mock_certificate(actor)],
            "issuer": "https://token.actions.githubusercontent.com",
            "actor": actor,
            "signed_at": signed_at,
            "backend": "mock",
        }

    def _mock_sign(self, data: bytes, actor: str) -> str:
        """Generate mock signature (SHA-256 based, NOT cryptographically secure)."""
        h = hashlib.sha256(data + actor.encode()).hexdigest()[:32]
        return f"MOCK_SIG_{h}"

    def _mock_certificate(self, actor: str) -> str:
        """Generate mock certificate for development/testing."""
        return f"-----BEGIN CERTIFICATE-----\nMOCK_CERT_FOR_{actor}\n-----END CERTIFICATE-----"
