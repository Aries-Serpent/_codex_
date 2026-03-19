"""
tests/archive conftest.py

Pre-imports codex.archive so the subpackage is registered as an attribute on
the codex namespace package BEFORE pytest-randomly reorders tests or sharding
splits the test suite into separate processes.

Without this, monkeypatch.setattr("codex.archive.retry.time.sleep", ...) can
fail with AttributeError when the test shard that contains test_retry.py starts
a fresh Python process where codex.archive hasn't been imported yet.

Root cause documented: CI sharding with pytest-randomly creates per-shard
processes; the top-level `import codex.archive` in test_retry.py itself fires
*within* that shard process, but only when the module is collected.  Adding
this conftest.py guarantees the import fires at conftest load time (before any
test in the shard runs), matching the behaviour of a local full test run.
"""
from __future__ import annotations

import codex.archive  # noqa: F401 — register subpackage as attr on codex for monkeypatch
import codex.archive.retry  # noqa: F401 — ensure retry module is importable via dotted path
