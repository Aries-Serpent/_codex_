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


import json  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import TYPE_CHECKING, Annotated  # noqa: E402

import typer  # noqa: E402

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
    """Score QA results using a rubric.

    Reads QA test cases from a CSV file, evaluates them against a scoring
    rubric, and outputs detailed scores in JSONL format. Each line in the
    output contains a scored result with metadata.

    Args:
        rubric_file: Path to QA rubric file (must exist, readable)
        input_csv: Path to input CSV with test cases (must exist, readable)
        output_jsonl: Path to output JSONL file with scores

    Input Format (CSV):
        Columns depend on rubric, typically:
        - question: Test question
        - expected: Expected answer
        - actual: Actual system output
        - context: Optional context

    Output Format (JSONL):
        Each line contains:
        {
            "test_id": "...",
            "question": "...",
            "score": 0.0-1.0,
            "details": {...},
            "timestamp": "ISO-8601"
        }

    Examples:
        # Score QA results
        codex qa score rubric.json test_cases.csv scores.jsonl

        # With custom file paths
        codex qa score /path/to/rubric.json /data/tests.csv /output/scores.jsonl

    Requirements:
        - Pydantic installed (optional dependency)
        - Rubric file in valid format
        - CSV matches rubric expectations

    See Also:
        codex quality evaluate - Evaluate system quality
    """
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
