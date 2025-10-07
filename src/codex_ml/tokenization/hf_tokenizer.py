"""HuggingFace tokenizer adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Optional, Sequence, cast

from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import

from .api import BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN, TokenizerAdapter

if TYPE_CHECKING:  # pragma: no cover - typing only
    from transformers import (  # type: ignore
        AutoTokenizer as HF_AutoTokenizer,
        PreTrainedTokenizerBase as HF_PreTrainedTokenizerBase,
    )
else:  # pragma: no cover - runtime fallback when dependency missing
    HF_AutoTokenizer = HF_PreTrainedTokenizerBase = object  # type: ignore


transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if _HAS_TRANSFORMERS and transformers is not None and hasattr(transformers, "AutoTokenizer"):
    AutoTokenizer = cast("type[HF_AutoTokenizer]", transformers.AutoTokenizer)  # type: ignore[attr-defined]
    PreTrainedTokenizerBase = cast(
        "type[HF_PreTrainedTokenizerBase]", transformers.PreTrainedTokenizerBase
    )  # type: ignore[attr-defined]
else:  # pragma: no cover - optional dependency unavailable
    AutoTokenizer = None  # type: ignore[assignment]
    PreTrainedTokenizerBase = cast("type[HF_PreTrainedTokenizerBase]", object)

TRANSFORMERS_AVAILABLE = _HAS_TRANSFORMERS

_SPECIAL_TOKENS = {
    "bos_token": BOS_TOKEN,
    "eos_token": EOS_TOKEN,
    "pad_token": PAD_TOKEN,
    "unk_token": UNK_TOKEN,
}


class _WhitespaceFallbackTokenizer:
    """Lightweight tokenizer shim used when ``transformers`` is unavailable."""

    def __init__(self, *, name_or_path: str, is_fast: bool) -> None:
        self.name_or_path = name_or_path
        self.is_fast = is_fast
        self.pad_token = PAD_TOKEN
        self.eos_token = EOS_TOKEN
        self.pad_token_id = 0
        self.eos_token_id = 1
        self.vocab_size = 2
        self._token_to_id: Dict[str, int] = {
            self.pad_token: self.pad_token_id,
            self.eos_token: self.eos_token_id,
        }
        self._id_to_token: Dict[int, str] = {v: k for k, v in self._token_to_id.items()}

    # ---- Internal helpers -------------------------------------------------
    def _ensure_token(self, token: str) -> int:
        if token not in self._token_to_id:
            idx = len(self._token_to_id)
            self._token_to_id[token] = idx
            self._id_to_token[idx] = token
            self.vocab_size = len(self._token_to_id)
        return self._token_to_id[token]

    @staticmethod
    def _should_pad(padding: bool | str, max_length: Optional[int]) -> bool:
        if max_length is None:
            return False
        if padding is True:
            return True
        return padding == "max_length"

    def _pad(self, ids: List[int], max_length: int) -> List[int]:
        trimmed = ids[:max_length]
        if len(trimmed) >= max_length:
            return trimmed
        return trimmed + [self.pad_token_id] * (max_length - len(trimmed))

    def _maybe_truncate(
        self, ids: List[int], truncation: bool | str, max_length: Optional[int]
    ) -> List[int]:
        if not max_length:
            return ids
        if not truncation:
            return ids
        return ids[:max_length]

    # ---- Public API -------------------------------------------------------
    def encode(
        self,
        text: str,
        *,
        add_special_tokens: bool = True,
        padding: bool | str = False,
        truncation: bool | str = False,
        max_length: Optional[int] = None,
        **_: Any,
    ) -> List[int]:
        tokens = [tok for tok in text.split() if tok]
        ids = [self._ensure_token(tok) for tok in tokens]
        if add_special_tokens:
            ids.append(self.eos_token_id)
        ids = self._maybe_truncate(ids, truncation, max_length)
        if max_length is not None and self._should_pad(padding, max_length):
            return self._pad(ids, max_length)
        return ids

    def decode(
        self, ids: Sequence[int], *, clean_up_tokenization_spaces: bool = False, **_: Any
    ) -> str:
        tokens: List[str] = []
        for idx in ids:
            token = self._id_to_token.get(int(idx), "")
            if token in {self.pad_token, self.eos_token}:
                continue
            tokens.append(token)
        text = " ".join(tokens).strip()
        if clean_up_tokenization_spaces:
            return " ".join(text.split())
        return text

    def add_special_tokens(self, mapping: Mapping[str, Any]) -> None:
        pad_tok = mapping.get("pad_token")
        if isinstance(pad_tok, str):
            self.pad_token = pad_tok
            self.pad_token_id = self._ensure_token(pad_tok)
        eos_tok = mapping.get("eos_token")
        if isinstance(eos_tok, str):
            self.eos_token = eos_tok
            self.eos_token_id = self._ensure_token(eos_tok)
        additional = mapping.get("additional_special_tokens")
        if isinstance(additional, str):
            additional_tokens = [additional]
        else:
            additional_tokens = list(additional or [])
        for token in additional_tokens:
            if isinstance(token, str):
                self._ensure_token(token)

    def save_pretrained(self, save_directory: str | Path) -> tuple[str]:
        path = Path(save_directory)
        path.mkdir(parents=True, exist_ok=True)
        (path / "tokenizer.txt").write_text("whitespace_fallback", encoding="utf-8")
        return (str(path),)

    def __call__(
        self,
        texts: Iterable[str],
        *,
        padding: bool | str = True,
        truncation: bool | str = True,
        max_length: Optional[int] = None,
        return_tensors: Optional[str] = None,
        add_special_tokens: bool = False,
        **_: Any,
    ) -> Dict[str, Any]:
        sequences = [
            self.encode(
                text,
                add_special_tokens=add_special_tokens,
                truncation=truncation,
                max_length=max_length,
            )
            for text in texts
        ]
        pad_to: Optional[int]
        if padding == "max_length" and max_length is not None:
            pad_to = max_length
        elif padding is True and max_length is None:
            pad_to = max((len(seq) for seq in sequences), default=0)
        elif padding is True and max_length is not None:
            pad_to = max_length
        else:
            pad_to = None
        if pad_to is not None:
            sequences = [self._pad(seq, pad_to) for seq in sequences]
        if return_tensors == "pt":
            try:
                import torch  # type: ignore
            except Exception:  # pragma: no cover - torch optional
                pass
            else:
                return {"input_ids": torch.tensor(sequences, dtype=torch.long)}
        return {"input_ids": sequences}


@dataclass
class HFTokenizerAdapter(TokenizerAdapter):
    """Adapter around a ``transformers`` tokenizer."""

    tokenizer: PreTrainedTokenizerBase

    @classmethod
    def load(
        cls, name_or_path: Optional[str] = None, *, use_fast: bool = True
    ) -> "HFTokenizerAdapter":
        """Instantiate the adapter from a pretrained tokenizer.

        Parameters
        ----------
        name_or_path:
            Hugging Face model identifier or path.
        use_fast:
            Whether to prefer the Rust-backed ``Fast`` tokenizer variant when
            available. Defaults to ``True`` for backward compatibility.
        """

        target = name_or_path or "gpt2"
        if target and Path(target).is_file():
            target = str(Path(target).parent)
        if not TRANSFORMERS_AVAILABLE or AutoTokenizer is None:
            return cls(
                _WhitespaceFallbackTokenizer(name_or_path=target or "whitespace", is_fast=use_fast)
            )
        tok = load_from_pretrained(
            AutoTokenizer,
            target,
            use_fast=use_fast,
            revision=get_hf_revision(),
        )
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
        """Register additional special tokens with the underlying tokenizer."""
        self.tokenizer.add_special_tokens({"additional_special_tokens": list(tokens)})
        return {t: int(self.tokenizer.convert_tokens_to_ids(t)) for t in tokens}

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

    def batch_encode(
        self,
        texts,
        max_length: Optional[int] = None,
        return_tensors: str | None = "pt",
        return_dict: bool = False,
        padding: bool | str = True,
        truncation: bool = True,
    ):
        """Encode a list of ``texts`` in a vectorized manner.

        Ensures GPT‑2 style tokenizers expose a pad token when padding is
        requested. Parameters mimic ``PreTrainedTokenizerBase.__call__`` with
        sensible defaults for padding and truncation. When ``return_dict`` is
        ``False`` the list of ``input_ids`` is returned for convenience.
        """

        pad_opt = padding
        if pad_opt is True and max_length is not None:
            pad_opt = "max_length"
        if pad_opt and getattr(self.tokenizer, "pad_token", None) is None:
            # GPT‑2 tokenizers lack pad token by default; reuse eos token
            self.tokenizer.pad_token = self.tokenizer.eos_token
        enc = self.tokenizer(
            list(texts),
            padding=pad_opt,
            truncation=truncation,
            max_length=max_length,
            return_tensors=return_tensors,
        )
        if return_dict:
            return enc
        input_ids = enc["input_ids"]
        if hasattr(input_ids, "tolist"):
            return input_ids.tolist()
        if isinstance(input_ids, list):
            return input_ids
        try:
            return list(input_ids)
        except TypeError:  # pragma: no cover - defensive
            return input_ids
