from __future__ import annotations

import math
import re
import uuid

_HDR = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


def approx_tokens(s: str) -> int:
    # Rough token proxy: 1 token ≈ 4 chars (safe offline heuristic)
    return max(1, math.ceil(len(s) / 4))


def split_by_headings(md: str) -> list[dict[str, str]]:
    """
    Split markdown into sections by headings.
    Returns list of {"title": str, "text": str}
    """
    parts: list[dict[str, str]] = []
    matches = list(_HDR.finditer(md))
    if not matches:
        return [{"title": "", "text": md}]
    for i, m in enumerate(matches):
        start = m.start()
        if i > 0:
            prev = matches[i - 1]
            sect = md[prev.start() : start]
            parts.append({"title": prev.group(2).strip(), "text": sect})
    # tail
    tail = md[matches[-1].start() :]
    parts.append({"title": matches[-1].group(2).strip(), "text": tail})
    return parts


def chunk_by_headings(
    md: str,
    *,
    target_tokens: int = 1024,
    overlap_tokens: int = 64,
) -> list[dict[str, object]]:
    """
    Create overlapping chunks guided by headings; enforce max token target.
    Returns list of KB records [{"chunk_id","chunk_idx","title","text"}]
    """
    sections = split_by_headings(md)
    chunks: list[dict[str, object]] = []
    chunk_idx = 0
    carry = ""
    for sec in sections:
        content = sec["text"]
        buf = (carry + "\n" + content).strip() if carry else content
        while buf:
            # cut on sentence-ish boundaries if too large
            if approx_tokens(buf) <= target_tokens:
                cid = "kb_" + uuid.uuid4().hex[:12]
                chunks.append(
                    {
                        "chunk_id": cid,
                        "chunk_idx": chunk_idx,
                        "title": sec["title"],
                        "text": buf,
                    }
                )
                chunk_idx += 1
                buf = ""
                carry = ""
            else:
                # split approximately in half on newline
                mid = len(buf) // 2
                cut = buf.rfind("\n", 0, mid)
                if cut == -1:
                    cut = mid
                left, right = buf[:cut], buf[cut:]
                cid = "kb_" + uuid.uuid4().hex[:12]
                chunks.append(
                    {
                        "chunk_id": cid,
                        "chunk_idx": chunk_idx,
                        "title": sec["title"],
                        "text": left,
                    }
                )
                chunk_idx += 1
                # overlap from end of left
                overlap_chars = overlap_tokens * 4
                ov = right[: min(len(right), overlap_chars)]
                buf = ov + right
                carry = ""
    return chunks
