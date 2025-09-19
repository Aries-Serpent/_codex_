"""Tokenization utilities."""

__all__: list[str] = []

try:
    from . import sentencepiece_adapter  # type: ignore # noqa: F401
except ModuleNotFoundError:
    sentencepiece_adapter = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("sentencepiece_adapter")

try:
    from . import train_tokenizer  # type: ignore # noqa: F401
except ModuleNotFoundError:
    train_tokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("train_tokenizer")
