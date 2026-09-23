"""
Hf Adapter Module

This module provides functionality for hf adapter.

Usage:
    from tokenization.hf_adapter import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


from collections.abc import Iterable, Sequence  # noqa: E402

from codex_ml.interfaces.tokenizer import TokenizerAdapter  # noqa: E402

# Import the registry lazily to avoid partial-initialization issues during package
# import and to keep optional dependencies safe in readiness checks.
try:
    from codex_ml.plugins.registries import tokenizers  # noqa: E402
except (ImportError, AttributeError, ValueError, TypeError):  # pragma: no cover - best effort
    tokenizers = None

try:  # pragma: no cover - optional dependency guard
    from tokenizers import Tokenizer as _FastTokenizer
except (ValueError, TypeError, ImportError, AttributeError):  # pragma: no cover - dependency missing
    _FastTokenizer = None


def _register_hf_adapter() -> None:
    """Register the adapter only when the registry is available and initialized."""
    if tokenizers is not None:
        try:
            tokenizers.register("hf_tokenizer_json")(HFTokenizerAdapter)
        except (AttributeError, ValueError, TypeError):
            logger.debug("HFTokenizerAdapter registration skipped during partial initialization", exc_info=True)


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
            except (ValueError, TypeError):
                logger.warning("Exception occurred", exc_info=True)
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
        except (ValueError, TypeError, RuntimeError):
            logger.warning("Exception occurred", exc_info=True)
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


_register_hf_adapter()

__all__ = ["HFTokenizerAdapter"]
