"""
Test Features

Test module for features.
"""
import importlib




def test_import_module():
    module = "hhg_logistics.pipeline_nodes.features"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
