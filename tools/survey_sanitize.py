#!/usr/bin/env python3
"""Normalize Codex plaintext survey output into well-formed Markdown."""
from __future__ import annotations

import re
import sys
from collections.abc import Iterable

BEGIN_MARKER = "[BEGIN CONTENT]"
END_MARKER = "[END CONTENT]"


def _collapse_fences(text: str) -> str:
    """Collapse any sequence of backticks >=3 into classic triple fences."""
    return re.sub(r"`{3,}", "```", text)


def _wrap_content_blocks(lines: Iterable[str]) -> list[str]:
    """Replace marker pairs with ```text fenced blocks."""
    output: list[str] = []
    buffer: list[str] = []
    inside = False

    for raw in lines:
        stripped = raw.strip()
        if stripped == BEGIN_MARKER:
            if inside:
                output.extend(_render_buffer(buffer))
                buffer.clear()
            inside = True
            buffer.clear()
            continue
        if stripped == END_MARKER:
            if inside:
                output.extend(_render_buffer(buffer))
                buffer.clear()
                inside = False
            continue

        clean = raw.rstrip("\r")
        if inside:
            buffer.append(clean)
        else:
            output.append(clean)

    if inside:
        output.extend(_render_buffer(buffer))

    return output


def _render_buffer(buffer: list[str]) -> list[str]:
    block = ["```text"]
    block.extend(buffer)
    block.append("```")
    return block


def _strip_empty_fences(text: str) -> str:
    # Remove accidental empty fences like ```\n``` or ```text\n```.
    return re.sub(r"```[a-zA-Z0-9_-]*\n```", "", text)


def sanitize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    collapsed = _collapse_fences(text)
    wrapped = _wrap_content_blocks(collapsed.split("\n"))
    rendered = "\n".join(wrapped).rstrip()
    cleaned = _strip_empty_fences(rendered)
    if cleaned and not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned


if __name__ == "__main__":
    raw = sys.stdin.read()
    sys.stdout.write(sanitize(raw))
