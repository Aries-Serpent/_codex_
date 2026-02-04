"""Zendesk MCP adapter with metric bridging."""

from __future__ import annotations

import logging
from typing import Any

from src.codex.monitoring import metrics
from src.codex.zendesk.monitoring import register_zendesk_metrics
from src.codex.zendesk.monitoring.mcp_bridge import export_zendesk_metrics
from src.mcp.adapters.base_adapter import AdapterConfig, BaseAdapter, QueryResult
from src.mcp.metrics.mcp_metrics import MetricCollector

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class ZendeskAdapter(BaseAdapter):
    """Adapter that exposes Zendesk metrics through MCP interfaces."""

    def xǁZendeskAdapterǁ__init____mutmut_orig(self, config: AdapterConfig | None = None) -> None:
        super().__init__(config=config)
        self._connected = False
        self.metrics = MetricCollector()

    def xǁZendeskAdapterǁ__init____mutmut_1(self, config: AdapterConfig | None = None) -> None:
        super().__init__(config=None)
        self._connected = False
        self.metrics = MetricCollector()

    def xǁZendeskAdapterǁ__init____mutmut_2(self, config: AdapterConfig | None = None) -> None:
        super().__init__(config=config)
        self._connected = None
        self.metrics = MetricCollector()

    def xǁZendeskAdapterǁ__init____mutmut_3(self, config: AdapterConfig | None = None) -> None:
        super().__init__(config=config)
        self._connected = True
        self.metrics = MetricCollector()

    def xǁZendeskAdapterǁ__init____mutmut_4(self, config: AdapterConfig | None = None) -> None:
        super().__init__(config=config)
        self._connected = False
        self.metrics = None
    
    xǁZendeskAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁZendeskAdapterǁ__init____mutmut_1': xǁZendeskAdapterǁ__init____mutmut_1, 
        'xǁZendeskAdapterǁ__init____mutmut_2': xǁZendeskAdapterǁ__init____mutmut_2, 
        'xǁZendeskAdapterǁ__init____mutmut_3': xǁZendeskAdapterǁ__init____mutmut_3, 
        'xǁZendeskAdapterǁ__init____mutmut_4': xǁZendeskAdapterǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁZendeskAdapterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁZendeskAdapterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁZendeskAdapterǁ__init____mutmut_orig)
    xǁZendeskAdapterǁ__init____mutmut_orig.__name__ = 'xǁZendeskAdapterǁ__init__'

    @property
    def adapter_name(self) -> str:
        return "zendesk"

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def xǁZendeskAdapterǁconnect__mutmut_orig(self) -> bool:
        register_zendesk_metrics()
        self._connected = True
        logger.info("ZendeskAdapter connected")
        return True

    async def xǁZendeskAdapterǁconnect__mutmut_1(self) -> bool:
        register_zendesk_metrics()
        self._connected = None
        logger.info("ZendeskAdapter connected")
        return True

    async def xǁZendeskAdapterǁconnect__mutmut_2(self) -> bool:
        register_zendesk_metrics()
        self._connected = False
        logger.info("ZendeskAdapter connected")
        return True

    async def xǁZendeskAdapterǁconnect__mutmut_3(self) -> bool:
        register_zendesk_metrics()
        self._connected = True
        logger.info(None)
        return True

    async def xǁZendeskAdapterǁconnect__mutmut_4(self) -> bool:
        register_zendesk_metrics()
        self._connected = True
        logger.info("XXZendeskAdapter connectedXX")
        return True

    async def xǁZendeskAdapterǁconnect__mutmut_5(self) -> bool:
        register_zendesk_metrics()
        self._connected = True
        logger.info("zendeskadapter connected")
        return True

    async def xǁZendeskAdapterǁconnect__mutmut_6(self) -> bool:
        register_zendesk_metrics()
        self._connected = True
        logger.info("ZENDESKADAPTER CONNECTED")
        return True

    async def xǁZendeskAdapterǁconnect__mutmut_7(self) -> bool:
        register_zendesk_metrics()
        self._connected = True
        logger.info("ZendeskAdapter connected")
        return False
    
    xǁZendeskAdapterǁconnect__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁZendeskAdapterǁconnect__mutmut_1': xǁZendeskAdapterǁconnect__mutmut_1, 
        'xǁZendeskAdapterǁconnect__mutmut_2': xǁZendeskAdapterǁconnect__mutmut_2, 
        'xǁZendeskAdapterǁconnect__mutmut_3': xǁZendeskAdapterǁconnect__mutmut_3, 
        'xǁZendeskAdapterǁconnect__mutmut_4': xǁZendeskAdapterǁconnect__mutmut_4, 
        'xǁZendeskAdapterǁconnect__mutmut_5': xǁZendeskAdapterǁconnect__mutmut_5, 
        'xǁZendeskAdapterǁconnect__mutmut_6': xǁZendeskAdapterǁconnect__mutmut_6, 
        'xǁZendeskAdapterǁconnect__mutmut_7': xǁZendeskAdapterǁconnect__mutmut_7
    }
    
    def connect(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁZendeskAdapterǁconnect__mutmut_orig"), object.__getattribute__(self, "xǁZendeskAdapterǁconnect__mutmut_mutants"), args, kwargs, self)
        return result 
    
    connect.__signature__ = _mutmut_signature(xǁZendeskAdapterǁconnect__mutmut_orig)
    xǁZendeskAdapterǁconnect__mutmut_orig.__name__ = 'xǁZendeskAdapterǁconnect'

    async def xǁZendeskAdapterǁdisconnect__mutmut_orig(self) -> None:
        self._connected = False
        logger.info("ZendeskAdapter disconnected")

    async def xǁZendeskAdapterǁdisconnect__mutmut_1(self) -> None:
        self._connected = None
        logger.info("ZendeskAdapter disconnected")

    async def xǁZendeskAdapterǁdisconnect__mutmut_2(self) -> None:
        self._connected = True
        logger.info("ZendeskAdapter disconnected")

    async def xǁZendeskAdapterǁdisconnect__mutmut_3(self) -> None:
        self._connected = False
        logger.info(None)

    async def xǁZendeskAdapterǁdisconnect__mutmut_4(self) -> None:
        self._connected = False
        logger.info("XXZendeskAdapter disconnectedXX")

    async def xǁZendeskAdapterǁdisconnect__mutmut_5(self) -> None:
        self._connected = False
        logger.info("zendeskadapter disconnected")

    async def xǁZendeskAdapterǁdisconnect__mutmut_6(self) -> None:
        self._connected = False
        logger.info("ZENDESKADAPTER DISCONNECTED")
    
    xǁZendeskAdapterǁdisconnect__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁZendeskAdapterǁdisconnect__mutmut_1': xǁZendeskAdapterǁdisconnect__mutmut_1, 
        'xǁZendeskAdapterǁdisconnect__mutmut_2': xǁZendeskAdapterǁdisconnect__mutmut_2, 
        'xǁZendeskAdapterǁdisconnect__mutmut_3': xǁZendeskAdapterǁdisconnect__mutmut_3, 
        'xǁZendeskAdapterǁdisconnect__mutmut_4': xǁZendeskAdapterǁdisconnect__mutmut_4, 
        'xǁZendeskAdapterǁdisconnect__mutmut_5': xǁZendeskAdapterǁdisconnect__mutmut_5, 
        'xǁZendeskAdapterǁdisconnect__mutmut_6': xǁZendeskAdapterǁdisconnect__mutmut_6
    }
    
    def disconnect(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁZendeskAdapterǁdisconnect__mutmut_orig"), object.__getattribute__(self, "xǁZendeskAdapterǁdisconnect__mutmut_mutants"), args, kwargs, self)
        return result 
    
    disconnect.__signature__ = _mutmut_signature(xǁZendeskAdapterǁdisconnect__mutmut_orig)
    xǁZendeskAdapterǁdisconnect__mutmut_orig.__name__ = 'xǁZendeskAdapterǁdisconnect'

    async def health_check(self) -> bool:
        return self._connected

    async def xǁZendeskAdapterǁquery__mutmut_orig(
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

    async def xǁZendeskAdapterǁquery__mutmut_1(
        self,
        query_text: str,
        *,
        top_k: int = 11,
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

    async def xǁZendeskAdapterǁquery__mutmut_2(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_3(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=None, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_4(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error=None)

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_5(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_6(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, )

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_7(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=True, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_8(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="XXquery_text must be non-emptyXX")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_9(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="QUERY_TEXT MUST BE NON-EMPTY")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_10(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter(None, 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_11(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", None)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_12(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter(1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_13(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", )
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_14(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("XXzendesk_api_calls_totalXX", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_15(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("ZENDESK_API_CALLS_TOTAL", 1)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_16(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 2)
        self.metrics.increment("zendesk_api_calls_total", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_17(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment(None, 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_18(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", None)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_19(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment(1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_20(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", )

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_21(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("XXzendesk_api_calls_totalXX", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_22(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("ZENDESK_API_CALLS_TOTAL", 1)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_23(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        if not query_text:
            return QueryResult(success=False, error="query_text must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", 1)
        self.metrics.increment("zendesk_api_calls_total", 2)

        payload = {
            "query": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_24(
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

        payload = None
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_25(
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
            "XXqueryXX": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_26(
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
            "QUERY": query_text,
            "top_k": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_27(
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
            "XXtop_kXX": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_28(
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
            "TOP_K": top_k,
            "filters": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_29(
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
            "XXfiltersXX": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_30(
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
            "FILTERS": filters or {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_31(
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
            "filters": filters and {},
        }
        return QueryResult(success=True, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_32(
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
        return QueryResult(success=None, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_33(
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
        return QueryResult(success=True, data=None, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_34(
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
        return QueryResult(success=True, data=payload, metadata=None)

    async def xǁZendeskAdapterǁquery__mutmut_35(
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
        return QueryResult(data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_36(
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
        return QueryResult(success=True, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_37(
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
        return QueryResult(success=True, data=payload, )

    async def xǁZendeskAdapterǁquery__mutmut_38(
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
        return QueryResult(success=False, data=payload, metadata={"source": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_39(
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
        return QueryResult(success=True, data=payload, metadata={"XXsourceXX": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_40(
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
        return QueryResult(success=True, data=payload, metadata={"SOURCE": "zendesk"})

    async def xǁZendeskAdapterǁquery__mutmut_41(
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
        return QueryResult(success=True, data=payload, metadata={"source": "XXzendeskXX"})

    async def xǁZendeskAdapterǁquery__mutmut_42(
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
        return QueryResult(success=True, data=payload, metadata={"source": "ZENDESK"})
    
    xǁZendeskAdapterǁquery__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁZendeskAdapterǁquery__mutmut_1': xǁZendeskAdapterǁquery__mutmut_1, 
        'xǁZendeskAdapterǁquery__mutmut_2': xǁZendeskAdapterǁquery__mutmut_2, 
        'xǁZendeskAdapterǁquery__mutmut_3': xǁZendeskAdapterǁquery__mutmut_3, 
        'xǁZendeskAdapterǁquery__mutmut_4': xǁZendeskAdapterǁquery__mutmut_4, 
        'xǁZendeskAdapterǁquery__mutmut_5': xǁZendeskAdapterǁquery__mutmut_5, 
        'xǁZendeskAdapterǁquery__mutmut_6': xǁZendeskAdapterǁquery__mutmut_6, 
        'xǁZendeskAdapterǁquery__mutmut_7': xǁZendeskAdapterǁquery__mutmut_7, 
        'xǁZendeskAdapterǁquery__mutmut_8': xǁZendeskAdapterǁquery__mutmut_8, 
        'xǁZendeskAdapterǁquery__mutmut_9': xǁZendeskAdapterǁquery__mutmut_9, 
        'xǁZendeskAdapterǁquery__mutmut_10': xǁZendeskAdapterǁquery__mutmut_10, 
        'xǁZendeskAdapterǁquery__mutmut_11': xǁZendeskAdapterǁquery__mutmut_11, 
        'xǁZendeskAdapterǁquery__mutmut_12': xǁZendeskAdapterǁquery__mutmut_12, 
        'xǁZendeskAdapterǁquery__mutmut_13': xǁZendeskAdapterǁquery__mutmut_13, 
        'xǁZendeskAdapterǁquery__mutmut_14': xǁZendeskAdapterǁquery__mutmut_14, 
        'xǁZendeskAdapterǁquery__mutmut_15': xǁZendeskAdapterǁquery__mutmut_15, 
        'xǁZendeskAdapterǁquery__mutmut_16': xǁZendeskAdapterǁquery__mutmut_16, 
        'xǁZendeskAdapterǁquery__mutmut_17': xǁZendeskAdapterǁquery__mutmut_17, 
        'xǁZendeskAdapterǁquery__mutmut_18': xǁZendeskAdapterǁquery__mutmut_18, 
        'xǁZendeskAdapterǁquery__mutmut_19': xǁZendeskAdapterǁquery__mutmut_19, 
        'xǁZendeskAdapterǁquery__mutmut_20': xǁZendeskAdapterǁquery__mutmut_20, 
        'xǁZendeskAdapterǁquery__mutmut_21': xǁZendeskAdapterǁquery__mutmut_21, 
        'xǁZendeskAdapterǁquery__mutmut_22': xǁZendeskAdapterǁquery__mutmut_22, 
        'xǁZendeskAdapterǁquery__mutmut_23': xǁZendeskAdapterǁquery__mutmut_23, 
        'xǁZendeskAdapterǁquery__mutmut_24': xǁZendeskAdapterǁquery__mutmut_24, 
        'xǁZendeskAdapterǁquery__mutmut_25': xǁZendeskAdapterǁquery__mutmut_25, 
        'xǁZendeskAdapterǁquery__mutmut_26': xǁZendeskAdapterǁquery__mutmut_26, 
        'xǁZendeskAdapterǁquery__mutmut_27': xǁZendeskAdapterǁquery__mutmut_27, 
        'xǁZendeskAdapterǁquery__mutmut_28': xǁZendeskAdapterǁquery__mutmut_28, 
        'xǁZendeskAdapterǁquery__mutmut_29': xǁZendeskAdapterǁquery__mutmut_29, 
        'xǁZendeskAdapterǁquery__mutmut_30': xǁZendeskAdapterǁquery__mutmut_30, 
        'xǁZendeskAdapterǁquery__mutmut_31': xǁZendeskAdapterǁquery__mutmut_31, 
        'xǁZendeskAdapterǁquery__mutmut_32': xǁZendeskAdapterǁquery__mutmut_32, 
        'xǁZendeskAdapterǁquery__mutmut_33': xǁZendeskAdapterǁquery__mutmut_33, 
        'xǁZendeskAdapterǁquery__mutmut_34': xǁZendeskAdapterǁquery__mutmut_34, 
        'xǁZendeskAdapterǁquery__mutmut_35': xǁZendeskAdapterǁquery__mutmut_35, 
        'xǁZendeskAdapterǁquery__mutmut_36': xǁZendeskAdapterǁquery__mutmut_36, 
        'xǁZendeskAdapterǁquery__mutmut_37': xǁZendeskAdapterǁquery__mutmut_37, 
        'xǁZendeskAdapterǁquery__mutmut_38': xǁZendeskAdapterǁquery__mutmut_38, 
        'xǁZendeskAdapterǁquery__mutmut_39': xǁZendeskAdapterǁquery__mutmut_39, 
        'xǁZendeskAdapterǁquery__mutmut_40': xǁZendeskAdapterǁquery__mutmut_40, 
        'xǁZendeskAdapterǁquery__mutmut_41': xǁZendeskAdapterǁquery__mutmut_41, 
        'xǁZendeskAdapterǁquery__mutmut_42': xǁZendeskAdapterǁquery__mutmut_42
    }
    
    def query(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁZendeskAdapterǁquery__mutmut_orig"), object.__getattribute__(self, "xǁZendeskAdapterǁquery__mutmut_mutants"), args, kwargs, self)
        return result 
    
    query.__signature__ = _mutmut_signature(xǁZendeskAdapterǁquery__mutmut_orig)
    xǁZendeskAdapterǁquery__mutmut_orig.__name__ = 'xǁZendeskAdapterǁquery'

    async def xǁZendeskAdapterǁupsert__mutmut_orig(self, vectors: list[dict[str, Any]]) -> QueryResult:
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

    async def xǁZendeskAdapterǁupsert__mutmut_1(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_2(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=None, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_3(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error=None)

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_4(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_5(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, )

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_6(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=True, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_7(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="XXvectors must be non-emptyXX")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_8(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="VECTORS MUST BE NON-EMPTY")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_9(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter(None, len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_10(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", None)
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_11(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter(len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_12(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", )
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_13(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("XXzendesk_api_calls_totalXX", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_14(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("ZENDESK_API_CALLS_TOTAL", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_15(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment(None, float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_16(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", None)
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_17(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment(float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_18(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", )
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_19(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("XXzendesk_api_calls_totalXX", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_20(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("ZENDESK_API_CALLS_TOTAL", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_21(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(None))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_22(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge(None, float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_23(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", None)

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_24(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge(float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_25(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", )

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_26(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("XXzendesk_upsert_vectorsXX", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_27(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("ZENDESK_UPSERT_VECTORS", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_28(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(None))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_29(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=None,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_30(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data=None,
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_31(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata=None,
        )

    async def xǁZendeskAdapterǁupsert__mutmut_32(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_33(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_34(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            )

    async def xǁZendeskAdapterǁupsert__mutmut_35(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=False,
            data={"upserted": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_36(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"XXupsertedXX": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_37(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"UPSERTED": len(vectors)},
            metadata={"source": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_38(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"XXsourceXX": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_39(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"SOURCE": "zendesk"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_40(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "XXzendeskXX"},
        )

    async def xǁZendeskAdapterǁupsert__mutmut_41(self, vectors: list[dict[str, Any]]) -> QueryResult:
        if not vectors:
            return QueryResult(success=False, error="vectors must be non-empty")

        metrics.emit_counter("zendesk_api_calls_total", len(vectors))
        self.metrics.increment("zendesk_api_calls_total", float(len(vectors)))
        self.metrics.set_gauge("zendesk_upsert_vectors", float(len(vectors)))

        return QueryResult(
            success=True,
            data={"upserted": len(vectors)},
            metadata={"source": "ZENDESK"},
        )
    
    xǁZendeskAdapterǁupsert__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁZendeskAdapterǁupsert__mutmut_1': xǁZendeskAdapterǁupsert__mutmut_1, 
        'xǁZendeskAdapterǁupsert__mutmut_2': xǁZendeskAdapterǁupsert__mutmut_2, 
        'xǁZendeskAdapterǁupsert__mutmut_3': xǁZendeskAdapterǁupsert__mutmut_3, 
        'xǁZendeskAdapterǁupsert__mutmut_4': xǁZendeskAdapterǁupsert__mutmut_4, 
        'xǁZendeskAdapterǁupsert__mutmut_5': xǁZendeskAdapterǁupsert__mutmut_5, 
        'xǁZendeskAdapterǁupsert__mutmut_6': xǁZendeskAdapterǁupsert__mutmut_6, 
        'xǁZendeskAdapterǁupsert__mutmut_7': xǁZendeskAdapterǁupsert__mutmut_7, 
        'xǁZendeskAdapterǁupsert__mutmut_8': xǁZendeskAdapterǁupsert__mutmut_8, 
        'xǁZendeskAdapterǁupsert__mutmut_9': xǁZendeskAdapterǁupsert__mutmut_9, 
        'xǁZendeskAdapterǁupsert__mutmut_10': xǁZendeskAdapterǁupsert__mutmut_10, 
        'xǁZendeskAdapterǁupsert__mutmut_11': xǁZendeskAdapterǁupsert__mutmut_11, 
        'xǁZendeskAdapterǁupsert__mutmut_12': xǁZendeskAdapterǁupsert__mutmut_12, 
        'xǁZendeskAdapterǁupsert__mutmut_13': xǁZendeskAdapterǁupsert__mutmut_13, 
        'xǁZendeskAdapterǁupsert__mutmut_14': xǁZendeskAdapterǁupsert__mutmut_14, 
        'xǁZendeskAdapterǁupsert__mutmut_15': xǁZendeskAdapterǁupsert__mutmut_15, 
        'xǁZendeskAdapterǁupsert__mutmut_16': xǁZendeskAdapterǁupsert__mutmut_16, 
        'xǁZendeskAdapterǁupsert__mutmut_17': xǁZendeskAdapterǁupsert__mutmut_17, 
        'xǁZendeskAdapterǁupsert__mutmut_18': xǁZendeskAdapterǁupsert__mutmut_18, 
        'xǁZendeskAdapterǁupsert__mutmut_19': xǁZendeskAdapterǁupsert__mutmut_19, 
        'xǁZendeskAdapterǁupsert__mutmut_20': xǁZendeskAdapterǁupsert__mutmut_20, 
        'xǁZendeskAdapterǁupsert__mutmut_21': xǁZendeskAdapterǁupsert__mutmut_21, 
        'xǁZendeskAdapterǁupsert__mutmut_22': xǁZendeskAdapterǁupsert__mutmut_22, 
        'xǁZendeskAdapterǁupsert__mutmut_23': xǁZendeskAdapterǁupsert__mutmut_23, 
        'xǁZendeskAdapterǁupsert__mutmut_24': xǁZendeskAdapterǁupsert__mutmut_24, 
        'xǁZendeskAdapterǁupsert__mutmut_25': xǁZendeskAdapterǁupsert__mutmut_25, 
        'xǁZendeskAdapterǁupsert__mutmut_26': xǁZendeskAdapterǁupsert__mutmut_26, 
        'xǁZendeskAdapterǁupsert__mutmut_27': xǁZendeskAdapterǁupsert__mutmut_27, 
        'xǁZendeskAdapterǁupsert__mutmut_28': xǁZendeskAdapterǁupsert__mutmut_28, 
        'xǁZendeskAdapterǁupsert__mutmut_29': xǁZendeskAdapterǁupsert__mutmut_29, 
        'xǁZendeskAdapterǁupsert__mutmut_30': xǁZendeskAdapterǁupsert__mutmut_30, 
        'xǁZendeskAdapterǁupsert__mutmut_31': xǁZendeskAdapterǁupsert__mutmut_31, 
        'xǁZendeskAdapterǁupsert__mutmut_32': xǁZendeskAdapterǁupsert__mutmut_32, 
        'xǁZendeskAdapterǁupsert__mutmut_33': xǁZendeskAdapterǁupsert__mutmut_33, 
        'xǁZendeskAdapterǁupsert__mutmut_34': xǁZendeskAdapterǁupsert__mutmut_34, 
        'xǁZendeskAdapterǁupsert__mutmut_35': xǁZendeskAdapterǁupsert__mutmut_35, 
        'xǁZendeskAdapterǁupsert__mutmut_36': xǁZendeskAdapterǁupsert__mutmut_36, 
        'xǁZendeskAdapterǁupsert__mutmut_37': xǁZendeskAdapterǁupsert__mutmut_37, 
        'xǁZendeskAdapterǁupsert__mutmut_38': xǁZendeskAdapterǁupsert__mutmut_38, 
        'xǁZendeskAdapterǁupsert__mutmut_39': xǁZendeskAdapterǁupsert__mutmut_39, 
        'xǁZendeskAdapterǁupsert__mutmut_40': xǁZendeskAdapterǁupsert__mutmut_40, 
        'xǁZendeskAdapterǁupsert__mutmut_41': xǁZendeskAdapterǁupsert__mutmut_41
    }
    
    def upsert(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁZendeskAdapterǁupsert__mutmut_orig"), object.__getattribute__(self, "xǁZendeskAdapterǁupsert__mutmut_mutants"), args, kwargs, self)
        return result 
    
    upsert.__signature__ = _mutmut_signature(xǁZendeskAdapterǁupsert__mutmut_orig)
    xǁZendeskAdapterǁupsert__mutmut_orig.__name__ = 'xǁZendeskAdapterǁupsert'

    def xǁZendeskAdapterǁexport_metrics__mutmut_orig(self) -> list[dict[str, object]]:
        """Export Zendesk metrics to MCP collector gauges."""
        return export_zendesk_metrics(self.metrics)

    def xǁZendeskAdapterǁexport_metrics__mutmut_1(self) -> list[dict[str, object]]:
        """Export Zendesk metrics to MCP collector gauges."""
        return export_zendesk_metrics(None)
    
    xǁZendeskAdapterǁexport_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁZendeskAdapterǁexport_metrics__mutmut_1': xǁZendeskAdapterǁexport_metrics__mutmut_1
    }
    
    def export_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁZendeskAdapterǁexport_metrics__mutmut_orig"), object.__getattribute__(self, "xǁZendeskAdapterǁexport_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    export_metrics.__signature__ = _mutmut_signature(xǁZendeskAdapterǁexport_metrics__mutmut_orig)
    xǁZendeskAdapterǁexport_metrics__mutmut_orig.__name__ = 'xǁZendeskAdapterǁexport_metrics'


__all__ = ["ZendeskAdapter"]
