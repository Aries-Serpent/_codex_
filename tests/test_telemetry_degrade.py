"""
Test Telemetry Degrade

Test module for telemetry degrade.
"""

from codex_ml.monitoring.codex_logging import init_telemetry


def test_full_profile_degrades_without_nvml(monkeypatch):
    import builtins
    original_import = builtins.__import__
    
    def fake_import(name, *args, **kwargs):
        if name == "pynvml":
            raise ImportError("no nvml")
        return original_import(name, *args, **kwargs)
    
    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        init_telemetry(profile="full")  # should not raise
    finally:
        # Ensure cleanup
        monkeypatch.undo()
