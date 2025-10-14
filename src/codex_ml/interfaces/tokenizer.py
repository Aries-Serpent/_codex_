"""Tokenization interfaces and adapters.

This module merges two previous implementations into a single, backward-
compatible adapter API for tokenizers (primarily Hugging Face AutoTokenizer).

Features:
- An abstract TokenizerAdapter base class for concrete adapters.
- A lightweight Protocol (TokenizerProtocol) for structural typing.
- HFTokenizer: concrete adapter around transformers.AutoTokenizer with
  compatibility shims (batch_encode return types, batch_encode_plus alias,
  both pad_id / pad_token_id and eos_id / eos_token_id accessors).
- Defensive handling when `transformers` is not installed.
- Graceful fallbacks and comprehensive error handling to avoid raising from
  detection/encoding helpers at import time.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Iterable, Sequence
from typing import Any, Protocol

from codex_ml.plugins.registries import load_tokenizer_entry_points, tokenizers
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision

# Optional transformers import - do not raise at module import if missing.
try:  # pragma: no cover - optional dependency
    from transformers import AutoTokenizer as _AutoTokenizer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _AutoTokenizer = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from tokenizers import Tokenizer as _FastTokenizer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _FastTokenizer = None  # type: ignore


def _resolve_auto_tokenizer():
    """Attempt to import ``AutoTokenizer`` lazily.

    This allows test environments to register lightweight stubs in ``sys.modules``
    after module import without forcing callers to install the optional
    dependency. The function caches the resolved class in the module-level
    ``_AutoTokenizer`` variable for subsequent lookups.
    """

    global _AutoTokenizer
    if _AutoTokenizer is None:
        try:
            from transformers import AutoTokenizer as _Imported  # type: ignore
        except Exception:
            _AutoTokenizer = None  # ensure consistency if import keeps failing
        else:
            _AutoTokenizer = _Imported
    return _AutoTokenizer


# Public exports
__all__ = [
    "TokenizerAdapter",
    "TokenizerProtocol",
    "TrainableTokenizerProtocol",
    "HFTokenizer",
    "HFTokenizerAdapter",
    "WhitespaceTokenizer",
    "get_tokenizer",
]


class TokenizerAdapter(ABC):
    """Abstract adapter for tokenization backends.

    Implementations should provide deterministic encode/decode for reproducibility
    and expose key ids for padding and end-of-sequence handling.

    Backwards-compatibility notes:
    - Older code expects `pad_id` and `eos_id` properties; newer callers may use
      `pad_token_id` / `eos_token_id`. Both are provided by implementations.
    - `batch_encode` may return a List[List[int]] by default; adapters MAY also
      support returning a Hugging Face-style dict when requested.
    """

    @abstractmethod
    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        """Encode a single string into token ids."""
        ...

    def batch_encode(
        self,
        texts: Iterable[str],
        *,
        add_special_tokens: bool = True,
        return_dict: bool = False,
    ) -> list[list[int]] | dict[str, Any]:
        """Optional batch encode; default maps to encode() across inputs.

        If return_dict=True an implementation MAY return a mapping similar to
        Hugging Face tokenizer outputs (e.g. containing "input_ids").
        """
        return [self.encode(t, add_special_tokens=add_special_tokens) for t in texts]

    @abstractmethod
    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        """Decode token ids into a string."""
        ...

    def batch_decode(self, batch_ids: Iterable[Iterable[int]]) -> list[str]:
        """Optional batch decode helper - default maps to decode()."""
        return [self.decode(ids) for ids in batch_ids]

    @property
    @abstractmethod
    def vocab_size(self) -> int:
        """Return size of vocabulary."""
        ...

    @property
    def pad_id(self) -> int:
        """Return padding token id (backwards-compatible alias)."""
        v = getattr(self, "pad_token_id", None)
        return int(v or 0)

    @property
    def eos_id(self) -> int:
        """Return end-of-sequence token id (backwards-compatible alias)."""
        v = getattr(self, "eos_token_id", None)
        return int(v or 0)

    # Newer-style names (may be provided by implementations)
    @property
    def pad_token_id(self) -> int | None:
        """Preferred pad token id property; may return None if undefined."""
        return None

    @property
    def eos_token_id(self) -> int | None:
        """Preferred eos token id property; may return None if undefined."""
        return None


@tokenizers.register("whitespace")
class _CallableInt(int):
    def __new__(cls, value: int):
        return super().__new__(cls, int(value))

    def __call__(self) -> int:
        return int(self)


class WhitespaceTokenizer(TokenizerAdapter):
    """Deterministic whitespace tokenizer used when transformers is absent."""

    def __init__(self, lowercase: bool = False, append_eos: bool = True) -> None:
        self.lowercase = lowercase
        self.append_eos = append_eos
        self._token_to_id: dict[str, int] = {"[PAD]": 0, "[EOS]": 1}
        self._id_to_token: dict[int, str] = {0: "[PAD]", 1: "[EOS]"}

    def _prepare(self, text: str) -> str:
        return text.lower() if self.lowercase else text

    def __call__(
        self,
        texts: Iterable[str],
        *,
        add_special_tokens: bool = True,
        **_: Any,
    ) -> dict[str, list[list[int]]]:
        encoded = [self.encode(t, add_special_tokens=add_special_tokens) for t in texts]
        return {"input_ids": encoded}

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        tokens = [tok for tok in self._prepare(text).split() if tok]
        ids: list[int] = []
        for tok in tokens:
            if tok not in self._token_to_id:
                idx = len(self._token_to_id)
                self._token_to_id[tok] = idx
                self._id_to_token[idx] = tok
            ids.append(self._token_to_id[tok])
        if add_special_tokens and self.append_eos:
            ids.append(self.eos_token_id)
        return ids

    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        tokens: list[str] = []
        for idx in ids:
            token = self._id_to_token.get(int(idx), "")
            if skip_special_tokens and token in {"[PAD]", "[EOS]"}:
                continue
            tokens.append(token)
        return " ".join(tokens).strip()

    def convert_ids_to_tokens(self, idx: int) -> str:
        return self._id_to_token.get(int(idx), "")

    def convert_tokens_to_string(self, tokens: Iterable[str]) -> str:
        return " ".join(tokens).strip()

    @property
    def vocab_size(self) -> int:
        return _CallableInt(len(self._token_to_id))

    @property
    def pad_token_id(self) -> int:
        return _CallableInt(self._token_to_id["[PAD]"])

    @property
    def eos_token_id(self) -> int:
        return _CallableInt(self._token_to_id["[EOS]"])


class TokenizerProtocol(Protocol):
    """Structural typing Protocol for minimal tokenizer usage across the repo.

    Use this when an implementation may not subclass TokenizerAdapter but exposes
    the expected methods/properties.
    """

    def encode(
        self,
        text: str,
        *,
        add_special_tokens: bool = True,
        max_length: int | None = None,
        padding: bool | str = False,
        truncation: bool | str = False,
        **kwargs: Any,
    ) -> list[int]:
        raise NotImplementedError

    def decode(
        self,
        ids: Sequence[int],
        *,
        skip_special_tokens: bool = True,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError

    def batch_encode(self, texts: Sequence[str], **kwargs: Any) -> list[list[int]]:
        raise NotImplementedError

    def batch_decode(self, batch_ids: Sequence[Sequence[int]], **kwargs: Any) -> list[str]:
        raise NotImplementedError

    @property
    def vocab_size(self) -> int:
        raise NotImplementedError

    @property
    def pad_token_id(self) -> int | None:
        raise NotImplementedError


class TrainableTokenizerProtocol(TokenizerProtocol, Protocol):
    """Protocol for tokenizers that can be trained and persisted offline."""

    def save(self, path: str) -> None:
        raise NotImplementedError

    @classmethod
    def load(cls, path: str) -> TrainableTokenizerProtocol:
        raise NotImplementedError

    @classmethod
    def train(
        cls,
        *,
        input_files: Sequence[str],
        vocab_size: int = 32000,
        model_type: str = "bpe",
        special_tokens: Sequence[str] | None = None,
        character_coverage: float = 0.9995,
        seed: int = 17,
        output_dir: str = "artifacts/tokenizer",
    ) -> TrainableTokenizerProtocol:
        raise NotImplementedError


class HFTokenizer(TokenizerAdapter):
    """Lightweight wrapper around `transformers.AutoTokenizer`.

    This adapter intentionally preserves compatibility with both usage patterns:
    - Returns List[List[int]] by default for `batch_encode(...)`.
    - Accepts `return_dict=True` to return the raw Hugging Face-style mapping.
    - Provides both old (pad_id / eos_id) and new (pad_token_id / eos_token_id)
      property names.
    - Exposes `raw_tokenizer` and `tokenizer` properties for direct access.

    Parameters
    ----------
    name_or_path:
        Model or tokenizer identifier to pass to AutoTokenizer.from_pretrained.
    padding, truncation, max_length, use_fast:
        Passed through to tokenizer encoding calls where applicable.
    **kwargs:
        Additional keyword arguments forwarded to AutoTokenizer.from_pretrained.

    Raises
    ------
    ImportError:
        If `transformers` is not installed when an instance is created.
    """

    def __init__(
        self,
        name_or_path: str | None,
        padding: bool | str = False,
        truncation: bool | str = True,
        max_length: int | None = None,
        use_fast: bool = True,
        artifacts_dir: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._fallback: WhitespaceTokenizer | None = None
        auto_tokenizer_cls = _resolve_auto_tokenizer()
        if auto_tokenizer_cls is None:
            self._fallback = WhitespaceTokenizer()
            self._tk = self._fallback
            self.padding = padding
            self.truncation = truncation
            self.max_length = max_length
            self._decode_cache: OrderedDict[tuple[tuple[int, ...], bool], str] = OrderedDict()
            return
        # Instantiate underlying tokenizer with provided kwargs
        try:
            if artifacts_dir:
                from pathlib import Path

                from transformers import PreTrainedTokenizerFast

                tj = Path(artifacts_dir) / "tokenizer.json"
                if not tj.exists():
                    raise FileNotFoundError(f"tokenizer.json not found in {artifacts_dir}")
                self._tk = PreTrainedTokenizerFast(tokenizer_file=str(tj))
                self._tk.add_special_tokens(
                    {
                        "pad_token": "[PAD]",
                        "bos_token": "[BOS]",
                        "eos_token": "[EOS]",
                        "unk_token": "[UNK]",
                    }
                )
            else:
                if name_or_path is None:
                    raise ValueError("name_or_path or artifacts_dir must be provided")
                params = dict(kwargs)
                params.setdefault("use_fast", use_fast)
                self._tk = load_from_pretrained(
                    auto_tokenizer_cls,
                    name_or_path,
                    revision=get_hf_revision(),
                    **params,
                )
        except Exception as exc:  # pragma: no cover - defensive
            # Provide a clearer error message while preserving original exception info.
            raise RuntimeError(
                f"failed to load tokenizer '{name_or_path or artifacts_dir}': {exc}"
            ) from exc

        self.padding = padding
        self.truncation = truncation
        self.max_length = max_length
        self._decode_cache: OrderedDict[tuple[tuple[int, ...], bool], str] = OrderedDict()

    # ---- Encoding / decoding helpers ------------------------------------
    def _encode_call_kwargs(self, add_special_tokens: bool) -> dict[str, Any]:
        """Construct kwargs for tokenizer.encode / tokenizer.__call__."""
        return {
            "add_special_tokens": add_special_tokens,
            "padding": self.padding,
            "truncation": self.truncation,
            "max_length": self.max_length,
        }

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        """Encode a single string to a list of token ids.

        Falls back to a safe behaviour if underlying tokenizer call fails.
        """
        if self._fallback is not None:
            tokens = self._fallback.encode(text)
            max_len = self.max_length if isinstance(self.max_length, int) else None
            if max_len is not None and bool(self.truncation):
                tokens = tokens[:max_len]
            pad_requested = False
            if isinstance(self.padding, str):
                pad_requested = self.padding.lower() == "max_length"
            else:
                pad_requested = bool(self.padding)
            if pad_requested and max_len is not None and len(tokens) < max_len:
                pad_id = 0
                tokens = tokens + [pad_id] * (max_len - len(tokens))
            return tokens
        try:
            result = list(
                self._tk.encode(
                    text,
                    **self._encode_call_kwargs(add_special_tokens=add_special_tokens),
                )
            )
        except Exception:
            # Fallback: try a minimal encode call (some tokenizers accept simple call)
            try:
                ids = self._tk.encode(text, add_special_tokens=add_special_tokens)
                result = list(ids)
            except Exception:
                # Last resort: return empty sequence to avoid raising in user code.
                result = []
        key = tuple(result)
        decoded_skip_special = self._decode_with_fallback(key, skip_special_tokens=True)
        if decoded_skip_special is not None:
            self._cache_decoded(key, True, decoded_skip_special)
        decoded_with_special = self._decode_with_fallback(key, skip_special_tokens=False)
        if decoded_with_special is not None:
            self._cache_decoded(key, False, decoded_with_special)
        return result

    def batch_encode(
        self,
        texts: Iterable[str],
        *,
        add_special_tokens: bool = True,
        return_dict: bool = False,
    ) -> list[list[int]] | dict[str, Any]:
        """Batch encode texts.

        - By default returns List[List[int]] of input_ids for adapter consistency.
        - If return_dict=True, returns the raw Hugging Face-style dict, preserving
          backward compatibility with prior usages expecting a mapping.
        """
        if self._fallback is not None:
            encoded = []
            for t in texts:
                ids = self._fallback.encode(t)
                max_len = self.max_length if isinstance(self.max_length, int) else None
                if max_len is not None and bool(self.truncation):
                    ids = ids[:max_len]
                pad_requested = False
                if isinstance(self.padding, str):
                    pad_requested = self.padding.lower() == "max_length"
                else:
                    pad_requested = bool(self.padding)
                if pad_requested and max_len is not None and len(ids) < max_len:
                    pad_id = 0
                    ids = ids + [pad_id] * (max_len - len(ids))
                encoded.append(ids)
            if return_dict:
                return {"input_ids": encoded}
            return encoded
        try:
            enc = self._tk(
                list(texts),
                add_special_tokens=add_special_tokens,
                padding=self.padding,
                truncation=self.truncation,
                max_length=self.max_length,
                return_tensors=None,
            )
            if return_dict:
                return enc  # type: ignore[return-value]
            # Extract input_ids safely and ensure lists of ints
            input_ids = enc.get("input_ids", [])
            return [list(seq) for seq in input_ids]
        except Exception:
            # Graceful fallback: encode individually
            fallback: list[list[int]] = []
            for t in texts:
                try:
                    fallback.append(self.encode(t, add_special_tokens=add_special_tokens))
                except Exception:
                    fallback.append([])
            if return_dict:
                # Provide a minimal, consistent dictionary shape
                return {"input_ids": fallback}
            return fallback

    def batch_encode_plus(
        self,
        texts: Iterable[str],
        *,
        add_special_tokens: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Return a Hugging Face-style encoding dict (compatibility alias)."""
        # Accept extra kwargs for compatibility; forward to batch_encode via return_dict
        _ = kwargs  # intentionally accepted but ignored
        out = self.batch_encode(texts, add_special_tokens=add_special_tokens, return_dict=True)
        return out  # type: ignore[return-value]

    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        """Decode a list of token ids back to a string."""
        key = tuple(int(i) for i in ids)
        cache_key = (key, skip_special_tokens)
        cached = self._decode_cache.get(cache_key)
        if cached is not None:
            return cached
        decoded = self._decode_with_fallback(key, skip_special_tokens=skip_special_tokens)
        if decoded is None:
            # As a last resort, allow the opposite skip flag variant if available.
            other_cached = self._decode_cache.get((key, not skip_special_tokens))
            if other_cached is not None:
                return other_cached
            return ""
        self._cache_decoded(key, skip_special_tokens, decoded)
        other_key = (key, not skip_special_tokens)
        if other_key not in self._decode_cache:
            other_decoded = self._decode_with_fallback(
                key, skip_special_tokens=not skip_special_tokens
            )
            if other_decoded is not None:
                self._cache_decoded(key, not skip_special_tokens, other_decoded)
        return decoded

    def _decode_with_fallback(
        self, key: tuple[int, ...], *, skip_special_tokens: bool
    ) -> str | None:
        """Decode via the underlying tokenizer with a graceful fallback."""
        if self._fallback is not None:
            return self._fallback.decode(key, skip_special_tokens=skip_special_tokens)
        try:
            return self._tk.decode(list(key), skip_special_tokens=skip_special_tokens)
        except Exception:
            try:
                tokens = [self._tk.convert_ids_to_tokens(int(i)) for i in key]
                return self._tk.convert_tokens_to_string(tokens)
            except Exception:
                return None

    def _cache_decoded(self, key: tuple[int, ...], skip_special_tokens: bool, text: str) -> None:
        """Store decoded text in the local LRU cache."""
        self._decode_cache[(key, skip_special_tokens)] = text
        while len(self._decode_cache) > 512:
            self._decode_cache.popitem(last=False)

    def batch_decode(self, batch_ids: Iterable[Iterable[int]]) -> list[str]:
        """Decode a batch of token id sequences."""
        out: list[str] = []
        for ids in batch_ids:
            out.append(self.decode(ids))
        return out

    # ---- Metadata accessors --------------------------------------------
    @property
    def vocab_size(self) -> int:
        """Return tokenizer vocabulary size as int (0 if undefined)."""
        if self._fallback is not None:
            return _CallableInt(self._fallback.vocab_size)
        try:
            return _CallableInt(int(getattr(self._tk, "vocab_size", 0) or 0))
        except Exception:
            return _CallableInt(0)

    @property
    def pad_token_id(self) -> int | None:
        """Return padding token id, or None if undefined."""
        if self._fallback is not None:
            return self._fallback.pad_token_id
        try:
            return getattr(self._tk, "pad_token_id", None)
        except Exception:
            return None

    @property
    def eos_token_id(self) -> int | None:
        """Return end-of-sequence token id, or None if undefined."""
        if self._fallback is not None:
            return self._fallback.eos_token_id
        try:
            return getattr(self._tk, "eos_token_id", None)
        except Exception:
            return None

    # Backwards-compatible aliases
    @property
    def pad_id(self) -> int:
        v = self.pad_token_id
        return _CallableInt(v or 0)

    @property
    def eos_id(self) -> int:
        v = self.eos_token_id
        return _CallableInt(v or 0)

    # Convenience accessors for underlying tokenizer
    @property
    def raw_tokenizer(self) -> Any:
        """Access the underlying Hugging Face tokenizer instance (alias)."""
        return self._tk

    @property
    def tokenizer(self) -> Any:
        """Preferred name for the underlying tokenizer instance."""
        return self._tk


@tokenizers.register("hf_tokenizer_json")
class HFTokenizerAdapter(TokenizerAdapter):
    """Adapter for Hugging Face ``tokenizers`` JSON artefacts.

    The adapter implements :class:`TokenizerAdapter` by delegating to the
    lightweight ``tokenizers`` runtime.  It allows offline usage of tokenizers
    exported as ``tokenizer.json`` without requiring the full ``transformers``
    dependency tree.
    """

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
            [
                pad_token,
                "<pad>",
                "[PAD]",
                "<PAD>",
            ],
            default=0,
        )
        self._eos_id = self._resolve_special_token(
            [
                eos_token,
                "</s>",
                "<eos>",
                "[EOS]",
            ],
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


_EP_LOADED = False


def get_tokenizer(name: str, **kwargs: Any) -> TokenizerAdapter:
    """Resolve a tokenizer by name via the plugin registry.

    If the ``CODEX_PLUGINS_ENTRYPOINTS`` environment variable is set to ``"1"``
    entry points in the ``codex_ml.tokenizers`` group are loaded once on the
    first invocation.  Local registrations take precedence over entry points.
    Falls back to :class:`HFTokenizer` when no plugin is registered.
    """

    global _EP_LOADED
    if not _EP_LOADED and os.getenv("CODEX_PLUGINS_ENTRYPOINTS") == "1":
        load_tokenizer_entry_points(True)
        _EP_LOADED = True

    item = tokenizers.get(name)
    if item:
        return tokenizers.resolve_and_instantiate(name, **kwargs)
    if _resolve_auto_tokenizer() is None:
        return WhitespaceTokenizer(**kwargs)
    return HFTokenizer(name, **kwargs)
