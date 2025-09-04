import pathlib
from typing import List, Optional

try:
    import sentencepiece as spm
except Exception:
    spm = None


class SentencePieceAdapter:
    def __init__(self, model_path: str, special_tokens: Optional[List[str]] = None):
        self.model_path = pathlib.Path(model_path)
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(str(self.model_path))
        self.special_tokens = special_tokens or []

    def encode(
        self,
        text: str,
        *,
        padding: Optional[str] = None,
        truncation: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> List[int]:
        ids = self.sp.EncodeAsIds(text)
        if truncation in ("longest_first", "only_first", "only_second") and max_length:
            ids = ids[-max_length:] if truncation == "only_first" else ids[:max_length]
        if padding in (True, "longest", "max_length") and max_length:
            pad_id = self.sp.pad_id() if self.sp.pad_id() >= 0 else 0
            ids = ids[:max_length] + [pad_id] * max(0, max_length - len(ids))
        return ids

    def decode(self, ids: List[int]) -> str:
        return self.sp.DecodeIds(ids)


__all__ = ["SentencePieceAdapter"]
