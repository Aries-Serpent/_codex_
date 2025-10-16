from __future__ import annotations

import html
import re
from pathlib import Path

_TAG = re.compile(r"<[^>]+>")
_MSPACE = re.compile(r"[ \t\r\f\v]+")
_NL3 = re.compile(r"\n{3,}")


def html_to_markdown(s: str) -> str:
    t = s
    for n in range(1, 7):
        t = re.sub(
            rf"<h{n}[^>]*>(.*?)</h{n}>",
            lambda m, level=n: "\n" + "#" * level + " " + strip_tags(m.group(1)) + "\n",
            t,
            flags=re.I | re.S,
        )
    t = _TAG.sub("", t)
    t = html.unescape(t)
    t = _MSPACE.sub(" ", t).replace("\r\n", "\n").replace("\r", "\n")
    t = _NL3.sub("\n\n", t)
    return t.strip() + ("\n" if t and not t.endswith("\n") else "")


def strip_tags(s: str) -> str:
    return _TAG.sub("", s)


def pdf_to_text_bytes(p: Path) -> bytes:
    try:
        from pdfminer.high_level import extract_text  # type: ignore

        txt = extract_text(p.as_posix()) or ""
        return txt.encode("utf-8")
    except Exception:
        raw = p.read_bytes()
        return b"[PDF_EXTRACTOR_MISSING]\n" + raw


def normalize_file(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    if ext in (".html", ".htm"):
        return html_to_markdown(p.read_text(encoding="utf-8", errors="ignore")), "text/markdown"
    if ext == ".md":
        t = p.read_text(encoding="utf-8", errors="ignore")
        t = _MSPACE.sub(" ", t).replace("\r\n", "\n").replace("\r", "\n")
        t = _NL3.sub("\n\n", t)
        return t, "text/markdown"
    if ext in (".txt", ".log"):
        return p.read_text(encoding="utf-8", errors="ignore"), "text/plain"
    if ext == ".pdf":
        return pdf_to_text_bytes(p).decode("utf-8", "ignore"), "application/pdf+text"
    return p.read_text(encoding="utf-8", errors="ignore"), "text/plain"
