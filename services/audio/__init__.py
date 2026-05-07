"""Services audio package - re-exports from src.services.audio."""

from __future__ import annotations

# Re-export from src.services.audio
try:
    import src.services.audio as _audio_module

    _exported_names = [name for name in dir(_audio_module) if not name.startswith("_")]
    globals().update({name: getattr(_audio_module, name) for name in _exported_names})
    __all__ = _exported_names
except ImportError:
    _ = None  # suppressed: no action needed
