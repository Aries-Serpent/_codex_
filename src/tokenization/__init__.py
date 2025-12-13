"""Tokenization utilities."""

__all__: list[str] = []

try:
    from .loader import load_tokenizer
except (ModuleNotFoundError, ImportError, AttributeError):
    # AttributeError: torch stub raises this when PyTorch not installed
    # ImportError/ModuleNotFoundError: tokenizers/transformers missing
    load_tokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("load_tokenizer")

try:
    from .adapter import TokenizerAdapter
except (ModuleNotFoundError, ImportError, AttributeError):
    # AttributeError: torch stub raises this when PyTorch not installed
    # ImportError/ModuleNotFoundError: codex_ml dependencies missing
    TokenizerAdapter = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("TokenizerAdapter")

try:
    from . import sentencepiece_adapter
except (ModuleNotFoundError, ImportError, AttributeError):
    # Catch broad exceptions for robustness with optional dependencies
    sentencepiece_adapter = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("sentencepiece_adapter")

try:
    from . import train_tokenizer
except (ModuleNotFoundError, ImportError, AttributeError):
    # Catch broad exceptions for robustness with optional dependencies
    train_tokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("train_tokenizer")

try:
    from . import cli
except (ModuleNotFoundError, ImportError, AttributeError):
    # Catch broad exceptions for robustness with optional dependencies
    cli = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("cli")
