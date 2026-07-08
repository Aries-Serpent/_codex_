"""
Test Models

Test module for models.
"""

from codex_ml.registry import models


def test_models_facade_exports_registry_functions():
    assert hasattr(models, "model_registry")
    assert hasattr(models, "register_model")
    assert hasattr(models, "get_model")
    assert hasattr(models, "list_models")
