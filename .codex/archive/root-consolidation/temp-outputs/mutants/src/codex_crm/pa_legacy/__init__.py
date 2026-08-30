"""Tools for interpreting legacy Power Automate packages."""

from __future__ import annotations

from .reader import PowerAutomatePackageError, read_pa_legacy, to_template

__all__ = [
    "PowerAutomatePackageError",
    "read_pa_legacy",
    "to_template",
]
