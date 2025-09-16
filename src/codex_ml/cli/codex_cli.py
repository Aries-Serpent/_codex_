from __future__ import annotations

from typing import NoReturn, Optional

import click

from codex_ml.config import ConfigError, load_app_config
from codex_ml.telemetry import start_metrics_server

DEFAULT_TOKENIZER_CONFIG = "configs/tokenization/base.yaml"
DEFAULT_TOKENIZER_JSON = "artifacts/tokenizers/default/tokenizer.json"


@click.group()
def codex() -> None:
    """Codex command line interface."""


TOKENIZER_STUB_MESSAGE = "tokenizer {command} not yet implemented; coming in EPIC 1 PR-2."


def _tokenizer_stub(command: str) -> NoReturn:
    raise click.ClickException(TOKENIZER_STUB_MESSAGE.format(command=command))


@codex.group()
def tokenizer() -> None:
    """Tokenizer pipeline utilities."""


@tokenizer.command("train")
@click.option(
    "--config",
    default=DEFAULT_TOKENIZER_CONFIG,
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
    default=DEFAULT_TOKENIZER_CONFIG,
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
    default=DEFAULT_TOKENIZER_JSON,
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
    default=DEFAULT_TOKENIZER_JSON,
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
    default="configs/tokenization/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the tokenizer YAML configuration.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Retrain even if dataset checksums match the cached manifest.",
)
def tokenizer_train(config: str, force: bool) -> None:
    """Train or refresh the tokenizer cache (stub)."""
    _tokenizer_stub("train")


@tokenizer.command(name="validate")
@click.option(
    "--config",
    default="configs/tokenization/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Configuration file to validate against the tokenizer manifest.",
)
def tokenizer_validate(config: str) -> None:
    """Validate tokenizer cache manifests (stub)."""
    _tokenizer_stub("validate")


@tokenizer.command(name="encode")
@click.argument("text", nargs=-1)
@click.option(
    "--tokenizer-path",
    default="artifacts/tokenizers/default/tokenizer.json",
    show_default=True,
    type=click.Path(exists=False, dir_okay=False, path_type=str),
    help="Tokenizer model JSON to load for encoding.",
)
@click.option(
    "--no-add-special-tokens",
    is_flag=True,
    help="Disable automatic inclusion of special tokens during encoding.",
)
def tokenizer_encode(
    text: tuple[str, ...], tokenizer_path: str, no_add_special_tokens: bool
) -> None:
    """Encode text to token IDs using the configured tokenizer (stub)."""
    _tokenizer_stub("encode")


@tokenizer.command(name="decode")
@click.argument("ids", nargs=-1, type=int)
@click.option(
    "--tokenizer-path",
    default="artifacts/tokenizers/default/tokenizer.json",
    show_default=True,
    type=click.Path(exists=False, dir_okay=False, path_type=str),
    help="Tokenizer model JSON to load for decoding.",
)
def tokenizer_decode(ids: tuple[int, ...], tokenizer_path: str) -> None:
    """Decode token IDs to text using the configured tokenizer (stub)."""
    _tokenizer_stub("decode")


@codex.command()
@click.option(
    "--config",
    default="configs/training/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the training YAML configuration.",
)
@click.argument("overrides", nargs=-1)
@click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
@click.option("--seed", type=int, default=None, help="Override the random seed from the config.")
def train(config: str, overrides: Tuple[str, ...], resume: bool, seed: Optional[int]) -> None:
    """Train a language model using the Codex functional trainer."""
    from codex_ml.training import run_functional_training
    from codex_ml.utils.error_log import log_error as log_training_error

    try:
        cfg_obj, raw_cfg = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    if seed is not None:
        if hasattr(raw_cfg, "training") and hasattr(raw_cfg.training, "seed"):
            raw_cfg.training.seed = seed
        else:
            raw_cfg.seed = seed
        cfg_obj.training.seed = seed

    try:
        run_functional_training(config=raw_cfg, resume=resume)
        click.echo("training complete")
    except Exception as exc:  # pragma: no cover - Click handles presentation
        log_training_error("cli.train", str(exc), f"config={config} resume={resume}")
        raise click.ClickException(str(exc)) from exc


@codex.command("metrics-server")
@click.option("--port", default=8000, show_default=True)
def metrics_server(port: int) -> None:
    if start_metrics_server(port=port):
        click.echo(f"metrics server running on {port}")
    else:
        click.echo("prometheus_client missing", err=True)


@codex.command()
@click.argument("text")
def tokenize(text: str) -> None:
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    tok = HFTokenizerAdapter.load()
    ids = tok.encode(text)
    click.echo(str(ids))


@codex.command()
def repo_map() -> None:
    click.echo("repo map not implemented")


@codex.command()
@click.option(
    "--config",
    default="configs/eval/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the evaluation configuration.",
)
@click.argument("overrides", nargs=-1)
def evaluate(config: str, overrides: Tuple[str, ...]) -> None:
    from codex_ml.eval.runner import EvaluationError, run_evaluation

    try:
        cfg_obj, _ = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    try:
        summary = run_evaluation(cfg_obj.evaluation, data_cfg=cfg_obj.data)
    except EvaluationError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    click.echo(json.dumps(summary, indent=2, sort_keys=True))


@codex.command("prepare-data")
@click.option(
    "--config",
    default="configs/data/base.yaml",
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Path to the data preparation configuration.",
)
@click.argument("overrides", nargs=-1)
def prepare_data(config: str, overrides: Tuple[str, ...]) -> None:
    from codex_ml.data.loader import DataPreparationError, prepare_data_from_config

    try:
        cfg_obj, _ = load_app_config(config, overrides)
    except ConfigError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    try:
        result = prepare_data_from_config(cfg_obj.data)
    except DataPreparationError as exc:  # pragma: no cover - Click handles presentation
        raise click.ClickException(str(exc)) from exc

    click.echo(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":  # pragma: no cover
    codex()
