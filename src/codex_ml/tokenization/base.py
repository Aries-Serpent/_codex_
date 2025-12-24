"""
Minimal byte-level tokenizer for offline operation.

Provides:
- encode/decode with UTF-8 byte encoding
- Padding and truncation support
- EOS token handling
- Deterministic operation
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenizerConfig:
    """Configuration for the tokenizer."""

    pad_token_id: int = 0
    eos_token_id: int = 1
    unk_token_id: int = 2
    max_length: Optional[int] = None
    padding: str = "max_length"  # "max_length" or "longest"
    truncation: bool = True


class ByteLevelTokenizer:
    """
    Byte-level tokenizer operating on UTF-8 encoded bytes.

    Provides deterministic tokenization for offline operation
    without external dependencies.

    Example:
        tokenizer = ByteLevelTokenizer(max_length=128)
        ids = tokenizer.encode("Hello, world!")
        text = tokenizer.decode(ids)
    """

    def __init__(
        self,
        pad_token_id: int = 0,
        eos_token_id: int = 1,
        unk_token_id: int = 2,
        max_length: Optional[int] = None,
        padding: str = "max_length",
        truncation: bool = True,
    ) -> None:
        """Initialize ByteLevelTokenizer.

        Args:
            pad_token_id: ID for padding token
            eos_token_id: ID for end-of-sequence token
            unk_token_id: ID for unknown token
            max_length: Maximum sequence length (must be >= 1 if set)
            padding: Padding strategy - "max_length" or "longest"
            truncation: Whether to truncate sequences exceeding max_length

        Raises:
            ValueError: If max_length is set but <= 0
        """
        if max_length is not None and max_length <= 0:
            raise ValueError(
                f"max_length must be >= 1 when set, got {max_length}. "
                f"Use max_length=None to disable truncation."
            )

        self.pad_token_id = pad_token_id
        self.eos_token_id = eos_token_id
        self.unk_token_id = unk_token_id
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation

        # Vocabulary: bytes 0-255 + special tokens
        # Offset by 3 to reserve special token IDs
        self._special_token_offset = 3

    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        """
        Encode text to token IDs.

        Args:
            text: Input text string
            add_special_tokens: Whether to add EOS token

        Returns:
            list of token IDs
        """
        # Convert to UTF-8 bytes, offset by special tokens
        ids = [b + self._special_token_offset for b in text.encode("utf-8")]

        # Truncation (reserve space for EOS if needed)
        if self.truncation and self.max_length is not None:
            if add_special_tokens:
                # Reserve space for EOS token
                ids = ids[: max(0, self.max_length - 1)]
            else:
                ids = ids[: self.max_length]

        # Add EOS token
        if add_special_tokens:
            ids.append(self.eos_token_id)

        # Padding
        if self.padding == "max_length" and self.max_length is not None:
            if len(ids) < self.max_length:
                ids += [self.pad_token_id] * (self.max_length - len(ids))

        return ids

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs back to text.

        Token ID layout (offset arithmetic):
        - 0: PAD token
        - 1: UNK token
        - 2: EOS token
        - 3-258: Byte values 0-255 (offset by 3 to avoid collision with specials)

        The offset ensures special tokens (0-2) don't conflict with byte values.

        Args:
            ids: list of token IDs
            skip_special_tokens: Whether to skip special tokens

        Returns:
            Decoded text string
        """
        # Filter special tokens
        special_ids = {self.pad_token_id, self.eos_token_id, self.unk_token_id}

        if skip_special_tokens:
            ids = [i for i in ids if i not in special_ids]

        # Convert back to bytes
        bytes_list = []
        for id_ in ids:
            # Remove offset to get original byte value
            byte_val = id_ - self._special_token_offset
            if 0 <= byte_val <= 255:  # Valid byte range only
                bytes_list.append(byte_val)

        return bytes(bytes_list).decode("utf-8", errors="replace")

    def batch_encode(
        self,
        texts: list[str],
        add_special_tokens: bool = True,
    ) -> list[list[int]]:
        """Encode multiple texts."""
        return [self.encode(t, add_special_tokens) for t in texts]

    def batch_decode(
        self,
        batch_ids: list[list[int]],
        skip_special_tokens: bool = True,
    ) -> list[str]:
        """Decode multiple ID sequences."""
        return [self.decode(ids, skip_special_tokens) for ids in batch_ids]

    @property
    def vocab_size(self) -> int:
        """Total vocabulary size."""
        return 256 + self._special_token_offset

    def tokenize_example(self, text: str) -> list[int]:
        """Legacy compatibility method."""
        return self.encode(text)


# Default tokenizer instance
Tokenizer = ByteLevelTokenizer


def tokenize_example(text: str) -> list[int]:
    """Legacy compatibility function for tests."""
    tokenizer = ByteLevelTokenizer()
    return tokenizer.encode(text, add_special_tokens=False)
