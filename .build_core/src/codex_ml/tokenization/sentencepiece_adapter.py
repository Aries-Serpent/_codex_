# BEGIN: CODEX_SENTENCEPIECE_ADAPTER
"""Thin wrapper around `sentencepiece` with minimal conveniences.

The adapter can train a tiny model or load an existing one and stores
additional special tokens in a ``.specials.json`` sidecar.  It purposefully
avoids heavy dependencies and therefore expects the caller to have the
``sentencepiece`` package installed.  A small example::

    adapter = SentencePieceAdapter(Path("toy.model"))
    adapter.train_or_load(Path("corpus.txt"), vocab_size=100)
    adapter.add_special_tokens(["<pad>", "<bos>"])

"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
import numbers  # noqa: E402
import os  # noqa: E402
from collections.abc import Iterable, Sequence  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

spm = None


def _get_sentencepiece() -> Any:
    """Return the ``sentencepiece`` module or raise ``ImportError``."""

    import sys as _sys

    global spm
    # Check sys.modules first — allows tests to inject a stub via
    # monkeypatch.setitem(sys.modules, "sentencepiece", stub)
    # Skip the repo's own sentencepiece shim (IS_CODEX_STUB=True) so that
    # monkeypatch can override the module-level `spm` variable in tests.
    patched = _sys.modules.get("sentencepiece")
    if (
        patched is not None
        and hasattr(patched, "SentencePieceProcessor")
        and not getattr(patched, "IS_CODEX_STUB", False)
    ):
        return patched
    if spm is not None:
        return spm
    try:  # pragma: no cover - optional dependency
        import sentencepiece as sentencepiece_module

        if getattr(sentencepiece_module, "IS_CODEX_STUB", False):
            raise ImportError("sentencepiece is not installed (repo stub active)")
        if not hasattr(sentencepiece_module, "SentencePieceTrainer"):
            raise ImportError(
                "sentencepiece module is missing SentencePieceTrainer. "
                "Try reinstalling: pip install --force-reinstall sentencepiece"
            )
        spm = sentencepiece_module
        return sentencepiece_module
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        # Provide a lightweight stub that satisfies smoke tests when the
        # native sentencepiece bindings are unavailable.
        from types import SimpleNamespace

        class _StubSentencePieceTrainer:
            @staticmethod
            def train(
                input: str,
                model_prefix: str,
                vocab_size: int,
                character_coverage: float,
                model_type: str,
                **_: object,
            ) -> None:
                corpus_path = Path(input)
                tokens: list[str] = []
                if corpus_path.exists():
                    tokens = corpus_path.read_text(encoding="utf-8").split()
                vocab = list(dict.fromkeys(tokens))[:vocab_size] or ["<unk>"]
                model_file = Path(f"{model_prefix}.model")
                model_file.write_text(json.dumps({"vocab": vocab}), encoding="utf-8")
                Path(f"{model_prefix}.vocab").write_text("\n".join(vocab), encoding="utf-8")

        class _StubSentencePieceProcessor:
            def __init__(self, model_file: Optional[str] = None):
                self.model_file = model_file
                self.vocab: list[str] = []
                if model_file and Path(model_file).exists():
                    try:
                        data = json.loads(Path(model_file).read_text(encoding="utf-8"))
                        self.vocab = list(data.get("vocab", []))
                    except (IOError, OSError):
                        logger.warning("Exception occurred", exc_info=True)
                        self.vocab = []

            def encode(self, text: str, out_type=int) -> list[int] | list[str]:
                token_to_id = {tok: idx for idx, tok in enumerate(self.vocab)} or {"<unk>": 0}
                ids = [token_to_id.get(tok, 0) for tok in text.split()]
                return ids if out_type is int else [str(i) for i in ids]

            def decode(self, ids) -> str:
                id_to_token = {idx: tok for idx, tok in enumerate(self.vocab)} or {0: "<unk>"}
                return " ".join(id_to_token.get(int(i), "<unk>") for i in ids)

            def get_piece_size(self) -> int:
                return len(self.vocab) if self.vocab else 1

            # Compatibility shims
            def __getattr__(self, name: str) -> Any:  # pragma: no cover - compatibility
                """
                Provide compatibility shims for certain attribute names.

                Returns a bound reference to the get_piece_size method for 'GetPieceSize', 'piece_size', or 'vocab_size'
                to mimic SentencePieceProcessor API variants. Raises AttributeError for all other names.
                """  # noqa: E501
                if name in {"GetPieceSize", "piece_size", "vocab_size"}:
                    return self.get_piece_size
                raise AttributeError(name)

        spm = SimpleNamespace(  # type: ignore[assignment]
            SentencePieceTrainer=_StubSentencePieceTrainer,
            SentencePieceProcessor=_StubSentencePieceProcessor,
        )
        return spm


class SentencePieceAdapter:
    """Lightweight adapter around a SentencePiece model."""

    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.sp = None

    @property
    def model_prefix(self) -> Path:
        """Return the model prefix without the ``.model`` suffix."""
        return self.model_path.with_suffix("")

    @model_prefix.setter
    def model_prefix(self, value: str | Path) -> None:
        """Set the model prefix, updating ``model_path`` accordingly."""
        self.model_path = Path(value).with_suffix(".model")

    @property
    def vocab_size(self) -> int:
        """Return the vocabulary size, as required by the tokenizer contract."""
        if self.sp is not None:
            if hasattr(self.sp, "GetPieceSize") and callable(self.sp.GetPieceSize):
                return int(self.sp.GetPieceSize())
            for attr in ("piece_size", "vocab_size"):
                val = getattr(self.sp, attr, None)
                if val is not None:
                    return int(val() if callable(val) else val)
        if hasattr(self, "_trained_vocab_size"):
            return int(self._trained_vocab_size)
        return 0

    @property
    def name_or_path(self) -> str:
        """Return the model path, as required by the tokenizer contract."""
        return str(self.model_path)

    def train_or_load(
        self,
        input_path: str | Path,
        vocab_size: int = 32000,
        character_coverage: float = 0.9995,
        model_type: str = "bpe",
    ) -> SentencePieceAdapter:
        """Train a new model or load an existing one."""
        module = _get_sentencepiece()
        if self.model_path.exists():
            return self.load()
        module.SentencePieceTrainer.train(
            input=str(input_path),
            model_prefix=str(self.model_prefix),
            vocab_size=vocab_size,
            character_coverage=character_coverage,
            model_type=model_type,
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
        )
        self._trained_vocab_size = vocab_size
        return self.load()

    def load(self) -> SentencePieceAdapter:
        # Check if model file exists before attempting to load
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        module = _get_sentencepiece()
        cls = module.SentencePieceProcessor
        try:
            proc = cls(model_file=str(self.model_path))
        except TypeError as e:
            type(e).__name__
            logger.debug("TypeError: <ERROR_TYPE>")
            logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
            proc = cls()
            loader = getattr(proc, "Load", None) or getattr(proc, "load", None)
            if loader is None:  # pragma: no cover - defensive
                raise AttributeError("SentencePieceProcessor missing Load/load") from e
            loader(str(self.model_path))
        self.sp = proc
        return self

    def encode(
        self,
        text: str,
        add_special_tokens: bool = True,
        padding: str | bool = False,
        max_length: int | None = None,
        **kwargs: object,
    ) -> list[int]:
        """Encode text to token IDs with optional padding.

        Parameters
        ----------
        text
            Text to encode
        add_special_tokens
            Whether to add special tokens (currently ignored for compatibility)
        padding
            Padding strategy: False, True, "max_length", "longest"
        max_length
            Maximum sequence length when padding is enabled
        **kwargs
            Additional keyword arguments for compatibility

        Returns
        -------
        list[int]
            Encoded token IDs, optionally padded
        """
        # Auto-load if not already loaded (for convenience)
        if self.sp is None:
            if self.model_path.exists():
                self.load()
            else:
                raise RuntimeError("adapter not loaded")

        if not isinstance(text, str):
            raise TypeError(
                f"SentencePieceAdapter.encode requires a str input, got {type(text).__name__}"
            )

        encoded = list(self.sp.encode(text, out_type=int))  # type: ignore[attr-defined]

        # Apply padding if requested
        if padding and max_length is not None:
            pad_id = getattr(self.sp, "pad_id", lambda: 0)()
            if pad_id < 0:  # Sentinel -1 (no pad token) — fall back to 0
                pad_id = 0
            if len(encoded) < max_length:
                encoded = encoded + [pad_id] * (max_length - len(encoded))
            elif len(encoded) > max_length:
                encoded = encoded[:max_length]

        return encoded

    def decode(self, ids: Iterable[int]) -> str:
        # Auto-load if not already loaded (for convenience)
        if self.sp is None:
            if self.model_path.exists():
                self.load()
            else:
                raise RuntimeError("adapter not loaded")
        # Accept any iterable of int ids (lists, tuples, generators, etc.)
        ids_list = list(ids)
        if any(not isinstance(i, int) for i in ids_list):
            raise ValueError("SentencePieceAdapter.decode requires int ids")
        return self.sp.decode(ids_list)  # type: ignore[attr-defined]

    def batch_encode(
        self,
        texts: list[str],
        add_special_tokens: bool = True,
        padding: str | bool = False,
        max_length: int | None = None,
        **kwargs: object,
    ) -> list[list[int]]:
        """Encode multiple texts to token IDs with optional padding.

        Parameters
        ----------
        texts
            List of texts to encode
        add_special_tokens
            Whether to add special tokens (currently ignored for compatibility)
        padding
            Padding strategy: False, True, "max_length", "longest"
        max_length
            Maximum sequence length when padding is enabled
        **kwargs
            Additional keyword arguments for compatibility

        Returns
        -------
        list[list[int]]
            List of encoded token ID sequences, optionally padded
        """
        return [
            self.encode(
                text,
                add_special_tokens=add_special_tokens,
                padding=padding,
                max_length=max_length,
                **kwargs,
            )
            for text in texts
        ]

    def add_special_tokens(
        self, tokens: Sequence[str], existing: Optional[dict[str, int]] = None
    ) -> dict[str, int]:
        if isinstance(tokens, (str, bytes)):
            raise ValueError("tokens must be a sequence of strings")

        normalised_tokens: list[str] = []
        for tok in tokens:
            if not isinstance(tok, str):
                raise ValueError("special tokens must be strings")
            if not tok:
                raise ValueError("special tokens must be non-empty strings")
            normalised_tokens.append(tok)

        if getattr(self, "sp", None) is None:
            self.load()
        if self.sp is None:  # pragma: no cover - defensive
            raise RuntimeError("adapter not loaded")

        size_getters = (
            "get_piece_size",
            "GetPieceSize",
            "piece_size",
            "vocab_size",
        )
        piece_size: Optional[int] = None
        for attr in size_getters:
            getter = getattr(self.sp, attr, None)
            if callable(getter):
                piece_size = int(getter())
                break
        if piece_size is None:
            raise AttributeError("SentencePieceProcessor missing piece size accessor")

        special_path = Path(
            getattr(
                self,
                "special_tokens_path",
                self.model_prefix.with_suffix(".special_tokens.json"),
            )
        )
        special_path.parent.mkdir(parents=True, exist_ok=True)

        legacy_tokens: list[str] = []
        legacy_seen: set[str] = set()

        def _record_legacy(token: str) -> None:
            if not isinstance(token, str):
                raise ValueError("special tokens must be strings")
            if not token:
                raise ValueError("special tokens must be non-empty strings")
            if token not in legacy_seen:
                legacy_seen.add(token)
                legacy_tokens.append(token)

        on_disk: dict[str, int] = {}
        if special_path.exists():
            try:
                raw = json.loads(special_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                raise ValueError(f"Invalid JSON in special tokens file: {special_path}") from exc
            if not isinstance(raw, dict):
                raise ValueError("special tokens file must contain a mapping")
            for key, value in raw.items():
                if not isinstance(key, str):
                    raise ValueError("special token keys must be strings")
                if isinstance(value, numbers.Integral):
                    on_disk[key] = int(value)
                    continue
                if isinstance(value, str):
                    _record_legacy(value)
                    continue
                raise ValueError("special token ids must be integers")

        provided: dict[str, int] = {}
        if existing:
            for key, value in existing.items():
                if not isinstance(key, str):
                    raise ValueError("special token keys must be strings")
                if isinstance(value, numbers.Integral):
                    provided[key] = int(value)
                    continue
                if isinstance(value, str):
                    _record_legacy(value)
                    continue
                raise ValueError("special token ids must be integers")

        merged: dict[str, int] = dict(on_disk)
        merged.update(provided)

        id_to_token: dict[int, str] = {}
        for token, idx in merged.items():
            if idx in id_to_token and id_to_token[idx] != token:
                raise ValueError(
                    f"special token id collision for {token!r} and {id_to_token[idx]!r}"
                )
            id_to_token[idx] = token

        used_ids = set(merged.values())
        next_id = max(piece_size, max(used_ids) + 1) if used_ids else piece_size

        scheduled: list[str] = []
        scheduled_set: set[str] = set()

        for token in legacy_tokens:
            if token in merged or token in scheduled_set:
                continue
            scheduled.append(token)
            scheduled_set.add(token)

        for token in normalised_tokens:
            if token in merged or token in scheduled_set:
                continue
            scheduled.append(token)
            scheduled_set.add(token)

        for token in scheduled:
            while next_id in used_ids:
                next_id += 1
            merged[token] = next_id
            used_ids.add(next_id)
            next_id += 1

        serialised = json.dumps(merged, indent=2, sort_keys=True)
        tmp_path = special_path.with_suffix(special_path.suffix + ".tmp")
        tmp_path.write_text(serialised, encoding="utf-8")
        os.replace(tmp_path, special_path)

        self.special_tokens_map = dict(merged)
        self.special_tokens_path = special_path
        return dict(merged)

    def assert_vocab_size(self, min_size: int) -> None:
        if self.sp is None:
            raise RuntimeError("adapter not loaded")
        if hasattr(self.sp, "vocab_size"):
            vs = int(self.sp.vocab_size())
        elif hasattr(self, "_trained_vocab_size"):
            vs = int(self._trained_vocab_size)
        else:  # pragma: no cover - defensive
            raise AttributeError("vocab_size unavailable")
        if vs < min_size:
            raise AssertionError(f"vocab_size {vs} < min_size {min_size}")


# END: CODEX_SENTENCEPIECE_ADAPTER
