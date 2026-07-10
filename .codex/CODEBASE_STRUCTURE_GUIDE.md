# 🗂️ CODEBASE STRUCTURE & ORGANIZATION GUIDE
**_codex_ Repository (Aries-Serpent/_codex_)**  
**Generated:** 2026-07-10T06:58Z

---

## 📋 TABLE OF CONTENTS

1. Directory Hierarchy (4-tier structure)
2. Module Organization (logical grouping)
3. Code Organization (file-level structure)
4. Dependency Relationships
5. API Boundaries & Integration Points
6. Configuration Management
7. Testing Organization

---

## 📁 DIRECTORY HIERARCHY (4-TIER STRUCTURE)

### TIER 1: PROJECT ROOT (Definition & Metadata)

```
_codex_/
├── README.md                      # Project overview & quick start
├── LICENSE                        # MIT License
├── CONTRIBUTING.md               # Contribution guidelines
├── .codex/archive/deprecated/AGENTS.md                      # AI agent documentation
├── pyproject.toml                # Python package definition (MAIN CONFIG)
├── setup.cfg                     # Legacy setuptools config
├── setup.py                      # Legacy build script
├── MANIFEST.in                   # Package data inclusion
├── requirements.txt              # Main dependencies
├── requirements-dev.txt          # Development dependencies
├── requirements-test.txt         # Testing dependencies
├── requirements-optional.txt     # Optional/extended features
├── pytest.ini                    # Pytest configuration
├── pyproject_core.toml           # Core profile build config
├── pyproject_cognitive.toml      # Cognitive brain build config
└── [48+ other config files]      # Various tool configs
```

**Key Files:**
- **pyproject.toml** - **CRITICAL**: Defines 3-profile strategy (core, runtime, full) with all dependencies organized by profile
- **pytest.ini** - Configures test discovery and markers
- **requirements-*.txt** - Dependency specifications organized by use case

---

### TIER 2: MAJOR SUBSYSTEMS

#### 2A: Source Code (`src/`)

```
src/
├── codex/                        # CORE ML PLATFORM (Main package)
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # **ENTRY POINT** - CLI commands (Typer)
│   ├── training/                # Training engine
│   │   ├── trainer.py           # Main trainer class
│   │   ├── optimizers.py        # Custom optimizers
│   │   ├── callbacks.py         # Training callbacks
│   │   └── ...
│   ├── evaluation/              # Evaluation engine
│   │   ├── evaluator.py         # Main evaluator class
│   │   ├── metrics.py           # Custom metrics
│   │   └── ...
│   ├── serving/                 # Model serving
│   │   ├── ray_serve_app.py     # Ray Serve integration
│   │   ├── fastapi_app.py       # FastAPI endpoints
│   │   └── ...
│   ├── config/                  # Configuration schemas
│   │   ├── training_config.py   # Training config
│   │   ├── base_config.py       # Base schemas
│   │   └── ...
│   ├── logging/                 # Session logging
│   │   ├── session_logger.py    # SQLite session tracking
│   │   └── ...
│   └── utils/                   # Utility functions
│
├── cognitive_brain/             # COGNITIVE BRAIN SYSTEM (46 modules)
│   ├── __init__.py              # Package init + OODA exports
│   ├── base.py                  # **CORE** - OODA loop (268 LOC)
│   ├── meta_cognitive_reflection.py  # Self-awareness (504 LOC)
│   ├── rhizome_connector.py     # Agent communication (365 LOC)
│   │
│   ├── quantum/                 # Quantum decision engine
│   │   ├── topology_manager.py  # Decision topology
│   │   ├── memory.py            # Quantum memory states
│   │   └── __init__.py
│   │
│   ├── memory/                  # STM/LTM system
│   │   ├── stm.py              # Short-term memory
│   │   ├── ltm.py              # Long-term memory
│   │   └── ...
│   │
│   ├── learning/                # RL & optimization
│   │   ├── rl_algorithms.py    # Reinforcement learning
│   │   ├── strategy_optimizer.py
│   │   ├── outcome_analyzer.py
│   │   └── __init__.py
│   │
│   ├── analytics/               # Analytics & decision support
│   │   ├── bayesian.py         # Bayesian analysis
│   │   ├── fuzzy.py            # Fuzzy logic
│   │   └── __init__.py
│   │
│   ├── models/                  # Data models
│   │   ├── learning_outcome.py
│   │   ├── quantum_metrics.py
│   │   └── __init__.py
│   │
│   ├── integrations/            # External system bridges
│   │   ├── memory_integration.py
│   │   ├── compliance_integration.py
│   │   ├── entangled_assessor.py
│   │   └── __init__.py
│   │
│   └── utils/                   # CB utilities
│       ├── pattern_validators.py
│       └── __init__.py
│
├── cli/                         # **CLI INTERFACE** (alternative to codex.cli)
│   ├── __init__.py
│   ├── commands/                # Command definitions
│   │   ├── train_command.py
│   │   ├── eval_command.py
│   │   └── serve_command.py
│   └── ...
│
└── plugins/                     # Extension system
    ├── __init__.py
    └── [user-defined plugins]
```

**Organization Principles:**
- Each major subsystem is a separate module (clear boundaries)
- CLI entry point: `src/codex/cli.py`
- Cognitive brain is self-contained in `src/cognitive_brain/`
- Configuration schemas colocated with usage (in `src/codex/config/`)

#### 2B: Tests (`tests/`)

```
tests/
├── conftest.py                  # Pytest fixtures & configuration
├── __init__.py
│
├── unit/                        # Unit tests (~1500 tests)
│   ├── test_training.py
│   ├── test_evaluation.py
│   ├── test_serving.py
│   ├── test_cli.py
│   ├── cognitive/               # Cognitive brain unit tests
│   │   ├── test_ooda_engine.py
│   │   ├── test_quantum_metrics.py
│   │   ├── test_memory.py
│   │   └── ...
│   └── ...
│
├── integration/                 # Integration tests (~800 tests)
│   ├── test_training_pipeline.py
│   ├── test_training_serving.py
│   ├── test_cognitive_agents.py
│   └── ...
│
├── e2e/                         # End-to-end tests (~400 tests)
│   ├── test_complete_workflow.py
│   ├── test_distributed_training.py
│   └── ...
│
├── ml/                          # ML-specific tests (~84 tests, stabilized)
│   ├── conftest.py             # ML-specific fixtures
│   ├── test_edge_cases_phase2.py
│   └── ...
│
└── fixtures/                    # Test data & mocks
    ├── sample_models/
    ├── sample_datasets/
    └── mock_data.py
```

**Test Coverage:**
- 2784 test files total
- 70%+ coverage across codebase
- Tests organized by type (unit/integration/e2e)
- ML tests have special stabilization (seed_control, threading barriers)

#### 2C: Scripts & Automation (`scripts/`)

```
scripts/
├── ci/                          # CI/CD helpers
│   ├── enforce_actions_versions.py    # GitHub Actions version enforcement
│   ├── auto_fix_common_issues.py      # Automated fixes (8 patterns)
│   ├── session_wrapup_autofix.py      # Session completion checks
│   ├── check_windows_filenames.py     # Cross-platform validation
│   └── ...
│
├── cognitive/                   # Cognitive brain utilities (22 files)
│   ├── agent_orchestrator.py
│   ├── decision_engine.py
│   ├── memory_manager.py
│   └── ...
│
├── security/                    # Security procedures
│   ├── establish_scan_baseline.sh
│   ├── track_cves.py
│   ├── sign_artifacts.py
│   └── ...
│
├── deployment/                  # Deployment helpers
│   ├── build_profiles.sh
│   ├── create_sbom.py
│   ├── validate_isolation.sh
│   └── ...
│
└── remediation/                 # Issue fixing
    ├── fix_imports.py
    ├── fix_type_errors.py
    └── ...
```

#### 2D: Metadata & Configuration (`.codex/`, `.github/`, `docs/`)

```
.codex/                         # Campaign metadata & reports
├── agent_context.json          # Repository variables snapshot
├── *.md                        # Campaign reports and plans
├── *.json                      # Configuration & metrics
└── aftermath/                  # PDA loop history

.github/
├── workflows/                  # 126 active GitHub Actions
│   ├── ci.yml
│   ├── testing.yml
│   ├── release.yml
│   └── ... (123 more)
│
├── agents/                     # 145 agent definitions
│   ├── AGENT_REGISTRY.yaml     # **AGENT REGISTRY** - source of truth
│   ├── unified-coverage-agent.md
│   ├── ci-auto-healer-agent.md
│   └── ... (142 more)
│
├── instructions/               # Coding standards
│   ├── python.instructions.md
│   ├── workflows.instructions.md
│   └── ...
│
└── ...

docs/                           # Documentation (93+ KB)
├── README.md
├── .codex/archive/misc/INSTALL.md
├── CLI_REFERENCE.md
├── ARCHITECTURE.md
├── COGNITIVE_BRAIN_GUIDE.md
├── SECURITY.md
├── DISTRIBUTED_TRAINING.md
├── MODEL_SERVING.md
├── PYTHON_INGESTION.md
└── ... (50+ more docs)
```

#### 2E: Docker & Containers

```
docker/
├── Dockerfile                  # Multi-stage production image
├── Dockerfile.dev             # Development image
├── docker-compose.yml         # Local development setup
├── .dockerignore              # Docker build optimization
└── images/                    # Pre-built image configs
    ├── core.dockerfile       # Core profile image
    ├── runtime.dockerfile    # Runtime profile image
    └── full.dockerfile       # Full profile image
```

#### 2F: Infrastructure

```
infrastructure/
├── k8s/                       # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── statefulset.yaml
│   └── ...
│
├── terraform/                # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   └── ...
│
└── ops/                       # Operational scripts
    ├── monitoring/
    ├── alerting/
    └── logging/
```

---

### TIER 3: MODULE GROUPS (Logical Organization)

#### Core ML Platform Group
**Directory:** `src/codex/`  
**Modules:** training, evaluation, serving, config, logging, utils  
**Purpose:** End-to-end ML workflow support

```
CLI → Training → Evaluation → Serving
  ↓        ↓          ↓         ↓
Config  PyTorch   lm-eval   Ray Serve
```

#### Cognitive Brain Group
**Directory:** `src/cognitive_brain/`  
**Modules:** 46 modules across 7 subsystems  
**Purpose:** Autonomous decision-making and agent orchestration

```
Observation → Orientation → Decision → Action
     ↓            ↓           ↓         ↓
   Sensors   Analysis    Quantum    Agents
                        Metrics
```

#### Python Ingestion Pipeline
**Modules:** Code analysis, transformation, verification  
**Purpose:** Automated Python code analysis and enhancement

```
Code Input → Analysis → Transformation → Verification → Output
  (file/ZIP)  (AST)   (Tier A/B/C)     (testing)     (enhanced)
```

#### Infrastructure Group
**Modules:** Logging, security, CI/CD, integrations  
**Purpose:** System support and external connectivity

```
GitHub → MLflow → Hugging Face → Cloud Storage
  ↓        ↓           ↓             ↓
Actions Tracking    Models       Data/Artifacts
```

---

### TIER 4: Individual Components (Code Level)

#### Example: Training Module
```python
# src/codex/training/trainer.py

class Trainer:
    """Main training orchestrator."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = self._build_model()
        self.optimizer = self._build_optimizer()
        self.callbacks = [...]
    
    def train(self, train_dataloader, val_dataloader):
        """Execute distributed training loop."""
        for epoch in range(self.config.num_epochs):
            for batch in train_dataloader:
                loss = self._train_step(batch)
                self.log_metrics({"loss": loss})
        
        self.save_checkpoint()
    
    def _train_step(self, batch):
        """Single training step."""
        outputs = self.model(batch)
        loss = self.criterion(outputs, batch.labels)
        loss.backward()
        self.optimizer.step()
        return loss.item()
```

#### Example: OODA Engine
```python
# src/cognitive_brain/base.py

class OODAEngine:
    """Core OODA loop (Observe → Orient → Decide → Act)."""
    
    async def process(self, observation: ObservationData) -> Decision:
        """Execute full OODA cycle."""
        
        # 1. OBSERVE: Collect sensor data
        sensor_data = observation.sensors
        
        # 2. ORIENT: Analyze context
        context = self.memory.get_context()
        situation_model = self._build_situation(sensor_data, context)
        
        # 3. DECIDE: Quantum probability calculation
        decision = self._decide(situation_model)
        
        # 4. ACT: Delegate to agent
        agent = self._select_agent(decision)
        action = await agent.execute(decision)
        
        # Update memory with outcome
        self.memory.record(observation, decision, action)
        
        return action
    
    def _decide(self, situation_model) -> Decision:
        """Calculate decision using quantum metrics."""
        k1 = 0.35  # Capability weight
        score = k1 * capability_match + (1-k1) * success_rate
        return Decision(agent_id=best_agent, score=score)
```

---

## 🔗 DEPENDENCY RELATIONSHIPS

### Direct Dependencies (Imported by Multiple Modules)

```
TIER 1 (Core Foundation - All others depend):
  ├─ pydantic (validation)
  ├─ omegaconf (configuration)
  ├─ pyyaml (config parsing)
  ├─ cryptography (security)
  └─ stdlib (dataclasses, json, etc.)

TIER 2 (ML Foundation):
  ├─ torch (PyTorch models)
  ├─ transformers (HuggingFace models)
  ├─ datasets (data loading)
  ├─ accelerate (distributed training)
  └─ ray (orchestration)

TIER 3 (Application Services):
  ├─ fastapi (REST APIs)
  ├─ typer (CLI framework)
  ├─ sqlalchemy (ORM, optional)
  └─ logging (SQLite sessions)

TIER 4 (Optional/Extended):
  ├─ mlflow (experiment tracking)
  ├─ plotly (visualization)
  ├─ jupyter (notebooks)
  ├─ pytest (testing)
  └─ mypy (type checking)
```

### Module Dependencies (Within _codex_)

```
codex.cli
  ├─ codex.training.*
  ├─ codex.evaluation.*
  ├─ codex.serving.*
  └─ codex.config.*

codex.training.*
  ├─ codex.config
  └─ codex.logging

cognitive_brain.base
  ├─ cognitive_brain.memory
  ├─ cognitive_brain.quantum
  ├─ cognitive_brain.analytics
  └─ cognitive_brain.integrations.*

cognitive_brain.integrations.*
  ├─ codex.logging
  └─ cognitive_brain.memory
```

---

## 📊 API BOUNDARIES & INTEGRATION POINTS

### External API Boundary (Outside → _codex_)

```
External System             Connection Point       Integration Type
─────────────────           ────────────────       ────────────────
Hugging Face Hub    ←→      transformers.py       Model downloads
PyTorch Hub         ←→      training/trainer.py   Model initialization
MLflow              ←→      logging/session_*.py  Experiment tracking
GitHub API          ←→      scripts/ci/*.py       PR automation
Ray Cluster         ←→      serving/ray_app.py    Distributed execution
Cloud Storage       ←→      config/paths.py       Data I/O
```

### Internal API Boundary (Module → Module)

```
CLI Interface (typer-based):
  cli.py → train_command.py → Trainer → PyTorch

Configuration Interface (Hydra-based):
  Trainer.__init__(config: TrainingConfig)
  Evaluator.__init__(config: EvaluationConfig)
  Serve.__init__(config: ServingConfig)

OODA Loop Interface (async-based):
  OODAEngine.process(observation) → Decision → Agent.execute()

Logging Interface (synchronous):
  session_logger.log(event_type, data)
  session_logger.query(filters)
```

---

## ⚙️ CONFIGURATION MANAGEMENT

### Configuration Hierarchy (Hydra)

```
defaults/              # Base configs
├── config.yaml        # Global defaults
├── trainer/
│   ├── default.yaml
│   ├── distributed.yaml
│   └── finetuning.yaml
├── evaluator/
│   ├── default.yaml
│   └── comprehensive.yaml
├── model/
│   ├── bert.yaml
│   ├── gpt2.yaml
│   └── custom.yaml
└── dataset/
    ├── default.yaml
    └── large.yaml

Output Composition Example:
$ python -m codex.cli train \
  --config-name=defaults \
  trainer=distributed \
  model=bert \
  dataset=large
  
Result: Merges:
  defaults/config.yaml
  + defaults/trainer/distributed.yaml
  + defaults/model/bert.yaml
  + defaults/dataset/large.yaml
```

### Environment Configuration

```
# .env (local development)
HYDRA_RUN_DIR=./runs
CODEX_ENV_PYTHON_VERSION=3.12
CODEX_SESSION_LOG_DIR=.codex/sessions
CODEX_LOG_DB_PATH=.codex/session_logs.db

# CI/CD (GitHub Actions environment variables)
COPILOT_AGENT_CCA_VERSION_LOCK=stable
COPILOT_AGENT_DEDUPLICATION_ENABLED=true
CODEX_MASTER_KEY=*** (secrets)
```

---

## 🧪 TESTING ORGANIZATION

### Test Discovery Pattern

```
# Pytest discovers tests by pattern:
tests/
  unit/test_*.py        → unit tests (fast, isolated)
  integration/test_*.py → integration tests (medium, connected)
  e2e/test_*.py         → e2e tests (slow, full workflows)
  ml/test_*.py          → ML tests (with special fixtures)

# Execution:
$ pytest tests/unit              # ~30 seconds (1500 tests)
$ pytest tests/integration       # ~5 minutes (800 tests)
$ pytest tests/e2e              # ~10 minutes (400 tests)
$ pytest tests/ml               # ~3 minutes (84 tests)
```

### Test Organization by Feature

```
Training Tests:
  tests/unit/test_training.py         → Trainer class, optimizers
  tests/integration/test_training_*.py → Full training pipelines
  tests/e2e/test_complete_workflow.py  → End-to-end workflow

Cognitive Brain Tests:
  tests/unit/cognitive/test_ooda_engine.py
  tests/unit/cognitive/test_quantum_metrics.py
  tests/unit/cognitive/test_memory.py
  tests/integration/test_cognitive_agents.py

CLI Tests:
  tests/unit/test_cli.py → Command parsing, defaults
  tests/integration/test_cli_workflows.py → Full commands
```

### Fixtures & Mocks

```
# tests/conftest.py (shared fixtures)
@pytest.fixture
def sample_model():
    """Mock model for testing."""
    return MockModel()

@pytest.fixture
def training_config():
    """Sample training configuration."""
    return TrainingConfig(epochs=2, batch_size=32)

@pytest.fixture
def temporary_run_dir(tmp_path):
    """Temporary directory for run outputs."""
    return tmp_path / "runs"

# Usage in tests:
def test_training(sample_model, training_config, temporary_run_dir):
    trainer = Trainer(training_config)
    trainer.train(sample_model, temporary_run_dir)
```

---

## 🎯 KEY INSIGHTS

1. **Clear Separation of Concerns**
   - ML platform (src/codex/) handles training/evaluation/serving
   - Cognitive brain (src/cognitive_brain/) handles decision-making
   - CLI orchestrates everything (src/codex/cli.py)

2. **Hierarchical Configuration (Hydra)**
   - Compose configs from base + overrides
   - YAML-based, environment-friendly
   - Enables reproducible experiments

3. **Comprehensive Testing**
   - 2784 tests across 4 categories
   - Unit tests for individual components
   - Integration tests for workflows
   - E2E tests for complete scenarios
   - ML tests with stabilization measures

4. **Modular Cognitive Brain**
   - 46 modules organized by function
   - Clear OODA loop interface
   - Quantum decision metrics
   - 145-agent orchestration
   - Isolated from ML core

5. **Security First**
   - 26 CVEs fixed
   - Secret detection baseline
   - SBOM generation
   - Cryptographic signing
   - Network isolation ready

---

## ✅ NEXT STEPS

1. Review Lane 1-5 detailed reports (pending completion)
2. Examine `.codex/SECURITY_ISOLATION_LANE4.md` (complete)
3. Review `.codex/REPOSITORY_EXPLAINED.md` (this document)
4. Prepare for packaging specification aggregation

**Campaign Status:** 25% complete (Lane 4/5 done, Lanes 1-3 running)  
**Next Update:** When remaining lanes complete
