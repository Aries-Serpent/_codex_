"""
Mock Adapter - Testing adapter that simulates AI responses.

This module provides a mock adapter for testing without making real API calls.

Author: Copilot Agent
Generated: 2025-12-24
"""

from __future__ import annotations

import time

from .base_adapter import BaseAdapter, CompletionRequest, CompletionResponse
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


class MockAdapter(BaseAdapter):
    """Mock adapter for testing.

    Simulates AI responses without making real API calls.
    Useful for unit tests and development.
    """

    def xǁMockAdapterǁ__init____mutmut_orig(self, response_template: str = "Mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = 100

    def xǁMockAdapterǁ__init____mutmut_1(self, response_template: str = "XXMock response: {prompt}XX") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = 100

    def xǁMockAdapterǁ__init____mutmut_2(self, response_template: str = "mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = 100

    def xǁMockAdapterǁ__init____mutmut_3(self, response_template: str = "MOCK RESPONSE: {PROMPT}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = 100

    def xǁMockAdapterǁ__init____mutmut_4(self, response_template: str = "Mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = None
        self._call_count = 0
        self._latency_ms = 100

    def xǁMockAdapterǁ__init____mutmut_5(self, response_template: str = "Mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = None
        self._latency_ms = 100

    def xǁMockAdapterǁ__init____mutmut_6(self, response_template: str = "Mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 1
        self._latency_ms = 100

    def xǁMockAdapterǁ__init____mutmut_7(self, response_template: str = "Mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = None

    def xǁMockAdapterǁ__init____mutmut_8(self, response_template: str = "Mock response: {prompt}") -> None:
        """Initialize the mock adapter.

        Args:
            response_template: Template for mock responses.
        """
        self._response_template = response_template
        self._call_count = 0
        self._latency_ms = 101
    
    xǁMockAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁ__init____mutmut_1': xǁMockAdapterǁ__init____mutmut_1, 
        'xǁMockAdapterǁ__init____mutmut_2': xǁMockAdapterǁ__init____mutmut_2, 
        'xǁMockAdapterǁ__init____mutmut_3': xǁMockAdapterǁ__init____mutmut_3, 
        'xǁMockAdapterǁ__init____mutmut_4': xǁMockAdapterǁ__init____mutmut_4, 
        'xǁMockAdapterǁ__init____mutmut_5': xǁMockAdapterǁ__init____mutmut_5, 
        'xǁMockAdapterǁ__init____mutmut_6': xǁMockAdapterǁ__init____mutmut_6, 
        'xǁMockAdapterǁ__init____mutmut_7': xǁMockAdapterǁ__init____mutmut_7, 
        'xǁMockAdapterǁ__init____mutmut_8': xǁMockAdapterǁ__init____mutmut_8
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMockAdapterǁ__init____mutmut_orig)
    xǁMockAdapterǁ__init____mutmut_orig.__name__ = 'xǁMockAdapterǁ__init__'

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "mock"

    async def xǁMockAdapterǁcomplete__mutmut_orig(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_1(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count = 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_2(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count -= 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_3(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 2

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_4(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(None)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_5(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms * 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_6(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1001)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_7(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = None

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_8(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=None,
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_9(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=None,
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_10(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_11(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_12(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:101],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_13(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model and "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_14(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "XXmock-modelXX",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_15(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "MOCK-MODEL",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_16(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = None
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_17(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = None

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_18(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=None,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_19(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=None,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_20(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage=None,
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_21(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason=None,
        )

    async def xǁMockAdapterǁcomplete__mutmut_22(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_23(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_24(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_25(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            )

    async def xǁMockAdapterǁcomplete__mutmut_26(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model and "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_27(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "XXmock-modelXX",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_28(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "MOCK-MODEL",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_29(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "XXprompt_tokensXX": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_30(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "PROMPT_TOKENS": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_31(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "XXcompletion_tokensXX": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_32(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "COMPLETION_TOKENS": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_33(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "XXtotal_tokensXX": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_34(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "TOTAL_TOKENS": prompt_tokens + completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_35(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens - completion_tokens,
            },
            finish_reason="stop",
        )

    async def xǁMockAdapterǁcomplete__mutmut_36(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="XXstopXX",
        )

    async def xǁMockAdapterǁcomplete__mutmut_37(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a mock completion.

        Args:
            request: The completion request.

        Returns:
            A mock completion response.
        """
        self._call_count += 1

        # Simulate latency
        time.sleep(self._latency_ms / 1000)

        content = self._response_template.format(
            prompt=request.prompt[:100],
            model=request.model or "mock-model",
        )

        # Simulate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())

        return CompletionResponse(
            content=content,
            model=request.model or "mock-model",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            finish_reason="STOP",
        )
    
    xǁMockAdapterǁcomplete__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁcomplete__mutmut_1': xǁMockAdapterǁcomplete__mutmut_1, 
        'xǁMockAdapterǁcomplete__mutmut_2': xǁMockAdapterǁcomplete__mutmut_2, 
        'xǁMockAdapterǁcomplete__mutmut_3': xǁMockAdapterǁcomplete__mutmut_3, 
        'xǁMockAdapterǁcomplete__mutmut_4': xǁMockAdapterǁcomplete__mutmut_4, 
        'xǁMockAdapterǁcomplete__mutmut_5': xǁMockAdapterǁcomplete__mutmut_5, 
        'xǁMockAdapterǁcomplete__mutmut_6': xǁMockAdapterǁcomplete__mutmut_6, 
        'xǁMockAdapterǁcomplete__mutmut_7': xǁMockAdapterǁcomplete__mutmut_7, 
        'xǁMockAdapterǁcomplete__mutmut_8': xǁMockAdapterǁcomplete__mutmut_8, 
        'xǁMockAdapterǁcomplete__mutmut_9': xǁMockAdapterǁcomplete__mutmut_9, 
        'xǁMockAdapterǁcomplete__mutmut_10': xǁMockAdapterǁcomplete__mutmut_10, 
        'xǁMockAdapterǁcomplete__mutmut_11': xǁMockAdapterǁcomplete__mutmut_11, 
        'xǁMockAdapterǁcomplete__mutmut_12': xǁMockAdapterǁcomplete__mutmut_12, 
        'xǁMockAdapterǁcomplete__mutmut_13': xǁMockAdapterǁcomplete__mutmut_13, 
        'xǁMockAdapterǁcomplete__mutmut_14': xǁMockAdapterǁcomplete__mutmut_14, 
        'xǁMockAdapterǁcomplete__mutmut_15': xǁMockAdapterǁcomplete__mutmut_15, 
        'xǁMockAdapterǁcomplete__mutmut_16': xǁMockAdapterǁcomplete__mutmut_16, 
        'xǁMockAdapterǁcomplete__mutmut_17': xǁMockAdapterǁcomplete__mutmut_17, 
        'xǁMockAdapterǁcomplete__mutmut_18': xǁMockAdapterǁcomplete__mutmut_18, 
        'xǁMockAdapterǁcomplete__mutmut_19': xǁMockAdapterǁcomplete__mutmut_19, 
        'xǁMockAdapterǁcomplete__mutmut_20': xǁMockAdapterǁcomplete__mutmut_20, 
        'xǁMockAdapterǁcomplete__mutmut_21': xǁMockAdapterǁcomplete__mutmut_21, 
        'xǁMockAdapterǁcomplete__mutmut_22': xǁMockAdapterǁcomplete__mutmut_22, 
        'xǁMockAdapterǁcomplete__mutmut_23': xǁMockAdapterǁcomplete__mutmut_23, 
        'xǁMockAdapterǁcomplete__mutmut_24': xǁMockAdapterǁcomplete__mutmut_24, 
        'xǁMockAdapterǁcomplete__mutmut_25': xǁMockAdapterǁcomplete__mutmut_25, 
        'xǁMockAdapterǁcomplete__mutmut_26': xǁMockAdapterǁcomplete__mutmut_26, 
        'xǁMockAdapterǁcomplete__mutmut_27': xǁMockAdapterǁcomplete__mutmut_27, 
        'xǁMockAdapterǁcomplete__mutmut_28': xǁMockAdapterǁcomplete__mutmut_28, 
        'xǁMockAdapterǁcomplete__mutmut_29': xǁMockAdapterǁcomplete__mutmut_29, 
        'xǁMockAdapterǁcomplete__mutmut_30': xǁMockAdapterǁcomplete__mutmut_30, 
        'xǁMockAdapterǁcomplete__mutmut_31': xǁMockAdapterǁcomplete__mutmut_31, 
        'xǁMockAdapterǁcomplete__mutmut_32': xǁMockAdapterǁcomplete__mutmut_32, 
        'xǁMockAdapterǁcomplete__mutmut_33': xǁMockAdapterǁcomplete__mutmut_33, 
        'xǁMockAdapterǁcomplete__mutmut_34': xǁMockAdapterǁcomplete__mutmut_34, 
        'xǁMockAdapterǁcomplete__mutmut_35': xǁMockAdapterǁcomplete__mutmut_35, 
        'xǁMockAdapterǁcomplete__mutmut_36': xǁMockAdapterǁcomplete__mutmut_36, 
        'xǁMockAdapterǁcomplete__mutmut_37': xǁMockAdapterǁcomplete__mutmut_37
    }
    
    def complete(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁcomplete__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁcomplete__mutmut_mutants"), args, kwargs, self)
        return result 
    
    complete.__signature__ = _mutmut_signature(xǁMockAdapterǁcomplete__mutmut_orig)
    xǁMockAdapterǁcomplete__mutmut_orig.__name__ = 'xǁMockAdapterǁcomplete'

    async def xǁMockAdapterǁhealth_check__mutmut_orig(self) -> bool:
        """Always returns True for mock adapter."""
        return True

    async def xǁMockAdapterǁhealth_check__mutmut_1(self) -> bool:
        """Always returns True for mock adapter."""
        return False
    
    xǁMockAdapterǁhealth_check__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁhealth_check__mutmut_1': xǁMockAdapterǁhealth_check__mutmut_1
    }
    
    def health_check(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁhealth_check__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁhealth_check__mutmut_mutants"), args, kwargs, self)
        return result 
    
    health_check.__signature__ = _mutmut_signature(xǁMockAdapterǁhealth_check__mutmut_orig)
    xǁMockAdapterǁhealth_check__mutmut_orig.__name__ = 'xǁMockAdapterǁhealth_check'

    def xǁMockAdapterǁget_default_model__mutmut_orig(self) -> str:
        """Return the default mock model."""
        return "mock-model-v1"

    def xǁMockAdapterǁget_default_model__mutmut_1(self) -> str:
        """Return the default mock model."""
        return "XXmock-model-v1XX"

    def xǁMockAdapterǁget_default_model__mutmut_2(self) -> str:
        """Return the default mock model."""
        return "MOCK-MODEL-V1"
    
    xǁMockAdapterǁget_default_model__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁget_default_model__mutmut_1': xǁMockAdapterǁget_default_model__mutmut_1, 
        'xǁMockAdapterǁget_default_model__mutmut_2': xǁMockAdapterǁget_default_model__mutmut_2
    }
    
    def get_default_model(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁget_default_model__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁget_default_model__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_default_model.__signature__ = _mutmut_signature(xǁMockAdapterǁget_default_model__mutmut_orig)
    xǁMockAdapterǁget_default_model__mutmut_orig.__name__ = 'xǁMockAdapterǁget_default_model'

    def get_call_count(self) -> int:
        """Return the number of calls made to this adapter."""
        return self._call_count

    def xǁMockAdapterǁreset__mutmut_orig(self) -> None:
        """Reset the call counter."""
        self._call_count = 0

    def xǁMockAdapterǁreset__mutmut_1(self) -> None:
        """Reset the call counter."""
        self._call_count = None

    def xǁMockAdapterǁreset__mutmut_2(self) -> None:
        """Reset the call counter."""
        self._call_count = 1
    
    xǁMockAdapterǁreset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁreset__mutmut_1': xǁMockAdapterǁreset__mutmut_1, 
        'xǁMockAdapterǁreset__mutmut_2': xǁMockAdapterǁreset__mutmut_2
    }
    
    def reset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁreset__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁreset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    reset.__signature__ = _mutmut_signature(xǁMockAdapterǁreset__mutmut_orig)
    xǁMockAdapterǁreset__mutmut_orig.__name__ = 'xǁMockAdapterǁreset'

    def xǁMockAdapterǁset_latency__mutmut_orig(self, ms: int) -> None:
        """Set simulated latency in milliseconds."""
        self._latency_ms = ms

    def xǁMockAdapterǁset_latency__mutmut_1(self, ms: int) -> None:
        """Set simulated latency in milliseconds."""
        self._latency_ms = None
    
    xǁMockAdapterǁset_latency__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁset_latency__mutmut_1': xǁMockAdapterǁset_latency__mutmut_1
    }
    
    def set_latency(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁset_latency__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁset_latency__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_latency.__signature__ = _mutmut_signature(xǁMockAdapterǁset_latency__mutmut_orig)
    xǁMockAdapterǁset_latency__mutmut_orig.__name__ = 'xǁMockAdapterǁset_latency'
