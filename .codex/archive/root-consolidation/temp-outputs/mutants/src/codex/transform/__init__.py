"""
Codex Transform Module

Code transformation and patch generation using libcst and refactoring rules.

Components:
- transformer: Generate edits and build patches
- patch: Create unified diffs and apply patches
"""

from __future__ import annotations

from .transformer import Patch, TransformResult, transform

__all__ = ["Patch", "TransformResult", "transform"]
