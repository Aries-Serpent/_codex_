from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx


def _host_port() -> tuple[str, int]:
    host = os.environ.get("SERVE_HOST", "127.0.0.1")
    port = int(os.environ.get("SERVE_PORT", "8000"))
    return host, port


async def _run_once(client: httpx.AsyncClient, idx: int) -> dict[str, Any]:
    payload = {
        "inputs": f"Ping #{idx}. What is {idx} + {idx}?",
        "generate_kwargs": {"max_new_tokens": 16},
    }
    start = time.perf_counter()
    response = await client.post("/predict", json=payload, timeout=30.0)
    latency_ms = int((time.perf_counter() - start) * 1000)
    return {"status": response.status_code, "latency_ms": latency_ms, "json": response.json()}


async def main_async(n: int = 16, concurrency: int = 4) -> None:
    host, port = _host_port()
    base_url = f"http://{host}:{port}"
    async with httpx.AsyncClient(base_url=base_url) as client:
        health = await client.get("/-/health", timeout=5.0)
        print("HEALTH:", health.status_code, health.text)

        semaphore = asyncio.Semaphore(concurrency)
        tasks: list[asyncio.Task[None]] = []

        async def runner(i: int) -> None:
            async with semaphore:
                result = await _run_once(client, i)
                print(f"req={i} code={result['status']} t={result['latency_ms']}ms")

        for i in range(n):
            tasks.append(asyncio.create_task(runner(i)))

        await asyncio.gather(*tasks)


def main() -> None:
    n = int(os.environ.get("SMOKE_N", "16"))
    concurrency = int(os.environ.get("SMOKE_C", "4"))
    asyncio.run(main_async(n=n, concurrency=concurrency))


if __name__ == "__main__":  # pragma: no cover - script entry
    main()
