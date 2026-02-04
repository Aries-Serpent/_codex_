"""
App Module

This module provides functionality for app.

Usage:
    from codex_cli.app import ...

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
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Optional

REASONING_TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "configs" / "training" / "reasoning"
REASONING_CURRICULA_ROOT = REASONING_TEMPLATE_ROOT / "curricula"

_USE_TYPER = False
try:  # pragma: no cover - prefer Typer when available
    import typer as _typer  # type: ignore

    if hasattr(_typer, "Typer"):
        _USE_TYPER = True
except Exception:  # pragma: no cover - Typer shadowed/unavailable
    _USE_TYPER = False

if _USE_TYPER:
    echo = _typer.echo
    Exit = _typer.Exit
else:  # pragma: no cover - click fallback
    import click as _click

    echo = _click.echo

    class Exit(SystemExit):
        def __init__(self, code: int = 0) -> None:
            super().__init__(code)
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


def x__track_smoke_impl__mutmut_orig(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_1(dir_path: Optional[Path]) -> None:
    target = None
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_2(dir_path: Optional[Path]) -> None:
    target = (dir_path and Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_3(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path(None)).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_4(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("XX./mlrunsXX")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_5(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./MLRUNS")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_6(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = None
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_7(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = None
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_8(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["XXMLFLOW_TRACKING_URIXX"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_9(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["mlflow_tracking_uri"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_10(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(None)
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_11(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=None)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_12(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=2)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_13(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=None, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_14(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=None)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_15(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_16(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, )
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_17(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=False, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_18(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=False)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_19(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name=None):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_20(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="XXsmokeXX"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_21(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="SMOKE"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_22(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param(None, 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_23(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", None)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_24(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param(1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_25(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", )
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_26(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("XXpXX", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_27(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("P", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_28(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 2)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_29(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric(None, 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_30(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", None)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_31(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric(0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_32(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", )
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_33(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("XXmXX", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_34(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("M", 0.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_35(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 1.123)
    echo(f"OK: tracking to {uri}")


def x__track_smoke_impl__mutmut_36(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(None)

x__track_smoke_impl__mutmut_mutants : ClassVar[MutantDict] = {
'x__track_smoke_impl__mutmut_1': x__track_smoke_impl__mutmut_1, 
    'x__track_smoke_impl__mutmut_2': x__track_smoke_impl__mutmut_2, 
    'x__track_smoke_impl__mutmut_3': x__track_smoke_impl__mutmut_3, 
    'x__track_smoke_impl__mutmut_4': x__track_smoke_impl__mutmut_4, 
    'x__track_smoke_impl__mutmut_5': x__track_smoke_impl__mutmut_5, 
    'x__track_smoke_impl__mutmut_6': x__track_smoke_impl__mutmut_6, 
    'x__track_smoke_impl__mutmut_7': x__track_smoke_impl__mutmut_7, 
    'x__track_smoke_impl__mutmut_8': x__track_smoke_impl__mutmut_8, 
    'x__track_smoke_impl__mutmut_9': x__track_smoke_impl__mutmut_9, 
    'x__track_smoke_impl__mutmut_10': x__track_smoke_impl__mutmut_10, 
    'x__track_smoke_impl__mutmut_11': x__track_smoke_impl__mutmut_11, 
    'x__track_smoke_impl__mutmut_12': x__track_smoke_impl__mutmut_12, 
    'x__track_smoke_impl__mutmut_13': x__track_smoke_impl__mutmut_13, 
    'x__track_smoke_impl__mutmut_14': x__track_smoke_impl__mutmut_14, 
    'x__track_smoke_impl__mutmut_15': x__track_smoke_impl__mutmut_15, 
    'x__track_smoke_impl__mutmut_16': x__track_smoke_impl__mutmut_16, 
    'x__track_smoke_impl__mutmut_17': x__track_smoke_impl__mutmut_17, 
    'x__track_smoke_impl__mutmut_18': x__track_smoke_impl__mutmut_18, 
    'x__track_smoke_impl__mutmut_19': x__track_smoke_impl__mutmut_19, 
    'x__track_smoke_impl__mutmut_20': x__track_smoke_impl__mutmut_20, 
    'x__track_smoke_impl__mutmut_21': x__track_smoke_impl__mutmut_21, 
    'x__track_smoke_impl__mutmut_22': x__track_smoke_impl__mutmut_22, 
    'x__track_smoke_impl__mutmut_23': x__track_smoke_impl__mutmut_23, 
    'x__track_smoke_impl__mutmut_24': x__track_smoke_impl__mutmut_24, 
    'x__track_smoke_impl__mutmut_25': x__track_smoke_impl__mutmut_25, 
    'x__track_smoke_impl__mutmut_26': x__track_smoke_impl__mutmut_26, 
    'x__track_smoke_impl__mutmut_27': x__track_smoke_impl__mutmut_27, 
    'x__track_smoke_impl__mutmut_28': x__track_smoke_impl__mutmut_28, 
    'x__track_smoke_impl__mutmut_29': x__track_smoke_impl__mutmut_29, 
    'x__track_smoke_impl__mutmut_30': x__track_smoke_impl__mutmut_30, 
    'x__track_smoke_impl__mutmut_31': x__track_smoke_impl__mutmut_31, 
    'x__track_smoke_impl__mutmut_32': x__track_smoke_impl__mutmut_32, 
    'x__track_smoke_impl__mutmut_33': x__track_smoke_impl__mutmut_33, 
    'x__track_smoke_impl__mutmut_34': x__track_smoke_impl__mutmut_34, 
    'x__track_smoke_impl__mutmut_35': x__track_smoke_impl__mutmut_35, 
    'x__track_smoke_impl__mutmut_36': x__track_smoke_impl__mutmut_36
}

def _track_smoke_impl(*args, **kwargs):
    result = _mutmut_trampoline(x__track_smoke_impl__mutmut_orig, x__track_smoke_impl__mutmut_mutants, args, kwargs)
    return result 

_track_smoke_impl.__signature__ = _mutmut_signature(x__track_smoke_impl__mutmut_orig)
x__track_smoke_impl__mutmut_orig.__name__ = 'x__track_smoke_impl'


def x__split_smoke_impl__mutmut_orig(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_1(seed: int) -> None:
    total = None
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_2(seed: int) -> None:
    total = 21
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_3(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = None
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_4(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(None, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_5(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, None, None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_6(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr("Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_7(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_8(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", )
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_9(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "XXGeneratorXX", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_10(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_11(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "GENERATOR", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_12(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is not None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_13(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = None
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_14(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(None, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_15(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=None)
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_16(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_17(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, )
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_18(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(None))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_19(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(None)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_20(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning(None, exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_21(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=None)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_22(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning(exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_23(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", )
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_24(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("XXException occurredXX", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_25(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_26(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_27(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=False)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_28(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(None, exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_29(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=None)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_30(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_31(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", )
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_32(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("XXException occurredXX", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_33(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_34(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_35(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=False)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_36(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(None)
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_37(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=None)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_38(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=2)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_39(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = None  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_40(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(None)  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_41(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(None))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_42(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = None
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_43(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(None)
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_44(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(None))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_45(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(None)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_46(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = None
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_47(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total / 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_48(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 3
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_49(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = None
    echo(f"A={mid} B={total - mid} (seed={seed})")


def x__split_smoke_impl__mutmut_50(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(None)


def x__split_smoke_impl__mutmut_51(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total + mid} (seed={seed})")

x__split_smoke_impl__mutmut_mutants : ClassVar[MutantDict] = {
'x__split_smoke_impl__mutmut_1': x__split_smoke_impl__mutmut_1, 
    'x__split_smoke_impl__mutmut_2': x__split_smoke_impl__mutmut_2, 
    'x__split_smoke_impl__mutmut_3': x__split_smoke_impl__mutmut_3, 
    'x__split_smoke_impl__mutmut_4': x__split_smoke_impl__mutmut_4, 
    'x__split_smoke_impl__mutmut_5': x__split_smoke_impl__mutmut_5, 
    'x__split_smoke_impl__mutmut_6': x__split_smoke_impl__mutmut_6, 
    'x__split_smoke_impl__mutmut_7': x__split_smoke_impl__mutmut_7, 
    'x__split_smoke_impl__mutmut_8': x__split_smoke_impl__mutmut_8, 
    'x__split_smoke_impl__mutmut_9': x__split_smoke_impl__mutmut_9, 
    'x__split_smoke_impl__mutmut_10': x__split_smoke_impl__mutmut_10, 
    'x__split_smoke_impl__mutmut_11': x__split_smoke_impl__mutmut_11, 
    'x__split_smoke_impl__mutmut_12': x__split_smoke_impl__mutmut_12, 
    'x__split_smoke_impl__mutmut_13': x__split_smoke_impl__mutmut_13, 
    'x__split_smoke_impl__mutmut_14': x__split_smoke_impl__mutmut_14, 
    'x__split_smoke_impl__mutmut_15': x__split_smoke_impl__mutmut_15, 
    'x__split_smoke_impl__mutmut_16': x__split_smoke_impl__mutmut_16, 
    'x__split_smoke_impl__mutmut_17': x__split_smoke_impl__mutmut_17, 
    'x__split_smoke_impl__mutmut_18': x__split_smoke_impl__mutmut_18, 
    'x__split_smoke_impl__mutmut_19': x__split_smoke_impl__mutmut_19, 
    'x__split_smoke_impl__mutmut_20': x__split_smoke_impl__mutmut_20, 
    'x__split_smoke_impl__mutmut_21': x__split_smoke_impl__mutmut_21, 
    'x__split_smoke_impl__mutmut_22': x__split_smoke_impl__mutmut_22, 
    'x__split_smoke_impl__mutmut_23': x__split_smoke_impl__mutmut_23, 
    'x__split_smoke_impl__mutmut_24': x__split_smoke_impl__mutmut_24, 
    'x__split_smoke_impl__mutmut_25': x__split_smoke_impl__mutmut_25, 
    'x__split_smoke_impl__mutmut_26': x__split_smoke_impl__mutmut_26, 
    'x__split_smoke_impl__mutmut_27': x__split_smoke_impl__mutmut_27, 
    'x__split_smoke_impl__mutmut_28': x__split_smoke_impl__mutmut_28, 
    'x__split_smoke_impl__mutmut_29': x__split_smoke_impl__mutmut_29, 
    'x__split_smoke_impl__mutmut_30': x__split_smoke_impl__mutmut_30, 
    'x__split_smoke_impl__mutmut_31': x__split_smoke_impl__mutmut_31, 
    'x__split_smoke_impl__mutmut_32': x__split_smoke_impl__mutmut_32, 
    'x__split_smoke_impl__mutmut_33': x__split_smoke_impl__mutmut_33, 
    'x__split_smoke_impl__mutmut_34': x__split_smoke_impl__mutmut_34, 
    'x__split_smoke_impl__mutmut_35': x__split_smoke_impl__mutmut_35, 
    'x__split_smoke_impl__mutmut_36': x__split_smoke_impl__mutmut_36, 
    'x__split_smoke_impl__mutmut_37': x__split_smoke_impl__mutmut_37, 
    'x__split_smoke_impl__mutmut_38': x__split_smoke_impl__mutmut_38, 
    'x__split_smoke_impl__mutmut_39': x__split_smoke_impl__mutmut_39, 
    'x__split_smoke_impl__mutmut_40': x__split_smoke_impl__mutmut_40, 
    'x__split_smoke_impl__mutmut_41': x__split_smoke_impl__mutmut_41, 
    'x__split_smoke_impl__mutmut_42': x__split_smoke_impl__mutmut_42, 
    'x__split_smoke_impl__mutmut_43': x__split_smoke_impl__mutmut_43, 
    'x__split_smoke_impl__mutmut_44': x__split_smoke_impl__mutmut_44, 
    'x__split_smoke_impl__mutmut_45': x__split_smoke_impl__mutmut_45, 
    'x__split_smoke_impl__mutmut_46': x__split_smoke_impl__mutmut_46, 
    'x__split_smoke_impl__mutmut_47': x__split_smoke_impl__mutmut_47, 
    'x__split_smoke_impl__mutmut_48': x__split_smoke_impl__mutmut_48, 
    'x__split_smoke_impl__mutmut_49': x__split_smoke_impl__mutmut_49, 
    'x__split_smoke_impl__mutmut_50': x__split_smoke_impl__mutmut_50, 
    'x__split_smoke_impl__mutmut_51': x__split_smoke_impl__mutmut_51
}

def _split_smoke_impl(*args, **kwargs):
    result = _mutmut_trampoline(x__split_smoke_impl__mutmut_orig, x__split_smoke_impl__mutmut_mutants, args, kwargs)
    return result 

_split_smoke_impl.__signature__ = _mutmut_signature(x__split_smoke_impl__mutmut_orig)
x__split_smoke_impl__mutmut_orig.__name__ = 'x__split_smoke_impl'


def x__checkpoint_smoke_impl__mutmut_orig(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_1(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_2(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(None, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_3(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, None):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_4(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr("nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_5(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, ):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_6(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "XXnnXX"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_7(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "NN"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_8(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError(None)
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_9(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("XXtorch.nn unavailableXX")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_10(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("TORCH.NN UNAVAILABLE")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_11(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=None, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_12(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=None)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_13(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_14(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, )
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_15(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=False, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_16(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=False)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_17(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = None
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_18(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir * "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_19(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "XXepoch1-metric0.500000.ptXX"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_20(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "EPOCH1-METRIC0.500000.PT"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_21(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(None)
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_22(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"XXstubXX")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_23(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"STUB")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_24(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(None)
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_25(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = None
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_26(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(None)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_27(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(None, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_28(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, None))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_29(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_30(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, ))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_31(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(9, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_32(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 4))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_33(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = None
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_34(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(None, lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_35(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=None)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_36(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_37(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), )
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_38(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=1.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_39(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=None, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_40(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=None)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_41(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_42(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, )
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_43(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=False, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_44(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=False)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_45(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = None
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_46(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        None, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_47(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, None, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_48(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=None, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_49(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=None, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_50(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=None, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_51(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=None
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_52(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_53(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_54(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_55(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_56(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_57(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_58(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=2, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_59(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=1.5, out_dir=out_dir, keep_best_k=2
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_60(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=3
    )
    echo(f"Saved {path}")


def x__checkpoint_smoke_impl__mutmut_61(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(
        model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2
    )
    echo(None)

x__checkpoint_smoke_impl__mutmut_mutants : ClassVar[MutantDict] = {
'x__checkpoint_smoke_impl__mutmut_1': x__checkpoint_smoke_impl__mutmut_1, 
    'x__checkpoint_smoke_impl__mutmut_2': x__checkpoint_smoke_impl__mutmut_2, 
    'x__checkpoint_smoke_impl__mutmut_3': x__checkpoint_smoke_impl__mutmut_3, 
    'x__checkpoint_smoke_impl__mutmut_4': x__checkpoint_smoke_impl__mutmut_4, 
    'x__checkpoint_smoke_impl__mutmut_5': x__checkpoint_smoke_impl__mutmut_5, 
    'x__checkpoint_smoke_impl__mutmut_6': x__checkpoint_smoke_impl__mutmut_6, 
    'x__checkpoint_smoke_impl__mutmut_7': x__checkpoint_smoke_impl__mutmut_7, 
    'x__checkpoint_smoke_impl__mutmut_8': x__checkpoint_smoke_impl__mutmut_8, 
    'x__checkpoint_smoke_impl__mutmut_9': x__checkpoint_smoke_impl__mutmut_9, 
    'x__checkpoint_smoke_impl__mutmut_10': x__checkpoint_smoke_impl__mutmut_10, 
    'x__checkpoint_smoke_impl__mutmut_11': x__checkpoint_smoke_impl__mutmut_11, 
    'x__checkpoint_smoke_impl__mutmut_12': x__checkpoint_smoke_impl__mutmut_12, 
    'x__checkpoint_smoke_impl__mutmut_13': x__checkpoint_smoke_impl__mutmut_13, 
    'x__checkpoint_smoke_impl__mutmut_14': x__checkpoint_smoke_impl__mutmut_14, 
    'x__checkpoint_smoke_impl__mutmut_15': x__checkpoint_smoke_impl__mutmut_15, 
    'x__checkpoint_smoke_impl__mutmut_16': x__checkpoint_smoke_impl__mutmut_16, 
    'x__checkpoint_smoke_impl__mutmut_17': x__checkpoint_smoke_impl__mutmut_17, 
    'x__checkpoint_smoke_impl__mutmut_18': x__checkpoint_smoke_impl__mutmut_18, 
    'x__checkpoint_smoke_impl__mutmut_19': x__checkpoint_smoke_impl__mutmut_19, 
    'x__checkpoint_smoke_impl__mutmut_20': x__checkpoint_smoke_impl__mutmut_20, 
    'x__checkpoint_smoke_impl__mutmut_21': x__checkpoint_smoke_impl__mutmut_21, 
    'x__checkpoint_smoke_impl__mutmut_22': x__checkpoint_smoke_impl__mutmut_22, 
    'x__checkpoint_smoke_impl__mutmut_23': x__checkpoint_smoke_impl__mutmut_23, 
    'x__checkpoint_smoke_impl__mutmut_24': x__checkpoint_smoke_impl__mutmut_24, 
    'x__checkpoint_smoke_impl__mutmut_25': x__checkpoint_smoke_impl__mutmut_25, 
    'x__checkpoint_smoke_impl__mutmut_26': x__checkpoint_smoke_impl__mutmut_26, 
    'x__checkpoint_smoke_impl__mutmut_27': x__checkpoint_smoke_impl__mutmut_27, 
    'x__checkpoint_smoke_impl__mutmut_28': x__checkpoint_smoke_impl__mutmut_28, 
    'x__checkpoint_smoke_impl__mutmut_29': x__checkpoint_smoke_impl__mutmut_29, 
    'x__checkpoint_smoke_impl__mutmut_30': x__checkpoint_smoke_impl__mutmut_30, 
    'x__checkpoint_smoke_impl__mutmut_31': x__checkpoint_smoke_impl__mutmut_31, 
    'x__checkpoint_smoke_impl__mutmut_32': x__checkpoint_smoke_impl__mutmut_32, 
    'x__checkpoint_smoke_impl__mutmut_33': x__checkpoint_smoke_impl__mutmut_33, 
    'x__checkpoint_smoke_impl__mutmut_34': x__checkpoint_smoke_impl__mutmut_34, 
    'x__checkpoint_smoke_impl__mutmut_35': x__checkpoint_smoke_impl__mutmut_35, 
    'x__checkpoint_smoke_impl__mutmut_36': x__checkpoint_smoke_impl__mutmut_36, 
    'x__checkpoint_smoke_impl__mutmut_37': x__checkpoint_smoke_impl__mutmut_37, 
    'x__checkpoint_smoke_impl__mutmut_38': x__checkpoint_smoke_impl__mutmut_38, 
    'x__checkpoint_smoke_impl__mutmut_39': x__checkpoint_smoke_impl__mutmut_39, 
    'x__checkpoint_smoke_impl__mutmut_40': x__checkpoint_smoke_impl__mutmut_40, 
    'x__checkpoint_smoke_impl__mutmut_41': x__checkpoint_smoke_impl__mutmut_41, 
    'x__checkpoint_smoke_impl__mutmut_42': x__checkpoint_smoke_impl__mutmut_42, 
    'x__checkpoint_smoke_impl__mutmut_43': x__checkpoint_smoke_impl__mutmut_43, 
    'x__checkpoint_smoke_impl__mutmut_44': x__checkpoint_smoke_impl__mutmut_44, 
    'x__checkpoint_smoke_impl__mutmut_45': x__checkpoint_smoke_impl__mutmut_45, 
    'x__checkpoint_smoke_impl__mutmut_46': x__checkpoint_smoke_impl__mutmut_46, 
    'x__checkpoint_smoke_impl__mutmut_47': x__checkpoint_smoke_impl__mutmut_47, 
    'x__checkpoint_smoke_impl__mutmut_48': x__checkpoint_smoke_impl__mutmut_48, 
    'x__checkpoint_smoke_impl__mutmut_49': x__checkpoint_smoke_impl__mutmut_49, 
    'x__checkpoint_smoke_impl__mutmut_50': x__checkpoint_smoke_impl__mutmut_50, 
    'x__checkpoint_smoke_impl__mutmut_51': x__checkpoint_smoke_impl__mutmut_51, 
    'x__checkpoint_smoke_impl__mutmut_52': x__checkpoint_smoke_impl__mutmut_52, 
    'x__checkpoint_smoke_impl__mutmut_53': x__checkpoint_smoke_impl__mutmut_53, 
    'x__checkpoint_smoke_impl__mutmut_54': x__checkpoint_smoke_impl__mutmut_54, 
    'x__checkpoint_smoke_impl__mutmut_55': x__checkpoint_smoke_impl__mutmut_55, 
    'x__checkpoint_smoke_impl__mutmut_56': x__checkpoint_smoke_impl__mutmut_56, 
    'x__checkpoint_smoke_impl__mutmut_57': x__checkpoint_smoke_impl__mutmut_57, 
    'x__checkpoint_smoke_impl__mutmut_58': x__checkpoint_smoke_impl__mutmut_58, 
    'x__checkpoint_smoke_impl__mutmut_59': x__checkpoint_smoke_impl__mutmut_59, 
    'x__checkpoint_smoke_impl__mutmut_60': x__checkpoint_smoke_impl__mutmut_60, 
    'x__checkpoint_smoke_impl__mutmut_61': x__checkpoint_smoke_impl__mutmut_61
}

def _checkpoint_smoke_impl(*args, **kwargs):
    result = _mutmut_trampoline(x__checkpoint_smoke_impl__mutmut_orig, x__checkpoint_smoke_impl__mutmut_mutants, args, kwargs)
    return result 

_checkpoint_smoke_impl.__signature__ = _mutmut_signature(x__checkpoint_smoke_impl__mutmut_orig)
x__checkpoint_smoke_impl__mutmut_orig.__name__ = 'x__checkpoint_smoke_impl'


if _USE_TYPER:
    app = _typer.Typer(
        name="codex",
        add_completion=False,
        help="Codex CLI for reasoning templates plus local/offline runs (tokenize/train/eval/tracking).",
    )

    def _discover_reasoning_templates() -> Sequence[tuple[str, str, Path]]:
        if not REASONING_TEMPLATE_ROOT.exists():
            return []
        entries: list[tuple[str, str, Path]] = []
        for path in sorted(REASONING_TEMPLATE_ROOT.glob("*.yaml")):
            description = "Reasoning template"
            try:
                with path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            text = stripped.lstrip("#").strip()
                            if text and "Template" in text:
                                description = text
                                break
                        elif stripped:
                            break
            except OSError as e:
                logger.debug(f"OSError: {e}")
                logger.warning(f"OSError: {e}", exc_info=True)
                description = "Reasoning template"
            entries.append((path.stem, description, path))
        return entries

    def _load_yaml(path: Path) -> dict:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency missing
            echo(f"PyYAML not available: {exc}")
            raise Exit(code=1)
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            echo(f"Failed to load {path}: {exc}")
            raise Exit(code=1)
        if not isinstance(data, dict):
            echo(f"Unexpected config structure in {path}")
            raise Exit(code=1)
        return data

    reasoning_templates = _typer.Typer(
        name="reasoning-templates",
        help="Surface reasoning training presets and curricula metadata.",
    )

    @reasoning_templates.command("list")
    def list_reasoning_templates() -> None:
        entries = _discover_reasoning_templates()
        if not entries:
            echo("No reasoning templates found under configs/training/reasoning.")
            return
        for name, description, path in entries:
            try:
                relative = path.relative_to(Path.cwd())
            except ValueError as e:
                logger.debug(f"ValueError: {e}")
                logger.warning(f"ValueError: {e}", exc_info=True)
                relative = path
            echo(f"{name}\t{description} ({relative})")

    @reasoning_templates.command("explain")
    def explain_reasoning_template(name: str) -> None:
        entries = {entry[0]: entry for entry in _discover_reasoning_templates()}
        if name not in entries:
            echo(f"Unknown reasoning template: {name}")
            available = ", ".join(sorted(entries)) or "<none>"
            echo(f"Available templates: {available}")
            raise Exit(code=1)
        _, description, path = entries[name]
        echo(description)
        echo(f"Path: {path}")
        data = _load_yaml(path)
        curriculum_name = (
            data.get("curriculum", {}).get("phase_schedule")
            if isinstance(data.get("curriculum"), dict)
            else None
        )
        if curriculum_name:
            schedule_path = REASONING_CURRICULA_ROOT / f"{curriculum_name}.yaml"
            if schedule_path.exists():
                schedule_data = _load_yaml(schedule_path)
                phases = schedule_data.get("phase_schedule")
                if isinstance(phases, Iterable):
                    echo("Phases:")
                    for phase in phases:
                        if isinstance(phase, dict):
                            phase_id = phase.get("id", "<unknown>")
                            dataset = phase.get("dataset", "<dataset>")
                            steps = phase.get("steps", "?")
                            echo(f"  - {phase_id}: {dataset} (steps={steps})")
        reasoning_block = (
            data.get("training", {}).get("reasoning")
            if isinstance(data.get("training"), dict)
            else None
        )
        if isinstance(reasoning_block, dict):
            mode = (
                reasoning_block.get("objective", {}).get("mode")
                if isinstance(reasoning_block.get("objective"), dict)
                else None
            )
            if mode:
                echo(f"Objective: {mode}")
            if reasoning_block.get("tool_adapter", {}).get("enabled"):
                tools = reasoning_block.get("tool_adapter", {}).get("tools", [])
                if isinstance(tools, Iterable):
                    tool_list = ", ".join(str(tool) for tool in tools)
                    echo(f"Tools: {tool_list}")

    app.add_typer(reasoning_templates, name="reasoning-templates")

    @app.command("repo-map")
    def repo_map(
        reasoning: bool = _typer.Option(
            False, "--reasoning", help="Emit reasoning-specific entries."
        ),
        include: list[str] | None = _typer.Option(
            None,
            "--include",
            help="Only include specified categories (can be repeated).",
        ),
    ) -> None:
        from codex_ml.cli.repo_map import render_repo_map

        categories = tuple(include or [])
        echo(render_repo_map(reasoning=reasoning, include=categories))

    @app.command("version")
    def version() -> None:
        try:
            from . import __version__
        except Exception:  # pragma: no cover - defensive fallback
            __version__ = "unknown"
        echo(__version__)

    @app.command("track-smoke")
    def track_smoke(
        dir: Optional[Path] = _typer.Option(None, "--dir", help="Local mlruns dir"),
    ) -> None:
        _track_smoke_impl(dir)

    @app.command("split-smoke")
    def split_smoke(seed: int = 1337) -> None:
        _split_smoke_impl(seed)

    @app.command("checkpoint-smoke")
    def checkpoint_smoke(
        out_dir: Path = _typer.Option(Path(".checkpoints"), "--out", help="Checkpoint directory"),
    ) -> None:
        _checkpoint_smoke_impl(out_dir)

else:  # pragma: no cover - click fallback
    import click as _click

    @_click.group(
        name="codex",
        help="Codex CLI for reasoning templates plus local/offline runs (tokenize/train/eval/tracking).",
    )
    def app() -> None:
        """Codex offline smoke helpers."""

    def _discover_reasoning_templates() -> Sequence[tuple[str, str, Path]]:
        if not REASONING_TEMPLATE_ROOT.exists():
            return []
        entries: list[tuple[str, str, Path]] = []
        for path in sorted(REASONING_TEMPLATE_ROOT.glob("*.yaml")):
            description = "Reasoning template"
            try:
                with path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            text = stripped.lstrip("#").strip()
                            if text and "Template" in text:
                                description = text
                                break
                        elif stripped:
                            break
            except OSError as e:
                logger.debug(f"OSError: {e}")
                logger.warning(f"OSError: {e}", exc_info=True)
                description = "Reasoning template"
            entries.append((path.stem, description, path))
        return entries

    def _load_yaml(path: Path) -> dict:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency missing
            echo(f"PyYAML not available: {exc}")
            raise Exit(code=1)
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            echo(f"Failed to load {path}: {exc}")
            raise Exit(code=1)
        if not isinstance(data, dict):
            echo(f"Unexpected config structure in {path}")
            raise Exit(code=1)
        return data

    @app.command("version")
    def version() -> None:
        try:
            from . import __version__
        except Exception:  # pragma: no cover - defensive fallback
            __version__ = "unknown"
        echo(__version__)

    @app.command("track-smoke")
    @_click.option(
        "--dir", "dir_", type=_click.Path(path_type=Path), default=None, help="Local mlruns dir"
    )
    def track_smoke(dir_: Optional[Path]) -> None:
        _track_smoke_impl(dir_)

    @app.command("split-smoke")
    @_click.option(
        "--seed", type=int, default=1337, show_default=True, help="Seed for deterministic split"
    )
    def split_smoke(seed: int) -> None:
        _split_smoke_impl(seed)

    @app.command("checkpoint-smoke")
    @_click.option(
        "--out",
        "out_dir",
        type=_click.Path(path_type=Path),
        default=Path(".checkpoints"),
        show_default=True,
        help="Checkpoint directory",
    )
    def checkpoint_smoke(out_dir: Path) -> None:
        _checkpoint_smoke_impl(out_dir)

    @app.group(
        name="reasoning-templates",
        help="Surface reasoning training presets and curricula metadata.",
    )
    def reasoning_templates() -> None:
        """Reasoning template helpers."""

    @reasoning_templates.command("list")
    def list_reasoning_templates() -> None:
        entries = _discover_reasoning_templates()
        if not entries:
            echo("No reasoning templates found under configs/training/reasoning.")
            return
        for name, description, path in entries:
            try:
                relative = path.relative_to(Path.cwd())
            except ValueError as e:
                logger.debug(f"ValueError: {e}")
                logger.warning(f"ValueError: {e}", exc_info=True)
                relative = path
            echo(f"{name}\t{description} ({relative})")

    @reasoning_templates.command("explain")
    @_click.argument("name")
    def explain_reasoning_template(name: str) -> None:
        entries = {entry[0]: entry for entry in _discover_reasoning_templates()}
        if name not in entries:
            echo(f"Unknown reasoning template: {name}")
            available = ", ".join(sorted(entries)) or "<none>"
            echo(f"Available templates: {available}")
            raise Exit(code=1)
        _, description, path = entries[name]
        echo(description)
        echo(f"Path: {path}")
        data = _load_yaml(path)
        curriculum_name = (
            data.get("curriculum", {}).get("phase_schedule")
            if isinstance(data.get("curriculum"), dict)
            else None
        )
        if curriculum_name:
            schedule_path = REASONING_CURRICULA_ROOT / f"{curriculum_name}.yaml"
            if schedule_path.exists():
                schedule_data = _load_yaml(schedule_path)
                phases = schedule_data.get("phase_schedule")
                if isinstance(phases, Iterable):
                    echo("Phases:")
                    for phase in phases:
                        if isinstance(phase, dict):
                            phase_id = phase.get("id", "<unknown>")
                            dataset = phase.get("dataset", "<dataset>")
                            steps = phase.get("steps", "?")
                            echo(f"  - {phase_id}: {dataset} (steps={steps})")
        reasoning_block = (
            data.get("training", {}).get("reasoning")
            if isinstance(data.get("training"), dict)
            else None
        )
        if isinstance(reasoning_block, dict):
            mode = (
                reasoning_block.get("objective", {}).get("mode")
                if isinstance(reasoning_block.get("objective"), dict)
                else None
            )
            if mode:
                echo(f"Objective: {mode}")
            if reasoning_block.get("tool_adapter", {}).get("enabled"):
                tools = reasoning_block.get("tool_adapter", {}).get("tools", [])
                if isinstance(tools, Iterable):
                    tool_list = ", ".join(str(tool) for tool in tools)
                    echo(f"Tools: {tool_list}")

    @app.command("repo-map")
    @_click.option("--reasoning", is_flag=True, help="Emit reasoning-specific entries.")
    @_click.option(
        "--include",
        "includes",
        multiple=True,
        help="Only include specified categories (can be repeated).",
    )
    def repo_map(reasoning: bool, includes: tuple[str, ...]) -> None:
        from codex_ml.cli.repo_map import render_repo_map

        echo(render_repo_map(reasoning=reasoning, include=includes))


def main() -> None:  # pragma: no cover - thin wrapper for python -m usage
    app()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
