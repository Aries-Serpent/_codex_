"""
Test Prometheus

Test module for prometheus.
"""
import importlib




def test_import_module():
    module = "codex_ml.monitoring.prometheus"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
