"""
Canonical import shim for src.training.data_utils
"""
from importlib import import_module as _im

_mod = _im("training.data_utils")
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
__all__ = [k for k in globals() if not k.startswith("_")]
