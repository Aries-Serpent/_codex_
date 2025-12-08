"""
Minimal byte-level tokenizer for offline operation.

Provides:
- encode/decode with UTF-8 byte encoding
- Padding and truncation support
- EOS token handling
- Deterministic operation
"""

from typing import List, Optional
from dataclasses import dataclass


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
        self.pad_token_id = pad_token_id
        self.eos_token_id = eos_token_id
        self.unk_token_id = unk_token_id
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation
        
        # Vocabulary: bytes 0-255 + special tokens
        # Offset by 3 to reserve special token IDs
        self._special_token_offset = 3
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text string
            add_special_tokens: Whether to add EOS token
            
        Returns:
            List of token IDs
        """
        # Convert to UTF-8 bytes, offset by special tokens
        ids = [b + self._special_token_offset for b in text.encode("utf-8")]
        
        # Add EOS token
        if add_special_tokens:
            ids.append(self.eos_token_id)
        
        # Truncation
        if self.truncation and self.max_length is not None:
            ids = ids[:self.max_length]
        
        # Padding
        if self.padding == "max_length" and self.max_length is not None:
            if len(ids) < self.max_length:
                ids += [self.pad_token_id] * (self.max_length - len(ids))
        
        return ids
    
    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs to text.
        
        Args:
            ids: List of token IDs
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
        for i in ids:
            byte_val = i - self._special_token_offset
            if 0 <= byte_val <= 255:
                bytes_list.append(byte_val)
        
        return bytes(bytes_list).decode("utf-8", errors="replace")
    
    def batch_encode(
        self,
        texts: List[str],
        add_special_tokens: bool = True,
    ) -> List[List[int]]:
        """Encode multiple texts."""
        return [self.encode(t, add_special_tokens) for t in texts]
    
    def batch_decode(
        self,
        batch_ids: List[List[int]],
        skip_special_tokens: bool = True,
    ) -> List[str]:
        """Decode multiple ID sequences."""
        return [self.decode(ids, skip_special_tokens) for ids in batch_ids]
    
    @property
    def vocab_size(self) -> int:
        """Total vocabulary size."""
        return 256 + self._special_token_offset
    
    def tokenize_example(self, text: str) -> List[int]:
        """Legacy compatibility method."""
        return self.encode(text)


# Default tokenizer instance
Tokenizer = ByteLevelTokenizer


def tokenize_example(text: str) -> list[int]:
    """Legacy compatibility function for tests."""
    tokenizer = ByteLevelTokenizer()
    return tokenizer.encode(text, add_special_tokens=False)
