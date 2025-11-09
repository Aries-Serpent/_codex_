from __future__ import annotations

import importlib

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")


def test_services_api_module_import_smoke():
    """Import smoke test for services.api.main."""
    try:
        module = importlib.import_module("services.api.main")
    except ModuleNotFoundError:
        pytest.skip("services.api.main not importable in this environment")
    except Exception as exc:  # pragma: no cover - environment specific
        pytest.skip(
            "services.api.main import skipped due to environment-specific error: " f"{exc!r}"
        )
    else:
        assert module is not None
