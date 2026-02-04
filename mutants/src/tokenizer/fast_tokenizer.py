"""
Fast Tokenizer Module

This module provides functionality for fast tokenizer.

Usage:
    from tokenizer.fast_tokenizer import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from pathlib import Path
from typing import Iterable, Sequence

try:  # pragma: no cover - optional dependency
    from tokenizers import Tokenizer
except Exception:  # pragma: no cover - degrade gracefully
    Tokenizer = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from transformers import AutoTokenizer  # type: ignore
except Exception:  # pragma: no cover - transformers missing is acceptable
    AutoTokenizer = None  # type: ignore[assignment]
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class FastTokenizerWrapper:
    """Thin wrapper around HuggingFace ``tokenizers`` with padding helpers."""

    def xǁFastTokenizerWrapperǁ__init____mutmut_orig(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_1(self, tokenizer_file: str):
        if Tokenizer is not None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_2(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError(None)
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_3(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("XXtokenizers library not installedXX")
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_4(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("TOKENIZERS LIBRARY NOT INSTALLED")
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_5(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_6(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError(None)
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_7(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError("XXtokenizer_file must be providedXX")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_8(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError("TOKENIZER_FILE MUST BE PROVIDED")
        self.tokenizer = Tokenizer.from_file(tokenizer_file)

    def xǁFastTokenizerWrapperǁ__init____mutmut_9(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = None

    def xǁFastTokenizerWrapperǁ__init____mutmut_10(self, tokenizer_file: str):
        if Tokenizer is None:
            raise RuntimeError("tokenizers library not installed")
        if not tokenizer_file:
            raise ValueError("tokenizer_file must be provided")
        self.tokenizer = Tokenizer.from_file(None)
    
    xǁFastTokenizerWrapperǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastTokenizerWrapperǁ__init____mutmut_1': xǁFastTokenizerWrapperǁ__init____mutmut_1, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_2': xǁFastTokenizerWrapperǁ__init____mutmut_2, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_3': xǁFastTokenizerWrapperǁ__init____mutmut_3, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_4': xǁFastTokenizerWrapperǁ__init____mutmut_4, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_5': xǁFastTokenizerWrapperǁ__init____mutmut_5, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_6': xǁFastTokenizerWrapperǁ__init____mutmut_6, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_7': xǁFastTokenizerWrapperǁ__init____mutmut_7, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_8': xǁFastTokenizerWrapperǁ__init____mutmut_8, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_9': xǁFastTokenizerWrapperǁ__init____mutmut_9, 
        'xǁFastTokenizerWrapperǁ__init____mutmut_10': xǁFastTokenizerWrapperǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastTokenizerWrapperǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁFastTokenizerWrapperǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁFastTokenizerWrapperǁ__init____mutmut_orig)
    xǁFastTokenizerWrapperǁ__init____mutmut_orig.__name__ = 'xǁFastTokenizerWrapperǁ__init__'

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_orig(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_1(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = None
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_2(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(None)]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_3(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(None))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_4(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_5(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = None
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_6(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) <= pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_7(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(None)
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_8(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq - [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_9(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] / (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_10(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [1] * (pad_to_length - len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_11(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length + len(seq)))
                else:
                    padded.append(seq[:pad_to_length])
            return padded
        return encodings

    def xǁFastTokenizerWrapperǁencode_batch__mutmut_12(
        self, texts: Sequence[str], pad_to_length: int | None = None
    ) -> list[list[int]]:
        encodings = [enc.ids for enc in self.tokenizer.encode_batch(list(texts))]
        if pad_to_length is not None:
            padded: list[list[int]] = []
            for seq in encodings:
                if len(seq) < pad_to_length:
                    padded.append(seq + [0] * (pad_to_length - len(seq)))
                else:
                    padded.append(None)
            return padded
        return encodings
    
    xǁFastTokenizerWrapperǁencode_batch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastTokenizerWrapperǁencode_batch__mutmut_1': xǁFastTokenizerWrapperǁencode_batch__mutmut_1, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_2': xǁFastTokenizerWrapperǁencode_batch__mutmut_2, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_3': xǁFastTokenizerWrapperǁencode_batch__mutmut_3, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_4': xǁFastTokenizerWrapperǁencode_batch__mutmut_4, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_5': xǁFastTokenizerWrapperǁencode_batch__mutmut_5, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_6': xǁFastTokenizerWrapperǁencode_batch__mutmut_6, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_7': xǁFastTokenizerWrapperǁencode_batch__mutmut_7, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_8': xǁFastTokenizerWrapperǁencode_batch__mutmut_8, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_9': xǁFastTokenizerWrapperǁencode_batch__mutmut_9, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_10': xǁFastTokenizerWrapperǁencode_batch__mutmut_10, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_11': xǁFastTokenizerWrapperǁencode_batch__mutmut_11, 
        'xǁFastTokenizerWrapperǁencode_batch__mutmut_12': xǁFastTokenizerWrapperǁencode_batch__mutmut_12
    }
    
    def encode_batch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastTokenizerWrapperǁencode_batch__mutmut_orig"), object.__getattribute__(self, "xǁFastTokenizerWrapperǁencode_batch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    encode_batch.__signature__ = _mutmut_signature(xǁFastTokenizerWrapperǁencode_batch__mutmut_orig)
    xǁFastTokenizerWrapperǁencode_batch__mutmut_orig.__name__ = 'xǁFastTokenizerWrapperǁencode_batch'

    def xǁFastTokenizerWrapperǁdecode__mutmut_orig(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode(list(token_ids))

    def xǁFastTokenizerWrapperǁdecode__mutmut_1(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode(None)

    def xǁFastTokenizerWrapperǁdecode__mutmut_2(self, token_ids: Iterable[int]) -> str:
        return self.tokenizer.decode(list(None))
    
    xǁFastTokenizerWrapperǁdecode__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastTokenizerWrapperǁdecode__mutmut_1': xǁFastTokenizerWrapperǁdecode__mutmut_1, 
        'xǁFastTokenizerWrapperǁdecode__mutmut_2': xǁFastTokenizerWrapperǁdecode__mutmut_2
    }
    
    def decode(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastTokenizerWrapperǁdecode__mutmut_orig"), object.__getattribute__(self, "xǁFastTokenizerWrapperǁdecode__mutmut_mutants"), args, kwargs, self)
        return result 
    
    decode.__signature__ = _mutmut_signature(xǁFastTokenizerWrapperǁdecode__mutmut_orig)
    xǁFastTokenizerWrapperǁdecode__mutmut_orig.__name__ = 'xǁFastTokenizerWrapperǁdecode'

    def xǁFastTokenizerWrapperǁencode__mutmut_orig(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_1(
        self,
        text: str,
        *,
        padding: str | bool = True,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_2(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = None
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_3(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(None)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_4(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = None
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_5(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(None)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_6(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_7(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = None
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_8(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" or len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_9(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding != "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_10(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "XXmax_lengthXX" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_11(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "MAX_LENGTH" and len(ids) < max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_12(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) <= max_length:
                ids = ids + [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_13(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = None
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_14(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids - [0] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_15(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] / (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_16(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [1] * (max_length - len(ids))
        return ids

    def xǁFastTokenizerWrapperǁencode__mutmut_17(
        self,
        text: str,
        *,
        padding: str | bool = False,
        truncation: bool | None = None,
        max_length: int | None = None,
    ) -> list[int]:
        """Encode text to token IDs with optional padding/truncation."""

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        if max_length is not None:
            if truncation:
                ids = ids[:max_length]
            if padding == "max_length" and len(ids) < max_length:
                ids = ids + [0] * (max_length + len(ids))
        return ids
    
    xǁFastTokenizerWrapperǁencode__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastTokenizerWrapperǁencode__mutmut_1': xǁFastTokenizerWrapperǁencode__mutmut_1, 
        'xǁFastTokenizerWrapperǁencode__mutmut_2': xǁFastTokenizerWrapperǁencode__mutmut_2, 
        'xǁFastTokenizerWrapperǁencode__mutmut_3': xǁFastTokenizerWrapperǁencode__mutmut_3, 
        'xǁFastTokenizerWrapperǁencode__mutmut_4': xǁFastTokenizerWrapperǁencode__mutmut_4, 
        'xǁFastTokenizerWrapperǁencode__mutmut_5': xǁFastTokenizerWrapperǁencode__mutmut_5, 
        'xǁFastTokenizerWrapperǁencode__mutmut_6': xǁFastTokenizerWrapperǁencode__mutmut_6, 
        'xǁFastTokenizerWrapperǁencode__mutmut_7': xǁFastTokenizerWrapperǁencode__mutmut_7, 
        'xǁFastTokenizerWrapperǁencode__mutmut_8': xǁFastTokenizerWrapperǁencode__mutmut_8, 
        'xǁFastTokenizerWrapperǁencode__mutmut_9': xǁFastTokenizerWrapperǁencode__mutmut_9, 
        'xǁFastTokenizerWrapperǁencode__mutmut_10': xǁFastTokenizerWrapperǁencode__mutmut_10, 
        'xǁFastTokenizerWrapperǁencode__mutmut_11': xǁFastTokenizerWrapperǁencode__mutmut_11, 
        'xǁFastTokenizerWrapperǁencode__mutmut_12': xǁFastTokenizerWrapperǁencode__mutmut_12, 
        'xǁFastTokenizerWrapperǁencode__mutmut_13': xǁFastTokenizerWrapperǁencode__mutmut_13, 
        'xǁFastTokenizerWrapperǁencode__mutmut_14': xǁFastTokenizerWrapperǁencode__mutmut_14, 
        'xǁFastTokenizerWrapperǁencode__mutmut_15': xǁFastTokenizerWrapperǁencode__mutmut_15, 
        'xǁFastTokenizerWrapperǁencode__mutmut_16': xǁFastTokenizerWrapperǁencode__mutmut_16, 
        'xǁFastTokenizerWrapperǁencode__mutmut_17': xǁFastTokenizerWrapperǁencode__mutmut_17
    }
    
    def encode(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastTokenizerWrapperǁencode__mutmut_orig"), object.__getattribute__(self, "xǁFastTokenizerWrapperǁencode__mutmut_mutants"), args, kwargs, self)
        return result 
    
    encode.__signature__ = _mutmut_signature(xǁFastTokenizerWrapperǁencode__mutmut_orig)
    xǁFastTokenizerWrapperǁencode__mutmut_orig.__name__ = 'xǁFastTokenizerWrapperǁencode'

    @property
    def vocab_size(self) -> int:
        """Expose the underlying vocabulary size."""

        return int(self.tokenizer.get_vocab_size())

    def xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_orig(self, token_ids: Iterable[int] | int) -> list[str] | str:
        """Convert ids to tokens mimicking Hugging Face API."""

        if isinstance(token_ids, int):
            return self.tokenizer.id_to_token(int(token_ids))
        return [self.tokenizer.id_to_token(int(idx)) for idx in token_ids]

    def xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_1(self, token_ids: Iterable[int] | int) -> list[str] | str:
        """Convert ids to tokens mimicking Hugging Face API."""

        if isinstance(token_ids, int):
            return self.tokenizer.id_to_token(None)
        return [self.tokenizer.id_to_token(int(idx)) for idx in token_ids]

    def xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_2(self, token_ids: Iterable[int] | int) -> list[str] | str:
        """Convert ids to tokens mimicking Hugging Face API."""

        if isinstance(token_ids, int):
            return self.tokenizer.id_to_token(int(None))
        return [self.tokenizer.id_to_token(int(idx)) for idx in token_ids]

    def xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_3(self, token_ids: Iterable[int] | int) -> list[str] | str:
        """Convert ids to tokens mimicking Hugging Face API."""

        if isinstance(token_ids, int):
            return self.tokenizer.id_to_token(int(token_ids))
        return [self.tokenizer.id_to_token(None) for idx in token_ids]

    def xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_4(self, token_ids: Iterable[int] | int) -> list[str] | str:
        """Convert ids to tokens mimicking Hugging Face API."""

        if isinstance(token_ids, int):
            return self.tokenizer.id_to_token(int(token_ids))
        return [self.tokenizer.id_to_token(int(None)) for idx in token_ids]
    
    xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_1': xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_1, 
        'xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_2': xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_2, 
        'xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_3': xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_3, 
        'xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_4': xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_4
    }
    
    def convert_ids_to_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_orig"), object.__getattribute__(self, "xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    convert_ids_to_tokens.__signature__ = _mutmut_signature(xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_orig)
    xǁFastTokenizerWrapperǁconvert_ids_to_tokens__mutmut_orig.__name__ = 'xǁFastTokenizerWrapperǁconvert_ids_to_tokens'

    def xǁFastTokenizerWrapperǁ__call____mutmut_orig(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_1(
        self,
        text: str,
        padding: str | bool = True,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_2(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = None
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_3(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            None,
            padding=padding,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_4(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=None,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_5(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=None,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_6(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is not None else False,
            max_length=None,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_7(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            padding=padding,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_8(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_9(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_10(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is not None else False,
            )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_11(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=False if max_length is not None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_12(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is None else False,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_13(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is not None else True,
            max_length=max_length,
        )
        return {"input_ids": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_14(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"XXinput_idsXX": ids}

    def xǁFastTokenizerWrapperǁ__call____mutmut_15(
        self,
        text: str,
        padding: str | bool = False,
        max_length: int | None = None,
    ) -> dict[str, list[int]]:
        """Provide a minimal call interface returning input ids."""

        ids = self.encode(
            text,
            padding=padding,
            truncation=True if max_length is not None else False,
            max_length=max_length,
        )
        return {"INPUT_IDS": ids}
    
    xǁFastTokenizerWrapperǁ__call____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFastTokenizerWrapperǁ__call____mutmut_1': xǁFastTokenizerWrapperǁ__call____mutmut_1, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_2': xǁFastTokenizerWrapperǁ__call____mutmut_2, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_3': xǁFastTokenizerWrapperǁ__call____mutmut_3, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_4': xǁFastTokenizerWrapperǁ__call____mutmut_4, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_5': xǁFastTokenizerWrapperǁ__call____mutmut_5, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_6': xǁFastTokenizerWrapperǁ__call____mutmut_6, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_7': xǁFastTokenizerWrapperǁ__call____mutmut_7, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_8': xǁFastTokenizerWrapperǁ__call____mutmut_8, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_9': xǁFastTokenizerWrapperǁ__call____mutmut_9, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_10': xǁFastTokenizerWrapperǁ__call____mutmut_10, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_11': xǁFastTokenizerWrapperǁ__call____mutmut_11, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_12': xǁFastTokenizerWrapperǁ__call____mutmut_12, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_13': xǁFastTokenizerWrapperǁ__call____mutmut_13, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_14': xǁFastTokenizerWrapperǁ__call____mutmut_14, 
        'xǁFastTokenizerWrapperǁ__call____mutmut_15': xǁFastTokenizerWrapperǁ__call____mutmut_15
    }
    
    def __call__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFastTokenizerWrapperǁ__call____mutmut_orig"), object.__getattribute__(self, "xǁFastTokenizerWrapperǁ__call____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __call__.__signature__ = _mutmut_signature(xǁFastTokenizerWrapperǁ__call____mutmut_orig)
    xǁFastTokenizerWrapperǁ__call____mutmut_orig.__name__ = 'xǁFastTokenizerWrapperǁ__call__'


def x_build_tokenizer__mutmut_orig(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_1(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = None
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_2(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(None).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_3(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = None

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_4(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_5(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = None
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_6(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(None)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_7(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(None)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_8(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = None
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_9(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(None)
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_10(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                break
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_11(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = None
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_12(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = None
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_13(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location * "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_14(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "XXtokenizer.jsonXX"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_15(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "TOKENIZER.JSON"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_16(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = None

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_17(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_18(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(None)

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_19(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(None)
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_20(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(None))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_21(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = None
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_22(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(None)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_23(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "XX; XX".join(errors)
        if context:
            raise RuntimeError(
                f"Unable to build tokenizer from {path}. Attempted loaders: {context}"
            ) from exc
        raise


def x_build_tokenizer__mutmut_24(path: str | Path) -> object:
    """Best-effort tokenizer loader for local paths or directories.

    When ``transformers`` is installed we attempt to reuse its loader to
    benefit from vocab metadata.  Otherwise a ``FastTokenizerWrapper`` backed
    by :mod:`tokenizers` is returned.  Errors are surfaced with context so CLI
    callers can handle them gracefully.
    """

    location = Path(path).expanduser()
    errors: list[str] = []

    if AutoTokenizer is not None:
        targets = []
        if location.is_file():
            targets.append(location.parent)
        targets.append(location)
        for target in targets:
            try:
                tokenizer = (
                    AutoTokenizer.from_pretrained()  # nosec B615                    str(target), use_fast=True, trust_remote_code=False
                )
            except Exception as exc:  # pragma: no cover - optional dependency path
                errors.append(f"transformers@{target}: {exc}")
                continue
            else:
                return tokenizer  # type: ignore[return-value]

    candidate = location
    if location.is_dir():
        potential = location / "tokenizer.json"
        if potential.exists():
            candidate = potential

    if not candidate.exists():
        raise FileNotFoundError(f"Tokenizer not found at {location}")

    try:
        return FastTokenizerWrapper(str(candidate))
    except Exception as exc:  # pragma: no cover - propagate readable error
        context = "; ".join(errors)
        if context:
            raise RuntimeError(
                None
            ) from exc
        raise

x_build_tokenizer__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_tokenizer__mutmut_1': x_build_tokenizer__mutmut_1, 
    'x_build_tokenizer__mutmut_2': x_build_tokenizer__mutmut_2, 
    'x_build_tokenizer__mutmut_3': x_build_tokenizer__mutmut_3, 
    'x_build_tokenizer__mutmut_4': x_build_tokenizer__mutmut_4, 
    'x_build_tokenizer__mutmut_5': x_build_tokenizer__mutmut_5, 
    'x_build_tokenizer__mutmut_6': x_build_tokenizer__mutmut_6, 
    'x_build_tokenizer__mutmut_7': x_build_tokenizer__mutmut_7, 
    'x_build_tokenizer__mutmut_8': x_build_tokenizer__mutmut_8, 
    'x_build_tokenizer__mutmut_9': x_build_tokenizer__mutmut_9, 
    'x_build_tokenizer__mutmut_10': x_build_tokenizer__mutmut_10, 
    'x_build_tokenizer__mutmut_11': x_build_tokenizer__mutmut_11, 
    'x_build_tokenizer__mutmut_12': x_build_tokenizer__mutmut_12, 
    'x_build_tokenizer__mutmut_13': x_build_tokenizer__mutmut_13, 
    'x_build_tokenizer__mutmut_14': x_build_tokenizer__mutmut_14, 
    'x_build_tokenizer__mutmut_15': x_build_tokenizer__mutmut_15, 
    'x_build_tokenizer__mutmut_16': x_build_tokenizer__mutmut_16, 
    'x_build_tokenizer__mutmut_17': x_build_tokenizer__mutmut_17, 
    'x_build_tokenizer__mutmut_18': x_build_tokenizer__mutmut_18, 
    'x_build_tokenizer__mutmut_19': x_build_tokenizer__mutmut_19, 
    'x_build_tokenizer__mutmut_20': x_build_tokenizer__mutmut_20, 
    'x_build_tokenizer__mutmut_21': x_build_tokenizer__mutmut_21, 
    'x_build_tokenizer__mutmut_22': x_build_tokenizer__mutmut_22, 
    'x_build_tokenizer__mutmut_23': x_build_tokenizer__mutmut_23, 
    'x_build_tokenizer__mutmut_24': x_build_tokenizer__mutmut_24
}

def build_tokenizer(*args, **kwargs):
    result = _mutmut_trampoline(x_build_tokenizer__mutmut_orig, x_build_tokenizer__mutmut_mutants, args, kwargs)
    return result 

build_tokenizer.__signature__ = _mutmut_signature(x_build_tokenizer__mutmut_orig)
x_build_tokenizer__mutmut_orig.__name__ = 'x_build_tokenizer'
