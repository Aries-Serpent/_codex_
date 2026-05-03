"""
Indexing performance benchmarks.

Measures indexing throughput and build times for different corpus sizes.
"""

import tempfile
from typing import Any, Optional

from .runner import BenchmarkRunner


def benchmark_indexing(
    corpus_sizes: Optional[list[int]] = None, chunk_sizes: Optional[list[int]] = None, runs: int = 3
) -> dict[str, Any]:
    """
    Benchmark indexing performance with various corpus sizes.

    Args:
        corpus_sizes: List of document counts to test
        chunk_sizes: List of chunk sizes to test
        runs: Number of runs per benchmark

    Returns:
        Dictionary with benchmark results
    """
    if corpus_sizes is None:
        corpus_sizes = [100, 1000, 10000]

    if chunk_sizes is None:
        chunk_sizes = [500]

    runner = BenchmarkRunner(warmup_runs=0)  # Skip warmup for indexing

    for corpus_size in corpus_sizes:
        for chunk_size in chunk_sizes:
            # Generate test corpus
            documents = _generate_test_corpus(corpus_size)

            # Create temporary directory for index
            with tempfile.TemporaryDirectory() as tmpdir:
                index_name = f"test_corpus_{corpus_size}_chunk_{chunk_size}"

                # Benchmark indexing
                result = runner.run_benchmark(
                    name=f"index_{corpus_size}_docs_chunk_{chunk_size}",
                    func=_build_index,
                    documents=documents,
                    index_name=index_name,
                    chunk_size=chunk_size,
                    tmpdir=tmpdir,
                    runs=runs,
                )

                # Calculate throughput
                if result.success:
                    # Estimate chunks (documents * avg_doc_size / chunk_size)
                    avg_doc_size = 500  # Average document size in chars
                    estimated_chunks = (corpus_size * avg_doc_size) / chunk_size
                    throughput = estimated_chunks / (result.duration_ms / 1000)
                    result.metadata["chunks_per_sec"] = throughput  # type: ignore[index]
                    result.metadata["corpus_size"] = corpus_size  # type: ignore[index]
                    result.metadata["chunk_size"] = chunk_size  # type: ignore[index]

    return {
        "results": [r.to_dict() for r in runner.results],
        "summary": runner.get_summary(),
    }


def _generate_test_corpus(size: int) -> list[str]:
    """Generate synthetic test corpus."""
    return [
        f"Document {i}: This is a test document with some content about topic {i % 10}. "
        f"It contains multiple sentences to simulate real documents. "
        f"The content varies to provide diversity in the corpus. "
        f"Keywords include: data, analysis, machine learning, algorithms, testing. "
        * (i % 3 + 1)  # Vary document length
        for i in range(size)
    ]


def _build_index(documents: list[str], index_name: str, chunk_size: int, tmpdir: str) -> None:
    """Build RAG index from documents."""
    from codex.rag.embeddings import create_embedding_provider
    from codex.rag.indexer import chunk_text, persist_index

    # Use TF-IDF for fast benchmarking
    provider = create_embedding_provider("tfidf")

    # Chunk all documents
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc, chunk_size=chunk_size)
        all_chunks.extend(chunks)

    # Extract texts
    texts = [chunk[2] for chunk in all_chunks]

    # Generate embeddings
    embeddings = provider.encode(texts)

    # Persist index to tmpdir
    persist_index(
        index_name=index_name,
        embeddings=embeddings,
        chunks=all_chunks,
        tenant_id="benchmark",
        index_dir=str(tmpdir),
    )


def benchmark_parallel_vs_sequential(corpus_size: int = 1000, runs: int = 3) -> dict[str, Any]:
    """
    Compare parallel vs sequential indexing.

    Args:
        corpus_size: Number of documents
        runs: Number of runs per benchmark

    Returns:
        Comparison results
    """
    runner = BenchmarkRunner(warmup_runs=0)
    documents = _generate_test_corpus(corpus_size)

    # Sequential indexing
    with tempfile.TemporaryDirectory() as tmpdir:
        runner.run_benchmark(
            name=f"sequential_index_{corpus_size}",
            func=_build_index,
            documents=documents,
            index_name="sequential",
            chunk_size=500,
            tmpdir=tmpdir,
            runs=runs,
        )

    # Note: Parallel indexing would require threading/multiprocessing
    # implementation which is beyond basic benchmark scope

    return {
        "results": [r.to_dict() for r in runner.results],
        "summary": runner.get_summary(),
    }
