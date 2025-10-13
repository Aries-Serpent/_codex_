from __future__ import annotations

import html
import re
from pathlib import Path

_HTML_TAG = re.compile(r"<[^>]+>")
_MULTISPACE = re.compile(r"[ \t\r\f\v]+")
_MULTINEWLINE = re.compile(r"\n{3,}")


def html_to_markdown(text: str) -> str:
    """
    Minimal HTML→Markdown/plain converter (offline, stdlib-only):
    - strip tags, unescape entities, collapse whitespace, preserve headings if obvious
    """
    t = text
    # naive heading preservation: replace <hN>..</hN> with markdown ##
    for n in range(1, 7):
        t = re.sub(
            rf"<h{n}[^>]*>(.*?)</h{n}>",
            lambda m, level=n: "\n" + "#" * level + " " + _strip_tags(m.group(1)) + "\n",
            t,
            flags=re.I | re.S,
        )
    t = _HTML_TAG.sub("", t)
    t = html.unescape(t)
    t = _MULTISPACE.sub(" ", t)
    # normalize newlines
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = _MULTINEWLINE.sub("\n\n", t)
    return t.strip() + ("\n" if t and not t.endswith("\n") else "")


def _strip_tags(s: str) -> str:
    return _HTML_TAG.sub("", s)


def pdf_to_text_bytes(pdf_path: Path) -> bytes:
    """
    Best-effort PDF→text:
    - Try pdfminer.six if installed
    - Else return a sentinel header + raw bytes for traceability
    """
    try:
        from pdfminer.high_level import extract_text  # type: ignore

        txt = extract_text(pdf_path.as_posix()) or ""
        return txt.encode("utf-8")
    except Exception:
        raw = pdf_path.read_bytes()
        return b"[PDF_EXTRACTOR_MISSING]\n" + raw


def normalize_file(path: Path) -> tuple[str, str]:
    """
    Returns tuple: (normalized_text, detected_mime_label)
    """
    ext = path.suffix.lower()
    if ext in (".html", ".htm"):
        return html_to_markdown(path.read_text(encoding="utf-8", errors="ignore")), "text/markdown"
    if ext == ".md":
        # normalize whitespace lightly
        t = path.read_text(encoding="utf-8", errors="ignore")
        t = _MULTISPACE.sub(" ", t).replace("\r\n", "\n").replace("\r", "\n")
        t = _MULTINEWLINE.sub("\n\n", t)
        return t, "text/markdown"
    if ext in (".txt", ".log"):
        return path.read_text(encoding="utf-8", errors="ignore"), "text/plain"
    if ext == ".pdf":
        return pdf_to_text_bytes(path).decode("utf-8", "ignore"), "application/pdf+text"
    # default: try to read as text
    return path.read_text(encoding="utf-8", errors="ignore"), "text/plain"
