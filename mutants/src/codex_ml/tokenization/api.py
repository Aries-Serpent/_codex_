"""Tokenization API exports with deprecation helpers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

import warnings  # noqa: E402
from collections.abc import Iterable, Sequence  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import (  # noqa: E402
    Optional,
    cast,
)

from codex_ml.interfaces.contracts import validate_tokenizer_contract  # noqa: E402
from codex_ml.interfaces.tokenizer import HFTokenizer  # noqa: E402

from ._protocols import TokenizerAdapter  # noqa: E402 — re-exported for backward compat
from ._types import (  # noqa: E402 — re-exported
    BOS_TOKEN,
    EOS_TOKEN,
    PAD_TOKEN,
    UNK_TOKEN,
)
from .adapter import WhitespaceTokenizer  # noqa: E402

# HFTokenizerAdapter and SPTokenizer are optional-dependency attributes exposed via
# __getattr__ below (and __init__.py).  They must NOT be bound at module level to
# None/fallback values here — doing so would make them *exist* as attributes, which
# would prevent __getattr__ from ever firing and would return None to callers instead
# of the intended lazy import or a helpful ModuleNotFoundError.
if TYPE_CHECKING:  # pragma: no cover
    from .hf_tokenizer import HFTokenizerAdapter
    from .sp_trainer import SPTokenizer


def _load_hf_adapter() -> type:
    try:
        from .hf_tokenizer import HFTokenizerAdapter as adapter
    except ModuleNotFoundError as exc:  # pragma: no cover - surfaced to callers
        missing = (exc.name or "").split(".", 1)[0]
        if missing == "transformers":
            raise ModuleNotFoundError(
                "Tokenizer operations that rely on Hugging Face tokenizers require the optional "
                "'transformers' dependency.",
                name="transformers",
            ) from exc
        raise
    return adapter


def load_tokenizer(
    name: Optional[str] = None,
    path: Optional[str] = None,
    *,
    use_fast: bool = True,
    allow_remote: bool = False,
) -> TokenizerAdapter:
    """Load a tokenizer by name or filesystem path."""

    target = path or name
    if target and str(target).endswith(".model"):
        from .sentencepiece_adapter import SentencePieceAdapter

        adapter = cast(TokenizerAdapter, SentencePieceAdapter(Path(target)).load())
        validate_tokenizer_contract(adapter)
        return adapter
    adapter = _load_hf_adapter()
    instance = adapter.load(target, use_fast=use_fast)  # type: ignore[attr-defined]
    if all(hasattr(instance, name) for name in ("encode", "decode", "add_special_tokens")):
        validate_tokenizer_contract(instance)
    return instance


def get_tokenizer(*args, **kwargs) -> TokenizerAdapter:
    """Alias maintained for compatibility."""

    return load_tokenizer(*args, **kwargs)


def _load_sp_tokenizer() -> type:
    try:
        from .sp_trainer import SPTokenizer as tokenizer
    except ModuleNotFoundError as exc:  # pragma: no cover - surfaced to callers
        missing = (exc.name or "").split(".", 1)[0]
        if missing == "sentencepiece":
            raise ModuleNotFoundError(
                "Tokenizer operations that rely on SentencePiece require the optional 'sentencepiece' dependency.",  # noqa: E501
                name="sentencepiece",
            ) from exc
        raise
    return tokenizer


def _load_export(name: str) -> type:  # pragma: no cover - thin lazy import shim
    if name == "HFTokenizerAdapter":
        return _load_hf_adapter()
    if name == "SPTokenizer":
        return _load_sp_tokenizer()
    raise AttributeError(name)


def __getattr__(name: str) -> type:
    return _load_export(name)


def pad_sequences(
    batch: Sequence[Sequence[int]] | Iterable[Sequence[int]],
    *,
    pad_id: int = 0,
    max_length: Optional[int] = None,
    truncate: bool = True,
    return_attention_mask: bool = False,
) -> list[list[int]] | tuple[list[list[int]], list[list[int]]]:
    """Pad or truncate a batch of token sequences to a uniform length.

    Parameters
    ----------
    batch:
        Iterable of token id sequences.
    pad_id:
        Token id used for padding. Defaults to ``0``.
    max_length:
        Target length. When omitted the longest sequence length in ``batch`` is
        used. A value of ``0`` is invalid and raises ``ValueError``.
    truncate:
        When ``False`` an error is raised if any sequence exceeds
        ``max_length``. Defaults to ``True`` (truncates longer sequences).
    return_attention_mask:
        When ``True`` also return attention masks where ``1`` denotes a real
        token and ``0`` denotes padding.

    Returns
    -------
    list[list[int]] | tuple[list[list[int]], list[list[int]]]
        Padded sequences and optional attention masks.
    """

    sequences = [list(seq) for seq in batch]
    if not sequences:
        raise ValueError("batch must contain at least one sequence")

    lengths = [len(seq) for seq in sequences]
    if max_length is None:
        target = max(lengths)
    else:
        if max_length <= 0:
            raise ValueError("max_length must be positive")
        target = max_length

    padded: list[list[int]] = []
    masks: list[list[int]] = []

    for seq in sequences:
        current = list(seq)
        if len(current) > target:
            if not truncate:
                raise ValueError(
                    f"Sequence length {len(current)} exceeds max_length {target} and truncate is False"  # noqa: E501
                )
            current = current[:target]
        pad_needed = target - len(current)
        current = current + [pad_id] * pad_needed
        padded.append(current)
        masks.append([1] * (target - pad_needed) + [0] * pad_needed)

    return (padded, masks) if return_attention_mask else padded


def deprecated_legacy_access(name: str):
    """Emit deprecation warning and provide legacy attribute access when possible."""

    legacy_map = {
        "TokenizerAdapter": lambda: TokenizerAdapter,
        "load_tokenizer": lambda: get_tokenizer,
        "get_tokenizer": lambda: get_tokenizer,
        "BOS_TOKEN": lambda: BOS_TOKEN,
        "EOS_TOKEN": lambda: EOS_TOKEN,
        "PAD_TOKEN": lambda: PAD_TOKEN,
        "UNK_TOKEN": lambda: UNK_TOKEN,
        "WhitespaceTokenizer": lambda: WhitespaceTokenizer,
        "HFTokenizer": lambda: HFTokenizer,
        "HFTokenizerAdapter": _load_hf_adapter,
        "SPTokenizer": _load_sp_tokenizer,
        "pad_sequences": lambda: pad_sequences,
    }
    provider = legacy_map.get(name)
    if provider is None:
        return None
    warnings.warn(
        "Accessing 'codex_ml.tokenization.%s' is deprecated; import from 'codex_ml.tokenization.api' instead."  # noqa: E501
        % name,
        DeprecationWarning,
        stacklevel=3,
    )
    try:
        value = provider()
    except ModuleNotFoundError as e:
        type(e).__name__
        logger.debug("ModuleNotFoundError: <ERROR_TYPE>")
        logger.warning("ModuleNotFoundError: <ERROR_TYPE>", exc_info=True)
        raise
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        if name == "SPTokenizer":  # pragma: no cover - optional dependency guard
            raise
        raise
    return value


__all__ = [
    "BOS_TOKEN",
    "EOS_TOKEN",
    "PAD_TOKEN",
    "UNK_TOKEN",
    "HFTokenizer",
    "HFTokenizerAdapter",
    "SPTokenizer",
    "TokenizerAdapter",
    "WhitespaceTokenizer",
    "deprecated_legacy_access",
    "get_tokenizer",
    "load_tokenizer",
    "pad_sequences",
]
