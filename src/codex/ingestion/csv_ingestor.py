"""Compatibility CSV ingestor for legacy `codex.ingestion` imports."""

from __future__ import annotations

import csv


class CSVIngestor:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def ingest(self, path):
        with open(path, newline="", encoding="utf-8") as handle:
            return list(csv.reader(handle))


__all__ = ["CSVIngestor"]
