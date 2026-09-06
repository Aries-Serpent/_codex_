"""Compatibility file ingestor for legacy `codex.ingestion` imports."""

from __future__ import annotations

class FileIngestor:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def ingest(self, path):
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()

    def process(self, data):
        return data


__all__ = ["FileIngestor"]
