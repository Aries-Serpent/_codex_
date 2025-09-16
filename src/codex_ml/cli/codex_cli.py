from __future__ import annotations

from typing import Optional

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
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the training YAML configuration.",
)
@click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
@click.option("--seed", type=int, default=None, help="Override the random seed from the config.")
def train(config: str, resume: bool, seed: Optional[int]) -> None:
    """Train a language model using the Codex functional trainer."""
    from codex_ml.training import run_functional_training
    from codex_ml.utils.config_loader import load_config
    from codex_ml.utils.error_log import log_error as log_training_error

    try:
        cfg = load_config(config_path=config)
        if seed is not None:
            if "training" in cfg and hasattr(cfg.training, "seed"):
                cfg.training.seed = seed
            else:
                cfg.seed = seed
        run_functional_training(config=cfg, resume=resume)
        click.echo("training complete")
    except Exception as exc:  # pragma: no cover - Click handles presentation
        log_training_error("cli.train", str(exc), f"config={config} resume={resume}")
        raise click.ClickException(str(exc))


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
