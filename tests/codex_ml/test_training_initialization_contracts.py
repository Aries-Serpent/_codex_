"""Regression coverage for typed training initialization and fallback contracts."""

from __future__ import annotations

import builtins
import hashlib
import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import get_type_hints
from unittest.mock import Mock

import pytest

from codex_ml import _train_init_helpers as helpers
from codex_ml import train_loop
from codex_ml._train_init_helpers import setup_optimizer_with_dp
from codex_ml.training.dp_config import DifferentialPrivacyConfig


@pytest.mark.parametrize(
    ("field", "variable"),
    [
        ("epsilon", "EPSILON"),
        ("delta", "DELTA"),
        ("noise_multiplier", "NOISE_MULTIPLIER"),
        ("max_grad_norm", "MAX_GRAD_NORM"),
    ],
)
def test_dp_environment_keeps_numeric_and_boolean_types(
    field: str, variable: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    dependency_check = Mock()
    monkeypatch.setattr(DifferentialPrivacyConfig, "_ensure_dependency", dependency_check)
    monkeypatch.setenv("PHASE2_DP_ENABLED", "true")
    monkeypatch.setenv("PHASE2_DP_SECURE_RNG", "true")
    monkeypatch.setenv(f"PHASE2_DP_{variable}", "0.125")

    config = helpers.setup_differential_privacy_config(None, env_prefix="PHASE2_DP_")

    assert isinstance(config, DifferentialPrivacyConfig)
    assert config.enabled is True
    assert config.secure_rng is True
    assert getattr(config, field) == 0.125
    dependency_check.assert_called_once()


def test_dp_invalid_number_uses_default_and_requires_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PHASE2_DP_ENABLED", "true")
    monkeypatch.setenv("PHASE2_DP_EPSILON", "not-a-number")
    check = Mock()
    monkeypatch.setattr(DifferentialPrivacyConfig, "_ensure_dependency", check)
    config = helpers.setup_differential_privacy_config(None, env_prefix="PHASE2_DP_")
    assert config.epsilon == DifferentialPrivacyConfig().epsilon

    check.side_effect = ImportError("Opacus missing")
    assert helpers.setup_differential_privacy_config(None, env_prefix="PHASE2_DP_") is None


def test_first_parameter_dtype_empty_and_populated_models() -> None:
    empty = SimpleNamespace(parameters=lambda: iter(()))
    populated = SimpleNamespace(parameters=lambda: iter([SimpleNamespace(dtype="float32")]))
    assert helpers._first_param_dtype(empty) is None
    assert helpers._first_param_dtype(populated) == "float32"


@pytest.mark.parametrize("dp_settings", [None, DifferentialPrivacyConfig(enabled=False)])
def test_optimizer_without_dp_preserves_model_and_loader(
    dp_settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    import torch.optim

    model = SimpleNamespace(parameters=lambda: [object()])
    loader = object()
    optimizer = Mock()
    monkeypatch.setattr(torch.optim, "Adam", Mock(return_value=optimizer))

    assert setup_optimizer_with_dp(model, 0.001, None, dp_settings, loader) == (
        model,
        optimizer,
        loader,
        None,
    )


@pytest.mark.parametrize("failure", ["import", "optimizer"])
def test_optimizer_setup_failure_preserves_model_and_loader(
    failure: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    import torch.optim

    model = SimpleNamespace(parameters=lambda: [object()])
    loader = object()
    if failure == "import":
        real_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name == "torch.optim":
                raise ImportError("optimizer unavailable")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", guarded_import)
    else:
        monkeypatch.setattr(torch.optim, "Adam", Mock(side_effect=ValueError("invalid params")))

    assert setup_optimizer_with_dp(model, 0.001, None, None, loader) == (
        model,
        None,
        loader,
        None,
    )


def _load_with_import_failure(
    monkeypatch: pytest.MonkeyPatch,
    source: Path,
    blocked: tuple[str, ...],
    error: type[Exception] = ImportError,
) -> ModuleType:
    real_import = builtins.__import__

    def guarded_import(name: str, *args, **kwargs):
        if name in blocked:
            raise error(f"test backend unavailable: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    name = f"_phase2_initialization_{source.stem}"
    spec = importlib.util.spec_from_file_location(name, source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def test_training_fallback_parameters_match_providers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_with_import_failure(
        monkeypatch,
        Path(train_loop.__file__),
        (
            "codex_ml.utils.repro",
            "codex_ml.utils.seeding",
            "codex_ml.telemetry",
            "codex_ml.utils.retention",
        ),
    )
    for name in (
        "record_dataset_checksums",
        "set_reproducible",
        "start_metrics_server",
        "prune_checkpoints",
    ):
        fallback = getattr(module, name)
        provider = getattr(train_loop, name)
        assert {
            key: value.replace(annotation=inspect.Parameter.empty)
            for key, value in inspect.signature(fallback).parameters.items()
        } == {
            key: value.replace(annotation=inspect.Parameter.empty)
            for key, value in inspect.signature(provider).parameters.items()
        }
        assert get_type_hints(fallback) == get_type_hints(provider)
    assert module.record_dataset_checksums([], tmp_path / "checksums.json") == {}
    assert module.set_reproducible(1, deterministic=True) is None
    assert module.start_metrics_server(port=9123, addr="127.0.0.1") is None
    assert module.prune_checkpoints(tmp_path, keep_last=2) == {"dry_run": True}


def test_cli_fallback_returns_logger_and_preserves_exception_behavior(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    from codex_ml.cli import entrypoints

    module = _load_with_import_failure(
        monkeypatch,
        Path(entrypoints.__file__),
        ("codex_ml.codex_structured_logging",),
        TypeError,
    )
    logger = module.init_json_logging(
        default_level="DEBUG", session_id="test", session_log_dir=tmp_path
    )
    assert isinstance(logger, logging.Logger)
    assert module.ArgparseJSONParser is None
    logger.info("not emitted")
    logger.error("not emitted")
    module.log_event(logger, "test.event", count=3)
    with module.capture_exceptions(logger) as entered:
        assert entered is None
    with pytest.raises(ValueError, match="not suppressed"):
        with module.capture_exceptions(logger=logger):
            raise ValueError("not suppressed")

    def decorated(value: int) -> int:
        return value + 1

    assert module.capture_exceptions(decorated) is decorated
    assert module.capture_exceptions(decorated)(2) == 3
    assert capsys.readouterr() == ("", "")


@pytest.fixture
def minimal_training(monkeypatch: pytest.MonkeyPatch):
    """Isolate orchestration from Torch, external telemetry and session sinks."""
    monkeypatch.setattr(train_loop, "_HAS_MLFLOW", False)
    monkeypatch.setattr(train_loop, "_set_seed", lambda seed: seed or 1)
    monkeypatch.setattr(train_loop, "set_reproducible", lambda *args, **kwargs: None)
    monkeypatch.setattr(train_loop, "_resolve_device", lambda device: None)
    monkeypatch.setattr(train_loop, "_resolve_dtype", lambda dtype: None)
    monkeypatch.setattr(
        train_loop, "get_session_logger", Mock(side_effect=RuntimeError("disabled test sink"))
    )
    monkeypatch.setattr(helpers, "setup_metrics_registry", lambda *args: (None, None))
    monkeypatch.setattr(helpers, "setup_dataset_and_loader", lambda *args: (None, None))
    monkeypatch.setattr(helpers, "setup_model_device_dtype", lambda *args: None)
    monkeypatch.setattr(
        helpers, "setup_optimizer_with_dp", lambda model, *args: (model, None, args[-1], None)
    )
    return train_loop


def test_training_hashes_datasets_when_artifact_directory_unavailable(
    minimal_training, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(minimal_training, "_HAS_TORCH", False)
    monkeypatch.setattr(helpers, "setup_artifacts_directory", lambda *args, **kwargs: None)
    source = tmp_path / "dataset.txt"
    source.write_text("training record\n", encoding="utf-8")
    checksum_writer = Mock(side_effect=AssertionError("must not write to a None path"))
    monkeypatch.setattr(minimal_training, "record_dataset_checksums", checksum_writer)

    result = minimal_training.run_training(epochs=1, seed=1, dataset_sources=[source])

    assert result["dataset_checksums"] == [hashlib.sha256(source.read_bytes()).hexdigest()]
    checksum_writer.assert_not_called()
    assert not (tmp_path / "dataset_checksums.json").exists()


def test_training_uses_distinct_data_and_model_drift_detectors(
    minimal_training, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from codex_ml.monitoring.data_drift import DataDriftDetector
    from codex_ml.monitoring.model_drift import ModelDriftDetector

    data_detector = DataDriftDetector()
    model_detector = ModelDriftDetector()
    data_check = Mock(wraps=data_detector.check_epoch)
    model_baseline = Mock(wraps=model_detector.update_baseline)
    model_check = Mock(wraps=model_detector.check)
    monkeypatch.setattr(data_detector, "check_epoch", data_check)
    monkeypatch.setattr(model_detector, "update_baseline", model_baseline)
    monkeypatch.setattr(model_detector, "check", model_check)
    monkeypatch.setattr(minimal_training, "_DataDriftDetector", lambda: data_detector)
    monkeypatch.setattr(
        "codex_ml.monitoring.model_drift.ModelDriftDetector", lambda: model_detector
    )
    model = SimpleNamespace(
        parameters=lambda: [],
        to=lambda *args, **kwargs: None,
        train=lambda: None,
    )
    optimizer = SimpleNamespace(
        param_groups=[{"lr": 0.001}],
        zero_grad=lambda **kwargs: None,
        step=lambda: None,
    )
    monkeypatch.setattr(minimal_training, "_HAS_TORCH", True)
    monkeypatch.setattr(minimal_training, "_synthetic_step", lambda model: 0.25)
    monkeypatch.setattr(
        helpers, "setup_optimizer_with_dp", lambda model, *args: (model, optimizer, args[-1], None)
    )

    result = minimal_training.run_training(
        epochs=2, steps_per_epoch=2, seed=1, model=model, art_dir=tmp_path, return_state=True
    )

    assert result["final_epoch"] == 2
    model_baseline.assert_called_once()
    model_check.assert_called_once()
    data_check.assert_called_once()
    assert model_check.call_args.kwargs["epoch"] == 2
    assert data_check.call_args.kwargs["epoch"] == 2
    assert "drift_result_epoch" in result["state"]


def test_enabled_dp_training_uses_private_model_optimizer_and_loader(
    minimal_training, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import torch.optim

    original_model = SimpleNamespace(parameters=lambda: [object()])
    original_loader = object()
    private_model = SimpleNamespace(
        parameters=lambda: [],
        to=lambda *args, **kwargs: None,
        train=Mock(),
    )
    private_optimizer = Mock(param_groups=[{"lr": 0.001}])
    consumed = []

    class PrivateLoader:
        def __iter__(self):
            consumed.append(True)
            return iter([object(), object()])

    private_loader = PrivateLoader()
    engine = Mock()
    engine.make_private.return_value = (private_model, private_optimizer, private_loader)
    privacy_engine = Mock(return_value=engine)
    monkeypatch.setitem(sys.modules, "opacus", SimpleNamespace(PrivacyEngine=privacy_engine))
    base_optimizer = Mock()
    monkeypatch.setattr(torch.optim, "Adam", Mock(return_value=base_optimizer))
    monkeypatch.setattr(minimal_training, "_HAS_TORCH", True)
    monkeypatch.setattr(helpers, "setup_dataset_and_loader", lambda *args: (None, original_loader))
    monkeypatch.setattr(helpers, "setup_optimizer_with_dp", setup_optimizer_with_dp)
    training_step = Mock(return_value=0.25)
    monkeypatch.setattr(minimal_training, "_synthetic_step", training_step)

    result = minimal_training.run_training(
        epochs=1,
        steps_per_epoch=2,
        seed=1,
        model=original_model,
        dp_config={"enabled": True},
        art_dir=tmp_path,
        return_state=True,
    )

    privacy_engine.assert_called_once_with(secure_rng=False)
    engine.make_private.assert_called_once_with(
        module=original_model,
        optimizer=base_optimizer,
        data_loader=original_loader,
        noise_multiplier=1.0,
        max_grad_norm=1.0,
    )
    assert result["state"]["model"] is private_model
    assert result["state"]["optimizer"] is private_optimizer
    assert result["privacy_engine"] is True
    assert consumed == [True]
    assert training_step.call_count == 2
    assert all(call.args == (private_model,) for call in training_step.call_args_list)
    assert private_optimizer.step.call_count == 2
    private_model.train.assert_called_once()


@pytest.mark.parametrize("requested_dtype", ["bf16", "bfloat16"])
def test_required_bf16_without_torch_is_a_capability_error(
    requested_dtype: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)
    with pytest.raises(RuntimeError, match="bf16 required but PyTorch") as caught:
        train_loop._assert_bf16_capability(requested_dtype, None, True)
    assert isinstance(caught.value.__cause__, ImportError)


def test_optional_or_unrequested_bf16_does_not_require_torch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)
    train_loop._assert_bf16_capability("bf16", None, False)
    train_loop._assert_bf16_capability("float32", None, True)


@pytest.mark.parametrize("failure_stage", ["allocation", "placement", "matmul"])
def test_bf16_probe_never_downgrades_after_runtime_failure(
    failure_stage: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    bf16 = object()
    allocations: list[object] = []
    placements: list[object] = []
    products: list[object] = []
    failure = RuntimeError(f"{failure_stage} failed")

    class ProbeTensor:
        def to(self, device: object):
            placements.append(device)
            if failure_stage == "placement":
                raise failure
            return self

        def __matmul__(self, other: object):
            products.append(other)
            if failure_stage == "matmul":
                raise failure
            return self

    def ones(shape: tuple[int, int], *, dtype: object) -> ProbeTensor:
        assert shape == (2, 2)
        allocations.append(dtype)
        if failure_stage == "allocation":
            raise failure
        return ProbeTensor()

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(bfloat16=bf16, ones=ones))
    with pytest.raises(RuntimeError, match="bf16 required but runtime") as caught:
        train_loop._assert_bf16_capability("bf16", bf16, True, device="cuda:1")

    assert caught.value.__cause__ is failure
    assert allocations and all(dtype is bf16 for dtype in allocations)
    if failure_stage == "placement":
        assert placements == ["cuda:1"]
        assert products == []


def test_bf16_probe_uses_requested_device_and_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bf16 = object()
    placements: list[object] = []
    allocations: list[object] = []
    products: list[object] = []

    class ProbeTensor:
        def to(self, device: object):
            placements.append(device)
            return self

        def __matmul__(self, other: object):
            products.append(other)
            return self

    def ones(shape: tuple[int, int], *, dtype: object) -> ProbeTensor:
        allocations.append(dtype)
        return ProbeTensor()

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(bfloat16=bf16, ones=ones))
    train_loop._assert_bf16_capability(None, bf16, True, device="cuda:1")

    assert allocations == [bf16, bf16]
    assert placements == ["cuda:1", "cuda:1"]
    assert len(products) == 1


@pytest.mark.parametrize("error_type", [ValueError, TypeError, RuntimeError, OSError])
def test_callback_start_errors_are_recorded_not_lost(
    error_type: type[Exception], minimal_training, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(minimal_training, "_HAS_TORCH", False)

    class BrokenCallback(minimal_training.Callback):
        def on_train_start(self, state):
            raise error_type("callback startup failed")

    result = minimal_training.run_training(
        epochs=1, art_dir=tmp_path, callbacks=[BrokenCallback()], return_state=True
    )

    assert result["final_epoch"] == 1
    assert len(result["callback_errors"]) == 1
    error = result["callback_errors"][0]
    assert error["stage"] == "on_train_start"
    assert error["error"] == "callback startup failed"
    assert result["state"]["callback_errors"] == result["callback_errors"]


@pytest.mark.parametrize("error_type", [KeyboardInterrupt, SystemExit])
def test_callback_cancellation_is_not_suppressed(
    error_type: type[BaseException],
    minimal_training,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(minimal_training, "_HAS_TORCH", False)

    class CancelledCallback(minimal_training.Callback):
        def on_train_start(self, state):
            raise error_type("cancel training")

    with pytest.raises(error_type, match="cancel training"):
        minimal_training.run_training(epochs=0, art_dir=tmp_path, callbacks=[CancelledCallback()])


def test_cli_unknown_model_remains_a_registry_error(
    minimal_training, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from codex_ml.models import registry as models
    from codex_ml.registry.base import Registry, RegistryNotFoundError

    monkeypatch.setattr(models, "model_registry", Registry("strict-cli-model"))
    monkeypatch.setattr(minimal_training, "instantiate_model", models.get_model)
    monkeypatch.setattr(minimal_training, "_HAS_TORCH", False)

    with pytest.raises(RegistryNotFoundError, match="missing-test-model"):
        minimal_training.main(
            ["--model-name", "missing-test-model", "--epochs", "0", "--art-dir", str(tmp_path)]
        )


def test_model_initialization_runtime_errors_remain_fatal(
    minimal_training, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    failure = RuntimeError("model initialization failed")
    monkeypatch.setattr(minimal_training, "_load_or_create_model", Mock(side_effect=failure))
    with pytest.raises(RuntimeError, match="model initialization failed") as caught:
        minimal_training.run_training(epochs=0, art_dir=tmp_path)
    assert caught.value is failure
