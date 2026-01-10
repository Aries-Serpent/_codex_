# Path to 100% Test Coverage - Rust-Python Hybrid Swarm

## Current Status: ~70% Coverage

**Completed**:
- ✅ Core module implementation (6/6 modules)
- ✅ Python integration tests (29 passing)
- ✅ Rust unit tests (49 created, not yet run)
- ✅ Build system validation
- ✅ Basic performance validation

**Gaps to Address**:
- ❌ Rust unit tests not executed
- ❌ Memory profiling
- ❌ Full integration testing
- ❌ Failure injection / chaos testing
- ❌ Performance benchmarking suite
- ❌ Production monitoring hooks
- ❌ Comprehensive documentation

---

## Phase 1: Execute Rust Unit Tests (Target: 75%)

### Objective
Run all Rust unit tests to validate core functionality at the Rust level.

### Tasks

**1.1 Run Basic Tests**
```bash
cd /home/runner/work/_codex_/_codex_
cargo test --lib --release
```

**Expected Output**:
- tests_rust/test_state.rs: 11 tests
- tests_rust/test_runtime.rs: 4 tests  
- tests_rust/test_queue.rs: 8 tests
- tests_rust/test_agent_manager.rs: 8 tests
- tests_rust/test_compression.rs: 10 tests
- tests_rust/test_serialization.rs: 8 tests

**Total**: 49 tests

**1.2 Address Test Failures**

If tests fail:
1. Analyze error messages
2. Fix implementation issues
3. Re-run tests
4. Iterate until all pass

**1.3 Generate Coverage Report**

```bash
# Install tarpaulin for coverage
cargo install cargo-tarpaulin

# Generate coverage
cargo tarpaulin --out Html --output-dir coverage
```

**Success Criteria**:
- ✅ 49/49 Rust tests passing
- ✅ Coverage report generated
- ✅ Core module coverage > 70%

**Time Estimate**: 2-4 hours

---

## Phase 2: Performance Benchmarking (Target: 78%)

### Objective
Create comprehensive benchmark suite to validate and track performance.

### Tasks

**2.1 Create Benchmark Suite**

Create `benches/swarm_benchmarks.rs`:

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use codex_engine::*;
use std::sync::Arc;

fn bench_swarm_state(c: &mut Criterion) {
    let mut group = c.benchmark_group("swarm_state");
    
    // Registration throughput
    group.bench_function("register_1000_agents", |b| {
        b.iter(|| {
            let state = SwarmState::new();
            for i in 0..1000 {
                state.register_agent(format!("agent_{}", i)).unwrap();
            }
        })
    });
    
    // Concurrent registration
    group.bench_function("concurrent_register_100", |b| {
        b.iter(|| {
            use std::thread;
            let state = Arc::new(SwarmState::new());
            let handles: Vec<_> = (0..10).map(|tid| {
                let s = Arc::clone(&state);
                thread::spawn(move || {
                    for i in 0..10 {
                        s.register_agent(format!("agent_{}_{}", tid, i)).unwrap();
                    }
                })
            }).collect();
            for h in handles { h.join().unwrap(); }
        })
    });
    
    group.finish();
}

fn bench_task_queue(c: &mut Criterion) {
    let mut group = c.benchmark_group("task_queue");
    
    // Submission throughput
    for size in [100, 1000, 10000].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, &size| {
            b.iter(|| {
                let queue = TaskQueue::new();
                for i in 0..size {
                    let task = Task::new(
                        format!("task_{}", i),
                        "test".to_string(),
                        "{}".to_string()
                    );
                    queue.submit(black_box(task)).unwrap();
                }
            })
        });
    }
    
    group.finish();
}

fn bench_compression(c: &mut Criterion) {
    let mut group = c.benchmark_group("compression");
    
    let data_1kb = vec![0u8; 1024];
    let data_1mb = vec![0u8; 1024 * 1024];
    
    // LZ4
    group.bench_function("lz4_1kb", |b| {
        let pipeline = CompressionPipeline::new("lz4".to_string(), None).unwrap();
        b.iter(|| pipeline.compress(black_box(&data_1kb)))
    });
    
    group.bench_function("lz4_1mb", |b| {
        let pipeline = CompressionPipeline::new("lz4".to_string(), None).unwrap();
        b.iter(|| pipeline.compress(black_box(&data_1mb)))
    });
    
    // Zstd
    group.bench_function("zstd_1mb", |b| {
        let pipeline = CompressionPipeline::new("zstd".to_string(), Some(3)).unwrap();
        b.iter(|| pipeline.compress(black_box(&data_1mb)))
    });
    
    group.finish();
}

fn bench_serialization(c: &mut Criterion) {
    let mut group = c.benchmark_group("serialization");
    
    let mut state = AgentState::new("agent_1".to_string(), vec!["item".to_string(); 1000]);
    for i in 0..10 {
        state.set_metric(format!("metric_{}", i), i as f64);
    }
    
    group.bench_function("serialize_state", |b| {
        b.iter(|| serialize_state(black_box(&state)))
    });
    
    let serialized = serialize_state(&state).unwrap();
    group.bench_function("deserialize_state", |b| {
        b.iter(|| deserialize_state(black_box(&serialized)))
    });
    
    group.finish();
}

criterion_group!(benches, bench_swarm_state, bench_task_queue, bench_compression, bench_serialization);
criterion_main!(benches);
```

**2.2 Add Benchmark Dependencies**

Update `Cargo.toml`:
```toml
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "swarm_benchmarks"
harness = false
```

**2.3 Run Benchmarks**

```bash
cargo bench
```

**2.4 Analyze Results**

- Compare against targets
- Identify performance regressions
- Generate HTML reports

**Success Criteria**:
- ✅ Benchmark suite runs successfully
- ✅ All performance targets met
- ✅ Baseline established for future comparison

**Time Estimate**: 4-6 hours

---

## Phase 3: Memory Profiling (Target: 82%)

### Objective
Profile memory usage and detect leaks.

### Tasks

**3.1 Install Profiling Tools**

```bash
# Valgrind
sudo apt-get install valgrind

# Heaptrack  
sudo apt-get install heaptrack

# Massif visualizer
sudo apt-get install massif-visualizer
```

**3.2 Create Memory Test Script**

Create `scripts/memory_profile.py`:

```python
import codex_engine
import time
import psutil
import os

def test_memory_usage():
    process = psutil.Process(os.getpid())
    
    # Baseline
    baseline = process.memory_info().rss / 1024 / 1024
    print(f"Baseline memory: {baseline:.2f} MB")
    
    # Create 1000 agents
    state = codex_engine.SwarmState()
    for i in range(1000):
        state.register_agent(f"agent_{i}")
    
    after_agents = process.memory_info().rss / 1024 / 1024
    print(f"After 1000 agents: {after_agents:.2f} MB")
    print(f"Per-agent memory: {(after_agents - baseline) / 1000:.3f} MB")
    
    # Submit 10k tasks
    queue = codex_engine.TaskQueue()
    for i in range(10000):
        task = codex_engine.Task(str(i), "test", "{}")
        queue.submit(task)
    
    after_tasks = process.memory_info().rss / 1024 / 1024
    print(f"After 10k tasks: {after_tasks:.2f} MB")
    
    # Cleanup test
    for i in range(1000):
        state.unregister_agent(f"agent_{i}")
    
    time.sleep(1)  # Allow cleanup
    
    after_cleanup = process.memory_info().rss / 1024 / 1024
    print(f"After cleanup: {after_cleanup:.2f} MB")
    
    # Validate
    assert (after_cleanup - baseline) < 50, "Memory leak detected"
    print("✅ No memory leaks detected")

if __name__ == "__main__":
    test_memory_usage()
```

**3.3 Run Memory Profiling**

```bash
# Valgrind massif
valgrind --tool=massif --massif-out-file=massif.out python3 scripts/memory_profile.py

# Analyze
ms_print massif.out

# Heaptrack
heaptrack python3 scripts/memory_profile.py
heaptrack_gui heaptrack.python3.*.gz
```

**3.4 Fix Memory Issues**

- Identify leaks in Rust code
- Add drop implementations if needed
- Re-test until clean

**Success Criteria**:
- ✅ Memory usage < 50 MB for 1000 agents
- ✅ No memory leaks detected
- ✅ Cleanup releases resources properly

**Time Estimate**: 4-6 hours

---

## Phase 4: Full Integration Testing (Target: 88%)

### Objective
Test complete system with 500 agents processing 10,000 tasks.

### Tasks

**4.1 Create Full Integration Test**

Create `tests/integration/test_full_swarm.py`:

```python
import pytest
import asyncio
import time
from codex_engine import (
    SwarmState,
    Orchestrator,
    TaskQueue,
    AgentManager,
    CompressionPipeline,
    AgentState,
    serialize_state,
    deserialize_state
)

@pytest.mark.integration
@pytest.mark.slow
async def test_full_swarm_integration():
    """Full integration test: 500 agents, 10k tasks"""
    
    # Setup
    state = SwarmState()
    queue = TaskQueue()
    manager = AgentManager(max_agents=500)
    orch = Orchestrator(state)
    compression = CompressionPipeline("lz4")
    
    print("\n=== Full Swarm Integration Test ===")
    
    # Start orchestrator
    orch.start()
    assert orch.is_running()
    print("✅ Orchestrator started")
    
    # Spawn 500 agents
    start = time.time()
    for i in range(500):
        agent_config = f'{{"id": "agent_{i}", "type": "worker"}}'
        try:
            manager.spawn_agent(f"agent_{i}", agent_config)
            state.register_agent(f"agent_{i}")
        except RuntimeError as e:
            print(f"Note: {e}")
    elapsed = time.time() - start
    print(f"✅ Spawned agents in {elapsed:.2f}s")
    assert elapsed < 10.0, "Agent spawning took too long"
    
    await asyncio.sleep(0.5)
    
    # Submit 10,000 tasks
    start = time.time()
    for i in range(10000):
        task_data = {
            "task_id": i,
            "operation": "analyze",
            "priority": i % 10
        }
        
        # Serialize task data
        agent_state = AgentState(f"task_{i}", [f"data_{i}"])
        serialized = serialize_state(agent_state)
        
        # Compress
        compressed = compression.compress(serialized)
        
        # Submit
        task = codex_engine.Task(
            str(i),
            "analyze",
            compressed.decode('latin1')  # Store as string
        )
        queue.submit(task)
    
    elapsed = time.time() - start
    throughput = 10000 / elapsed
    print(f"✅ Submitted 10k tasks in {elapsed:.2f}s ({throughput:.0f} tasks/s)")
    assert throughput > 5000, f"Throughput too low: {throughput:.0f} tasks/s"
    
    # Process tasks
    await asyncio.sleep(2.0)
    
    # Validate state
    agent_count = state.get_agent_count()
    print(f"✅ Agent count: {agent_count}")
    assert agent_count > 0
    
    # Cleanup
    orch.stop()
    print("✅ Orchestrator stopped")
    
    print("\n=== Integration Test Complete ===")

@pytest.mark.integration
def test_compression_pipeline_integration():
    """Test compression with serialization"""
    
    pipeline = CompressionPipeline("zstd", 3)
    
    # Create large state
    state = AgentState("agent_1", ["memory_item"] * 10000)
    for i in range(100):
        state.set_metric(f"metric_{i}", float(i))
    
    # Serialize
    serialized = serialize_state(state)
    original_size = len(serialized)
    
    # Compress
    compressed = pipeline.compress(serialized)
    compressed_size = len(compressed)
    
    # Decompress
    decompressed = pipeline.decompress(compressed)
    
    # Deserialize
    recovered = deserialize_state(decompressed)
    
    # Validate
    assert recovered.id == state.id
    assert len(recovered.memory) == len(state.memory)
    
    ratio = original_size / compressed_size
    print(f"Compression ratio: {ratio:.2f}x")
    assert ratio > 2.0, "Compression not effective"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

**4.2 Run Integration Tests**

```bash
pytest tests/integration/test_full_swarm.py -v -s --tb=short
```

**4.3 Monitor Performance**

- CPU utilization (should reach 90%+)
- Memory usage (< 25 GB for 500 agents)
- Task processing latency
- No deadlocks or crashes

**Success Criteria**:
- ✅ 500 agents spawn successfully
- ✅ 10,000 tasks submitted and processed
- ✅ No crashes or deadlocks
- ✅ Performance targets met

**Time Estimate**: 6-8 hours

---

## Phase 5: Failure Injection & Chaos Testing (Target: 92%)

### Objective
Test system resilience under failure conditions.

### Tasks

**5.1 Create Chaos Test Suite**

Create `tests/chaos/test_resilience.py`:

```python
import pytest
import time
import random
from codex_engine import SwarmState, TaskQueue, AgentManager

def test_agent_spawn_failure_recovery():
    """Test recovery from agent spawn failures"""
    manager = AgentManager(max_agents=10)
    
    successful = 0
    failed = 0
    
    for i in range(20):
        try:
            manager.spawn_agent(f"agent_{i}", "{}")
            successful += 1
        except RuntimeError:
            failed += 1
    
    # Should hit max limit
    assert manager.get_active_count() <= 10
    assert failed > 0
    
    print(f"Spawned: {successful}, Failed: {failed}")

def test_task_queue_stress():
    """Stress test task queue with rapid submit/receive"""
    queue = TaskQueue()
    
    # Submit rapidly
    for i in range(100000):
        task = codex_engine.Task(str(i), "test", "{}")
        queue.submit(task)
    
    # Receive all
    count = 0
    while True:
        task = queue.receive()
        if task is None:
            break
        count += 1
    
    assert count == 100000

def test_concurrent_state_modifications():
    """Test state under concurrent stress"""
    import concurrent.futures
    import threading
    
    state = SwarmState()
    errors = []
    
    def worker(thread_id):
        try:
            for i in range(100):
                agent_id = f"agent_{thread_id}_{i}"
                state.register_agent(agent_id)
                state.set_agent_status(agent_id, "working", "test")
                state.set_agent_status(agent_id, "complete")
                state.unregister_agent(agent_id)
        except Exception as e:
            errors.append(e)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(worker, i) for i in range(50)]
        concurrent.futures.wait(futures)
    
    assert len(errors) == 0, f"Errors occurred: {errors}"
    print("✅ No errors under concurrent stress")

def test_memory_leak_detection():
    """Detect memory leaks through repeated operations"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    baseline = process.memory_info().rss / 1024 / 1024
    
    for iteration in range(10):
        state = SwarmState()
        for i in range(100):
            state.register_agent(f"agent_{i}")
        for i in range(100):
            state.unregister_agent(f"agent_{i}")
        
        del state
    
    final = process.memory_info().rss / 1024 / 1024
    growth = final - baseline
    
    print(f"Memory growth: {growth:.2f} MB")
    assert growth < 10, f"Memory leak detected: {growth:.2f} MB growth"
```

**5.2 Run Chaos Tests**

```bash
pytest tests/chaos/ -v -s
```

**Success Criteria**:
- ✅ System recovers from agent spawn failures
- ✅ Task queue handles 100k tasks
- ✅ No race conditions under concurrent stress
- ✅ No memory leaks detected

**Time Estimate**: 4-6 hours

---

## Phase 6: Documentation (Target: 96%)

### Objective
Comprehensive API documentation and architecture diagrams.

### Tasks

**6.1 API Documentation**

Create `docs/rust_api.md`:
- Module overview
- Class/function signatures
- Usage examples
- Performance characteristics
- Thread safety guarantees

**6.2 Architecture Documentation**

Create `docs/architecture.md`:
- System overview diagram
- Data flow diagrams
- Concurrency model
- Memory layout
- Integration patterns

**6.3 Performance Guide**

Create `docs/performance.md`:
- Benchmarking results
- Tuning parameters
- Scalability limits
- Best practices

**6.4 Update Type Stubs**

Update `codex_engine.pyi` with new modules:
- AgentManager
- CompressionPipeline
- AgentState
- Serialization functions

**Success Criteria**:
- ✅ All public APIs documented
- ✅ Architecture diagrams complete
- ✅ Performance guide published
- ✅ Type stubs current

**Time Estimate**: 6-8 hours

---

## Phase 7: CI/CD Integration (Target: 98%)

### Objective
Automate testing and deployment.

### Tasks

**7.1 GitHub Actions Workflow**

Create `.github/workflows/rust-tests.yml`:

```yaml
name: Rust Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
    
    - name: Cache cargo
      uses: actions/cache@v3
      with:
        path: ~/.cargo
        key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    
    - name: Run tests
      run: cargo test --release
    
    - name: Run benchmarks
      run: cargo bench
    
    - name: Build wheel
      run: |
        pip install maturin
        maturin build --release
    
    - name: Python integration tests
      run: |
        pip install target/wheels/*.whl
        pytest tests/rust_integration/ -v
```

**7.2 Coverage Reporting**

Add coverage reporting to CI:
- Codecov integration
- Coverage badge in README

**7.3 Performance Regression Detection**

- Store benchmark baselines
- Alert on > 10% regression

**Success Criteria**:
- ✅ CI runs all tests automatically
- ✅ Coverage tracked over time
- ✅ Performance regressions caught

**Time Estimate**: 4-6 hours

---

## Phase 8: Production Monitoring (Target: 100%)

### Objective
Add production observability hooks.

### Tasks

**8.1 Metrics Export**

Add Prometheus metrics:
- Agent count
- Task throughput
- Queue depth
- Latency percentiles

**8.2 Tracing Integration**

Integrate with OpenTelemetry:
- Task execution traces
- Agent lifecycle traces
- Cross-component tracing

**8.3 Health Checks**

Add health check endpoints:
- `/health/live` - liveness probe
- `/health/ready` - readiness probe
- `/metrics` - Prometheus metrics

**8.4 Alerting Rules**

Define alerting rules:
- High task queue depth
- Agent spawn failures
- Memory leaks
- Performance degradation

**Success Criteria**:
- ✅ Metrics exportable to Prometheus
- ✅ Traces integrated with OpenTelemetry
- ✅ Health checks functional
- ✅ Alerting rules defined

**Time Estimate**: 6-8 hours

---

## Coverage Roadmap Summary

| Phase | Target Coverage | Est. Time | Key Deliverables |
|-------|-----------------|-----------|------------------|
| 1. Rust Unit Tests | 75% | 2-4h | 49 tests passing, coverage report |
| 2. Benchmarking | 78% | 4-6h | Criterion suite, baseline metrics |
| 3. Memory Profiling | 82% | 4-6h | Valgrind/heaptrack reports, leak-free |
| 4. Integration Tests | 88% | 6-8h | 500 agents × 10k tasks validated |
| 5. Chaos Testing | 92% | 4-6h | Failure recovery validated |
| 6. Documentation | 96% | 6-8h | API docs, architecture, performance guide |
| 7. CI/CD | 98% | 4-6h | Automated testing, coverage tracking |
| 8. Monitoring | 100% | 6-8h | Prometheus, tracing, health checks |

**Total Estimated Time**: 36-54 hours (4-7 working days)

---

## Continuation Prompt for Next Session

```markdown
@copilot Continue Rust-Python Hybrid Swarm Implementation - Path to 100% Coverage

**Context**: Milestones 1.2-3.2 complete (commit 10f398b). Python tests passing (29/29). Rust tests created but not executed.

**Current Status**: ~70% coverage

**Next Phase Tasks**:

1. **Execute Rust Unit Tests**
   - Run: `cargo test --lib --release`
   - Validate all 49 tests pass
   - Generate coverage report with cargo-tarpaulin

2. **Performance Benchmarking**
   - Create benchmark suite in `benches/swarm_benchmarks.rs`
   - Run: `cargo bench`
   - Validate performance targets met

3. **Memory Profiling**
   - Run valgrind massif profiling
   - Validate < 50 MB for 1000 agents
   - Ensure no memory leaks

4. **Full Integration Test**
   - Create `tests/integration/test_full_swarm.py`
   - Test: 500 agents, 10,000 tasks
   - Validate throughput > 5000 tasks/s

5. **Documentation**
   - Update API docs
   - Create architecture diagrams
   - Performance guide

6. **Cognitive Brain Update**
   - Update phase status to COMPLETE
   - Document final metrics
   - Outline production deployment

**Success Criteria**:
- All Rust tests passing
- Benchmarks meet targets
- Memory usage validated
- Integration test successful
- Documentation complete
- 100% coverage achieved

**Reference**: `.github/RUST_SWARM_PATH_TO_100_COVERAGE.md`

Begin with Phase 1 (Rust unit tests) and proceed sequentially.
```

---

*Generated: 2026-01-10*
*For: copilot/sub-pr-2782*
*Current Coverage: ~70%*
*Target: 100%*
