"""
Cli Module

This module provides functionality for cli.

Usage:
    from quality.cli import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import ast
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

from typing import Any

import click  # noqa: E402


def _count_function_lines(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    if not node.body:
        return 0
    return max(0, (node.end_lineno or node.lineno) - node.lineno)


def _scan_smells(
    src_root: Path,
    long_fn_threshold: int = 50,
    max_args: int = 5,
    max_file_lines: int = 500,
) -> dict[str, Any]:
    long_functions: list[dict[str, Any]] = []
    large_files: list[dict[str, Any]] = []
    many_args: list[dict[str, Any]] = []

    for path in src_root.rglob("*.py"):
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except (IOError, OSError):  # nosec B112
            continue
        lines = source.splitlines()
        if len(lines) > max_file_lines:
            large_files.append({"file": str(path), "lines": len(lines)})
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_lines = _count_function_lines(node)
                if fn_lines > long_fn_threshold:
                    long_functions.append(
                        {"file": str(path), "function": node.name, "lines": fn_lines}
                    )
                arg_count = (
                    len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
                )
                if arg_count > max_args:
                    many_args.append({"file": str(path), "function": node.name, "args": arg_count})

    return {
        "long_functions": long_functions,
        "large_files": large_files,
        "many_args_functions": many_args,
    }


@click.command()
@click.option("--format", type=click.Choice(["json", "yaml", "html"]), default="json")
@click.option("--output", type=click.Path(), help="Output file")
@click.option("--config", type=click.Path(), default="configs/code_quality.yaml")
@click.option(
    "--fail-on",
    multiple=True,
    help="Smell category to fail on (long_functions, large_files, many_args_functions)",
)
@click.option(
    "--warn-on",
    multiple=True,
    help="Smell category to warn on (long_functions, large_files, many_args_functions)",
)
@click.option("--fail-on-smells", is_flag=True, default=False, help="Exit 1 if any smells found")
def smell_main(
    format: str,
    output: str,
    config: str,
    fail_on: tuple[Any, ...],
    warn_on: tuple[Any, ...],
    fail_on_smells: bool,
) -> None:
    """Detect code smells based on configured thresholds.

    Examples:
        codex-smell --format json --output smells.json
        codex-smell --fail-on long_functions --warn-on large_files
    """
    long_fn_threshold = 50
    max_args = 5
    max_file_lines = 500

    # Try loading config if it exists
    try:
        import yaml

        cfg_path = Path(config)
        if cfg_path.exists():
            with open(cfg_path) as f:
                conf = yaml.safe_load(f) or {}
            smells = conf.get("code_smells", {})
            long_fn_threshold = smells.get("long_function", {}).get("threshold", long_fn_threshold)
            max_args = smells.get("max_arguments", {}).get("threshold", max_args)
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Config load skipped: <ERROR_TYPE>")

    src_root = Path("src")
    if not src_root.exists():
        src_root = Path(".")

    smells_data = _scan_smells(src_root, long_fn_threshold, max_args, max_file_lines)
    total = sum(len(v) for v in smells_data.values())

    summary = {
        "long_functions_count": len(smells_data["long_functions"]),
        "large_files_count": len(smells_data["large_files"]),
        "many_args_functions_count": len(smells_data["many_args_functions"]),
        "total_smells": total,
        "details": smells_data,
    }

    import json

    output_text = json.dumps(summary, indent=2)

    if output:
        Path(output).write_text(output_text)
        click.echo(f"Smell report written to {output}")
    else:
        click.echo(output_text)

    click.echo(
        f"\nSummary: {len(smells_data['long_functions'])} long functions, "
        f"{len(smells_data['large_files'])} large files, "
        f"{len(smells_data['many_args_functions'])} functions with many args",
        err=True,
    )

    if fail_on_smells and total > 0:
        sys.exit(1)

    # Honour explicit --fail-on / --warn-on smell-category severity flags.
    # Accepted category names: long_functions, large_files, many_args_functions
    # (match the keys returned by _scan_smells).
    VALID_CATEGORIES = {"long_functions", "large_files", "many_args_functions"}
    CATEGORY_MAP = {
        "long_functions": len(smells_data["long_functions"]),
        "large_files": len(smells_data["large_files"]),
        "many_args_functions": len(smells_data["many_args_functions"]),
    }
    for category in (*warn_on, *fail_on):
        if category not in VALID_CATEGORIES:
            click.echo(
                f"ERROR: unknown category {category!r}. "
                f"Valid values: {', '.join(sorted(VALID_CATEGORIES))}",
                err=True,
            )
            sys.exit(2)
    warned = False
    failed = False
    for category in warn_on:
        count = CATEGORY_MAP.get(category, 0)
        if count > 0:
            click.echo(
                f"WARNING: {count} '{category}' smell(s) found (--warn-on {category})",
                err=True,
            )
            warned = True
    for category in fail_on:
        count = CATEGORY_MAP.get(category, 0)
        if count > 0:
            click.echo(
                f"ERROR: {count} '{category}' smell(s) found (--fail-on {category})",
                err=True,
            )
            failed = True
    _ = warned  # consumed for side-effects above; suppress unused-var lint
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    smell_main()
