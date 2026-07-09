"""Knowledge ingestion helpers (offline/deterministic)."""

from .build import archive_and_manifest, build_kb
from .chunk import approx_tokens, chunk_by_headings
from .normalize import html_to_markdown, normalize_file, pdf_to_text_bytes
from .pii import scrub
from .schema import KBRecord, validate_kb

__all__ = [
    "KBRecord",
    "approx_tokens",
    "archive_and_manifest",
    "build_kb",
    "chunk_by_headings",
    "html_to_markdown",
    "normalize_file",
    "pdf_to_text_bytes",
    "scrub",
    "validate_kb",
]
