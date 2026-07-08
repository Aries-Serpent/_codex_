"""Ensure codex version module exposes __version__."""

from __future__ import annotations

from codex import _version


def test_version_exposed():
    assert hasattr(_version, "__version__")
    assert isinstance(_version.__version__, str)
    assert len(_version.__version__) > 0, "Collection must not be empty"
