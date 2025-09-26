"""Minimal SentencePiece tokenizer trainer/adapter.

This utility intentionally keeps runtime dependencies optional. The
``sentencepiece`` package is imported lazily to avoid import-time errors when
tokenizer training is not required. The resulting tokenizer implements the
``TrainableTokenizerProtocol`` for use in lightweight training/evaluation
workflows.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from codex_ml.interfaces.tokenizer import TrainableTokenizerProtocol

try:  # pragma: no cover - optional dependency
    import sentencepiece as spm  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    spm = None  # type: ignore[assignment]

__all__ = ["SPTokenizer"]


def _require_sentencepiece() -> "spm":  # type: ignore[name-defined]
    if spm is None:  # pragma: no cover - runtime guard
        raise ImportError(
            "sentencepiece is required for SPTokenizer; install 'sentencepiece' to use the trainer"
        )
    return spm  # type: ignore[return-value]


class SPTokenizer(TrainableTokenizerProtocol):
    """Minimal SentencePiece-backed tokenizer implementation."""

    def __init__(self, model_file: str):
        module = _require_sentencepiece()
        self._model_path = Path(model_file)
        self._sp = module.SentencePieceProcessor(model_file=str(self._model_path))

    # ------------------------------------------------------------------
    # Encoding helpers
    # ------------------------------------------------------------------
    def encode(
        self,
        text: str,
        *,
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        padding: bool | str = False,
        truncation: bool | str = False,
        **_: object,
    ) -> List[int]:
        add_bos = add_special_tokens
        add_eos = add_special_tokens
        ids = list(
            self._sp.encode(
                text,
                out_type=int,
                add_bos=add_bos,
                add_eos=add_eos,
            )
        )
        if max_length is not None:
            if bool(truncation) and len(ids) > max_length:
                ids = ids[:max_length]
            if bool(padding) and len(ids) < max_length:
                pad_id = self._sp.pad_id() if hasattr(self._sp, "pad_id") else 0
                ids.extend([pad_id] * (max_length - len(ids)))
        return ids

    def batch_encode(self, texts: Iterable[str], **kwargs: object) -> List[List[int]]:
        return [self.encode(text, **kwargs) for text in texts]

    def decode(
        self,
        ids: Iterable[int],
        *,
        skip_special_tokens: bool = True,
        **_: object,
    ) -> str:
        if skip_special_tokens:
            skip_ids = {
                getattr(self._sp, "pad_id", lambda: -1)(),
                getattr(self._sp, "bos_id", lambda: -1)(),
                getattr(self._sp, "eos_id", lambda: -1)(),
            }
            filtered = [int(i) for i in ids if int(i) not in skip_ids]
        else:
            filtered = [int(i) for i in ids]
        return self._sp.decode(filtered)

    def batch_decode(
        self,
        batch_ids: Iterable[Iterable[int]],
        **kwargs: object,
    ) -> List[str]:
        return [self.decode(ids, **kwargs) for ids in batch_ids]

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save(self, path: str) -> None:
        pointer = Path(path)
        pointer.parent.mkdir(parents=True, exist_ok=True)
        # Persist a copy of the model next to the pointer for portability.
        model_copy = pointer.with_suffix(".model")
        shutil.copy2(self._model_path, model_copy)
        pointer.write_text(str(model_copy))

    @classmethod
    def load(cls, path: str) -> "SPTokenizer":
        pointer = Path(path)
        if not pointer.exists():
            raise FileNotFoundError(f"tokenizer pointer not found: {pointer}")
        target = pointer.read_text().strip()
        model_path = Path(target)
        if not model_path.is_absolute():
            if model_path.exists():
                model_path = model_path.resolve()
            else:
                model_path = (pointer.parent / model_path).resolve()
        if not model_path.exists():
            raise FileNotFoundError(f"SentencePiece model not found: {model_path}")
        return cls(str(model_path))

    # ------------------------------------------------------------------
    # Training helper
    # ------------------------------------------------------------------
    @classmethod
    def train(
        cls,
        *,
        input_files: Sequence[str],
        vocab_size: int = 32000,
        model_type: str = "bpe",
        special_tokens: Optional[Sequence[str]] = None,
        character_coverage: float = 0.9995,
        seed: int = 17,
        output_dir: str = "artifacts/tokenizer",
    ) -> "SPTokenizer":
        module = _require_sentencepiece()
        if not input_files:
            raise ValueError("input_files must contain at least one corpus file")

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        model_prefix = out_dir / "spm"

        tokens = list(special_tokens or ("<pad>", "<bos>", "<eos>"))
        # Ensure pad/bos/eos exist in the list and maintain deterministic order.
        defaults = ["<pad>", "<bos>", "<eos>"]
        for tok in defaults:
            if tok not in tokens:
                tokens.insert(defaults.index(tok), tok)
        extra_symbols = [tok for tok in tokens if tok not in defaults]

        trainer_args = {
            "input": ",".join(str(Path(f)) for f in input_files),
            "model_prefix": str(model_prefix),
            "vocab_size": int(vocab_size),
            "model_type": model_type,
            "character_coverage": float(character_coverage),
            "pad_id": 0,
            "bos_id": 1,
            "eos_id": 2,
            "unk_id": 3,
            "seed": int(seed),
            "shuffle_input_sentence": False,
            "input_sentence_size": 0,
            "user_defined_symbols": list(dict.fromkeys(extra_symbols)),
        }

        module.SentencePieceTrainer.train(**trainer_args)
        model_file = f"{model_prefix}.model"
        pointer_path = out_dir / "tokenizer.pointer"
        pointer_path.write_text(model_file)
        return cls(model_file)
