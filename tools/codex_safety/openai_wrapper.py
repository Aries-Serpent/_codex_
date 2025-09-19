"""OpenAI wrapper with streaming, retries, and sensible defaults."""

from __future__ import annotations

import asyncio
import os
import random
from collections.abc import AsyncIterator
from typing import Any, Dict, Optional

from openai import AsyncOpenAI

MODEL = os.getenv("CODEX_MODEL", "gpt-4.1-mini")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "8192"))
CLIENT_TIMEOUT_S = int(os.getenv("OPENAI_CLIENT_TIMEOUT_S", "120"))
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "6"))
BASE_BACKOFF_S = float(os.getenv("OPENAI_BASE_BACKOFF_S", "0.5"))
MAX_CONCURRENCY = int(os.getenv("OPENAI_MAX_CONCURRENCY", "8"))

_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=CLIENT_TIMEOUT_S)
_sema = asyncio.Semaphore(MAX_CONCURRENCY)


def _jitter_delay(attempt: int) -> float:
    """Exponential backoff with full jitter, capped to 30 seconds."""

    return min(30.0, BASE_BACKOFF_S * (2**attempt)) * random.random()


async def call_openai_stream(
    prompt_messages: list[Dict[str, Any]],
    extra: Optional[Dict[str, Any]] = None,
) -> AsyncIterator[str]:
    """Stream text deltas from the OpenAI Responses API with retries."""

    extra = extra or {}
    attempt = 0
    while True:
        try:
            async with _sema:
                async with _client.responses.stream(
                    model=extra.get("model", MODEL),
                    input=prompt_messages,
                    max_output_tokens=extra.get("max_output_tokens", MAX_OUTPUT_TOKENS),
                    temperature=extra.get("temperature", 0.2),
                ) as stream:
                    async for event in stream:
                        if event.type == "response.output_text.delta":
                            yield event.delta
                        elif event.type == "response.error":
                            raise RuntimeError(str(event.error))
                        elif event.type == "response.completed":
                            return
                    raise RuntimeError("stream ended without completion")
        except asyncio.CancelledError:
            raise
        except Exception:
            if attempt >= MAX_RETRIES:
                raise
            delay = _jitter_delay(attempt)
            await asyncio.sleep(delay)
            attempt += 1


async def call_openai_json(
    prompt_messages: list[Dict[str, Any]],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Request a non-streaming response and return the JSON payload."""

    extra = extra or {}
    attempt = 0
    while True:
        try:
            async with _sema:
                response = await _client.responses.create(
                    model=extra.get("model", MODEL),
                    input=prompt_messages,
                    max_output_tokens=extra.get("max_output_tokens", MAX_OUTPUT_TOKENS),
                    temperature=extra.get("temperature", 0.2),
                )
                return response.model_dump()
        except asyncio.CancelledError:
            raise
        except Exception:
            if attempt >= MAX_RETRIES:
                raise
            delay = _jitter_delay(attempt)
            await asyncio.sleep(delay)
            attempt += 1


def chunk_text(payload: str, max_chars: int = 12_000) -> list[str]:
    """Split a long string into smaller chunks for safer API calls."""

    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    return [payload[i : i + max_chars] for i in range(0, len(payload), max_chars)]
