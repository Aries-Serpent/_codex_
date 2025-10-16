from __future__ import annotations

import math
import re
import uuid

_HDR = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


def approx_tokens(s: str) -> int:
    return max(1, math.ceil(len(s) / 4))


def split_by_headings(md: str) -> list[dict]:
    parts = []
    matches = list(_HDR.finditer(md))
    if not matches:
        return [{"title": "", "text": md}]
    for i, m in enumerate(matches):
        if i > 0:
            prev = matches[i - 1]
            parts.append({"title": prev.group(2).strip(), "text": md[prev.start() : m.start()]})
    parts.append({"title": matches[-1].group(2).strip(), "text": md[matches[-1].start() :]})
    return parts


def chunk_by_headings(
    md: str, *, target_tokens: int = 1024, overlap_tokens: int = 64
) -> list[dict]:
    sections = split_by_headings(md)
    out: list[dict] = []
    idx = 0
    for sec in sections:
        buf = sec["text"]
        while buf:
            if approx_tokens(buf) <= target_tokens:
                out.append(
                    {
                        "chunk_id": "kb_" + uuid.uuid4().hex[:12],
                        "chunk_idx": idx,
                        "title": sec["title"],
                        "text": buf,
                    }
                )
                idx += 1
                buf = ""
            else:
                mid = len(buf) // 2
                cut = buf.rfind("\n", 0, mid)
                if cut == -1:
                    cut = mid
                left, right = buf[:cut], buf[cut:]
                out.append(
                    {
                        "chunk_id": "kb_" + uuid.uuid4().hex[:12],
                        "chunk_idx": idx,
                        "title": sec["title"],
                        "text": left,
                    }
                )
                idx += 1
                ov = right[: min(len(right), overlap_tokens * 4)]
                buf = ov + right
    return out
