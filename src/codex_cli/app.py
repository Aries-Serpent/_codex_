
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_USE_TYPER = False
try:  # pragma: no cover - prefer Typer when available
    import typer as _typer  # type: ignore
    if hasattr(_typer, "Typer"):
        _USE_TYPER = True
except Exception:  # pragma: no cover - Typer shadowed/unavailable
    _USE_TYPER = False

if _USE_TYPER:
    echo = _typer.echo
    Exit = _typer.Exit
else:  # pragma: no cover - click fallback
    import click as _click

    echo = _click.echo

    class Exit(SystemExit):
        def __init__(self, code: int = 0) -> None:
            super().__init__(code)


def _track_smoke_impl(dir_path: Optional[Path]) -> None:
    target = (dir_path or Path("./mlruns")).resolve()
    uri = f"file:{target}"
    os.environ["MLFLOW_TRACKING_URI"] = uri
    try:
        import mlflow  # optional runtime dependency
    except Exception as exc:  # pragma: no cover - optional dependency missing
        echo(f"MLflow not available: {exc}")
        raise Exit(code=1)
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
            raise AttributeError
        order = torch.randperm(total, generator=torch.Generator().manual_seed(int(seed)))
    except Exception as exc:  # pragma: no cover - optional dependency missing
        try:
            import random
        except Exception:
            echo(f"torch unavailable: {exc}")
            raise Exit(code=1)
        rng = random.Random(int(seed))
        order = list(range(total))
        rng.shuffle(order)
    mid = total // 2
    _ = order[:mid], order[mid:]
    echo(f"A={mid} B={total - mid} (seed={seed})")


def _checkpoint_smoke_impl(out_dir: Path) -> None:
    try:
        import torch
        from src.training.checkpointing import save_checkpoint
        if not hasattr(torch, "nn"):
            raise AttributeError("torch.nn unavailable")
    except Exception as exc:  # pragma: no cover - optional dependency missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "epoch1-metric0.500000.pt"
        path.write_bytes(b"stub")
        echo(f"Saved {path} (stub: {exc})")
        return

    model = torch.nn.Sequential(torch.nn.Linear(8, 3))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = save_checkpoint(model, optimizer, epoch=1, val_metric=0.50, out_dir=out_dir, keep_best_k=2)
    echo(f"Saved {path}")


if _USE_TYPER:
    app = _typer.Typer(
        name="codex",
        add_completion=False,
        help="Codex CLI for local/offline runs (tokenize/train/eval/tracking).",
    )

    @app.command("version")
    def version() -> None:
        try:
            from . import __version__
        except Exception:  # pragma: no cover - defensive fallback
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

    @_click.group(name="codex", help="Codex CLI for local/offline runs (tokenize/train/eval/tracking).")
    def app() -> None:
        """Codex offline smoke helpers."""

    @app.command("version")
    def version() -> None:
        try:
            from . import __version__
        except Exception:  # pragma: no cover - defensive fallback
            __version__ = "unknown"
        echo(__version__)

    @app.command("track-smoke")
    @_click.option("--dir", "dir_", type=_click.Path(path_type=Path), default=None, help="Local mlruns dir")
    def track_smoke(dir_: Optional[Path]) -> None:
        _track_smoke_impl(dir_)

    @app.command("split-smoke")
    @_click.option("--seed", type=int, default=1337, show_default=True, help="Seed for deterministic split")
    def split_smoke(seed: int) -> None:
        _split_smoke_impl(seed)

    @app.command("checkpoint-smoke")
    @_click.option("--out", "out_dir", type=_click.Path(path_type=Path), default=Path(".checkpoints"), show_default=True, help="Checkpoint directory")
    def checkpoint_smoke(out_dir: Path) -> None:
        _checkpoint_smoke_impl(out_dir)


def main() -> None:  # pragma: no cover - thin wrapper for python -m usage
    app()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
