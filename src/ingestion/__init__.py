"""Ingestion utilities package."""

from .encoding_detect import detect_encoding
from .io_text import read_text
from .utils import deterministic_shuffle

__all__ = ["read_text", "deterministic_shuffle", "detect_encoding"]
