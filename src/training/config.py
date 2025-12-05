"""
Canonical import shim for src.training.config
"""
from importlib import import_module as _im

_mod = _im("training.config")
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
__all__ = [k for k in globals() if not k.startswith("_")]
