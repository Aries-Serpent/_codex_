"""Runtime contracts behind the optional-backend typing annotations."""

from __future__ import annotations

import builtins
import importlib.util
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest
from omegaconf import DictConfig, OmegaConf

from codex_ml.utils import config_loader


def _isolated_module(
    monkeypatch: pytest.MonkeyPatch,
    source: Path,
    blocked_imports: tuple[str, ...],
) -> ModuleType:
    """Exercise import guards without altering the application's cached module."""
    real_import = builtins.__import__

    def guarded_import(name: str, *args, **kwargs):
        if any(name == blocked or name.startswith(f"{blocked}.") for blocked in blocked_imports):
            raise ImportError(f"unavailable test backend: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    name = f"_phase2_test_{source.stem}"
    spec = importlib.util.spec_from_file_location(name, source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def test_training_config_preserves_non_string_keys_and_aliases() -> None:
    original = {7: "numeric key", "training": {"learning_rate": 0.25, "max_epochs": 2}}
    config = config_loader._to_config_object(original)

    assert config[7] == "numeric key"
    assert config.training.lr == 0.25
    assert config.training.epochs == 2
    assert config.lr == 0.25
    assert config.epochs == 2
    assert original["training"] == {"learning_rate": 0.25, "max_epochs": 2}


def test_load_config_preserves_yaml_keys(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("7: numeric key\ntraining:\n  learning_rate: 0.25\n", encoding="utf-8")

    config = config_loader.load_config(config_path=str(path))

    assert isinstance(config, DictConfig)
    assert config[7] == "numeric key"
    assert config.training.lr == 0.25


def test_training_config_real_hydra_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "base.yaml").write_text(
        "training:\n  learning_rate: 0.25\n  epochs: 2\n", encoding="utf-8"
    )
    monkeypatch.setattr(config_loader, "_CFG_DIR", tmp_path)
    assert config_loader._HYDRA_AVAILABLE

    config = config_loader.load_training_cfg(overrides=["training.epochs=4"])

    assert config.training.epochs == config.epochs == 4
    assert config.training.lr == config.lr == 0.25


def test_training_config_without_hydra(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _isolated_module(
        monkeypatch,
        Path(config_loader.__file__),
        ("hydra", "config_legacy", "hydra_core"),
    )
    monkeypatch.setattr(module, "_CFG_DIR", tmp_path)

    assert module.compose is None
    assert module.initialize_config_dir is None
    assert module._HYDRA_AVAILABLE is False
    config = module.load_training_cfg(overrides=["training.epochs=5"])
    assert config.training.epochs == config.epochs == 5

    with pytest.raises(module.MissingConfigException) as caught:
        module.load_training_cfg(allow_fallback=False)
    assert caught.value.missing_cfg_file == str(tmp_path / "base.yaml")

    (tmp_path / "base.yaml").write_text("training:\n  seed: 9\n", encoding="utf-8")
    assert module.load_training_cfg(allow_fallback=False).training.seed == 9


@pytest.mark.parametrize("provider", ["config_legacy", "hydra_core"])
def test_training_config_alternate_hydra_provider(
    provider: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[object] = []
    backend = ModuleType(provider)
    errors = ModuleType(f"{provider}.errors")

    @contextmanager
    def initialize_config_dir(
        config_dir: str, job_name: str = "app", version_base: str | None = None
    ) -> Iterator[None]:
        calls.append((config_dir, job_name, version_base))
        yield

    def compose(
        config_name: str | None = None,
        overrides: list[str] | None = None,
        return_hydra_config: bool = False,
        strict: bool | None = None,
    ) -> DictConfig:
        calls.append((config_name, overrides))
        return OmegaConf.create({"training": {"learning_rate": 0.125}})

    monkeypatch.setattr(backend, "compose", compose, raising=False)
    monkeypatch.setattr(backend, "initialize_config_dir", initialize_config_dir, raising=False)
    monkeypatch.setattr(
        errors,
        "MissingConfigException",
        config_loader._FallbackMissingConfigException,
        raising=False,
    )
    monkeypatch.setitem(sys.modules, provider, backend)
    monkeypatch.setitem(sys.modules, f"{provider}.errors", errors)
    blocked = ("hydra",) if provider == "config_legacy" else ("hydra", "config_legacy")
    module = _isolated_module(monkeypatch, Path(config_loader.__file__), blocked)
    monkeypatch.setattr(module, "_CFG_DIR", tmp_path)
    (tmp_path / "base.yaml").write_text("training: {}\n", encoding="utf-8")

    config = module.load_training_cfg(overrides=["training.epochs=3"])

    assert module._HYDRA_AVAILABLE is True
    assert config.lr == 0.125
    assert calls == [(str(tmp_path), "app", None), ("base", ["training.epochs=3"])]


def test_metrics_registry_without_prometheus(monkeypatch: pytest.MonkeyPatch) -> None:
    from codex_ml.monitoring import prometheus_metrics

    module = _isolated_module(
        monkeypatch, Path(prometheus_metrics.__file__), ("prometheus_client",)
    )
    registry = module.CodexMetricsRegistry()
    registry.record_training_step(0.25)
    registry.record_inference("/infer", -1)
    registry.observe_data_loading(-1)
    registry.active_sessions.set(2)
    monkeypatch.setattr(module.time, "perf_counter", iter([10.0, 12.5]).__next__)
    with pytest.raises(ValueError, match="training failed"):
        with registry.track_duration():
            raise ValueError("training failed")
    with registry.training_steps.time():
        pass

    assert registry.registry is None
    assert registry.training_steps._value == 1
    assert registry.training_loss._value == 0.25
    assert registry.inference_requests._value == 1
    assert registry.inference_latency_seconds._value == 0
    assert registry.data_loading_duration_seconds._value == 0
    assert registry.active_sessions._value == 2
    assert registry.training_duration_seconds._value == 2.5


def test_metrics_registry_real_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    from prometheus_client import CollectorRegistry

    from codex_ml.monitoring import prometheus_metrics

    collector = CollectorRegistry()
    registry = prometheus_metrics.CodexMetricsRegistry(registry=collector)
    registry.record_training_step(0.75)
    registry.record_inference("/infer", -1)
    monkeypatch.setattr(prometheus_metrics.time, "perf_counter", iter([1.0, 4.0]).__next__)
    with registry.track_duration():
        pass

    assert registry.registry is collector
    assert collector.get_sample_value("codex_ml_training_steps_total") == 1
    assert collector.get_sample_value("codex_ml_training_loss") == 0.75
    assert (
        collector.get_sample_value("codex_ml_inference_requests_total", {"endpoint": "/infer"}) == 1
    )
    assert (
        collector.get_sample_value("codex_ml_inference_latency_seconds_sum", {"endpoint": "/infer"})
        == 0
    )
    assert collector.get_sample_value("codex_ml_training_duration_seconds_sum") == 3


def test_metrics_export_real_backend(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import prometheus_client
    from prometheus_client import CollectorRegistry, Counter, Gauge

    from codex_ml.monitoring import prometheus

    collector = CollectorRegistry()
    ports: list[int] = []

    def counter(name: str, description: str) -> Counter:
        return Counter(name, description, registry=collector)

    def gauge(name: str, description: str) -> Gauge:
        return Gauge(name, description, registry=collector)

    monkeypatch.setattr(prometheus_client, "Counter", counter)
    monkeypatch.setattr(prometheus_client, "Gauge", gauge)
    monkeypatch.setattr(prometheus_client, "start_http_server", ports.append)

    counters, gauges = prometheus.maybe_export_metrics(port=9123, fallback_dir=tmp_path)
    counters["requests_total"].inc(2)
    gauges["queue_depth"].set(3)

    assert ports == [9123]
    assert prometheus.fallback_status() == (False, None, None)
    assert collector.get_sample_value("requests_total") == 2
    assert collector.get_sample_value("queue_depth") == 3
    assert not (tmp_path / "prometheus.ndjson").exists()


def test_metrics_export_reports_degradation_as_a_warning(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from codex_ml.monitoring import prometheus

    module = _isolated_module(monkeypatch, Path(prometheus.__file__), ("prometheus_client",))
    logger = Mock()
    monkeypatch.setattr(module, "get_default_logger", lambda: logger)

    counters, gauges = module.maybe_export_metrics(fallback_dir=tmp_path)
    counters["requests_total"].inc()
    gauges["queue_depth"].set(1)

    logger.warning.assert_called_once()
    logger.info.assert_not_called()
    assert "falling back to NDJSON" in logger.warning.call_args.args[0]
    assert logger.warning.call_args.kwargs == {}
    assert module.fallback_status()[0] is True
