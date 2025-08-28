from typing import Any, Dict, List, Optional, Union

from transformers import AutoTokenizer


class HFTokenizer:
    """Thin wrapper over Hugging Face fast tokenizers with explicit padding/truncation."""

    def __init__(
        self,
        name_or_path: str,
        *,
        use_fast: bool = True,
        padding: Union[bool, str] = "longest",
        truncation: Union[bool, str] = True,
        max_length: Optional[int] = None,
    ) -> None:
        self.tk = AutoTokenizer.from_pretrained(name_or_path, use_fast=use_fast)
        self.padding = padding
        self.truncation = truncation
        self.max_length = max_length

    def encode(self, texts: List[str]) -> Dict[str, Any]:
        return self.tk(
            texts,
            padding=self.padding,
            truncation=self.truncation,
            max_length=self.max_length,
            return_tensors="pt",
        )
