"""Lightweight logging utilities (TensorBoard + MLflow)."""

from __future__ import annotations

import importlib
import json
import logging
logger = logging.getLogger(__name__)
import os
import time
from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codex_ml.utils.optional import optional_dependency_error

try:  # pragma: no cover - tensorboard is optional in lightweight envs
    from torch.utils.tensorboard import SummaryWriter
except Exception:  # pragma: no cover - fall back to a stub
    SummaryWriter = None  # type: ignore[assignment]

try:  # pragma: no cover - MLflow is optional for offline smoke tests
    import mlflow
except Exception:  # pragma: no cover - guard offline runs that skip mlflow install
    mlflow = None  # type: ignore[assignment]

try:  # pragma: no cover - optional runtime dependency
    import psutil
except Exception:  # pragma: no cover - allow execution without psutil
    psutil = None  # type: ignore[assignment]

try:  # pragma: no cover - optional GPU metrics dependency
    import pynvml
except Exception:  # pragma: no cover - allow execution without NVML bindings
    pynvml = None  # type: ignore[assignment]


LOGGER = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_import_module__mutmut_orig(name: str) -> Any:
    return importlib.import_module(name)


def x_import_module__mutmut_1(name: str) -> Any:
    return importlib.import_module(None)

x_import_module__mutmut_mutants : ClassVar[MutantDict] = {
'x_import_module__mutmut_1': x_import_module__mutmut_1
}

def import_module(*args, **kwargs):
    result = _mutmut_trampoline(x_import_module__mutmut_orig, x_import_module__mutmut_mutants, args, kwargs)
    return result 

import_module.__signature__ = _mutmut_signature(x_import_module__mutmut_orig)
x_import_module__mutmut_orig.__name__ = 'x_import_module'


@dataclass(slots=True)
class LoggingConfig:
    enable_tensorboard: bool = False
    tensorboard_log_dir: str = "runs"
    enable_mlflow: bool = False
    mlflow_run_name: str = "codex-training"
    mlflow_tracking_uri: str | None = None
    mlflow_offline: bool = True
    mlflow_tracking_dir: str | Path = "./mlruns"
    enable_fallback_metrics: bool = True
    fallback_metrics_path: str | Path = "metrics_fallback.ndjson"


@dataclass(slots=True)
class LoggingSession:
    tensorboard: SummaryWriter | None
    mlflow_active: bool
    fallback_writer: FallbackMetricsWriter | None


@dataclass(slots=True)
class LogHandles:
    """Lightweight container for optional logging backends."""

    tb: SummaryWriter | None = None
    mlflow_run_active: bool = False


class FallbackMetricsWriter:
    """Persist metrics to JSONL when richer telemetry backends are unavailable."""

    def xǁFallbackMetricsWriterǁ__init____mutmut_orig(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def xǁFallbackMetricsWriterǁ__init____mutmut_1(self, path: Path) -> None:
        self.path = None
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def xǁFallbackMetricsWriterǁ__init____mutmut_2(self, path: Path) -> None:
        self.path = Path(None)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def xǁFallbackMetricsWriterǁ__init____mutmut_3(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=None, exist_ok=True)

    def xǁFallbackMetricsWriterǁ__init____mutmut_4(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=None)

    def xǁFallbackMetricsWriterǁ__init____mutmut_5(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(exist_ok=True)

    def xǁFallbackMetricsWriterǁ__init____mutmut_6(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, )

    def xǁFallbackMetricsWriterǁ__init____mutmut_7(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=False, exist_ok=True)

    def xǁFallbackMetricsWriterǁ__init____mutmut_8(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=False)
    
    xǁFallbackMetricsWriterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFallbackMetricsWriterǁ__init____mutmut_1': xǁFallbackMetricsWriterǁ__init____mutmut_1, 
        'xǁFallbackMetricsWriterǁ__init____mutmut_2': xǁFallbackMetricsWriterǁ__init____mutmut_2, 
        'xǁFallbackMetricsWriterǁ__init____mutmut_3': xǁFallbackMetricsWriterǁ__init____mutmut_3, 
        'xǁFallbackMetricsWriterǁ__init____mutmut_4': xǁFallbackMetricsWriterǁ__init____mutmut_4, 
        'xǁFallbackMetricsWriterǁ__init____mutmut_5': xǁFallbackMetricsWriterǁ__init____mutmut_5, 
        'xǁFallbackMetricsWriterǁ__init____mutmut_6': xǁFallbackMetricsWriterǁ__init____mutmut_6, 
        'xǁFallbackMetricsWriterǁ__init____mutmut_7': xǁFallbackMetricsWriterǁ__init____mutmut_7, 
        'xǁFallbackMetricsWriterǁ__init____mutmut_8': xǁFallbackMetricsWriterǁ__init____mutmut_8
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFallbackMetricsWriterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁFallbackMetricsWriterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁFallbackMetricsWriterǁ__init____mutmut_orig)
    xǁFallbackMetricsWriterǁ__init____mutmut_orig.__name__ = 'xǁFallbackMetricsWriterǁ__init__'

    def xǁFallbackMetricsWriterǁwrite__mutmut_orig(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_1(self, metrics: Mapping[str, float], step: int) -> None:
        payload = None
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_2(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "XXtsXX": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_3(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "TS": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_4(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "XXstepXX": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_5(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "STEP": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_6(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "XXmetricsXX": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_7(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "METRICS": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_8(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(None) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_9(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open(None, encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_10(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding=None) as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_11(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open(encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_12(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", ) as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_13(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("XXaXX", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_14(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("A", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_15(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="XXutf-8XX") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_16(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="UTF-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_17(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(None)
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_18(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(None, ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_19(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=None))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_20(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(ensure_ascii=False))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_21(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_22(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True))
            handle.write("\n")

    def xǁFallbackMetricsWriterǁwrite__mutmut_23(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write(None)

    def xǁFallbackMetricsWriterǁwrite__mutmut_24(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("XX\nXX")
    
    xǁFallbackMetricsWriterǁwrite__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFallbackMetricsWriterǁwrite__mutmut_1': xǁFallbackMetricsWriterǁwrite__mutmut_1, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_2': xǁFallbackMetricsWriterǁwrite__mutmut_2, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_3': xǁFallbackMetricsWriterǁwrite__mutmut_3, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_4': xǁFallbackMetricsWriterǁwrite__mutmut_4, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_5': xǁFallbackMetricsWriterǁwrite__mutmut_5, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_6': xǁFallbackMetricsWriterǁwrite__mutmut_6, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_7': xǁFallbackMetricsWriterǁwrite__mutmut_7, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_8': xǁFallbackMetricsWriterǁwrite__mutmut_8, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_9': xǁFallbackMetricsWriterǁwrite__mutmut_9, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_10': xǁFallbackMetricsWriterǁwrite__mutmut_10, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_11': xǁFallbackMetricsWriterǁwrite__mutmut_11, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_12': xǁFallbackMetricsWriterǁwrite__mutmut_12, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_13': xǁFallbackMetricsWriterǁwrite__mutmut_13, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_14': xǁFallbackMetricsWriterǁwrite__mutmut_14, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_15': xǁFallbackMetricsWriterǁwrite__mutmut_15, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_16': xǁFallbackMetricsWriterǁwrite__mutmut_16, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_17': xǁFallbackMetricsWriterǁwrite__mutmut_17, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_18': xǁFallbackMetricsWriterǁwrite__mutmut_18, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_19': xǁFallbackMetricsWriterǁwrite__mutmut_19, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_20': xǁFallbackMetricsWriterǁwrite__mutmut_20, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_21': xǁFallbackMetricsWriterǁwrite__mutmut_21, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_22': xǁFallbackMetricsWriterǁwrite__mutmut_22, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_23': xǁFallbackMetricsWriterǁwrite__mutmut_23, 
        'xǁFallbackMetricsWriterǁwrite__mutmut_24': xǁFallbackMetricsWriterǁwrite__mutmut_24
    }
    
    def write(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFallbackMetricsWriterǁwrite__mutmut_orig"), object.__getattribute__(self, "xǁFallbackMetricsWriterǁwrite__mutmut_mutants"), args, kwargs, self)
        return result 
    
    write.__signature__ = _mutmut_signature(xǁFallbackMetricsWriterǁwrite__mutmut_orig)
    xǁFallbackMetricsWriterǁwrite__mutmut_orig.__name__ = 'xǁFallbackMetricsWriterǁwrite'


def x__create_tensorboard_writer__mutmut_orig(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_1(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is not None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_2(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            None,
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_3(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            None,
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_4(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_5(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_6(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "XX%sXX",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_7(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%S",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_8(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                None,
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_9(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose=None,
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_10(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_11(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_12(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "XXtensorboardXX",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_13(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "TENSORBOARD",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_14(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="XXTensorBoard loggingXX",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_15(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="tensorboard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_16(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TENSORBOARD LOGGING",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_17(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = None
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_18(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(None)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_19(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=None, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_20(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=None)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_21(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_22(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, )
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_23(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=False, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_24(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=False)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_25(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning(None, log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_26(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", None, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_27(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, None)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_28(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning(log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_29(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_30(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, )
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_31(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("XXUnable to create TensorBoard log directory '%s': %sXX", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_32(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("unable to create tensorboard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_33(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("UNABLE TO CREATE TENSORBOARD LOG DIRECTORY '%S': %S", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_34(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(None)
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_35(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(None))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_36(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning(None, exc)
        return None


def x__create_tensorboard_writer__mutmut_37(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", None)
        return None


def x__create_tensorboard_writer__mutmut_38(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning(exc)
        return None


def x__create_tensorboard_writer__mutmut_39(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", )
        return None


def x__create_tensorboard_writer__mutmut_40(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("XXFailed to initialise TensorBoard writer: %sXX", exc)
        return None


def x__create_tensorboard_writer__mutmut_41(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("failed to initialise tensorboard writer: %s", exc)
        return None


def x__create_tensorboard_writer__mutmut_42(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("FAILED TO INITIALISE TENSORBOARD WRITER: %S", exc)
        return None

x__create_tensorboard_writer__mutmut_mutants : ClassVar[MutantDict] = {
'x__create_tensorboard_writer__mutmut_1': x__create_tensorboard_writer__mutmut_1, 
    'x__create_tensorboard_writer__mutmut_2': x__create_tensorboard_writer__mutmut_2, 
    'x__create_tensorboard_writer__mutmut_3': x__create_tensorboard_writer__mutmut_3, 
    'x__create_tensorboard_writer__mutmut_4': x__create_tensorboard_writer__mutmut_4, 
    'x__create_tensorboard_writer__mutmut_5': x__create_tensorboard_writer__mutmut_5, 
    'x__create_tensorboard_writer__mutmut_6': x__create_tensorboard_writer__mutmut_6, 
    'x__create_tensorboard_writer__mutmut_7': x__create_tensorboard_writer__mutmut_7, 
    'x__create_tensorboard_writer__mutmut_8': x__create_tensorboard_writer__mutmut_8, 
    'x__create_tensorboard_writer__mutmut_9': x__create_tensorboard_writer__mutmut_9, 
    'x__create_tensorboard_writer__mutmut_10': x__create_tensorboard_writer__mutmut_10, 
    'x__create_tensorboard_writer__mutmut_11': x__create_tensorboard_writer__mutmut_11, 
    'x__create_tensorboard_writer__mutmut_12': x__create_tensorboard_writer__mutmut_12, 
    'x__create_tensorboard_writer__mutmut_13': x__create_tensorboard_writer__mutmut_13, 
    'x__create_tensorboard_writer__mutmut_14': x__create_tensorboard_writer__mutmut_14, 
    'x__create_tensorboard_writer__mutmut_15': x__create_tensorboard_writer__mutmut_15, 
    'x__create_tensorboard_writer__mutmut_16': x__create_tensorboard_writer__mutmut_16, 
    'x__create_tensorboard_writer__mutmut_17': x__create_tensorboard_writer__mutmut_17, 
    'x__create_tensorboard_writer__mutmut_18': x__create_tensorboard_writer__mutmut_18, 
    'x__create_tensorboard_writer__mutmut_19': x__create_tensorboard_writer__mutmut_19, 
    'x__create_tensorboard_writer__mutmut_20': x__create_tensorboard_writer__mutmut_20, 
    'x__create_tensorboard_writer__mutmut_21': x__create_tensorboard_writer__mutmut_21, 
    'x__create_tensorboard_writer__mutmut_22': x__create_tensorboard_writer__mutmut_22, 
    'x__create_tensorboard_writer__mutmut_23': x__create_tensorboard_writer__mutmut_23, 
    'x__create_tensorboard_writer__mutmut_24': x__create_tensorboard_writer__mutmut_24, 
    'x__create_tensorboard_writer__mutmut_25': x__create_tensorboard_writer__mutmut_25, 
    'x__create_tensorboard_writer__mutmut_26': x__create_tensorboard_writer__mutmut_26, 
    'x__create_tensorboard_writer__mutmut_27': x__create_tensorboard_writer__mutmut_27, 
    'x__create_tensorboard_writer__mutmut_28': x__create_tensorboard_writer__mutmut_28, 
    'x__create_tensorboard_writer__mutmut_29': x__create_tensorboard_writer__mutmut_29, 
    'x__create_tensorboard_writer__mutmut_30': x__create_tensorboard_writer__mutmut_30, 
    'x__create_tensorboard_writer__mutmut_31': x__create_tensorboard_writer__mutmut_31, 
    'x__create_tensorboard_writer__mutmut_32': x__create_tensorboard_writer__mutmut_32, 
    'x__create_tensorboard_writer__mutmut_33': x__create_tensorboard_writer__mutmut_33, 
    'x__create_tensorboard_writer__mutmut_34': x__create_tensorboard_writer__mutmut_34, 
    'x__create_tensorboard_writer__mutmut_35': x__create_tensorboard_writer__mutmut_35, 
    'x__create_tensorboard_writer__mutmut_36': x__create_tensorboard_writer__mutmut_36, 
    'x__create_tensorboard_writer__mutmut_37': x__create_tensorboard_writer__mutmut_37, 
    'x__create_tensorboard_writer__mutmut_38': x__create_tensorboard_writer__mutmut_38, 
    'x__create_tensorboard_writer__mutmut_39': x__create_tensorboard_writer__mutmut_39, 
    'x__create_tensorboard_writer__mutmut_40': x__create_tensorboard_writer__mutmut_40, 
    'x__create_tensorboard_writer__mutmut_41': x__create_tensorboard_writer__mutmut_41, 
    'x__create_tensorboard_writer__mutmut_42': x__create_tensorboard_writer__mutmut_42
}

def _create_tensorboard_writer(*args, **kwargs):
    result = _mutmut_trampoline(x__create_tensorboard_writer__mutmut_orig, x__create_tensorboard_writer__mutmut_mutants, args, kwargs)
    return result 

_create_tensorboard_writer.__signature__ = _mutmut_signature(x__create_tensorboard_writer__mutmut_orig)
x__create_tensorboard_writer__mutmut_orig.__name__ = 'x__create_tensorboard_writer'


def x_init_tensorboard__mutmut_orig(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_1(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = None
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_2(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = None
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_3(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = False
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_4(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = None

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_5(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(None)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_6(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_7(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = None

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_8(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir and "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_9(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "XXrunsXX"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_10(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "RUNS"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_11(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = None
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_12(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module(None)
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_13(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("XXtorch.utils.tensorboardXX")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_14(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("TORCH.UTILS.TENSORBOARD")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_15(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = None
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_16(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(None, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_17(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, None, None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_18(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr("SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_19(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_20(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", )
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_21(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "XXSummaryWriterXX", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_22(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "summarywriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_23(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SUMMARYWRITER", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_24(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = ""
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_25(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is not None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_26(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                None,
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_27(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                None,
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_28(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_29(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_30(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "XX%sXX",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_31(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%S",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_32(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    None,
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_33(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose=None,
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_34(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_35(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_36(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "XXtensorboardXX",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_37(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "TENSORBOARD",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_38(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="XXTensorBoard loggingXX",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_39(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="tensorboard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_40(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TENSORBOARD LOGGING",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_41(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(None)

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_42(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(None))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_43(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is not None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_44(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            None,
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_45(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            None,
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_46(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_47(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_48(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "XX%sXX",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_49(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%S",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_50(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                None,
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_51(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose=None,
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_52(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_53(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_54(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "XXtensorboardXX",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_55(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "TENSORBOARD",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_56(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="XXTensorBoard loggingXX",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_57(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="tensorboard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_58(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TENSORBOARD LOGGING",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


def x_init_tensorboard__mutmut_59(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(None)

x_init_tensorboard__mutmut_mutants : ClassVar[MutantDict] = {
'x_init_tensorboard__mutmut_1': x_init_tensorboard__mutmut_1, 
    'x_init_tensorboard__mutmut_2': x_init_tensorboard__mutmut_2, 
    'x_init_tensorboard__mutmut_3': x_init_tensorboard__mutmut_3, 
    'x_init_tensorboard__mutmut_4': x_init_tensorboard__mutmut_4, 
    'x_init_tensorboard__mutmut_5': x_init_tensorboard__mutmut_5, 
    'x_init_tensorboard__mutmut_6': x_init_tensorboard__mutmut_6, 
    'x_init_tensorboard__mutmut_7': x_init_tensorboard__mutmut_7, 
    'x_init_tensorboard__mutmut_8': x_init_tensorboard__mutmut_8, 
    'x_init_tensorboard__mutmut_9': x_init_tensorboard__mutmut_9, 
    'x_init_tensorboard__mutmut_10': x_init_tensorboard__mutmut_10, 
    'x_init_tensorboard__mutmut_11': x_init_tensorboard__mutmut_11, 
    'x_init_tensorboard__mutmut_12': x_init_tensorboard__mutmut_12, 
    'x_init_tensorboard__mutmut_13': x_init_tensorboard__mutmut_13, 
    'x_init_tensorboard__mutmut_14': x_init_tensorboard__mutmut_14, 
    'x_init_tensorboard__mutmut_15': x_init_tensorboard__mutmut_15, 
    'x_init_tensorboard__mutmut_16': x_init_tensorboard__mutmut_16, 
    'x_init_tensorboard__mutmut_17': x_init_tensorboard__mutmut_17, 
    'x_init_tensorboard__mutmut_18': x_init_tensorboard__mutmut_18, 
    'x_init_tensorboard__mutmut_19': x_init_tensorboard__mutmut_19, 
    'x_init_tensorboard__mutmut_20': x_init_tensorboard__mutmut_20, 
    'x_init_tensorboard__mutmut_21': x_init_tensorboard__mutmut_21, 
    'x_init_tensorboard__mutmut_22': x_init_tensorboard__mutmut_22, 
    'x_init_tensorboard__mutmut_23': x_init_tensorboard__mutmut_23, 
    'x_init_tensorboard__mutmut_24': x_init_tensorboard__mutmut_24, 
    'x_init_tensorboard__mutmut_25': x_init_tensorboard__mutmut_25, 
    'x_init_tensorboard__mutmut_26': x_init_tensorboard__mutmut_26, 
    'x_init_tensorboard__mutmut_27': x_init_tensorboard__mutmut_27, 
    'x_init_tensorboard__mutmut_28': x_init_tensorboard__mutmut_28, 
    'x_init_tensorboard__mutmut_29': x_init_tensorboard__mutmut_29, 
    'x_init_tensorboard__mutmut_30': x_init_tensorboard__mutmut_30, 
    'x_init_tensorboard__mutmut_31': x_init_tensorboard__mutmut_31, 
    'x_init_tensorboard__mutmut_32': x_init_tensorboard__mutmut_32, 
    'x_init_tensorboard__mutmut_33': x_init_tensorboard__mutmut_33, 
    'x_init_tensorboard__mutmut_34': x_init_tensorboard__mutmut_34, 
    'x_init_tensorboard__mutmut_35': x_init_tensorboard__mutmut_35, 
    'x_init_tensorboard__mutmut_36': x_init_tensorboard__mutmut_36, 
    'x_init_tensorboard__mutmut_37': x_init_tensorboard__mutmut_37, 
    'x_init_tensorboard__mutmut_38': x_init_tensorboard__mutmut_38, 
    'x_init_tensorboard__mutmut_39': x_init_tensorboard__mutmut_39, 
    'x_init_tensorboard__mutmut_40': x_init_tensorboard__mutmut_40, 
    'x_init_tensorboard__mutmut_41': x_init_tensorboard__mutmut_41, 
    'x_init_tensorboard__mutmut_42': x_init_tensorboard__mutmut_42, 
    'x_init_tensorboard__mutmut_43': x_init_tensorboard__mutmut_43, 
    'x_init_tensorboard__mutmut_44': x_init_tensorboard__mutmut_44, 
    'x_init_tensorboard__mutmut_45': x_init_tensorboard__mutmut_45, 
    'x_init_tensorboard__mutmut_46': x_init_tensorboard__mutmut_46, 
    'x_init_tensorboard__mutmut_47': x_init_tensorboard__mutmut_47, 
    'x_init_tensorboard__mutmut_48': x_init_tensorboard__mutmut_48, 
    'x_init_tensorboard__mutmut_49': x_init_tensorboard__mutmut_49, 
    'x_init_tensorboard__mutmut_50': x_init_tensorboard__mutmut_50, 
    'x_init_tensorboard__mutmut_51': x_init_tensorboard__mutmut_51, 
    'x_init_tensorboard__mutmut_52': x_init_tensorboard__mutmut_52, 
    'x_init_tensorboard__mutmut_53': x_init_tensorboard__mutmut_53, 
    'x_init_tensorboard__mutmut_54': x_init_tensorboard__mutmut_54, 
    'x_init_tensorboard__mutmut_55': x_init_tensorboard__mutmut_55, 
    'x_init_tensorboard__mutmut_56': x_init_tensorboard__mutmut_56, 
    'x_init_tensorboard__mutmut_57': x_init_tensorboard__mutmut_57, 
    'x_init_tensorboard__mutmut_58': x_init_tensorboard__mutmut_58, 
    'x_init_tensorboard__mutmut_59': x_init_tensorboard__mutmut_59
}

def init_tensorboard(*args, **kwargs):
    result = _mutmut_trampoline(x_init_tensorboard__mutmut_orig, x_init_tensorboard__mutmut_mutants, args, kwargs)
    return result 

init_tensorboard.__signature__ = _mutmut_signature(x_init_tensorboard__mutmut_orig)
x_init_tensorboard__mutmut_orig.__name__ = 'x_init_tensorboard'


class MLflowHandle:
    def xǁMLflowHandleǁ__init____mutmut_orig(self, module: Any) -> None:
        self._module = module
    def xǁMLflowHandleǁ__init____mutmut_1(self, module: Any) -> None:
        self._module = None
    
    xǁMLflowHandleǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLflowHandleǁ__init____mutmut_1': xǁMLflowHandleǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLflowHandleǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMLflowHandleǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMLflowHandleǁ__init____mutmut_orig)
    xǁMLflowHandleǁ__init____mutmut_orig.__name__ = 'xǁMLflowHandleǁ__init__'

    def xǁMLflowHandleǁlog_metrics__mutmut_orig(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        self._module.log_metrics(metrics, step=step)

    def xǁMLflowHandleǁlog_metrics__mutmut_1(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        self._module.log_metrics(None, step=step)

    def xǁMLflowHandleǁlog_metrics__mutmut_2(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        self._module.log_metrics(metrics, step=None)

    def xǁMLflowHandleǁlog_metrics__mutmut_3(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        self._module.log_metrics(step=step)

    def xǁMLflowHandleǁlog_metrics__mutmut_4(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        self._module.log_metrics(metrics, )
    
    xǁMLflowHandleǁlog_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLflowHandleǁlog_metrics__mutmut_1': xǁMLflowHandleǁlog_metrics__mutmut_1, 
        'xǁMLflowHandleǁlog_metrics__mutmut_2': xǁMLflowHandleǁlog_metrics__mutmut_2, 
        'xǁMLflowHandleǁlog_metrics__mutmut_3': xǁMLflowHandleǁlog_metrics__mutmut_3, 
        'xǁMLflowHandleǁlog_metrics__mutmut_4': xǁMLflowHandleǁlog_metrics__mutmut_4
    }
    
    def log_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLflowHandleǁlog_metrics__mutmut_orig"), object.__getattribute__(self, "xǁMLflowHandleǁlog_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    log_metrics.__signature__ = _mutmut_signature(xǁMLflowHandleǁlog_metrics__mutmut_orig)
    xǁMLflowHandleǁlog_metrics__mutmut_orig.__name__ = 'xǁMLflowHandleǁlog_metrics'

    def xǁMLflowHandleǁlog_params__mutmut_orig(self, params: Mapping[str, Any]) -> None:
        self._module.log_params(params)

    def xǁMLflowHandleǁlog_params__mutmut_1(self, params: Mapping[str, Any]) -> None:
        self._module.log_params(None)
    
    xǁMLflowHandleǁlog_params__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMLflowHandleǁlog_params__mutmut_1': xǁMLflowHandleǁlog_params__mutmut_1
    }
    
    def log_params(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMLflowHandleǁlog_params__mutmut_orig"), object.__getattribute__(self, "xǁMLflowHandleǁlog_params__mutmut_mutants"), args, kwargs, self)
        return result 
    
    log_params.__signature__ = _mutmut_signature(xǁMLflowHandleǁlog_params__mutmut_orig)
    xǁMLflowHandleǁlog_params__mutmut_orig.__name__ = 'xǁMLflowHandleǁlog_params'

    def end(self) -> None:
        self._module.end_run()


def x__start_mlflow_run__mutmut_orig(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_1(config: LoggingConfig) -> bool:
    if config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_2(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return True
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_3(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is not None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_4(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            None,
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_5(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            None,
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_6(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_7(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_8(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "XX%sXX",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_9(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%S",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_10(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                None,
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_11(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose=None,
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_12(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_13(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_14(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "XXmlflowXX",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_15(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "MLFLOW",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_16(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="XXexperiment trackingXX",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_17(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="EXPERIMENT TRACKING",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_18(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return True
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_19(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(None)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_20(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = None
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_21(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(None)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_22(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(None):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_23(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=None, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_24(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=None)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_25(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_26(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, )
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_27(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=False, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_28(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=False)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_29(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(None)
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_30(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=None)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_31(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning(None, config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_32(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", None, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_33(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, None)
        return False
    return True


def x__start_mlflow_run__mutmut_34(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning(config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_35(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", exc)
        return False
    return True


def x__start_mlflow_run__mutmut_36(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, )
        return False
    return True


def x__start_mlflow_run__mutmut_37(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("XXFailed to start MLflow run '%s': %sXX", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_38(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("failed to start mlflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_39(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("FAILED TO START MLFLOW RUN '%S': %S", config.mlflow_run_name, exc)
        return False
    return True


def x__start_mlflow_run__mutmut_40(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return True
    return True


def x__start_mlflow_run__mutmut_41(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return False

x__start_mlflow_run__mutmut_mutants : ClassVar[MutantDict] = {
'x__start_mlflow_run__mutmut_1': x__start_mlflow_run__mutmut_1, 
    'x__start_mlflow_run__mutmut_2': x__start_mlflow_run__mutmut_2, 
    'x__start_mlflow_run__mutmut_3': x__start_mlflow_run__mutmut_3, 
    'x__start_mlflow_run__mutmut_4': x__start_mlflow_run__mutmut_4, 
    'x__start_mlflow_run__mutmut_5': x__start_mlflow_run__mutmut_5, 
    'x__start_mlflow_run__mutmut_6': x__start_mlflow_run__mutmut_6, 
    'x__start_mlflow_run__mutmut_7': x__start_mlflow_run__mutmut_7, 
    'x__start_mlflow_run__mutmut_8': x__start_mlflow_run__mutmut_8, 
    'x__start_mlflow_run__mutmut_9': x__start_mlflow_run__mutmut_9, 
    'x__start_mlflow_run__mutmut_10': x__start_mlflow_run__mutmut_10, 
    'x__start_mlflow_run__mutmut_11': x__start_mlflow_run__mutmut_11, 
    'x__start_mlflow_run__mutmut_12': x__start_mlflow_run__mutmut_12, 
    'x__start_mlflow_run__mutmut_13': x__start_mlflow_run__mutmut_13, 
    'x__start_mlflow_run__mutmut_14': x__start_mlflow_run__mutmut_14, 
    'x__start_mlflow_run__mutmut_15': x__start_mlflow_run__mutmut_15, 
    'x__start_mlflow_run__mutmut_16': x__start_mlflow_run__mutmut_16, 
    'x__start_mlflow_run__mutmut_17': x__start_mlflow_run__mutmut_17, 
    'x__start_mlflow_run__mutmut_18': x__start_mlflow_run__mutmut_18, 
    'x__start_mlflow_run__mutmut_19': x__start_mlflow_run__mutmut_19, 
    'x__start_mlflow_run__mutmut_20': x__start_mlflow_run__mutmut_20, 
    'x__start_mlflow_run__mutmut_21': x__start_mlflow_run__mutmut_21, 
    'x__start_mlflow_run__mutmut_22': x__start_mlflow_run__mutmut_22, 
    'x__start_mlflow_run__mutmut_23': x__start_mlflow_run__mutmut_23, 
    'x__start_mlflow_run__mutmut_24': x__start_mlflow_run__mutmut_24, 
    'x__start_mlflow_run__mutmut_25': x__start_mlflow_run__mutmut_25, 
    'x__start_mlflow_run__mutmut_26': x__start_mlflow_run__mutmut_26, 
    'x__start_mlflow_run__mutmut_27': x__start_mlflow_run__mutmut_27, 
    'x__start_mlflow_run__mutmut_28': x__start_mlflow_run__mutmut_28, 
    'x__start_mlflow_run__mutmut_29': x__start_mlflow_run__mutmut_29, 
    'x__start_mlflow_run__mutmut_30': x__start_mlflow_run__mutmut_30, 
    'x__start_mlflow_run__mutmut_31': x__start_mlflow_run__mutmut_31, 
    'x__start_mlflow_run__mutmut_32': x__start_mlflow_run__mutmut_32, 
    'x__start_mlflow_run__mutmut_33': x__start_mlflow_run__mutmut_33, 
    'x__start_mlflow_run__mutmut_34': x__start_mlflow_run__mutmut_34, 
    'x__start_mlflow_run__mutmut_35': x__start_mlflow_run__mutmut_35, 
    'x__start_mlflow_run__mutmut_36': x__start_mlflow_run__mutmut_36, 
    'x__start_mlflow_run__mutmut_37': x__start_mlflow_run__mutmut_37, 
    'x__start_mlflow_run__mutmut_38': x__start_mlflow_run__mutmut_38, 
    'x__start_mlflow_run__mutmut_39': x__start_mlflow_run__mutmut_39, 
    'x__start_mlflow_run__mutmut_40': x__start_mlflow_run__mutmut_40, 
    'x__start_mlflow_run__mutmut_41': x__start_mlflow_run__mutmut_41
}

def _start_mlflow_run(*args, **kwargs):
    result = _mutmut_trampoline(x__start_mlflow_run__mutmut_orig, x__start_mlflow_run__mutmut_mutants, args, kwargs)
    return result 

_start_mlflow_run.__signature__ = _mutmut_signature(x__start_mlflow_run__mutmut_orig)
x__start_mlflow_run__mutmut_orig.__name__ = 'x__start_mlflow_run'


def x__create_fallback_writer__mutmut_orig(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_1(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_2(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None or pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_3(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_4(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_5(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(None)
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_6(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(None))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_7(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            None,
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_8(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            None,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_9(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            None,
        )
        return None


def x__create_fallback_writer__mutmut_10(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_11(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_12(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            )
        return None


def x__create_fallback_writer__mutmut_13(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "XXUnable to initialise fallback metrics writer at '%s': %sXX",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_14(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def x__create_fallback_writer__mutmut_15(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except Exception as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "UNABLE TO INITIALISE FALLBACK METRICS WRITER AT '%S': %S",
            config.fallback_metrics_path,
            exc,
        )
        return None

x__create_fallback_writer__mutmut_mutants : ClassVar[MutantDict] = {
'x__create_fallback_writer__mutmut_1': x__create_fallback_writer__mutmut_1, 
    'x__create_fallback_writer__mutmut_2': x__create_fallback_writer__mutmut_2, 
    'x__create_fallback_writer__mutmut_3': x__create_fallback_writer__mutmut_3, 
    'x__create_fallback_writer__mutmut_4': x__create_fallback_writer__mutmut_4, 
    'x__create_fallback_writer__mutmut_5': x__create_fallback_writer__mutmut_5, 
    'x__create_fallback_writer__mutmut_6': x__create_fallback_writer__mutmut_6, 
    'x__create_fallback_writer__mutmut_7': x__create_fallback_writer__mutmut_7, 
    'x__create_fallback_writer__mutmut_8': x__create_fallback_writer__mutmut_8, 
    'x__create_fallback_writer__mutmut_9': x__create_fallback_writer__mutmut_9, 
    'x__create_fallback_writer__mutmut_10': x__create_fallback_writer__mutmut_10, 
    'x__create_fallback_writer__mutmut_11': x__create_fallback_writer__mutmut_11, 
    'x__create_fallback_writer__mutmut_12': x__create_fallback_writer__mutmut_12, 
    'x__create_fallback_writer__mutmut_13': x__create_fallback_writer__mutmut_13, 
    'x__create_fallback_writer__mutmut_14': x__create_fallback_writer__mutmut_14, 
    'x__create_fallback_writer__mutmut_15': x__create_fallback_writer__mutmut_15
}

def _create_fallback_writer(*args, **kwargs):
    result = _mutmut_trampoline(x__create_fallback_writer__mutmut_orig, x__create_fallback_writer__mutmut_mutants, args, kwargs)
    return result 

_create_fallback_writer.__signature__ = _mutmut_signature(x__create_fallback_writer__mutmut_orig)
x__create_fallback_writer__mutmut_orig.__name__ = 'x__create_fallback_writer'


def x_init_mlflow__mutmut_orig(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_1(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_2(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = None
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_3(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name and "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_4(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "XXcodex-runXX"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_5(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "CODEX-RUN"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_6(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = None
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_7(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module(None)
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_8(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("XXmlflowXX")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_9(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("MLFLOW")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_10(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                None,
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_11(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                None,
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_12(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_13(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_14(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "XX%sXX",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_15(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%S",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_16(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    None,
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_17(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose=None,
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_18(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_19(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_20(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "XXmlflowXX",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_21(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "MLFLOW",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_22(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="XXexperiment trackingXX",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_23(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="EXPERIMENT TRACKING",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_24(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(None)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_25(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(None)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_26(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=None)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_27(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(None)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_28(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = None
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_29(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is not None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_30(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            None,
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_31(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            None,
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_32(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_33(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_34(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "XX%sXX",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_35(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%S",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_36(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                None,
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_37(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose=None,
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_38(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_39(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_40(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "XXmlflowXX",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_41(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "MLFLOW",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_42(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="XXexperiment trackingXX",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_43(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="EXPERIMENT TRACKING",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_44(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(None)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_45(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(None)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_46(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = None
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_47(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=None, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_48(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_49(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_50(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, )
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_51(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(None) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_52(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning(None, experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_53(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", None, exc)
        return mlflow, None


def x_init_mlflow__mutmut_54(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, None)
        return mlflow, None


def x_init_mlflow__mutmut_55(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning(experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_56(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", exc)
        return mlflow, None


def x_init_mlflow__mutmut_57(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, )
        return mlflow, None


def x_init_mlflow__mutmut_58(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("XXFailed to initialise MLflow for '%s': %sXX", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_59(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("failed to initialise mlflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def x_init_mlflow__mutmut_60(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        if not enabled:
            return None
        resolved_run = run_name or "codex-run"
        try:
            module = import_module("mlflow")
        except ModuleNotFoundError:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "mlflow",
                    purpose="experiment tracking",
                ),
            )
            return None
        if tracking_uri:
            module.set_tracking_uri(tracking_uri)
        if experiment:
            module.set_experiment(experiment)
        module.start_run(run_name=resolved_run)
        return MLflowHandle(module)

    experiment_name = enabled
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("FAILED TO INITIALISE MLFLOW FOR '%S': %S", experiment_name, exc)
        return mlflow, None

x_init_mlflow__mutmut_mutants : ClassVar[MutantDict] = {
'x_init_mlflow__mutmut_1': x_init_mlflow__mutmut_1, 
    'x_init_mlflow__mutmut_2': x_init_mlflow__mutmut_2, 
    'x_init_mlflow__mutmut_3': x_init_mlflow__mutmut_3, 
    'x_init_mlflow__mutmut_4': x_init_mlflow__mutmut_4, 
    'x_init_mlflow__mutmut_5': x_init_mlflow__mutmut_5, 
    'x_init_mlflow__mutmut_6': x_init_mlflow__mutmut_6, 
    'x_init_mlflow__mutmut_7': x_init_mlflow__mutmut_7, 
    'x_init_mlflow__mutmut_8': x_init_mlflow__mutmut_8, 
    'x_init_mlflow__mutmut_9': x_init_mlflow__mutmut_9, 
    'x_init_mlflow__mutmut_10': x_init_mlflow__mutmut_10, 
    'x_init_mlflow__mutmut_11': x_init_mlflow__mutmut_11, 
    'x_init_mlflow__mutmut_12': x_init_mlflow__mutmut_12, 
    'x_init_mlflow__mutmut_13': x_init_mlflow__mutmut_13, 
    'x_init_mlflow__mutmut_14': x_init_mlflow__mutmut_14, 
    'x_init_mlflow__mutmut_15': x_init_mlflow__mutmut_15, 
    'x_init_mlflow__mutmut_16': x_init_mlflow__mutmut_16, 
    'x_init_mlflow__mutmut_17': x_init_mlflow__mutmut_17, 
    'x_init_mlflow__mutmut_18': x_init_mlflow__mutmut_18, 
    'x_init_mlflow__mutmut_19': x_init_mlflow__mutmut_19, 
    'x_init_mlflow__mutmut_20': x_init_mlflow__mutmut_20, 
    'x_init_mlflow__mutmut_21': x_init_mlflow__mutmut_21, 
    'x_init_mlflow__mutmut_22': x_init_mlflow__mutmut_22, 
    'x_init_mlflow__mutmut_23': x_init_mlflow__mutmut_23, 
    'x_init_mlflow__mutmut_24': x_init_mlflow__mutmut_24, 
    'x_init_mlflow__mutmut_25': x_init_mlflow__mutmut_25, 
    'x_init_mlflow__mutmut_26': x_init_mlflow__mutmut_26, 
    'x_init_mlflow__mutmut_27': x_init_mlflow__mutmut_27, 
    'x_init_mlflow__mutmut_28': x_init_mlflow__mutmut_28, 
    'x_init_mlflow__mutmut_29': x_init_mlflow__mutmut_29, 
    'x_init_mlflow__mutmut_30': x_init_mlflow__mutmut_30, 
    'x_init_mlflow__mutmut_31': x_init_mlflow__mutmut_31, 
    'x_init_mlflow__mutmut_32': x_init_mlflow__mutmut_32, 
    'x_init_mlflow__mutmut_33': x_init_mlflow__mutmut_33, 
    'x_init_mlflow__mutmut_34': x_init_mlflow__mutmut_34, 
    'x_init_mlflow__mutmut_35': x_init_mlflow__mutmut_35, 
    'x_init_mlflow__mutmut_36': x_init_mlflow__mutmut_36, 
    'x_init_mlflow__mutmut_37': x_init_mlflow__mutmut_37, 
    'x_init_mlflow__mutmut_38': x_init_mlflow__mutmut_38, 
    'x_init_mlflow__mutmut_39': x_init_mlflow__mutmut_39, 
    'x_init_mlflow__mutmut_40': x_init_mlflow__mutmut_40, 
    'x_init_mlflow__mutmut_41': x_init_mlflow__mutmut_41, 
    'x_init_mlflow__mutmut_42': x_init_mlflow__mutmut_42, 
    'x_init_mlflow__mutmut_43': x_init_mlflow__mutmut_43, 
    'x_init_mlflow__mutmut_44': x_init_mlflow__mutmut_44, 
    'x_init_mlflow__mutmut_45': x_init_mlflow__mutmut_45, 
    'x_init_mlflow__mutmut_46': x_init_mlflow__mutmut_46, 
    'x_init_mlflow__mutmut_47': x_init_mlflow__mutmut_47, 
    'x_init_mlflow__mutmut_48': x_init_mlflow__mutmut_48, 
    'x_init_mlflow__mutmut_49': x_init_mlflow__mutmut_49, 
    'x_init_mlflow__mutmut_50': x_init_mlflow__mutmut_50, 
    'x_init_mlflow__mutmut_51': x_init_mlflow__mutmut_51, 
    'x_init_mlflow__mutmut_52': x_init_mlflow__mutmut_52, 
    'x_init_mlflow__mutmut_53': x_init_mlflow__mutmut_53, 
    'x_init_mlflow__mutmut_54': x_init_mlflow__mutmut_54, 
    'x_init_mlflow__mutmut_55': x_init_mlflow__mutmut_55, 
    'x_init_mlflow__mutmut_56': x_init_mlflow__mutmut_56, 
    'x_init_mlflow__mutmut_57': x_init_mlflow__mutmut_57, 
    'x_init_mlflow__mutmut_58': x_init_mlflow__mutmut_58, 
    'x_init_mlflow__mutmut_59': x_init_mlflow__mutmut_59, 
    'x_init_mlflow__mutmut_60': x_init_mlflow__mutmut_60
}

def init_mlflow(*args, **kwargs):
    result = _mutmut_trampoline(x_init_mlflow__mutmut_orig, x_init_mlflow__mutmut_mutants, args, kwargs)
    return result 

init_mlflow.__signature__ = _mutmut_signature(x_init_mlflow__mutmut_orig)
x_init_mlflow__mutmut_orig.__name__ = 'x_init_mlflow'


def x_setup_logging__mutmut_orig(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_1(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is not None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_2(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = None
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_3(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = None
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_4(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(None, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_5(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, None):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_6(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr("to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_7(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, ):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_8(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "XXto_containerXX"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_9(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "TO_CONTAINER"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_10(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = None  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_11(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=None)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_12(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=False)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_13(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = None
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_14(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(None)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_15(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = None

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_16(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = None
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_17(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(None)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_18(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = None
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_19(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(None)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_20(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = None
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_21(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(None)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_22(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=None,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_23(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=None,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_24(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=None,
    )


def x_setup_logging__mutmut_25(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_26(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        fallback_writer=fallback_writer,
    )


def x_setup_logging__mutmut_27(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        )

x_setup_logging__mutmut_mutants : ClassVar[MutantDict] = {
'x_setup_logging__mutmut_1': x_setup_logging__mutmut_1, 
    'x_setup_logging__mutmut_2': x_setup_logging__mutmut_2, 
    'x_setup_logging__mutmut_3': x_setup_logging__mutmut_3, 
    'x_setup_logging__mutmut_4': x_setup_logging__mutmut_4, 
    'x_setup_logging__mutmut_5': x_setup_logging__mutmut_5, 
    'x_setup_logging__mutmut_6': x_setup_logging__mutmut_6, 
    'x_setup_logging__mutmut_7': x_setup_logging__mutmut_7, 
    'x_setup_logging__mutmut_8': x_setup_logging__mutmut_8, 
    'x_setup_logging__mutmut_9': x_setup_logging__mutmut_9, 
    'x_setup_logging__mutmut_10': x_setup_logging__mutmut_10, 
    'x_setup_logging__mutmut_11': x_setup_logging__mutmut_11, 
    'x_setup_logging__mutmut_12': x_setup_logging__mutmut_12, 
    'x_setup_logging__mutmut_13': x_setup_logging__mutmut_13, 
    'x_setup_logging__mutmut_14': x_setup_logging__mutmut_14, 
    'x_setup_logging__mutmut_15': x_setup_logging__mutmut_15, 
    'x_setup_logging__mutmut_16': x_setup_logging__mutmut_16, 
    'x_setup_logging__mutmut_17': x_setup_logging__mutmut_17, 
    'x_setup_logging__mutmut_18': x_setup_logging__mutmut_18, 
    'x_setup_logging__mutmut_19': x_setup_logging__mutmut_19, 
    'x_setup_logging__mutmut_20': x_setup_logging__mutmut_20, 
    'x_setup_logging__mutmut_21': x_setup_logging__mutmut_21, 
    'x_setup_logging__mutmut_22': x_setup_logging__mutmut_22, 
    'x_setup_logging__mutmut_23': x_setup_logging__mutmut_23, 
    'x_setup_logging__mutmut_24': x_setup_logging__mutmut_24, 
    'x_setup_logging__mutmut_25': x_setup_logging__mutmut_25, 
    'x_setup_logging__mutmut_26': x_setup_logging__mutmut_26, 
    'x_setup_logging__mutmut_27': x_setup_logging__mutmut_27
}

def setup_logging(*args, **kwargs):
    result = _mutmut_trampoline(x_setup_logging__mutmut_orig, x_setup_logging__mutmut_mutants, args, kwargs)
    return result 

setup_logging.__signature__ = _mutmut_signature(x_setup_logging__mutmut_orig)
x_setup_logging__mutmut_orig.__name__ = 'x_setup_logging'


def x_log_scalar_tb__mutmut_orig(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_1(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is not None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_2(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(None, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_3(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, None, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_4(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=None)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_5(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_6(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_7(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_8(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug(None, exc_info=True)


def x_log_scalar_tb__mutmut_9(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=None)


def x_log_scalar_tb__mutmut_10(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug(exc_info=True)


def x_log_scalar_tb__mutmut_11(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", )


def x_log_scalar_tb__mutmut_12(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("XXTensorBoard scalar logging failedXX", exc_info=True)


def x_log_scalar_tb__mutmut_13(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("tensorboard scalar logging failed", exc_info=True)


def x_log_scalar_tb__mutmut_14(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TENSORBOARD SCALAR LOGGING FAILED", exc_info=True)


def x_log_scalar_tb__mutmut_15(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=False)

x_log_scalar_tb__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_scalar_tb__mutmut_1': x_log_scalar_tb__mutmut_1, 
    'x_log_scalar_tb__mutmut_2': x_log_scalar_tb__mutmut_2, 
    'x_log_scalar_tb__mutmut_3': x_log_scalar_tb__mutmut_3, 
    'x_log_scalar_tb__mutmut_4': x_log_scalar_tb__mutmut_4, 
    'x_log_scalar_tb__mutmut_5': x_log_scalar_tb__mutmut_5, 
    'x_log_scalar_tb__mutmut_6': x_log_scalar_tb__mutmut_6, 
    'x_log_scalar_tb__mutmut_7': x_log_scalar_tb__mutmut_7, 
    'x_log_scalar_tb__mutmut_8': x_log_scalar_tb__mutmut_8, 
    'x_log_scalar_tb__mutmut_9': x_log_scalar_tb__mutmut_9, 
    'x_log_scalar_tb__mutmut_10': x_log_scalar_tb__mutmut_10, 
    'x_log_scalar_tb__mutmut_11': x_log_scalar_tb__mutmut_11, 
    'x_log_scalar_tb__mutmut_12': x_log_scalar_tb__mutmut_12, 
    'x_log_scalar_tb__mutmut_13': x_log_scalar_tb__mutmut_13, 
    'x_log_scalar_tb__mutmut_14': x_log_scalar_tb__mutmut_14, 
    'x_log_scalar_tb__mutmut_15': x_log_scalar_tb__mutmut_15
}

def log_scalar_tb(*args, **kwargs):
    result = _mutmut_trampoline(x_log_scalar_tb__mutmut_orig, x_log_scalar_tb__mutmut_mutants, args, kwargs)
    return result 

log_scalar_tb.__signature__ = _mutmut_signature(x_log_scalar_tb__mutmut_orig)
x_log_scalar_tb__mutmut_orig.__name__ = 'x_log_scalar_tb'


def x_log_params_mlflow__mutmut_orig(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def x_log_params_mlflow__mutmut_1(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None and not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def x_log_params_mlflow__mutmut_2(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is not None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def x_log_params_mlflow__mutmut_3(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def x_log_params_mlflow__mutmut_4(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            None
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def x_log_params_mlflow__mutmut_5(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(None)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def x_log_params_mlflow__mutmut_6(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug(None, exc_info=True)


def x_log_params_mlflow__mutmut_7(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=None)


def x_log_params_mlflow__mutmut_8(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug(exc_info=True)


def x_log_params_mlflow__mutmut_9(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", )


def x_log_params_mlflow__mutmut_10(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("XXMLflow parameter logging failedXX", exc_info=True)


def x_log_params_mlflow__mutmut_11(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("mlflow parameter logging failed", exc_info=True)


def x_log_params_mlflow__mutmut_12(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLFLOW PARAMETER LOGGING FAILED", exc_info=True)


def x_log_params_mlflow__mutmut_13(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=False)

x_log_params_mlflow__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_params_mlflow__mutmut_1': x_log_params_mlflow__mutmut_1, 
    'x_log_params_mlflow__mutmut_2': x_log_params_mlflow__mutmut_2, 
    'x_log_params_mlflow__mutmut_3': x_log_params_mlflow__mutmut_3, 
    'x_log_params_mlflow__mutmut_4': x_log_params_mlflow__mutmut_4, 
    'x_log_params_mlflow__mutmut_5': x_log_params_mlflow__mutmut_5, 
    'x_log_params_mlflow__mutmut_6': x_log_params_mlflow__mutmut_6, 
    'x_log_params_mlflow__mutmut_7': x_log_params_mlflow__mutmut_7, 
    'x_log_params_mlflow__mutmut_8': x_log_params_mlflow__mutmut_8, 
    'x_log_params_mlflow__mutmut_9': x_log_params_mlflow__mutmut_9, 
    'x_log_params_mlflow__mutmut_10': x_log_params_mlflow__mutmut_10, 
    'x_log_params_mlflow__mutmut_11': x_log_params_mlflow__mutmut_11, 
    'x_log_params_mlflow__mutmut_12': x_log_params_mlflow__mutmut_12, 
    'x_log_params_mlflow__mutmut_13': x_log_params_mlflow__mutmut_13
}

def log_params_mlflow(*args, **kwargs):
    result = _mutmut_trampoline(x_log_params_mlflow__mutmut_orig, x_log_params_mlflow__mutmut_mutants, args, kwargs)
    return result 

log_params_mlflow.__signature__ = _mutmut_signature(x_log_params_mlflow__mutmut_orig)
x_log_params_mlflow__mutmut_orig.__name__ = 'x_log_params_mlflow'


def x_log_metrics_mlflow__mutmut_orig(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_1(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None and not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_2(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is not None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_3(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_4(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics(None, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_5(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=None)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_6(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics(step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_7(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_8(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(None) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_9(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug(None, exc_info=True)


def x_log_metrics_mlflow__mutmut_10(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=None)


def x_log_metrics_mlflow__mutmut_11(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug(exc_info=True)


def x_log_metrics_mlflow__mutmut_12(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", )


def x_log_metrics_mlflow__mutmut_13(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("XXMLflow metric logging failedXX", exc_info=True)


def x_log_metrics_mlflow__mutmut_14(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("mlflow metric logging failed", exc_info=True)


def x_log_metrics_mlflow__mutmut_15(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLFLOW METRIC LOGGING FAILED", exc_info=True)


def x_log_metrics_mlflow__mutmut_16(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=False)

x_log_metrics_mlflow__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_metrics_mlflow__mutmut_1': x_log_metrics_mlflow__mutmut_1, 
    'x_log_metrics_mlflow__mutmut_2': x_log_metrics_mlflow__mutmut_2, 
    'x_log_metrics_mlflow__mutmut_3': x_log_metrics_mlflow__mutmut_3, 
    'x_log_metrics_mlflow__mutmut_4': x_log_metrics_mlflow__mutmut_4, 
    'x_log_metrics_mlflow__mutmut_5': x_log_metrics_mlflow__mutmut_5, 
    'x_log_metrics_mlflow__mutmut_6': x_log_metrics_mlflow__mutmut_6, 
    'x_log_metrics_mlflow__mutmut_7': x_log_metrics_mlflow__mutmut_7, 
    'x_log_metrics_mlflow__mutmut_8': x_log_metrics_mlflow__mutmut_8, 
    'x_log_metrics_mlflow__mutmut_9': x_log_metrics_mlflow__mutmut_9, 
    'x_log_metrics_mlflow__mutmut_10': x_log_metrics_mlflow__mutmut_10, 
    'x_log_metrics_mlflow__mutmut_11': x_log_metrics_mlflow__mutmut_11, 
    'x_log_metrics_mlflow__mutmut_12': x_log_metrics_mlflow__mutmut_12, 
    'x_log_metrics_mlflow__mutmut_13': x_log_metrics_mlflow__mutmut_13, 
    'x_log_metrics_mlflow__mutmut_14': x_log_metrics_mlflow__mutmut_14, 
    'x_log_metrics_mlflow__mutmut_15': x_log_metrics_mlflow__mutmut_15, 
    'x_log_metrics_mlflow__mutmut_16': x_log_metrics_mlflow__mutmut_16
}

def log_metrics_mlflow(*args, **kwargs):
    result = _mutmut_trampoline(x_log_metrics_mlflow__mutmut_orig, x_log_metrics_mlflow__mutmut_mutants, args, kwargs)
    return result 

log_metrics_mlflow.__signature__ = _mutmut_signature(x_log_metrics_mlflow__mutmut_orig)
x_log_metrics_mlflow__mutmut_orig.__name__ = 'x_log_metrics_mlflow'


def x_log_metrics__mutmut_orig(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_1(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_2(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_3(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(None, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_4(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, None, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_5(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, None)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_6(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_7(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_8(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, )
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_9(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug(None, key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_10(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", None, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_11(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, None, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_12(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, None)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_13(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug(key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_14(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_15(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_16(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, )
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_17(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("XXTensorBoard logging failed for %s=%s: %sXX", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_18(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("tensorboard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_19(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TENSORBOARD LOGGING FAILED FOR %S=%S: %S", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_20(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active or mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_21(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_22(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics(None, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_23(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=None)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_24(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics(step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_25(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, )
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_26(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(None) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_27(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug(None, step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_28(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", None, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_29(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, None)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_30(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug(step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_31(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_32(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, )
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_33(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("XXMLflow logging failed at step %s: %sXX", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_34(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("mlflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_35(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLFLOW LOGGING FAILED AT STEP %S: %S", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_36(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is None:
        session.fallback_writer.write(metrics, step)


def x_log_metrics__mutmut_37(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(None, step)


def x_log_metrics__mutmut_38(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, None)


def x_log_metrics__mutmut_39(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(step)


def x_log_metrics__mutmut_40(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, )

x_log_metrics__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_metrics__mutmut_1': x_log_metrics__mutmut_1, 
    'x_log_metrics__mutmut_2': x_log_metrics__mutmut_2, 
    'x_log_metrics__mutmut_3': x_log_metrics__mutmut_3, 
    'x_log_metrics__mutmut_4': x_log_metrics__mutmut_4, 
    'x_log_metrics__mutmut_5': x_log_metrics__mutmut_5, 
    'x_log_metrics__mutmut_6': x_log_metrics__mutmut_6, 
    'x_log_metrics__mutmut_7': x_log_metrics__mutmut_7, 
    'x_log_metrics__mutmut_8': x_log_metrics__mutmut_8, 
    'x_log_metrics__mutmut_9': x_log_metrics__mutmut_9, 
    'x_log_metrics__mutmut_10': x_log_metrics__mutmut_10, 
    'x_log_metrics__mutmut_11': x_log_metrics__mutmut_11, 
    'x_log_metrics__mutmut_12': x_log_metrics__mutmut_12, 
    'x_log_metrics__mutmut_13': x_log_metrics__mutmut_13, 
    'x_log_metrics__mutmut_14': x_log_metrics__mutmut_14, 
    'x_log_metrics__mutmut_15': x_log_metrics__mutmut_15, 
    'x_log_metrics__mutmut_16': x_log_metrics__mutmut_16, 
    'x_log_metrics__mutmut_17': x_log_metrics__mutmut_17, 
    'x_log_metrics__mutmut_18': x_log_metrics__mutmut_18, 
    'x_log_metrics__mutmut_19': x_log_metrics__mutmut_19, 
    'x_log_metrics__mutmut_20': x_log_metrics__mutmut_20, 
    'x_log_metrics__mutmut_21': x_log_metrics__mutmut_21, 
    'x_log_metrics__mutmut_22': x_log_metrics__mutmut_22, 
    'x_log_metrics__mutmut_23': x_log_metrics__mutmut_23, 
    'x_log_metrics__mutmut_24': x_log_metrics__mutmut_24, 
    'x_log_metrics__mutmut_25': x_log_metrics__mutmut_25, 
    'x_log_metrics__mutmut_26': x_log_metrics__mutmut_26, 
    'x_log_metrics__mutmut_27': x_log_metrics__mutmut_27, 
    'x_log_metrics__mutmut_28': x_log_metrics__mutmut_28, 
    'x_log_metrics__mutmut_29': x_log_metrics__mutmut_29, 
    'x_log_metrics__mutmut_30': x_log_metrics__mutmut_30, 
    'x_log_metrics__mutmut_31': x_log_metrics__mutmut_31, 
    'x_log_metrics__mutmut_32': x_log_metrics__mutmut_32, 
    'x_log_metrics__mutmut_33': x_log_metrics__mutmut_33, 
    'x_log_metrics__mutmut_34': x_log_metrics__mutmut_34, 
    'x_log_metrics__mutmut_35': x_log_metrics__mutmut_35, 
    'x_log_metrics__mutmut_36': x_log_metrics__mutmut_36, 
    'x_log_metrics__mutmut_37': x_log_metrics__mutmut_37, 
    'x_log_metrics__mutmut_38': x_log_metrics__mutmut_38, 
    'x_log_metrics__mutmut_39': x_log_metrics__mutmut_39, 
    'x_log_metrics__mutmut_40': x_log_metrics__mutmut_40
}

def log_metrics(*args, **kwargs):
    result = _mutmut_trampoline(x_log_metrics__mutmut_orig, x_log_metrics__mutmut_mutants, args, kwargs)
    return result 

log_metrics.__signature__ = _mutmut_signature(x_log_metrics__mutmut_orig)
x_log_metrics__mutmut_orig.__name__ = 'x_log_metrics'


def x_shutdown_logging__mutmut_orig(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_1(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_2(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug(None, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_3(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", None)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_4(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug(exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_5(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", )
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_6(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("XXTensorBoard writer shutdown encountered an error: %sXX", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_7(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("tensorboard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_8(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TENSORBOARD WRITER SHUTDOWN ENCOUNTERED AN ERROR: %S", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_9(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active or mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_10(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_11(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug(None, exc)


def x_shutdown_logging__mutmut_12(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", None)


def x_shutdown_logging__mutmut_13(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug(exc)


def x_shutdown_logging__mutmut_14(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", )


def x_shutdown_logging__mutmut_15(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("XXFailed to end MLflow run cleanly: %sXX", exc)


def x_shutdown_logging__mutmut_16(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("failed to end mlflow run cleanly: %s", exc)


def x_shutdown_logging__mutmut_17(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("FAILED TO END MLFLOW RUN CLEANLY: %S", exc)

x_shutdown_logging__mutmut_mutants : ClassVar[MutantDict] = {
'x_shutdown_logging__mutmut_1': x_shutdown_logging__mutmut_1, 
    'x_shutdown_logging__mutmut_2': x_shutdown_logging__mutmut_2, 
    'x_shutdown_logging__mutmut_3': x_shutdown_logging__mutmut_3, 
    'x_shutdown_logging__mutmut_4': x_shutdown_logging__mutmut_4, 
    'x_shutdown_logging__mutmut_5': x_shutdown_logging__mutmut_5, 
    'x_shutdown_logging__mutmut_6': x_shutdown_logging__mutmut_6, 
    'x_shutdown_logging__mutmut_7': x_shutdown_logging__mutmut_7, 
    'x_shutdown_logging__mutmut_8': x_shutdown_logging__mutmut_8, 
    'x_shutdown_logging__mutmut_9': x_shutdown_logging__mutmut_9, 
    'x_shutdown_logging__mutmut_10': x_shutdown_logging__mutmut_10, 
    'x_shutdown_logging__mutmut_11': x_shutdown_logging__mutmut_11, 
    'x_shutdown_logging__mutmut_12': x_shutdown_logging__mutmut_12, 
    'x_shutdown_logging__mutmut_13': x_shutdown_logging__mutmut_13, 
    'x_shutdown_logging__mutmut_14': x_shutdown_logging__mutmut_14, 
    'x_shutdown_logging__mutmut_15': x_shutdown_logging__mutmut_15, 
    'x_shutdown_logging__mutmut_16': x_shutdown_logging__mutmut_16, 
    'x_shutdown_logging__mutmut_17': x_shutdown_logging__mutmut_17
}

def shutdown_logging(*args, **kwargs):
    result = _mutmut_trampoline(x_shutdown_logging__mutmut_orig, x_shutdown_logging__mutmut_mutants, args, kwargs)
    return result 

shutdown_logging.__signature__ = _mutmut_signature(x_shutdown_logging__mutmut_orig)
x_shutdown_logging__mutmut_orig.__name__ = 'x_shutdown_logging'


@contextmanager
def mlflow_run(
    run_name: str = "run",
    *,
    offline: bool = True,
    tracking_dir: str | Path = "./mlruns",
) -> Iterator[None]:
    """Context manager that starts an MLflow run if MLflow is available."""

    if mlflow is None:
        yield
        return

    tracking_path = Path(tracking_dir)
    if offline:
        os.environ.setdefault("MLFLOW_TRACKING_URI", f"file:{tracking_path.resolve()}")
        with suppress(Exception):  # pragma: no cover - directory creation best-effort
            tracking_path.mkdir(parents=True, exist_ok=True)

    mlflow.start_run(run_name=run_name)
    try:
        yield
    finally:
        try:
            mlflow.end_run()
        except Exception:  # pragma: no cover - best-effort shutdown
            LOGGER.debug("Failed to end MLflow run via context manager", exc_info=True)


def x_system_metrics__mutmut_orig() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_1() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = None

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_2() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"XXtsXX": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_3() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"TS": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_4() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_5() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = None
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_6() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = None
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_7() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                None
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_8() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "XXcpu_percentXX": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_9() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "CPU_PERCENT": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_10() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(None),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_11() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "XXram_used_bytesXX": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_12() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "RAM_USED_BYTES": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_13() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(None),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_14() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "XXram_total_bytesXX": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_15() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "RAM_TOTAL_BYTES": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_16() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(None),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_17() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug(None, exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_18() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=None)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_19() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug(exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_20() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", )

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_21() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("XXpsutil metrics collection failedXX", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_22() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("PSUTIL METRICS COLLECTION FAILED", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_23() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=False)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_24() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_25() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = None
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_26() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = None
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_27() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(None):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_28() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = None
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_29() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(None)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_30() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = None
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_31() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(None)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_32() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    None
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_33() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "XXindexXX": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_34() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "INDEX": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_35() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "XXmem_used_bytesXX": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_36() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "MEM_USED_BYTES": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_37() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(None),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_38() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "XXmem_total_bytesXX": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_39() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "MEM_TOTAL_BYTES": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_40() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(None),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_41() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = None
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_42() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["XXgpusXX"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_43() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["GPUS"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_44() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug(None, exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_45() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=None)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_46() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug(exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_47() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", )
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_48() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("XXNVML metrics collection failedXX", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_49() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("nvml metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_50() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML METRICS COLLECTION FAILED", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_51() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=False)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_52() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug(None, exc_info=True)

    return snapshot


def x_system_metrics__mutmut_53() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=None)

    return snapshot


def x_system_metrics__mutmut_54() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug(exc_info=True)

    return snapshot


def x_system_metrics__mutmut_55() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", )

    return snapshot


def x_system_metrics__mutmut_56() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("XXNVML shutdown failedXX", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_57() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("nvml shutdown failed", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_58() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML SHUTDOWN FAILED", exc_info=True)

    return snapshot


def x_system_metrics__mutmut_59() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=False)

    return snapshot

x_system_metrics__mutmut_mutants : ClassVar[MutantDict] = {
'x_system_metrics__mutmut_1': x_system_metrics__mutmut_1, 
    'x_system_metrics__mutmut_2': x_system_metrics__mutmut_2, 
    'x_system_metrics__mutmut_3': x_system_metrics__mutmut_3, 
    'x_system_metrics__mutmut_4': x_system_metrics__mutmut_4, 
    'x_system_metrics__mutmut_5': x_system_metrics__mutmut_5, 
    'x_system_metrics__mutmut_6': x_system_metrics__mutmut_6, 
    'x_system_metrics__mutmut_7': x_system_metrics__mutmut_7, 
    'x_system_metrics__mutmut_8': x_system_metrics__mutmut_8, 
    'x_system_metrics__mutmut_9': x_system_metrics__mutmut_9, 
    'x_system_metrics__mutmut_10': x_system_metrics__mutmut_10, 
    'x_system_metrics__mutmut_11': x_system_metrics__mutmut_11, 
    'x_system_metrics__mutmut_12': x_system_metrics__mutmut_12, 
    'x_system_metrics__mutmut_13': x_system_metrics__mutmut_13, 
    'x_system_metrics__mutmut_14': x_system_metrics__mutmut_14, 
    'x_system_metrics__mutmut_15': x_system_metrics__mutmut_15, 
    'x_system_metrics__mutmut_16': x_system_metrics__mutmut_16, 
    'x_system_metrics__mutmut_17': x_system_metrics__mutmut_17, 
    'x_system_metrics__mutmut_18': x_system_metrics__mutmut_18, 
    'x_system_metrics__mutmut_19': x_system_metrics__mutmut_19, 
    'x_system_metrics__mutmut_20': x_system_metrics__mutmut_20, 
    'x_system_metrics__mutmut_21': x_system_metrics__mutmut_21, 
    'x_system_metrics__mutmut_22': x_system_metrics__mutmut_22, 
    'x_system_metrics__mutmut_23': x_system_metrics__mutmut_23, 
    'x_system_metrics__mutmut_24': x_system_metrics__mutmut_24, 
    'x_system_metrics__mutmut_25': x_system_metrics__mutmut_25, 
    'x_system_metrics__mutmut_26': x_system_metrics__mutmut_26, 
    'x_system_metrics__mutmut_27': x_system_metrics__mutmut_27, 
    'x_system_metrics__mutmut_28': x_system_metrics__mutmut_28, 
    'x_system_metrics__mutmut_29': x_system_metrics__mutmut_29, 
    'x_system_metrics__mutmut_30': x_system_metrics__mutmut_30, 
    'x_system_metrics__mutmut_31': x_system_metrics__mutmut_31, 
    'x_system_metrics__mutmut_32': x_system_metrics__mutmut_32, 
    'x_system_metrics__mutmut_33': x_system_metrics__mutmut_33, 
    'x_system_metrics__mutmut_34': x_system_metrics__mutmut_34, 
    'x_system_metrics__mutmut_35': x_system_metrics__mutmut_35, 
    'x_system_metrics__mutmut_36': x_system_metrics__mutmut_36, 
    'x_system_metrics__mutmut_37': x_system_metrics__mutmut_37, 
    'x_system_metrics__mutmut_38': x_system_metrics__mutmut_38, 
    'x_system_metrics__mutmut_39': x_system_metrics__mutmut_39, 
    'x_system_metrics__mutmut_40': x_system_metrics__mutmut_40, 
    'x_system_metrics__mutmut_41': x_system_metrics__mutmut_41, 
    'x_system_metrics__mutmut_42': x_system_metrics__mutmut_42, 
    'x_system_metrics__mutmut_43': x_system_metrics__mutmut_43, 
    'x_system_metrics__mutmut_44': x_system_metrics__mutmut_44, 
    'x_system_metrics__mutmut_45': x_system_metrics__mutmut_45, 
    'x_system_metrics__mutmut_46': x_system_metrics__mutmut_46, 
    'x_system_metrics__mutmut_47': x_system_metrics__mutmut_47, 
    'x_system_metrics__mutmut_48': x_system_metrics__mutmut_48, 
    'x_system_metrics__mutmut_49': x_system_metrics__mutmut_49, 
    'x_system_metrics__mutmut_50': x_system_metrics__mutmut_50, 
    'x_system_metrics__mutmut_51': x_system_metrics__mutmut_51, 
    'x_system_metrics__mutmut_52': x_system_metrics__mutmut_52, 
    'x_system_metrics__mutmut_53': x_system_metrics__mutmut_53, 
    'x_system_metrics__mutmut_54': x_system_metrics__mutmut_54, 
    'x_system_metrics__mutmut_55': x_system_metrics__mutmut_55, 
    'x_system_metrics__mutmut_56': x_system_metrics__mutmut_56, 
    'x_system_metrics__mutmut_57': x_system_metrics__mutmut_57, 
    'x_system_metrics__mutmut_58': x_system_metrics__mutmut_58, 
    'x_system_metrics__mutmut_59': x_system_metrics__mutmut_59
}

def system_metrics(*args, **kwargs):
    result = _mutmut_trampoline(x_system_metrics__mutmut_orig, x_system_metrics__mutmut_mutants, args, kwargs)
    return result 

system_metrics.__signature__ = _mutmut_signature(x_system_metrics__mutmut_orig)
x_system_metrics__mutmut_orig.__name__ = 'x_system_metrics'


__all__ = [
    "FallbackMetricsWriter",
    "LogHandles",
    "LoggingConfig",
    "LoggingSession",
    "init_mlflow",
    "init_tensorboard",
    "log_metrics",
    "log_metrics_mlflow",
    "log_params_mlflow",
    "log_scalar_tb",
    "mlflow_run",
    "setup_logging",
    "shutdown_logging",
    "system_metrics",
]
