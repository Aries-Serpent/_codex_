from __future__ import annotations

import pytest

try:
    from codex_ml.models.registry import get_model
    from codex_ml.registry.base import RegistryNotFoundError
except Exception as exc:  # pragma: no cover - optional dependency missing
    pytest.skip(f"model registry unavailable: {exc}", allow_module_level=True)


def test_invalid_model_name_raises_registry_error() -> None:
    with pytest.raises(RegistryNotFoundError):
        get_model("no_such_model", {})
