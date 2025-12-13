"""Tokenization utilities."""

__all__: list[str] = []

try:
    from .loader import load_tokenizer
except (ModuleNotFoundError, ImportError, AttributeError):
    load_tokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("load_tokenizer")

try:
    from .adapter import TokenizerAdapter
except (ModuleNotFoundError, ImportError, AttributeError):
    TokenizerAdapter = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("TokenizerAdapter")

try:
    from . import sentencepiece_adapter
except (ModuleNotFoundError, ImportError, AttributeError):
    sentencepiece_adapter = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("sentencepiece_adapter")

try:
    from . import train_tokenizer
except (ModuleNotFoundError, ImportError, AttributeError):
    train_tokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("train_tokenizer")

try:
    from . import cli
except (ModuleNotFoundError, ImportError, AttributeError):
    cli = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("cli")
