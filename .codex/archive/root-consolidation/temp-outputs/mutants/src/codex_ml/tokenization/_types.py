"""Shared tokenization type constants.

Extracted from api.py to break the api→hf_tokenizer→api circular import.
All tokenization modules should import token constants from here, not from api.
"""

from __future__ import annotations

# Standard special token strings used across all tokenizer implementations.
# These follow the common BOS/EOS/PAD/UNK convention.  They are deliberately
# enclosed in angle-brackets to avoid collisions with natural language tokens.
BOS_TOKEN: str = "<BOS>"  # nosec B105 - conventional special token, not a secret
EOS_TOKEN: str = "<EOS>"  # nosec B105 - conventional special token, not a secret
PAD_TOKEN: str = "<PAD>"  # nosec B105 - conventional special token, not a secret
UNK_TOKEN: str = "<UNK>"  # nosec B105 - conventional special token, not a secret

__all__ = ["BOS_TOKEN", "EOS_TOKEN", "PAD_TOKEN", "UNK_TOKEN"]
