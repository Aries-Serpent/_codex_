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
import os
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

REASONING_TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "configs" / "training" / "reasoning"
REASONING_CURRICULA_ROOT = REASONING_TEMPLATE_ROOT / "curricula"

_USE_TYPER = False
try:  # pragma: no cover - prefer Typer when available
    import typer as _typer

    _USE_TYPER = True
except (ImportError, AttributeError):  # pragma: no cover - Typer shadowed/unavailable
    _USE_TYPER = False

if _USE_TYPER:
    echo = _typer.echo
    Exit = _typer.Exit
else:  # pragma: no cover - click fallback
    import click as _click

    echo = _click.echo

    class Exit(SystemExit):  # type: ignore[no-redef]
        def __init__(self, code: int = 0) -> None:
            super().__init__(code)


def _track_smoke_impl(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1) from exc
    target.mkdir(parents=True, exist_ok=True)
    with mlflow.start_run(run_name="smoke"):
        mlflow.log_param("p", 1)
        mlflow.log_metric("m", 0.123)
    echo(f"OK: tracking to {uri}")


def _split_smoke_impl(seed: int) -> None:
    total = 20
    try:
        import torch

        generator = getattr(torch, "Generator", None)
        if generator is None:
            raise AttributeError()
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except (ImportError, AttributeError) as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except (ImportError, AttributeError) as err:
            logger.warning("Exception occurred", exc_info=True)
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1) from err
        rng = random.Random(int(seed))  # nosec B311 - deterministic CLI shuffle
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def _checkpoint_smoke_impl(out_dir: Path) -> None:
    try:
        import torch

        from training.checkpointing import save_checkpoint

        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - optional dependency missing
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


if _USE_TYPER:
    app = _typer.Typer(
        name="codex",
        add_completion=False,
        help="Codex CLI for reasoning templates plus local/offline runs (tokenize/train/eval/tracking).",  # noqa: E501
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
                type(e).__name__
                logger.debug("OSError: <ERROR_TYPE>")
                logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
                description = "Reasoning template"
            entries.append((path.stem, description, path))
        return entries

    def _load_yaml(path: Path) -> dict[str, Any]:
        try:
            import yaml
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - optional dependency missing
            echo(f"PyYAML not available: {exc}")
            raise Exit(code=1) from exc
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            echo(f"Failed to load {path}: {exc}")
            raise Exit(code=1) from exc
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
                type(e).__name__
                logger.debug("ValueError: <ERROR_TYPE>")
                logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
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
        except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - defensive fallback
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
        help="Codex CLI for reasoning templates plus local/offline runs (tokenize/train/eval/tracking).",  # noqa: E501
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
                type(e).__name__
                logger.debug("OSError: <ERROR_TYPE>")
                logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
                description = "Reasoning template"
            entries.append((path.stem, description, path))
        return entries

    def _load_yaml(path: Path) -> dict[str, Any]:
        try:
            import yaml
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - optional dependency missing
            echo(f"PyYAML not available: {exc}")
            raise Exit(code=1) from exc
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            echo(f"Failed to load {path}: {exc}")
            raise Exit(code=1) from exc
        if not isinstance(data, dict):
            echo(f"Unexpected config structure in {path}")
            raise Exit(code=1)
        return data

    @app.command("version")
    def version() -> None:
        try:
            from . import __version__
        except (ImportError, AttributeError):  # pragma: no cover - defensive fallback
            __version__ = "unknown"
        echo(__version__)

    @app.command("track-smoke")
    @_click.option(
        "--dir",
        "dir_",
        type=_click.Path(path_type=Path),
        default=None,
        help="Local mlruns dir",
    )
    def track_smoke(dir_: Optional[Path] = None) -> None:

        _track_smoke_impl(dir_)

    @app.command("split-smoke")
    @_click.option(
        "--seed",
        type=int,
        default=1337,
        show_default=True,
        help="Seed for deterministic split",
    )
    def split_smoke(seed: int = 1337) -> None:
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
    def checkpoint_smoke(out_dir: Path = Path(".checkpoints")) -> None:
        _checkpoint_smoke_impl(out_dir)

    # Modern sub-apps pattern: define group separately, then register via add_command.
    # This mirrors the Typer branch's app.add_typer(reasoning_templates, ...) pattern.
    reasoning_templates = _click.Group(
        name="reasoning-templates",
        help="Surface reasoning training presets and curricula metadata.",
    )
    app.add_command(reasoning_templates, name="reasoning-templates")

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
                type(e).__name__
                logger.debug("ValueError: <ERROR_TYPE>")
                logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
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
    def repo_map(reasoning: bool, includes: tuple[str, ...] = ()) -> None:

        from codex_ml.cli.repo_map import render_repo_map

        echo(render_repo_map(reasoning=reasoning, include=includes))


def main() -> None:  # pragma: no cover - thin wrapper for python -m usage
    app()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
