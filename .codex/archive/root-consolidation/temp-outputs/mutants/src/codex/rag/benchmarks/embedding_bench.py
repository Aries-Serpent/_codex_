"""
Embedding provider benchmarks.

Measures latency and throughput of different embedding providers.
"""

from typing import Any, Optional

import numpy as np

from .runner import BenchmarkResult, BenchmarkRunner


def benchmark_embedding_providers(
    providers: Optional[list[str]] = None, corpus_sizes: Optional[list[int]] = None, runs: int = 5
) -> dict[str, Any]:
    """
    Benchmark all available embedding providers.

    Args:
        providers: List of provider names to test (None = all)
        corpus_sizes: List of corpus sizes to test
        runs: Number of runs per benchmark

    Returns:
        Dictionary with benchmark results
    """
    if providers is None:
        providers = ["tfidf", "transformers"]  # Available providers

    if corpus_sizes is None:
        corpus_sizes = [10, 100, 1000]

    runner = BenchmarkRunner(warmup_runs=1)

    # Generate test corpus
    test_texts = {
        size: [f"This is test document number {i} with some content." for i in range(size)]
        for size in corpus_sizes
    }

    for provider_name in providers:
        try:
            provider = _get_provider(provider_name)

            for size in corpus_sizes:
                texts = test_texts[size]

                # Benchmark encoding
                result = runner.run_benchmark(
                    name=f"{provider_name}_encode_{size}",
                    func=provider.encode,  # type: ignore[attr-defined]
                    texts=texts,
                    runs=runs,
                )

                # Calculate throughput
                if result.success:
                    throughput = size / (result.duration_ms / 1000)
                    result.metadata["throughput_texts_per_sec"] = throughput  # type: ignore[index]

        except Exception as e:
            runner.results.append(
                BenchmarkResult(
                    name=f"{provider_name}_error",
                    duration_ms=0.0,
                    memory_mb=0.0,
                    success=False,
                    error=str(e),
                )
            )

    return {
        "results": [r.to_dict() for r in runner.results],
        "summary": runner.get_summary(),
    }


def _get_provider(name: str) -> object:
    """Get embedding provider by name."""
    from codex.rag.embeddings import create_embedding_provider

    if name == "tfidf":
        return create_embedding_provider("tfidf")
    if name == "transformers":
        try:
            return create_embedding_provider("transformers")
        except Exception as e:  # codeql[py/catch-all-except]
            # Fallback to TF-IDF if transformers not available
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Transformers provider failed, falling back to TF-IDF: {type(e).__name__}: {e}"
            )
            return create_embedding_provider("tfidf")
    elif name == "ollama":
        return create_embedding_provider("ollama")
    elif name == "llamacpp":
        return create_embedding_provider("llamacpp")
    elif name == "gpt4all":
        return create_embedding_provider("gpt4all")
    else:
        raise ValueError(f"Unknown provider: {name}")


def benchmark_embedding_quality(
    providers: Optional[list[str]] = None, test_queries: Optional[list[str]] = None
) -> dict[str, Any]:
    """
    Benchmark embedding quality using similarity tests.

    Args:
        providers: List of provider names to test
        test_queries: Test queries for similarity evaluation

    Returns:
        Quality metrics for each provider
    """
    if providers is None:
        providers = ["tfidf"]

    if test_queries is None:
        test_queries = [
            "machine learning algorithms",
            "data science python",
            "natural language processing",
        ]

    results = {}

    for provider_name in providers:
        try:
            provider = _get_provider(provider_name)

            # Encode queries
            query_embeddings = provider.encode(test_queries)  # type: ignore[attr-defined]

            # Calculate pairwise similarities
            similarities = []
            for i in range(len(query_embeddings)):
                for j in range(i + 1, len(query_embeddings)):
                    sim = _cosine_similarity(query_embeddings[i], query_embeddings[j])
                    similarities.append(float(sim))

            results[provider_name] = {
                "avg_similarity": np.mean(similarities),
                "std_similarity": np.std(similarities),
                "embedding_dim": len(query_embeddings[0]),
            }

        except Exception as e:
            results[provider_name] = {"error": str(e)}

    return results


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
