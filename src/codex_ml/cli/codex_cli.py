from __future__ import annotations

import click

from codex_ml.telemetry import start_metrics_server


@click.group()
def codex() -> None:
    """Codex command line interface."""


@codex.command()
@click.option(
    "--config",
    default="configs/training/base.yaml",
    show_default=True,
    help="Path to the training YAML configuration file.",
)
@click.option(
    "--resume",
    is_flag=True,
    help="Resume from the latest checkpoint if available.",
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Override the random seed defined in the config.",
)
def train(config: str, resume: bool, seed: int | None) -> None:
    """Train a model using the functional training pipeline."""
    import json
    from pathlib import Path

    import yaml

    from codex_ml.training import run_functional_training
    from codex_ml.utils.error_log import log_error as log_training_error

    cfg_path = Path(config)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    if seed is not None:
        cfg["seed"] = seed

    try:
        result = run_functional_training(cfg, resume=resume)
    except Exception as exc:  # pragma: no cover - surfaced via CLI
        log_training_error(
            "train",
            f"{exc.__class__.__name__}: {exc}",
            json.dumps({"config": config, "resume": resume, "seed": seed}),
        )
        raise

    checkpoint_dir = result.get("checkpoint_dir") if isinstance(result, dict) else None
    if checkpoint_dir:
        click.echo(f"Training complete. Checkpoints saved to {checkpoint_dir}")
    else:
        click.echo("Training complete.")


@codex.command("metrics-server")
@click.option("--port", default=8000, show_default=True)
def metrics_server(port: int) -> None:
    if start_metrics_server(port=port):
        click.echo(f"metrics server running on {port}")
    else:
        click.echo("prometheus_client missing", err=True)


@codex.command()
@click.argument("text")
def tokenize(text: str):
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    tok = HFTokenizerAdapter.load()
    ids = tok.encode(text)
    click.echo(str(ids))


@codex.command()
def repo_map():
    click.echo("repo map not implemented")


@codex.command()
@click.option("--dataset", default="dummy")
def evaluate(dataset: str):
    click.echo(f"evaluate {dataset} not implemented")


if __name__ == "__main__":  # pragma: no cover
    codex()
