"""OpenAI-compatible generation provider adapter."""

from __future__ import annotations

import os
from typing import Any

from .base_adapter import BaseGenerationProvider, GenerationRequest, GenerationResponse


class OpenAICompatibleAdapter(BaseGenerationProvider):
    """Thin adapter over OpenAI-compatible chat-completions APIs."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_COMPATIBLE_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_COMPATIBLE_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL") or os.getenv("OPENAI_COMPATIBLE_MODEL") or "gpt-4o-mini"
        self._client = client

    @property
    def provider_name(self) -> str:
        return "openai-compatible"

    async def health_check(self) -> bool:
        return bool(self.api_key) or self._client is not None

    async def complete(self, request: GenerationRequest) -> GenerationResponse:
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:  # pragma: no cover - dependency optional
                raise RuntimeError("OpenAI Python SDK is not installed") from exc

            if not self.api_key:
                raise RuntimeError("OpenAI-compatible API key is not configured")

            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        response = self._client.chat.completions.create(
            model=request.model or self.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        usage_dict = {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
            "completion_tokens": getattr(usage, "completion_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0),
        }

        return GenerationResponse(
            content=content,
            model=request.model or self.model,
            usage=usage_dict,
            finish_reason=getattr(response.choices[0], "finish_reason", "stop"),
            provider=self.provider_name,
            raw={"id": getattr(response, "id", None), "model": getattr(response, "model", None)},
        )


OpenAICompatibleGenerationProvider = OpenAICompatibleAdapter
