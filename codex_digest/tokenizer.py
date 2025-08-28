from __future__ import annotations
from dataclasses import dataclass
from typing import List, Iterable
import re


@dataclass(frozen=True)
class Token:
    text: str
    kind: str  # "word" | "number" | "punct" | "symbol"


class Tokenizer:
    """Abstract tokenizer API."""

    def normalize(self, s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    def tokenize(self, s: str) -> List[Token]:
        raise NotImplementedError


class DefaultTokenizer(Tokenizer):
    """
    Whitespace + punctuation tokenizer (no external deps).
    Optional compatibility: if HuggingFace fast tokenizer is available,
    you can plug one in by implementing Tokenizer.tokenize.
    """

    WORD = re.compile(r"[A-Za-z_]+")
    NUM = re.compile(r"\d+(?:\.\d+)?")

    def tokenize(self, s: str) -> List[Token]:
        s = self.normalize(s)
        out: List[Token] = []
        i = 0
        while i < len(s):
            ch = s[i]
            if ch.isspace():
                i += 1
                continue
            m = self.NUM.match(s, i)
            if m:
                out.append(Token(m.group(), "number"))
                i = m.end()
                continue
            m = self.WORD.match(s, i)
            if m:
                out.append(Token(m.group().lower(), "word"))
                i = m.end()
                continue
            if re.match(r"[^\w\s]", ch):
                out.append(Token(ch, "punct"))
                i += 1
                continue
            out.append(Token(ch, "symbol"))
            i += 1
        return out


def detok(tokens: Iterable[Token]) -> str:
    out, prev = [], None
    for t in tokens:
        if prev and t.kind in ("word", "number") and prev.kind in ("word", "number"):
            out.append(" ")
        if t.kind == "punct" and t.text in (")", "]", "}", ",", ".", ":", ";"):
            pass
        elif prev and prev.kind == "punct" and prev.text in ("(", "[", "{"):
            pass
        elif out:
            out.append(" ")
        out.append(t.text)
        prev = t
    return "".join(out)
