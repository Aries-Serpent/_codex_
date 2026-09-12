"""Deprecated forwarding module for :mod:`codex_lora` adapters.

Scheduled for removal in ``codex-ml 0.5.0``.
"""

from codex_lora import CodexMlLoraAdapter, OptionalDependencyError, PeftBackend

__all__ = ["CodexMlLoraAdapter", "OptionalDependencyError", "PeftBackend"]
