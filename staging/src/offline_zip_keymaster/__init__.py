"""Offline ZIP keymaster package.

This package exposes the secure, local-only ZIP key generation and unpacking
logic as a standalone Python application while keeping the canonical backend in
`scripts/security/offline_zip_keymaster.py`.
"""

from .cli import main

__all__ = ["main"]
