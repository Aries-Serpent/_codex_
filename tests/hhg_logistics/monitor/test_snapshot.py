"""
Test Snapshot

Test module for snapshot.
"""
import importlib




def test_import_module():
    module = "hhg_logistics.monitor.snapshot"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
