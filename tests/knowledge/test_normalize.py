from __future__ import annotations

from codex.knowledge.normalize import html_to_markdown


def test_html_to_md_preserves_headings() -> None:
    html = "<h1>Title</h1><p>Hello <b>world</b></p>"
    md = html_to_markdown(html)
    assert "# Title" in md
    assert "Hello world" in md
