"""
Retrieval performance benchmarks.

Measures query latency and accuracy for semantic search.
"""

import tempfile
from typing import Any, Optional

from .runner import BenchmarkRunner


def benchmark_retrieval(
    index_sizes: Optional[list[int]] = None,
    top_k_values: Optional[list[int]] = None,
    runs: int = 10,
) -> dict[str, Any]:
    """
    Benchmark retrieval performance with various index sizes.

    Args:
        index_sizes: List of index sizes to test
        top_k_values: List of top-k values to test
        runs: Number of runs per benchmark

    Returns:
        Dictionary with benchmark results
    """
    if index_sizes is None:
        index_sizes = [100, 1000, 10000]

    if top_k_values is None:
        top_k_values = [1, 5, 10]

    runner = BenchmarkRunner(warmup_runs=2)

    test_queries = [
        "machine learning algorithms",
        "data processing pipeline",
        "neural network architecture",
        "information retrieval system",
        "semantic search implementation",
    ]

    for index_size in index_sizes:
        # Build test index
        with tempfile.TemporaryDirectory() as tmpdir:
            index_name = f"bench_index_{index_size}"
            _build_test_index(index_size, index_name, tmpdir)

            for top_k in top_k_values:
                for query in test_queries:
                    # Benchmark query
                    result = runner.run_benchmark(
                        name=f"query_{index_size}_docs_top{top_k}",
                        func=_query_index,
                        query=query,
                        index_name=index_name,
                        top_k=top_k,
                        tmpdir=tmpdir,
                        runs=runs,
                    )

                    if result.success:
                        result.metadata["index_size"] = index_size  # type: ignore[index]
                        result.metadata["top_k"] = top_k  # type: ignore[index]

    # Calculate percentiles
    _calculate_percentiles(runner.results)

    return {
        "results": [r.to_dict() for r in runner.results],
        "summary": runner.get_summary(),
        "percentiles": _get_latency_percentiles(runner.results),
    }


def _build_test_index(size: int, index_name: str, tmpdir: str) -> None:
    """Build a test index with specified size."""
    from codex.rag.embeddings import create_embedding_provider
    from codex.rag.indexer import chunk_text, persist_index

    provider = create_embedding_provider("tfidf")

    # Generate test documents
    documents = [
        f"Document {i} about topic {i % 10} with content related to "
        f"machine learning, data science, algorithms, and testing. " * (i % 5 + 1)
        for i in range(size)
    ]

    # Chunk and embed
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc, chunk_size=500)
        all_chunks.extend(chunks)

    texts = [chunk[2] for chunk in all_chunks]
    embeddings = provider.encode(texts)

    # Persist
    persist_index(
        index_name=index_name,
        embeddings=embeddings,
        chunks=all_chunks,
        tenant_id="benchmark",
        index_dir=tmpdir,
    )


def _query_index(query: str, index_name: str, top_k: int, tmpdir: str) -> list[dict[str, Any]]:
    """Query the index and return results."""
    from codex.rag.retriever import Retriever

    retriever = Retriever(index_name=index_name, tenant_id="benchmark", index_dir=tmpdir)

    return retriever.query(query, top_k=top_k)


def _calculate_percentiles(results: list[Any]) -> None:
    """Calculate and add percentile information to results."""
    import statistics

    durations = [r.duration_ms for r in results if r.success]

    if not durations:
        return

    p50 = statistics.median(durations)
    p95 = _percentile(durations, 0.95)
    p99 = _percentile(durations, 0.99)

    for result in results:
        if result.success and result.metadata:
            result.metadata["p50_ms"] = p50
            result.metadata["p95_ms"] = p95
            result.metadata["p99_ms"] = p99


def _percentile(data: list[float], percentile: float) -> float:
    """Calculate percentile."""
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile)
    return sorted_data[min(index, len(sorted_data) - 1)]


def _get_latency_percentiles(results: list[Any]) -> dict[str, float]:
    """Get latency percentiles from results."""
    import statistics

    durations = [r.duration_ms for r in results if r.success]

    if not durations:
        return {}

    return {
        "p50_ms": statistics.median(durations),
        "p95_ms": _percentile(durations, 0.95),
        "p99_ms": _percentile(durations, 0.99),
        "mean_ms": statistics.mean(durations),
        "min_ms": min(durations),
        "max_ms": max(durations),
    }


def benchmark_cache_effectiveness(index_size: int = 1000, runs: int = 20) -> dict[str, Any]:
    """
    Benchmark cache hit rates and effectiveness.

    Args:
        index_size: Size of test index
        runs: Number of query runs

    Returns:
        Cache performance metrics
    """
    # Note: Cache benchmarking requires cache implementation
    # This is a placeholder for future implementation
    return {
        "note": "Cache benchmarking requires cache middleware implementation",
        "index_size": index_size,
        "planned_runs": runs,
    }
