"""Canonical Hugging Face tokenizer adapter surface."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from codex_ml.interfaces.tokenizer import TokenizerAdapter
from codex_ml.plugins.registries import tokenizers

try:  # pragma: no cover - optional dependency guard
    from tokenizers import Tokenizer as _FastTokenizer  # type: ignore
except Exception:  # pragma: no cover - dependency missing
    _FastTokenizer = None  # type: ignore[assignment]


@tokenizers.register("hf_tokenizer_json")
class HFTokenizerAdapter(TokenizerAdapter):
    """Adapter for Hugging Face ``tokenizers`` JSON artefacts."""

    def __init__(
        self,
        tokenizer_path: str,
        *,
        pad_token: str | None = None,
        eos_token: str | None = None,
    ) -> None:
        if _FastTokenizer is None:
            raise ImportError(
                "tokenizers is required for HFTokenizerAdapter; "
                "install it with `pip install tokenizers`."
            )

        pad_token = pad_token or "<pad>"
        eos_token = eos_token or "</s>"

        self._tokenizer = _FastTokenizer.from_file(str(tokenizer_path))
        self._pad_id = self._resolve_special_token(
            [pad_token, "<pad>", "[PAD]", "<PAD>"],
            default=0,
        )
        self._eos_id = self._resolve_special_token(
            [eos_token, "</s>", "<eos>", "[EOS]"],
            default=1,
        )

    def _resolve_special_token(self, candidates: Sequence[str], default: int) -> int:
        for candidate in candidates:
            try:
                idx = self._tokenizer.token_to_id(candidate)
            except Exception:
                idx = None
            if idx is not None and idx >= 0:
                return int(idx)
        return int(default)

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        encoding = self._tokenizer.encode(text, add_special_tokens=add_special_tokens)
        return list(getattr(encoding, "ids", []))

    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        return self._tokenizer.decode(list(ids), skip_special_tokens=skip_special_tokens)

    @property
    def vocab_size(self) -> int:
        try:
            return int(self._tokenizer.get_vocab_size())
        except Exception:
            return 0

    @property
    def pad_token_id(self) -> int:
        return int(self._pad_id)

    @property
    def eos_token_id(self) -> int:
        return int(self._eos_id)

    # Backwards-compatible aliases
    @property
    def pad_id(self) -> int:
        return int(self._pad_id)

    @property
    def eos_id(self) -> int:
        return int(self._eos_id)


__all__ = ["HFTokenizerAdapter"]
