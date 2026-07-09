"""
End-to-end RAG pipeline benchmarks.

Measures complete workflow performance from indexing to retrieval.
"""

import tempfile
from typing import Any, Optional

from .runner import BenchmarkRunner


def benchmark_e2e_pipeline(
    corpus_sizes: Optional[list[int]] = None,
    query_counts: Optional[list[int]] = None,
    runs: int = 3,
) -> dict[str, Any]:
    """
    Benchmark complete RAG pipeline end-to-end.

    Args:
        corpus_sizes: List of corpus sizes to test
        query_counts: Number of queries to run per corpus
        runs: Number of complete pipeline runs

    Returns:
        Dictionary with benchmark results
    """
    if corpus_sizes is None:
        corpus_sizes = [100, 1000]

    if query_counts is None:
        query_counts = [10]

    runner = BenchmarkRunner(warmup_runs=0)

    for corpus_size in corpus_sizes:
        for query_count in query_counts:
            result = runner.run_benchmark(
                name=f"e2e_{corpus_size}_docs_{query_count}_queries",
                func=_run_complete_pipeline,
                corpus_size=corpus_size,
                query_count=query_count,
                runs=runs,
            )

            if result.success:
                result.metadata["corpus_size"] = corpus_size  # type: ignore[index]
                result.metadata["query_count"] = query_count  # type: ignore[index]
                result.metadata["total_operations"] = corpus_size + query_count  # type: ignore[index]

    return {
        "results": [r.to_dict() for r in runner.results],
        "summary": runner.get_summary(),
    }


def _run_complete_pipeline(corpus_size: int, query_count: int) -> dict[str, Any]:
    """
    Run complete RAG pipeline: build index + queries.

    Args:
        corpus_size: Number of documents to index
        query_count: Number of queries to execute

    Returns:
        Pipeline execution results
    """
    from codex.rag.embeddings import create_embedding_provider
    from codex.rag.indexer import chunk_text, persist_index
    from codex.rag.retriever import Retriever

    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Generate corpus
        documents = [
            f"Document {i}: Content about topic {i % 10} including "
            f"information on data science, machine learning, NLP, and AI. "
            f"This document contains multiple sentences with varied content. " * (i % 3 + 1)
            for i in range(corpus_size)
        ]

        # Step 2: Create embeddings provider
        provider = create_embedding_provider("tfidf")

        # Step 3: Chunk documents
        all_chunks = []
        for doc in documents:
            chunks = chunk_text(doc, chunk_size=500)
            all_chunks.extend(chunks)

        # Step 4: Generate embeddings
        texts = [chunk[2] for chunk in all_chunks]
        embeddings = provider.encode(texts)

        # Step 5: Build and persist index
        index_name = "e2e_test"
        persist_index(
            index_name=index_name,
            embeddings=embeddings,
            chunks=all_chunks,
            tenant_id="benchmark",
            index_dir=tmpdir,
        )

        # Step 6: Create retriever
        retriever = Retriever(index_name=index_name, tenant_id="benchmark", index_dir=tmpdir)

        # Step 7: Execute queries
        queries = [
            "machine learning algorithms",
            "data science techniques",
            "natural language processing",
            "artificial intelligence applications",
            "deep learning models",
        ]

        query_results = []
        for i in range(query_count):
            query = queries[i % len(queries)]
            results = retriever.query(query, top_k=5)
            query_results.append(len(results))

        return {
            "chunks_indexed": len(all_chunks),
            "queries_executed": query_count,
            "avg_results_per_query": sum(query_results) / len(query_results),
        }


def benchmark_multi_query_types(index_size: int = 1000, runs: int = 5) -> dict[str, Any]:
    """
    Benchmark different query types (simple, complex, multi-term).

    Args:
        index_size: Size of test index
        runs: Number of runs per query type

    Returns:
        Results for different query types
    """
    runner = BenchmarkRunner(warmup_runs=1)

    # Build test index once
    with tempfile.TemporaryDirectory() as tmpdir:
        _build_e2e_index(index_size, tmpdir)

        query_types = {
            "simple": "algorithms",
            "compound": "machine learning algorithms",
            "complex": "machine learning algorithms for natural language processing",
            "multi_term": "data science AND machine learning OR artificial intelligence",
        }

        for query_type, query in query_types.items():
            result = runner.run_benchmark(
                name=f"query_type_{query_type}",
                func=_execute_query,
                query=query,
                index_name="e2e_test",
                tmpdir=tmpdir,
                runs=runs,
            )

            if result.success:
                result.metadata["query_type"] = query_type  # type: ignore[index]
                result.metadata["query_length"] = len(query.split())  # type: ignore[index]

    return {
        "results": [r.to_dict() for r in runner.results],
        "summary": runner.get_summary(),
    }


def _build_e2e_index(size: int, tmpdir: str) -> None:
    """Build test index for e2e benchmarks."""
    from codex.rag.embeddings import create_embedding_provider
    from codex.rag.indexer import chunk_text, persist_index

    provider = create_embedding_provider("tfidf")

    documents = [
        f"Document {i} with content about various topics including "
        f"machine learning, data science, algorithms, and testing. " * 3
        for i in range(size)
    ]

    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc, chunk_size=500)
        all_chunks.extend(chunks)

    texts = [chunk[2] for chunk in all_chunks]
    embeddings = provider.encode(texts)

    persist_index(
        index_name="e2e_test",
        embeddings=embeddings,
        chunks=all_chunks,
        tenant_id="benchmark",
        index_dir=tmpdir,
    )


def _execute_query(query: str, index_name: str, tmpdir: str) -> list[Any]:
    """Execute a single query."""
    from codex.rag.retriever import Retriever

    retriever = Retriever(index_name=index_name, tenant_id="benchmark", index_dir=tmpdir)

    return retriever.query(query, top_k=5)
