"""Deprecated forwarding module for :mod:`codex_lora` use-case functions.

Scheduled for removal in ``codex-ml 0.5.0``. The legacy two-argument helper
remains available from :mod:`codex_ml.peft.peft_adapter` and the package root.
"""

from codex_lora import apply_lora, load_lora

__all__ = ["apply_lora", "load_lora"]
