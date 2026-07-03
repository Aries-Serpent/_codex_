"""Tokenizer-related Typer commands.

The CLI is feature-flagged via ``CODEX_ENABLE_TOKENIZER_CLI`` so that
installations can opt out by clearing the environment variable.  When the flag
is enabled the ``train`` command loads a tokenizer configuration from disk,
normalises a handful of convenience overrides and delegates to the existing
``codex_ml.tokenization.train_tokenizer`` helpers.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from codex.logging.structured_logger import logger
from codex_ml.utils.optional import optional_import

typer, _HAS_TYPER = optional_import("typer")
yaml, _HAS_YAML = optional_import("yaml")

if TYPE_CHECKING:  # pragma: no cover - typing only
    from codex_ml.tokenization.train_tokenizer import TrainTokenizerConfig as _TrainTokenizerConfig
else:
    _TrainTokenizerConfig = Any

if typer is not None and hasattr(typer, "Typer"):
    _Typer = typer.Typer
else:  # pragma: no cover - Typer missing in environment
    typer = None

    class _FallbackTyper:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("Typer is required for codex_ml.cli.tokenizer")

    _Typer = _FallbackTyper


app = _Typer(help="Tokenizer utilities")


def _feature_enabled() -> bool:
    value = os.getenv("CODEX_ENABLE_TOKENIZER_CLI", "1").lower()
    return value in {"1", "true", "yes", "on"}


def _echo(message: str) -> None:
    if typer is not None:
        typer.echo(message)
    else:  # pragma: no cover - Typer missing
        logger.info(message)


def _load_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if _HAS_YAML else json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Tokenizer config at {path} must be a mapping")
    return data


def _coerce_config(data: dict[str, Any]) -> _TrainTokenizerConfig:
    from codex_ml.tokenization import train_tokenizer as trainer

    return trainer.TrainTokenizerConfig(**data)


def _prepare_config(
    config_path: Path,
    *,
    output_dir: Optional[Path],
    seed: int,
    force: bool,
) -> _TrainTokenizerConfig:
    data = _load_mapping(config_path)
    cfg = _coerce_config(data)

    if output_dir is not None:
        cfg.out_dir = str(output_dir)
    target_dir = Path(cfg.out_dir) / cfg.name
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_dir.exists():
        if not force:
            raise FileExistsError(
                f"Tokenizer output {target_dir} already exists; pass --force to overwrite"
            )
        shutil.rmtree(target_dir)

    cfg.seed = int(seed)
    return cfg


def train(
    config: str = "configs/training/tokenizer/offline/tiny_vocab.yaml",
    output_dir: Optional[Path] = None,
    seed: int = 42,
    force: bool = False,
) -> None:
    """Train a tokenizer according to the supplied configuration file."""

    if not _feature_enabled():
        _echo("Tokenizer CLI is disabled via CODEX_ENABLE_TOKENIZER_CLI")
        if typer is not None:
            raise typer.Exit(code=1)
        raise SystemExit(1)

    from codex_ml.tokenization import train_tokenizer as trainer

    config_path = Path(config)
    if not config_path.exists():
        raise FileNotFoundError(f"Tokenizer config not found: {config_path}")

    cfg = _prepare_config(config_path, output_dir=output_dir, seed=seed, force=force)
    trainer.train(cfg)
    _echo(f"Tokenizer training invoked (config={config_path}, output_dir={cfg.out_dir})")


if typer is not None:  # pragma: no branch - guard keeps decorator import-safe
    app.command("train")(train)


__all__ = ["app", "train"]
