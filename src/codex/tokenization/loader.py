"""Compatibility loader for legacy `codex.tokenization` imports."""

from __future__ import annotations


class TokenizerLoader:
    """Very small compatibility wrapper that mirrors the expected API."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def load(self, *args, **kwargs):
        return {"status": "ok", "loader": "compat"}


__all__ = ["TokenizerLoader"]
