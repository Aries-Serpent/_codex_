# src/codex_ml/analysis/registry.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Registry:
    parsers: dict[str, Callable] | None = None
    extractors: dict[str, Callable] | None = None


REG = Registry(parsers={}, extractors={})


def register_parser(name: str, fn: Callable) -> None:
    REG.parsers[name] = fn


def register_extractor(name: str, fn: Callable) -> None:
    REG.extractors[name] = fn


# Default registrations bind to core implementations
try:  # pragma: no cover - import side effects only
    from .extractors import extract_ast, extract_cst, extract_degraded, extract_parso
    from .parsers import parse_tiered

    register_parser("tiered", parse_tiered)
    register_extractor("ast", extract_ast)
    register_extractor("cst", extract_cst)
    register_extractor("parso", extract_parso)
    register_extractor("degraded", extract_degraded)
except Exception:
    # Registration is best-effort; failures fall back to manual wiring.
    pass
