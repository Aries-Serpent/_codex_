"""Utility helpers for resilient OpenAI API usage."""

from __future__ import annotations

import asyncio
import os
import random
from typing import Any, AsyncIterator, Dict, Optional

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tunables (sane defaults for Codex Safety usage)
MODEL = os.getenv("CODEX_MODEL", "gpt-4.1-mini")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "8192"))
CLIENT_TIMEOUT_S = int(os.getenv("OPENAI_CLIENT_TIMEOUT_S", "120"))
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "6"))
BASE_BACKOFF_S = float(os.getenv("OPENAI_BASE_BACKOFF_S", "0.5"))
MAX_CONCURRENCY = int(os.getenv("OPENAI_MAX_CONCURRENCY", "8"))

_sema = asyncio.Semaphore(MAX_CONCURRENCY)


def _jitter_delay(attempt: int) -> float:
    """Return an exponential backoff delay with full jitter."""
    return min(30.0, BASE_BACKOFF_S * (2**attempt)) * random.random()


async def call_openai_stream(
    prompt_messages: list[dict[str, Any]],
    extra: Optional[Dict[str, Any]] = None,
) -> AsyncIterator[str]:
    """Stream a response with retries and jittered backoff."""
    extra = extra or {}
    attempt = 0
    while True:
        try:
            async with _sema:
                with client.responses.stream(
                    model=extra.get("model", MODEL),
                    input=prompt_messages,
                    max_output_tokens=extra.get("max_output_tokens", MAX_OUTPUT_TOKENS),
                    temperature=extra.get("temperature", 0.2),
                    timeout=CLIENT_TIMEOUT_S,
                ) as stream:
                    for event in stream:
                        if event.type == "response.output_text.delta":
                            yield event.delta
                        elif event.type == "response.completed":
                            return
                    raise RuntimeError("stream ended without completion")
        except Exception:
            if attempt >= MAX_RETRIES:
                raise
            delay = _jitter_delay(attempt)
            await asyncio.sleep(delay)
            attempt += 1


async def call_openai_json(
    prompt_messages: list[dict[str, Any]],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Non-streaming request with retries; returns the JSON response."""
    extra = extra or {}
    attempt = 0
    while True:
        try:
            async with _sema:
                resp = client.responses.create(
                    model=extra.get("model", MODEL),
                    input=prompt_messages,
                    max_output_tokens=extra.get("max_output_tokens", MAX_OUTPUT_TOKENS),
                    temperature=extra.get("temperature", 0.2),
                    timeout=CLIENT_TIMEOUT_S,
                )
                return resp.to_dict()
        except Exception:
            if attempt >= MAX_RETRIES:
                raise
            delay = _jitter_delay(attempt)
            await asyncio.sleep(delay)
            attempt += 1


def chunk_text(content: str, max_chars: int = 12_000) -> list[str]:
    """Split text into chunks small enough for single API calls."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    return [content[i : i + max_chars] for i in range(0, len(content), max_chars)]
