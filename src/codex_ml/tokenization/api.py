"""Tokenization compatibility layer for the deprecated package namespace."""

from __future__ import annotations

import warnings
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Sequence, cast

BOS_TOKEN = "<BOS>"
EOS_TOKEN = "<EOS>"
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


class TokenizerAdapter(Protocol):
    """Minimal tokenizer interface retained for backward compatibility."""

    def encode(self, text: str) -> List[int]: ...

    def decode(self, ids: Sequence[int]) -> str: ...

    def add_special_tokens(self, tokens: Sequence[str]) -> Dict[str, int]: ...

    def save(self, path: Path) -> None: ...

    @property
    def vocab_size(self) -> int: ...

    @property
    def name_or_path(self) -> str: ...


def _load_hf_adapter():
    from .hf_tokenizer import HFTokenizerAdapter

    return HFTokenizerAdapter


def load_tokenizer(
    name: Optional[str] = None,
    path: Optional[str] = None,
    *,
    use_fast: bool = True,
) -> TokenizerAdapter:
    target = path or name
    if target and str(target).endswith(".model"):
        from .sentencepiece_adapter import SentencePieceAdapter

        return cast(TokenizerAdapter, SentencePieceAdapter(Path(target)).load())
    adapter = _load_hf_adapter()
    try:
        return adapter.load(target, use_fast=use_fast)
    except ImportError:
        from codex_ml.interfaces import tokenizer as _interfaces

        hf = _interfaces.HFTokenizer(target, use_fast=use_fast)

        class _InterfacesBackedAdapter:
            def __init__(self, inner, requested: Optional[str]) -> None:
                self._inner = inner
                self.tokenizer = inner.tokenizer
                if not hasattr(self.tokenizer, "is_fast"):
                    setattr(self.tokenizer, "is_fast", bool(use_fast))
                self._requested = requested or "whitespace-fallback"

            def encode(self, text: str) -> List[int]:
                return self._inner.encode(text)

            def decode(self, ids: Sequence[int]) -> str:
                return self._inner.decode(ids)

            def add_special_tokens(self, tokens: Sequence[str]) -> Dict[str, int]:
                added: Dict[str, int] = {}
                add_fn = getattr(self.tokenizer, "add_special_tokens", None)
                if callable(add_fn):
                    try:
                        result = add_fn({"additional_special_tokens": list(tokens)})
                        if isinstance(result, dict):
                            for key, value in result.items():
                                try:
                                    added[str(key)] = int(value)
                                except Exception:
                                    continue
                    except Exception:
                        pass
                return added

            def save(self, path: Path) -> None:
                path = Path(path)
                path.mkdir(parents=True, exist_ok=True)

            @property
            def vocab_size(self) -> int:
                try:
                    return int(getattr(self.tokenizer, "vocab_size", 0) or 0)
                except Exception:
                    return 0

            @property
            def name_or_path(self) -> str:
                base = getattr(self.tokenizer, "name_or_path", None)
                return str(base or self._requested)

        return cast(TokenizerAdapter, _InterfacesBackedAdapter(hf, target))


@lru_cache()
def _new_exports() -> Dict[str, Callable[[], Any]]:
    from codex_ml.interfaces import tokenizer as _interfaces

    return {
        "get_tokenizer": lambda: _interfaces.get_tokenizer,
        "WhitespaceTokenizer": lambda: _interfaces.WhitespaceTokenizer,
        "HFTokenizer": lambda: _interfaces.HFTokenizer,
    }


@lru_cache()
def _legacy_exports() -> Dict[str, Callable[[], Any]]:
    exports: Dict[str, Callable[[], Any]] = {
        "TokenizerAdapter": lambda: TokenizerAdapter,
        "load_tokenizer": lambda: load_tokenizer,
        "BOS_TOKEN": lambda: BOS_TOKEN,
        "EOS_TOKEN": lambda: EOS_TOKEN,
        "PAD_TOKEN": lambda: PAD_TOKEN,
        "UNK_TOKEN": lambda: UNK_TOKEN,
    }
    try:
        from .hf_tokenizer import HFTokenizerAdapter

        exports["HFTokenizerAdapter"] = lambda: HFTokenizerAdapter
    except Exception:  # pragma: no cover - optional dependency path
        pass
    try:
        from .sp_trainer import SPTokenizer

        exports["SPTokenizer"] = lambda: SPTokenizer
    except Exception:  # pragma: no cover - optional dependency
        pass
    return exports


_WARNED: Dict[str, bool] = {}


def deprecated_legacy_access(name: str) -> Any:
    registry: Dict[str, Callable[[], Any]] = {}
    registry.update(_new_exports())
    registry.update(_legacy_exports())
    factory = registry.get(name)
    if factory is None:
        return None
    warnings.warn(
        "`codex_ml.tokenization.%s` is deprecated; use `codex_ml.interfaces.tokenizer` instead."
        % name,
        DeprecationWarning,
        stacklevel=3,
    )
    _WARNED[name] = True
    value = factory()
    globals()[name] = value
    return value


__all__ = [
    "TokenizerAdapter",
    "load_tokenizer",
    "BOS_TOKEN",
    "EOS_TOKEN",
    "PAD_TOKEN",
    "UNK_TOKEN",
    "deprecated_legacy_access",
]
