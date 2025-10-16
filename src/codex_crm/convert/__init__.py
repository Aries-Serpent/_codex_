"""Conversion utilities that translate shared methodology rules across CRM stacks."""

from __future__ import annotations

from .rules import ConversionFidelity, automation_to_d365, compute_fidelity, trigger_to_d365

__all__ = [
    "ConversionFidelity",
    "compute_fidelity",
    "automation_to_d365",
    "trigger_to_d365",
]
