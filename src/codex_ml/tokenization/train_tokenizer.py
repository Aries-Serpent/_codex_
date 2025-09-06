"""Utilities for training and inspecting tokenizers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

try:
    import hydra
    from omegaconf import MISSING
except Exception:  # pragma: no cover - optional dependency
    hydra = None
    MISSING = object()  # type: ignore

from . import BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN
from .sentencepiece_adapter import SentencePieceAdapter


@dataclass
class TrainTokenizerConfig:
    """Configuration for :func:`main`."""

    input_file: str = MISSING  # type: ignore[assignment]
    output_dir: str = "tokenizer"
    vocab_size: int = 32000
    character_coverage: float = 0.9995
    model_type: str = "bpe"


def _export_hf_tokenizer(model_path: Path, output_dir: Path) -> None:
    """Attempt to export a ``tokenizer.json`` using ``transformers``."""
    try:  # pragma: no cover - optional dependency
        from transformers import PreTrainedTokenizerFast

        tok = PreTrainedTokenizerFast(tokenizer_file=str(model_path))
        tok.add_special_tokens(
            {
                "pad_token": PAD_TOKEN,
                "bos_token": BOS_TOKEN,
                "eos_token": EOS_TOKEN,
                "unk_token": UNK_TOKEN,
            }
        )
        tok.save_pretrained(str(output_dir))
    except Exception as exc:  # pragma: no cover - best effort
        logging.warning("Could not export tokenizer.json via transformers: %s", exc)


def run(cfg: TrainTokenizerConfig) -> None:
    """Entry point for training a SentencePiece tokenizer."""
    output = Path(cfg.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    model_path = output / "tokenizer.model"
    adapter = SentencePieceAdapter(model_path)
    adapter.train_or_load(
        cfg.input_file,
        vocab_size=cfg.vocab_size,
        character_coverage=cfg.character_coverage,
        model_type=cfg.model_type,
    )
    _export_hf_tokenizer(model_path, output)
    logging.info("Tokenizer written to %s", output)


if hydra is not None:  # pragma: no cover - hydra integration

    @hydra.main(config_path="../../configs", config_name="train_tokenizer", version_base=None)
    def main(cfg: TrainTokenizerConfig) -> None:  # type: ignore[misc]
        run(cfg)
else:  # pragma: no cover - fallback when hydra missing

    def main(cfg: TrainTokenizerConfig) -> None:  # type: ignore[override]
        run(cfg)


__all__ = ["TrainTokenizerConfig", "run", "main"]
