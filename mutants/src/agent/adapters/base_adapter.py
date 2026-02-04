"""
Base Adapter - Interface for AI provider adapters.

This module defines the base interface that all AI provider adapters must implement.

Author: Copilot Agent
Generated: 2025-12-24
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
class CompletionRequest:
    """Request for a completion from an AI provider."""

    prompt: str
    system_prompt: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7
    tools: list[dict[str, Any]] | None = None
    model: str | None = None


@dataclass
class CompletionResponse:
    """Response from an AI provider."""

    content: str
    model: str
    usage: dict[str, int]
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str = "stop"


class BaseAdapter(ABC):
    """Base interface for AI provider adapters.

    All adapter implementations must inherit from this class and
    implement the required methods.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the AI provider."""

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a completion for the given request.

        Args:
            request: The completion request.

        Returns:
            The completion response.
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the adapter is healthy and can make requests.

        Returns:
            True if healthy, False otherwise.
        """

    def xǁBaseAdapterǁget_default_model__mutmut_orig(self) -> str:
        """Return the default model for this provider."""
        return "default"

    def xǁBaseAdapterǁget_default_model__mutmut_1(self) -> str:
        """Return the default model for this provider."""
        return "XXdefaultXX"

    def xǁBaseAdapterǁget_default_model__mutmut_2(self) -> str:
        """Return the default model for this provider."""
        return "DEFAULT"
    
    xǁBaseAdapterǁget_default_model__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseAdapterǁget_default_model__mutmut_1': xǁBaseAdapterǁget_default_model__mutmut_1, 
        'xǁBaseAdapterǁget_default_model__mutmut_2': xǁBaseAdapterǁget_default_model__mutmut_2
    }
    
    def get_default_model(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseAdapterǁget_default_model__mutmut_orig"), object.__getattribute__(self, "xǁBaseAdapterǁget_default_model__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_default_model.__signature__ = _mutmut_signature(xǁBaseAdapterǁget_default_model__mutmut_orig)
    xǁBaseAdapterǁget_default_model__mutmut_orig.__name__ = 'xǁBaseAdapterǁget_default_model'

    def xǁBaseAdapterǁestimate_cost__mutmut_orig(self, usage: dict[str, int]) -> float:
        """Estimate the cost of a request based on usage.

        Args:
            usage: Token usage dictionary.

        Returns:
            Estimated cost in USD.
        """
        return 0.0

    def xǁBaseAdapterǁestimate_cost__mutmut_1(self, usage: dict[str, int]) -> float:
        """Estimate the cost of a request based on usage.

        Args:
            usage: Token usage dictionary.

        Returns:
            Estimated cost in USD.
        """
        return 1.0
    
    xǁBaseAdapterǁestimate_cost__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaseAdapterǁestimate_cost__mutmut_1': xǁBaseAdapterǁestimate_cost__mutmut_1
    }
    
    def estimate_cost(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaseAdapterǁestimate_cost__mutmut_orig"), object.__getattribute__(self, "xǁBaseAdapterǁestimate_cost__mutmut_mutants"), args, kwargs, self)
        return result 
    
    estimate_cost.__signature__ = _mutmut_signature(xǁBaseAdapterǁestimate_cost__mutmut_orig)
    xǁBaseAdapterǁestimate_cost__mutmut_orig.__name__ = 'xǁBaseAdapterǁestimate_cost'
