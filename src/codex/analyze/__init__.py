"""
Codex Analyze Module

Static and runtime analysis of Python code for the ingestion pipeline.

Components:
- static: AST parsing, linting, security scanning, complexity analysis
- runtime: Sandboxed execution, tracing, IO capture
"""

from __future__ import annotations

__all__ = ["static", "runtime"]
