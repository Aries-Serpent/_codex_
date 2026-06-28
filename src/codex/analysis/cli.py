"""Code analysis CLI."""

import ast
import json
from pathlib import Path
from typing import Any

import click


def _analyze_module(path: Path) -> dict[str, Any]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except (IOError, OSError):
        return {
            "file": str(path),
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "error": "unreadable",
        }
    lines = len(source.splitlines())
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return {
            "file": str(path),
            "lines": lines,
            "functions": 0,
            "classes": 0,
            "error": "syntax_error",
        }
    functions = sum(
        1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    return {
        "file": str(path),
        "lines": lines,
        "functions": functions,
        "classes": classes,
    }


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--format", type=click.Choice(["json", "yaml", "html", "csv"]), default="json")
@click.option("--output", type=click.Path(), help="Output file (default: stdout)")
@click.option("--threshold", type=int, default=50, help="Long function threshold")
def analyze_main(path: str, format: str, output: str, threshold: int) -> None:
    """Analyze code quality and generate metrics report.

    Examples:
        codex-analyze . --format html --output report.html
        codex-analyze src/ --threshold 40
    """
    root = Path(path)
    modules: list[dict[str, Any]] = []
    for py_file in sorted(root.rglob("*.py")):
        modules.append(_analyze_module(py_file))

    total_files = len(modules)
    total_lines = sum(m.get("lines", 0) for m in modules)
    total_functions = sum(m.get("functions", 0) for m in modules)
    total_classes = sum(m.get("classes", 0) for m in modules)

    report = {
        "summary": {
            "file_count": total_files,
            "line_count": total_lines,
            "function_count": total_functions,
            "class_count": total_classes,
        },
        "modules": modules,
    }

    output_text = json.dumps(report, indent=2)

    if output:
        Path(output).write_text(output_text)
        click.echo(f"Analysis report written to {output}")
    else:
        click.echo(output_text)


if __name__ == "__main__":
    analyze_main()
