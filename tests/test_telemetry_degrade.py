from codex_ml.monitoring.codex_logging import init_telemetry


def test_full_profile_degrades_without_nvml(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "pynvml":
            raise ImportError("no nvml")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    init_telemetry(profile="full")
