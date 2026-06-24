"""
Registry Module

This module provides functionality for registry.

Usage:
    from analysis.registry import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# src/codex_ml/analysis/registry.py
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402


@dataclass
class Registry:
    parsers: dict[str, Callable] | None = None
    extractors: dict[str, Callable] | None = None


REG = Registry(parsers={}, extractors={})


def register_parser(name: str, fn: Callable) -> None:
    REG.parsers[name] = fn  # type: ignore[index]


def register_extractor(name: str, fn: Callable) -> None:
    REG.extractors[name] = fn  # type: ignore[index]


# Default registrations bind to core implementations
try:  # pragma: no cover - import side effects only
    from .extractors import extract_ast, extract_cst, extract_degraded, extract_parso
    from .parsers import parse_tiered

    register_parser("tiered", parse_tiered)
    register_extractor("ast", extract_ast)
    register_extractor("cst", extract_cst)
    register_extractor("parso", extract_parso)
    register_extractor("degraded", extract_degraded)
except (ValueError, TypeError):
    logger.warning("Exception occurred", exc_info=True)
    # Registration is best-effort; failures fall back to manual wiring.
