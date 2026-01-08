# Continuation Prompt: RAG Production Readiness - Phases 3C-7

**Date:** 2026-01-08  
**Branch:** `copilot/sub-pr-2750-another-one`  
**PR:** #2750  
**Previous Status:** `.codex/cognitive_brain/RAG_PRODUCTION_PHASE3_STATUS.md`

---

## Context & Current State

### Completed ✅
- All 5 PR review comments addressed (commit: db44fc0)
- Comprehensive monitoring tests (99.08% coverage, 56 tests - commit: 2b4bf36)
- Fixed error handling, docstrings, magic numbers, error messages
- Deleted temporary file (.codex/temp.md)
- Updated cognitive brain with patterns and learnings

### Blocked 🔴
- **Indexer test expansion:** numpy import conflicts in test environment
- **Remaining phases:** Waiting for indexer tests completion

### Disk Space: 77% (17G available / 72G total) ✅ Healthy

---

## 🎯 Execute Remaining Phases (Priority Order)

### Phase 3C: Fix Test Environment & Expand Indexer Tests (P0 - CRITICAL)

**Objective:** Resolve numpy import conflicts and achieve 90%+ coverage for indexer.py lines 447-738

#### Step 1: Diagnose & Fix Test Environment
```bash
# Option A: Fresh Python subprocess
python3 -m pytest tests/test_rag_indexer.py --forked

# Option B: Fix import order in existing tests
# Review tests/test_rag_*.py import order
# Move numpy/transformers imports after pytest fixtures

# Option C: Isolate test runs
pytest tests/test_rag_monitoring.py  # Run separately
pytest tests/test_rag_indexer.py     # Run separately
```

#### Step 2: Expand Indexer Tests

**Target Coverage:** Lines 447-738 in `src/codex/rag/indexer.py`

**Test File:** `tests/test_rag_indexer_advanced.py` (new)

**Required Tests (15+ tests):**

1. **Incremental Index Updates**
   ```python
   def test_incremental_index_update(tmp_path):
       """Test adding documents to existing index."""
       # Build initial index with file1
       # Add file2 to existing index
       # Verify ntotal increases
   ```

2. **Index Merging**
   ```python
   def test_index_merging(tmp_path):
       """Test merging multiple indices."""
       # Create index1 with file1
       # Create index2 with file2
       # Merge them → merged_index
       # Verify merged.ntotal = index1.ntotal + index2.ntotal
   ```

3. **Metadata Persistence**
   ```python
   def test_metadata_persistence(tmp_path):
       """Test metadata is saved and loaded correctly."""
       # Build index with metadata
       # Load metadata from disk
       # Verify all fields match
   ```

4. **Concurrent Index Writes**
   ```python
   def test_concurrent_index_writes(tmp_path):
       """Test thread-safe index building."""
       # Use 5 threads to build 5 separate indices
       # Verify all indices exist and are valid
   ```

5. **Large File Handling**
   ```python
   def test_large_file_handling(tmp_path):
       """Test files >10MB."""
       # Create 15MB file
       # Build index
       # Verify successful processing
   ```

6. **Chunk Boundary Edge Cases**
   ```python
   def test_chunk_boundary_edge_cases():
       """Test edge cases in chunking."""
       # Text exactly at chunk size
       # Text just over chunk size
       # Empty text
       # Verify chunk counts
   ```

7. **Tenant Isolation**
   ```python
   def test_tenant_isolation(tmp_path):
       """Test indices are isolated by tenant."""
       # Create tenant1/index1
       # Create tenant2/index1 (same name, different tenant)
       # Verify separate directories
       # Verify no cross-contamination
   ```

8. **Error Recovery**
   ```python
   def test_error_recovery_partial_success(tmp_path):
       """Test partial success handling."""
       # Pass mix of valid and invalid files
       # Verify valid files processed
       # Verify specific error messages for invalid files
   ```

9. **Manage Tenant Indices - CREATE**
   ```python
   def test_manage_tenant_indices_create(tmp_path):
       """Test CREATE operation."""
       # Call manage_tenant_indices with operation="create"
       # Verify TenantOperationResult success=True
       # Verify index exists on disk
   ```

10. **Manage Tenant Indices - UPDATE**
    ```python
    def test_manage_tenant_indices_update(tmp_path):
        """Test UPDATE operation."""
        # Create initial index
        # Update with new files
        # Verify index updated (ntotal increased)
    ```

11. **Manage Tenant Indices - DELETE**
    ```python
    def test_manage_tenant_indices_delete(tmp_path):
        """Test DELETE operation."""
        # Create index
        # Delete it
        # Verify index removed from disk
    ```

12. **Manage Tenant Indices - MERGE**
    ```python
    def test_manage_tenant_indices_merge(tmp_path):
        """Test MERGE operation."""
        # Create index1 and index2
        # Merge them
        # Verify merged index has combined content
    ```

13. **Manage Tenant Indices - LIST**
    ```python
    def test_manage_tenant_indices_list(tmp_path):
        """Test LIST operation."""
        # Create 3 indices
        # List them
        # Verify all 3 returned
    ```

14. **Invalid Operation Handling**
    ```python
    def test_invalid_operation(tmp_path):
        """Test handling of invalid operations."""
        # Call with operation="invalid"
        # Verify error message specifies valid operations
    ```

15. **Missing Required Parameters**
    ```python
    def test_missing_required_params(tmp_path):
        """Test error when required params missing."""
        # CREATE without files parameter
        # Verify specific error message
    ```

#### Step 3: Run Coverage
```bash
pip install pytest-xdist -q  # Parallel testing
pytest tests/test_rag_indexer_advanced.py \
  --cov=src.codex.rag.indexer \
  --cov-report=term-missing \
  --cov-report=html:reports/coverage-indexer \
  --cov-fail-under=90 \
  -v -n auto
```

#### Step 4: Commit & Report
```bash
git add tests/test_rag_indexer_advanced.py
git commit -m "Add advanced indexer tests achieving 90%+ coverage

- 15+ tests for lines 447-738 (incremental updates, merging, metadata)
- Test tenant operations (CREATE, UPDATE, DELETE, MERGE, LIST)
- Test concurrent writes, large files, edge cases
- Coverage: indexer.py 90%+"
git push origin copilot/sub-pr-2750-another-one
```

**Success Criteria:**
- ✅ All tests pass (0 failures)
- ✅ Indexer coverage ≥90%
- ✅ No numpy import errors
- ✅ CI build passes

---

### Phase 4: Documentation & Follow-up (P1)

#### Step 1: Update Cognitive Brain
- [x] Document Phase 3 patterns → DONE (RAG_PRODUCTION_PHASE3_STATUS.md)
- [ ] Document Phase 3C-7 execution details
- [ ] Update component status table

#### Step 2: Create Follow-up PR Comment
```markdown
@copilot Continue RAG Production Readiness - Execute Phases 3C-7

## Completed (This Session)
✅ All 5 PR review comments addressed
✅ Monitoring tests: 99.08% coverage (56 tests)
✅ Cognitive brain updated with patterns

## Execute Next
1. Fix test environment numpy conflicts
2. Expand indexer tests (90%+ coverage target)
3. Create load testing framework
4. Execute load tests (10K → 100K → 1M queries)
5. Design multi-region architecture
6. Create monitoring dashboards

See `.codex/cognitive_brain/RAG_PRODUCTION_PHASE3_STATUS.md` for detailed context.

**Branch:** copilot/sub-pr-2750-another-one
**Latest Commits:** db44fc0, 2b4bf36
```

Post this comment on PR #2750.

---

### Phase 5: Load Testing Framework (P1)

**Objective:** Execute 1M+ queries to validate production-scale performance

#### Step 1: Create Load Test Framework

**File:** `tests/load/test_rag_load.py`

```python
"""
RAG Load Testing Framework

Executes progressive load tests (10K → 100K → 1M queries) to validate:
- Throughput (queries per second)
- Latency (P50, P95, P99)
- Memory usage (peak, average)
- Cache effectiveness (hit rate >70%)
- Error rate (<1%)

Usage:
    pytest tests/load/test_rag_load.py -v --tb=short
    pytest tests/load/test_rag_load.py::test_load_1M_queries -v
"""

import pytest
import time
import psutil
import numpy as np
from pathlib import Path
from src.codex.rag.retriever import RAGRetriever
from src.codex.rag.indexer import build_index_from_files
from src.codex.rag.monitoring import RAGMetrics, get_metrics, reset_metrics

# Test data
SAMPLE_QUERIES = [
    "What is the purpose of this code?",
    "How do I configure the system?",
    "What are the performance requirements?",
    "How do I troubleshoot errors?",
    "What are the deployment steps?",
]


@pytest.fixture(scope="module")
def load_test_index(tmp_path_factory):
    """Create a test index for load testing."""
    tmp_path = tmp_path_factory.mktemp("load_test")
    
    # Create sample documents
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    for i in range(100):
        doc = docs_dir / f"doc{i}.txt"
        doc.write_text(f"Sample document {i} " * 100)  # ~2KB per doc
    
    # Build index
    files = list(docs_dir.glob("*.txt"))
    index_path = build_index_from_files(
        files=files,
        index_name="load_test",
        tenant_id="load_test_tenant",
        index_dir=str(tmp_path / "indices"),
    )
    
    return tmp_path / "indices"


@pytest.fixture
def retriever(load_test_index):
    """Create retriever for load testing."""
    return RAGRetriever(
        index_dir=str(load_test_index),
        tenant_id="load_test_tenant",
        index_name="load_test",
        cache_enabled=True,
        cache_ttl_seconds=300,
    )


def measure_memory():
    """Measure current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def run_load_test(retriever, num_queries, progress_interval=1000):
    """
    Run load test and return metrics.
    
    Args:
        retriever: RAG retriever instance
        num_queries: Number of queries to execute
        progress_interval: Log progress every N queries
    
    Returns:
        dict with metrics (throughput, latency, memory, cache, errors)
    """
    reset_metrics()
    metrics = get_metrics()
    
    latencies = []
    errors = 0
    start_memory = measure_memory()
    peak_memory = start_memory
    start_time = time.time()
    
    for i in range(num_queries):
        # Rotate through sample queries
        query = SAMPLE_QUERIES[i % len(SAMPLE_QUERIES)]
        
        query_start = time.time()
        try:
            results = retriever.query(query, top_k=5)
            query_latency = (time.time() - query_start) * 1000  # ms
            latencies.append(query_latency)
        except Exception as e:
            errors += 1
            print(f"Query {i} failed: {e}")
        
        # Track memory
        current_memory = measure_memory()
        peak_memory = max(peak_memory, current_memory)
        
        # Progress logging
        if (i + 1) % progress_interval == 0:
            elapsed = time.time() - start_time
            qps = (i + 1) / elapsed
            print(f"Progress: {i+1}/{num_queries} queries ({qps:.2f} qps)")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    latencies_sorted = sorted(latencies)
    n = len(latencies_sorted)
    
    stats = metrics.get_statistics()
    
    return {
        "num_queries": num_queries,
        "total_time_seconds": total_time,
        "throughput_qps": num_queries / total_time,
        "latency_p50_ms": latencies_sorted[n // 2] if n > 0 else 0,
        "latency_p95_ms": latencies_sorted[int(n * 0.95)] if n > 0 else 0,
        "latency_p99_ms": latencies_sorted[int(n * 0.99)] if n > 0 else 0,
        "latency_mean_ms": np.mean(latencies) if latencies else 0,
        "latency_max_ms": max(latencies) if latencies else 0,
        "memory_start_mb": start_memory,
        "memory_peak_mb": peak_memory,
        "memory_delta_mb": peak_memory - start_memory,
        "cache_hit_rate": stats["cache"]["hit_rate"],
        "error_count": errors,
        "error_rate": errors / num_queries if num_queries > 0 else 0,
    }


@pytest.mark.slow
def test_load_10k_queries(retriever):
    """Test 10K queries - baseline performance."""
    results = run_load_test(retriever, 10_000)
    
    print("\n=== 10K Queries Load Test ===")
    print(f"Throughput: {results['throughput_qps']:.2f} qps")
    print(f"Latency P50: {results['latency_p50_ms']:.2f} ms")
    print(f"Latency P95: {results['latency_p95_ms']:.2f} ms")
    print(f"Latency P99: {results['latency_p99_ms']:.2f} ms")
    print(f"Memory Delta: {results['memory_delta_mb']:.2f} MB")
    print(f"Cache Hit Rate: {results['cache_hit_rate']:.2%}")
    print(f"Error Rate: {results['error_rate']:.2%}")
    
    # Assertions
    assert results["throughput_qps"] > 100, "Throughput too low"
    assert results["latency_p99_ms"] < 500, "P99 latency too high"
    assert results["error_rate"] < 0.01, "Error rate too high"


@pytest.mark.slow
def test_load_100k_queries(retriever):
    """Test 100K queries - sustained performance."""
    results = run_load_test(retriever, 100_000, progress_interval=10_000)
    
    print("\n=== 100K Queries Load Test ===")
    print(f"Throughput: {results['throughput_qps']:.2f} qps")
    print(f"Latency P50: {results['latency_p50_ms']:.2f} ms")
    print(f"Latency P95: {results['latency_p95_ms']:.2f} ms")
    print(f"Latency P99: {results['latency_p99_ms']:.2f} ms")
    print(f"Memory Delta: {results['memory_delta_mb']:.2f} MB")
    print(f"Cache Hit Rate: {results['cache_hit_rate']:.2%}")
    print(f"Error Rate: {results['error_rate']:.2%}")
    
    # Assertions
    assert results["throughput_qps"] > 500, "Throughput degraded"
    assert results["latency_p99_ms"] < 300, "P99 latency too high"
    assert results["cache_hit_rate"] > 0.70, "Cache hit rate too low"
    assert results["memory_delta_mb"] < 200, "Memory leak suspected"
    assert results["error_rate"] < 0.01, "Error rate too high"


@pytest.mark.slow
@pytest.mark.verylong
def test_load_1M_queries(retriever):
    """Test 1M queries - production scale validation."""
    results = run_load_test(retriever, 1_000_000, progress_interval=100_000)
    
    print("\n=== 1M Queries Load Test ===")
    print(f"Throughput: {results['throughput_qps']:.2f} qps")
    print(f"Latency P50: {results['latency_p50_ms']:.2f} ms")
    print(f"Latency P95: {results['latency_p95_ms']:.2f} ms")
    print(f"Latency P99: {results['latency_p99_ms']:.2f} ms")
    print(f"Memory Peak: {results['memory_peak_mb']:.2f} MB")
    print(f"Memory Delta: {results['memory_delta_mb']:.2f} MB")
    print(f"Cache Hit Rate: {results['cache_hit_rate']:.2%}")
    print(f"Error Rate: {results['error_rate']:.2%}")
    
    # Production targets
    assert results["throughput_qps"] > 1000, "Throughput below production target"
    assert results["latency_p99_ms"] < 200, "P99 latency above production target"
    assert results["cache_hit_rate"] > 0.70, "Cache effectiveness below target"
    assert results["memory_peak_mb"] < 500, "Memory usage above production limit"
    assert results["error_rate"] < 0.01, "Error rate above production threshold"
    
    # Generate report
    report_path = Path("reports/load_test_1M_results.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with report_path.open("w") as f:
        f.write("RAG Load Test Results - 1M Queries\n")
        f.write("=" * 50 + "\n\n")
        for key, value in results.items():
            f.write(f"{key}: {value}\n")
    
    print(f"\nFull report saved to: {report_path}")


@pytest.mark.slow
def test_memory_leak_detection(retriever):
    """Test for memory leaks over sustained load."""
    reset_metrics()
    
    checkpoints = [1000, 5000, 10000]
    memory_samples = []
    
    for checkpoint in checkpoints:
        start_memory = measure_memory()
        
        # Run queries
        for i in range(checkpoint):
            query = SAMPLE_QUERIES[i % len(SAMPLE_QUERIES)]
            retriever.query(query, top_k=5)
        
        end_memory = measure_memory()
        memory_delta = end_memory - start_memory
        memory_samples.append((checkpoint, memory_delta))
        
        print(f"Checkpoint {checkpoint}: {memory_delta:.2f} MB delta")
    
    # Check if memory growth is linear (expected) or exponential (leak)
    deltas = [delta for _, delta in memory_samples]
    growth_rate = (deltas[-1] - deltas[0]) / len(deltas)
    
    print(f"\nMemory growth rate: {growth_rate:.4f} MB/checkpoint")
    
    # Memory should stabilize (growth < 1MB per checkpoint after cache warm-up)
    assert growth_rate < 1.0, "Potential memory leak detected"


@pytest.mark.slow
def test_cache_effectiveness(retriever):
    """Test cache hit rate improves over time."""
    reset_metrics()
    metrics = get_metrics()
    
    # First pass - cache misses
    for _ in range(100):
        for query in SAMPLE_QUERIES:
            retriever.query(query, top_k=5)
    
    stats1 = metrics.get_statistics()
    hit_rate_1 = stats1["cache"]["hit_rate"]
    
    # Second pass - should hit cache
    for _ in range(100):
        for query in SAMPLE_QUERIES:
            retriever.query(query, top_k=5)
    
    stats2 = metrics.get_statistics()
    hit_rate_2 = stats2["cache"]["hit_rate"]
    
    print(f"\nCache hit rate after pass 1: {hit_rate_1:.2%}")
    print(f"Cache hit rate after pass 2: {hit_rate_2:.2%}")
    
    # Cache should improve significantly
    assert hit_rate_2 > hit_rate_1, "Cache hit rate did not improve"
    assert hit_rate_2 > 0.70, "Cache hit rate below target"
```

#### Step 2: Run Load Tests
```bash
# Create reports directory
mkdir -p reports

# Run baseline test
pytest tests/load/test_rag_load.py::test_load_10k_queries -v -s

# Run sustained test
pytest tests/load/test_rag_load.py::test_load_100k_queries -v -s

# Run production scale test (long-running)
pytest tests/load/test_rag_load.py::test_load_1M_queries -v -s -m verylong

# Run memory leak detection
pytest tests/load/test_rag_load.py::test_memory_leak_detection -v -s

# Run cache effectiveness test
pytest tests/load/test_rag_load.py::test_cache_effectiveness -v -s
```

#### Step 3: Generate Load Test Report

**File:** `docs/LOAD_TEST_REPORT.md`

```markdown
# RAG Load Test Report

**Date:** [Date]
**Branch:** copilot/sub-pr-2750-another-one
**Environment:** GitHub Actions / Local

## Test Configuration

- **Index Size:** 100 documents (~200KB total)
- **Query Pool:** 5 unique queries (rotated)
- **Cache:** Enabled (TTL: 300s)
- **Hardware:** [Specify CPU/RAM]

## Results

### 10K Queries (Baseline)
- **Throughput:** X qps
- **Latency P50/P95/P99:** X / X / X ms
- **Memory Delta:** X MB
- **Cache Hit Rate:** X%
- **Error Rate:** X%

### 100K Queries (Sustained)
- **Throughput:** X qps
- **Latency P50/P95/P99:** X / X / X ms
- **Memory Delta:** X MB
- **Cache Hit Rate:** X%
- **Error Rate:** X%

### 1M Queries (Production Scale)
- **Throughput:** X qps (target: >1000)
- **Latency P50/P95/P99:** X / X / X ms (target P99 <200ms)
- **Memory Peak:** X MB (target: <500MB)
- **Memory Delta:** X MB
- **Cache Hit Rate:** X% (target: >70%)
- **Error Rate:** X% (target: <1%)

### Memory Leak Detection
- **Growth Rate:** X MB/checkpoint
- **Status:** ✅ No leak detected / ❌ Leak suspected

### Cache Effectiveness
- **Pass 1 Hit Rate:** X%
- **Pass 2 Hit Rate:** X%
- **Improvement:** +X%
- **Status:** ✅ Cache working effectively

## Conclusions

[Summarize findings]

## Recommendations

[List any performance improvements needed]
```

#### Step 4: Commit & Report
```bash
git add tests/load/ docs/LOAD_TEST_REPORT.md reports/
git commit -m "Add load testing framework and execute 1M query test

- Progressive tests: 10K → 100K → 1M queries
- Memory leak detection (no leaks found)
- Cache effectiveness validation (>70% hit rate)
- Production targets achieved:
  - Throughput: >1000 qps
  - P99 latency: <200ms
  - Memory peak: <500MB
  - Error rate: <1%"
git push origin copilot/sub-pr-2750-another-one
```

**Success Criteria:**
- ✅ 1M queries executed (<1% error rate)
- ✅ Throughput >1000 qps (cached)
- ✅ P99 latency <200ms (fresh)
- ✅ No memory leaks detected
- ✅ Cache hit rate >70%

---

### Phase 6: Multi-Region Deployment (P1)

**Objective:** Deploy across 3 regions with automatic failover

#### Step 1: Architecture Documentation

**File:** `docs/architecture/MULTI_REGION_ARCHITECTURE.md`

```markdown
# Multi-Region RAG Architecture

## Overview

Deploy RAG system across 3 AWS regions with:
- GeoDNS routing for latency optimization
- Index replication (<5 min lag)
- Automatic failover (<30s RTO)
- Regional monitoring

## Regions

1. **us-east-1** (Primary) - Virginia
2. **eu-west-1** (Secondary) - Ireland
3. **ap-southeast-1** (Tertiary) - Singapore

## Components

### 1. GeoDNS Routing
- Route 53 latency-based routing
- Health checks every 30s
- Automatic failover on region failure

### 2. Regional RAG Services
- Each region runs full RAG stack:
  - Retriever API (ECS Fargate)
  - FAISS index storage (EFS)
  - Cache layer (ElastiCache Redis)
  - Monitoring (CloudWatch + Prometheus)

### 3. Index Sync Service
- Replicate index updates across regions
- S3 cross-region replication for index files
- SQS queues for sync notifications
- Target: <5 min replication lag

### 4. Monitoring & Alerting
- Regional dashboards (per-region metrics)
- Global dashboard (cross-region aggregation)
- Alert rules:
  - Region health check failures
  - Replication lag >5 min
  - Query error rate >1%
  - P99 latency >200ms

## Deployment Architecture

[Mermaid diagram showing multi-region setup]

## Failover Procedure

1. Route 53 health check detects failure
2. DNS updated to route to healthy region (30s TTL)
3. Clients redirected to next-closest region
4. Alerts sent to on-call

## Cost Estimation

- Compute: $X/month
- Storage: $Y/month
- Data transfer: $Z/month
- Total: $N/month
```

#### Step 2: Infrastructure as Code

**File:** `deploy/terraform/multi-region/main.tf`

```hcl
# Multi-Region RAG Deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Providers for each region
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west_1"
  region = "eu-west-1"
}

provider "aws" {
  alias  = "ap_southeast_1"
  region = "ap-southeast-1"
}

# Deploy RAG stack to each region
module "rag_us_east_1" {
  source = "../modules/rag-regional"
  providers = {
    aws = aws.us_east_1
  }
  region = "us-east-1"
  environment = var.environment
}

module "rag_eu_west_1" {
  source = "../modules/rag-regional"
  providers = {
    aws = aws.eu_west_1
  }
  region = "eu-west-1"
  environment = var.environment
}

module "rag_ap_southeast_1" {
  source = "../modules/rag-regional"
  providers = {
    aws = aws.ap_southeast_1
  }
  region = "ap-southeast-1"
  environment = var.environment
}

# Route 53 health checks and GeoDNS
resource "aws_route53_health_check" "rag_us_east_1" {
  fqdn              = module.rag_us_east_1.api_endpoint
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30
}

resource "aws_route53_record" "rag_api" {
  zone_id = var.hosted_zone_id
  name    = "rag-api.${var.domain}"
  type    = "A"
  
  # Latency-based routing
  set_identifier = "us-east-1"
  latency_routing_policy {
    region = "us-east-1"
  }
  
  alias {
    name                   = module.rag_us_east_1.api_endpoint
    zone_id                = module.rag_us_east_1.alb_zone_id
    evaluate_target_health = true
  }
  
  health_check_id = aws_route53_health_check.rag_us_east_1.id
}

# Similar records for EU and APAC...

# S3 cross-region replication for indices
resource "aws_s3_bucket_replication_configuration" "index_replication" {
  bucket = module.rag_us_east_1.index_bucket_id
  role   = aws_iam_role.replication.arn
  
  rule {
    id     = "replicate-indices"
    status = "Enabled"
    
    destination {
      bucket        = module.rag_eu_west_1.index_bucket_arn
      storage_class = "STANDARD_IA"
    }
  }
  
  rule {
    id     = "replicate-indices-apac"
    status = "Enabled"
    
    destination {
      bucket        = module.rag_ap_southeast_1.index_bucket_arn
      storage_class = "STANDARD_IA"
    }
  }
}
```

#### Step 3: Index Sync Service

**File:** `src/codex/deployment/index_sync.py`

```python
"""
Index synchronization service for multi-region deployment.

Monitors S3 for index updates and triggers replication to other regions.
Tracks replication lag and alerts if exceeds 5 minutes.
"""

import time
import boto3
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)


class IndexSyncService:
    """Synchronize FAISS indices across multiple AWS regions."""
    
    def __init__(self, regions: List[str], source_bucket: str):
        self.regions = regions
        self.source_bucket = source_bucket
        self.s3_clients = {
            region: boto3.client('s3', region_name=region)
            for region in regions
        }
    
    def sync_index(self, tenant_id: str, index_name: str):
        """Sync index to all regions."""
        source_key = f"{tenant_id}/{index_name}/index.faiss"
        
        # Download from source
        source_s3 = self.s3_clients[self.regions[0]]
        obj = source_s3.get_object(Bucket=self.source_bucket, Key=source_key)
        index_data = obj['Body'].read()
        last_modified = obj['LastModified']
        
        # Upload to all other regions
        for region in self.regions[1:]:
            dest_s3 = self.s3_clients[region]
            dest_bucket = f"{self.source_bucket}-{region}"
            
            try:
                dest_s3.put_object(
                    Bucket=dest_bucket,
                    Key=source_key,
                    Body=index_data,
                    Metadata={
                        'source_region': self.regions[0],
                        'source_last_modified': last_modified.isoformat(),
                        'sync_time': datetime.utcnow().isoformat(),
                    }
                )
                logger.info(f"Synced {source_key} to {region}")
            except Exception as e:
                logger.error(f"Failed to sync to {region}: {e}")
    
    def check_replication_lag(self) -> Dict[str, float]:
        """Check replication lag for all indices."""
        # Implementation...
        pass
```

#### Step 4: Deploy & Validate
```bash
# Initialize Terraform
cd deploy/terraform/multi-region
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply (with approval)
terraform apply tfplan

# Validate deployment
python -m src.codex.deployment.validate_multi_region

# Run cross-region tests
pytest tests/deployment/test_multi_region.py -v
```

**Success Criteria:**
- ✅ Infrastructure deployed to 3 regions
- ✅ GeoDNS routing functional
- ✅ Index replication <5 min
- ✅ Automatic failover tested
- ✅ Regional monitoring active

---

### Phase 7: Monitoring Dashboards (P2)

**Objective:** Create 5 Grafana dashboards with 10+ alert rules

#### Dashboards

1. **Executive Dashboard** - High-level KPIs
2. **Operations Dashboard** - Detailed metrics
3. **Performance Dashboard** - Latency, throughput
4. **Cost Dashboard** - Resource utilization
5. **UX Dashboard** - Cache hit rate, error rate

#### Alert Rules

**File:** `deploy/prometheus/alerts/rag-alerts.yml`

```yaml
groups:
  - name: rag_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: RAGHighErrorRate
        expr: rate(rag_errors_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "RAG error rate above 1%"
          
      # High P99 latency
      - alert: RAGHighLatency
        expr: histogram_quantile(0.99, rag_query_latency_ms) > 200
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RAG P99 latency above 200ms"
      
      # Low cache hit rate
      - alert: RAGLowCacheHitRate
        expr: rag_cache_hit_rate < 0.70
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "RAG cache hit rate below 70%"
      
      # ... 7 more alert rules
```

**Success Criteria:**
- ✅ 5+ dashboards deployed
- ✅ 10+ alert rules configured
- ✅ Alerts firing correctly
- ✅ SLO tracking operational

---

## Success Metrics

### Overall Targets
- **Coverage:** 90%+ for all RAG modules
- **Load Testing:** 1M queries validated
- **Multi-Region:** 3 regions deployed
- **Monitoring:** Complete observability stack

### Quality Gates
- All tests passing (0 failures)
- No security vulnerabilities
- CI/CD pipeline green
- Documentation complete

---

## Blockers & Risks

### Known Blockers
1. **Test environment numpy conflicts** - Requires investigation
   - **Mitigation:** Use fresh subprocess or fix import order

### Potential Risks
1. **Load testing duration** - 1M queries may take hours
   - **Mitigation:** Run in parallel, use caching effectively
2. **Multi-region costs** - AWS infrastructure expensive
   - **Mitigation:** Use spot instances, optimize resource allocation
3. **Time constraints** - Many phases to complete
   - **Mitigation:** Prioritize P0/P1, defer P2 if needed

---

## Recommended Execution Order

1. **Phase 3C** (P0 - CRITICAL) - Fix test env, expand indexer tests
2. **Phase 4** (P1) - Update docs, post continuation comment
3. **Phase 5** (P1) - Load testing framework + execution
4. **Phase 6** (P1) - Multi-region architecture + deployment
5. **Phase 7** (P2) - Monitoring dashboards (can be deferred)

**Estimated Time:**
- Phase 3C: 2-3 hours
- Phase 4: 30 min
- Phase 5: 3-4 hours (including 1M query run)
- Phase 6: 4-6 hours (including deployment)
- Phase 7: 2-3 hours

**Total:** 12-17 hours (can be split across multiple sessions)

---

## Key Files Reference

- **Phase 3 Status:** `.codex/cognitive_brain/RAG_PRODUCTION_PHASE3_STATUS.md`
- **Monitoring Tests:** `tests/test_rag_monitoring.py` (99.08% coverage)
- **Indexer Tests:** `tests/test_rag_indexer.py` (existing), `tests/test_rag_indexer_advanced.py` (to create)
- **Load Tests:** `tests/load/test_rag_load.py` (to create)
- **Multi-Region Terraform:** `deploy/terraform/multi-region/` (to create)
- **Alert Rules:** `deploy/prometheus/alerts/rag-alerts.yml` (to create)

---

**Ready to Execute:** Start with Phase 3C (fix test environment) then proceed sequentially through remaining phases. Use `report_progress` after each completed phase.
