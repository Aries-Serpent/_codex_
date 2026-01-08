#!/usr/bin/env python3
"""
RAG End-to-End Workflow Example
Demonstrates complete RAG system usage from indexing to querying with monitoring.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codex.rag import (
    build_index_from_files,
    manage_tenant_indices,
    Retriever,
    CachedRetriever,
    ProvenanceMetadata,
)
from codex.rag.monitoring import get_metrics
import time
import glob


def example_1_basic_indexing():
    """Example 1: Basic indexing and querying"""
    print("=" * 60)
    print("Example 1: Basic Indexing and Querying")
    print("=" * 60)
    
    # Find documentation files
    doc_files = [Path(f) for f in glob.glob("docs/**/*.md", recursive=True)]
    print(f"\nFound {len(doc_files)} documentation files")
    
    if not doc_files:
        print("No docs found, using README.md")
        doc_files = [Path("README.md")]
    
    # Build index
    print("\nBuilding index...")
    start_time = time.time()
    
    index_path = build_index_from_files(
        files=doc_files[:5],  # Limit to first 5 for demo
        index_name="docs",
        tenant_id="example",
        chunk_size=1000,
        overlap=128
    )
    
    build_time = time.time() - start_time
    print(f"✅ Index built in {build_time:.2f}s at: {index_path}")
    
    # Query the index
    print("\nQuerying index...")
    retriever = Retriever(
        index_name="docs",
        tenant_id="example"
    )
    
    query = "how to use RAG system"
    results = retriever.query(query, top_k=3)
    
    print(f"\nQuery: '{query}'")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['file']} (lines {result['start_line']}-{result['end_line']})")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Preview: {result['text'][:80]}...")
        print()


def example_2_cached_retrieval():
    """Example 2: Cached retrieval for performance"""
    print("=" * 60)
    print("Example 2: Cached Retrieval Performance")
    print("=" * 60)
    
    # Create cached retriever
    cached = CachedRetriever(
        index_name="docs",
        tenant_id="example",
        cache_ttl=3600,
        cache_maxsize=1000,
        normalize_queries=True
    )
    
    query = "RAG system features"
    
    # First query - cache miss
    print(f"\nFirst query: '{query}'")
    start1 = time.time()
    results1 = cached.query_with_cache(query, top_k=5)
    time1 = (time.time() - start1) * 1000
    print(f"⏱️  Time: {time1:.2f}ms (cache miss)")
    
    # Second query - cache hit
    print(f"\nSecond query: '{query}'")
    start2 = time.time()
    results2 = cached.query_with_cache(query, top_k=5)
    time2 = (time.time() - start2) * 1000
    print(f"⚡ Time: {time2:.2f}ms (cache hit)")
    
    # Performance improvement
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"\n🚀 Speedup: {speedup:.1f}x faster")
    
    # Cache statistics
    stats = cached.get_cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"   Hit rate: {stats['hit_rate']:.1%}")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Size: {stats['size']}/{stats['maxsize']}")


def example_3_multi_tenant():
    """Example 3: Multi-tenant index management"""
    print("=" * 60)
    print("Example 3: Multi-Tenant Index Management")
    print("=" * 60)
    
    # Create indices for different tenants
    tenants = ["project_a", "project_b"]
    
    for tenant in tenants:
        print(f"\nCreating index for {tenant}...")
        
        # In real usage, each tenant would have different docs
        doc_files = [Path(f) for f in glob.glob("docs/**/*.md", recursive=True)][:3]
        
        result = manage_tenant_indices(
            tenant_id=tenant,
            operation="create",
            index_names=["docs"],
            files=doc_files,
            chunk_size=1000
        )
        
        if result.success:
            print(f"✅ {result.message}")
        else:
            print(f"❌ {result.message}")
    
    # Query each tenant's index
    query = "documentation"
    
    for tenant in tenants:
        print(f"\nQuerying {tenant}...")
        retriever = Retriever(index_name="docs", tenant_id=tenant)
        results = retriever.query(query, top_k=2)
        print(f"   Found {len(results)} results")
    
    # List all indices
    print("\nListing all indices for project_a...")
    list_result = manage_tenant_indices(
        tenant_id="project_a",
        operation="list",
        index_names=[]
    )
    
    if list_result.details:
        for idx in list_result.details["indices"]:
            print(f"   - {idx['name']}: {idx['vectors']} vectors")


def example_4_provenance_tracking():
    """Example 4: Provenance tracking for results"""
    print("=" * 60)
    print("Example 4: Provenance Tracking")
    print("=" * 60)
    
    # Query with provenance
    retriever = Retriever(index_name="docs", tenant_id="example")
    results = retriever.query("installation", top_k=3)
    
    print("\nResults with full provenance:\n")
    
    for i, result in enumerate(results, 1):
        # Create provenance metadata
        prov = ProvenanceMetadata(
            source_file=Path(result["file"]),
            line_range=(result["start_line"], result["end_line"]),
            chunk_id=result["chunk_id"],
            indexed_at=result.get("generated_at", "unknown"),
            embedding_model="all-MiniLM-L6-v2",
            retrieval_score=result["score"],
            char_range=None,
            metadata={"query": "installation"}
        )
        
        print(f"{i}. Provenance:")
        print(f"   Source: {prov.source_file}")
        print(f"   Lines: {prov.line_range[0]}-{prov.line_range[1]}")
        print(f"   Chunk ID: {prov.chunk_id}")
        print(f"   Score: {prov.retrieval_score:.3f}")
        print(f"   Model: {prov.embedding_model}")
        
        # Serialize for storage
        prov_dict = prov.to_dict()
        print(f"   Serializable: {len(prov_dict)} fields")
        print()


def example_5_monitoring():
    """Example 5: Monitoring and metrics"""
    print("=" * 60)
    print("Example 5: Monitoring and Metrics")
    print("=" * 60)
    
    # Get global metrics
    metrics = get_metrics()
    
    # Perform some queries to generate metrics
    retriever = Retriever(index_name="docs", tenant_id="example")
    
    print("\nPerforming queries...")
    queries = [
        "installation guide",
        "API reference",
        "configuration",
        "troubleshooting",
        "examples"
    ]
    
    for query in queries:
        start = time.time()
        results = retriever.query(query, top_k=3)
        duration_ms = (time.time() - start) * 1000
        
        # Track metrics
        metrics.track_query_latency(
            duration_ms,
            tenant_id="example",
            index_name="docs"
        )
        
        print(f"   ✓ '{query}': {duration_ms:.2f}ms")
    
    # Get statistics
    print("\n📊 Metrics Summary:")
    stats = metrics.get_statistics()
    
    if stats.get("query_latency"):
        ql = stats["query_latency"]
        print(f"   Query Latency:")
        print(f"      Mean: {ql.get('mean_ms', 0):.2f}ms")
        print(f"      P95: {ql.get('p95_ms', 0):.2f}ms")
        print(f"      P99: {ql.get('p99_ms', 0):.2f}ms")
    
    print(f"   Total Queries: {stats.get('total_queries', 0)}")
    print(f"   Index Count: {stats.get('index_count', 0)}")
    
    # Export for Prometheus
    print("\n📈 Prometheus Metrics (first 10 lines):")
    prom_output = metrics.export_prometheus()
    for line in prom_output.split("\n")[:10]:
        if line:
            print(f"   {line}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("RAG End-to-End Workflow Examples")
    print("=" * 60)
    print("\nThis script demonstrates:")
    print("  1. Basic indexing and querying")
    print("  2. Cached retrieval for performance")
    print("  3. Multi-tenant index management")
    print("  4. Provenance tracking")
    print("  5. Monitoring and metrics")
    print()
    
    try:
        # Run examples
        example_1_basic_indexing()
        print("\n")
        
        example_2_cached_retrieval()
        print("\n")
        
        example_3_multi_tenant()
        print("\n")
        
        example_4_provenance_tracking()
        print("\n")
        
        example_5_monitoring()
        print("\n")
        
        print("=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
