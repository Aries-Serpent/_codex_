"""
Canonical import shim for src.training.functional_training
"""
from importlib import import_module as _im

_mod = _im("training.functional_training")
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
__all__ = [k for k in globals() if not k.startswith("_")]
