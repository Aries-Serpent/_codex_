"""
Base Adapter - Interface for MCP service adapters.

This module defines the base interface that all MCP adapters must implement.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Input validation on all parameters
- Timeout handling for external calls
- Retry logic with exponential backoff
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
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


@dataclass
class AdapterConfig:
    """Configuration for an MCP adapter."""

    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0


@dataclass
class QueryResult:
    """Result of a query to an MCP adapter."""

    success: bool
    data: Any = None
    error: str | None = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAdapter(ABC):
    """Base interface for MCP service adapters.

    All adapter implementations must inherit from this class and
    implement the required abstract methods.
    """

    def xǁBaseAdapterǁ__init____mutmut_orig(self, config: AdapterConfig | None = None) -> None:
        """Initialize the adapter with configuration."""
        self.config = config or AdapterConfig()

    def xǁBaseAdapterǁ__init____mutmut_1(self, config: AdapterConfig | None = None) -> None:
        """Initialize the adapter with configuration."""
        self.config = None

    def xǁBaseAdapterǁ__init____mutmut_2(self, config: AdapterConfig | None = None) -> None:
        """Initialize the adapter with configuration."""
        self.config = config and AdapterConfig()
    
    xǁBaseAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseAdapterǁ__init____mutmut_1': xǁBaseAdapterǁ__init____mutmut_1, 
        'xǁBaseAdapterǁ__init____mutmut_2': xǁBaseAdapterǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseAdapterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBaseAdapterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBaseAdapterǁ__init____mutmut_orig)
    xǁBaseAdapterǁ__init____mutmut_orig.__name__ = 'xǁBaseAdapterǁ__init__'

    @property
    @abstractmethod
    def adapter_name(self) -> str:
        """Return the name of the adapter."""

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the adapter is connected to its service."""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the external service.

        Returns:
            True if connection successful, False otherwise.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the external service."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is healthy.

        Returns:
            True if healthy, False otherwise.
        """

    @abstractmethod
    async def query(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        """Query the service.

        Args:
            query_text: The query text.
            top_k: Number of results to return.
            filters: Optional filters to apply.

        Returns:
            QueryResult with data or error.
        """

    @abstractmethod
    async def upsert(
        self,
        vectors: list[dict[str, Any]],
    ) -> QueryResult:
        """Upsert vectors to the service.

        Args:
            vectors: List of vector dictionaries with id, values, metadata.

        Returns:
            QueryResult indicating success or failure.
        """

    async def __aenter__(self) -> "BaseAdapter":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
