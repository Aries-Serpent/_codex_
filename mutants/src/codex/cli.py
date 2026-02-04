"""Unified CLI for codex, using click for subcommands and input validation."""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import importlib
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import click

try:  # pragma: no cover - optional dependency
    import typer
except Exception:  # pragma: no cover - degrade gracefully when Typer missing
    typer = None  # type: ignore[assignment]
else:  # pragma: no cover - exercised in Typer-enabled environments
    try:
        from codex.cli_knowledge import app as knowledge_app
        from codex.cli_release import app as release_app
    except Exception:  # pragma: no cover - Typer sub-app import guard
        knowledge_app = None  # type: ignore[assignment]
        release_app = None  # type: ignore[assignment]
    else:
        app = typer.Typer(help="Codex Typer CLI (release + knowledge)")
        app.add_typer(release_app, name="release")
        app.add_typer(knowledge_app, name="knowledge")

try:  # pragma: no cover - optional dependency
    from typer.main import get_command as _typer_get_command
except Exception:  # pragma: no cover
    _typer_get_command = None

try:  # pragma: no cover - optional dependency
    from codex_digest.error_capture import log_error as _log_error
except Exception:  # pragma: no cover

    def _log_error(step_no: str, step_desc: str, msg: str, ctx: str) -> None:  # type: ignore[func-returns-value]
        """Fallback error logger when codex_digest is unavailable."""
        return None


# Resolve helper scripts relative to this file so the CLI works from any CWD.
TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools"
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


def x__run_ingest__mutmut_orig() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_1() -> None:
    """Ingest example data into the Codex environment."""
    src = None
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_2() -> None:
    """Ingest example data into the Codex environment."""
    src = Path(None)
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_3() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("XXdata/example.jsonlXX")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_4() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("DATA/EXAMPLE.JSONL")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_5() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = None
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_6() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path(None)
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_7() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("XXdata/ingested.jsonlXX")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_8() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("DATA/INGESTED.JSONL")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_9() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_10() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(None)
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_11() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(None, encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_12() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding=None)
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_13() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(encoding="utf-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_14() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), )
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_15() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="XXutf-8XX")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_16() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="UTF-8")
    print(f"Ingested {src} -> {dst}")


def x__run_ingest__mutmut_17() -> None:
    """Ingest example data into the Codex environment."""
    src = Path("data/example.jsonl")
    dst = Path("data/ingested.jsonl")
    if not src.exists():
        print(f"No source data found at {src}")
        return
    dst.write_text(src.read_text(), encoding="utf-8")
    print(None)

x__run_ingest__mutmut_mutants : ClassVar[MutantDict] = {
'x__run_ingest__mutmut_1': x__run_ingest__mutmut_1, 
    'x__run_ingest__mutmut_2': x__run_ingest__mutmut_2, 
    'x__run_ingest__mutmut_3': x__run_ingest__mutmut_3, 
    'x__run_ingest__mutmut_4': x__run_ingest__mutmut_4, 
    'x__run_ingest__mutmut_5': x__run_ingest__mutmut_5, 
    'x__run_ingest__mutmut_6': x__run_ingest__mutmut_6, 
    'x__run_ingest__mutmut_7': x__run_ingest__mutmut_7, 
    'x__run_ingest__mutmut_8': x__run_ingest__mutmut_8, 
    'x__run_ingest__mutmut_9': x__run_ingest__mutmut_9, 
    'x__run_ingest__mutmut_10': x__run_ingest__mutmut_10, 
    'x__run_ingest__mutmut_11': x__run_ingest__mutmut_11, 
    'x__run_ingest__mutmut_12': x__run_ingest__mutmut_12, 
    'x__run_ingest__mutmut_13': x__run_ingest__mutmut_13, 
    'x__run_ingest__mutmut_14': x__run_ingest__mutmut_14, 
    'x__run_ingest__mutmut_15': x__run_ingest__mutmut_15, 
    'x__run_ingest__mutmut_16': x__run_ingest__mutmut_16, 
    'x__run_ingest__mutmut_17': x__run_ingest__mutmut_17
}

def _run_ingest(*args, **kwargs):
    result = _mutmut_trampoline(x__run_ingest__mutmut_orig, x__run_ingest__mutmut_mutants, args, kwargs)
    return result 

_run_ingest.__signature__ = _mutmut_signature(x__run_ingest__mutmut_orig)
x__run_ingest__mutmut_orig.__name__ = 'x__run_ingest'


def x__run_ci__mutmut_orig() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_1() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(None, check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_2() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=None)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_3() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_4() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_5() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["XXnoxXX", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_6() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["NOX", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_7() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "XX-sXX", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_8() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-S", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_9() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "XXtestsXX"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_10() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "TESTS"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_11() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=False)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_12() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(None)
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_13() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(None)
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_14() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error(None, "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_15() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", None, str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_16() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", None, "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_17() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), None)
        raise SystemExit(1) from exc


def x__run_ci__mutmut_18() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_19() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_20() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_21() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), )
        raise SystemExit(1) from exc


def x__run_ci__mutmut_22() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("XXSTEP CIXX", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_23() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("step ci", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_24() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "XXnox -s testsXX", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_25() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "NOX -S TESTS", str(exc), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_26() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(None), "running local CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_27() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "XXrunning local CIXX")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_28() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local ci")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_29() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "RUNNING LOCAL CI")
        raise SystemExit(1) from exc


def x__run_ci__mutmut_30() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(None) from exc


def x__run_ci__mutmut_31() -> None:
    """Run local CI checks (lint + tests)."""
    try:
        subprocess.run(["nox", "-s", "tests"], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        print(f"CI failed: {exc}")
        _log_error("STEP CI", "nox -s tests", str(exc), "running local CI")
        raise SystemExit(2) from exc

x__run_ci__mutmut_mutants : ClassVar[MutantDict] = {
'x__run_ci__mutmut_1': x__run_ci__mutmut_1, 
    'x__run_ci__mutmut_2': x__run_ci__mutmut_2, 
    'x__run_ci__mutmut_3': x__run_ci__mutmut_3, 
    'x__run_ci__mutmut_4': x__run_ci__mutmut_4, 
    'x__run_ci__mutmut_5': x__run_ci__mutmut_5, 
    'x__run_ci__mutmut_6': x__run_ci__mutmut_6, 
    'x__run_ci__mutmut_7': x__run_ci__mutmut_7, 
    'x__run_ci__mutmut_8': x__run_ci__mutmut_8, 
    'x__run_ci__mutmut_9': x__run_ci__mutmut_9, 
    'x__run_ci__mutmut_10': x__run_ci__mutmut_10, 
    'x__run_ci__mutmut_11': x__run_ci__mutmut_11, 
    'x__run_ci__mutmut_12': x__run_ci__mutmut_12, 
    'x__run_ci__mutmut_13': x__run_ci__mutmut_13, 
    'x__run_ci__mutmut_14': x__run_ci__mutmut_14, 
    'x__run_ci__mutmut_15': x__run_ci__mutmut_15, 
    'x__run_ci__mutmut_16': x__run_ci__mutmut_16, 
    'x__run_ci__mutmut_17': x__run_ci__mutmut_17, 
    'x__run_ci__mutmut_18': x__run_ci__mutmut_18, 
    'x__run_ci__mutmut_19': x__run_ci__mutmut_19, 
    'x__run_ci__mutmut_20': x__run_ci__mutmut_20, 
    'x__run_ci__mutmut_21': x__run_ci__mutmut_21, 
    'x__run_ci__mutmut_22': x__run_ci__mutmut_22, 
    'x__run_ci__mutmut_23': x__run_ci__mutmut_23, 
    'x__run_ci__mutmut_24': x__run_ci__mutmut_24, 
    'x__run_ci__mutmut_25': x__run_ci__mutmut_25, 
    'x__run_ci__mutmut_26': x__run_ci__mutmut_26, 
    'x__run_ci__mutmut_27': x__run_ci__mutmut_27, 
    'x__run_ci__mutmut_28': x__run_ci__mutmut_28, 
    'x__run_ci__mutmut_29': x__run_ci__mutmut_29, 
    'x__run_ci__mutmut_30': x__run_ci__mutmut_30, 
    'x__run_ci__mutmut_31': x__run_ci__mutmut_31
}

def _run_ci(*args, **kwargs):
    result = _mutmut_trampoline(x__run_ci__mutmut_orig, x__run_ci__mutmut_mutants, args, kwargs)
    return result 

_run_ci.__signature__ = _mutmut_signature(x__run_ci__mutmut_orig)
x__run_ci__mutmut_orig.__name__ = 'x__run_ci'


def x__fix_pool__mutmut_orig(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_1(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_2(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = None
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_3(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(None, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_4(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, None, None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_5(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr("_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_6(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_7(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", )
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_8(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "XX_executorXX", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_9(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_EXECUTOR", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_10(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_11(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=None)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_12(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=True)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_13(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = None
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_14(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=None)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_15(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error(None, "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_16(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", None, str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_17(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", None, "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_18(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), None)
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_19(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_20(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_21(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_22(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), )
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_23(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("XXPOOLXX", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_24(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("pool", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_25(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "XXfix executorXX", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_26(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "FIX EXECUTOR", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_27(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(None), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_28(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "XXconfigure thread poolXX")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_29(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "CONFIGURE THREAD POOL")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_30(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault(None, "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_31(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", None)
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_32(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_33(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", )
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_34(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("XXCODEX_SQLITE_POOLXX", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_35(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("codex_sqlite_pool", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_36(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "XX1XX")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_37(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = None
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_38(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(None)
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_39(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv(None, ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_40(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", None))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_41(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv(".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_42(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_43(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("XXCODEX_LOG_DB_PATHXX", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_44(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("codex_log_db_path", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_45(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", "XX.codex/session_logs.dbXX"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_46(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".CODEX/SESSION_LOGS.DB"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_47(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=None, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_48(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=None)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_49(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_50(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, )

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_51(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=False, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_52(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=False)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_53(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = None
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_54(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers and 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_55(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 1
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_56(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(None):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_57(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(None, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_58(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, None)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_59(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_60(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, )):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_61(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(1, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_62(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(None)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_63(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(None))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_64(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(None)
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_65(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error(None, "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_66(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", None, str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_67(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", None, f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_68(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), None)
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_69(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_70(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_71(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_72(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), )
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_73(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("XXPOOLXX", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_74(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("pool", "warm connection", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_75(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "XXwarm connectionXX", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_76(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "WARM CONNECTION", str(exc), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_77(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(None), f"db={db}")
            break

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_78(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            return

    print(f"enabled SQLite pooling (warm={workers}) for {db}")


def x__fix_pool__mutmut_79(max_workers: int | None = None) -> None:
    """Configure a process/thread pool for tokenization.

    Some tokenization libraries lazily create a global
    :class:`concurrent.futures.ThreadPoolExecutor`.  On certain
    platforms this implicit executor can lead to hangs or excessive
    resource usage.  This function resets the global executor with a
    bounded number of workers.  If ``max_workers`` is ``None`` the
    existing executor (if any) is left untouched.  The function is a
    best-effort helper - if ``concurrent.futures`` internals are not
    available the call is silently ignored.

    Parameters
    ----------
    max_workers:
        Optional number of worker threads / warm SQLite connections.  ``None``
        leaves the default executor untouched and skips warming connections.
    """

    # --- Fix global ThreadPoolExecutor ---
    try:  # pragma: no cover - implementation detail
        import concurrent.futures as _cf

        if max_workers is not None:
            executor = getattr(_cf, "_executor", None)
            if executor is not None:
                executor.shutdown(wait=False)
            _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
    except Exception as exc:  # pragma: no cover - best effort
        _log_error("POOL", "fix executor", str(exc), "configure thread pool")
        return

    # --- Enable SQLite connection pooling ---
    from .db import sqlite_patch

    os.environ.setdefault("CODEX_SQLITE_POOL", "1")
    sqlite_patch.enable_pooling()

    db = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
    db.parent.mkdir(parents=True, exist_ok=True)

    workers = max_workers or 0
    for _ in range(max(0, workers)):
        try:  # pragma: no cover - best effort
            sqlite3.connect(str(db))
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("POOL", "warm connection", str(exc), f"db={db}")
            break

    print(None)

x__fix_pool__mutmut_mutants : ClassVar[MutantDict] = {
'x__fix_pool__mutmut_1': x__fix_pool__mutmut_1, 
    'x__fix_pool__mutmut_2': x__fix_pool__mutmut_2, 
    'x__fix_pool__mutmut_3': x__fix_pool__mutmut_3, 
    'x__fix_pool__mutmut_4': x__fix_pool__mutmut_4, 
    'x__fix_pool__mutmut_5': x__fix_pool__mutmut_5, 
    'x__fix_pool__mutmut_6': x__fix_pool__mutmut_6, 
    'x__fix_pool__mutmut_7': x__fix_pool__mutmut_7, 
    'x__fix_pool__mutmut_8': x__fix_pool__mutmut_8, 
    'x__fix_pool__mutmut_9': x__fix_pool__mutmut_9, 
    'x__fix_pool__mutmut_10': x__fix_pool__mutmut_10, 
    'x__fix_pool__mutmut_11': x__fix_pool__mutmut_11, 
    'x__fix_pool__mutmut_12': x__fix_pool__mutmut_12, 
    'x__fix_pool__mutmut_13': x__fix_pool__mutmut_13, 
    'x__fix_pool__mutmut_14': x__fix_pool__mutmut_14, 
    'x__fix_pool__mutmut_15': x__fix_pool__mutmut_15, 
    'x__fix_pool__mutmut_16': x__fix_pool__mutmut_16, 
    'x__fix_pool__mutmut_17': x__fix_pool__mutmut_17, 
    'x__fix_pool__mutmut_18': x__fix_pool__mutmut_18, 
    'x__fix_pool__mutmut_19': x__fix_pool__mutmut_19, 
    'x__fix_pool__mutmut_20': x__fix_pool__mutmut_20, 
    'x__fix_pool__mutmut_21': x__fix_pool__mutmut_21, 
    'x__fix_pool__mutmut_22': x__fix_pool__mutmut_22, 
    'x__fix_pool__mutmut_23': x__fix_pool__mutmut_23, 
    'x__fix_pool__mutmut_24': x__fix_pool__mutmut_24, 
    'x__fix_pool__mutmut_25': x__fix_pool__mutmut_25, 
    'x__fix_pool__mutmut_26': x__fix_pool__mutmut_26, 
    'x__fix_pool__mutmut_27': x__fix_pool__mutmut_27, 
    'x__fix_pool__mutmut_28': x__fix_pool__mutmut_28, 
    'x__fix_pool__mutmut_29': x__fix_pool__mutmut_29, 
    'x__fix_pool__mutmut_30': x__fix_pool__mutmut_30, 
    'x__fix_pool__mutmut_31': x__fix_pool__mutmut_31, 
    'x__fix_pool__mutmut_32': x__fix_pool__mutmut_32, 
    'x__fix_pool__mutmut_33': x__fix_pool__mutmut_33, 
    'x__fix_pool__mutmut_34': x__fix_pool__mutmut_34, 
    'x__fix_pool__mutmut_35': x__fix_pool__mutmut_35, 
    'x__fix_pool__mutmut_36': x__fix_pool__mutmut_36, 
    'x__fix_pool__mutmut_37': x__fix_pool__mutmut_37, 
    'x__fix_pool__mutmut_38': x__fix_pool__mutmut_38, 
    'x__fix_pool__mutmut_39': x__fix_pool__mutmut_39, 
    'x__fix_pool__mutmut_40': x__fix_pool__mutmut_40, 
    'x__fix_pool__mutmut_41': x__fix_pool__mutmut_41, 
    'x__fix_pool__mutmut_42': x__fix_pool__mutmut_42, 
    'x__fix_pool__mutmut_43': x__fix_pool__mutmut_43, 
    'x__fix_pool__mutmut_44': x__fix_pool__mutmut_44, 
    'x__fix_pool__mutmut_45': x__fix_pool__mutmut_45, 
    'x__fix_pool__mutmut_46': x__fix_pool__mutmut_46, 
    'x__fix_pool__mutmut_47': x__fix_pool__mutmut_47, 
    'x__fix_pool__mutmut_48': x__fix_pool__mutmut_48, 
    'x__fix_pool__mutmut_49': x__fix_pool__mutmut_49, 
    'x__fix_pool__mutmut_50': x__fix_pool__mutmut_50, 
    'x__fix_pool__mutmut_51': x__fix_pool__mutmut_51, 
    'x__fix_pool__mutmut_52': x__fix_pool__mutmut_52, 
    'x__fix_pool__mutmut_53': x__fix_pool__mutmut_53, 
    'x__fix_pool__mutmut_54': x__fix_pool__mutmut_54, 
    'x__fix_pool__mutmut_55': x__fix_pool__mutmut_55, 
    'x__fix_pool__mutmut_56': x__fix_pool__mutmut_56, 
    'x__fix_pool__mutmut_57': x__fix_pool__mutmut_57, 
    'x__fix_pool__mutmut_58': x__fix_pool__mutmut_58, 
    'x__fix_pool__mutmut_59': x__fix_pool__mutmut_59, 
    'x__fix_pool__mutmut_60': x__fix_pool__mutmut_60, 
    'x__fix_pool__mutmut_61': x__fix_pool__mutmut_61, 
    'x__fix_pool__mutmut_62': x__fix_pool__mutmut_62, 
    'x__fix_pool__mutmut_63': x__fix_pool__mutmut_63, 
    'x__fix_pool__mutmut_64': x__fix_pool__mutmut_64, 
    'x__fix_pool__mutmut_65': x__fix_pool__mutmut_65, 
    'x__fix_pool__mutmut_66': x__fix_pool__mutmut_66, 
    'x__fix_pool__mutmut_67': x__fix_pool__mutmut_67, 
    'x__fix_pool__mutmut_68': x__fix_pool__mutmut_68, 
    'x__fix_pool__mutmut_69': x__fix_pool__mutmut_69, 
    'x__fix_pool__mutmut_70': x__fix_pool__mutmut_70, 
    'x__fix_pool__mutmut_71': x__fix_pool__mutmut_71, 
    'x__fix_pool__mutmut_72': x__fix_pool__mutmut_72, 
    'x__fix_pool__mutmut_73': x__fix_pool__mutmut_73, 
    'x__fix_pool__mutmut_74': x__fix_pool__mutmut_74, 
    'x__fix_pool__mutmut_75': x__fix_pool__mutmut_75, 
    'x__fix_pool__mutmut_76': x__fix_pool__mutmut_76, 
    'x__fix_pool__mutmut_77': x__fix_pool__mutmut_77, 
    'x__fix_pool__mutmut_78': x__fix_pool__mutmut_78, 
    'x__fix_pool__mutmut_79': x__fix_pool__mutmut_79
}

def _fix_pool(*args, **kwargs):
    result = _mutmut_trampoline(x__fix_pool__mutmut_orig, x__fix_pool__mutmut_mutants, args, kwargs)
    return result 

_fix_pool.__signature__ = _mutmut_signature(x__fix_pool__mutmut_orig)
x__fix_pool__mutmut_orig.__name__ = 'x__fix_pool'


ALLOWED_TASKS = {
    "ingest": (_run_ingest, "Ingest example data into the Codex environment."),
    "ci": (_run_ci, "Run local CI checks (lint + tests)."),
    "pool-fix": (lambda: _fix_pool(4), "Reset tokenization thread pool (default 4 workers)."),
}


def x__missing_command__mutmut_orig(name: str, message: str, help_text: str | None = None) -> click.Command:
    """Return a small Click command that raises ``message`` when invoked."""

    help_msg = help_text or message

    @click.command(name=name, help=help_msg)
    def _cmd() -> None:  # pragma: no cover - trivial error reporting
        raise click.ClickException(message)

    return _cmd


def x__missing_command__mutmut_1(name: str, message: str, help_text: str | None = None) -> click.Command:
    """Return a small Click command that raises ``message`` when invoked."""

    help_msg = None

    @click.command(name=name, help=help_msg)
    def _cmd() -> None:  # pragma: no cover - trivial error reporting
        raise click.ClickException(message)

    return _cmd


def x__missing_command__mutmut_2(name: str, message: str, help_text: str | None = None) -> click.Command:
    """Return a small Click command that raises ``message`` when invoked."""

    help_msg = help_text and message

    @click.command(name=name, help=help_msg)
    def _cmd() -> None:  # pragma: no cover - trivial error reporting
        raise click.ClickException(message)

    return _cmd

x__missing_command__mutmut_mutants : ClassVar[MutantDict] = {
'x__missing_command__mutmut_1': x__missing_command__mutmut_1, 
    'x__missing_command__mutmut_2': x__missing_command__mutmut_2
}

def _missing_command(*args, **kwargs):
    result = _mutmut_trampoline(x__missing_command__mutmut_orig, x__missing_command__mutmut_mutants, args, kwargs)
    return result 

_missing_command.__signature__ = _mutmut_signature(x__missing_command__mutmut_orig)
x__missing_command__mutmut_orig.__name__ = 'x__missing_command'


def x__register_click_command__mutmut_orig(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_1(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name not in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_2(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = None
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_3(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(None)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_4(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = None
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_5(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(None, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_6(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, None)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_7(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_8(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, )
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_9(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = None
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_10(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(None)
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_11(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(None, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_12(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, None, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_13(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, None))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_14(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_15(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_16(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, ))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_17(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text or not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_18(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_19(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(None, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_20(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, None, None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_21(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr("help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_22(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_23(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", ):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_24(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "XXhelpXX", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_25(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "HELP", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_click_command__mutmut_26(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = None
    group.add_command(command, name=name)


def x__register_click_command__mutmut_27(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(None, name=name)


def x__register_click_command__mutmut_28(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=None)


def x__register_click_command__mutmut_29(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(name=name)


def x__register_click_command__mutmut_30(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach ``module_path.attr`` to ``group`` under ``name`` if available."""

    if name in group.commands:
        return
    try:
        module = importlib.import_module(module_path)
        command = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, )

x__register_click_command__mutmut_mutants : ClassVar[MutantDict] = {
'x__register_click_command__mutmut_1': x__register_click_command__mutmut_1, 
    'x__register_click_command__mutmut_2': x__register_click_command__mutmut_2, 
    'x__register_click_command__mutmut_3': x__register_click_command__mutmut_3, 
    'x__register_click_command__mutmut_4': x__register_click_command__mutmut_4, 
    'x__register_click_command__mutmut_5': x__register_click_command__mutmut_5, 
    'x__register_click_command__mutmut_6': x__register_click_command__mutmut_6, 
    'x__register_click_command__mutmut_7': x__register_click_command__mutmut_7, 
    'x__register_click_command__mutmut_8': x__register_click_command__mutmut_8, 
    'x__register_click_command__mutmut_9': x__register_click_command__mutmut_9, 
    'x__register_click_command__mutmut_10': x__register_click_command__mutmut_10, 
    'x__register_click_command__mutmut_11': x__register_click_command__mutmut_11, 
    'x__register_click_command__mutmut_12': x__register_click_command__mutmut_12, 
    'x__register_click_command__mutmut_13': x__register_click_command__mutmut_13, 
    'x__register_click_command__mutmut_14': x__register_click_command__mutmut_14, 
    'x__register_click_command__mutmut_15': x__register_click_command__mutmut_15, 
    'x__register_click_command__mutmut_16': x__register_click_command__mutmut_16, 
    'x__register_click_command__mutmut_17': x__register_click_command__mutmut_17, 
    'x__register_click_command__mutmut_18': x__register_click_command__mutmut_18, 
    'x__register_click_command__mutmut_19': x__register_click_command__mutmut_19, 
    'x__register_click_command__mutmut_20': x__register_click_command__mutmut_20, 
    'x__register_click_command__mutmut_21': x__register_click_command__mutmut_21, 
    'x__register_click_command__mutmut_22': x__register_click_command__mutmut_22, 
    'x__register_click_command__mutmut_23': x__register_click_command__mutmut_23, 
    'x__register_click_command__mutmut_24': x__register_click_command__mutmut_24, 
    'x__register_click_command__mutmut_25': x__register_click_command__mutmut_25, 
    'x__register_click_command__mutmut_26': x__register_click_command__mutmut_26, 
    'x__register_click_command__mutmut_27': x__register_click_command__mutmut_27, 
    'x__register_click_command__mutmut_28': x__register_click_command__mutmut_28, 
    'x__register_click_command__mutmut_29': x__register_click_command__mutmut_29, 
    'x__register_click_command__mutmut_30': x__register_click_command__mutmut_30
}

def _register_click_command(*args, **kwargs):
    result = _mutmut_trampoline(x__register_click_command__mutmut_orig, x__register_click_command__mutmut_mutants, args, kwargs)
    return result 

_register_click_command.__signature__ = _mutmut_signature(x__register_click_command__mutmut_orig)
x__register_click_command__mutmut_orig.__name__ = 'x__register_click_command'


def x__register_typer_app__mutmut_orig(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_1(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name not in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_2(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is not None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_3(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = None
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_4(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(None)
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_5(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(None, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_6(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, None, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_7(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, None))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_8(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_9(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_10(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, ))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_11(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = None
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_12(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(None)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_13(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = None
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_14(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(None, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_15(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, None)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_16(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_17(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, )
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_18(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = None
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_19(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(None)
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_20(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(None, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_21(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, None, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_22(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, None))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_23(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_24(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_25(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, ))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_26(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = None
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_27(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(None)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_28(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text or not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_29(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_30(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(None, "help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_31(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, None, None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_32(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr("help", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_33(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_34(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", ):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_35(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "XXhelpXX", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_36(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "HELP", None):
        command.help = help_text
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_37(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = None
    group.add_command(command, name=name)


def x__register_typer_app__mutmut_38(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(None, name=name)


def x__register_typer_app__mutmut_39(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, name=None)


def x__register_typer_app__mutmut_40(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(name=name)


def x__register_typer_app__mutmut_41(
    group: click.Group,
    name: str,
    module_path: str,
    attr: str,
    help_text: str | None = None,
) -> None:
    """Attach a Typer app under ``group`` if dependencies are present."""

    if name in group.commands:
        return
    if _typer_get_command is None:  # pragma: no cover - Typer missing
        message = f"{name} command unavailable: Typer is not installed"
        group.add_command(_missing_command(name, message, help_text))
        return
    try:
        module = importlib.import_module(module_path)
        app = getattr(module, attr)
    except Exception as exc:  # pragma: no cover - optional dependency path
        message = f"{name} command unavailable: {exc}"
        group.add_command(_missing_command(name, message, help_text))
        return
    command = _typer_get_command(app)
    if help_text and not getattr(command, "help", None):
        command.help = help_text
    group.add_command(command, )

x__register_typer_app__mutmut_mutants : ClassVar[MutantDict] = {
'x__register_typer_app__mutmut_1': x__register_typer_app__mutmut_1, 
    'x__register_typer_app__mutmut_2': x__register_typer_app__mutmut_2, 
    'x__register_typer_app__mutmut_3': x__register_typer_app__mutmut_3, 
    'x__register_typer_app__mutmut_4': x__register_typer_app__mutmut_4, 
    'x__register_typer_app__mutmut_5': x__register_typer_app__mutmut_5, 
    'x__register_typer_app__mutmut_6': x__register_typer_app__mutmut_6, 
    'x__register_typer_app__mutmut_7': x__register_typer_app__mutmut_7, 
    'x__register_typer_app__mutmut_8': x__register_typer_app__mutmut_8, 
    'x__register_typer_app__mutmut_9': x__register_typer_app__mutmut_9, 
    'x__register_typer_app__mutmut_10': x__register_typer_app__mutmut_10, 
    'x__register_typer_app__mutmut_11': x__register_typer_app__mutmut_11, 
    'x__register_typer_app__mutmut_12': x__register_typer_app__mutmut_12, 
    'x__register_typer_app__mutmut_13': x__register_typer_app__mutmut_13, 
    'x__register_typer_app__mutmut_14': x__register_typer_app__mutmut_14, 
    'x__register_typer_app__mutmut_15': x__register_typer_app__mutmut_15, 
    'x__register_typer_app__mutmut_16': x__register_typer_app__mutmut_16, 
    'x__register_typer_app__mutmut_17': x__register_typer_app__mutmut_17, 
    'x__register_typer_app__mutmut_18': x__register_typer_app__mutmut_18, 
    'x__register_typer_app__mutmut_19': x__register_typer_app__mutmut_19, 
    'x__register_typer_app__mutmut_20': x__register_typer_app__mutmut_20, 
    'x__register_typer_app__mutmut_21': x__register_typer_app__mutmut_21, 
    'x__register_typer_app__mutmut_22': x__register_typer_app__mutmut_22, 
    'x__register_typer_app__mutmut_23': x__register_typer_app__mutmut_23, 
    'x__register_typer_app__mutmut_24': x__register_typer_app__mutmut_24, 
    'x__register_typer_app__mutmut_25': x__register_typer_app__mutmut_25, 
    'x__register_typer_app__mutmut_26': x__register_typer_app__mutmut_26, 
    'x__register_typer_app__mutmut_27': x__register_typer_app__mutmut_27, 
    'x__register_typer_app__mutmut_28': x__register_typer_app__mutmut_28, 
    'x__register_typer_app__mutmut_29': x__register_typer_app__mutmut_29, 
    'x__register_typer_app__mutmut_30': x__register_typer_app__mutmut_30, 
    'x__register_typer_app__mutmut_31': x__register_typer_app__mutmut_31, 
    'x__register_typer_app__mutmut_32': x__register_typer_app__mutmut_32, 
    'x__register_typer_app__mutmut_33': x__register_typer_app__mutmut_33, 
    'x__register_typer_app__mutmut_34': x__register_typer_app__mutmut_34, 
    'x__register_typer_app__mutmut_35': x__register_typer_app__mutmut_35, 
    'x__register_typer_app__mutmut_36': x__register_typer_app__mutmut_36, 
    'x__register_typer_app__mutmut_37': x__register_typer_app__mutmut_37, 
    'x__register_typer_app__mutmut_38': x__register_typer_app__mutmut_38, 
    'x__register_typer_app__mutmut_39': x__register_typer_app__mutmut_39, 
    'x__register_typer_app__mutmut_40': x__register_typer_app__mutmut_40, 
    'x__register_typer_app__mutmut_41': x__register_typer_app__mutmut_41
}

def _register_typer_app(*args, **kwargs):
    result = _mutmut_trampoline(x__register_typer_app__mutmut_orig, x__register_typer_app__mutmut_mutants, args, kwargs)
    return result 

_register_typer_app.__signature__ = _mutmut_signature(x__register_typer_app__mutmut_orig)
x__register_typer_app__mutmut_orig.__name__ = 'x__register_typer_app'


_CLI_HELP = (
    "Codex CLI entry point.\n\n"
    "This Click facade exposes the curated maintenance helpers that back the"
    " `tasks` and `run` commands (see `ALLOWED_TASKS`) while the richer Typer"
    " applications shipped with Codex—for example the `codex-ml` console"
    " scripts—remain available for end-to-end ML workflows."
)


def x__emit_group_help__mutmut_orig(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_1(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = None
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_2(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = None

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_3(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(None)

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_4(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = None
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_5(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(None)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_6(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append(None)
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_7(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("XXXX")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_8(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append(None)
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_9(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("XXAvailable subcommands:XX")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_10(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_11(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("AVAILABLE SUBCOMMANDS:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_12(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = None
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_13(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(None, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_14(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, None)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_15(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_16(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, )
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_17(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = None
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_18(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = "XXXX"
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_19(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_20(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = None
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_21(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) and getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_22(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(None, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_23(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, None, None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_24(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr("short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_25(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_26(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", ) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_27(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "XXshort_helpXX", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_28(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "SHORT_HELP", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_29(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(None, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_30(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, None, "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_31(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", None)
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_32(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr("help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_33(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_34(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", )
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_35(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "XXhelpXX", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_36(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "HELP", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_37(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "XXXX")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_38(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = None
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_39(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(None).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_40(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[1] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_41(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else "XXXX"
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_42(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(None)
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_43(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(None)
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_44(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append(None)
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_45(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("XXXX")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_46(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append(None)

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_47(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("XXUse '<command> --help' for more details.XX")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_48(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_49(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("USE '<COMMAND> --HELP' FOR MORE DETAILS.")

    click.echo("\n".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_50(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo(None)
    ctx.exit(0)


def x__emit_group_help__mutmut_51(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(None))
    ctx.exit(0)


def x__emit_group_help__mutmut_52(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("XX\nXX".join(lines))
    ctx.exit(0)


def x__emit_group_help__mutmut_53(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(None)


def x__emit_group_help__mutmut_54(ctx: click.Context) -> None:
    """Render a short overview of available subcommands and exit cleanly."""

    command = ctx.command
    lines: list[str] = []

    if command.help:
        lines.append(command.help.strip())

    subcommands = command.list_commands(ctx)
    if subcommands:
        if lines:
            lines.append("")
        lines.append("Available subcommands:")
        for name in subcommands:
            sub_cmd = command.get_command(ctx, name)
            summary = ""
            if sub_cmd is not None:
                help_text = getattr(sub_cmd, "short_help", None) or getattr(sub_cmd, "help", "")
                summary = str(help_text).strip().splitlines()[0] if help_text else ""
            if summary:
                lines.append(f"  {name} - {summary}")
            else:
                lines.append(f"  {name}")
        lines.append("")
        lines.append("Use '<command> --help' for more details.")

    click.echo("\n".join(lines))
    ctx.exit(1)

x__emit_group_help__mutmut_mutants : ClassVar[MutantDict] = {
'x__emit_group_help__mutmut_1': x__emit_group_help__mutmut_1, 
    'x__emit_group_help__mutmut_2': x__emit_group_help__mutmut_2, 
    'x__emit_group_help__mutmut_3': x__emit_group_help__mutmut_3, 
    'x__emit_group_help__mutmut_4': x__emit_group_help__mutmut_4, 
    'x__emit_group_help__mutmut_5': x__emit_group_help__mutmut_5, 
    'x__emit_group_help__mutmut_6': x__emit_group_help__mutmut_6, 
    'x__emit_group_help__mutmut_7': x__emit_group_help__mutmut_7, 
    'x__emit_group_help__mutmut_8': x__emit_group_help__mutmut_8, 
    'x__emit_group_help__mutmut_9': x__emit_group_help__mutmut_9, 
    'x__emit_group_help__mutmut_10': x__emit_group_help__mutmut_10, 
    'x__emit_group_help__mutmut_11': x__emit_group_help__mutmut_11, 
    'x__emit_group_help__mutmut_12': x__emit_group_help__mutmut_12, 
    'x__emit_group_help__mutmut_13': x__emit_group_help__mutmut_13, 
    'x__emit_group_help__mutmut_14': x__emit_group_help__mutmut_14, 
    'x__emit_group_help__mutmut_15': x__emit_group_help__mutmut_15, 
    'x__emit_group_help__mutmut_16': x__emit_group_help__mutmut_16, 
    'x__emit_group_help__mutmut_17': x__emit_group_help__mutmut_17, 
    'x__emit_group_help__mutmut_18': x__emit_group_help__mutmut_18, 
    'x__emit_group_help__mutmut_19': x__emit_group_help__mutmut_19, 
    'x__emit_group_help__mutmut_20': x__emit_group_help__mutmut_20, 
    'x__emit_group_help__mutmut_21': x__emit_group_help__mutmut_21, 
    'x__emit_group_help__mutmut_22': x__emit_group_help__mutmut_22, 
    'x__emit_group_help__mutmut_23': x__emit_group_help__mutmut_23, 
    'x__emit_group_help__mutmut_24': x__emit_group_help__mutmut_24, 
    'x__emit_group_help__mutmut_25': x__emit_group_help__mutmut_25, 
    'x__emit_group_help__mutmut_26': x__emit_group_help__mutmut_26, 
    'x__emit_group_help__mutmut_27': x__emit_group_help__mutmut_27, 
    'x__emit_group_help__mutmut_28': x__emit_group_help__mutmut_28, 
    'x__emit_group_help__mutmut_29': x__emit_group_help__mutmut_29, 
    'x__emit_group_help__mutmut_30': x__emit_group_help__mutmut_30, 
    'x__emit_group_help__mutmut_31': x__emit_group_help__mutmut_31, 
    'x__emit_group_help__mutmut_32': x__emit_group_help__mutmut_32, 
    'x__emit_group_help__mutmut_33': x__emit_group_help__mutmut_33, 
    'x__emit_group_help__mutmut_34': x__emit_group_help__mutmut_34, 
    'x__emit_group_help__mutmut_35': x__emit_group_help__mutmut_35, 
    'x__emit_group_help__mutmut_36': x__emit_group_help__mutmut_36, 
    'x__emit_group_help__mutmut_37': x__emit_group_help__mutmut_37, 
    'x__emit_group_help__mutmut_38': x__emit_group_help__mutmut_38, 
    'x__emit_group_help__mutmut_39': x__emit_group_help__mutmut_39, 
    'x__emit_group_help__mutmut_40': x__emit_group_help__mutmut_40, 
    'x__emit_group_help__mutmut_41': x__emit_group_help__mutmut_41, 
    'x__emit_group_help__mutmut_42': x__emit_group_help__mutmut_42, 
    'x__emit_group_help__mutmut_43': x__emit_group_help__mutmut_43, 
    'x__emit_group_help__mutmut_44': x__emit_group_help__mutmut_44, 
    'x__emit_group_help__mutmut_45': x__emit_group_help__mutmut_45, 
    'x__emit_group_help__mutmut_46': x__emit_group_help__mutmut_46, 
    'x__emit_group_help__mutmut_47': x__emit_group_help__mutmut_47, 
    'x__emit_group_help__mutmut_48': x__emit_group_help__mutmut_48, 
    'x__emit_group_help__mutmut_49': x__emit_group_help__mutmut_49, 
    'x__emit_group_help__mutmut_50': x__emit_group_help__mutmut_50, 
    'x__emit_group_help__mutmut_51': x__emit_group_help__mutmut_51, 
    'x__emit_group_help__mutmut_52': x__emit_group_help__mutmut_52, 
    'x__emit_group_help__mutmut_53': x__emit_group_help__mutmut_53, 
    'x__emit_group_help__mutmut_54': x__emit_group_help__mutmut_54
}

def _emit_group_help(*args, **kwargs):
    result = _mutmut_trampoline(x__emit_group_help__mutmut_orig, x__emit_group_help__mutmut_mutants, args, kwargs)
    return result 

_emit_group_help.__signature__ = _mutmut_signature(x__emit_group_help__mutmut_orig)
x__emit_group_help__mutmut_orig.__name__ = 'x__emit_group_help'


@click.group(invoke_without_command=True, help=_CLI_HELP)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Codex CLI entry point bridging Click groups and Typer apps.

    The available subcommands intentionally mirror :data:`ALLOWED_TASKS` so
    that ``codex tasks`` lists the same curated helpers that ``codex run``
    executes.
    """

    if ctx.invoked_subcommand or ctx.resilient_parsing:
        return
    if ctx.args:
        args_display = " ".join(ctx.args)
        ctx.fail(f"Unexpected extra arguments: {args_display}")
    _emit_group_help(ctx)


@cli.group(
    "logs",
    invoke_without_command=True,
    help=(
        "Inspect Codex SQLite logs.\n\n"
        "These Click wrappers surface quick summaries while the Typer-based"
        " logging console scripts (for example `python -m codex.logging.viewer`)"
        " remain the primary interface for deep-dive workflows."
    ),
)
@click.pass_context
def logs(ctx: click.Context) -> None:
    """Codex logs (local SQLite data store) Click group.

    The subcommands complement the richer Typer logging utilities so users can
    quickly inspect the same datasets that power :mod:`codex.logging`.
    """

    if ctx.invoked_subcommand or ctx.resilient_parsing:
        return
    if ctx.args:
        args_display = " ".join(ctx.args)
        ctx.fail(f"Unexpected extra arguments: {args_display}")
    _emit_group_help(ctx)


@logs.command("init")
@click.option("--db", default=".codex/codex.sqlite", help="DB path")
def logs_init(db: str) -> None:
    """Initialize SQLite schema for logs."""
    script = TOOLS_DIR / "codex_db.py"
    try:
        subprocess.run([sys.executable, str(script), "--init", "--db", db], check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"Failed to init logs DB: {exc}", err=True)
        _log_error("STEP logs_init", "codex_db --init", str(exc), f"db={db}")
        sys.exit(1)


@logs.command("ingest")
@click.option("--changes", type=click.Path(exists=True), help=".codex/change_log.md")
@click.option("--results", type=click.Path(exists=True), help=".codex/results.md")
@click.option("--branch", default="unknown")
@click.option("--db", default=".codex/codex.sqlite")
def logs_ingest(changes, results, branch: str, db: str) -> None:
    """Ingest markdown logs into SQLite."""
    script = TOOLS_DIR / "codex_ingest_md.py"
    args = [sys.executable, str(script), "--db", db]
    if changes:
        args += ["--changes", changes, "--branch", branch]
    if results:
        args += ["--results", results]
    try:
        subprocess.run(args, check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"Failed to ingest logs: {exc}", err=True)
        _log_error("STEP logs_ingest", "codex_ingest_md", str(exc), f"db={db}")
        sys.exit(1)


@logs.command("query")
@click.option("--sql", required=True, help="SQL query to run")
@click.option("--db", default=".codex/codex.sqlite")
def logs_query(sql: str, db: str) -> None:
    """Query the SQLite logs database."""
    script = TOOLS_DIR / "codex_db.py"
    args = [sys.executable, str(script), "--db", db, "--query", sql]
    try:
        subprocess.run(args, check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"Failed to query logs: {exc}", err=True)
        _log_error("STEP logs_query", "codex_db --query", str(exc), f"db={db}")
        sys.exit(1)


@cli.command("train", context_settings={"ignore_unknown_options": True})
@click.option(
    "--engine",
    type=click.Choice(["hf_trainer", "hf", "custom"]),
    default="hf_trainer",
    help="Training engine to use (hf_trainer/hf or custom).",
)
@click.argument("engine_args", nargs=-1)
def train_cmd(engine: str, engine_args: tuple[str, ...]) -> None:
    """Train a model with the selected engine.

    Any additional arguments after ``--engine`` are forwarded directly to the
    underlying engine entry point.
    """
    from codex_ml.utils.repro import set_reproducible

    set_reproducible()
    if engine in {"hf_trainer", "hf"}:
        from src.training.engine_hf_trainer import build_parser, run_hf_trainer

        parser = build_parser()
        parser.add_argument("--texts", nargs="+", required=True)
        parser.add_argument("--output-dir", type=Path, default=Path("training_runs"))
        parser.add_argument("--val-texts", nargs="*", default=None)
        parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
        parser.add_argument("--precision", choices=["fp32", "fp16", "bf16"], default=None)
        parser.add_argument("--lora-r", type=int, default=0, help="LoRA rank; set >0 to enable")
        parser.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha scaling")
        parser.add_argument(
            "--lora-dropout", type=float, default=0.0, help="LoRA dropout probability"
        )
        parser.add_argument(
            "--lora-task-type",
            type=str,
            default=None,
            help="LoRA task type (defaults to CAUSAL_LM)",
        )
        parser.add_argument("--seed", type=int, default=0)
        parser.add_argument(
            "--config-path",
            type=Path,
            default=None,
            help="Optional training config file (JSON/YAML) to snapshot into resume manifests.",
        )

        args = parser.parse_args(list(engine_args))
        kw: dict[str, object] = {
            "val_texts": args.val_texts,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "precision": args.precision,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "lora_task_type": args.lora_task_type,
            "seed": args.seed,
        }

        hydra_cfg: dict[str, object] = {}
        defaults = {
            "gradient_accumulation_steps": parser.get_default("gradient_accumulation_steps"),
            "precision": parser.get_default("precision"),
            "seed": parser.get_default("seed"),
            "lora_r": parser.get_default("lora_r"),
            "lora_alpha": parser.get_default("lora_alpha"),
            "lora_dropout": parser.get_default("lora_dropout"),
            "lora_task_type": parser.get_default("lora_task_type"),
        }

        if args.gradient_accumulation_steps != defaults["gradient_accumulation_steps"]:
            hydra_cfg["gradient_accumulation_steps"] = args.gradient_accumulation_steps
        if args.precision is not None:
            hydra_cfg["precision"] = args.precision
        if args.seed != defaults["seed"]:
            hydra_cfg["seed"] = args.seed

        lora_section: dict[str, object] = {}
        if args.lora_r and args.lora_r != defaults["lora_r"]:
            lora_section["r"] = args.lora_r
        if args.lora_alpha is not None and args.lora_alpha != defaults["lora_alpha"]:
            lora_section["alpha"] = args.lora_alpha
        if args.lora_dropout and args.lora_dropout != defaults["lora_dropout"]:
            lora_section["dropout"] = args.lora_dropout
        if args.lora_task_type:
            lora_section["task_type"] = args.lora_task_type
        if lora_section:
            hydra_cfg["lora"] = lora_section
        if not hydra_cfg:
            hydra_cfg = None
        if args.config_path:
            kw["config_path"] = args.config_path
        if hydra_cfg:
            kw["hydra_cfg"] = hydra_cfg
        # Optionally forward device/dtype if parser/engine supports them
        for opt in ("device", "dtype"):
            if hasattr(args, opt):
                val = getattr(args, opt)
                if val is not None:
                    kw[opt] = val
        try:
            run_hf_trainer(args.texts, args.output_dir, **kw)
            return
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("STEP train", "run_hf_trainer", str(exc), f"texts={args.texts}")
            raise
    else:
        try:
            from codex.training import main as run_custom_train
        except Exception as exc:  # pragma: no cover - fallback path
            click.echo(f"[warn] custom engine unavailable, falling back to hf_trainer: {exc}")
            from src.training.engine_hf_trainer import run_hf_trainer

            try:
                run_hf_trainer(*engine_args)
                return
            except Exception as exc2:
                logger.debug(f"Exception: {exc2}")
                _log_error(
                    "STEP train", "fallback run_hf_trainer", str(exc2), f"args={engine_args}"
                )
                raise
        argv = ["--engine", "custom", *engine_args]
        orig_argv = sys.argv
        try:
            sys.argv = [orig_argv[0], *argv]
            run_custom_train()
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            _log_error("STEP train", "run_custom_train", str(exc), f"argv={argv}")
            raise
        finally:
            sys.argv = orig_argv


@cli.command("batch-triage")
@click.option("--issues", help="Comma-separated GitHub issue numbers")
@click.option("--from-file", type=click.Path(exists=True), help="CSV file with issue/workflow data")
@click.option("--output", type=click.Path(), default="batch_triage_report.md", help="Output file path")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON instead of markdown")
@click.option("--group-by", type=click.Choice(["root_cause", "workflow", "severity", "failure_type"]),
              default="root_cause", help="Grouping strategy")
def batch_triage(issues, from_file, output, as_json, group_by):
    """Batch triage CI/test failures with automated remediation suggestions.
    
    Examples:
        codex batch-triage --issues 2905,2906,2907,2908,2909,2910,2912,2913,2914,2915
        codex batch-triage --from-file scripts/ci/links_extraction.csv
    """
    script = Path(__file__).resolve().parent.parent.parent / "scripts" / "ci" / "batch_triage.py"
    
    args = [sys.executable, str(script), "--output", output, "--group-by", group_by]
    
    if issues:
        args.extend(["--issues", issues])
    elif from_file:
        args.extend(["--from-file", from_file])
    else:
        click.echo("Error: Must provide either --issues or --from-file", err=True)
        sys.exit(1)
    
    if as_json:
        args.append("--json")
    
    try:
        subprocess.run(args, check=True)
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"Batch triage failed: {exc}", err=True)
        _log_error("STEP batch_triage", "batch_triage.py", str(exc), "")
        sys.exit(1)


_WHITELIST_HEADER = "Whitelisted maintenance tasks:"


def x__print_task_whitelist__mutmut_orig() -> None:
    click.echo(_WHITELIST_HEADER)
    for name, (_, desc) in ALLOWED_TASKS.items():
        click.echo(f"  - {name}: {desc}")


def x__print_task_whitelist__mutmut_1() -> None:
    click.echo(None)
    for name, (_, desc) in ALLOWED_TASKS.items():
        click.echo(f"  - {name}: {desc}")


def x__print_task_whitelist__mutmut_2() -> None:
    click.echo(_WHITELIST_HEADER)
    for name, (_, desc) in ALLOWED_TASKS.items():
        click.echo(None)

x__print_task_whitelist__mutmut_mutants : ClassVar[MutantDict] = {
'x__print_task_whitelist__mutmut_1': x__print_task_whitelist__mutmut_1, 
    'x__print_task_whitelist__mutmut_2': x__print_task_whitelist__mutmut_2
}

def _print_task_whitelist(*args, **kwargs):
    result = _mutmut_trampoline(x__print_task_whitelist__mutmut_orig, x__print_task_whitelist__mutmut_mutants, args, kwargs)
    return result 

_print_task_whitelist.__signature__ = _mutmut_signature(x__print_task_whitelist__mutmut_orig)
x__print_task_whitelist__mutmut_orig.__name__ = 'x__print_task_whitelist'


@cli.command("tasks")
def list_tasks() -> None:
    """List allowed maintenance tasks."""

    _print_task_whitelist()


@cli.command("run")
@click.argument("task", required=False)
def run_task(task: str | None) -> None:
    """Run a whitelisted maintenance task by name."""
    if not task:
        _print_task_whitelist()
        click.echo("\nInvoke `codex run <task>` to execute a whitelisted task.")
        return

    if task not in ALLOWED_TASKS:
        click.echo(f"Task '{task}' is not allowed.", err=True)
        sys.exit(1)
    func = ALLOWED_TASKS[task][0]
    func()


@cli.command("resume")
@click.argument("run_dir", type=click.Path(exists=True, path_type=Path))
def resume_cmd(run_dir: Path) -> None:
    """Resume a training run by emitting the canonical configuration.

    Precedence (highest to lowest):
    1. Embedded snapshot in ``resume_manifest.json`` under ``config``.
    2. Copied config file in ``run_dir`` (``resume_config.json|yaml|yml``).
    3. ``config_path`` recorded in the manifest (absolute or relative to the run dir).
    Fails with a non-zero exit code if no configuration source is available.
    """

    manifest_path = run_dir / "resume_manifest.json"
    if not manifest_path.exists():
        click.echo(f"ERROR: resume_manifest.json not found in {run_dir}", err=True)
        raise SystemExit(2)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - robust CLI behavior
        click.echo(f"ERROR: failed to read resume_manifest.json: {exc}", err=True)
        raise SystemExit(2)

    if manifest.get("config") is not None:
        click.echo("INFO: Using config snapshot embedded in resume_manifest.json")
        click.echo(json.dumps(manifest["config"], indent=2, sort_keys=True))
        raise SystemExit(0)

    for suffix in (".json", ".yaml", ".yml"):
        candidate = run_dir / f"resume_config{suffix}"
        if candidate.exists():
            click.echo(f"INFO: Using copied config file: {candidate.name}")
            content = candidate.read_text(encoding="utf-8")
            try:
                parsed = json.loads(content)
                click.echo(json.dumps(parsed, indent=2, sort_keys=True))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                click.echo(content)
            raise SystemExit(0)

    cfg_path = manifest.get("config_path")
    if cfg_path:
        for path in (Path(cfg_path), run_dir / cfg_path):
            if path.exists():
                click.echo(f"INFO: Using config_path from manifest: {path}")
                content = path.read_text(encoding="utf-8")
                try:
                    parsed = json.loads(content)
                    click.echo(json.dumps(parsed, indent=2, sort_keys=True))
                except Exception:
                    logger.warning("Exception occurred", exc_info=True)
                    logger.warning("Exception occurred", exc_info=True)
                    click.echo(content)
                raise SystemExit(0)

    click.echo(
        "ERROR: No configuration snapshot or config_path available in resume manifest. "
        "Refusing to resume to avoid using defaults. Re-run training passing --config-path or "
        "ensure your run directory contains a resume_config.(json|yaml|yml).",
        err=True,
    )
    raise SystemExit(1)


@cli.group(
    "tokenizer",
    invoke_without_command=True,
    help=(
        "Tokenization utilities.\n\n"
        "Use these lightweight wrappers for quick checks; the richer"
        " tokenization workflows remain under `codex_ml.cli`."
    ),
)
@click.pass_context
def tokenizer_group(ctx: click.Context) -> None:
    """Tokenization utilities."""

    if ctx.invoked_subcommand or ctx.resilient_parsing or ctx.args:
        return
    _emit_group_help(ctx)


@tokenizer_group.command("encode")
@click.argument("text")
@click.option("--tokenizer", "tokenizer_path", default=None, help="Tokenizer path")
def tokenizer_encode(text: str, tokenizer_path: str | None) -> None:
    """Encode TEXT and print token ids."""
    from codex_ml.tokenization import load_tokenizer

    tk = load_tokenizer(path=tokenizer_path)
    ids = tk.encode(text)
    click.echo(" ".join(str(i) for i in ids))


@tokenizer_group.command("decode")
@click.argument("ids", nargs=-1, type=int)
@click.option("--tokenizer", "tokenizer_path", default=None, help="Tokenizer path")
def tokenizer_decode(ids: tuple[int, ...], tokenizer_path: str | None) -> None:
    """Decode integer token IDS and print text."""
    from codex_ml.tokenization import load_tokenizer

    tk = load_tokenizer(path=tokenizer_path)
    click.echo(tk.decode(list(ids)))


@tokenizer_group.command("stats")
@click.option("--tokenizer", "tokenizer_path", default=None, help="Tokenizer path")
def tokenizer_stats(tokenizer_path: str | None) -> None:
    """Show basic tokenizer statistics."""
    from codex_ml.tokenization import load_tokenizer

    tk = load_tokenizer(path=tokenizer_path)
    click.echo(f"vocab_size={tk.vocab_size}")


@cli.group(
    "repro",
    invoke_without_command=True,
    help=(
        "Reproducibility utilities.\n\n"
        "These commands offer fast local checks; training pipelines may use"
        " the lower-level modules directly for advanced workflows."
    ),
)
@click.pass_context
def repro_group(ctx: click.Context) -> None:
    """Reproducibility utilities."""

    if ctx.invoked_subcommand or ctx.resilient_parsing or ctx.args:
        return
    _emit_group_help(ctx)


@repro_group.command("seed")
@click.option("--seed", type=int, default=42, show_default=True, help="Seed value")
@click.option(
    "--out-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory to write seeds.json",
)
def repro_seed(seed: int, out_dir: Path | None) -> None:
    """Seed RNGs across libraries and optionally persist seeds.json."""
    from codex_ml.utils.checkpointing import set_seed

    set_seed(seed, out_dir)
    click.echo(f"seed={seed}")


@repro_group.command("env")
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default="env.json",
    show_default=True,
    help="Output path for environment info",
)
def repro_env(path: Path) -> None:
    """Record git commit and installed packages."""
    try:
        from codex_utils.repro import log_env_info
    except Exception as exc:  # pragma: no cover
        click.echo(f"Environment logging module unavailable: {exc}", err=True)
        sys.exit(1)

    try:
        log_env_info(path)
        click.echo(f"wrote {path}")
    except Exception as exc:  # pragma: no cover
        click.echo(f"Failed to write env info: {exc}", err=True)
        sys.exit(1)


@repro_group.command("system")
@click.option(
    "--path",
    type=click.Path(path_type=Path),
    default="system.json",
    show_default=True,
    help="Output path for system metrics",
)
def repro_system(path: Path) -> None:
    """Capture CPU/GPU system metrics."""
    from codex_ml.monitoring.codex_logging import _codex_sample_system

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_codex_sample_system()), encoding="utf-8")
    click.echo(f"wrote {path}")


def x__register_tokenizer_pipeline_commands__mutmut_orig() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name in tokenizer_group.commands:
            continue
        tokenizer_group.add_command(command, name=name)


def x__register_tokenizer_pipeline_commands__mutmut_1() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name not in tokenizer_group.commands:
            continue
        tokenizer_group.add_command(command, name=name)


def x__register_tokenizer_pipeline_commands__mutmut_2() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name in tokenizer_group.commands:
            break
        tokenizer_group.add_command(command, name=name)


def x__register_tokenizer_pipeline_commands__mutmut_3() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name in tokenizer_group.commands:
            continue
        tokenizer_group.add_command(None, name=name)


def x__register_tokenizer_pipeline_commands__mutmut_4() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name in tokenizer_group.commands:
            continue
        tokenizer_group.add_command(command, name=None)


def x__register_tokenizer_pipeline_commands__mutmut_5() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name in tokenizer_group.commands:
            continue
        tokenizer_group.add_command(name=name)


def x__register_tokenizer_pipeline_commands__mutmut_6() -> None:
    """Expose :mod:`codex_ml` tokenizer commands when available."""

    try:
        from codex_ml.cli.codex_cli import tokenizer as codex_tokenizer
    except Exception:  # pragma: no cover - optional dependency path
        return
    for name, command in codex_tokenizer.commands.items():
        if name in tokenizer_group.commands:
            continue
        tokenizer_group.add_command(command, )

x__register_tokenizer_pipeline_commands__mutmut_mutants : ClassVar[MutantDict] = {
'x__register_tokenizer_pipeline_commands__mutmut_1': x__register_tokenizer_pipeline_commands__mutmut_1, 
    'x__register_tokenizer_pipeline_commands__mutmut_2': x__register_tokenizer_pipeline_commands__mutmut_2, 
    'x__register_tokenizer_pipeline_commands__mutmut_3': x__register_tokenizer_pipeline_commands__mutmut_3, 
    'x__register_tokenizer_pipeline_commands__mutmut_4': x__register_tokenizer_pipeline_commands__mutmut_4, 
    'x__register_tokenizer_pipeline_commands__mutmut_5': x__register_tokenizer_pipeline_commands__mutmut_5, 
    'x__register_tokenizer_pipeline_commands__mutmut_6': x__register_tokenizer_pipeline_commands__mutmut_6
}

def _register_tokenizer_pipeline_commands(*args, **kwargs):
    result = _mutmut_trampoline(x__register_tokenizer_pipeline_commands__mutmut_orig, x__register_tokenizer_pipeline_commands__mutmut_mutants, args, kwargs)
    return result 

_register_tokenizer_pipeline_commands.__signature__ = _mutmut_signature(x__register_tokenizer_pipeline_commands__mutmut_orig)
x__register_tokenizer_pipeline_commands__mutmut_orig.__name__ = 'x__register_tokenizer_pipeline_commands'


def x__register_external_cli__mutmut_orig() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_1() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        None,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_2() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        None,
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_3() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        None,
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_4() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        None,
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_5() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_6() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_7() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_8() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_9() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_10() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_11() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "XXmlXX",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_12() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ML",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_13() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "XXcodex_ml.cli.codex_cliXX",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_14() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "CODEX_ML.CLI.CODEX_CLI",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_15() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "XXcodexXX",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_16() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "CODEX",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_17() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="XXCodex ML command line interface.XX",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_18() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="codex ml command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_19() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="CODEX ML COMMAND LINE INTERFACE.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_20() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        None,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_21() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        None,
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_22() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        None,
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_23() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        None,
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_24() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_25() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_26() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_27() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_28() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_29() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_30() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "XXzendeskXX",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_31() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "ZENDESK",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_32() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "XXcodex.cli_zendeskXX",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_33() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "CODEX.CLI_ZENDESK",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_34() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "XXappXX",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_35() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "APP",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_36() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="XXZendesk admin workflow commands.XX",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_37() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_38() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="ZENDESK ADMIN WORKFLOW COMMANDS.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_39() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        None,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_40() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        None,
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_41() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        None,
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_42() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        None,
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_43() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_44() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_45() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_46() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_47() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_48() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_49() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "XXd365XX",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_50() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "D365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_51() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "XXcodex.dynamics.cli_d365XX",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_52() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "CODEX.DYNAMICS.CLI_D365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_53() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "XXappXX",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_54() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "APP",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_55() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="XXDynamics 365 admin utilities.XX",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_56() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_57() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="DYNAMICS 365 ADMIN UTILITIES.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_58() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        None,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_59() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        None,
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_60() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        None,
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_61() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        None,
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_62() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text=None,
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_63() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_64() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_65() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_66() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_67() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_68() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "XXmapsXX",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_69() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "MAPS",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_70() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "XXcodex.cli_mapsXX",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_71() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "CODEX.CLI_MAPS",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_72() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "XXappXX",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_73() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "APP",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_74() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="XXInspect mapping CSV definitions.XX",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_75() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="inspect mapping csv definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_76() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="INSPECT MAPPING CSV DEFINITIONS.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_77() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        None,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_78() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        None,
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_79() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        None,
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_80() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        None,
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_81() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text=None,
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_82() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_83() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_84() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_85() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_86() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_87() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "XXarchive-legacyXX",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_88() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "ARCHIVE-LEGACY",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_89() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "XXcodex.archive.cliXX",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_90() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "CODEX.ARCHIVE.CLI",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_91() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "XXcliXX",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_92() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "CLI",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_93() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="XXCodex tombstone archive workflow (legacy Click CLI).XX",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_94() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="codex tombstone archive workflow (legacy click cli).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_95() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="CODEX TOMBSTONE ARCHIVE WORKFLOW (LEGACY CLICK CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_96() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        None,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_97() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        None,
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_98() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        None,
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_99() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        None,
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_100() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_101() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_102() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_103() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_104() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_105() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_106() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "XXarchiveXX",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_107() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "ARCHIVE",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_108() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "XXcodex.cli_archiveXX",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_109() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "CODEX.CLI_ARCHIVE",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_110() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "XXappXX",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_111() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "APP",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_112() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="XXArchive and restore code artifacts.XX",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_113() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_114() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="ARCHIVE AND RESTORE CODE ARTIFACTS.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_115() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        None,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_116() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        None,
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_117() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        None,
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_118() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        None,
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_119() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text=None,
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_120() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_121() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_122() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_123() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_124() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_125() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "XXreleaseXX",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_126() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "RELEASE",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_127() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "XXcodex.cli_releaseXX",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_128() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "CODEX.CLI_RELEASE",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_129() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "XXappXX",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_130() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "APP",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_131() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="XXOffline release pack/verify/unpack.XX",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_132() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_133() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="OFFLINE RELEASE PACK/VERIFY/UNPACK.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_134() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        None,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_135() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        None,
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_136() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        None,
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_137() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        None,
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_138() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_139() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_140() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_141() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_142() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_143() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_144() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "XXgithub-logsXX",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_145() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "GITHUB-LOGS",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_146() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "XXcodex.cli_github_logsXX",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_147() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "CODEX.CLI_GITHUB_LOGS",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_148() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "XXcliXX",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_149() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "CLI",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_150() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="XXFetch GitHub Actions logs via CLI.XX",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_151() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="fetch github actions logs via cli.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_152() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="FETCH GITHUB ACTIONS LOGS VIA CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_153() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        None,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_154() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        None,
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_155() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        None,
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_156() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        None,
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_157() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_158() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_159() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_160() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_161() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_162() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_163() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "XXknowledgeXX",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_164() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "KNOWLEDGE",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_165() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "XXcodex.cli_knowledgeXX",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_166() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "CODEX.CLI_KNOWLEDGE",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_167() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "XXappXX",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_168() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "APP",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_169() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="XXKnowledge ingest/normalize/chunk/build pipeline.XX",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_170() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_171() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="KNOWLEDGE INGEST/NORMALIZE/CHUNK/BUILD PIPELINE.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_172() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        None,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_173() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        None,
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_174() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        None,
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_175() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        None,
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_176() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_177() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_178() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_179() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_180() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_181() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_182() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "XXragXX",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_183() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "RAG",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_184() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "XXcodex.cli_ragXX",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_185() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "CODEX.CLI_RAG",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_186() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "XXappXX",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_187() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "APP",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_188() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="XXRAG index management and semantic search.XX",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_189() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="rag index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_190() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG INDEX MANAGEMENT AND SEMANTIC SEARCH.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_191() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        None,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_192() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        None,
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_193() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        None,
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_194() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        None,
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_195() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text=None,
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_196() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_197() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_198() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_199() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_200() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_201() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "XXvalidateXX",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_202() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "VALIDATE",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_203() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "XXcodex_ml.cli.validateXX",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_204() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "CODEX_ML.CLI.VALIDATE",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_205() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "XXappXX",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_206() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "APP",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_207() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="XXValidate Codex ML configuration files.XX",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_208() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="validate codex ml configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_209() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="VALIDATE CODEX ML CONFIGURATION FILES.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_210() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        None,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_211() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        None,
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_212() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        None,
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_213() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        None,
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_214() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text=None,
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_215() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_216() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_217() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_218() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_219() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_220() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "XXpluginsXX",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_221() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "PLUGINS",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_222() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "XXcodex_ml.cli.plugins_cliXX",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_223() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "CODEX_ML.CLI.PLUGINS_CLI",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_224() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "XXappXX",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_225() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "APP",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_226() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="XXInspect codex_ml plugin registries.XX",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_227() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_228() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="INSPECT CODEX_ML PLUGIN REGISTRIES.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_229() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        None,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_230() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        None,
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_231() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        None,
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_232() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        None,
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_233() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text=None,
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_234() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_235() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_236() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_237() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_238() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_239() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "XXtelemetryXX",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_240() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "TELEMETRY",
        "codex_ml.monitoring.cli",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_241() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "XXcodex_ml.monitoring.cliXX",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_242() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "CODEX_ML.MONITORING.CLI",
        "app",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_243() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "XXappXX",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_244() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "APP",
        help_text="Telemetry NDJSON utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_245() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="XXTelemetry NDJSON utilities.XX",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_246() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="telemetry ndjson utilities.",
    )
    _register_tokenizer_pipeline_commands()


def x__register_external_cli__mutmut_247() -> None:
    """Register optional CLI integrations backed by codex_ml."""

    _register_click_command(
        cli,
        "ml",
        "codex_ml.cli.codex_cli",
        "codex",
        help_text="Codex ML command line interface.",
    )
    _register_typer_app(
        cli,
        "zendesk",
        "codex.cli_zendesk",
        "app",
        help_text="Zendesk admin workflow commands.",
    )
    _register_typer_app(
        cli,
        "d365",
        "codex.dynamics.cli_d365",
        "app",
        help_text="Dynamics 365 admin utilities.",
    )
    _register_typer_app(
        cli,
        "maps",
        "codex.cli_maps",
        "app",
        help_text="Inspect mapping CSV definitions.",
    )
    _register_click_command(
        cli,
        "archive-legacy",
        "codex.archive.cli",
        "cli",
        help_text="Codex tombstone archive workflow (legacy Click CLI).",
    )
    _register_click_command(
        cli,
        "archive",
        "codex.cli_archive",
        "app",
        help_text="Archive and restore code artifacts.",
    )
    _register_typer_app(
        cli,
        "release",
        "codex.cli_release",
        "app",
        help_text="Offline release pack/verify/unpack.",
    )
    _register_click_command(
        cli,
        "github-logs",
        "codex.cli_github_logs",
        "cli",
        help_text="Fetch GitHub Actions logs via CLI.",
    )
    _register_typer_app(
        cli,
        "knowledge",
        "codex.cli_knowledge",
        "app",
        help_text="Knowledge ingest/normalize/chunk/build pipeline.",
    )
    _register_typer_app(
        cli,
        "rag",
        "codex.cli_rag",
        "app",
        help_text="RAG index management and semantic search.",
    )
    _register_typer_app(
        cli,
        "validate",
        "codex_ml.cli.validate",
        "app",
        help_text="Validate Codex ML configuration files.",
    )
    _register_typer_app(
        cli,
        "plugins",
        "codex_ml.cli.plugins_cli",
        "app",
        help_text="Inspect codex_ml plugin registries.",
    )
    _register_typer_app(
        logs,
        "telemetry",
        "codex_ml.monitoring.cli",
        "app",
        help_text="TELEMETRY NDJSON UTILITIES.",
    )
    _register_tokenizer_pipeline_commands()

x__register_external_cli__mutmut_mutants : ClassVar[MutantDict] = {
'x__register_external_cli__mutmut_1': x__register_external_cli__mutmut_1, 
    'x__register_external_cli__mutmut_2': x__register_external_cli__mutmut_2, 
    'x__register_external_cli__mutmut_3': x__register_external_cli__mutmut_3, 
    'x__register_external_cli__mutmut_4': x__register_external_cli__mutmut_4, 
    'x__register_external_cli__mutmut_5': x__register_external_cli__mutmut_5, 
    'x__register_external_cli__mutmut_6': x__register_external_cli__mutmut_6, 
    'x__register_external_cli__mutmut_7': x__register_external_cli__mutmut_7, 
    'x__register_external_cli__mutmut_8': x__register_external_cli__mutmut_8, 
    'x__register_external_cli__mutmut_9': x__register_external_cli__mutmut_9, 
    'x__register_external_cli__mutmut_10': x__register_external_cli__mutmut_10, 
    'x__register_external_cli__mutmut_11': x__register_external_cli__mutmut_11, 
    'x__register_external_cli__mutmut_12': x__register_external_cli__mutmut_12, 
    'x__register_external_cli__mutmut_13': x__register_external_cli__mutmut_13, 
    'x__register_external_cli__mutmut_14': x__register_external_cli__mutmut_14, 
    'x__register_external_cli__mutmut_15': x__register_external_cli__mutmut_15, 
    'x__register_external_cli__mutmut_16': x__register_external_cli__mutmut_16, 
    'x__register_external_cli__mutmut_17': x__register_external_cli__mutmut_17, 
    'x__register_external_cli__mutmut_18': x__register_external_cli__mutmut_18, 
    'x__register_external_cli__mutmut_19': x__register_external_cli__mutmut_19, 
    'x__register_external_cli__mutmut_20': x__register_external_cli__mutmut_20, 
    'x__register_external_cli__mutmut_21': x__register_external_cli__mutmut_21, 
    'x__register_external_cli__mutmut_22': x__register_external_cli__mutmut_22, 
    'x__register_external_cli__mutmut_23': x__register_external_cli__mutmut_23, 
    'x__register_external_cli__mutmut_24': x__register_external_cli__mutmut_24, 
    'x__register_external_cli__mutmut_25': x__register_external_cli__mutmut_25, 
    'x__register_external_cli__mutmut_26': x__register_external_cli__mutmut_26, 
    'x__register_external_cli__mutmut_27': x__register_external_cli__mutmut_27, 
    'x__register_external_cli__mutmut_28': x__register_external_cli__mutmut_28, 
    'x__register_external_cli__mutmut_29': x__register_external_cli__mutmut_29, 
    'x__register_external_cli__mutmut_30': x__register_external_cli__mutmut_30, 
    'x__register_external_cli__mutmut_31': x__register_external_cli__mutmut_31, 
    'x__register_external_cli__mutmut_32': x__register_external_cli__mutmut_32, 
    'x__register_external_cli__mutmut_33': x__register_external_cli__mutmut_33, 
    'x__register_external_cli__mutmut_34': x__register_external_cli__mutmut_34, 
    'x__register_external_cli__mutmut_35': x__register_external_cli__mutmut_35, 
    'x__register_external_cli__mutmut_36': x__register_external_cli__mutmut_36, 
    'x__register_external_cli__mutmut_37': x__register_external_cli__mutmut_37, 
    'x__register_external_cli__mutmut_38': x__register_external_cli__mutmut_38, 
    'x__register_external_cli__mutmut_39': x__register_external_cli__mutmut_39, 
    'x__register_external_cli__mutmut_40': x__register_external_cli__mutmut_40, 
    'x__register_external_cli__mutmut_41': x__register_external_cli__mutmut_41, 
    'x__register_external_cli__mutmut_42': x__register_external_cli__mutmut_42, 
    'x__register_external_cli__mutmut_43': x__register_external_cli__mutmut_43, 
    'x__register_external_cli__mutmut_44': x__register_external_cli__mutmut_44, 
    'x__register_external_cli__mutmut_45': x__register_external_cli__mutmut_45, 
    'x__register_external_cli__mutmut_46': x__register_external_cli__mutmut_46, 
    'x__register_external_cli__mutmut_47': x__register_external_cli__mutmut_47, 
    'x__register_external_cli__mutmut_48': x__register_external_cli__mutmut_48, 
    'x__register_external_cli__mutmut_49': x__register_external_cli__mutmut_49, 
    'x__register_external_cli__mutmut_50': x__register_external_cli__mutmut_50, 
    'x__register_external_cli__mutmut_51': x__register_external_cli__mutmut_51, 
    'x__register_external_cli__mutmut_52': x__register_external_cli__mutmut_52, 
    'x__register_external_cli__mutmut_53': x__register_external_cli__mutmut_53, 
    'x__register_external_cli__mutmut_54': x__register_external_cli__mutmut_54, 
    'x__register_external_cli__mutmut_55': x__register_external_cli__mutmut_55, 
    'x__register_external_cli__mutmut_56': x__register_external_cli__mutmut_56, 
    'x__register_external_cli__mutmut_57': x__register_external_cli__mutmut_57, 
    'x__register_external_cli__mutmut_58': x__register_external_cli__mutmut_58, 
    'x__register_external_cli__mutmut_59': x__register_external_cli__mutmut_59, 
    'x__register_external_cli__mutmut_60': x__register_external_cli__mutmut_60, 
    'x__register_external_cli__mutmut_61': x__register_external_cli__mutmut_61, 
    'x__register_external_cli__mutmut_62': x__register_external_cli__mutmut_62, 
    'x__register_external_cli__mutmut_63': x__register_external_cli__mutmut_63, 
    'x__register_external_cli__mutmut_64': x__register_external_cli__mutmut_64, 
    'x__register_external_cli__mutmut_65': x__register_external_cli__mutmut_65, 
    'x__register_external_cli__mutmut_66': x__register_external_cli__mutmut_66, 
    'x__register_external_cli__mutmut_67': x__register_external_cli__mutmut_67, 
    'x__register_external_cli__mutmut_68': x__register_external_cli__mutmut_68, 
    'x__register_external_cli__mutmut_69': x__register_external_cli__mutmut_69, 
    'x__register_external_cli__mutmut_70': x__register_external_cli__mutmut_70, 
    'x__register_external_cli__mutmut_71': x__register_external_cli__mutmut_71, 
    'x__register_external_cli__mutmut_72': x__register_external_cli__mutmut_72, 
    'x__register_external_cli__mutmut_73': x__register_external_cli__mutmut_73, 
    'x__register_external_cli__mutmut_74': x__register_external_cli__mutmut_74, 
    'x__register_external_cli__mutmut_75': x__register_external_cli__mutmut_75, 
    'x__register_external_cli__mutmut_76': x__register_external_cli__mutmut_76, 
    'x__register_external_cli__mutmut_77': x__register_external_cli__mutmut_77, 
    'x__register_external_cli__mutmut_78': x__register_external_cli__mutmut_78, 
    'x__register_external_cli__mutmut_79': x__register_external_cli__mutmut_79, 
    'x__register_external_cli__mutmut_80': x__register_external_cli__mutmut_80, 
    'x__register_external_cli__mutmut_81': x__register_external_cli__mutmut_81, 
    'x__register_external_cli__mutmut_82': x__register_external_cli__mutmut_82, 
    'x__register_external_cli__mutmut_83': x__register_external_cli__mutmut_83, 
    'x__register_external_cli__mutmut_84': x__register_external_cli__mutmut_84, 
    'x__register_external_cli__mutmut_85': x__register_external_cli__mutmut_85, 
    'x__register_external_cli__mutmut_86': x__register_external_cli__mutmut_86, 
    'x__register_external_cli__mutmut_87': x__register_external_cli__mutmut_87, 
    'x__register_external_cli__mutmut_88': x__register_external_cli__mutmut_88, 
    'x__register_external_cli__mutmut_89': x__register_external_cli__mutmut_89, 
    'x__register_external_cli__mutmut_90': x__register_external_cli__mutmut_90, 
    'x__register_external_cli__mutmut_91': x__register_external_cli__mutmut_91, 
    'x__register_external_cli__mutmut_92': x__register_external_cli__mutmut_92, 
    'x__register_external_cli__mutmut_93': x__register_external_cli__mutmut_93, 
    'x__register_external_cli__mutmut_94': x__register_external_cli__mutmut_94, 
    'x__register_external_cli__mutmut_95': x__register_external_cli__mutmut_95, 
    'x__register_external_cli__mutmut_96': x__register_external_cli__mutmut_96, 
    'x__register_external_cli__mutmut_97': x__register_external_cli__mutmut_97, 
    'x__register_external_cli__mutmut_98': x__register_external_cli__mutmut_98, 
    'x__register_external_cli__mutmut_99': x__register_external_cli__mutmut_99, 
    'x__register_external_cli__mutmut_100': x__register_external_cli__mutmut_100, 
    'x__register_external_cli__mutmut_101': x__register_external_cli__mutmut_101, 
    'x__register_external_cli__mutmut_102': x__register_external_cli__mutmut_102, 
    'x__register_external_cli__mutmut_103': x__register_external_cli__mutmut_103, 
    'x__register_external_cli__mutmut_104': x__register_external_cli__mutmut_104, 
    'x__register_external_cli__mutmut_105': x__register_external_cli__mutmut_105, 
    'x__register_external_cli__mutmut_106': x__register_external_cli__mutmut_106, 
    'x__register_external_cli__mutmut_107': x__register_external_cli__mutmut_107, 
    'x__register_external_cli__mutmut_108': x__register_external_cli__mutmut_108, 
    'x__register_external_cli__mutmut_109': x__register_external_cli__mutmut_109, 
    'x__register_external_cli__mutmut_110': x__register_external_cli__mutmut_110, 
    'x__register_external_cli__mutmut_111': x__register_external_cli__mutmut_111, 
    'x__register_external_cli__mutmut_112': x__register_external_cli__mutmut_112, 
    'x__register_external_cli__mutmut_113': x__register_external_cli__mutmut_113, 
    'x__register_external_cli__mutmut_114': x__register_external_cli__mutmut_114, 
    'x__register_external_cli__mutmut_115': x__register_external_cli__mutmut_115, 
    'x__register_external_cli__mutmut_116': x__register_external_cli__mutmut_116, 
    'x__register_external_cli__mutmut_117': x__register_external_cli__mutmut_117, 
    'x__register_external_cli__mutmut_118': x__register_external_cli__mutmut_118, 
    'x__register_external_cli__mutmut_119': x__register_external_cli__mutmut_119, 
    'x__register_external_cli__mutmut_120': x__register_external_cli__mutmut_120, 
    'x__register_external_cli__mutmut_121': x__register_external_cli__mutmut_121, 
    'x__register_external_cli__mutmut_122': x__register_external_cli__mutmut_122, 
    'x__register_external_cli__mutmut_123': x__register_external_cli__mutmut_123, 
    'x__register_external_cli__mutmut_124': x__register_external_cli__mutmut_124, 
    'x__register_external_cli__mutmut_125': x__register_external_cli__mutmut_125, 
    'x__register_external_cli__mutmut_126': x__register_external_cli__mutmut_126, 
    'x__register_external_cli__mutmut_127': x__register_external_cli__mutmut_127, 
    'x__register_external_cli__mutmut_128': x__register_external_cli__mutmut_128, 
    'x__register_external_cli__mutmut_129': x__register_external_cli__mutmut_129, 
    'x__register_external_cli__mutmut_130': x__register_external_cli__mutmut_130, 
    'x__register_external_cli__mutmut_131': x__register_external_cli__mutmut_131, 
    'x__register_external_cli__mutmut_132': x__register_external_cli__mutmut_132, 
    'x__register_external_cli__mutmut_133': x__register_external_cli__mutmut_133, 
    'x__register_external_cli__mutmut_134': x__register_external_cli__mutmut_134, 
    'x__register_external_cli__mutmut_135': x__register_external_cli__mutmut_135, 
    'x__register_external_cli__mutmut_136': x__register_external_cli__mutmut_136, 
    'x__register_external_cli__mutmut_137': x__register_external_cli__mutmut_137, 
    'x__register_external_cli__mutmut_138': x__register_external_cli__mutmut_138, 
    'x__register_external_cli__mutmut_139': x__register_external_cli__mutmut_139, 
    'x__register_external_cli__mutmut_140': x__register_external_cli__mutmut_140, 
    'x__register_external_cli__mutmut_141': x__register_external_cli__mutmut_141, 
    'x__register_external_cli__mutmut_142': x__register_external_cli__mutmut_142, 
    'x__register_external_cli__mutmut_143': x__register_external_cli__mutmut_143, 
    'x__register_external_cli__mutmut_144': x__register_external_cli__mutmut_144, 
    'x__register_external_cli__mutmut_145': x__register_external_cli__mutmut_145, 
    'x__register_external_cli__mutmut_146': x__register_external_cli__mutmut_146, 
    'x__register_external_cli__mutmut_147': x__register_external_cli__mutmut_147, 
    'x__register_external_cli__mutmut_148': x__register_external_cli__mutmut_148, 
    'x__register_external_cli__mutmut_149': x__register_external_cli__mutmut_149, 
    'x__register_external_cli__mutmut_150': x__register_external_cli__mutmut_150, 
    'x__register_external_cli__mutmut_151': x__register_external_cli__mutmut_151, 
    'x__register_external_cli__mutmut_152': x__register_external_cli__mutmut_152, 
    'x__register_external_cli__mutmut_153': x__register_external_cli__mutmut_153, 
    'x__register_external_cli__mutmut_154': x__register_external_cli__mutmut_154, 
    'x__register_external_cli__mutmut_155': x__register_external_cli__mutmut_155, 
    'x__register_external_cli__mutmut_156': x__register_external_cli__mutmut_156, 
    'x__register_external_cli__mutmut_157': x__register_external_cli__mutmut_157, 
    'x__register_external_cli__mutmut_158': x__register_external_cli__mutmut_158, 
    'x__register_external_cli__mutmut_159': x__register_external_cli__mutmut_159, 
    'x__register_external_cli__mutmut_160': x__register_external_cli__mutmut_160, 
    'x__register_external_cli__mutmut_161': x__register_external_cli__mutmut_161, 
    'x__register_external_cli__mutmut_162': x__register_external_cli__mutmut_162, 
    'x__register_external_cli__mutmut_163': x__register_external_cli__mutmut_163, 
    'x__register_external_cli__mutmut_164': x__register_external_cli__mutmut_164, 
    'x__register_external_cli__mutmut_165': x__register_external_cli__mutmut_165, 
    'x__register_external_cli__mutmut_166': x__register_external_cli__mutmut_166, 
    'x__register_external_cli__mutmut_167': x__register_external_cli__mutmut_167, 
    'x__register_external_cli__mutmut_168': x__register_external_cli__mutmut_168, 
    'x__register_external_cli__mutmut_169': x__register_external_cli__mutmut_169, 
    'x__register_external_cli__mutmut_170': x__register_external_cli__mutmut_170, 
    'x__register_external_cli__mutmut_171': x__register_external_cli__mutmut_171, 
    'x__register_external_cli__mutmut_172': x__register_external_cli__mutmut_172, 
    'x__register_external_cli__mutmut_173': x__register_external_cli__mutmut_173, 
    'x__register_external_cli__mutmut_174': x__register_external_cli__mutmut_174, 
    'x__register_external_cli__mutmut_175': x__register_external_cli__mutmut_175, 
    'x__register_external_cli__mutmut_176': x__register_external_cli__mutmut_176, 
    'x__register_external_cli__mutmut_177': x__register_external_cli__mutmut_177, 
    'x__register_external_cli__mutmut_178': x__register_external_cli__mutmut_178, 
    'x__register_external_cli__mutmut_179': x__register_external_cli__mutmut_179, 
    'x__register_external_cli__mutmut_180': x__register_external_cli__mutmut_180, 
    'x__register_external_cli__mutmut_181': x__register_external_cli__mutmut_181, 
    'x__register_external_cli__mutmut_182': x__register_external_cli__mutmut_182, 
    'x__register_external_cli__mutmut_183': x__register_external_cli__mutmut_183, 
    'x__register_external_cli__mutmut_184': x__register_external_cli__mutmut_184, 
    'x__register_external_cli__mutmut_185': x__register_external_cli__mutmut_185, 
    'x__register_external_cli__mutmut_186': x__register_external_cli__mutmut_186, 
    'x__register_external_cli__mutmut_187': x__register_external_cli__mutmut_187, 
    'x__register_external_cli__mutmut_188': x__register_external_cli__mutmut_188, 
    'x__register_external_cli__mutmut_189': x__register_external_cli__mutmut_189, 
    'x__register_external_cli__mutmut_190': x__register_external_cli__mutmut_190, 
    'x__register_external_cli__mutmut_191': x__register_external_cli__mutmut_191, 
    'x__register_external_cli__mutmut_192': x__register_external_cli__mutmut_192, 
    'x__register_external_cli__mutmut_193': x__register_external_cli__mutmut_193, 
    'x__register_external_cli__mutmut_194': x__register_external_cli__mutmut_194, 
    'x__register_external_cli__mutmut_195': x__register_external_cli__mutmut_195, 
    'x__register_external_cli__mutmut_196': x__register_external_cli__mutmut_196, 
    'x__register_external_cli__mutmut_197': x__register_external_cli__mutmut_197, 
    'x__register_external_cli__mutmut_198': x__register_external_cli__mutmut_198, 
    'x__register_external_cli__mutmut_199': x__register_external_cli__mutmut_199, 
    'x__register_external_cli__mutmut_200': x__register_external_cli__mutmut_200, 
    'x__register_external_cli__mutmut_201': x__register_external_cli__mutmut_201, 
    'x__register_external_cli__mutmut_202': x__register_external_cli__mutmut_202, 
    'x__register_external_cli__mutmut_203': x__register_external_cli__mutmut_203, 
    'x__register_external_cli__mutmut_204': x__register_external_cli__mutmut_204, 
    'x__register_external_cli__mutmut_205': x__register_external_cli__mutmut_205, 
    'x__register_external_cli__mutmut_206': x__register_external_cli__mutmut_206, 
    'x__register_external_cli__mutmut_207': x__register_external_cli__mutmut_207, 
    'x__register_external_cli__mutmut_208': x__register_external_cli__mutmut_208, 
    'x__register_external_cli__mutmut_209': x__register_external_cli__mutmut_209, 
    'x__register_external_cli__mutmut_210': x__register_external_cli__mutmut_210, 
    'x__register_external_cli__mutmut_211': x__register_external_cli__mutmut_211, 
    'x__register_external_cli__mutmut_212': x__register_external_cli__mutmut_212, 
    'x__register_external_cli__mutmut_213': x__register_external_cli__mutmut_213, 
    'x__register_external_cli__mutmut_214': x__register_external_cli__mutmut_214, 
    'x__register_external_cli__mutmut_215': x__register_external_cli__mutmut_215, 
    'x__register_external_cli__mutmut_216': x__register_external_cli__mutmut_216, 
    'x__register_external_cli__mutmut_217': x__register_external_cli__mutmut_217, 
    'x__register_external_cli__mutmut_218': x__register_external_cli__mutmut_218, 
    'x__register_external_cli__mutmut_219': x__register_external_cli__mutmut_219, 
    'x__register_external_cli__mutmut_220': x__register_external_cli__mutmut_220, 
    'x__register_external_cli__mutmut_221': x__register_external_cli__mutmut_221, 
    'x__register_external_cli__mutmut_222': x__register_external_cli__mutmut_222, 
    'x__register_external_cli__mutmut_223': x__register_external_cli__mutmut_223, 
    'x__register_external_cli__mutmut_224': x__register_external_cli__mutmut_224, 
    'x__register_external_cli__mutmut_225': x__register_external_cli__mutmut_225, 
    'x__register_external_cli__mutmut_226': x__register_external_cli__mutmut_226, 
    'x__register_external_cli__mutmut_227': x__register_external_cli__mutmut_227, 
    'x__register_external_cli__mutmut_228': x__register_external_cli__mutmut_228, 
    'x__register_external_cli__mutmut_229': x__register_external_cli__mutmut_229, 
    'x__register_external_cli__mutmut_230': x__register_external_cli__mutmut_230, 
    'x__register_external_cli__mutmut_231': x__register_external_cli__mutmut_231, 
    'x__register_external_cli__mutmut_232': x__register_external_cli__mutmut_232, 
    'x__register_external_cli__mutmut_233': x__register_external_cli__mutmut_233, 
    'x__register_external_cli__mutmut_234': x__register_external_cli__mutmut_234, 
    'x__register_external_cli__mutmut_235': x__register_external_cli__mutmut_235, 
    'x__register_external_cli__mutmut_236': x__register_external_cli__mutmut_236, 
    'x__register_external_cli__mutmut_237': x__register_external_cli__mutmut_237, 
    'x__register_external_cli__mutmut_238': x__register_external_cli__mutmut_238, 
    'x__register_external_cli__mutmut_239': x__register_external_cli__mutmut_239, 
    'x__register_external_cli__mutmut_240': x__register_external_cli__mutmut_240, 
    'x__register_external_cli__mutmut_241': x__register_external_cli__mutmut_241, 
    'x__register_external_cli__mutmut_242': x__register_external_cli__mutmut_242, 
    'x__register_external_cli__mutmut_243': x__register_external_cli__mutmut_243, 
    'x__register_external_cli__mutmut_244': x__register_external_cli__mutmut_244, 
    'x__register_external_cli__mutmut_245': x__register_external_cli__mutmut_245, 
    'x__register_external_cli__mutmut_246': x__register_external_cli__mutmut_246, 
    'x__register_external_cli__mutmut_247': x__register_external_cli__mutmut_247
}

def _register_external_cli(*args, **kwargs):
    result = _mutmut_trampoline(x__register_external_cli__mutmut_orig, x__register_external_cli__mutmut_mutants, args, kwargs)
    return result 

_register_external_cli.__signature__ = _mutmut_signature(x__register_external_cli__mutmut_orig)
x__register_external_cli__mutmut_orig.__name__ = 'x__register_external_cli'


# ==============================================================================
# AGENTS.md Infrastructure Commands
# ==============================================================================


@cli.command("session-logger")
@click.option("--session-id", help="Session ID (default: auto-generate)")
@click.option(
    "--role",
    type=click.Choice(["system", "user", "assistant", "tool"]),
    required=True,
    help="Log message role",
)
@click.option("--message", required=True, help="Log message")
def session_logger_cmd(session_id: str | None, role: str, message: str) -> None:
    """Record session events to the database.

    Examples:
        codex session-logger --role=user --message="Starting analysis"
        codex session-logger --session-id=abc --role=assistant --message="Done"
    """
    try:
        from codex.logging.error_handler import error_handler
        from codex.logging.session_logger import SessionLogger, get_session_id

        @error_handler.log_errors
        def _log() -> None:
            # Use provided session_id or auto-generate
            sid = session_id or get_session_id()
            logger = SessionLogger(session_id=sid)
            logger.log(role=role, message=message)
            click.echo(f"✅ Logged {role} message to session {logger.session_id}")

        _log()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to log message: {exc}", err=True)
        sys.exit(1)


@cli.command("viewer")
@click.option("--session-id", help="Session ID to view (default: latest)")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def viewer_cmd(session_id: str | None, output_format: str) -> None:
    """View session logs in various formats.

    Examples:
        codex viewer
        codex viewer --session-id=abc123
        codex viewer --format=json
    """
    try:
        from codex.logging.error_handler import error_handler
        from codex.logging.viewer import LogViewer

        @error_handler.log_errors
        def _view() -> None:
            viewer = LogViewer()
            viewer.view(session_id=session_id, output_format=output_format)

        _view()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to view logs: {exc}", err=True)
        sys.exit(1)


@cli.command("query-logs")
@click.option("--search", required=True, help="Search query")
@click.option("--role", help="Filter by role")
def query_logs_cmd(search: str, role: str | None) -> None:
    """Search through conversation transcripts.

    Examples:
        codex query-logs --search="error"
        codex query-logs --search="test" --role=tool
    """
    try:
        from codex.logging.error_handler import error_handler
        from codex.logging.query_logs import LogQueryEngine

        @error_handler.log_errors
        def _query() -> None:
            engine = LogQueryEngine()
            results = engine.search(query=search, role=role)

            if not results:
                click.echo("No results found")
                return

            for result in results:
                timestamp = result.get("timestamp", "unknown")
                msg_role = result.get("role", "unknown")
                msg = result.get("message", "")
                click.echo(f"\n[{timestamp}] {msg_role}: {msg}")

        _query()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to query logs: {exc}", err=True)
        sys.exit(1)


@cli.command("validate-env")
def validate_env_cmd() -> None:
    """Validate and display current environment configuration.

    Displays all CODEX_* environment variables and their values.

    Examples:
        codex validate-env
    """
    try:
        from codex.config.env_vars import env_manager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _validate() -> None:
            config = env_manager.dump_config()

            click.echo("📊 Current Environment Configuration:\n")
            for var, value in config.items():
                display_value = value if value else "<not set>"
                click.echo(f"  {var}: {display_value}")

            click.echo("\n✅ Environment validation passed")

        _validate()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Environment validation failed: {exc}", err=True)
        sys.exit(1)


@cli.command("init-db")
@click.option(
    "--db-path",
    help="Database path (default: from env or .codex/session_logs.db)",
)
def init_db_cmd(db_path: str | None) -> None:
    """Initialize the session logging database.

    Creates the database schema and tables if they don't exist.

    Examples:
        codex init-db
        codex init-db --db-path=.codex/custom.db
    """
    try:
        from pathlib import Path

        from codex.logging.db_manager import DBManager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _init() -> None:
            db_path_obj = Path(db_path) if db_path else None
            manager = DBManager(db_path=db_path_obj)

            click.echo(f"Initializing database: {manager.db_path}")
            manager.init_schema()
            click.echo("✅ Database initialized successfully")
            click.echo("   Schema: session_events table created")
            click.echo(f"   Location: {manager.db_path}")

        _init()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to initialize database: {exc}", err=True)
        sys.exit(1)


@cli.command("export-env")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "shell"]),
    default="text",
    help="Output format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (default: stdout)",
)
def export_env_cmd(output_format: str, output: str | None) -> None:
    """Export environment configuration.

    Examples:
        codex export-env
        codex export-env --format=json
        codex export-env --format=shell -o .env
    """
    try:
        import json as json_lib

        from codex.config.env_vars import env_manager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _export() -> None:
            config = env_manager.dump_config()

            if output_format == "json":
                content = json_lib.dumps(config, indent=2)
            elif output_format == "shell":
                lines = []
                for var, value in config.items():
                    if value:
                        lines.append(f'export {var}="{value}"')
                content = "\n".join(lines)
            else:  # text
                lines = []
                for var, value in config.items():
                    display_value = value if value else "<not set>"
                    lines.append(f"{var}={display_value}")
                content = "\n".join(lines)

            if output:
                Path(output).write_text(content)
                click.echo(f"✅ Environment exported to {output}")
            else:
                click.echo(content)

        _export()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to export environment: {exc}", err=True)
        sys.exit(1)


@cli.command("list-sessions")
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Maximum number of sessions to list",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def list_sessions_cmd(limit: int, output_format: str) -> None:
    """List recent session IDs.

    Examples:
        codex list-sessions
        codex list-sessions --limit=20
        codex list-sessions --format=json
    """
    try:
        import json as json_lib

        from codex.logging.db_manager import db_manager
        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _list() -> None:
            db_manager.init_schema()

            with db_manager.connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT DISTINCT session_id, MIN(ts) as first_seen, MAX(ts) as last_seen,
                            COUNT(*) as message_count
                    FROM session_events
                    GROUP BY session_id
                    ORDER BY last_seen DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()

            if not rows:
                click.echo("No sessions found")
                return

            if output_format == "json":
                sessions = []
                for row in rows:
                    sessions.append(
                        {
                            "session_id": row[0],
                            "first_seen": row[1],
                            "last_seen": row[2],
                            "message_count": row[3],
                        }
                    )
                click.echo(json_lib.dumps(sessions, indent=2))
            else:
                click.echo(f"{'Session ID':<40} {'Messages':<10} {'Last Activity'}")
                click.echo("-" * 70)
                for row in rows:
                    from datetime import datetime

                    last_seen = datetime.fromtimestamp(row[2]).strftime("%Y-%m-%d %H:%M:%S")
                    click.echo(f"{row[0]:<40} {row[3]:<10} {last_seen}")

        _list()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to list sessions: {exc}", err=True)
        sys.exit(1)


@cli.command("clean-logs")
@click.option(
    "--older-than",
    type=int,
    default=30,
    help="Remove logs older than N days",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without deleting",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
def clean_logs_cmd(older_than: int, dry_run: bool, yes: bool) -> None:
    """Clean old log files and sessions.

    Examples:
        codex clean-logs --dry-run
        codex clean-logs --older-than=7 -y
        codex clean-logs --older-than=14
    """
    try:
        import time
        from pathlib import Path

        from codex.logging.error_handler import error_handler

        @error_handler.log_errors
        def _clean() -> None:
            # Calculate cutoff timestamp
            cutoff = time.time() - (older_than * 24 * 60 * 60)

            # Find old log files
            log_dir = Path(".codex/logs")
            session_dir = Path(".codex/sessions")

            files_to_delete = []

            if log_dir.exists():
                for log_file in log_dir.glob("*.log*"):
                    if log_file.stat().st_mtime < cutoff:
                        files_to_delete.append(log_file)

            if session_dir.exists():
                for log_file in session_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff:
                        files_to_delete.append(log_file)

            if not files_to_delete:
                click.echo(f"No log files older than {older_than} days found")
                return

            click.echo(f"Found {len(files_to_delete)} files older than {older_than} days:")
            for f in files_to_delete:
                click.echo(f"  {f}")

            if dry_run:
                click.echo("\n🔍 Dry run mode - no files deleted")
                return

            if not yes:
                if not click.confirm(f"\nDelete {len(files_to_delete)} files?"):
                    click.echo("Cancelled")
                    return

            deleted = 0
            for f in files_to_delete:
                try:
                    f.unlink()
                    deleted += 1
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    click.echo(f"⚠️  Failed to delete {f}: {e}", err=True)

            click.echo(f"✅ Deleted {deleted} files")

        _clean()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to clean logs: {exc}", err=True)
        sys.exit(1)


@cli.group("duplication")
def duplication_group():
    """Duplication detection and metrics commands."""
    pass


@duplication_group.command("check")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--min-lines",
    type=int,
    default=4,
    help="Minimum lines to consider as duplicate",
)
@click.option(
    "--threshold",
    type=float,
    default=0.1,
    help="Fail if duplication ratio exceeds this value",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Save results to file (JSON format)",
)
def duplication_check(path: str, min_lines: int, threshold: float, output: str | None):
    """Check code for duplicates and calculate ratio.

    Examples:
        codex duplication check
        codex duplication check src/
        codex duplication check --min-lines=6 --threshold=0.15
        codex duplication check --output=duplication.json
    """
    try:
        from pathlib import Path as PathLib

        from codex.metrics.duplication import (
            calculate_duplication_ratio,
            detect_duplicates,
        )

        path_obj = PathLib(path).resolve()
        click.echo(f"🔍 Scanning {path_obj} for duplicates...")

        # Detect duplicates
        duplicates = detect_duplicates(
            path_obj,
            min_lines=min_lines,
            ignore_trivial=True,
        )

        # Count total lines (rough estimate for now)
        total_lines = 0
        for py_file in path_obj.rglob("*.py"):
            try:
                total_lines += len(py_file.read_text().splitlines())
            except (OSError, UnicodeDecodeError) as e:
                logger.debug(f"Exception: {e}")
                click.echo(f"⚠️  Skipping {py_file}: {e}", err=True)
                pass

        # Calculate ratio
        ratio = calculate_duplication_ratio(duplicates, total_lines)
        ratio.files_scanned = len(list(path_obj.rglob("*.py")))

        # Display results
        click.echo("\n📊 Duplication Report:")
        click.echo(f"  Total lines: {ratio.total_lines:,}")
        click.echo(f"  Duplicate lines: {ratio.duplicate_lines:,}")
        click.echo(f"  Duplication ratio: {ratio.ratio:.2%}")
        click.echo(f"  Files scanned: {ratio.files_scanned}")
        click.echo(f"  Files with duplicates: {ratio.files_with_duplicates}")
        click.echo(f"  Duplicate blocks: {len(ratio.duplicate_blocks)}")

        # Save to file if requested
        if output:
            output_path = PathLib(output)
            data = ratio.to_dict()
            data["path"] = str(path_obj)
            data["min_lines"] = min_lines

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            click.echo(f"\n💾 Saved results to {output_path}")

        # Check threshold
        if ratio.ratio > threshold:
            click.echo(
                f"\n❌ Duplication ratio {ratio.ratio:.2%} exceeds threshold {threshold:.2%}",
                err=True,
            )
            sys.exit(1)
        else:
            click.echo(
                f"\n✅ Duplication ratio {ratio.ratio:.2%} is within threshold {threshold:.2%}"
            )

    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to check duplicates: {exc}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


@duplication_group.command("report")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--min-lines",
    type=int,
    default=4,
    help="Minimum lines to consider as duplicate",
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.option(
    "--output",
    type=click.Path(),
    required=True,
    help="Output file path",
)
@click.option(
    "--save-db",
    is_flag=True,
    help="Also save to SQLite database",
)
def duplication_report(path: str, min_lines: int, format: str, output: str, save_db: bool):
    """Generate detailed duplication report.

    Examples:
        codex duplication report --output=report.json
        codex duplication report --format=text --output=report.txt
        codex duplication report --save-db --output=report.json
    """
    try:
        from pathlib import Path as PathLib

        from codex.metrics.duplication import (
            calculate_duplication_ratio,
            detect_duplicates,
        )
        from codex.metrics.storage import MetricStorage

        path_obj = PathLib(path).resolve()
        click.echo(f"🔍 Generating duplication report for {path_obj}...")

        # Detect duplicates
        duplicates = detect_duplicates(path_obj, min_lines=min_lines)

        # Count total lines
        total_lines = 0
        files_scanned = 0
        for py_file in path_obj.rglob("*.py"):
            try:
                total_lines += len(py_file.read_text().splitlines())
                files_scanned += 1
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read or decoded
                pass

        # Calculate ratio
        ratio = calculate_duplication_ratio(duplicates, total_lines)
        ratio.files_scanned = files_scanned

        output_path = PathLib(output)

        if format == "json":
            # JSON format
            data = ratio.to_dict()
            data["scan_path"] = str(path_obj)
            data["min_lines"] = min_lines

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        else:
            # Text format
            lines = [
                "=" * 60,
                "DUPLICATION REPORT",
                "=" * 60,
                f"Scan path: {path_obj}",
                f"Generated: {__import__('datetime').datetime.now().isoformat()}",
                "",
                "SUMMARY",
                "-" * 60,
                f"Total lines: {ratio.total_lines:,}",
                f"Duplicate lines: {ratio.duplicate_lines:,}",
                f"Duplication ratio: {ratio.ratio:.2%}",
                f"Files scanned: {ratio.files_scanned}",
                f"Files with duplicates: {ratio.files_with_duplicates}",
                f"Duplicate blocks: {len(ratio.duplicate_blocks)}",
                "",
            ]

            if ratio.duplicate_blocks:
                lines.append("DUPLICATE BLOCKS")
                lines.append("-" * 60)
                for i, block in enumerate(ratio.duplicate_blocks[:10], 1):
                    lines.append(f"\n#{i} {block.severity.upper()} - {block.clone_type}")
                    lines.append(f"  Lines: {block.lines[0]}-{block.lines[1]}")
                    lines.append(f"  Occurrences: {len(block.occurrences)}")
                    for occ in block.occurrences[:5]:
                        lines.append(f"    - {occ['file']}:{occ['start']}")

                if len(ratio.duplicate_blocks) > 10:
                    lines.append(f"\n... and {len(ratio.duplicate_blocks) - 10} more blocks")

            with open(output_path, "w") as f:
                f.write("\n".join(lines))

        click.echo(f"✅ Report saved to {output_path}")

        # Save to database if requested
        if save_db:
            storage = MetricStorage()
            result = storage.save(ratio)
            click.echo(f"💾 Saved to database (ID: {result.get('sqlite_id', 'N/A')})")

    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to generate report: {exc}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


@duplication_group.command("compare")
@click.argument("current", type=click.Path(exists=True))
@click.option(
    "--baseline",
    type=click.Path(exists=True),
    help="Baseline JSON file to compare against",
)
@click.option(
    "--threshold-increase",
    type=float,
    default=0.05,
    help="Fail if ratio increased by more than this value",
)
def duplication_compare(current: str, baseline: str | None, threshold_increase: float):
    """Compare duplication metrics against baseline.

    Examples:
        codex duplication compare report.json --baseline=baseline.json
        codex duplication compare report.json --baseline=baseline.json --threshold-increase=0.10
    """
    try:
        from pathlib import Path as PathLib

        current_path = PathLib(current)

        # Load current metrics
        with open(current_path) as f:
            current_data = json.load(f)

        current_ratio = current_data.get("ratio", 0.0)

        if baseline:
            # Load baseline
            baseline_path = PathLib(baseline)
            with open(baseline_path) as f:
                baseline_data = json.load(f)

            baseline_ratio = baseline_data.get("ratio", 0.0)

            # Compare
            difference = current_ratio - baseline_ratio
            percent_change = (difference / baseline_ratio * 100) if baseline_ratio > 0 else 0

            click.echo("📊 Duplication Comparison")
            click.echo(f"  Baseline: {baseline_ratio:.2%}")
            click.echo(f"  Current:  {current_ratio:.2%}")
            click.echo(f"  Change:   {difference:+.2%} ({percent_change:+.1f}%)")

            if difference > threshold_increase:
                click.echo(
                    f"\n❌ Duplication increased by {difference:.2%}, exceeds threshold {threshold_increase:.2%}",
                    err=True,
                )
                sys.exit(1)
            elif difference > 0:
                click.echo(
                    f"\n⚠️  Duplication increased by {difference:.2%}, within threshold {threshold_increase:.2%}"
                )
            else:
                click.echo("\n✅ Duplication decreased or stayed the same")
        else:
            # No baseline - just show current
            click.echo("📊 Current Duplication Metrics")
            click.echo(f"  Ratio: {current_ratio:.2%}")
            click.echo(f"  Total lines: {current_data.get('total_lines', 0):,}")
            click.echo(f"  Duplicate lines: {current_data.get('duplicate_lines', 0):,}")
            click.echo("\n💡 Use --baseline to compare against a previous report")

    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        click.echo(f"❌ Failed to compare metrics: {exc}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# Quantum Orchestrator CLI Integration
# ============================================================================

try:
    from codex.quantum_orchestrator.cli import cli as quantum_cli

    # Add quantum orchestrator as a subcommand group
    cli.add_command(quantum_cli, name="quantum")
except Exception:  # pragma: no cover - optional module
    pass


_register_external_cli()


@cli.command("workflow-scan")
@click.option(
    "--workflows-dir",
    "-d",
    default=".github/workflows",
    help="Path to workflows directory",
    type=click.Path(exists=True),
)
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json", "summary"]),
    help="Output format",
)
@click.option(
    "--triggerable-only",
    "-t",
    is_flag=True,
    help="Show only triggerable workflows",
)
def workflow_scan(workflows_dir: str, format: str, triggerable_only: bool) -> None:
    """Scan and display GitHub Actions workflows."""
    try:
        from services.workflow.inventory import WorkflowInventory
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        click.echo("Error: workflow services not available", err=True)
        sys.exit(1)
    
    inventory = WorkflowInventory(workflows_dir)
    count = inventory.scan()
    
    if count == 0:
        click.echo(f"No workflows found in {workflows_dir}")
        return
    
    workflows = inventory.get_triggerable() if triggerable_only else list(inventory.workflows.values())
    
    if format == "json":
        data = [
            {
                "name": w.name,
                "file": w.filename,
                "triggerable": w.is_triggerable,
                "jobs": len(w.jobs),
                "triggers": len(w.triggers),
            }
            for w in workflows
        ]
        click.echo(json.dumps(data, indent=2))
    elif format == "summary":
        stats = inventory.get_stats()
        click.echo("\n📊 Workflow Inventory Summary\n")
        click.echo(f"Total workflows: {stats.total_workflows}")
        click.echo(f"Triggerable: {stats.triggerable_workflows}")
        click.echo(f"Reusable: {stats.reusable_workflows}")
        click.echo(f"Total jobs: {stats.total_jobs}")
        click.echo(f"Total triggers: {stats.total_triggers}")
        click.echo(f"Dependencies: {stats.dependency_count}")
    else:  # table
        click.echo(f"\n📋 Workflows ({len(workflows)} {'triggerable' if triggerable_only else 'total'})\n")
        click.echo(f"{'Name':<40} {'File':<30} {'Jobs':<6} {'Triggers':<10}")
        click.echo("-" * 90)
        for w in workflows:
            click.echo(f"{w.name[:39]:<40} {w.filename[:29]:<30} {len(w.jobs):<6} {len(w.triggers):<10}")


# Expose CLI groups as module attributes for testing and dynamic imports
# These are already defined above and don't need reassignment
__all__ = ["cli", "logs", "tokenizer_group", "repro_group"]


if __name__ == "__main__":
    cli()
