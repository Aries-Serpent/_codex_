"""
RAG Performance Benchmarking Suite.

This module provides comprehensive benchmarking tools for evaluating
RAG pipeline performance across different dimensions.
"""

from .runner import BenchmarkRunner, BenchmarkResult
from .embedding_bench import benchmark_embedding_providers, benchmark_embedding_quality
from .indexing_bench import benchmark_indexing, benchmark_parallel_vs_sequential
from .retrieval_bench import benchmark_retrieval, benchmark_cache_effectiveness
from .e2e_bench import benchmark_e2e_pipeline, benchmark_multi_query_types

__all__ = [
    "BenchmarkRunner",
    "BenchmarkResult",
    "benchmark_embedding_providers",
    "benchmark_embedding_quality",
    "benchmark_indexing",
    "benchmark_parallel_vs_sequential",
    "benchmark_retrieval",
    "benchmark_cache_effectiveness",
    "benchmark_e2e_pipeline",
    "benchmark_multi_query_types",
]
