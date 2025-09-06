"""CLI utilities for inspecting plugin registries."""

from __future__ import annotations

import inspect

import typer

from codex_ml.plugins import registries

app = typer.Typer(help="Inspect codex_ml plugin registries")

_GROUPS = {
    "tokenizers": registries.tokenizers,
    "models": registries.models,
    "datasets": registries.datasets,
    "metrics": registries.metrics,
    "trainers": registries.trainers,
    "reward_models": registries.reward_models,
    "rl_agents": registries.rl_agents,
}


def _get_registry(group: str):
    reg = _GROUPS.get(group)
    if not reg:
        raise typer.BadParameter(f"unknown group: {group}")
    return reg


@app.command()
def list(group: str) -> None:
    """List registered plugin names for ``group``."""

    reg = _get_registry(group)
    for name in reg.names():
        typer.echo(name)


@app.command()
def diagnose(group: str, use_entry_points: bool = False) -> None:
    """Diagnose plugin loading for ``group``."""

    reg = _get_registry(group)
    errors = {}
    if use_entry_points:
        _, errors = reg.load_from_entry_points(f"codex_ml.{group}", require_api="v1")
    typer.echo(f"registered={len(reg.names())}")
    for k, v in errors.items():
        typer.echo(f"{k}: {v}")


@app.command()
def explain(group: str, name: str) -> None:
    """Show details for a specific plugin."""

    reg = _get_registry(group)
    item = reg.get(name)
    if not item:
        raise typer.Exit(code=1)
    obj = item.obj
    typer.echo(f"module: {obj.__module__}")
    doc = inspect.getdoc(obj) or ""
    if doc:
        typer.echo(doc)
    try:
        sig = inspect.signature(obj)
        typer.echo(str(sig))
    except ValueError:  # pragma: no cover - builtins may not have signature
        pass


if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
