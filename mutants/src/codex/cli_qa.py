"""
Cli Qa Module

This module provides functionality for cli qa.

Usage:
    from codex.cli_qa import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Typer CLI for offline QA scoring."""


import json
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

if TYPE_CHECKING:  # pragma: no cover - import guards
    from codex.qa.rubric import QARubric

app = typer.Typer(help="Offline QA utilities.")


InputArg = Annotated[Path, typer.Argument(..., exists=True, readable=True)]
OutputArg = Annotated[Path, typer.Argument(...)]
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


@app.command("score")
def score(
    rubric_file: InputArg,
    input_csv: InputArg,
    output_jsonl: OutputArg,
) -> None:
    try:
        from codex.qa import rubric as rubric_module
    except ImportError as exc:  # pragma: no cover - optional dependency guard
        typer.echo(
            "QA rubric tooling requires optional dependencies (install 'pydantic').",
            err=True,
        )
        raise typer.Exit(3) from exc

    rubric: QARubric = rubric_module.load_rubric(rubric_file)
    rubric_module.generate_scores(input_csv, rubric, output_jsonl)
    typer.echo(json.dumps({"ok": True, "output": output_jsonl.as_posix()}, indent=2))
