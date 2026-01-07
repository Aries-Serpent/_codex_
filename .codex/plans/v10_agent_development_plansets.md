# V10 Custom Agent Development - Complete Plansets & Promptsets
# PR #2685 - Autonomous Implementation Guide

> **Generated**: 2026-01-03T19:49:22Z  
> **Author**: Copilot AI Agent  
> **Branch**: copilot/sub-pr-2682  
> **Purpose**: Autonomous agent-by-agent implementation with complete promptsets

---

## 📋 Overview

This document provides complete plansets and promptsets for implementing all remaining V10 custom agents. Each agent includes:
- Detailed implementation specification
- Complete promptset for autonomous execution
- Test requirements and validation criteria
- Integration points and dependencies
- Performance benchmarks

**Current Status**: 1/6 agents complete (Agent 1: Emergent Intelligence ✅)  
**Remaining**: 5 agents + 4 enhancements = 9 tasks  
**Target**: 597+ total tests

---

## 🎯 Agent 2: Performance Monitor Agent

**Priority**: HIGH | **Week**: 2, Day 3 | **Seed**: 47 | **Tests**: 15+

### Specification

**Purpose**: Real-time performance tracking, latency monitoring, and throughput optimization

**Integration Points**:
- Phase 8.10: `PerformanceBenchmarkSuite`
- Phase 8.10: `MonitoringObservability`
- Prometheus metrics
- OpenTelemetry traces

**Capabilities**:
1. Continuous latency monitoring (target: <100ms p95)
2. Throughput optimization (target: >1000 req/s)
3. Resource usage prediction
4. Automatic performance regression detection
5. Real-time alerting

**File Structure**:
```
.github/agents/performance-monitor-agent/
├── agent.yml
├── README.md
├── src/
│   ├── latency_monitor.py
│   ├── throughput_optimizer.py
│   ├── resource_predictor.py
│   ├── regression_detector.py
│   └── alert_manager.py
└── tests/
    └── test_performance_monitor_agent.py (15+ tests)
```

### Implementation Promptset

```markdown
# PROMPTSET: Performance Monitor Agent Implementation

## CONTEXT
You are implementing Agent 2 of 6 for V10 Custom Agent Development.
- Base pattern: emergent-intelligence-agent (reference implementation)
- Seed: 47 (from vars.PERF_MONITOR_SEED)
- Integration: Phase 8.10 production deployment module

## REQUIREMENTS
1. Create performance-monitor-agent/ directory structure
2. Implement 5 core capabilities with PDA loop integration
3. Write 15+ comprehensive tests (deterministic, seed=47)
4. Add agent.yml manifest with performance targets
5. Create README.md with usage examples
6. Compile and validate all code

## CORE IMPLEMENTATION

### File 1: src/latency_monitor.py
```python
"""
Latency Monitor for Performance Agent
Tracks request latencies and detects anomalies
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import time
import statistics

RANDOM_SEED = 47  # Performance Monitor Agent seed

@dataclass
class LatencyMetric:
    """Single latency measurement"""
    timestamp: datetime
    endpoint: str
    latency_ms: float
    status_code: int
    metadata: Dict[str, Any]

class LatencyMonitor:
    """Monitor request latencies and detect performance issues"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.measurements: List[LatencyMetric] = []
        self.thresholds = {
            "p50": 50.0,   # 50ms
            "p95": 100.0,  # 100ms
            "p99": 200.0   # 200ms
        }
    
    def record_latency(
        self,
        endpoint: str,
        latency_ms: float,
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a latency measurement"""
        metric = LatencyMetric(
            timestamp=datetime.now(),
            endpoint=endpoint,
            latency_ms=latency_ms,
            status_code=status_code,
            metadata=metadata or {}
        )
        self.measurements.append(metric)
    
    def get_percentiles(self, endpoint: Optional[str] = None) -> Dict[str, float]:
        """Calculate latency percentiles"""
        measurements = self.measurements
        if endpoint:
            measurements = [m for m in measurements if m.endpoint == endpoint]
        
        if not measurements:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        latencies = sorted([m.latency_ms for m in measurements])
        n = len(latencies)
        
        return {
            "p50": latencies[int(n * 0.50)],
            "p95": latencies[int(n * 0.95)] if n > 1 else latencies[0],
            "p99": latencies[int(n * 0.99)] if n > 1 else latencies[0]
        }
    
    def detect_regression(self) -> bool:
        """Detect if latencies have regressed"""
        if len(self.measurements) < 10:
            return False
        
        # Compare recent vs historical
        recent = [m.latency_ms for m in self.measurements[-10:]]
        historical = [m.latency_ms for m in self.measurements[:-10]]
        
        if not historical:
            return False
        
        recent_p95 = sorted(recent)[int(len(recent) * 0.95)]
        hist_p95 = sorted(historical)[int(len(historical) * 0.95)]
        
        # Regression if recent > 120% of historical
        return recent_p95 > hist_p95 * 1.2
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get monitoring metrics"""
        percentiles = self.get_percentiles()
        return {
            "total_measurements": len(self.measurements),
            "percentiles": percentiles,
            "threshold_violations": sum(
                1 for m in self.measurements 
                if m.latency_ms > self.thresholds["p95"]
            ),
            "regression_detected": self.detect_regression()
        }
```

### File 2: agent.yml
```yaml
name: performance-monitor-agent
version: 1.0.0
description: Real-time performance tracking and optimization
author: Cognitive Brain Team
created: 2026-01-03

capabilities:
  - latency_monitoring
  - throughput_optimization
  - resource_usage_prediction
  - regression_detection
  - real_time_alerting

integration:
  phase8_10:
    - PerformanceBenchmarkSuite
    - MonitoringObservability

triggers:
  - pull_request
  - push
  - schedule: "*/15 * * * *"  # Every 15 pre-commits

config:
  random_seed: 47
  max_retries: 3
  timeout_seconds: 300
  latency_p95_target_ms: 100
  throughput_target_rps: 1000

metrics:
  - latency_p50
  - latency_p95
  - latency_p99
  - throughput_rps
  - regression_count

performance_targets:
  latency_p95_ms: 100
  throughput_rps: 1000
  monitoring_overhead_pct: 5
```

### File 3: tests/test_performance_monitor_agent.py
```python
"""
Tests for Performance Monitor Agent
Minimum 15 test methods required
"""
import pytest
from datetime import datetime

from latency_monitor import LatencyMonitor, LatencyMetric

RANDOM_SEED = 47

class TestLatencyMonitor:
    """Test latency monitoring"""
    
    def test_init(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        assert monitor.seed == RANDOM_SEED
        assert len(monitor.measurements) == 0
    
    def test_record_latency(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        monitor.record_latency("/api/v1/test", 45.5, 200)
        assert len(monitor.measurements) == 1
        assert monitor.measurements[0].latency_ms == 45.5
    
    def test_percentiles_empty(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        percentiles = monitor.get_percentiles()
        assert percentiles["p50"] == 0.0
    
    def test_percentiles_single(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        monitor.record_latency("/api/test", 50.0)
        percentiles = monitor.get_percentiles()
        assert percentiles["p50"] == 50.0
    
    def test_percentiles_multiple(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        for i in range(100):
            monitor.record_latency("/api/test", float(i))
        percentiles = monitor.get_percentiles()
        assert 45.0 <= percentiles["p50"] <= 55.0
        assert 90.0 <= percentiles["p95"] <= 99.0
    
    def test_regression_detection_insufficient_data(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        for i in range(5):
            monitor.record_latency("/api/test", 50.0)
        assert not monitor.detect_regression()
    
    def test_regression_detection_no_regression(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        # Historical: 50ms
        for i in range(50):
            monitor.record_latency("/api/test", 50.0)
        # Recent: 55ms (within threshold)
        for i in range(10):
            monitor.record_latency("/api/test", 55.0)
        assert not monitor.detect_regression()
    
    def test_regression_detection_with_regression(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        # Historical: 50ms
        for i in range(50):
            monitor.record_latency("/api/test", 50.0)
        # Recent: 150ms (regression!)
        for i in range(10):
            monitor.record_latency("/api/test", 150.0)
        assert monitor.detect_regression()
    
    def test_get_metrics(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        monitor.record_latency("/api/test", 50.0)
        metrics = monitor.get_metrics()
        assert "total_measurements" in metrics
        assert metrics["total_measurements"] == 1
    
    def test_threshold_violations(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        # Below threshold
        monitor.record_latency("/api/test", 50.0)
        # Above threshold
        monitor.record_latency("/api/test", 150.0)
        metrics = monitor.get_metrics()
        assert metrics["threshold_violations"] == 1
    
    def test_filter_by_endpoint(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        monitor.record_latency("/api/v1", 50.0)
        monitor.record_latency("/api/v2", 100.0)
        percentiles = monitor.get_percentiles("/api/v1")
        assert percentiles["p50"] == 50.0
    
    def test_deterministic_with_seed(self):
        monitor1 = LatencyMonitor(seed=47)
        monitor2 = LatencyMonitor(seed=47)
        assert monitor1.seed == monitor2.seed
    
    # Add 3 more tests for 15 total...
    def test_metadata_storage(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        monitor.record_latency("/api/test", 50.0, metadata={"user": "test"})
        assert monitor.measurements[0].metadata["user"] == "test"
    
    def test_status_code_tracking(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        monitor.record_latency("/api/test", 50.0, status_code=404)
        assert monitor.measurements[0].status_code == 404
    
    def test_timestamp_recorded(self):
        monitor = LatencyMonitor(seed=RANDOM_SEED)
        before = datetime.now()
        monitor.record_latency("/api/test", 50.0)
        after = datetime.now()
        ts = monitor.measurements[0].timestamp
        assert before <= ts <= after
```

## VALIDATION
1. Compile: `python3 -m py_compile src/*.py tests/*.py`
2. Import test: `python3 -c "from src.latency_monitor import LatencyMonitor"`
3. Test count: `grep -c "def test_" tests/*.py` (should be >= 15)
4. agent.yml validation: `python3 -c "import yaml; yaml.safe_load(open('agent.yml'))"`

## SUCCESS CRITERIA
- All files compile without errors
- 15+ tests defined
- agent.yml valid
- README.md with examples
- Seed 47 used consistently
- PDA loop structure present
```

---

## 🎯 Agent 3: Documentation Agent

**Priority**: HIGH | **Week**: 2, Day 4 | **Seed**: 48 | **Tests**: 15+

### Specification

**Purpose**: Auto-generate API documentation, tutorials, changelogs, and architecture diagrams

**Integration Points**:
- Phase 8.10: `DocumentationPortal`
- Phase 8.11: `ExplainableAI`
- AST analysis
- Git history

**Capabilities**:
1. API documentation from code (docstrings + type hints)
2. Tutorial generation from usage patterns
3. Changelog automation (from git commits)
4. Architecture diagram updates (mermaid generation)
5. Documentation versioning

### Implementation Promptset

```markdown
# PROMPTSET: Documentation Agent Implementation

## CONTEXT
You are implementing Agent 3 of 6 for V10 Custom Agent Development.
- Base pattern: emergent-intelligence-agent
- Seed: 48 (from vars.DOC_AGENT_SEED)
- Integration: Phase 8.10 documentation portal

## REQUIREMENTS
1. Create documentation-agent/ directory structure
2. Implement 5 core capabilities with PDA loop integration
3. Write 15+ comprehensive tests (deterministic, seed=48)
4. Add agent.yml manifest with doc generation targets
5. Create README.md with usage examples
6. Focus on Python API doc generation

## CORE IMPLEMENTATION

### File 1: src/api_doc_generator.py
```python
"""
API Documentation Generator
Extracts docstrings and type hints to generate API docs
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import ast
import inspect
import random

RANDOM_SEED = 48  # Documentation Agent seed

@dataclass
class FunctionDoc:
    """Documentation for a function"""
    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, str]]
    returns: Optional[str]
    examples: List[str]

class APIDocGenerator:
    """Generate API documentation from Python code"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.documented_functions: List[FunctionDoc] = []
    
    def extract_function_docs(self, source_code: str) -> List[FunctionDoc]:
        """Extract documentation from Python source code"""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []
        
        docs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc = self._extract_function_doc(node, source_code)
                if doc:
                    docs.append(doc)
        
        self.documented_functions.extend(docs)
        return docs
    
    def _extract_function_doc(
        self,
        node: ast.FunctionDef,
        source: str
    ) -> Optional[FunctionDoc]:
        """Extract documentation for a single function"""
        # Get docstring
        docstring = ast.get_docstring(node) or "No documentation"
        
        # Build signature
        args = [arg.arg for arg in node.args.args]
        signature = f"{node.name}({', '.join(args)})"
        
        # Extract parameters
        parameters = [
            {"name": arg.arg, "type": "Any", "description": ""}
            for arg in node.args.args
        ]
        
        # Extract return type
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)
        
        return FunctionDoc(
            name=node.name,
            signature=signature,
            docstring=docstring,
            parameters=parameters,
            returns=returns,
            examples=[]
        )
    
    def generate_markdown(self) -> str:
        """Generate Markdown API documentation"""
        if not self.documented_functions:
            return "# API Documentation\n\nNo functions documented.\n"
        
        md = "# API Documentation\n\n"
        for func in self.documented_functions:
            md += f"## `{func.signature}`\n\n"
            md += f"{func.docstring}\n\n"
            
            if func.parameters:
                md += "**Parameters:**\n\n"
                for param in func.parameters:
                    md += f"- `{param['name']}` ({param['type']}): {param.get('description', 'No description')}\n"
                md += "\n"
            
            if func.returns:
                md += f"**Returns:** `{func.returns}`\n\n"
        
        return md
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get documentation metrics"""
        return {
            "functions_documented": len(self.documented_functions),
            "total_docstring_length": sum(
                len(f.docstring) for f in self.documented_functions
            ),
            "functions_with_examples": sum(
                1 for f in self.documented_functions if f.examples
            )
        }
```

### File 2: agent.yml
```yaml
name: documentation-agent
version: 1.0.0
description: Auto-generate API docs, tutorials, and changelogs
author: Cognitive Brain Team
created: 2026-01-03

capabilities:
  - api_documentation_generation
  - tutorial_generation
  - changelog_automation
  - diagram_generation
  - documentation_versioning

integration:
  phase8_10:
    - DocumentationPortal
  phase8_11:
    - ExplainableAI

triggers:
  - pull_request
  - push:
      branches: [main, develop]
  - schedule: "0 0 * * *"  # Daily

config:
  random_seed: 48
  max_retries: 3
  timeout_seconds: 600
  min_docstring_length: 50
  generate_diagrams: true

metrics:
  - functions_documented
  - tutorials_generated
  - changelogs_created
  - doc_coverage_percent

performance_targets:
  doc_generation_time_s: 10
  coverage_target_pct: 90
```

### File 3: tests/test_documentation_agent.py (15+ tests)
```python
"""Tests for Documentation Agent"""
import pytest
from api_doc_generator import APIDocGenerator, FunctionDoc

RANDOM_SEED = 48

class TestAPIDocGenerator:
    def test_init(self):
        generator = APIDocGenerator(seed=RANDOM_SEED)
        assert generator.seed == RANDOM_SEED
    
    def test_extract_simple_function(self):
        code = '''
def hello(name):
    """Say hello"""
    return f"Hello {name}"
'''
        generator = APIDocGenerator(seed=RANDOM_SEED)
        docs = generator.extract_function_docs(code)
        assert len(docs) == 1
        assert docs[0].name == "hello"
    
    # Add 13 more tests...
```

## VALIDATION
Same as Agent 2

## SUCCESS CRITERIA
- All files compile
- 15+ tests
- Can generate API docs from sample code
- Markdown output valid
```

---

## 📊 Progress Tracking

### Implementation Checklist

- [x] Agent 1: Emergent Intelligence (34 tests) ✅
- [ ] Agent 2: Performance Monitor (15+ tests)
- [ ] Agent 3: Documentation (15+ tests)
- [ ] Agent 4: Self-Optimizing CI (20+ tests)
- [ ] Agent 5: Reasoning Advisor (20+ tests)
- [ ] Agent 6: Ecosystem Coordinator (20+ tests)
- [ ] Enhance: ci-testing-agent (10+ tests)
- [ ] Enhance: cognitive-brain-agent (15+ tests)
- [ ] Enhance: ast-analysis-agent (10+ tests)
- [ ] Enhance: security-scan-agent (10+ tests)

### Test Count Tracker

| Agent | Required | Completed | Status |
|-------|----------|-----------|--------|
| 1. Emergent Intelligence | 20+ | 34 | ✅ |
| 2. Performance Monitor | 15+ | 0 | ⏳ |
| 3. Documentation | 15+ | 0 | ⏳ |
| 4. Self-Optimizing CI | 20+ | 0 | ⏳ |
| 5. Reasoning Advisor | 20+ | 0 | ⏳ |
| 6. Ecosystem Coordinator | 20+ | 0 | ⏳ |
| **Total New Tests** | **110+** | **34** | **31%** |

---

*[Continued in next section for Agents 4-6 and enhancements]*
