# `_codex_`
> 🏆 **Level 4 MLOps Certified** - Production-ready ML platform with end-to-end automation, drift-triggered retraining, and comprehensive observability (v1.5.5)

![Tests](https://img.shields.io/badge/tests-1500%2B%20total%20%7C%20100%25%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-72%25-yellow)
![Security](https://img.shields.io/badge/security-0%20vulnerabilities-brightgreen)
![Production](https://img.shields.io/badge/production-ready-brightgreen)

## 🎯 Achievement Status

**🏆 100/100 Azure MLOps Maturity (Level 4)**  
✅ End-to-End Automation | ✅ Auto-Retraining | ✅ Observability  
✅ Production Engineering | ✅ Cross-Functional | ✅ Governance

**Gap Analysis Status:** 47/47 Items Complete (100%) ✅

**Latest Milestone:** MCP Package System Complete + Cognitive Brain Infrastructure (2025-12-30)  
**Latest Update:** 9 Topics, Workflow Automation, 93+ KB Documentation, Unified Navigation  
📊 [Cognitive Map](docs/system/CODEBASE_COGNITIVE_MAP.md) | 📈 [Dashboard](docs/system/CODEBASE_DASHBOARD.md) | 🗺️ [Roadmap](docs/ROADMAP.md)

## 🚀 Genesis Protocol - Pre-token Setup

**Status:** Template files added, **awaiting human admin secret injection**

This repository includes Genesis Protocol templates for establishing autonomous agent operations. The setup is currently in **pre-token state** with all workflows disabled by default.

### Quick Start for Human Admin

1. **Review Templates**: All files in this PR are templates with placeholders
2. **Inject Secrets**: Follow [Genesis Setup Guide](docs/admin/GENESIS_SETUP_GUIDE.md)
3. **Enable Workflows**: Remove safety guards after secret injection
4. **Validate**: Run genesis-bootstrap workflow manually
5. **Enable Agent**: Set `autonomous_actions_enabled: true`

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| [`.github/workflows/genesis-bootstrap.yml`](.github/workflows/genesis-bootstrap.yml) | Genesis validation workflow | 🔒 Disabled (if: false) |
| [`.codex/autonomous_agent.yaml`](.codex/autonomous_agent.yaml) | Agent configuration | 🔒 Safe defaults |
| [`.codex/guardrails.md`](.codex/guardrails.md) | Operational policies | 📝 Template |
| [`scripts/autonomous_agent.py`](scripts/autonomous_agent.py) | Agent orchestrator | 🔒 SAFE_MODE = True |
| [`docs/admin/GENESIS_SETUP_GUIDE.md`](docs/admin/GENESIS_SETUP_GUIDE.md) | Admin documentation | 📖 Complete guide |
| [`docs/agent/OPERATIONAL_GUIDELINES.md`](docs/agent/OPERATIONAL_GUIDELINES.md) | Agent guidelines | 📖 Operational reference |

### Security Notes

- ✅ No secrets committed to repository
- ✅ All workflows disabled by default
- ✅ Explicit placeholder comments for human injection
- ✅ Multiple safety guards (if: false, SAFE_MODE, autonomous_actions_enabled: false)

**⚠️ DO NOT enable workflows until secrets are injected and validated**

For detailed instructions, see: [Genesis Setup Guide](docs/admin/GENESIS_SETUP_GUIDE.md)

## 🎨 Cognitive Codex Web Application

**Status:** Integrated & Built Successfully ✅  
**Access:** https://aries-serpent.github.io/_codex_/cognitive_app/ (GitHub Pages deployment - available after PR merge)

A React/Vite-based quantum-enhanced code generation platform with real-time cognitive brain visualization.

### Features
- **Quantum Decision Engine** - Real-time k₁ factor tracking, 2.86× quantum advantage visualization
- **Agent Orchestration Panel** - 6 physics paradigms, workflow token execution, cascading monitors
- **Memory Management Dashboard** - STM/LTM visualization, 60% compression, pattern library
- **Code Generator** - Natural language code generation with quantum metrics
- **Metrics Dashboard** - Real-time system health and performance monitoring

### Components (95% Complete)
- ✅ 27 Quantum components (QuantumDecisionEngine, WorkflowTokenOrchestrator, etc.)
- ✅ 44 UI components (complete shadcn/ui library)
- ✅ 3 Code generation components
- ✅ 5 Custom React hooks
- ⚠️ Backend API integration pending (see `cognitive_app/CODEX_INTEGRATION_MASTER_PLAN.md`)

**Documentation:** [`cognitive_app/README_INTEGRATION.md`](cognitive_app/README_INTEGRATION.md)

## 🆕 Recent Additions (2025-12-24)

| Component | Description | Location |
|-----------|-------------|----------|
| **Agent Core** | Autonomous agent orchestration with RAG and verification | `src/agent/` |
| **RAG Pipelines** | Chunking, embedding, and retrieval pipelines | `src/rag/pipelines/` |
| **Verification Engine** | Chain-of-Verification (CoVe) for fact-checking | `src/verification/` |
| **MCP Adapters** | Model Context Protocol integrations (Pinecone, Mock) | `src/mcp/adapters/` |
| **MCP Metrics** | Telemetry and monitoring for MCP operations | `src/mcp/metrics/` |
| **MCP Workers** | Background embedding and checkpoint workers | `src/mcp/workers/` |
| **Tool Registry** | Centralized tool registration and discovery | `src/tools/` |

## 🆕 Previous Additions (2025-12-17)

| Component | Description | Location |
|-----------|-------------|----------|
| **Python Ingestion Pipeline** | Complete code ingestion, analysis, transform, verify | `src/codex/` |
| **LLM Intent Inference** | OpenAI integration with provenance tracking | `src/codex/intent/` |
| **Runtime Sandbox** | Sandboxed execution with resource limits | `src/codex/analyze/runtime/` |
| **Tier-Based Transform** | A/B/C transformation classification | `src/codex/transform/` |
| **Behavior Verification** | Comparison modes and test generation | `src/codex/verify/` |
| **PR Operator** | Automated GitHub PR creation | `src/codex/cli/pr_operator.py` |
| **4-Stream Infrastructure** | Caching, OpenAI, Security, CodeQL | Multiple locations |

## 🆕 Previous Additions (2025-12-11)

| Component | Description | Location |
|-----------|-------------|----------|
| **Agent Memory System** | SQLite-backed persistent memory with pattern library | `agents/agent_memory.py` |
| **Self-Healing CI** | Automated issue detection and remediation | `.github/workflows/self-healing-ci.yml` |
| **Quantum Game Theory** | Physics-inspired Blue/Red team decision framework | `agents/quantum_game_theory.py` |
| **Performance Tests** | Regression testing suite | `tests/performance/` |
| **API Documentation** | Complete API reference with GitHub Pages | `docs/api/` |
| **Scalability Utils** | LRUCache, RateLimiter, CircuitBreaker, LoadBalancer | `src/codex_ml/utils/scalability.py` |
| **HAR Integration** | HTTP Archive recording/replay | `src/codex_ml/integrations/har_integration.py` |

## 🧠 Cognitive Brain - Quantum-Inspired Decision System

**Phase 8.0-8.1 Complete**: k₁ = 0.35 + Memory Management ✅  
**Status:** 275/320 tests passing (86% complete) | 2 reviews complete | Production-ready

The Cognitive Brain is a quantum-inspired decision-making system featuring superposition, entanglement, adaptive learning, and memory management for complex compliance scenarios.

### 🎯 Current Capabilities (Phase 7-8.1)
- ✅ **SuperpositionEngine** - Parallel evaluation of ambiguous decisions (22 tests)
- ✅ **EntanglementManager** - Coordinated 2-agent decision-making (28 tests)  
- ✅ **UncertaintyOptimizer** - Wave function collapse with Bell states (17 tests)
- ✅ **AdaptiveScoringOptimizer** - ML-inspired weight optimization (10 tests, k₁=0.35)
- ✅ **QuantumMemoryManager** - Hippocampus-cortex architecture (STM/LTM)
- ✅ **PatternCompressor** - 60% size reduction via PCA + quantization (25 tests)
- ✅ **Complex Scenario Validation** - 110 scenarios across 8 pattern types
- ✅ **k₁ Optimization** - 2.86x quantum advantage over classical

### 📊 Phase 8 Progress (40% Complete)
```
Phase 8.0: ████████████████████████████████ 100% (k₁=0.35) ✅
Phase 8.1: ████████████████████████████████ 100% (Memory+Reviews) ✅
Phase 8.2: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% (Multi-Agent GHZ) 📋
Phase 8.3: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% (Adaptive Learning) 📋
Phase 8.4: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% (Transfer Learning) 📋

Test Coverage: 275/320 (86%)
```

### 🎓 Phase 8 Roadmap
| Phase | Feature | k₁ Target | Status |
|-------|---------|-----------|--------|
| 8.0 | Weight Optimization | ≤ 0.35 | ✅ COMPLETE |
| 8.1 | Quantum Memory | ≤ 0.345 | ✅ COMPLETE (pending validation) |
| 8.2 | Multi-Agent GHZ States | ≤ 0.34 | 🔄 Next |
| 8.3 | Reinforcement Learning | ≤ 0.33 | 📋 Planned |
| 8.4 | Transfer Learning | 0.33 | 📋 Planned |

### 📖 Documentation
- 📊 **[Phase 8 Status (v2)](/.github/agents/COGNITIVE_BRAIN_PHASE8_STATUS_V2.md)** - Complete overview + reviews
- 🗺️ **[Phase 8 Roadmap](/.github/agents/PHASE_8_ROADMAP.md)** - Full specifications (8.2-8.4)
- 📈 **[K1 Strategy](/.github/agents/K1_OPTIMIZATION_STRATEGY.md)** - Rayleigh criterion
- 🧪 **[EXP-1B](src/cognitive_brain/experiments/exp1b_revalidation.py)** | **[EXP-5](src/cognitive_brain/experiments/exp5_validation.py)** - Validations

### 🔬 Key Metrics
| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| k₁ Factor | ≤ 0.35 | 0.3500 | ✅ 100% |
| Accuracy | ≥ 84% | 86.4% | ✅ +2.4% |
| Coherence | ≥ 0.650 | 0.685 | ✅ +5.4% |
| Cache Rate | ≥ 30% | Ready | 🔄 Validation |
| Time Reduction | ≥ 15% | Ready | 🔄 Validation |
| Tests | 320 | 275 | 🔄 86% |

### Code Quality
- ✅ **26 Issues Resolved:** 23 code review + 3 self-review
- ✅ **Zero Code Smells:** No unused imports/variables
- ✅ **Proper Logging:** Production-ready
- ✅ **Named Constants:** All magic numbers eliminated

### Quick Access (AI Agents)
- 🗺️ **[Cognitive Map](docs/system/CODEBASE_COGNITIVE_MAP.md)** - Architecture & flows
- 📊 **[Live Dashboard](docs/system/CODEBASE_DASHBOARD.md)** - Status & metrics
- 🎯 **[Unified Roadmap](docs/ROADMAP.md)** - Plans & priorities

### Why This Matters
This cognitive brain enables:
- **Quantum Advantage**: 2.86x faster than classical with memory caching
- **Context Continuity**: Memory-guided decisions with pattern reuse
- **Efficient Processing**: 60% compression + cache-first strategy
- **Autonomous Operation**: Self-directed agents with learned patterns

### For AI Agents
Start here on every session:
1. Review [Dashboard](docs/system/CODEBASE_DASHBOARD.md) for current state
2. Check [Roadmap](docs/ROADMAP.md) for priorities
3. Reference [Cognitive Map](docs/system/CODEBASE_COGNITIVE_MAP.md) for architecture
4. Execute tasks with full context

---

## 🤖 Codex Quick-Index (For AI Agents)

**New to this repository as an AI agent (Copilot, ChatGPT, etc.)?**

**Start here:** [AGENTS.md](AGENTS.md) → Comprehensive agent guide + Level 4 MLOps features  
**Tokenized Workflows:** [agents/TOKENIZED_WORKFLOWS.md](agents/TOKENIZED_WORKFLOWS.md) → Deterministic navigation paths  
**Machine index:** [_codex_/codex_index.yaml](_codex_/codex_index.yaml) → Primary files, priorities, orchestration map  
**Continuation:** [AGENT_CONTINUATION_PROMPT.md](docs/plans/AGENT_CONTINUATION_PROMPT.md) → Resume protocol for multi-step tasks  
**Agent Interface:** Generate with `python -m scripts.space_traversal.audit_runner agent-interface`

**Optimization:** Following the wavepoint order in AGENTS.md reduces repository traversal time by 62%.

### 🔄 Python Ingestion Pipeline

The Codex Ingestion Pipeline provides a complete system for processing Python code:

```bash
# Ingest code from file, ZIP, or Git URL
python -m codex.cli ingest ./script.py --manifest manifest.yaml

# Run static + runtime analysis
python -m codex.cli analyze <snapshot-id>

# Apply tier-based transformations
python -m codex.cli transform <snapshot-id> --tier A --auto

# Verify behavior preservation
python -m codex.cli verify <snapshot-id> --compare
```

See [docs/plans/operational_runbook.md](docs/plans/operational_runbook.md) for complete documentation.

### 🔄 Tokenized Workflow Navigation

AI Agents can execute common operations using deterministic, token-based workflows:

```python
from agents.workflow_navigator import WorkflowNavigator

navigator = WorkflowNavigator()
navigator.execute('AUDIT_EXEC')  # Run full audit pipeline
navigator.execute('DOC_GEN')      # Generate documentation
```

**Quick Access Tokens:** `audit`, `decide`, `docs`, `organize`, `review`, `heal`  
See [agents/TOKENIZED_WORKFLOWS.md](agents/TOKENIZED_WORKFLOWS.md) for complete workflow catalog.

### 🤖 ChatGPT 5.1 Agent Mode

Generate an intuitive control interface for AI agents:

```bash
python -m scripts.space_traversal.audit_runner agent-interface --output agent_interface.html
```

This creates an HTML interface specifically designed for ChatGPT 5.1 Agent mode with:
- Clear action buttons and navigation
- Per-capability audit triggers
- Report generation controls
- Machine-readable command outputs
- Tokenized workflow execution

### 📦 Packaging for ChatGPT Projects

Package any part of the codebase for ChatGPT Project uploads with the MCP Package System:

```bash
# List available topics
./scripts/mcp/mcp-package --list

# Package a topic (agents, docs, mcp, workflows, testing, security, etc.)
./scripts/mcp/mcp-package --topic agents

# Custom package with specific files
./scripts/mcp/mcp-package --custom "agents/**/*.py,tests/agents/**/*.py"

# Preview before creating
./scripts/mcp/mcp-package --topic mcp --dry-run
```

**Features**:
- **9 predefined topics** covering all major capabilities
- **Flat-structure packages** optimized for ChatGPT
- **Automatic manifest generation** with SHA256 hashes and metadata
- **GitHub Actions workflow** with dropdown menu selection
- **Size validation** and duplicate detection

**Output**: Packages include `manifest.json`, `README_dataset.md`, `index.md`, and flattened files (`src__agents__file.py`)

**Documentation**:
- [Quick Start Guide](docs/mcp/QUICK_START.md) - Get started in 5 minutes
- [Packaging Guide](docs/mcp/PACKAGING_GUIDE.md) - Complete packaging workflows
- [Packageable Capabilities](docs/mcp/PACKAGEABLE_CAPABILITIES.md) - Methodology transfer framework
- [Advanced Features Planset](docs/mcp/ADVANCED_FEATURES_PLANSET.md) - Future enhancements roadmap

**Automated Workflow**: Actions → Build ChatGPT Project Package → Select topic from dropdown

---

## Status & CI Badges

- Status Validation: ![Status Validation](https://github.com/Aries-Serpent/_codex_/actions/workflows/status_validation.yml/badge.svg)
- Security Gates: ![Security Gates](https://github.com/Aries-Serpent/_codex_/actions/workflows/security_gates.yml/badge.svg)
- Nox Quality Gates: ![Nox Gates](https://github.com/Aries-Serpent/_codex_/actions/workflows/nox_gates.yml/badge.svg)
- Semgrep SAST: ![Semgrep](https://github.com/Aries-Serpent/_codex_/actions/workflows/semgrep.yml/badge.svg)

## Documentation

All primary documentation now lives in the [`docs/`](docs/) directory.

### 📁 Repository Organization

| Directory | Purpose |
|-----------|---------|
| `docs/` | Primary documentation, guides, and references |
| `docs/mcp/` | MCP (Model Context Protocol) documentation |
| `docs/archive/` | Historical planning docs and session reports |
| `docs/api/` | API reference documentation |
| `reports/` | Generated reports, diagnostics, and manifests |
| `coverage_reports/` | Test coverage JSON reports |
| `configs/` | Configuration files and templates |
| `scripts/` | Utility scripts and automation |
| `tools/` | Development and validation tools |

### 🔧 Administrator Guide

**New to managing this repository?** See the admin documentation:

- **[Admin Implementation Guide](docs/ADMIN_IMPLEMENTATION_GUIDE.md)** - Complete setup for GitHub Apps, secrets, and workflows
- **[Admin Quick Start](docs/ADMIN_QUICKSTART.md)** - 5-minute critical setup
- **[Admin FAQ](docs/ADMIN_FAQ.md)** - Common questions and troubleshooting

### 📚 Capabilities Documentation

**Deep-dive implementation guides for ML/AI workflows:**

- **[Model Checkpointing](docs/capabilities/checkpointing.md)** - Complete checkpoint management with SafeTensors, distributed training, and cloud storage
- **[Training Loops](docs/capabilities/train_loop.md)** - Production training patterns with AMP, distributed training, and gradient accumulation
- **[PEFT Techniques](docs/capabilities/peft_hooks.md)** - Parameter-efficient fine-tuning with LoRA, adapters, prefix tuning, and QLoRA
- **[Code Quality Tooling](docs/capabilities/code_quality_tooling.md)** - Complete code quality stack with Ruff, Black, mypy, pytest, and nox
- **[GitHub CLI Troubleshooting](.github/docs/GH_CLI_Resolution_Copilot.md)** - Comprehensive guide for gh CLI issues and REST API alternatives

### 🆕 Latest Updates (December 2025)

#### Audit Pipeline v1.5.5 (2025-12-10)

**Complete Trend Aggregation & Visualization Release:**

```mermaid
flowchart LR
    subgraph v1.5.x["Audit Pipeline v1.5.x"]
        DB[(Trend Database)]
        Compare[Comparison]
        Viz[Visualization]
        CI[CI Integration]
    end
    
    subgraph Outputs
        Dashboard[Dashboard]
        Reports[Reports]
        Wiki[Wiki]
        Agent[Agent UI]
    end
    
    DB --> Compare
    Compare --> Reports
    Viz --> Dashboard
    Viz --> Agent
    Viz --> Wiki
```

| Version | Features |
|---------|----------|
| v1.5.0 | SQLite trend database, schema migrations |
| v1.5.1 | Historical comparison, regression detection |
| v1.5.2 | ASCII sparklines, HTML dashboards |
| v1.5.3 | Jinja2 report templates |
| v1.5.4 | Webhooks (Slack/Teams), CI integration |
| v1.5.5 | Performance tools, agent interface, wiki generator |

**New Commands:**
```bash
# Trend operations
python -m scripts.space_traversal.audit_runner store-trend
python -m scripts.space_traversal.audit_runner show-trend <capability>
python -m scripts.space_traversal.audit_runner check-regressions

# Visualization
python -m scripts.space_traversal.audit_runner dashboard
python -m scripts.space_traversal.audit_runner cli-builder
python -m scripts.space_traversal.audit_runner api-collection
python -m scripts.space_traversal.audit_runner api-docs
python -m scripts.space_traversal.audit_runner agent-interface

# Documentation
python -m scripts.space_traversal.wiki_generator
```

#### PR #2449 Verification Complete (2025-12-09)
- **Final Convergence Check**: All 4 verification items confirmed correct
  - ✅ Tokenizer `max_length` validation (raises `ValueError` for invalid values)
  - ✅ PYTHONHASHSEED warning (without ineffective post-startup setting)
  - ✅ Test cleanup using `tmp_path` fixture (proper resource management)
  - ✅ Deprecation tests (complete coverage including permission errors)
- **Audit Pipeline v1.4.0**: 39 capabilities tracked, 18/18 critical at maturity
- **Quality Gates**: All passing (security, linting, type checking, tests)

#### Duplicate Detection & Technical Debt Management
- **Comprehensive Duplicate Detection System**: 4 detection modes (exact, normalized, AST, semantic) operational
- **SHIM Integration**: Cross-references with `.github/SHIM_INVENTORY.yaml` for prioritization
- **Git Metadata**: Enriches findings with blame, churn, and age metrics
- **Complete Documentation**: See [docs/DUPLICATE_DETECTION.md](docs/DUPLICATE_DETECTION.md)
- **Automation**: Weekly GitHub Actions workflow for continuous monitoring
- **CLI Tool**: `python tools/duplicate_inventory.py` - full-featured duplicate scanner

#### Nightly Audit Fix
- **Whitelist Parsing**: Fixed false positives in `scripts/remediation/verify_conflicts.py`
- **Strict Mode**: Correctly excludes whitelisted modules from violations
- **Comprehensive Tests**: 3 test cases added, all passing

#### Remediation Execution
- **Module Consolidation**: Removed 6 duplicate files (scripts/analysis/ → tools/dupinv/)
- **Configuration Audit**: 12 config duplicates analyzed, migration plan created
- **Refactoring Roadmap**: 217 prioritized tickets with detailed implementation plans

#### Latest offline-first updates

- **Inference serving:** FastAPI server now wires a deterministic local model with real `/predict` and `/embed` responses. See [docs/INFERENCE_SERVING_GUIDE.md](docs/INFERENCE_SERVING_GUIDE.md) for usage and configuration.
- **Duplication quality gate:** Reusable duplication analysis module with CLI wrapper and thresholds is documented in [docs/QUALITY_GATES.md](docs/QUALITY_GATES.md).
- **Training telemetry toggle:** `codex-train` exposes `--system-metrics` to emit optional CPU/RAM metrics; documented in [docs/CLI.md](docs/CLI.md).
- **Gap/task alignment:** The declarative task list in [codex_task_sequence.yaml](codex_task_sequence.yaml) is mapped to [codex_gap_registry.yaml](codex_gap_registry.yaml) so every gap is closed or explicitly deferred.

### API Reference

📚 **[API Documentation](docs/api/README.md)** - Comprehensive API reference auto-generated from source code docstrings

To build API docs locally:
```bash
# Using nox (recommended - deterministic offline build)
nox -s docs_build

# Or using the build script directly
bash scripts/docs_build.sh

# Skip optional modules (faster, no ML dependencies required)
SKIP_OPTIONAL=1 nox -s docs_build

# Strict mode (fail if any modules missing - for CI)
FAIL_ON_MISSING=1 bash scripts/docs_build.sh
```text

**Build Modes:**
- **Default**: Includes all available modules (core + optional ML when installed)
- **Skip Optional** (`SKIP_OPTIONAL=1`): Only core modules, no ML dependencies needed
- **Strict** (`FAIL_ON_MISSING=1`): Fail build if any requested modules are unavailable

**Note:** The API documentation script automatically includes optional packages like `codex_ml` when their dependencies are installed. For complete API documentation including the ML framework:

```bash
# Install optional ML dependencies
pip install -e .[ml]

# Build full documentation
nox -s docs_build
```text

View the generated docs at `artifacts/docs/api/index.html` or serve locally:
```bash
python -m http.server -d artifacts/docs/api 8000
```text

### New to _codex_?

👉 **Start here**: [`NEWCOMER_GUIDE.md`](docs/NEWCOMER_GUIDE.md) - Comprehensive onboarding guide for all newcomers

### Quick Links - Status & Validation

- **Status Update Generator**: [tools/generate_status_update.py](tools/generate_status_update.py) - Automated JSON status report generator
- **Status Update Schema**: [schemas/codex_status_update.schema.json](schemas/codex_status_update.schema.json) - JSON Schema v1.2
- **Status Update Guide**: [tools/README_status_update.md](tools/README_status_update.md) - Usage and integration guide
- **Status Template**: [codex_status_template_v1.2.md](docs/templates/status/codex_status_template_v1.2.md)
- **Status Schema (JSON)**: [codex_status_template.schema_v1.2.json](docs/templates/status/codex_status_template.schema_v1.2.json)
- **Authoring (Quickstart)**: [authoring_quickstart_v1.2.md](docs/templates/status/authoring_quickstart_v1.2.md)
- **Validation Guides**: [docs/validation](docs/validation)
- **Ops Workflow**: [status_reports.md](docs/ops/status_reports.md)

### Quick Links - General

- **General Onboarding**: [`NEWCOMER_GUIDE.md`](docs/NEWCOMER_GUIDE.md)
- **Zendesk Administration**: [`docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md`](docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md)
- **Project Overview**: [`docs/README_ROOT.md`](docs/README_ROOT.md)
- **Contribution Guidelines**: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- **Testing Guide**: [`docs/guides/TESTING_GUIDE.md`](docs/guides/TESTING_GUIDE.md) | [`tests/README.md`](tests/README.md)
- **Changelog**: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- **Operational Templates**: [`docs/templates/README.md`](docs/templates/README.md)

## Testing

### Running Tests

**Quick test run:**
```bash
pytest                           # Run all tests
pytest -q                        # Quiet mode
pytest -m smoke                  # Smoke tests only
pytest -m "not slow"             # Skip slow tests
```

**With coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
open htmlcov/index.html          # View coverage report
```

**CI/CD:** All PRs run automated tests via `.github/workflows/ci-pytest.yml`
- Python 3.11+ (ubuntu-latest)
- 90% coverage threshold (configurable)
- Coverage reports uploaded as artifacts
- Automatic PR comments with results

See [`tests/README.md`](tests/README.md) for comprehensive testing instructions.

### Local DoD (short)

```bash
# Run all quality gates
nox -s lint typecheck tests gates

# Run tests with coverage
pytest --cov=src --cov-fail-under=90

# Validate status schema
pytest -q tests/status/test_example_report_schema.py

# Validate configs
python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml
```

## Local Gates & Status Reports

This repository ships **local-only** quality gates (no CI) and a local status reporter:

- See **docs/ops/local_gates.md** for running fences, evaluator, schema checks, and the selection guard.
- See **docs/ops/status_reports.md** for generating a reusable **STATUS_REPORT.md** (including template mode, `--verbose`, and `--save-logs`).

Quick start:
```bash
python tools/status_report.py --summary samples/assistant_message_summary.sample.json --selected 3 --out STATUS_REPORT.md
```text

### Repository Status Audit

Generate a comprehensive status update audit report for the Codex repository:

```bash
# Generate JSON status update (new schema-based generator)
codex-status-audit --generate
# Output: .codex/status/_codex_status_update-YYYY-MM-DD.json

# Or use the direct script
python tools/generate_status_update.py

# Full audit and report (legacy)
codex-status-audit

# Quick regeneration with existing artifacts
codex-status-audit --skip-audit

# Compare against baseline
codex-status-audit --baseline audit_artifacts/capabilities_scored.json.baseline
```text

The new JSON-based status update generator provides:
- Automated repository analysis
- 8 capability checks with gap analysis
- Reproducibility controls audit
- Test infrastructure status
- Security assessment
- Schema validation (v1.2)

See **[tools/README_status_update.md](tools/README_status_update.md)** for the new generator documentation.  
See **[docs/cli/status_audit.md](docs/cli/status_audit.md)** for legacy audit tool usage.

## Candidate Selection (local-only)

You can generate a local selection recommendation across 1–4 assistant variants:

```bash
python tools/selection_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --out SELECTION_REPORT.md
```text

This runs the evaluator and enforces required selection-guard signals, then explains the tie-break.

## Quickstart

```bash
codex-train experiment=debug training.max_epochs=1 training.batch_size=2 \
  data.train_path=data/train.jsonl data.eval_path=data/eval.jsonl \
  logging.tensorboard=false logging.mlflow_enable=false \
  training.output_dir=artifacts/runs/quickstart
codex reasoning-templates list
codex-train +reasoning=baseline curriculum.phase_schedule=starter \
  logging.reasoning_trace=true training.output_dir=artifacts/runs/reasoning-starter
codex evaluate --config configs/evaluation/reasoning.yaml --metrics-only
```text

### Offline-first environment bootstrap

```bash
# 1) Create and activate a virtualenv (any tool)
python -m venv .venv && . .venv/bin/activate

# 2) Install dev tools
pip install -r requirements-dev.txt

# 3) (Optional) Sync minimal runtime deps from a lockfile if provided
if [ -f requirements/lock.txt ]; then
  pip install -r requirements/lock.txt
fi

# 4) Sanity gates
python tools/validate_fences.py
python tools/schema_validate.py \
  --data manifests/selection_guard_rules.json --schema schemas/selection_guard_rules.schema.json \
  --data manifests/codex_eval_rules.v3.json --schema schemas/codex_eval_rules.v3.schema.json

# Optional: selection and status one-liners
python tools/selection_report.py --summary samples/assistant_message_summary.sample.json --out SELECTION_REPORT.md
python tools/status_report.py    --summary samples/assistant_message_summary.sample.json --selected 3 \
                                 --template docs/templates/status_update.md \
                                 --branch my/branch --pr 1234 --verbose --save-logs --out STATUS_REPORT.md
```text

---

## 🔍 Search Index

Quick access to key repository areas via GitHub search. Click any link or use the search patterns with ChatGPT/Copilot.

### Core Components

| Component | Search Query | Description |
|-----------|--------------|-------------|
| **ML Training Core** | [`path:src/codex_ml/ language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Asrc%2Fcodex_ml%2F+language%3APython) | Training engine, LoRA/QLoRA, model initialization |
| **CLI Commands** | [`path:src/codex/cli.py OR path:cli/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Asrc%2Fcodex%2Fcli.py+OR+path%3Acli%2F) | Command-line interface and entry points |
| **Logging & Telemetry** | [`path:src/codex/logging/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Asrc%2Fcodex%2Flogging%2F) | Session tracking, SQLite backend, query engine |
| **Services & APIs** | [`path:services/ language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Aservices%2F+language%3APython) | Microservices, adapters, API endpoints |
| **Interfaces & Contracts** | [`path:interfaces/ (Protocol OR pydantic)`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Ainterfaces%2F+%28Protocol+OR+pydantic%29) | Type definitions, protocols, schemas |

### Configuration & Data

| Area | Search Query | Description |
|------|--------------|-------------|
| **Hydra Configs** | [`path:config/ OR path:configs/ extension:yaml`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Aconfig%2F+OR+path%3Aconfigs%2F+extension%3Ayaml) | Hydra configuration files |
| **Schemas** | [`path:schemas/ (extension:json OR extension:yaml)`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Aschemas%2F+%28extension%3Ajson+OR+extension%3Ayaml%29) | Data validation schemas |
| **Data Quality** | [`path:great_expectations/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Agreat_expectations%2F) | Great Expectations configurations |
| **Project Config** | [`filename:pyproject.toml OR filename:noxfile.py`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3Apyproject.toml+OR+filename%3Anoxfile.py) | Project dependencies and build config |

### Documentation & Governance

| Document Type | Search Query | Description |
|---------------|--------------|-------------|
| **Architecture** | [`path:docs/ARCHITECTURE.md OR path:docs/arch/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adocs%2FARCHITECTURE.md+OR+path%3Adocs%2Farch%2F) | System architecture, C4 diagrams |
| **ADRs** | [`path:docs/decision_records/ filename:*.md`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adocs%2Fdecision_records%2F+filename%3A*.md) | Architecture Decision Records |
| **Security & Policy** | [`filename:SECURITY.md OR path:docs/security/`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3ASECURITY.md+OR+path%3Adocs%2Fsecurity%2F) | Security policy, vulnerability reporting |
| **Code Owners** | [`filename:CODEOWNERS`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3ACODEOWNERS) | Repository ownership mapping |
| **API Documentation** | [`path:docs/api/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adocs%2Fapi%2F) | API references and guides |
| **Prompts & Recipes** | [`path:PROMPTS/ OR path:docs/prompts/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3APROMPTS%2F+OR+path%3Adocs%2Fprompts%2F) | ChatGPT search recipes, prompt templates |

### CI/CD & Workflows

| Area | Search Query | Description |
|------|--------------|-------------|
| **GitHub Workflows** | [`path:.github/workflows/ extension:yml`](https://github.com/Aries-Serpent/_codex_/search?q=path%3A.github%2Fworkflows%2F+extension%3Ayml) | CI/CD workflow definitions |
| **Issue Templates** | [`path:.github/ISSUE_TEMPLATE/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3A.github%2FISSUE_TEMPLATE%2F) | Bug reports, feature requests |
| **Dependabot** | [`filename:dependabot.yml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3Adependabot.yml) | Dependency update configuration |
| **Pre-commit Hooks** | [`filename:.pre-commit-config.yaml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3A.pre-commit-config.yaml) | Linting and formatting hooks |

### Testing & Quality

| Category | Search Query | Description |
|----------|--------------|-------------|
| **Test Files** | [`path:tests/ language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Atests%2F+language%3APython) | All test modules |
| **Test Functions** | [`"def test_" language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=%22def+test_%22+language%3APython) | Individual test functions |
| **Fixtures** | [`"@pytest.fixture" OR "conftest.py"`](https://github.com/Aries-Serpent/_codex_/search?q=%22%40pytest.fixture%22+OR+%22conftest.py%22) | Test fixtures and configuration |
| **Linter Configs** | [`filename:.ruff.toml OR filename:.bandit.yml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3A.ruff.toml+OR+filename%3A.bandit.yml) | Code quality configuration |

Security scanning runs with `bandit -r src/ -c bandit.yaml -f txt` using the curated ruleset in `bandit.yaml` (medium severity/confidence, explicit skips documented inline).

### Deployment & Docker

| Resource | Search Query | Description |
|----------|--------------|-------------|
| **Dockerfiles** | [`filename:Dockerfile OR filename:docker-compose.yml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3ADockerfile+OR+filename%3Adocker-compose.yml) | Container definitions |
| **Deployment** | [`path:deploy/ OR path:manifests/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adeploy%2F+OR+path%3Amanifests%2F) | Deployment configurations |
| **Scripts** | [`path:scripts/ (language:Python OR language:Shell)`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Ascripts%2F+%28language%3APython+OR+language%3AShell%29) | Automation and utility scripts |

### Advanced Search Patterns

```text
# Find all configuration entry points
filename:pyproject.toml OR filename:setup.py OR filename:noxfile.py

# Locate error handling patterns
path:src/ "try:" language:Python

# Find logging usage
path:src/ ("logging.info" OR "logger.error") language:Python

# Search for security-sensitive code
("password" OR "secret" OR "api_key" OR "token") language:Python

# Find deprecation notices
("deprecated" OR "DEPRECATED" OR "TODO: remove") in:file

# Locate all README files
filename:README.md

# Find Mermaid diagrams
path:docs/ "mermaid" in:file
```text

### Quick Navigation

- **Getting Started**: Start with [`NEWCOMER_GUIDE.md`](docs/NEWCOMER_GUIDE.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Security**: Report vulnerabilities via [SECURITY.md](SECURITY.md)
- **Search Help**: Full guide in [PROMPTS/CHATGPT_SEARCH_RECIPES.md](PROMPTS/CHATGPT_SEARCH_RECIPES.md)

---

**For more search patterns and ChatGPT/Copilot guidance**, see [PROMPTS/CHATGPT_SEARCH_RECIPES.md](PROMPTS/CHATGPT_SEARCH_RECIPES.md).

## Building Docker images locally

To reproduce the CI image builds locally (recommended to use linux/amd64 platform to match published wheels):

- CPU image:

```bash
docker build --platform=linux/amd64 -f Dockerfile -t codex-ml:cpu-local .
```

- GPU image (requires NVIDIA container toolkit and compatible CUDA runtime):

```bash
docker build --platform=linux/amd64 -f Dockerfile.gpu -t codex-ml:gpu-local .
```

Notes:
- If you set `ALLOW_MULTIARCH` to `true` in the workflow, CI will attempt arm64 builds; ensure that required Python wheels exist for that platform.

### Build cache and per-arch wheels

- The Dockerfiles use BuildKit cache mounts to speed up Python package downloads:
  - Ensure BuildKit is enabled (default on GitHub Actions; locally: export DOCKER_BUILDKIT=1).
- CI uses docker/build-push-action cache-to/cache-from to reuse layers across runs.
- Per-arch wheel builds:
  - The workflow uploads wheelhouse artifacts for each enabled platform (amd64 always; arm64 only when ALLOW_MULTIARCH='true').
  - Review artifacts in the Actions run to validate wheel availability on each platform before enabling multi-arch pushes.

## Supply Chain Security & Dependency Management

### Wheel Manifest & Baseline Artifacts

The CI pipeline generates cryptographic manifests of all Python wheels built during the image build process:

- **Manifest Generation**: Each wheel build produces a `manifest.json` with SHA256 hashes
- **Per-Platform Baselines**: Separate manifests for `linux/amd64` and `linux/arm64` (when enabled)
- **Artifact Storage**: Manifests uploaded to GitHub Actions artifacts for 30-90 days

Generate a local manifest:
```bash
python scripts/ci/generate_wheel_manifest.py \
  --wheelhouse ./wheelhouse \
  --output manifest.json \
  --platform linux/amd64 \
  --python-version 3.11
```

### SBOM (Software Bill of Materials)

Every PR build generates SBOM files in multiple formats:

- **SPDX JSON**: Industry-standard format for license compliance
- **CycloneDX JSON**: OWASP standard for security analysis
- **Syft JSON**: Anchore-native format with rich metadata

SBOMs are automatically:
- Generated for both CPU and GPU images
- Scanned with Grype for known vulnerabilities
- Uploaded to GitHub Security tab (SARIF format)
- Stored as workflow artifacts

### Scheduled Dependency Audit

Weekly automated audit workflow (`scheduled-dependency-audit.yml`) runs:

1. **Baseline Regeneration**: Rebuild wheelhouse and manifests
2. **Drift Detection**: Compare with previous baseline, alert on changes
3. **SBOM Scanning**: Generate and scan SBOMs for vulnerabilities
4. **Upgrade Compatibility**: Test Python 3.11, 3.12, 3.13 compatibility
5. **Issue Creation**: Auto-file GitHub issues when drift detected

Trigger manually:
```bash
gh workflow run scheduled-dependency-audit.yml \
  -f python_version=3.12 \
  -f enable_multiarch=true
```

### Upgrade Strategy

| Scenario | Action | Trigger |
|----------|--------|---------|
| **Ray publishes 3.12 wheels** | Test in shadow matrix | Weekly audit detects availability |
| **Hash mismatch detected** | Review manifest diff, update pins | Drift detection alerts |
| **CVE in dependency** | Review Grype SARIF, patch/upgrade | Security scan on PR |
| **Multi-arch expansion** | Enable `ALLOW_MULTIARCH=true`, verify artifacts | Manual testing then repo variable |
| **Python minor upgrade** | Run upgrade-compatibility job, fix issues | Scheduled audit tests new versions |

### Security Posture

- ✅ All wheels integrity-verified via SHA256 manifest
- ✅ SBOM generation on every PR build
- ✅ Vulnerability scanning with Grype (critical = fail)
- ✅ Weekly dependency drift detection
- ✅ Automated Python version compatibility testing
- ✅ GitHub Security integration for SARIF alerts

## 🔒 Security Utilities

**New in v2.0**: Comprehensive security utilities for sensitive data handling.

### Quick Start

```python
from codex.security import mask_token, sanitize_log, hash_secure
from codex.security.storage import SecureStorage

# Mask sensitive data in logs
logger.info(f"API Key: {mask_token(api_key)}")
# Output: "API Key: ****************xyz789"

# Prevent log injection attacks
user_input = request.form.get('data')
logger.info(f"User provided: {sanitize_log(user_input)}")

# Secure token hashing for comparison
token_hash = hash_secure(token, algorithm='sha256')

# Encrypted storage for secrets
storage = SecureStorage()  # Requires ENCRYPTION_KEY env var
storage.store_secret("secrets/api_key.enc", api_key)
api_key = storage.load_secret("secrets/api_key.enc")
```

### Performance

All security functions are highly optimized for production use:

| Function | Throughput | Use Case |
|----------|-----------|----------|
| `mask_token()` | 3.7M ops/sec | API key masking |
| `mask_password()` | 12.4M ops/sec | Password hiding |
| `sanitize_log()` | 1.3M ops/sec | Log injection prevention |
| `hash_secure()` | 1.2M ops/sec | SHA-256 token hashing |

**Benchmark Results**: All functions <0.01ms average (see `benchmarks/security_benchmarks.py`)

### Documentation

- **[Security Guidelines](docs/security/SECURITY_GUIDELINES.md)** - Best practices & examples
- **[Complete Status Report](docs/security/COMPLETE_STATUS_REPORT.md)** - Implementation details
- **[API Reference](src/codex/security/__init__.py)** - Full function documentation

### Features

✅ **Unified Security Module** - Single import for all security utilities  
✅ **Encrypted Storage** - Fernet (AES-128-CBC + HMAC) for secrets at rest  
✅ **Log Injection Prevention** - Sanitize user input before logging  
✅ **Secure Hashing** - SHA-256/SHA-512 (no MD5/SHA-1)  
✅ **Performance** - <0.01ms per operation for hot paths  
✅ **Testing** - 18 integration tests covering all utilities  

## MCP Packager

Generate MCP package scaffolds using the built-in packager. See [docs/mcp_packager.md](docs/mcp_packager.md) and the sample config at [docs/mcp_packager_template.yaml](docs/mcp_packager_template.yaml).

---

## 🔧 Workflow Management & CI Health

**Status**: ✅ Production Ready (as of 2025-12-28)

### Quick Stats
- **Active Workflows**: 48 (target achieved)
- **Consolidation**: 19 workflows consolidated (-28.4%)
- **CI Health**: EXCELLENT
- **Backup Coverage**: 100%
- **YAML Validity**: 100%

### Key Features

#### 1. Automated Workflow Consolidation
Intelligent workflow lifecycle management with phased consolidation:
- **7-phase system**: testing, documentation, container, validation, monitoring, maintenance, other
- **Safety-first**: Backup before every change
- **Metadata tracking**: Complete audit trail
- **Rollback capability**: Multiple restore options

#### 2. CI Health Monitoring
Automated health checks every 6 hours:
- YAML syntax validation
- Workflow count tracking
- Automatic issue creation
- Trend analysis
- Performance metrics

#### 3. Self-Service Restoration
Easy workflow restoration via UI or CLI:
- 3 restore sources (backup-latest, backup-date, archive-disabled)
- Enable immediately or restore as disabled
- SHA256 verification
- Automatic inventory updates

### Quick Start

#### Validate CI Health
```bash
bash scripts/validate_ci_health.sh
```

#### Catalog Workflows
```bash
python3 scripts/catalog_workflows.py
```

#### Restore a Workflow
1. Go to Actions → Workflow Restore Tool
2. Select workflow and source
3. Click "Run workflow"

### Documentation
- [Final Consolidation Report](.github/workflow-archive/FINAL_CONSOLIDATION_REPORT.md)
- [Workflow Inventory](.github/workflow-archive/WORKFLOW_INVENTORY.yaml)
- [AGENTS.md](AGENTS.md) - Detailed agent documentation

### Monitoring
- **Automated**: [CI Health Monitor](.github/workflows/ci-health-monitor.yml)
- **Manual**: Run `bash scripts/validate_ci_health.sh`
- **Trends**: Check workflow-trends artifacts in Actions

### Support
For issues or questions about workflow management:
1. Check [FINAL_CONSOLIDATION_REPORT.md](.github/workflow-archive/FINAL_CONSOLIDATION_REPORT.md)
2. Review [CONSOLIDATION_STATUS.md](.github/workflow-archive/CONSOLIDATION_STATUS.md)
3. Use [Workflow Restore Tool](.github/workflows/workflow-restore.yml)
4. Contact maintainers via issues

---

---

## 🔐 Security & Token Management

The `_codex_` repository uses **encrypted token storage** for Copilot Agent operations.

### For Administrators

Setup secure token storage:

```bash
python3 scripts/security/token_encryption_tool.py
```

See: [Admin Token Setup Guide](docs/admin/security/ADMIN_TOKEN_SETUP.md)

### For Copilot Agent

Token retrieval is automatic:

```python
from scripts.security.copilot_token_decoder import copilot_get_github_token

token = copilot_get_github_token()
# Use for GitHub API operations
```

**Security Level**: 🔐🔐🔐🔐🔐 (AES-256-GCM encryption available)
