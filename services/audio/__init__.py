"""Services audio package - re-exports from src.services.audio."""

from __future__ import annotations

import warnings

# Re-export from src.services.audio
try:
    import src.services.audio as _audio_module

    _module_all = getattr(_audio_module, "__all__", None)
    if _module_all is not None:
        _exported_names = [name for name in _module_all if isinstance(name, str)]
        if len(_exported_names) != len(_module_all):
            warnings.warn(
                "src.services.audio.__all__ contains non-string entries; skipping invalid exports",
                RuntimeWarning,
                stacklevel=1,
            )
    else:
        _exported_names = [name for name in dir(_audio_module) if not name.startswith("_")]
    globals().update({name: getattr(_audio_module, name) for name in _exported_names})
    __all__ = _exported_names
except ImportError:
    _ = None  # suppressed: no action needed
