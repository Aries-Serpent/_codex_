"""Ensure the scripts/ package root is on sys.path before test collection.

Tests in this directory import top-level scripts directly (e.g.
``from list_checkpoints import ...``).  Centralising the path insertion here
prevents each test file from having module-level ``sys.path.insert`` calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_ROOT = str(Path(__file__).resolve().parents[2] / "scripts")
if _SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, _SCRIPTS_ROOT)


@pytest.fixture
def disable_torch_profiler(monkeypatch):
    """Disable PyTorch profiler to avoid Protocol isinstance issues."""
    try:
        import torch.profiler as profiler_module

        # Disable profiler record function to prevent Protocol isinstance errors
        if hasattr(profiler_module, "_record_function_enter"):
            monkeypatch.setattr(
                profiler_module, "_record_function_enter", lambda *args, **kwargs: None
            )
        if hasattr(profiler_module, "_record_function_exit"):
            monkeypatch.setattr(
                profiler_module, "_record_function_exit", lambda *args, **kwargs: None
            )
    except (ImportError, AttributeError):
        pass  # PyTorch profiler not available or already disabled
