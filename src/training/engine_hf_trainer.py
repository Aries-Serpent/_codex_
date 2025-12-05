"""
Canonical import shim for src.training.engine_hf_trainer

Bridges to legacy training.engine_hf_trainer to preserve runtime behavior
while refactors converge on src.* as the canonical import path.
"""
from importlib import import_module as _im

_mod = _im("training.engine_hf_trainer")
# Export all public members from legacy module under src.training namespace
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
__all__ = [k for k in globals() if not k.startswith("_")]
