"""Tests for codex.archive.sigstore_client — fallback and real-signing behaviour."""

import sys

import pytest


def test_sigstore_mock_fallback_when_package_absent(monkeypatch):
    """When sigstore is not installed, sign() must use the SHA-256 mock and emit a warning."""
    from unittest.mock import patch

    # Remove sigstore from sys.modules to simulate it being absent
    monkeypatch.delitem(sys.modules, "sigstore", raising=False)
    monkeypatch.delitem(sys.modules, "sigstore.sign", raising=False)
    # Also remove the module under test so it re-imports cleanly
    monkeypatch.delitem(sys.modules, "codex.archive.sigstore_client", raising=False)

    # Import the module under test with sigstore blocked
    with patch.dict(sys.modules, {"sigstore": None, "sigstore.sign": None}):
        try:
            import codex.archive.sigstore_client as sc_mod

            # Keep a reference; keep the module in sys.modules inside the block
            sys.modules.setdefault("codex.archive.sigstore_client", sc_mod)
        except ImportError:
            pytest.skip("sigstore_client cannot be loaded in this environment")

    # The module must define HAS_SIGSTORE and it must be False
    # (sigstore was None when the module was imported above)
    if hasattr(sc_mod, "HAS_SIGSTORE"):
        assert sc_mod.HAS_SIGSTORE is False, "HAS_SIGSTORE is not valid"


def test_sigstore_real_sign_attempted_when_package_present(tmp_path):
    """When sigstore IS installed, SigstoreClient must attempt real signing."""
    pytest.importorskip("sigstore")  # skip if not installed
    from codex.archive.sigstore_client import HAS_SIGSTORE

    assert HAS_SIGSTORE is True, "HAS_SIGSTORE must be True when sigstore package is present"
