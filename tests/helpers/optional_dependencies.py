from __future__ import annotations

from typing import Any

import pytest

OPTIONAL_DEPENDENCY_REASONS: dict[str, str] = {
    "torch": (
        "PyTorch provides tensor operations and checkpoint serialization required "
        "for training and resume smoke tests."
    ),
    "transformers": (
        "Hugging Face transformers exposes the model and tokenizer loaders used "
        "throughout the Codex ML stack. Install the 'ml' extra to enable these tests."
    ),
    "numpy": "NumPy underpins dataset fixtures and numerical assertions in the regression suite.",
    "mlflow": (
        "MLflow powers experiment tracking; enable it to exercise logging adapters "
        "and offline recording flows."
    ),
    "peft": (
        "PEFT supplies LoRA adapters for fine-tuning paths. Install the 'train' extra "
        "to cover parameter-efficient training tests."
    ),
}


def import_optional_dependency(name: str, *, allow_stub: bool = False) -> Any:
    """Import ``name`` or skip the calling test with a structured reason."""

    reason = OPTIONAL_DEPENDENCY_REASONS.get(name, f"{name} is required for this test")
    module = pytest.importorskip(name, reason=reason)
    if not allow_stub and getattr(module, "IS_CODEX_STUB", False):
        pytest.skip(f"{name} stub installed: {reason}")
    return module
