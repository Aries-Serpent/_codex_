"""Canonical codex analyze compatibility facade."""

from aries_serpent_core.analyze import runtime, static
from aries_serpent_core.analyze.static.analyzer import analyze

__all__ = ["analyze", "runtime", "static"]
