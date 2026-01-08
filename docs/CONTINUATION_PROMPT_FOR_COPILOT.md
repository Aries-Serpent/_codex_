# Continuation Prompt for GitHub Copilot Agent
# Post this as a comment on PR #2750

@copilot Continue RAG Production Readiness - Execute Phases 3-7 with Comprehensive Coverage and Iterations 5-7

## Context & Current Status

**Branch**: `copilot/sub-pr-2750-again`  
**PR**: #2750  
**Last Commit**: `a637594` - "Fix test failures and address all PR review feedback"  
**Review Document**: `docs/PHASE3_PR2750_COMPREHENSIVE_REVIEW.md`

### Completed (Phases 1-2) ✅
- Fixed all 6 test failures (OpenAI patches, error messages, MultiIndexRetriever filtering)
- Addressed all 7 PR review comments (security, logging, error messages, pytest config)
- Comprehensive self-review completed
- Cognitive brain updated with 18 patterns
- Production-ready custom agents documented

### Current Blockers 🔴
1. **Disk Space**: 96% usage (69G/72G) - prevents installing test dependencies
2. **Coverage**: 46.02% overall (need 90%+)
   - `monitoring.py`: 16.67% coverage
   - `indexer.py`: 52.42% coverage

---

## 🎯 Phase 3: Coverage Improvement (Priority: P0)
**Estimated**: 4-6 hours | **Status**: Not Started

### Step 1: Clean Disk Space
```bash
# Free up space before installing dependencies
sudo apt-get clean
sudo apt-get autoremove -y
pip cache purge
docker system prune -af --volumes
rm -rf ~/.cache/pip /tmp/* /var/tmp/*
df -h  # Verify >10GB available
```

### Step 2: Create Monitoring Tests
**File**: `tests/test_rag_monitoring.py`  
**Target**: 90%+ coverage of `src/codex/rag/monitoring.py`

```python
"""Comprehensive tests for RAG monitoring module."""
import pytest
from src.codex.rag.monitoring import RAGMetrics, MetricsConfig, MetricDataPoint

class TestMetricsConfig:
    """Test MetricsConfig validation."""
    
    def test_valid_config(self):
        """Test valid configuration."""
        config = MetricsConfig(
            query_latency_window=100,
            embedding_throughput_window=200,
            index_build_time_window=50
        )
        assert config.query_latency_window == 100
    
    def test_window_size_validation(self):
        """Test minimum window size validation."""
        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(query_latency_window=5)
        
        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(embedding_throughput_window=8)
        
        with pytest.raises(ValueError, match="statistically meaningful"):
            MetricsConfig(index_build_time_window=9)

class TestRAGMetrics:
    """Test RAGMetrics tracking."""
    
    def test_track_query_latency(self):
        """Test query latency tracking."""
        metrics = RAGMetrics()
        
        # Track 100 queries
        for i in range(100):
            metrics.track_query_latency(float(i), "tenant1", "index1")
        
        stats = metrics.get_query_stats("tenant1", "index1")
        assert stats['count'] == 100
        assert stats['p50'] > 0
        assert stats['p95'] > stats['p50']
        assert stats['p99'] > stats['p95']
    
    def test_track_embedding_throughput(self):
        """Test embedding throughput tracking."""
        metrics = RAGMetrics()
        
        metrics.track_embedding_throughput(100, "tenant1")
        metrics.track_embedding_throughput(200, "tenant1")
        
        stats = metrics.get_embedding_stats("tenant1")
        assert stats['total_embeddings'] == 300
        assert stats['avg_throughput'] > 0
    
    def test_track_index_build_time(self):
        """Test index build time tracking."""
        metrics = RAGMetrics()
        
        metrics.track_index_build_time(10.5, "tenant1", "index1")
        metrics.track_index_build_time(12.3, "tenant1", "index1")
        
        stats = metrics.get_index_build_stats("tenant1", "index1")
        assert stats['count'] == 2
        assert stats['avg_time'] > 10
    
    def test_cache_stats(self):
        """Test cache statistics tracking."""
        metrics = RAGMetrics()
        
        metrics.record_cache_hit("tenant1")
        metrics.record_cache_hit("tenant1")
        metrics.record_cache_miss("tenant1")
        
        stats = metrics.get_cache_stats("tenant1")
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == pytest.approx(0.666, rel=0.01)
    
    def test_percentile_calculation(self):
        """Test percentile calculation accuracy."""
        metrics = RAGMetrics()
        
        # Track known distribution
        for val in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            metrics.track_query_latency(float(val), "tenant1", "index1")
        
        stats = metrics.get_query_stats("tenant1", "index1")
        assert stats['p50'] == pytest.approx(50, abs=5)
        assert stats['p95'] == pytest.approx(95, abs=5)
    
    def test_window_trimming(self):
        """Test metrics window trimming for memory efficiency."""
        config = MetricsConfig(query_latency_window=50)
        metrics = RAGMetrics(config)
        
        # Track more than window size
        for i in range(100):
            metrics.track_query_latency(float(i), "tenant1", "index1")
        
        # Window should be trimmed to 50 most recent
        assert len(metrics._get_latency_window("tenant1", "index1")) <= 50
    
    def test_concurrent_access(self):
        """Test thread-safe concurrent access."""
        import threading
        metrics = RAGMetrics()
        
        def track_metrics():
            for i in range(100):
                metrics.track_query_latency(float(i), "tenant1", "index1")
        
        threads = [threading.Thread(target=track_metrics) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        stats = metrics.get_query_stats("tenant1", "index1")
        assert stats['count'] == 500

# Add 15+ more tests covering:
# - Multi-tenant metrics isolation
# - Alert threshold checking
# - Metrics export (Prometheus format)
# - Time-based aggregations
# - Edge cases (empty data, single data point, outliers)
```

### Step 3: Expand Indexer Tests
**File**: `tests/test_rag_indexer.py` (expand existing)  
**Target**: 90%+ coverage of `src/codex/rag/indexer.py` lines 447-738

```python
"""Additional tests for advanced indexer features."""

def test_incremental_index_update(tmp_path):
    """Test adding documents to existing index."""
    from src.codex.rag.indexer import build_index_from_files, add_to_index, load_index
    
    # Create test files
    file1 = tmp_path / "doc1.txt"
    file1.write_text("Initial document content")
    
    file2 = tmp_path / "doc2.txt"
    file2.write_text("Additional document content")
    
    # Build initial index
    index_path = build_index_from_files([file1], "test", "tenant1", str(tmp_path))
    initial_index = load_index(str(tmp_path), "test", "tenant1")
    initial_count = initial_index.ntotal
    
    # Add new document
    add_to_index(index_path, [file2])
    updated_index = load_index(str(tmp_path), "test", "tenant1")
    
    assert updated_index.ntotal > initial_count

def test_index_merging(tmp_path):
    """Test merging multiple indices."""
    from src.codex.rag.indexer import build_index_from_files, merge_indices
    
    # Create two indices
    file1 = tmp_path / "doc1.txt"
    file1.write_text("Document 1 content")
    
    file2 = tmp_path / "doc2.txt"
    file2.write_text("Document 2 content")
    
    index1_path = build_index_from_files([file1], "index1", "tenant1", str(tmp_path))
    index2_path = build_index_from_files([file2], "index2", "tenant1", str(tmp_path))
    
    # Merge them
    merged_path = merge_indices([index1_path, index2_path], "merged", "tenant1", str(tmp_path))
    
    merged_index = load_index(str(tmp_path), "merged", "tenant1")
    index1 = load_index(str(tmp_path), "index1", "tenant1")
    index2 = load_index(str(tmp_path), "index2", "tenant1")
    
    assert merged_index.ntotal == index1.ntotal + index2.ntotal

def test_metadata_persistence(tmp_path):
    """Test metadata is persisted with index."""
    from src.codex.rag.indexer import build_index_from_files, load_index_metadata
    
    file1 = tmp_path / "doc1.txt"
    file1.write_text("Content with metadata")
    
    metadata = {
        "source": "test_suite",
        "version": "1.0",
        "timestamp": "2026-01-08T20:00:00Z"
    }
    
    index_path = build_index_from_files(
        [file1], "test", "tenant1", str(tmp_path), metadata=metadata
    )
    
    loaded_metadata = load_index_metadata(str(tmp_path), "test", "tenant1")
    assert loaded_metadata["source"] == "test_suite"
    assert loaded_metadata["version"] == "1.0"

def test_concurrent_index_writes(tmp_path):
    """Test concurrent writes to different indices."""
    import threading
    from src.codex.rag.indexer import build_index_from_files
    
    def build_index(index_num):
        file = tmp_path / f"doc{index_num}.txt"
        file.write_text(f"Content {index_num}")
        build_index_from_files([file], f"index{index_num}", f"tenant{index_num}", str(tmp_path))
    
    threads = [threading.Thread(target=build_index, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # All 5 indices should exist
    for i in range(5):
        assert (tmp_path / f"tenant{i}" / f"index{i}" / "index.faiss").exists()

def test_large_file_handling(tmp_path):
    """Test handling files >10MB."""
    from src.codex.rag.indexer import build_index_from_files
    
    # Create 15MB file
    large_file = tmp_path / "large.txt"
    large_file.write_text("x" * (15 * 1024 * 1024))
    
    index_path = build_index_from_files([large_file], "large", "tenant1", str(tmp_path))
    assert (tmp_path / "tenant1" / "large" / "index.faiss").exists()

def test_chunk_boundary_edge_cases(tmp_path):
    """Test edge cases in chunk boundaries."""
    from src.codex.rag.indexer import chunk_text
    
    # Text exactly at chunk size
    text = "a" * 500
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) == 1
    
    # Text just over chunk size
    text = "a" * 501
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) == 2
    
    # Empty text
    chunks = chunk_text("", chunk_size=500, overlap=100)
    assert len(chunks) == 0

# Add 10+ more tests for lines 447-738
```

### Step 4: Run Tests & Verify Coverage
```bash
# Install dependencies (after disk cleanup)
pip install -r requirements-test.txt --no-cache-dir
pip install numpy sentence-transformers faiss-cpu openai --no-cache-dir

# Run tests with coverage
pytest tests/ \
  --cov=src/codex/rag \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=90 \
  -v \
  --tb=short

# Generate detailed coverage report
coverage html -d reports/coverage
coverage report --show-missing > reports/coverage-summary.txt
```

### Step 5: Commit & Report
```bash
git add tests/test_rag_monitoring.py tests/test_rag_indexer.py
git commit -m "Add comprehensive tests for monitoring and indexer modules

- Add 25+ tests for monitoring.py (target 90%+ coverage)
- Add 15+ tests for advanced indexer features (lines 447-738)
- Test concurrent access, edge cases, large files
- Verify metrics tracking, percentile calculations, cache stats
- Test incremental updates, index merging, metadata persistence

Coverage improvement: 46.02% → 90%+"

git push origin copilot/sub-pr-2750-again
```

**Success Criteria**:
- ✅ All tests pass (0 failures)
- ✅ Coverage ≥90% overall
- ✅ `monitoring.py` ≥90% coverage
- ✅ `indexer.py` ≥90% coverage
- ✅ CI build passes

---

## 🎯 Phase 4: Respond to PR Comments (Priority: P1)
**Estimated**: 1-2 hours

Use `reply_to_comment` tool to respond to all actionable comments on PR #2750. Reference commit `a637594` where fixes were applied.

---

## 🎯 Phase 5: Iteration 5 - Load Testing (Priority: P1)
**Estimated**: 6-8 hours | **Reference**: `prompts/ITERATION_5_LOAD_TESTING.md`

**Objective**: Execute 1M+ queries to validate production-scale performance

### Tasks:
1. Create load test framework (`tests/load/test_rag_load.py`)
2. Execute progressive tests (10K → 100K → 1M queries)
3. Run memory leak detection
4. Validate cache effectiveness (>70% hit rate)
5. Generate comprehensive report

**Success Criteria**:
- ✅ 1M queries executed (<1% error rate)
- ✅ Throughput >1000 qps (cached)
- ✅ P99 latency <10ms (cached), <200ms (fresh)
- ✅ No memory leaks detected
- ✅ Peak memory <500MB

---

## 🎯 Phase 6: Iteration 6 - Multi-Region Deployment (Priority: P1)
**Estimated**: 8-12 hours | **Reference**: `prompts/ITERATION_6_MULTI_REGION.md`

**Objective**: Deploy across 3 regions with automatic failover

### Tasks:
1. Create architecture documentation (`docs/architecture/MULTI_REGION_ARCHITECTURE.md`)
2. Write Infrastructure as Code (`deploy/terraform/multi-region/main.tf`)
3. Implement index sync service (`src/codex/deployment/index_sync.py`)
4. Deploy and validate
5. Create monitoring dashboards

**Success Criteria**:
- ✅ Infrastructure in 3+ regions
- ✅ GeoDNS routing functional
- ✅ Index replication <5 min
- ✅ Automatic failover tested
- ✅ P99 latency <100ms regional

---

## 🎯 Phase 7: Iteration 7 - Monitoring Dashboards (Priority: P2)
**Estimated**: 6-8 hours | **Reference**: `prompts/ITERATION_7_MONITORING_DASHBOARDS.md`

**Objective**: Create 5 Grafana dashboards with 10+ alert rules

### Tasks:
1. Create executive dashboard (high-level KPIs)
2. Create operations dashboard (detailed metrics)
3. Create performance/cost/UX dashboards
4. Configure alert rules (`deploy/prometheus/alerts/rag-alerts.yml`)
5. Deploy and validate

**Success Criteria**:
- ✅ 5+ dashboards deployed
- ✅ 10+ alert rules configured
- ✅ SLO tracking operational
- ✅ Alerts firing correctly

---

## 📊 Expected Final Deliverables

### Code:
- 50+ new tests (monitoring, indexer)
- Load testing framework
- Multi-region infrastructure (Terraform)
- Index sync service
- 5 Grafana dashboards
- 10+ alert rules

### Documentation:
- Phase 3 review (completed)
- Iteration 5 results (load testing)
- Iteration 6 architecture (multi-region)
- Iteration 7 playbooks (monitoring)
- Updated cognitive brain

### Metrics:
- **Coverage**: 90%+ (from 46.02%)
- **Load Testing**: 1M queries validated
- **Multi-Region**: 3 regions deployed
- **Monitoring**: Complete observability stack

---

## 🚀 Execution Instructions

**Execute phases in order: 3 → 4 → 5 → 6 → 7**

Use `report_progress` after each phase completion. Update cognitive brain with learnings. Create production-ready deliverables. Document any blockers with solutions.

**Autonomous Mode**: Execute all tasks without waiting for approval unless encountering critical blockers (e.g., infrastructure provisioning requiring credentials).

**Context Files**:
- Review status: `docs/PHASE3_PR2750_COMPREHENSIVE_REVIEW.md`
- Iteration 5 prompt: `prompts/ITERATION_5_LOAD_TESTING.md`
- Iteration 6 prompt: `prompts/ITERATION_6_MULTI_REGION.md`
- Iteration 7 prompt: `prompts/ITERATION_7_MONITORING_DASHBOARDS.md`

---

**Posted**: 2026-01-08 20:30 UTC  
**Estimated Total**: 24-36 hours  
**Expected Completion**: Multiple sessions
