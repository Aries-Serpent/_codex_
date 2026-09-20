"""Compatibility shim for repo-root tool entrypoints.

The canonical implementation lives under ``src/tools``; this root-level package
keeps legacy CLI paths such as ``python tools/template_lint.py`` working while
preserving the modern src-first layout.
"""

from __future__ import annotations
