# PROMPTSET: Autonomous Rust-Python Hybrid Swarm Implementation
## Milestone-Driven Execution Templates

**Version**: 1.0.0  
**Date**: 2026-01-10  
**Parent Plan**: RUST_SWARM_ARCHITECTURE_PLANSET.md  

---

## Purpose

This promptset provides ready-to-use prompt templates for autonomous implementation of the Rust-Python Hybrid Swarm architecture. Each prompt is designed for the GitHub Copilot coding agent to execute independently with minimal human intervention.

---

## Master Execution Prompt

```markdown
@copilot Implement Rust-Python Hybrid AI Agent Swarm Architecture

**Plan**: `.github/plans/RUST_SWARM_ARCHITECTURE_PLANSET.md`  
**Phase**: Foundation → Orchestration → Optimization  
**Duration**: 8 weeks autonomous execution  

**Context**:
Transitioning Codex from pure Python to Rust-orchestrated agent swarm to eliminate GIL bottlenecks and enable 500+ concurrent agents. Zero additional cost (GitHub Team + Copilot Pro+ only).

**Execution Protocol**:
1. Implement each milestone sequentially
2. Validate before proceeding to next
3. Self-healing: max 5 iterations per milestone
4. Document progress via PDA loops
5. Update cognitive brain status

**Starting Point**: Milestone 1.1 (Project Scaffolding)

**Success Criteria**:
- 10x latency improvement
- 4x memory reduction
- 100x agent scaling (5 → 500)
- Zero additional infrastructure cost

Begin autonomous implementation. Create PRs for each milestone.
```

---

## Milestone 1.1: Project Scaffolding

```markdown
@copilot Implement Milestone 1.1: Rust-Python Project Scaffolding

**Objective**: Create Maturin mixed-layout project structure for hybrid swarm

**Tasks**:
1. Create `Cargo.toml`:
   ```toml
   [package]
   name = "codex-swarm-engine"
   version = "0.1.0"
   edition = "2021"
   
   [lib]
   name = "codex_engine"
   crate-type = ["cdylib"]
   
   [dependencies]
   pyo3 = { version = "0.20", features = ["extension-module", "abi3-py37"] }
   tokio = { version = "1.36", features = ["full"] }
   dashmap = "5.5.3"
   serde = { version = "1.0", features = ["derive"] }
   ```

2. Configure `pyproject.toml`:
   ```toml
   [build-system]
   requires = ["maturin>=1.4,<2.0"]
   build-backend = "maturin"
   
   [project]
   name = "codex-engine"
   requires-python = ">=3.7"
   ```

3. Create `src/lib.rs`:
   ```rust
   use pyo3::prelude::*;
   
   #[pymodule]
   fn codex_engine(_py: Python, m: &PyModule) -> PyResult<()> {
       m.add_class::<SwarmState>()?;
       Ok(())
   }
   ```

4. Generate type stubs `codex_engine.pyi`

**Validation**:
```bash
maturin develop
python -c "import codex_engine; print('✓ Import successful')"
```

**Acceptance Criteria**:
- Build completes without errors
- Python can import module
- Type hints work in IDE

**Failure Recovery**:
If build fails, check Python version compatibility and retry with abi3-py38.

**Time Estimate**: 2-4 hours

Create PR: "feat: Add Rust project scaffolding for hybrid swarm"
```

---

## Milestone 1.2: SwarmState Bridge

```markdown
@copilot Implement Milestone 1.2: SwarmState PyO3 Bridge

**Objective**: Create shared state accessible from both Rust and Python

**Context**: Previous milestone created basic scaffold. Now adding state management.

**Implementation**:

Create `src/state.rs`:
```rust
use pyo3::prelude::*;
use dashmap::DashMap;
use std::sync::Arc;

#[pyclass]
pub struct SwarmState {
    agents: Arc<DashMap<String, AgentStatus>>,
}

#[derive(Clone)]
pub enum AgentStatus {
    Idle,
    Working(String),
    Complete,
}

#[pymethods]
impl SwarmState {
    #[new]
    fn new() -> Self {
        SwarmState {
            agents: Arc::new(DashMap::new()),
        }
    }
    
    fn register_agent(&self, agent_id: String) -> PyResult<()> {
        self.agents.insert(agent_id, AgentStatus::Idle);
        Ok(())
    }
    
    fn get_agent_count(&self) -> usize {
        self.agents.len()
    }
    
    fn set_agent_status(&self, agent_id: String, status: String) -> PyResult<()> {
        self.agents.insert(agent_id, AgentStatus::Working(status));
        Ok(())
    }
}
```

Update `src/lib.rs` to include state module.

**Tests**:

Create `tests/test_state.rs`:
```rust
#[test]
fn test_concurrent_agent_registration() {
    use std::thread;
    let state = SwarmState::new();
    let handles: Vec<_> = (0..100)
        .map(|i| {
            let s = state.clone();
            thread::spawn(move || {
                s.register_agent(format!("agent_{}", i)).unwrap();
            })
        })
        .collect();
    for h in handles { h.join().unwrap(); }
    assert_eq!(state.get_agent_count(), 100);
}
```

Create `tests/test_python_bridge.py`:
```python
def test_swarm_state_from_python():
    from codex_engine import SwarmState
    state = SwarmState()
    state.register_agent("agent_1")
    assert state.get_agent_count() == 1
```

**Validation**:
```bash
cargo test
pytest tests/test_python_bridge.py
```

**Acceptance Criteria**:
- All Rust tests pass
- Python can create and use SwarmState
- Concurrent access works (no data races)
- Memory usage < 10 MB for 1000 agents

**Time Estimate**: 4-6 hours

Create PR: "feat: Add SwarmState with concurrent access support"
```

---

## Milestone 1.3: Tokio Runtime Integration

```markdown
@copilot Implement Milestone 1.3: Tokio Async Runtime

**Objective**: Initialize Tokio runtime for asynchronous orchestration

**Context**: SwarmState created in previous milestone. Now adding async execution layer.

**Implementation**:

Create `src/runtime.rs`:
```rust
use pyo3::prelude::*;
use tokio::runtime::Runtime;
use std::sync::Arc;

#[pyclass]
pub struct Orchestrator {
    runtime: Arc<Runtime>,
    state: Arc<SwarmState>,
}

#[pymethods]
impl Orchestrator {
    #[new]
    fn new(state: Py<SwarmState>) -> PyResult<Self> {
        let runtime = Runtime::new()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(Orchestrator {
            runtime: Arc::new(runtime),
            state: Arc::new(state.extract()?),
        })
    }
    
    fn start(&self) -> PyResult<()> {
        let state = self.state.clone();
        self.runtime.spawn(async move {
            orchestrator_loop(state).await;
        });
        Ok(())
    }
}

async fn orchestrator_loop(state: Arc<SwarmState>) {
    let mut interval = tokio::time::interval(std::time::Duration::from_millis(100));
    loop {
        interval.tick().await;
        // Process tasks
    }
}
```

**Integration with PyO3 Async**:
```toml
# Add to Cargo.toml
pyo3-async-runtimes = { version = "0.20", features = ["tokio-runtime"] }
```

**Tests**:
```rust
#[tokio::test]
async fn test_orchestrator_startup() {
    let state = SwarmState::new();
    let orch = Orchestrator::new(state).unwrap();
    orch.start().unwrap();
    tokio::time::sleep(Duration::from_millis(500)).await;
    // Verify orchestrator is running
}
```

**Python Integration Test**:
```python
import asyncio
from codex_engine import SwarmState, Orchestrator

async def test_async_orchestrator():
    state = SwarmState()
    orch = Orchestrator(state)
    orch.start()
    await asyncio.sleep(1.0)
    # Verify state updates
```

**Validation**:
```bash
cargo test --features tokio
pytest tests/test_async.py
```

**Acceptance Criteria**:
- Tokio runtime starts without blocking Python
- Async loop processes at 10 Hz minimum
- No deadlocks or race conditions
- CPU usage appropriate (not spinning)

**Time Estimate**: 6-8 hours

Create PR: "feat: Add Tokio async runtime for orchestration"
```

---

## Milestone 2.1: Asynchronous Task Queue

```markdown
@copilot Implement Milestone 2.1: High-Performance Task Queue

**Objective**: Replace Python asyncio.Queue with Tokio mpsc channels

**Context**: Foundation complete. Now building core orchestration primitives.

**Benefits**:
- 10x higher throughput vs Python queue
- Lock-free multi-producer support
- Built-in backpressure handling

**Implementation**:

Create `src/queue.rs`:
```rust
use tokio::sync::mpsc;
use serde::{Serialize, Deserialize};
use pyo3::prelude::*;

#[derive(Serialize, Deserialize, Clone)]
#[pyclass]
pub struct Task {
    #[pyo3(get, set)]
    id: String,
    #[pyo3(get, set)]
    task_type: String,
    #[pyo3(get, set)]
    data: String, // JSON-encoded data
}

#[pyclass]
pub struct TaskQueue {
    tx: Arc<mpsc::UnboundedSender<Task>>,
    rx: Arc<Mutex<mpsc::UnboundedReceiver<Task>>>,
}

#[pymethods]
impl TaskQueue {
    #[new]
    fn new() -> Self {
        let (tx, rx) = mpsc::unbounded_channel();
        TaskQueue {
            tx: Arc::new(tx),
            rx: Arc::new(Mutex::new(rx)),
        }
    }
    
    fn submit(&self, task: Task) -> PyResult<()> {
        self.tx.send(task)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(())
    }
    
    fn receive(&self, py: Python) -> PyResult<Option<Task>> {
        py.allow_threads(|| {
            let mut rx = self.rx.lock().unwrap();
            Ok(rx.try_recv().ok())
        })
    }
}
```

**Benchmarks**:
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_task_submission(c: &mut Criterion) {
    let queue = TaskQueue::new();
    c.bench_function("submit_10k_tasks", |b| {
        b.iter(|| {
            for i in 0..10000 {
                let task = Task { id: format!("{}", i), task_type: "test".to_string(), data: "{}".to_string() };
                queue.submit(black_box(task)).unwrap();
            }
        })
    });
}
```

**Python Integration**:
```python
from codex_engine import TaskQueue, Task

def test_task_queue_throughput():
    import time
    queue = TaskQueue()
    start = time.time()
    for i in range(10000):
        task = Task(id=str(i), task_type="test", data="{}")
        queue.submit(task)
    elapsed = time.time() - start
    assert elapsed < 1.0  # < 1 second for 10k tasks
```

**Validation**:
```bash
cargo bench
pytest tests/test_queue.py
```

**Acceptance Criteria**:
- Throughput > 10,000 tasks/second
- Latency < 1ms per submission
- No message loss under high load
- Backpressure handled correctly

**Time Estimate**: 6-8 hours

Create PR: "feat: Add high-performance Tokio-based task queue"
```

---

## Milestone 2.2: Agent Lifecycle Management

```markdown
@copilot Implement Milestone 2.2: Agent Pool Manager

**Objective**: Rust orchestrator manages Python agent processes

**Context**: Task queue operational. Now adding agent execution layer.

**Implementation**:

Create `src/agent_manager.rs`:
```rust
use rayon::ThreadPool;
use pyo3::prelude::*;
use dashmap::DashMap;

#[pyclass]
pub struct AgentManager {
    pool: ThreadPool,
    active_agents: Arc<DashMap<String, AgentHandle>>,
    max_agents: usize,
}

pub struct AgentHandle {
    id: String,
    status: AgentStatus,
}

#[pymethods]
impl AgentManager {
    #[new]
    fn new(max_agents: usize) -> PyResult<Self> {
        let pool = rayon::ThreadPoolBuilder::new()
            .num_threads(max_agents)
            .build()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(AgentManager {
            pool,
            active_agents: Arc::new(DashMap::new()),
            max_agents,
        })
    }
    
    fn spawn_agent(&self, agent_id: String, config: String) -> PyResult<()> {
        if self.active_agents.len() >= self.max_agents {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Max agents reached"));
        }
        
        let agents = self.active_agents.clone();
        self.pool.spawn(move || {
            Python::with_gil(|py| {
                let agent_module = py.import("codex.agent")?;
                let agent = agent_module.call_method1("Agent", (config,))?;
                agent.call_method0("run")?;
                agents.remove(&agent_id);
                Ok::<(), PyErr>(())
            }).unwrap();
        });
        
        self.active_agents.insert(agent_id.clone(), AgentHandle {
            id: agent_id,
            status: AgentStatus::Working("initialized".to_string()),
        });
        Ok(())
    }
    
    fn get_active_count(&self) -> usize {
        self.active_agents.len()
    }
}
```

**Load Testing**:
```rust
#[test]
fn test_spawn_500_agents() {
    let manager = AgentManager::new(500).unwrap();
    let start = Instant::now();
    for i in 0..500 {
        manager.spawn_agent(format!("agent_{}", i), "{}".to_string()).unwrap();
    }
    let elapsed = start.elapsed();
    assert!(elapsed < Duration::from_secs(5)); // < 5s to spawn 500
    
    // Wait for agents to initialize
    std::thread::sleep(Duration::from_secs(2));
    assert!(manager.get_active_count() > 450); // Most should be active
}
```

**Python Test**:
```python
def test_agent_pool_parallel_execution():
    from codex_engine import AgentManager
    manager = AgentManager(max_agents=10)
    for i in range(10):
        manager.spawn_agent(f"agent_{i}", "{}")
    time.sleep(0.5)
    assert manager.get_active_count() > 0
```

**Validation**:
```bash
cargo test --release -- --test-threads=1
pytest tests/test_agent_manager.py
```

**Acceptance Criteria**:
- Can spawn 500 agents in < 5 seconds
- Agents execute in true parallel (not GIL-limited)
- CPU utilization reaches 90%+ under load
- Memory usage < 50 MB per agent

**Time Estimate**: 8-10 hours

Create PR: "feat: Add agent lifecycle manager with Rayon thread pool"
```

---

## Milestone 3.1: Compression Middleware

```markdown
@copilot Implement Milestone 3.1: LZ4/Zstd Compression Pipeline

**Objective**: Add high-performance compression for data efficiency

**Context**: Orchestration layer functional. Now optimizing data transfer.

**Benefits**:
- 2x speedup with BufWriter optimization
- 400 MB/s compression with LZ4
- 50% smaller payloads vs uncompressed

**Implementation**:

Create `src/compression.rs`:
```rust
use std::io::{BufWriter, Write};
use lz4::EncoderBuilder;
use pyo3::prelude::*;

#[pyclass]
pub struct CompressionPipeline {
    codec: CompressionCodec,
}

#[derive(Clone, Copy)]
enum CompressionCodec {
    LZ4,
    Zstd(i32), // compression level
}

#[pymethods]
impl CompressionPipeline {
    #[new]
    fn new(codec: String, level: Option<i32>) -> PyResult<Self> {
        let codec = match codec.as_str() {
            "lz4" => CompressionCodec::LZ4,
            "zstd" => CompressionCodec::Zstd(level.unwrap_or(3)),
            _ => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid codec")),
        };
        Ok(CompressionPipeline { codec })
    }
    
    fn compress(&self, data: &[u8]) -> PyResult<Vec<u8>> {
        match self.codec {
            CompressionCodec::LZ4 => self.compress_lz4(data),
            CompressionCodec::Zstd(level) => self.compress_zstd(data, level),
        }
    }
    
    fn decompress(&self, data: &[u8]) -> PyResult<Vec<u8>> {
        match self.codec {
            CompressionCodec::LZ4 => self.decompress_lz4(data),
            CompressionCodec::Zstd(_) => self.decompress_zstd(data),
        }
    }
}

impl CompressionPipeline {
    fn compress_lz4(&self, data: &[u8]) -> PyResult<Vec<u8>> {
        let mut output = Vec::new();
        let mut writer = BufWriter::with_capacity(4096, &mut output);
        let mut encoder = EncoderBuilder::new()
            .level(4)
            .build(&mut writer)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        encoder.write_all(data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let (_writer, result) = encoder.finish();
        result.map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        Ok(output)
    }
}
```

**Benchmarks**:
```rust
fn bench_compression(c: &mut Criterion) {
    let data = vec![0u8; 1024 * 1024]; // 1MB
    let pipeline = CompressionPipeline::new("lz4".to_string(), None).unwrap();
    
    c.bench_function("compress_1mb_lz4", |b| {
        b.iter(|| pipeline.compress(black_box(&data)))
    });
}
```

**Python Integration**:
```python
def test_compression_ratio():
    from codex_engine import CompressionPipeline
    pipeline = CompressionPipeline("lz4")
    data = b"x" * 1024 * 1024  # 1MB repetitive data
    compressed = pipeline.compress(data)
    ratio = len(data) / len(compressed)
    assert ratio > 10.0  # > 10x for repetitive data
```

**Validation**:
```bash
cargo bench --bench compression
pytest tests/test_compression.py
```

**Acceptance Criteria**:
- LZ4 compression > 400 MB/s
- Zstd level 3 > 200 MB/s
- 2x speedup with BufWriter vs naive
- Round-trip compression lossless

**Time Estimate**: 6-8 hours

Create PR: "feat: Add LZ4/Zstd compression middleware"
```

---

## Milestone 3.2: Binary Serialization

```markdown
@copilot Implement Milestone 3.2: MessagePack Serialization

**Objective**: Replace JSON with binary format via Serde

**Context**: Compression added. Now optimizing serialization layer.

**Benefits**:
- 10x faster than Python pickle
- 50% smaller than JSON
- Zero-copy deserialization

**Implementation**:

Create `src/serialization.rs`:
```rust
use serde::{Serialize, Deserialize};
use pyo3::prelude::*;
use rmp_serde;

#[derive(Serialize, Deserialize, Clone)]
#[pyclass]
pub struct AgentState {
    #[pyo3(get, set)]
    id: String,
    #[pyo3(get, set)]
    memory: Vec<String>,
    metrics: HashMap<String, f64>,
}

#[pyfunction]
fn serialize_state(state: &AgentState) -> PyResult<Vec<u8>> {
    rmp_serde::to_vec(state)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

#[pyfunction]
fn deserialize_state(data: &[u8]) -> PyResult<AgentState> {
    rmp_serde::from_slice(data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}
```

**Benchmarks**:
```rust
fn bench_serialization(c: &mut Criterion) {
    let state = AgentState {
        id: "agent_1".to_string(),
        memory: vec!["item1".to_string(); 1000],
        metrics: HashMap::new(),
    };
    
    c.bench_function("messagepack_serialize", |b| {
        b.iter(|| serialize_state(black_box(&state)))
    });
    
    c.bench_function("json_serialize", |b| {
        b.iter(|| serde_json::to_vec(black_box(&state)))
    });
}
```

**Comparison Test**:
```python
import json
import time
from codex_engine import AgentState, serialize_state, deserialize_state

def test_serialization_speed():
    state = AgentState(id="agent_1", memory=["item"] * 1000)
    
    # MessagePack
    start = time.time()
    for _ in range(1000):
        data = serialize_state(state)
        deserialize_state(data)
    msgpack_time = time.time() - start
    
    # JSON
    start = time.time()
    for _ in range(1000):
        data = json.dumps({"id": state.id, "memory": state.memory})
        json.loads(data)
    json_time = time.time() - start
    
    assert msgpack_time < json_time / 5  # > 5x faster
```

**Validation**:
```bash
cargo bench --bench serialization
pytest tests/test_serialization.py
```

**Acceptance Criteria**:
- MessagePack 10x faster than JSON
- Payloads 50% smaller than JSON
- Round-trip serialization preserves data
- Python interop seamless

**Time Estimate**: 4-6 hours

Create PR: "feat: Add MessagePack binary serialization"
```

---

## Continuous Validation Prompt

```markdown
@copilot Run continuous validation suite

**Context**: Multiple milestones implemented. Validate integration.

**Tasks**:
1. Build all modules: `maturin develop --release`
2. Run Rust tests: `cargo test --release`
3. Run Python tests: `pytest tests/ -v`
4. Run benchmarks: `cargo bench`
5. Profile memory: `valgrind --tool=massif python -c "import codex_engine; ..."`
6. Check CPU usage under load

**Metrics to Report**:
- Build time
- Test pass rate
- Benchmark results vs targets
- Memory usage per agent
- CPU utilization

**Failure Recovery**:
- If tests fail: Identify failing test, debug, retry
- If benchmarks below target: Profile with samply, optimize hot paths
- If memory leaks: Use heaptrack, fix leaks
- Maximum 3 validation cycles before human review

**Success Criteria**:
- All tests pass
- All benchmarks meet targets
- No memory leaks
- CPU utilization > 90% under load

Report results in PR comment with metrics table.
```

---

## Final Integration Prompt

```markdown
@copilot Finalize Rust-Python Hybrid Swarm Integration

**Context**: All milestones complete. Final integration and validation.

**Tasks**:
1. Integration testing with full swarm (500 agents)
2. End-to-end performance validation
3. Stress testing under sustained load
4. Documentation updates
5. Cognitive brain status update

**Integration Test**:
```python
async def test_full_swarm_integration():
    from codex_engine import SwarmState, Orchestrator, AgentManager, TaskQueue
    
    # Initialize components
    state = SwarmState()
    queue = TaskQueue()
    manager = AgentManager(max_agents=500)
    orch = Orchestrator(state)
    
    # Start orchestrator
    orch.start()
    
    # Spawn 500 agents
    for i in range(500):
        manager.spawn_agent(f"agent_{i}", "{}")
    
    # Submit 10,000 tasks
    for i in range(10000):
        task = Task(id=str(i), task_type="analyze", data="{}")
        queue.submit(task)
    
    # Wait for completion
    await asyncio.sleep(30)
    
    # Validate
    assert manager.get_active_count() > 450
    assert state.get_agent_count() == 500
```

**Performance Validation**:
- Latency: < 1ms task submission
- Throughput: > 10k tasks/second
- Memory: < 50 MB per agent (< 25 GB total)
- CPU: > 90% utilization

**Documentation**:
- Update README with Rust architecture
- Add migration guide
- Document performance improvements
- Create deployment guide

**Cognitive Brain Update**:
```yaml
phase_11_rust_hybrid:
  status: COMPLETE
  architecture:
    python_brain: ML logic preserved
    rust_body: Orchestration layer
    bridge: PyO3 seamless
  metrics:
    latency_improvement: 10x
    memory_reduction: 4x
    agent_scaling: 100x (5 → 500)
    cost: $0 additional
  next_phase:
    - distributed_tracing
    - auto_scaling
    - advanced_consensus
```

**Success Criteria**:
- Full integration test passes
- All performance targets met
- Documentation complete
- Production deployment ready

Create PR: "feat: Complete Rust-Python hybrid swarm integration"

Mark planset as COMPLETE in cognitive brain.
```

---

## Emergency Rollback Prompt

```markdown
@copilot Execute emergency rollback of Rust orchestrator

**Reason**: <specify critical issue>

**Tasks**:
1. Disable Rust orchestrator: `export CODEX_USE_RUST_ORCHESTRATOR=false`
2. Revert to Python orchestrator
3. Validate fallback functionality
4. Document failure mode
5. Create hotfix branch

**Validation**:
- System functional on Python orchestrator
- No data loss
- Agents can resume work

**Root Cause Analysis**:
- Identify failure point
- Document reproduction steps
- Propose fix strategy
- Estimate fix timeline

**Recovery Plan**:
- Short-term: Run on Python (degraded performance)
- Medium-term: Fix identified issue
- Long-term: Re-enable Rust with additional safeguards

Create incident report in `.github/incidents/rust-rollback-YYYY-MM-DD.md`
```

---

## Conclusion

This promptset provides comprehensive, ready-to-execute templates for autonomous implementation of the Rust-Python Hybrid Swarm architecture. Each prompt:

✅ **Is self-contained** with full context  
✅ **Includes validation** criteria  
✅ **Provides failure recovery** plans  
✅ **Estimates time** for planning  
✅ **Creates traceable PRs** for review  

**Usage**: Copy prompts to GitHub issues, assign to `@copilot`, and let autonomous implementation proceed.

---

**PROMPTSET STATUS**: ✅ COMPLETE AND READY FOR EXECUTION

**Next Action**: Begin with Master Execution Prompt to start autonomous implementation
