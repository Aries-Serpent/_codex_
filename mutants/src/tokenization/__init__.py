"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from tokenization.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging
import warnings as _warnings

logger = logging.getLogger(__name__)

_warnings.warn(
    "src.tokenization is deprecated and will be removed in version 2.0. "
    "Use src.codex_ml.tokenization instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []

try:
    from .loader import load_tokenizer
except (ModuleNotFoundError, ImportError, AttributeError):
    # AttributeError: torch stub (torch/__init__.py) raises this when PyTorch not installed
    # ImportError/ModuleNotFoundError: tokenizers/transformers missing
    load_tokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("load_tokenizer")

try:
    from .adapter import TokenizerAdapter
except (ModuleNotFoundError, ImportError, AttributeError):
    # AttributeError: torch stub (torch/__init__.py) raises this when PyTorch not installed
    # ImportError/ModuleNotFoundError: tokenizers/transformers missing
    TokenizerAdapter = None
else:  # pragma: no cover - import succeeded
    __all__.append("TokenizerAdapter")

try:
    from . import sentencepiece_adapter
except (ModuleNotFoundError, ImportError, AttributeError):
    # ImportError/ModuleNotFoundError: sentencepiece missing
    # AttributeError: potential stub-related issues in dependency chain
    sentencepiece_adapter = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("sentencepiece_adapter")

try:
    from . import train_tokenizer
except (ModuleNotFoundError, ImportError, AttributeError):
    # ImportError/ModuleNotFoundError: tokenizers/hydra missing
    # AttributeError: potential stub-related issues in dependency chain
    train_tokenizer = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("train_tokenizer")

try:
    from . import cli
except (ModuleNotFoundError, ImportError, AttributeError):
    # ImportError/ModuleNotFoundError: optional CLI dependencies missing
    # AttributeError: potential stub-related issues in dependency chain
    cli = None  # type: ignore[assignment]
else:  # pragma: no cover - import succeeded
    __all__.append("cli")
