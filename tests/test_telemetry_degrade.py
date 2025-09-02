from codex_ml.monitoring.codex_logging import init_telemetry


def test_full_profile_degrades_without_nvml(monkeypatch):
    def fake_import(name, *args, **kwargs):
        if name == "pynvml":
            raise ImportError("no nvml")
        return __import__(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    init_telemetry(profile="full")  # should not raise
