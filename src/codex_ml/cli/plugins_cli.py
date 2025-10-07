"""CLI utilities for inspecting plugin registries."""

from __future__ import annotations

import inspect
import sys
from typing import Sequence

from codex_ml.plugins import registries
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = (ArgparseJSONParser, run_cmd)

try:  # Optional dependency: Typer preferred when available
    import typer  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Typer missing
    typer = None  # type: ignore[assignment]
else:  # pragma: no cover - namespace stub
    if not hasattr(typer, "Typer"):
        typer = None  # type: ignore[assignment]

_GROUPS = {
    "tokenizers": registries.tokenizers,
    "models": registries.models,
    "datasets": registries.datasets,
    "metrics": registries.metrics,
    "trainers": registries.trainers,
    "reward_models": registries.reward_models,
    "rl_agents": registries.rl_agents,
}


def _get_registry(group: str, *, bad_param_exc):
    reg = _GROUPS.get(group)
    if not reg:
        raise bad_param_exc(f"unknown group: {group}")
    return reg


def _list_group(group: str, *, echo, bad_param_exc) -> None:
    reg = _get_registry(group, bad_param_exc=bad_param_exc)
    for name in reg.names():
        echo(name)


def _diagnose_group(group: str, use_entry_points: bool, *, echo, bad_param_exc) -> None:
    reg = _get_registry(group, bad_param_exc=bad_param_exc)
    errors = {}
    if use_entry_points:
        _, errors = reg.load_from_entry_points(f"codex_ml.{group}", require_api="v1")
    echo(f"registered={len(reg.names())}")
    for key, value in errors.items():
        echo(f"{key}: {value}")


def _explain_group(group: str, name: str, *, echo, exit_exc, bad_param_exc) -> None:
    reg = _get_registry(group, bad_param_exc=bad_param_exc)
    item = reg.get(name)
    if not item:
        raise exit_exc(code=1)
    obj = item.obj
    echo(f"module: {obj.__module__}")
    doc = inspect.getdoc(obj) or ""
    if doc:
        echo(doc)
    try:
        sig = inspect.signature(obj, eval_str=True)
        echo(str(sig))
    except ValueError:  # pragma: no cover - builtins may not have signature
        pass


if typer is not None:  # pragma: no cover - Typer CLI
    app = typer.Typer(help="Inspect codex_ml plugin registries")

    @app.command()
    def list(group: str) -> None:
        """List registered plugin names for ``group``."""

        _list_group(group, echo=typer.echo, bad_param_exc=typer.BadParameter)

    @app.command()
    def diagnose(group: str, use_entry_points: bool = False) -> None:
        """Diagnose plugin loading for ``group``."""

        _diagnose_group(group, use_entry_points, echo=typer.echo, bad_param_exc=typer.BadParameter)

    @app.command()
    def explain(group: str, name: str) -> None:
        """Show details for a specific plugin."""

        _explain_group(
            group,
            name,
            echo=typer.echo,
            exit_exc=typer.Exit,
            bad_param_exc=typer.BadParameter,
        )

else:
    import click

    @click.group(help="Inspect codex_ml plugin registries")
    def app() -> None:
        """Click fallback CLI for plugin inspection."""

    @app.command("list")
    @click.argument("group")
    def list_cmd(group: str) -> None:
        """List registered plugin names for ``group``."""

        _list_group(group, echo=click.echo, bad_param_exc=click.BadParameter)

    @app.command()
    @click.argument("group")
    @click.option("--use-entry-points", is_flag=True, default=False)
    def diagnose(group: str, use_entry_points: bool) -> None:
        """Diagnose plugin loading for ``group``."""

        _diagnose_group(group, use_entry_points, echo=click.echo, bad_param_exc=click.BadParameter)

    @app.command()
    @click.argument("group")
    @click.argument("name")
    def explain(group: str, name: str) -> None:
        """Show details for a specific plugin."""

        _explain_group(
            group,
            name,
            echo=click.echo,
            exit_exc=click.exceptions.Exit,
            bad_param_exc=click.BadParameter,
        )


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    arg_list = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
        exit_code = 0
        if typer is not None:
            try:
                app(prog_name=sys.argv[0], args=arg_list, standalone_mode=False)
            except typer.Exit as exc:
                exit_code = exc.exit_code
        else:
            try:
                app.main(args=arg_list, prog_name=sys.argv[0], standalone_mode=False)
            except click.exceptions.Exit as exc:
                exit_code = exc.exit_code
        log_event(
            logger,
            "cli.finish",
            prog=sys.argv[0],
            status="ok" if exit_code == 0 else "error",
            exit_code=exit_code,
        )
        return exit_code


if __name__ == "__main__":  # pragma: no cover - manual invocation
    raise SystemExit(main())
