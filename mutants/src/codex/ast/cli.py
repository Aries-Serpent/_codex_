"""
AST CLI (Typer) — analyze | audit | diff

Human-readable by default; use --json for machine output.
Exit codes:
 0 success
 2 invalid args
 3 runtime error
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path
from typing import Any

import typer

app = typer.Typer(help="AST tools: analyze, audit, diff.")
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


def x__collect_py_files__mutmut_orig(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".py":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("*.py")]
    return []


def x__collect_py_files__mutmut_1(path: Path) -> list[Path]:
    if path.is_file() or path.suffix == ".py":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("*.py")]
    return []


def x__collect_py_files__mutmut_2(path: Path) -> list[Path]:
    if path.is_file() and path.suffix != ".py":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("*.py")]
    return []


def x__collect_py_files__mutmut_3(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == "XX.pyXX":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("*.py")]
    return []


def x__collect_py_files__mutmut_4(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".PY":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("*.py")]
    return []


def x__collect_py_files__mutmut_5(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".py":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob(None)]
    return []


def x__collect_py_files__mutmut_6(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".py":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("XX*.pyXX")]
    return []


def x__collect_py_files__mutmut_7(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".py":
        return [path]
    if path.is_dir():
        return [p for p in path.rglob("*.PY")]
    return []

x__collect_py_files__mutmut_mutants : ClassVar[MutantDict] = {
'x__collect_py_files__mutmut_1': x__collect_py_files__mutmut_1, 
    'x__collect_py_files__mutmut_2': x__collect_py_files__mutmut_2, 
    'x__collect_py_files__mutmut_3': x__collect_py_files__mutmut_3, 
    'x__collect_py_files__mutmut_4': x__collect_py_files__mutmut_4, 
    'x__collect_py_files__mutmut_5': x__collect_py_files__mutmut_5, 
    'x__collect_py_files__mutmut_6': x__collect_py_files__mutmut_6, 
    'x__collect_py_files__mutmut_7': x__collect_py_files__mutmut_7
}

def _collect_py_files(*args, **kwargs):
    result = _mutmut_trampoline(x__collect_py_files__mutmut_orig, x__collect_py_files__mutmut_mutants, args, kwargs)
    return result 

_collect_py_files.__signature__ = _mutmut_signature(x__collect_py_files__mutmut_orig)
x__collect_py_files__mutmut_orig.__name__ = 'x__collect_py_files'


def x__analyze_path__mutmut_orig(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_1(path: Path) -> dict[str, Any]:
    files = None
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_2(path: Path) -> dict[str, Any]:
    files = _collect_py_files(None)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_3(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = None
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_4(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 1
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_5(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines = sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_6(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines -= sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_7(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                None
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_8(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                2 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_9(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding=None, errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_10(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors=None).splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_11(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_12(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", ).splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_13(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="XXutf-8XX", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_14(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="UTF-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_15(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="XXignoreXX").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_16(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="IGNORE").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_17(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(None)
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_18(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(None, exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_19(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=None)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_20(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_21(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", )
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_22(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=False)
    return {
        "path": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_23(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "XXpathXX": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_24(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "PATH": str(path),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_25(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(None),
        "files": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_26(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "XXfilesXX": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_27(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "FILES": len(files),
        "total_lines": total_lines,
    }


def x__analyze_path__mutmut_28(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "XXtotal_linesXX": total_lines,
    }


def x__analyze_path__mutmut_29(path: Path) -> dict[str, Any]:
    files = _collect_py_files(path)
    total_lines = 0
    for f in files:
        try:
            total_lines += sum(
                1 for _ in f.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Exception: {e}", exc_info=True)
    return {
        "path": str(path),
        "files": len(files),
        "TOTAL_LINES": total_lines,
    }

x__analyze_path__mutmut_mutants : ClassVar[MutantDict] = {
'x__analyze_path__mutmut_1': x__analyze_path__mutmut_1, 
    'x__analyze_path__mutmut_2': x__analyze_path__mutmut_2, 
    'x__analyze_path__mutmut_3': x__analyze_path__mutmut_3, 
    'x__analyze_path__mutmut_4': x__analyze_path__mutmut_4, 
    'x__analyze_path__mutmut_5': x__analyze_path__mutmut_5, 
    'x__analyze_path__mutmut_6': x__analyze_path__mutmut_6, 
    'x__analyze_path__mutmut_7': x__analyze_path__mutmut_7, 
    'x__analyze_path__mutmut_8': x__analyze_path__mutmut_8, 
    'x__analyze_path__mutmut_9': x__analyze_path__mutmut_9, 
    'x__analyze_path__mutmut_10': x__analyze_path__mutmut_10, 
    'x__analyze_path__mutmut_11': x__analyze_path__mutmut_11, 
    'x__analyze_path__mutmut_12': x__analyze_path__mutmut_12, 
    'x__analyze_path__mutmut_13': x__analyze_path__mutmut_13, 
    'x__analyze_path__mutmut_14': x__analyze_path__mutmut_14, 
    'x__analyze_path__mutmut_15': x__analyze_path__mutmut_15, 
    'x__analyze_path__mutmut_16': x__analyze_path__mutmut_16, 
    'x__analyze_path__mutmut_17': x__analyze_path__mutmut_17, 
    'x__analyze_path__mutmut_18': x__analyze_path__mutmut_18, 
    'x__analyze_path__mutmut_19': x__analyze_path__mutmut_19, 
    'x__analyze_path__mutmut_20': x__analyze_path__mutmut_20, 
    'x__analyze_path__mutmut_21': x__analyze_path__mutmut_21, 
    'x__analyze_path__mutmut_22': x__analyze_path__mutmut_22, 
    'x__analyze_path__mutmut_23': x__analyze_path__mutmut_23, 
    'x__analyze_path__mutmut_24': x__analyze_path__mutmut_24, 
    'x__analyze_path__mutmut_25': x__analyze_path__mutmut_25, 
    'x__analyze_path__mutmut_26': x__analyze_path__mutmut_26, 
    'x__analyze_path__mutmut_27': x__analyze_path__mutmut_27, 
    'x__analyze_path__mutmut_28': x__analyze_path__mutmut_28, 
    'x__analyze_path__mutmut_29': x__analyze_path__mutmut_29
}

def _analyze_path(*args, **kwargs):
    result = _mutmut_trampoline(x__analyze_path__mutmut_orig, x__analyze_path__mutmut_mutants, args, kwargs)
    return result 

_analyze_path.__signature__ = _mutmut_signature(x__analyze_path__mutmut_orig)
x__analyze_path__mutmut_orig.__name__ = 'x__analyze_path'


@app.command("analyze")
def analyze(
    target: Path = typer.Argument(..., exists=True, readable=True),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
):
    try:
        res = _analyze_path(target)
        if json_output:
            typer.echo(json.dumps(res, indent=2))
        else:
            typer.echo(f"Analyze {target}: files={res['files']} lines={res['total_lines']}")
    except Exception as e:
        logger.debug(f"Exception: {e}")
        typer.echo(f"Analyze error: {e}", err=True)
        raise typer.Exit(code=3)


@app.command("audit")
def audit(
    target: Path = typer.Argument(".", help="Root to audit"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
):
    try:
        res = _analyze_path(target)
        # For now, reuse analyze summary as audit-lite
        if json_output:
            typer.echo(json.dumps({"summary": res}, indent=2))
        else:
            typer.echo(f"Audit {target}: files={res['files']} lines={res['total_lines']}")
    except Exception as e:
        logger.debug(f"Exception: {e}")
        typer.echo(f"Audit error: {e}", err=True)
        raise typer.Exit(code=3)


@app.command("diff")
def diff(
    a: Path = typer.Argument(..., exists=True, readable=True),
    b: Path = typer.Argument(..., exists=True, readable=True),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
):
    try:
        ra = _analyze_path(a)
        rb = _analyze_path(b)
        delta_files = rb["files"] - ra["files"]
        delta_lines = rb["total_lines"] - ra["total_lines"]
        res = {
            "a": ra,
            "b": rb,
            "delta_files": delta_files,
            "delta_lines": delta_lines,
        }
        if json_output:
            typer.echo(json.dumps(res, indent=2))
        else:
            typer.echo(f"Diff files={delta_files:+} lines={delta_lines:+}")
    except Exception as e:
        logger.debug(f"Exception: {e}")
        typer.echo(f"Diff error: {e}", err=True)
        raise typer.Exit(code=3)


if __name__ == "__main__":  # pragma: no cover
    app()
