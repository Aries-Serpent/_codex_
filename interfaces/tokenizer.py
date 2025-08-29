from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from transformers import AutoTokenizer


class HFTokenizer:
    """Thin wrapper over Hugging Face fast tokenizers with explicit padding/truncation.

    The helper exposes a minimal subset of :class:`~transformers.PreTrainedTokenizer`
    methods to keep tests lightweight while still mirroring the library's behaviour.
    """

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

    # BEGIN: encode/decode helpers
    def encode(self, texts: Union[str, Sequence[str]]) -> Dict[str, Any]:
        """Tokenise *texts* returning PyTorch tensors.

        Parameters follow the same semantics as ``AutoTokenizer.__call__`` with
        the padding/truncation options supplied at construction time.
        """

        return self.tk(
            texts,
            padding=self.padding,
            truncation=self.truncation,
            max_length=self.max_length,
            return_tensors="pt",
        )

    def decode(self, ids: Iterable[int]) -> str:
        """Decode a sequence of token ids to a string."""

        return self.tk.decode(list(ids), skip_special_tokens=True)

    @property
    def pad_id(self) -> int:
        return int(self.tk.pad_token_id or 0)

    @property
    def eos_id(self) -> int:
        return int(self.tk.eos_token_id or 0)

    @property
    def vocab_size(self) -> int:
        return int(self.tk.vocab_size)
    # END: encode/decode helpers
