"""Offline ZIP keymaster package.

This package exposes the secure, local-only ZIP key generation and unpacking
logic as a standalone Python application. The bundled implementation lives in
`_impl.py` so the GUI and release wheel remain import-safe even when the repo's
`scripts/` tree is not present in a frozen or downloaded bundle.
"""

from .cli import main

__all__ = ["main"]
