# Phase 9.3 Track 9.3.3 - Comprehensive Test Framework

**Version**: 1.0.0-baseline  
**Status**: Framework Complete - Ready for Baseline Testing  
**Date**: 2026-07-06  
**Authority**: D-tier autonomous (mbaetiong)

## 📋 Framework Overview

This document describes the comprehensive stress test framework built for Phase 9.3 Track 9.3.3. The framework provides:

- **Stress Test Suite** (`stress_test_suite.py`) - Core framework for stress testing
- **Load Test Scripts** (`load_test_scripts.py`) - 100-concurrent PR simulation
- **Failover Scenarios** (`failover_scenarios.py`) - All 10 failure modes
- **Metrics Collection** (`metrics_collection.py`) - Real-time monitoring

## 🏗️ Architecture

### Component Structure

```
Phase 9.3 Test Framework
├── stress_test_suite.py
│   ├── TestPhase (enum)
│   ├── FailoverScenario (enum)
│   ├── TestConfig
│   ├── TestResult
│   ├── TestMetricsCollector
│   ├── StressTestRunner (abstract)
│   ├── FailoverScenarioTest (abstract)
│   └── SimpleStressTestRunner (concrete)
├── load_test_scripts.py
│   ├── LoadTestConfig
│   ├── LoadTestRequest
│   ├── LoadTestMetrics
│   ├── LoadTestRunner
│   └── Dashboard data generators
├── failover_scenarios.py
│   ├── FailoverScenarioBase (abstract)
│   ├── Scenario1_SemanticRouterFailure
│   ├── Scenario2_WorkloadBalancerFailure
│   ├── Scenario3_MCPPlaywrightFailure
│   ├── Scenario4_MCPGitHubFailure
│   ├── Scenario5_NetworkLatencySpike
│   ├── Scenario6_NetworkConnectionDrop
│   ├── Scenario7_CacheFailure
│   ├── Scenario8_MemoryLeak
│   ├── Scenario9_CascadingFailure
│   ├── Scenario10_PartialDegradation
│   └── Scenario runners
└── metrics_collection.py
    ├── SystemMetrics
    ├── AlertThresholds
    ├── AlertManager
    ├── MetricsCollector
    └── DashboardDataProvider
```

## 🧪 Test Phases

### Phase 1: Stress Test Suite

**Module**: `stress_test_suite.py`

The stress test suite provides the core framework for testing system behavior under load:

#### Key Classes

| Class | Purpose |
|-------|---------|
| `TestConfig` | Configuration for stress tests |
| `TestResult` | Results from test execution |
| `TestMetricsCollector` | Collects and aggregates metrics |
| `StressTestRunner` | Abstract base for test runners |
| `SimpleStressTestRunner` | Concrete implementation for baseline |

#### Test Entry Points

```python
# Baseline stress test (5 minutes)
@pytest.mark.stress_test
@pytest.mark.asyncio
async def test_baseline_stress_simple():
    """5-minute baseline load test with 10 concurrent requests."""

# 100-concurrent load test (10 minutes)
@pytest.mark.stress_test
@pytest.mark.asyncio
async def test_100_concurrent_load():
    """Full 100-concurrent PR simulation."""

# Failover scenario tests
@pytest.mark.stress_test
@pytest.mark.asyncio
async def test_failover_scenarios():
    """Execute all 10 failover scenarios."""
```

### Phase 2: Load Test Scripts

**Module**: `load_test_scripts.py`

Load tests simulate 100 concurrent PR requests with realistic latency distributions:

#### Key Classes

| Class | Purpose |
|-------|---------|
| `LoadTestConfig` | Configuration for load tests |
| `LoadTestRequest` | Simulated PR request |
| `LoadTestMetrics` | Metrics from load test |
| `LoadTestRunner` | Executes load tests |

#### Execution Functions

```python
# Baseline load test (5 minutes, 10 concurrent)
async def run_baseline_load_test(duration_sec: int = 300) -> LoadTestMetrics

# 100-concurrent load test (10 minutes)
async def run_100_concurrent_load_test(duration_sec: int = 600) -> LoadTestMetrics

# Sustained load test (30 minutes)
async def run_sustained_load_test(
    duration_sec: int = 1800, concurrent: int = 50
) -> LoadTestMetrics
```

### Phase 3: Failover Scenarios

**Module**: `failover_scenarios.py`

All 10 failover scenarios with failure injection, detection, and recovery verification:

#### Scenario List

| # | Scenario | Module | Timeout | Recovery Time |
|---|----------|--------|---------|----------------|
| 1 | Semantic Router Failure | `Scenario1_SemanticRouterFailure` | 30s | ~2s |
| 2 | Workload Balancer Failure | `Scenario2_WorkloadBalancerFailure` | 30s | ~2s |
| 3 | MCP Playwright Failure | `Scenario3_MCPPlaywrightFailure` | 60s | ~3s |
| 4 | MCP GitHub Failure | `Scenario4_MCPGitHubFailure` | 45s | ~2.5s |
| 5 | Network Latency Spike | `Scenario5_NetworkLatencySpike` | 60s | ~3s |
| 6 | Network Connection Drop | `Scenario6_NetworkConnectionDrop` | 45s | ~2s |
| 7 | Cache Failure | `Scenario7_CacheFailure` | 30s | ~2s |
| 8 | Memory Leak | `Scenario8_MemoryLeak` | 90s | ~3s |
| 9 | Cascading Failure | `Scenario9_CascadingFailure` | 120s | ~3s |
| 10 | Partial Degradation | `Scenario10_PartialDegradation` | 90s | ~5s |

#### Scenario Execution

```python
# Run all 10 scenarios
async def run_all_failover_scenarios() -> list[FailoverScenarioResult]

# Generate report
async def generate_failover_report(
    results: list[FailoverScenarioResult],
) -> dict[str, Any]
```

### Phase 4: Metrics Collection

**Module**: `metrics_collection.py`

Real-time metrics collection with Prometheus export and alerting:

#### Key Classes

| Class | Purpose |
|-------|---------|
| `SystemMetrics` | Complete system metrics snapshot |
| `CPUMetrics` | CPU usage metrics |
| `MemoryMetrics` | Memory usage metrics |
| `NetworkMetrics` | Network activity metrics |
| `LatencyMetrics` | Request latency metrics |
| `ThroughputMetrics` | Throughput metrics |
| `AlertManager` | Alert generation and tracking |
| `MetricsCollector` | Collects and exports metrics |
| `DashboardDataProvider` | Real-time dashboard data |

#### Default Alert Thresholds

```python
cpu_percent_warn = 75.0
cpu_percent_crit = 90.0
memory_percent_warn = 75.0
memory_percent_crit = 90.0
error_rate_warn = 0.05  # 5%
error_rate_crit = 0.10  # 10%
latency_p99_warn_ms = 1000.0
latency_p99_crit_ms = 5000.0
```

## 📊 Running the Framework

### Prerequisites

```bash
pip install pytest pytest-asyncio psutil
```

### Running Individual Test Suites

#### Baseline Stress Test
```bash
pytest stress_test_suite.py::test_baseline_stress_simple -v
```

#### 100-Concurrent Load Test
```bash
pytest stress_test_suite.py::test_100_concurrent_load -v
```

#### Failover Scenarios
```bash
pytest stress_test_suite.py::test_failover_scenarios -v
```

### Running as Standalone Scripts

#### Load Test
```bash
python load_test_scripts.py
# Generates: load_test_report.json
```

#### Failover Scenarios
```bash
python failover_scenarios.py
# Outputs JSON report to stdout
```

#### Metrics Collection
```bash
python metrics_collection.py
# Generates: metrics_<timestamp>.json and metrics_<timestamp>.prom
```

### Full Framework Test (All Components)

```bash
# Run all tests
pytest stress_test_suite.py -v -m stress_test
```

## 🎯 Success Criteria

### Baseline Tests (5-10 min)

- ✅ Framework initializes without errors
- ✅ Basic stress test completes successfully
- ✅ Metrics collected properly
- ✅ All 10 failover scenarios execute
- ✅ Alert system functions

### Target Performance Metrics

| Metric | Target | Pass Criteria |
|--------|--------|---------------|
| Success Rate | ≥95% | ≥ Target |
| P99 Latency | ≤5000ms | ≤ Target |
| CPU Usage | <80% | < Target |
| Memory Usage | <80% | < Target |
| Error Rate | <5% | < Target |

## 📈 Output Artifacts

### JSON Reports

Each test generates JSON reports in `.codex/test_results/<test_id>/`:

```json
{
  "test_id": "test_001",
  "test_name": "stress_test",
  "status": "success",
  "duration_sec": 300.0,
  "metrics_count": 60,
  "scenario_results": {...},
  "error_count": 0
}
```

### Prometheus Metrics

Exportable metrics in Prometheus format:

```
system_cpu_percent{instance="test"} 45.2 1656000000000
system_memory_mb{instance="test"} 2048.5 1656000000000
request_latency_p99_ms{instance="test"} 245.3 1656000000000
request_success_rate{instance="test"} 0.98 1656000000000
```

### Dashboard Data

Real-time dashboard state:

```json
{
  "status": "running",
  "timestamp": "2026-07-06T09:00:00",
  "system": {
    "cpu_percent": 45.2,
    "memory_mb": 2048.5,
    "memory_percent": 52.0,
    "active_connections": 85
  },
  "performance": {
    "request_latency_p99_ms": 245.3,
    "request_success_rate": 0.98,
    "throughput_requests": 1000
  },
  "alerts": {
    "critical": 0,
    "warning": 1
  }
}
```

## 🔧 Configuration

### Stress Test Configuration

```python
config = TestConfig(
    test_name="my_test",
    initial_concurrent=1,
    max_concurrent=100,
    ramp_up_duration_sec=60,
    sustained_duration_sec=300,
    request_timeout_sec=30,
)
```

### Load Test Configuration

```python
config = LoadTestConfig(
    test_name="load_test",
    duration_sec=600,
    max_concurrent_requests=100,
    ramp_up_sec=60,
    target_success_rate=0.95,
    target_p99_latency_ms=5000.0,
)
```

### Metrics Collection Configuration

```python
collector = MetricsCollector(
    output_dir=Path(".codex/metrics"),
    collection_interval_sec=5.0,
)
```

## 📝 Framework Design Notes

### Async Architecture

All framework components use Python's `asyncio` for efficient concurrent execution:

- Non-blocking I/O simulation
- Concurrent request handling
- Graceful shutdown and cleanup
- Task cancellation support

### Failure Injection Patterns

Each failover scenario follows a standardized pattern:

1. **Inject Failure** - Trigger failure condition
2. **Detect Failure** - Verify failure occurred
3. **Simulate Recovery** - System recovers
4. **Verify Recovery** - Confirm recovery successful

### Metrics Collection Strategy

- **Periodic Snapshots** - System metrics every 5 seconds
- **Event-Based Recording** - Request latency on completion
- **Aggregation** - Rolling averages and percentiles
- **Alert Thresholds** - Warning and critical levels

## 🔄 Extension Points

### Creating Custom Test Runners

```python
class CustomTestRunner(StressTestRunner):
    async def execute_request(self, request_id: str) -> float:
        # Implement custom request logic
        pass
    
    async def validate_response(self, response: Any) -> bool:
        # Implement validation logic
        pass
```

### Creating Custom Failover Scenarios

```python
class CustomFailoverScenario(FailoverScenarioBase):
    async def inject_failure(self) -> bool:
        # Implement failure injection
        pass
    
    async def detect_failure(self) -> bool:
        # Implement failure detection
        pass
    
    async def simulate_recovery(self) -> bool:
        # Implement recovery simulation
        pass
    
    async def verify_recovery(self) -> bool:
        # Implement recovery verification
        pass
```

## 📚 References

### Key Framework Files

- `stress_test_suite.py` - 18KB, Core framework
- `load_test_scripts.py` - 14KB, Load testing
- `failover_scenarios.py` - 24KB, Failover tests
- `metrics_collection.py` - 19KB, Metrics collection
- `.codex/PHASE_9_3_TRACK_3_TEST_FRAMEWORK.md` - This file

### Related Configuration

- `pytest.ini` - Pytest configuration
- `pyproject.toml` - Project dependencies
- `conftest.py` - Global pytest fixtures

## 🎓 Usage Examples

### Example 1: Run Basic Baseline Test

```bash
python -c "
import asyncio
from stress_test_suite import test_baseline_stress_simple

result = asyncio.run(test_baseline_stress_simple())
print(f'Test Status: {result.status}')
print(f'Duration: {result.total_duration_sec}s')
"
```

### Example 2: Run Load Test with Custom Config

```python
import asyncio
from load_test_scripts import LoadTestRunner, LoadTestConfig

async def run_custom_test():
    config = LoadTestConfig(
        test_name='custom_load_test',
        duration_sec=600,
        max_concurrent_requests=100,
    )
    runner = LoadTestRunner(config)
    metrics = await runner.run()
    return metrics.get_summary()

result = asyncio.run(run_custom_test())
print(result)
```

### Example 3: Collect Metrics During Test

```python
import asyncio
from stress_test_suite import SimpleStressTestRunner, TestConfig
from metrics_collection import MetricsCollector

async def run_with_metrics():
    config = TestConfig(max_concurrent=10)
    runner = SimpleStressTestRunner(config)
    collector = MetricsCollector()
    
    # Collect metrics periodically
    for _ in range(10):
        snapshot = collector.collect_snapshot()
        collector.metrics_history.append(snapshot)
        await asyncio.sleep(1)
    
    result = await runner.run()
    collector.export_json('metrics.json')
    return result

asyncio.run(run_with_metrics())
```

## ✅ Checklist

Framework Build Completion:

- [x] Stress test suite created (`stress_test_suite.py`)
- [x] Load test scripts created (`load_test_scripts.py`)
- [x] All 10 failover scenarios implemented (`failover_scenarios.py`)
- [x] Metrics collection framework created (`metrics_collection.py`)
- [x] Framework documentation written (this file)
- [ ] Baseline tests executed
- [ ] Baseline results documented
- [ ] Report template created

## 📞 Support

For issues or questions about the test framework:

1. Check pytest output: `pytest -v --tb=short`
2. Review metrics: Check `.codex/metrics/` directory
3. Check alerts: Review `AlertManager.alerts` list
4. Debug scenarios: Use `logging.basicConfig(level=logging.DEBUG)`

---

**Next Phase**: Execute baseline tests (5-10 min) and document results
