
from __future__ import annotations
import os, asyncio, random
from typing import AsyncIterator, Dict, Any, Optional
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("CODEX_MODEL", "gpt-4.1-mini")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "4096"))
CLIENT_TIMEOUT_S = int(os.getenv("OPENAI_CLIENT_TIMEOUT_S", "120"))
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "5"))
BASE_BACKOFF_S = float(os.getenv("OPENAI_BASE_BACKOFF_S", "0.5"))
MAX_CONCURRENCY = int(os.getenv("OPENAI_MAX_CONCURRENCY", "6"))
_sema = asyncio.Semaphore(MAX_CONCURRENCY)

def _jitter_delay(attempt:int)->float:
    return min(30.0, BASE_BACKOFF_S * (2 ** attempt)) * random.random()

async def stream(messages: list[dict], extra: Optional[Dict[str, Any]] = None) -> AsyncIterator[str]:
    extra = extra or {}
    attempt = 0
    while True:
        try:
            async with _sema:
                with client.responses.stream(
                    model=extra.get("model", MODEL),
                    input=messages,
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
            await asyncio.sleep(_jitter_delay(attempt)); attempt += 1
