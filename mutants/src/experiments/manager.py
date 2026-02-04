"""
Manager Module

This module provides functionality for manager.

Usage:
    from experiments.manager import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import os
from pathlib import Path

from codex_ml.utils.optional import optional_dependency_error
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


def x_init_experiment__mutmut_orig(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_1(exp_name: str = "XXcodex_experimentXX") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_2(exp_name: str = "CODEX_EXPERIMENT") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_3(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = None
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_4(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get(None, "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_5(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", None)
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_6(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_7(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", )
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_8(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("XXEXPERIMENT_BACKENDXX", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_9(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("experiment_backend", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_10(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "XXfileXX")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_11(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "FILE")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_12(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            None,
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_13(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose=None,
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_14(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_15(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_16(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "XXmlflowXX",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_17(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "MLFLOW",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_18(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="XXexperiment initializationXX",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_19(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="EXPERIMENT INITIALIZATION",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_20(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend != "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_21(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "XXfileXX":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_22(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "FILE":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_23(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = None
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_24(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(None).resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_25(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path("XX.mlrunsXX").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_26(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".MLRUNS").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_27(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=None, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_28(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=None)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_29(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_30(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, )
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_31(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=False, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_32(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=False)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_33(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(None)
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_34(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = None
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_35(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get(None)
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_36(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("XXMLFLOW_TRACKING_URIXX")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_37(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("mlflow_tracking_uri")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_38(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_39(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError(None)
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_40(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("XXMLFLOW_TRACKING_URI must be set for non-file backendsXX")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_41(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("mlflow_tracking_uri must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_42(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI MUST BE SET FOR NON-FILE BACKENDS")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_43(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(None)
    mlflow.set_experiment(exp_name)


def x_init_experiment__mutmut_44(exp_name: str = "codex_experiment") -> None:
    """Initialise MLflow in offline (local file store) mode by default."""

    backend = os.environ.get("EXPERIMENT_BACKEND", "file")
    try:
        import mlflow
    except Exception as exc:  # noqa: BLE001
        raise optional_dependency_error(
            "mlflow",
            purpose="experiment initialization",
        ) from exc

    if backend == "file":
        tracking_dir = Path(".mlruns").resolve()
        tracking_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{tracking_dir}")
    else:
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            raise RuntimeError("MLFLOW_TRACKING_URI must be set for non-file backends")
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(None)

x_init_experiment__mutmut_mutants : ClassVar[MutantDict] = {
'x_init_experiment__mutmut_1': x_init_experiment__mutmut_1, 
    'x_init_experiment__mutmut_2': x_init_experiment__mutmut_2, 
    'x_init_experiment__mutmut_3': x_init_experiment__mutmut_3, 
    'x_init_experiment__mutmut_4': x_init_experiment__mutmut_4, 
    'x_init_experiment__mutmut_5': x_init_experiment__mutmut_5, 
    'x_init_experiment__mutmut_6': x_init_experiment__mutmut_6, 
    'x_init_experiment__mutmut_7': x_init_experiment__mutmut_7, 
    'x_init_experiment__mutmut_8': x_init_experiment__mutmut_8, 
    'x_init_experiment__mutmut_9': x_init_experiment__mutmut_9, 
    'x_init_experiment__mutmut_10': x_init_experiment__mutmut_10, 
    'x_init_experiment__mutmut_11': x_init_experiment__mutmut_11, 
    'x_init_experiment__mutmut_12': x_init_experiment__mutmut_12, 
    'x_init_experiment__mutmut_13': x_init_experiment__mutmut_13, 
    'x_init_experiment__mutmut_14': x_init_experiment__mutmut_14, 
    'x_init_experiment__mutmut_15': x_init_experiment__mutmut_15, 
    'x_init_experiment__mutmut_16': x_init_experiment__mutmut_16, 
    'x_init_experiment__mutmut_17': x_init_experiment__mutmut_17, 
    'x_init_experiment__mutmut_18': x_init_experiment__mutmut_18, 
    'x_init_experiment__mutmut_19': x_init_experiment__mutmut_19, 
    'x_init_experiment__mutmut_20': x_init_experiment__mutmut_20, 
    'x_init_experiment__mutmut_21': x_init_experiment__mutmut_21, 
    'x_init_experiment__mutmut_22': x_init_experiment__mutmut_22, 
    'x_init_experiment__mutmut_23': x_init_experiment__mutmut_23, 
    'x_init_experiment__mutmut_24': x_init_experiment__mutmut_24, 
    'x_init_experiment__mutmut_25': x_init_experiment__mutmut_25, 
    'x_init_experiment__mutmut_26': x_init_experiment__mutmut_26, 
    'x_init_experiment__mutmut_27': x_init_experiment__mutmut_27, 
    'x_init_experiment__mutmut_28': x_init_experiment__mutmut_28, 
    'x_init_experiment__mutmut_29': x_init_experiment__mutmut_29, 
    'x_init_experiment__mutmut_30': x_init_experiment__mutmut_30, 
    'x_init_experiment__mutmut_31': x_init_experiment__mutmut_31, 
    'x_init_experiment__mutmut_32': x_init_experiment__mutmut_32, 
    'x_init_experiment__mutmut_33': x_init_experiment__mutmut_33, 
    'x_init_experiment__mutmut_34': x_init_experiment__mutmut_34, 
    'x_init_experiment__mutmut_35': x_init_experiment__mutmut_35, 
    'x_init_experiment__mutmut_36': x_init_experiment__mutmut_36, 
    'x_init_experiment__mutmut_37': x_init_experiment__mutmut_37, 
    'x_init_experiment__mutmut_38': x_init_experiment__mutmut_38, 
    'x_init_experiment__mutmut_39': x_init_experiment__mutmut_39, 
    'x_init_experiment__mutmut_40': x_init_experiment__mutmut_40, 
    'x_init_experiment__mutmut_41': x_init_experiment__mutmut_41, 
    'x_init_experiment__mutmut_42': x_init_experiment__mutmut_42, 
    'x_init_experiment__mutmut_43': x_init_experiment__mutmut_43, 
    'x_init_experiment__mutmut_44': x_init_experiment__mutmut_44
}

def init_experiment(*args, **kwargs):
    result = _mutmut_trampoline(x_init_experiment__mutmut_orig, x_init_experiment__mutmut_mutants, args, kwargs)
    return result 

init_experiment.__signature__ = _mutmut_signature(x_init_experiment__mutmut_orig)
x_init_experiment__mutmut_orig.__name__ = 'x_init_experiment'
