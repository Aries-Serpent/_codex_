"""Factory utilities for generation providers."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from .base_adapter import BaseGenerationProvider, GenerationRequest, GenerationResponse
from .mock_adapter import MockAdapter, MockGenerationProvider
from .openai_compatible_adapter import OpenAICompatibleAdapter, OpenAICompatibleGenerationProvider
from .spark_adapter import SparkAdapter, SparkGenerationProvider


class GenerationProviderFactory:
    """Resolve a generation provider and gracefully fall back across providers."""

    def __init__(self, providers: Sequence[BaseGenerationProvider] | None = None) -> None:
        self.providers = list(providers or [
            OpenAICompatibleAdapter(),
            SparkAdapter(),
            MockAdapter(),
        ])

    def add_provider(self, provider: BaseGenerationProvider) -> None:
        self.providers.append(provider)

    async def complete(self, request: GenerationRequest) -> GenerationResponse:
        errors: list[tuple[str, Exception]] = []

        for provider in self.providers:
            try:
                healthy = await provider.health_check()
                if not healthy:
                    continue
                return await provider.complete(request)
            except Exception as exc:  # pragma: no cover - exercised via fallback logic
                errors.append((provider.provider_name, exc))

        if not self.providers:
            raise RuntimeError("No generation providers configured")

        last_error: Exception = RuntimeError("Generation provider failure")
        if errors:
            last_error = errors[-1][1]

        raise RuntimeError(
            "All generation providers failed; last error: "
            + "; ".join(f"{name}: {type(err).__name__}: {err}" for name, err in errors)
        ) from last_error

    def __iter__(self):
        return iter(self.providers)


ProviderFactory = GenerationProviderFactory


def get_generation_provider(
    *,
    providers: Iterable[BaseGenerationProvider] | None = None,
) -> GenerationProviderFactory:
    return GenerationProviderFactory(list(providers) if providers is not None else None)


def get_provider(*, providers: Iterable[BaseGenerationProvider] | None = None) -> GenerationProviderFactory:
    return get_generation_provider(providers=providers)


__all__ = [
    "GenerationProviderFactory",
    "ProviderFactory",
    "get_generation_provider",
    "get_provider",
    "MockGenerationProvider",
    "OpenAICompatibleGenerationProvider",
    "SparkGenerationProvider",
]
