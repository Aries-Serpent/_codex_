"""Tests for codex_ml.utils.hf_revision — HF pinned revision helper."""

from __future__ import annotations

from codex_ml.utils.hf_revision import get_hf_revision


class TestGetHfRevision:
    def test_returns_none_when_no_env(self, monkeypatch):
        for var in ("HF_REVISION", "HF_MODEL_REVISION", "CODEX_HF_REVISION"):
            monkeypatch.delenv(var, raising=False)
        assert get_hf_revision() is None, "Condition must be true"

    def test_returns_hf_revision(self, monkeypatch):
        monkeypatch.setenv("HF_REVISION", "abc123")
        monkeypatch.delenv("HF_MODEL_REVISION", raising=False)
        monkeypatch.delenv("CODEX_HF_REVISION", raising=False)
        assert get_hf_revision() == "abc123", "Condition must be true"

    def test_returns_hf_model_revision_fallback(self, monkeypatch):
        monkeypatch.delenv("HF_REVISION", raising=False)
        monkeypatch.setenv("HF_MODEL_REVISION", "def456")
        monkeypatch.delenv("CODEX_HF_REVISION", raising=False)
        assert get_hf_revision() == "def456", "Condition must be true"

    def test_returns_codex_hf_revision_fallback(self, monkeypatch):
        monkeypatch.delenv("HF_REVISION", raising=False)
        monkeypatch.delenv("HF_MODEL_REVISION", raising=False)
        monkeypatch.setenv("CODEX_HF_REVISION", "ghi789")
        assert get_hf_revision() == "ghi789", "Condition must be true"

    def test_primary_takes_precedence_over_fallbacks(self, monkeypatch):
        monkeypatch.setenv("HF_REVISION", "primary")
        monkeypatch.setenv("HF_MODEL_REVISION", "secondary")
        monkeypatch.setenv("CODEX_HF_REVISION", "tertiary")
        assert get_hf_revision() == "primary", "Condition must be true"

    def test_custom_env_var(self, monkeypatch):
        monkeypatch.setenv("MY_CUSTOM_REV", "custom_rev")
        monkeypatch.delenv("HF_MODEL_REVISION", raising=False)
        monkeypatch.delenv("CODEX_HF_REVISION", raising=False)
        assert get_hf_revision("MY_CUSTOM_REV") == "custom_rev", "Condition must be true"

    def test_empty_string_treated_as_missing(self, monkeypatch):
        monkeypatch.setenv("HF_REVISION", "")
        monkeypatch.delenv("HF_MODEL_REVISION", raising=False)
        monkeypatch.delenv("CODEX_HF_REVISION", raising=False)
        # Empty string is falsy — should fall through to None
        assert get_hf_revision() is None, "Condition must be true"
