"""Smoke tests for auxiliary training utilities."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest


@pytest.fixture
def stub_torch_module(monkeypatch):
    """Provide a minimal torch stub for modules that expect torch presence."""

    class FakeTensor:
        def __init__(self, value):
            self.value = value

        def item(self):  # pragma: no cover - convenience hook
            return self.value

    fake_dist = SimpleNamespace(
        ReduceOp=SimpleNamespace(MIN="min", MAX="max"),
        barrier=lambda: None,
        all_reduce=lambda tensor, op=None: None,
        is_available=lambda: False,
        is_initialized=lambda: False,
        get_world_size=lambda: 1,
        get_rank=lambda: 0,
    )

    fake_cuda = SimpleNamespace(
        is_available=lambda: False,
        device_count=lambda: 0,
        memory_allocated=lambda index=0: 0,
        get_device_name=lambda index=0: f"gpu-{index}",
    )

    fake_torch = SimpleNamespace(
        Tensor=FakeTensor,
        tensor=FakeTensor,
        manual_seed=lambda seed: None,
        Generator=type("Generator", (), {"manual_seed": lambda self, seed: None}),
        cuda=fake_cuda,
        distributed=fake_dist,
    )

    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(sys.modules, "torch.distributed", fake_dist)
    yield fake_torch
    sys.modules.pop("torch", None)
    sys.modules.pop("torch.distributed", None)


def test_dataloader_utils_generator(monkeypatch):
    """make_generator returns a seeded torch.Generator when available."""

    from codex_ml.training import dataloader_utils

    class DummyGenerator:
        def __init__(self):
            self.seed = None

        def manual_seed(self, seed):
            self.seed = seed

    monkeypatch.setattr(dataloader_utils, "torch", SimpleNamespace(Generator=DummyGenerator))
    generator = dataloader_utils.make_generator(123)
    assert isinstance(generator, DummyGenerator)
    assert generator.seed == 123, "seed is not valid"


def test_ray_distributed_guardrails():
    """Ray helpers expose availability and guard import errors."""

    import codex_ml.training.ray_distributed as ray_module

    if ray_module.check_ray_available():
        pytest.skip("Ray is installed in this environment; test covers the no-ray path only")

    assert ray_module.check_ray_available() is False, "Condition must be true"
    with pytest.raises(ImportError):
        ray_module.RayDistributedTrainer(lambda cfg: cfg, num_workers=1)


def test_fsdp_config_export():
    """FSDPConfig serialises core settings for logging."""

    from codex_ml.training.fsdp_wrapper import TORCH_AVAILABLE, FSDPConfig, FSDPTrainer

    cfg = FSDPConfig(sharding_strategy="NO_SHARD", mixed_precision=None)
    exported = cfg.to_dict()
    assert exported["sharding_strategy"] == "NO_SHARD", "exp is not valid"
    assert exported["mixed_precision"] is None, "exp is not valid"

    if not TORCH_AVAILABLE:
        with pytest.raises(RuntimeError):
            FSDPTrainer(model=None, config=cfg)


def test_legacy_api_text_helpers(tmp_path):
    """_listify_texts and _load_texts tolerate varied inputs."""

    from codex_ml.training import legacy_api

    assert legacy_api._listify_texts(None) == [], "Condition must be true"
    assert legacy_api._listify_texts("hello") == ["hello"], "Condition must be true"
    assert legacy_api._listify_texts([1, "x"]) == ["1", "x"]

    sample = tmp_path / "sample.txt"
    sample.write_text("first\nsecond\n")
    assert legacy_api._load_texts(str(sample), fmt="text") == ["first", "second"]


def test_multi_node_orchestration_health(monkeypatch, stub_torch_module):
    """Coordinator health/aggregation works with stubbed distributed runtime."""

    sys.modules["torch"] = stub_torch_module
    sys.modules["torch.distributed"] = stub_torch_module.distributed
    import importlib

    mnode = importlib.import_module("codex_ml.training.multi_node_orchestration")
    import codex_ml.training.distributed_setup as dist_setup

    monkeypatch.setattr(dist_setup, "setup_distributed", lambda backend=None: True)
    monkeypatch.setattr(dist_setup, "cleanup_distributed", lambda: None)
    monkeypatch.setattr(dist_setup, "get_world_size", lambda: 1)
    monkeypatch.setattr(dist_setup, "get_rank", lambda: 0)
    monkeypatch.setattr(dist_setup, "is_main_process", lambda: True)

    cfg = mnode.ClusterConfig(num_nodes=1, node_rank=0, master_addr="localhost", master_port=1234)
    coord = mnode.MultiNodeCoordinator(cfg)
    coord.initialized = True
    coord.active_nodes = {0}
    health = coord.monitor_health()
    assert health["node_rank"] == 0, "Condition must be true"
    aggregated = coord.aggregate_metrics({"loss": 1.5}, reduction="sum")
    assert aggregated["loss"] == 1.5, "Condition must be true"


def test_ab_testing_flow(tmp_path):
    """ABTestManager records metrics and writes reports."""

    from codex_ml.training.ab_testing import ABTestConfig, ABTestManager

    config = ABTestConfig(
        experiment_name="exp1",
        control_variant="base",
        treatment_variants=["variant"],
        traffic_split={"base": 50.0, "variant": 50.0},
        min_samples=1,
    )
    manager = ABTestManager(config)
    manager.record_result("base", {"accuracy": 0.6})
    manager.record_result("variant", {"accuracy": 0.65})

    assert manager.is_significant(alpha=0.1) is True, "Condition must be true"
    winner = manager.get_winner()
    assert winner in {"base", "variant"}

    output_path = tmp_path / "report.json"
    manager.save_results(output_path)
    assert output_path.exists(), "Condition must be true"


def test_strategy_safe_callbacks_and_result(monkeypatch):
    """Training strategies provide safe callback defaults and dataclass results."""

    from codex_ml.training import strategies

    callbacks = strategies._safe_callbacks([])
    assert callbacks and isinstance(callbacks[0], strategies.NoOpCallback)

    result = strategies.TrainingResult(
        status="ok", backend="functional", final_epoch=0, output_dir="/tmp", extra={}
    )
    assert result.status == "ok", "Result must not be empty"
