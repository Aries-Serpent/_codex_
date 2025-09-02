"""HuggingFace tokenizer adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from transformers import AutoTokenizer, PreTrainedTokenizerBase

from . import BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN, TokenizerAdapter

_SPECIAL_TOKENS = {
    "bos_token": BOS_TOKEN,
    "eos_token": EOS_TOKEN,
    "pad_token": PAD_TOKEN,
    "unk_token": UNK_TOKEN,
}


@dataclass
class HFTokenizerAdapter(TokenizerAdapter):
    """Adapter around a ``transformers`` tokenizer."""

    tokenizer: PreTrainedTokenizerBase

    @classmethod
    def load(cls, name_or_path: Optional[str] = None) -> "HFTokenizerAdapter":
        target = name_or_path or "gpt2"
        if target and Path(target).is_file():
            target = str(Path(target).parent)
        tok = AutoTokenizer.from_pretrained(target)
        tok.add_special_tokens(_SPECIAL_TOKENS)
        return cls(tok)

    def encode(
        self,
        text: str,
        *,
        pad_to_max: bool = False,
        max_length: Optional[int] = None,
    ) -> List[int]:
        """Encode ``text`` into token ids with optional padding and truncation.

        Parameters
        ----------
        text : str
            Input string to tokenize.
        pad_to_max : bool, default=False
            If ``True``, pad the sequence to ``max_length`` using the tokenizer's
            pad token. When ``False``, no padding is applied.
        max_length : int, optional
            When provided, truncates sequences longer than this length. If
            ``pad_to_max`` is also ``True``, the output will be exactly
            ``max_length`` tokens long.
        """

        return self.tokenizer.encode(
            text,
            add_special_tokens=False,
            padding="max_length" if pad_to_max else False,
            truncation=max_length is not None,
            max_length=max_length,
        )

    def decode(self, ids: Sequence[int]) -> str:
        return self.tokenizer.decode(ids, clean_up_tokenization_spaces=False)

    def add_special_tokens(self, tokens: Sequence[str]) -> Dict[str, int]:
        return self.tokenizer.add_special_tokens({"additional_special_tokens": list(tokens)})

    def save(self, path: Path) -> None:
        path = Path(path)
        save_dir = path if path.suffix == "" else path.parent
        save_dir.mkdir(parents=True, exist_ok=True)
        self.tokenizer.save_pretrained(save_dir)
        if path.suffix != "":
            (save_dir / "tokenizer.json").replace(path)

    @property
    def vocab_size(self) -> int:  # type: ignore[override]
        return int(self.tokenizer.vocab_size)

    @property
    def pad_id(self) -> int:  # type: ignore[override]
        return int(self.tokenizer.pad_token_id or 0)

    @property
    def eos_id(self) -> int:  # type: ignore[override]
        return int(self.tokenizer.eos_token_id or 0)

    @property
    def name_or_path(self) -> str:  # type: ignore[override]
        return str(self.tokenizer.name_or_path)
