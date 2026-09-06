"""Compatibility package for the static analysis API.

This module exposes the canonical static-analysis implementation under the
``aries_serpent_core`` package while keeping the ``codex.analyze.static`` import
path stable for repo tests and callers.
"""

from aries_serpent_core.analyze.static import FileAnalysis, StaticReport, analyze

__all__ = ["FileAnalysis", "StaticReport", "analyze"]
