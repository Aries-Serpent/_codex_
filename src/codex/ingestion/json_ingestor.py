"""Compatibility JSON ingestor for legacy `codex.ingestion` imports."""

from __future__ import annotations

import json


class JSONIngestor:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def ingest(self, path):
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)


__all__ = ["JSONIngestor"]
