"""Zendesk MCP adapter with metric bridging."""

from __future__ import annotations

import logging
from typing import Any

from codex.monitoring import metrics
from codex.zendesk.monitoring import register_zendesk_metrics
from codex.zendesk.monitoring.mcp_bridge import export_zendesk_metrics
from mcp.adapters.base_adapter import AdapterConfig, BaseAdapter, QueryResult
from mcp.metrics.mcp_metrics import MetricCollector

logger = logging.getLogger(__name__)


class ZendeskAdapter(BaseAdapter):
    """Adapter that exposes Zendesk metrics through MCP interfaces."""

    def __init__(self, config: AdapterConfig | None = None) -> None:
        super().__init__(config=config)
        self._connected = False
        self.metrics = MetricCollector()

    @property
    def adapter_name(self) -> str:
        return "zendesk"

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        register_zendesk_metrics()
        self._connected = True
        logger.info("ZendeskAdapter connected")
        return True

    async def disconnect(self) -> None:
        self._connected = False
        logger.info("ZendeskAdapter disconnected")

    async def health_check(self) -> bool:
        return self._connected

    async def query(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def upsert(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    def export_metrics(self) -> list[dict[str, object]]:
        """Export Zendesk metrics to MCP collector gauges."""
        return export_zendesk_metrics(self.metrics)


__all__ = ["ZendeskAdapter"]
