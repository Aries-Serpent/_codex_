"""Compatibility wrapper for the canonical tokenizer adapter.

This module simply re-exports the TokenizerAdapter interface and HFTokenizer
implementation from :mod:`codex_ml.interfaces.tokenizer`.  Code importing
``interfaces.tokenizer`` continues to work while all logic lives in the
centralised module.
"""

from codex_ml.interfaces.tokenizer import HFTokenizer, TokenizerAdapter

__all__ = ["TokenizerAdapter", "HFTokenizer"]
