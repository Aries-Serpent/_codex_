"""Typer CLI for offline QA scoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

if TYPE_CHECKING:  # pragma: no cover - import guards
    from codex.qa.rubric import QARubric

app = typer.Typer(help="Offline QA utilities.")


InputArg = Annotated[Path, typer.Argument(..., exists=True, readable=True)]
OutputArg = Annotated[Path, typer.Argument(...)]


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
