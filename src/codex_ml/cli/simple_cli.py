"""Lightweight click-based CLI for common Codex ML workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from codex_ml.modeling.codex_model import CodexModel
from codex_ml.training import run_functional_training
from codex_ml.utils.optional import optional_import

_yaml, _HAS_YAML = optional_import("yaml")
_tokenizer_pipeline, _HAS_TOKENIZER_PIPELINE = optional_import("codex_ml.tokenization.pipeline")

if _HAS_TOKENIZER_PIPELINE and _tokenizer_pipeline is not None:
    run_tokenizer_train = _tokenizer_pipeline.run_train
    TokenizerPipelineError = _tokenizer_pipeline.TokenizerPipelineError
else:  # pragma: no cover - exercised when optional deps missing
    run_tokenizer_train = None
    TokenizerPipelineError = RuntimeError


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise click.ClickException(f"Config file not found: {path}")
    if path.suffix in {".yaml", ".yml"}:
        if not _HAS_YAML or _yaml is None:
            raise click.ClickException("PyYAML is required to parse YAML configs")
        data = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise click.ClickException("Training configuration must be a mapping")
    return data


@click.group()
def cli() -> None:
    """Codex ML command line interface."""


@cli.command()
@click.option("--model", "model_name", default="gpt2", show_default=True)
@click.option("--prompt", default="Hello Codex", show_default=True)
@click.option("--max-tokens", default=32, show_default=True, type=int)
@click.option("--temperature", default=0.8, show_default=True, type=float)
@click.option("--device", default=None, help="Override device placement (cpu/cuda)")
@click.option("--dtype", default=None, help="Torch dtype name (e.g. float16)")
def infer(
    model_name: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    device: str | None,
    dtype: str | None,
) -> None:
    """Generate text from a prompt using a pretrained model."""

    model = CodexModel(model_name, device=device, dtype=dtype)
    output = model.generate(prompt, max_tokens=max_tokens, temperature=temperature)
    click.echo(output)


@cli.command("train-model")
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    required=True,
    help="Path to a JSON or YAML training configuration.",
)
@click.option("--resume", is_flag=True, help="Resume from checkpoint when available.")
def train_model(config_path: Path, resume: bool) -> None:
    """Run the functional trainer using a configuration file."""

    config = _load_config(config_path)
    result = run_functional_training(config, resume=resume)
    if result is not None:
        click.echo(json.dumps(result, indent=2))


@cli.command("build-tokenizer")
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    required=True,
    help="Tokenizer YAML configuration to execute.",
)
@click.option("--dry-run", is_flag=True, help="Validate configuration without training.")
def build_tokenizer(config_path: Path, dry_run: bool) -> None:
    """Train a tokenizer via the offline tokenization pipeline."""

    if run_tokenizer_train is None:
        raise click.ClickException(
            "Tokenization pipeline dependencies are missing; "
            "install tokenizers to enable this command."
        )
    try:
        result_path = run_tokenizer_train(str(config_path), dry_run=dry_run)
    except TokenizerPipelineError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(str(result_path))


def main(argv: list[str] | None = None) -> int:
    result = cli.main(args=argv, prog_name="codex-cli", standalone_mode=False)
    return 0 if result is None else int(result)


__all__ = ["cli", "main"]
