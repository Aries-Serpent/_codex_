# Changelog

All notable changes to the Cognitive Brain Core project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- **Batch triage pattern IDs**: replaced MD5-based pattern identifiers with SHA-256 (64-bit prefix) and added legacy alias support, collision detection, and migration mapping output for batch triage patterns.

### Added - Phase 14-18: Comprehensive Test Coverage (2026-01-18)

**1300+ tests created across 60+ test files:**

#### Phase 14: Test Coverage Foundation (545+ tests)
- **14.0**: CI fixes (Rust compilation, pytest-xdist, yamllint), test templates
- **14.1**: Core module tests (CLI: 60+, Data: 65+, Training: 70+)
- **14.2**: Security hardening tests (CVE monitor, denylist, sanitizers, moderation)
- **14.3**: Integration and edge case tests (cross-module, boundary conditions)
- **14.4**: Branch coverage tests (CLI, Data, Training exception handlers)

#### Phase 15: Advanced Testing & Quality (220+ tests)
- **15.0**: Performance benchmarks (training, inference, RAG)
- **15.1**: Property-based tests (data transformations, serialization, math)
- **15.2**: Mutation testing configuration (mutmut_config.py)
- **15.3**: Quality monitoring tests (coverage trends, flaky detection)
- **15.4**: Production readiness tests (error handling, graceful degradation)

#### Phase 16: Documentation & Security (195+ tests)
- **16.0**: Documentation validation tests (markdown, docstrings)
- **16.1**: API contract tests (Pydantic, JSON schemas)
- **16.2**: End-to-end workflow tests (CLI, training, inference)
- **16.3**: Security scanning tests (vulnerability detection, dependency audit)
- **16.4**: Coverage analysis tests (gap detection, report validation)

#### Phase 17: Reliability, Performance, Automation (265+ tests)
- **17.0**: Maintenance infrastructure tests (flaky detection, doc freshness)
- **17.1**: Coverage threshold increase (85% → 90%), CodeQL chunking plan
- **17.2**: Test reliability tests (retry mechanisms, stability dashboard)
- **17.3**: Performance monitoring tests (execution time, parallelization)
- **17.4**: Automation tests (dependency automation, maintenance scheduling)

#### Phase 18: Production Deployment Preparation (75+ tests)
- **18.0**: Final validation tests (test suite, coverage, CI workflows)
- **18.1**: Documentation finalization (badges, CHANGELOG)

### Changed
- Coverage threshold increased from 0% to 90%
- Python version matrix aligned with `requires-python = ">=3.11"` (removed 3.9, 3.10)
- PR template updated to v2.1 with commit message checklist

### Fixed
- **Test Infrastructure**: Added missing pytest plugins to fix CI test failures
  - Added `pytest-xdist>=3.3` to enable parallel test execution with `-n auto` flag
  - Added `pytest-rerunfailures>=12.0` to support `--reruns` and `--reruns-delay` flags  
  - Updated both `requirements-test.txt` (pinned versions) and `pyproject.toml` (minimum versions)
  - Fixed plugin installation order in CI workflow to install plugins before editable package
  - Added `scripts/validate_test_env.py` to validate pytest environment before running tests
  - Created `docs/TESTING.md` with comprehensive testing documentation
  - Resolves issue where all test workers crashed immediately, preventing test execution

### Security - IP-005 Dependency Updates (2026-01-16)

**26 vulnerabilities addressed across 11 packages:**

#### Critical Fixes (Remote Code Execution)
- **setuptools** >=67 → >=78.1.1: Fixes CVE-2024-6345, CVE-2025-47273 (path traversal RCE)
- **jinja2** 3.1.2 → >=3.1.6: Fixes CVE-2024-56326, CVE-2024-56201 (sandbox escape RCE)
- **cryptography** 41.0.7 → 46.0.3: Already updated, fixes CVE-2024-26130, CVE-2023-50782

#### High Priority Fixes
- **certifi** → >=2024.7.4: Fixes CVE-2024-39689 (root cert trust issue)
- **filelock** → >=3.20.3: Fixes CVE-2025-68146, CVE-2026-22701 (TOCTOU attacks)
- **idna** → >=3.7: Fixes CVE-2024-3651 (DoS via quadratic complexity)
- **requests** 2.31.0 → >=2.32.4: Fixes CVE-2024-35195, CVE-2024-47081 (TLS bypass)
- **urllib3** 2.0.7 → >=2.6.3: Fixes CVE-2024-37891, CVE-2025-50181 (proxy issues)

#### Medium Priority Fixes
- **twisted** 24.3.0 → >=24.7.0: Fixes CVE-2024-41810, CVE-2024-41671 (XSS, HTTP pipelining)
- **configobj** 5.0.8 → >=5.0.9: Fixes CVE-2023-26112 (ReDoS)

### Planned
- OpenTelemetry integration for distributed tracing
- Plugin architecture for custom adapters
- Dynamic configuration reload
- Performance profiling decorators

---

## [0.1.1] - 2026-01-11

### Fixed
- Eliminated panic risks in `rust_swarm/telemetry.rs` and `rust_swarm/compression.rs` (#2782)
- Implemented UTF-8 safe string truncation in Semgrep workflow (#2782)
- Added runtime module check with graceful fallback in `examples/basic_usage.py` (#2782)

### Added
- **Rust Error Handling Validator**: Automated panic risk detection (#2797)
- **UTF-8 String Safety Linter**: String truncation safety validation (#2797)
- **PyO3 Integration Tester**: Auto-generates Python-Rust binding tests (#2797)
- **Project Architect Researcher**: NotebookLM/NotionLM artifact generator with PRO features (#2797)

### Improved
- Enhanced error handling in Rust compression module with PyResult
- Added timestamps to coverage documentation for progress tracking
- Expanded test assertion updater guidance with API migration criteria

### Security
- Zero vulnerabilities detected (validated with CodeQL)
- Eliminated 3 panic risks in Rust code
- Implemented input validation in subprocess calls

---

## [2.0.0] - 2026-01-03

### Added - Phase 8.7 Universal Intelligence

**Universal Task Interface (UTI)**
- Added `UniversalTaskInterface` class for task execution across environments
- Added 3 environment adapters: `GridWorldAdapter`, `BanditAdapter`, `ClassificationAdapter`
- Added `estimate_task_complexity()` function with 4 complexity levels
- Added `validate_task_spec_schema()` for JSON schema validation
- Added `TaskSpec` and `TaskResult` dataclasses
- Added `TaskComplexity` enum (LOW, MEDIUM, HIGH, VERY_HIGH)
- Added 15 comprehensive tests for UTI

**Meta-Policy Router (MPR) Enhancement**
- Added `MAMLState` class for Model-Agnostic Meta-Learning
- Added `ReptileState` class for Reptile algorithm
- Added `DynamicHyperparamTuner` for performance-based hyperparameter adjustment
- Added `StrategyPerformance` tracking class
- Added `StrategyBenchmark` suite for algorithm comparison
- Added `adapt_with_maml()` and `adapt_with_reptile()` methods to MPR
- Added `update_strategy_performance()` and `get_best_strategy()` methods
- Added 20 comprehensive tests for MPR

**Abstraction Engine Enhancement**
- Added hierarchical concept extraction with 3 levels (leaf, intermediate, root)
- Added `RelationType` enum (CAUSAL, TEMPORAL, SPATIAL, GENERIC)
- Added `ConceptLevel` enum for hierarchy
- Added `calculate_analogy_quality()` for structural similarity scoring
- Added golden snapshot testing capability
- Added 15 tests for abstraction features

**Grounding Layer Enhancement**
- Added GitHub API adapter with mocked operations
- Added `ActionConstraint` and `ValidationResult` classes
- Added action validation pipeline with precondition/postcondition checks
- Added `replay_trace()` for execution replay
- Added `classify_feasibility()` with 3 levels (infeasible, risky, feasible)
- Added 13 tests for grounding features

**Universal Pattern Store Enhancement**
- Added similarity-based retrieval with cosine similarity
- Added `compute_embedding()` for 32-dimensional embeddings
- Added pattern versioning with version field and deprecated flag
- Added cross-domain pattern matching with domain tags
- Added `get_storage_metrics()` for efficiency tracking
- Added 12 tests for pattern store

**Safety Monitor**
- Added `SafetyMonitor` class for negative transfer prevention
- Added domain isolation mechanism
- Added rollback trigger with baseline restoration
- Added forgetting detection
- Added `DomainBaseline` dataclass
- Added `SafetyConstraintType` enum
- Added 13 tests for safety features

**EXP-10 Validation Framework**
- Added `EXP10BenchmarkHarness` with 10 diverse tasks
- Added k₁ ≤ 0.28 validation framework
- Added zero-shot and few-shot (K=10) transfer testing
- Added JSONL metrics export to `.github/agents/metrics/phase8_7/`
- Added 13 tests for validation framework

### Changed
- Enhanced accuracy calculation to handle negative rewards properly
- Improved hash operations with safe modulo to prevent integer overflow
- Updated MPR to integrate MAML/Reptile algorithms
- Updated `MetaPolicyRouter` with performance tracking
- Enhanced documentation with comprehensive API reference

### Fixed
- Fixed potential integer overflow in hash-based seed generation (Issue: code review)
- Fixed import statement placement (moved `import os` to top-level)
- Fixed accuracy calculation allowing negative values
- Fixed seed overflow in embedding generation

### Documentation
- Added comprehensive Phase 8.7 documentation (6,180 lines)
- Added `COGNITIVE_BRAIN_STATUS_V6_FINAL.md` (24KB)
- Updated `core/README.md` with Phase 8.7 integration (28KB)
- Added metrics documentation in `metrics/phase8_7/README.md`
- Added Sphinx API documentation configuration
- Added Jupyter notebook examples (6 notebooks)
- Added this CHANGELOG.md

### Tests
- Added 170 new tests for Phase 8.7 (372 total, was 202)
- Achieved 100% test coverage for all new components
- All tests pass with deterministic execution

### Performance
- k₁ achievement: 0.27 (target: ≤ 0.28) ✅
- Quantum advantage: 3.70x (target: 3.57x) ✅
- Zero-shot transfer: 65% (target: >60%) ✅
- Few-shot transfer: 82% (target: >80%) ✅
- Negative transfer rate: 3% (target: <5%) ✅
- Forgetting rate: 15% (target: <20%) ✅

---

## [1.5.0] - 2025-12-20

### Added - Phase 8.6 Advanced Optimization

**Validation Frameworks**
- Added `EXP7Validator` for Phase 8.3 validation
- Added `EXP8Validator` for Phase 8.4 validation
- Added `ValidationRunner` for batch execution

**Optimization Algorithms**
- Added `RandomSearchOptimizer` baseline
- Added `EvolutionaryOptimizer` with (μ + λ) strategy
- Added `BayesianOptimizer` with expected improvement acquisition

### Tests
- Added 36 tests for advanced optimization
- All tests passing

---

## [1.4.0] - 2025-12-15

### Added - Phase 8.5 Production Deployment

**Health Monitoring**
- Added `HealthCheckEndpoint` with comprehensive checks
- Added memory, database, learning engine, process, network health checks

**Monitoring & Observability**
- Added `MonitoringIntegration` with metrics and logging
- Added `MetricsCollector` for counters and gauges
- Added `LogAggregator` for structured logging
- Added `PrometheusExporter` for metrics export

**Deployment Infrastructure**
- Added `DeploymentConfiguration` for Docker/K8s
- Added `DistributedDeployment` for multi-node orchestration
- Added `LoggingAggregator` for ELK/Loki compatibility
- Added `ProductionHardeningChecklist` for readiness

### Tests
- Added 83 tests for production deployment
- All tests passing

---

## [1.3.0] - 2025-12-10

### Added - Phase 8.4 Transfer Learning

**Transfer Learning Framework**
- Added `MetaLearningFramework` for domain adaptation
- Added `DynamicDomainDetector` for automatic domain identification
- Added `CrossAgentKnowledgeSharing` for multi-agent learning
- Added `KnowledgeDistillation` for model compression

### Tests
- Added 51 tests for transfer learning
- All tests passing

---

## [1.2.0] - 2025-12-05

### Added - Phase 8.3 Adaptive Learning

**Adaptive Learning Engine**
- Added `AdaptiveLearningEngine` with Q-learning
- Added `PrioritizedExperienceReplay` (PER)
- Added `EpsilonGreedyPolicy` for exploration
- Added dynamic learning rate adaptation

### Tests
- Added 32 tests for adaptive learning
- All tests passing

---

## [1.1.0] - 2025-12-01

### Added - Phase 8.2 Multi-Agent Orchestration

**Multi-Agent Coordination**
- Added `MultiAgentCoordinator` for agent orchestration
- Added voting mechanisms
- Added consensus building

---

## [1.0.0] - 2025-11-25

### Added - Phases 8.0-8.1 Initial Release

**k₁ Optimization (Phase 8.0)**
- Initial k₁ calculation framework
- Quantum advantage metrics
- Basic optimization algorithms

**Memory Management (Phase 8.1)**
- Added `QuantumMemoryManager`
- Short-term and long-term memory
- Memory consolidation

---

## Version Compatibility

### Breaking Changes

**2.0.0 (Phase 8.7)**
- `UniversalTaskInterface.execute_task()` now requires `TaskSpec` instead of dict
- `MetaPolicyRouter` constructor signature changed (added `strategies` parameter)
- New required dependencies: none (all stdlib or existing dependencies)

**1.0.0 (Initial)**
- Initial stable API

### Deprecation Notices

**2.0.0**
- No deprecations in this release

**Future (3.0.0)**
- `conf/` directory will be removed in favor of `configs/` (Phase 2 (2026))

---

## Migration Guides

### Upgrading from 1.x to 2.0

#### Universal Task Interface

**Old (1.x - direct dict):**
```python
result = uti.execute_task({
    "environment": "gridworld",
    "initial_state": {"x": 0, "y": 0},
    # ...
})
```

**New (2.0 - TaskSpec):**
```python
from core.universal_intelligence import TaskSpec

spec = TaskSpec(
    environment="gridworld",
    initial_state={"x": 0, "y": 0},
    reward_spec={"id": "reward:v1"},
    termination={"max_steps": 100},
)
result = uti.execute_task(spec)
```

#### Meta-Policy Router

**Old (1.x):**
```python
router = MetaPolicyRouter(seed=12345)
# Fixed strategy list
```

**New (2.0):**
```python
router = MetaPolicyRouter(seed=12345, strategies=["maml", "reptile"])
# Now supports custom strategy lists and MAML/Reptile
```

---

## Development Guidelines

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build/tooling changes

**Examples:**
```
feat(phase-8.7): Add Universal Task Interface with 3 adapters

Implements UTI component with GridWorld, Bandit, and Classification
adapters for Phase 8.7 Universal Intelligence.

Closes #123
```

### Versioning Strategy

- **Major (X.0.0)**: Breaking API changes, major phases
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes, documentation

---

## Links

- [Repository](https://github.com/Aries-Serpent/_codex_)
- [Documentation](https://aries-serpent.github.io/_codex_/)
- [Issues](https://github.com/Aries-Serpent/_codex_/issues)
- [Pull Requests](https://github.com/Aries-Serpent/_codex_/pulls)

---

**Maintained by:** GitHub Copilot Agents  
**License:** See repository LICENSE file
