"""
tests/github conftest.py

Pre-imports codex.github so the subpackage is registered as an attribute on
the codex namespace package BEFORE pytest-randomly reorders tests or sharding
splits the test suite into separate processes.

Without this, monkeypatch.setattr("codex.github.mcp_poster.urllib.request.urlopen", ...)
can fail with AttributeError when the test shard starts a fresh Python process
where codex.github hasn't been imported yet.

Root cause documented: same pattern as tests/archive/conftest.py — see that
file for a full explanation of the shard isolation problem.
"""

from __future__ import annotations

import importlib

# Pre-import for test shard isolation: register subpackages as attributes on the
# codex namespace before pytest-randomly reorders tests or sharding splits the
# suite into separate processes.  importlib.import_module avoids unused-import
# warnings while producing the identical side-effect as a bare import statement.
importlib.import_module("codex.github")
importlib.import_module("codex.github.mcp_poster")
