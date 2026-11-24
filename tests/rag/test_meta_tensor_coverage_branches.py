"""Coverage tests for RAG meta-tensor safety boundary branches."""

from __future__ import annotations

import builtins
import gc
import sys
from datetime import UTC, datetime
from types import SimpleNamespace

from codex.rag.materialization_prevention import (
    MaterializationPreventionFramework,
    MaterializationRecoveryStrategy,
    MatTensorDetector,
)
from codex.rag.meta_tensor_guard import GuardRailReport, GuardRailStatus, MetaTensorGuardRail


class _Tensor:
    def __init__(
        self,
        *,
        device_type: str = "cpu",
        is_meta: bool = False,
        data_device_type: str | None = None,
        data_error: bool = False,
    ) -> None:
        self.device = SimpleNamespace(type=device_type)
        self.is_meta = is_meta
        self.shape = (2, 3)
        self.dtype = "float32"
        self._data_device_type = data_device_type
        self._data_error = data_error

    @property
    def data(self) -> SimpleNamespace:
        if self._data_error:
            raise RuntimeError("materialized")
        return SimpleNamespace(
            device=SimpleNamespace(type=self._data_device_type or self.device.type)
        )


def _model_with_meta_submodules():
    direct_meta = _Tensor(device_type="meta")
    meta_buffer = _Tensor(is_meta=True)
    sub = SimpleNamespace(
        named_parameters=lambda recurse=False: [("weight", _Tensor(device_type="meta"))],
        named_buffers=lambda recurse=False: [("cache", _Tensor(is_meta=True))],
    )
    model = SimpleNamespace(
        named_parameters=lambda: [("direct", direct_meta)],
        named_buffers=lambda: [("buffer", meta_buffer)],
        named_modules=lambda: [("", None), ("layer", sub)],
    )
    return model


def test_detector_covers_all_meta_tensor_strategies() -> None:
    assert MatTensorDetector._is_meta_tensor(_Tensor(device_type="meta"))
    assert MatTensorDetector._is_meta_tensor(_Tensor(is_meta=True))
    assert MatTensorDetector._is_meta_tensor(_Tensor(data_device_type="meta"))
    assert not MatTensorDetector._is_meta_tensor(_Tensor(data_error=True))
    assert not MatTensorDetector._is_meta_tensor(object())


def test_detector_reports_submodule_parameters_and_buffers() -> None:
    found = MatTensorDetector.detect_in_model(_model_with_meta_submodules())

    assert {(location.value, name) for location, name, _ in found} == {
        ("parameters", "direct"),
        ("buffers", "buffer"),
        ("submodule_params", "layer.weight"),
        ("submodule_buffers", "layer.cache"),
    }


def test_tensor_info_returns_missing_fields_and_errors() -> None:
    assert MatTensorDetector.get_tensor_info(object()) == {
        "shape": None,
        "dtype": None,
        "device": None,
        "is_meta": False,
    }

    class BrokenTensor:
        @property
        def shape(self):
            raise RuntimeError("shape unavailable")

    assert "shape unavailable" in MatTensorDetector.get_tensor_info(BrokenTensor())["error"]


def test_recovery_strategies_cover_cuda_and_failure_paths(monkeypatch) -> None:
    calls = SimpleNamespace(empty_cache=0, reset_peak_memory_stats=0)

    class Cuda:
        @staticmethod
        def is_available() -> bool:
            return True

        @staticmethod
        def empty_cache() -> None:
            calls.empty_cache += 1

        @staticmethod
        def reset_peak_memory_stats() -> None:
            calls.reset_peak_memory_stats += 1

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=Cuda))

    assert MaterializationRecoveryStrategy.strategy_cache_clear() == (True, "cache_clear")
    assert MaterializationRecoveryStrategy.strategy_memory_reset() == (True, "memory_reset")
    assert calls.empty_cache == 2
    assert calls.reset_peak_memory_stats == 1

    monkeypatch.setattr(gc, "collect", lambda: (_ for _ in ()).throw(RuntimeError("blocked")))
    assert MaterializationRecoveryStrategy.strategy_garbage_collection() == (
        False,
        "garbage_collection",
    )


def test_framework_records_positive_detection_and_disabled_recovery(monkeypatch) -> None:
    framework = MaterializationPreventionFramework("model")

    assert framework.detect_materialization(_model_with_meta_submodules())
    assert framework.monitor.get_summary()["total_events"] == 4

    framework.recovery_enabled = False
    assert framework.attempt_recovery() is False

    monkeypatch.setattr(
        MaterializationRecoveryStrategy,
        "try_all_strategies",
        lambda: [(True, "cache_clear"), (False, "memory_reset")],
    )
    framework.recovery_enabled = True
    assert framework.attempt_recovery() is True
    last_event = framework.monitor.events[-1]
    assert last_event.recovery_attempted
    assert last_event.recovery_method == "memory_reset"


def test_framework_environment_respects_existing_configuration(monkeypatch) -> None:
    monkeypatch.setenv("PYTORCH_CUDA_ALLOC_CONF", "configured")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")

    framework = MaterializationPreventionFramework()
    assert framework.setup_prevention_environment() == {}


def test_guard_environment_covers_cuda_and_allocation_failure(monkeypatch) -> None:
    class Cuda:
        @staticmethod
        def is_available() -> bool:
            return True

        @staticmethod
        def device_count() -> int:
            return 2

    def fail_allocation(*_args, **_kwargs):
        raise RuntimeError("allocation failed")

    fake_torch = SimpleNamespace(__version__="stub", cuda=Cuda, zeros=fail_allocation)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    report = MetaTensorGuardRail().check_environment()
    assert report.status == GuardRailStatus.PASSED
    assert report.details["device_count"] == 2
    assert report.details["cpu_allocation_test"].startswith("failed:")


def test_guard_pre_init_covers_gpu_memory_cleanup(monkeypatch) -> None:
    calls = SimpleNamespace(empty_cache=0)

    class Cuda:
        @staticmethod
        def is_available() -> bool:
            return True

        @staticmethod
        def empty_cache() -> None:
            calls.empty_cache += 1

        @staticmethod
        def mem_get_info() -> tuple[int, int]:
            return 2 * 1024 * 1024, 8 * 1024 * 1024

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=Cuda))

    report = MetaTensorGuardRail().check_pre_init_state()
    assert report.status == GuardRailStatus.PASSED
    assert calls.empty_cache == 1
    assert report.details["gpu_free_mb"] == 2


def test_guard_detects_direct_buffers_and_submodule_tensors() -> None:
    report = MetaTensorGuardRail().check_meta_tensors_post_init(_model_with_meta_submodules())

    assert report.status == GuardRailStatus.FAILED
    assert report.details["meta_params"] == ["direct"]
    assert report.details["meta_buffers"] == ["buffer"]
    assert report.details["meta_submodule_params"] == ["layer.weight"]
    assert report.details["meta_submodule_buffers"] == ["layer.cache"]
    assert report.details["total_meta_tensors"] == 4


def test_guard_oom_covers_high_system_and_gpu_usage(monkeypatch) -> None:
    fake_psutil = SimpleNamespace(
        virtual_memory=lambda: SimpleNamespace(percent=96, available=4 * 1024 * 1024)
    )

    class Cuda:
        @staticmethod
        def is_available() -> bool:
            return True

        @staticmethod
        def mem_get_info() -> tuple[int, int]:
            return 1024 * 1024, 32 * 1024 * 1024

    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=Cuda))

    report = MetaTensorGuardRail().check_oom_condition()
    assert report.status == GuardRailStatus.FAILED
    assert report.details["system_memory_percent"] == 96
    assert report.details["gpu_memory_percent"] > 95


def test_guard_recovery_retries_and_summary_handles_empty_reports() -> None:
    guard = MetaTensorGuardRail(max_recovery_attempts=2)
    attempts = 0

    def recover() -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("first attempt")

    report = guard.check_recovery_mechanism(recover)
    assert report.status == GuardRailStatus.RECOVERED
    assert report.details["recovery_attempts"] == 2

    empty = MetaTensorGuardRail().get_summary()
    assert empty["pass_rate"] == 0
    assert empty["avg_check_time_ms"] == 0


def test_detector_handles_data_and_model_exceptions(monkeypatch) -> None:
    class FailingData:
        accesses = 0
        device = SimpleNamespace(type="cpu")
        is_meta = False

        @property
        def data(self):
            self.accesses += 1
            if self.accesses > 1:
                raise TypeError("data materialization failed")
            return SimpleNamespace(device=SimpleNamespace(type="cpu"))

    assert MatTensorDetector._is_meta_tensor(FailingData())

    monkeypatch.setattr(
        MaterializationRecoveryStrategy,
        "strategy_garbage_collection",
        MaterializationRecoveryStrategy.strategy_garbage_collection,
    )
    broken_model = SimpleNamespace(
        named_parameters=lambda: (_ for _ in ()).throw(RuntimeError("broken model"))
    )
    assert MatTensorDetector.detect_in_model(broken_model) == []


def test_recovery_strategies_cover_missing_and_broken_cuda(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace())
    assert MaterializationRecoveryStrategy.strategy_cache_clear() == (True, "cache_clear")
    assert MaterializationRecoveryStrategy.strategy_memory_reset() == (True, "memory_reset")

    class BrokenCuda:
        @staticmethod
        def is_available() -> bool:
            raise RuntimeError("cuda query failed")

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=BrokenCuda))
    assert MaterializationRecoveryStrategy.strategy_cache_clear() == (False, "cache_clear")
    assert MaterializationRecoveryStrategy.strategy_memory_reset() == (False, "memory_reset")


def test_guard_environment_and_model_introspection_failures(monkeypatch) -> None:
    real_import = builtins.__import__

    def without_torch(name, *args, **kwargs):
        if name == "torch":
            raise ImportError("missing torch")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_torch)
    report = MetaTensorGuardRail().check_environment()
    assert report.status == GuardRailStatus.FAILED
    assert "import_error" in report.details

    broken_model = SimpleNamespace(
        named_parameters=lambda: (_ for _ in ()).throw(RuntimeError("broken model")),
        named_buffers=lambda: [],
        named_modules=lambda: [],
    )
    post_init = MetaTensorGuardRail().check_meta_tensors_post_init(broken_model)
    assert post_init.status == GuardRailStatus.FAILED
    assert "broken model" in post_init.details["error"]


def test_guard_oom_tolerates_gpu_introspection_failure(monkeypatch) -> None:
    fake_psutil = SimpleNamespace(
        virtual_memory=lambda: SimpleNamespace(percent=10, available=8 * 1024 * 1024)
    )

    class BrokenCuda:
        @staticmethod
        def is_available() -> bool:
            return True

        @staticmethod
        def mem_get_info():
            raise RuntimeError("mem query failed")

    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=BrokenCuda))

    report = MetaTensorGuardRail().check_oom_condition()
    assert report.status == GuardRailStatus.PASSED
    assert report.details["system_memory_percent"] == 10
    assert "gpu_memory_percent" not in report.details


def test_guard_report_error_and_summary_logging(caplog) -> None:
    error = RuntimeError("failed")
    report = GuardRailReport(
        name="failed",
        status=GuardRailStatus.FAILED,
        timestamp=datetime.now(UTC),
        details={"value": 1},
        error=error,
    )
    assert report.to_dict()["error"] == "failed"

    guard = MetaTensorGuardRail()
    guard.reports.append(report)
    guard.log_summary()
    assert "Guard Rail Summary" in caplog.text
