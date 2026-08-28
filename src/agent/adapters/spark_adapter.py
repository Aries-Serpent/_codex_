"""Spark generation provider adapter."""

from __future__ import annotations

import os
from typing import Any

from .base_adapter import BaseGenerationProvider, GenerationRequest, GenerationResponse


class SparkAdapter(BaseGenerationProvider):
    """Adapter for Spark-backed generation endpoints.

    The implementation intentionally mirrors the OpenAI-compatible request/response
    contract so higher-order orchestration can swap providers without changing the
    call site.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("SPARK_API_KEY") or os.getenv("SPARK_TOKEN")
        self.base_url = base_url or os.getenv("SPARK_BASE_URL") or "https://api.spark.example/v1"
        self.model = model or os.getenv("SPARK_MODEL") or "spark-lite"
        self._client = client

    @property
    def provider_name(self) -> str:
        return "spark"

    async def health_check(self) -> bool:
        return bool(self.api_key) or self._client is not None

    async def complete(self, request: GenerationRequest) -> GenerationResponse:
        if self._client is None:
            self._client = {"chat": {"completions": {"create": self._simulate_response}}}

        payload = {
            "model": request.model or self.model,
            "messages": [
                {"role": "user", "content": request.prompt},
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        if request.system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": request.system_prompt})

        response = self._client["chat"]["completions"]["create"](payload)
        usage = {
            "prompt_tokens": len(request.prompt.split()),
            "completion_tokens": len(response["content"].split()),
            "total_tokens": len(request.prompt.split()) + len(response["content"].split()),
        }
        return GenerationResponse(
            content=response["content"],
            model=response["model"],
            usage=usage,
            finish_reason=response.get("finish_reason", "stop"),
            provider=self.provider_name,
            raw=response,
        )

    def _simulate_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = payload["messages"][-1]["content"]
        content = f"[spark] {prompt.strip()}"
        model = payload.get("model", self.model)
        return {
            "content": content,
            "model": model,
            "finish_reason": "stop",
        }


SparkGenerationProvider = SparkAdapter
