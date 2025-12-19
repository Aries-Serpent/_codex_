from __future__ import annotations
import importlib
import importlib.util
import os
from typing import Optional, Tuple

DEFAULT_ADAPTER = "src.mcp.backends.mock_backend.InMemoryMockBackend"


def _import_class(path: str):
    module_name, class_name = path.rsplit(".", 1)
    if importlib.util.find_spec(module_name) is None:
        return None
    mod = importlib.import_module(module_name)
    return getattr(mod, class_name, None)


def load_adapter(adapter_path: Optional[str] = None) -> Tuple[object, str]:
    """
    Loads adapter based on ADAPTER_CLASS environment variable or explicit param.
    Returns (adapter_instance, adapter_class_path).
    If ADAPTER_CLASS not set or loading fails, fall back to DEFAULT_ADAPTER.

    adapter_path: optional explicit adapter import path (useful for tests)
    """
    cls_path = adapter_path or os.environ.get("ADAPTER_CLASS", DEFAULT_ADAPTER)
    cls = _import_class(cls_path)
    if cls is None:
        cls_path = DEFAULT_ADAPTER
        cls = _import_class(cls_path)
    if cls is None:
        raise RuntimeError("Unable to load adapter class")
    instance = cls()
    try:
        instance.connect()
    except Exception:
        # ignore connect failures for import-safety
        pass
    return instance, cls_path
