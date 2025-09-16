from __future__ import annotations

from typing import Optional

import click

from codex_ml.telemetry import start_metrics_server


@click.group()
def codex() -> None:
    """Codex command line interface."""


@codex.group()
def tokenizer() -> None:
    """Tokenizer pipeline utilities."""


@tokenizer.command("train")
@click.option(
    "--config",
    default="configs/tokenization/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the tokenizer pipeline configuration file.",
)
def tokenizer_train(config: str) -> None:
    """Train a tokenizer according to the provided configuration."""
    del config
    raise click.ClickException(
        "tokenizer train pipeline not yet implemented; will land in a follow-up."
    )


@tokenizer.command("validate")
@click.option(
    "--config",
    default="configs/tokenization/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the tokenizer pipeline configuration file.",
)
def tokenizer_validate(config: str) -> None:
    """Validate dataset manifests and cached tokenizer artifacts."""
    del config
    raise click.ClickException(
        "tokenizer validate pipeline not yet implemented; will land in a follow-up."
    )


@tokenizer.command("encode")
@click.argument("text", required=False)
@click.option(
    "--tokenizer-path",
    default="artifacts/tokenizers/default/tokenizer.json",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to the serialized tokenizer JSON file to use for encoding.",
)
def tokenizer_encode(text: Optional[str], tokenizer_path: str) -> None:
    """Encode text with a trained tokenizer."""
    del text, tokenizer_path
    raise click.ClickException(
        "tokenizer encode pipeline not yet implemented; will land in a follow-up."
    )


@tokenizer.command("decode")
@click.argument("token_ids", nargs=-1, type=int)
@click.option(
    "--tokenizer-path",
    default="artifacts/tokenizers/default/tokenizer.json",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=str),
    help="Path to the serialized tokenizer JSON file to use for decoding.",
)
def tokenizer_decode(token_ids: tuple[int, ...], tokenizer_path: str) -> None:
    """Decode token IDs with a trained tokenizer."""
    del token_ids, tokenizer_path
    raise click.ClickException(
        "tokenizer decode pipeline not yet implemented; will land in a follow-up."
    )


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
