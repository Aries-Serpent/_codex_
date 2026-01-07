# Codebase Cognitive Map

**Purpose**: High-level cognitive map of the `_codex_` repository - components, flows, dependencies, and operational context for AI agents.

**Last Updated**: 2024-12-30 | **Version**: 1.0.0 | **Status**: Active

---

## Architecture Overview

**Type**: Modular ML/AI Platform with Agent Orchestration  
**MLOps Maturity**: Level 4 (100/100 Azure MLOps) - Production Ready  
**Stats**: 1500+ tests (100% passing), 72% coverage, 0 vulnerabilities

### Repository Structure
```
_codex_/
├── src/              # Core application code
│   ├── codex/       # Ingestion pipeline (ingest→analyze→transform→verify)
│   ├── rag/         # RAG pipelines & retrieval
│   ├── verification/ # Chain-of-Verification (CoVe)
│   ├── mcp/         # Model Context Protocol adapters
│   └── tools/       # Tool registry
├── agents/          # Autonomous agents (workflow, quantum, physics)
├── scripts/         # Automation & utilities
│   └── mcp/        # ChatGPT Project packaging system
├── tests/           # 1500+ test suite
├── docs/            # Documentation hub
│   ├── mcp/        # MCP packaging docs (93+ KB)
│   ├── system/     # Cognitive brain (this file)
│   └── capabilities/ # Capability guides
└── .github/         # CI/CD workflows & automation
```

---

## Core Components

### 1. Codex Ingestion Pipeline (`src/codex/`)
**Purpose**: Complete Python code processing system

**Commands**:
```bash
python -m codex.cli ingest <source>      # Ingest code (file/ZIP/Git)
python -m codex.cli analyze <snapshot-id> # Static + runtime analysis
python -m codex.cli transform <snapshot-id> --tier A # Apply transformations
python -m codex.cli verify <snapshot-id> # Behavior verification
```

**Flow**: Source → Ingest → Analyze → Transform → Verify → PR

### 2. Agent System (`agents/`)
**Purpose**: Autonomous AI agents with physics-inspired optimization

**Key Agents**:
- `workflow_navigator.py` - Tokenized workflows (AUDIT_EXEC, DOC_GEN)
- `quantum_game_theory.py` - Quantum-inspired decisions
- `physics_orchestrator.py` - 6 physics paradigms
- `mental_mapping.py` - Context tracking

**Tokens**: `audit`, `decide`, `docs`, `organize`, `review`, `heal`

### 3. MCP Package System (`scripts/mcp/`)
**Purpose**: Package codebase for ChatGPT Projects

**Commands**:
```bash
./scripts/mcp/mcp-package --list              # List 9 topics
./scripts/mcp/mcp-package --topic agents      # Package by topic
./scripts/mcp/mcp-package --custom "patterns" # Custom patterns
```

**Topics**: zendesk, agents, quantum, docs, mcp, workflows, python_dev, testing, security

**Output**: Flat ZIP with manifest.json, README_dataset.md, index.md

**Docs**: `docs/mcp/` - 93+ KB across 8 comprehensive guides

### 4. RAG & Verification (`src/rag/`, `src/verification/`)
- RAG pipelines: Chunking, embedding, retrieval
- CoVe: Chain-of-Verification fact-checking
- MCP adapters: Pinecone, Mock integrations

---

## Data Flows

### Code Ingestion
```
External Source → Ingest → Static Analysis → Runtime Analysis →
LLM Intent Inference → Transformation → Verification → PR Creation
```

### Agent Workflow
```
Request → WorkflowNavigator → Agent Orchestration →
Task Execution → Verification → State Persistence
```

### MCP Packaging
```
Human Request → Component Selection → File Flattening →
Manifest Generation → ZIP Creation → ChatGPT Upload
```

### CI/CD
```
Git Push → Status Validation → Security Gates → Quality Gates →
Test Execution → Cache Management → Artifact Generation
```

---

## Dependencies & Integrations

### External Services
- **OpenAI API**: LLM intent inference (`OPENAI_API_KEY`)
- **GitHub API**: PR creation, workflows (`GITHUB_TOKEN`)
- **Pinecone**: Vector embeddings (optional)
- **CodeQL/Semgrep**: Security scanning

### Python Dependencies
- **Core**: numpy, pandas, openai, httpx, pydantic, hydra-core
- **Dev**: pytest, black, ruff, mypy, nox, pre-commit
- **ML/AI**: torch, transformers, safetensors (optional)

---

## CI/CD Pipeline

### Key Workflows (`.github/workflows/`)
| Workflow | Trigger | Purpose | Cache |
|----------|---------|---------|-------|
| `status_validation.yml` | push, PR | Repo status | - |
| `security_gates.yml` | push, PR | Security | - |
| `nox_gates.yml` | push, PR | Quality (lint/type) | Ruff, MyPy |
| `optimized-ci.yml` | push, PR | Optimized CI | All tools |
| `build-chatgpt-package.yml` | dispatch | MCP packaging | - |
| `scan-secrets-variables.yml` | schedule | Secrets scan | Gitleaks |

### Cache Strategy (Phase 3C-Lite)
- **Ruff**: ~20-30 MB | **MyPy**: ~50-80 MB
- **Pytest**: ~30-50 MB | **pre-commit**: ~50-100 MB
- **Total**: 7.69 GB / 10 GB limit (23% buffer)
- **Keys**: `${{ runner.os }}-${{ github.workflow }}-<tool>-${{ hashFiles(...) }}`

---

## Security & Secrets

### Secrets (GitHub UI injected)
- `OPENAI_API_KEY` - OpenAI API
- `PINECONE_API_KEY` - Pinecone (optional)
- `CODEX_MASTER_KEY` - Genesis Protocol

### Security Scanning
- Gitleaks, Trufflehog - Secret detection
- Semgrep SAST - Static analysis
- CodeQL - Code scanning

### Anti-/tmp/ Protection
**Policy**: Use `.github/tmp/` instead of `/tmp/`  
**Applied**: emergency_cache_cleanup.sh, MCP tools  
**Doc**: `docs/system/ANTI_TMP_PROTECTION_SYSTEM.md`

---

## MCP & ChatGPT Integration

### Packaging Capabilities
1. **9 Predefined Topics**: All major capabilities covered
2. **Custom Patterns**: Glob-based file selection
3. **Flat Structure**: Optimized for ChatGPT
4. **Metadata**: SHA256, sizes, language detection
5. **Navigation**: Manifest-driven discovery

### Methodology Transfer (8 Capabilities)
1. Python script development/deconstruction
2. Workflow navigation & state management
3. Quantum game theory application
4. API integration patterns
5. CI/CD workflow optimization
6. Agent-based architecture
7. TDD methodology
8. Documentation generation

### Documentation (`docs/mcp/`)
- `QUICK_START.md` - 5-minute onboarding
- `PACKAGING_GUIDE.md` - Complete workflows
- `PACKAGEABLE_CAPABILITIES.md` - Capability transfer
- `ChatGPT_Project_SYSTEM_PROMPT.md` - AI prompt
- `GENERIC_NAVIGATION_SYSTEM.md` - Universal navigation
- `ADVANCED_FEATURES_PLANSET.md` - Roadmap (Cycle 1-Phase 3 (Current Cycle))

---

## Operational Context

### GitHub Limits
- **Copilot Pro+**: 64K tokens/session
- **GitHub Team**: 10 GB cache, limited Actions minutes
- **Current Cache**: 7.69 GB (23% buffer)

### Quality Metrics
- **Tests**: 1500+ (100% passing)
- **Coverage**: 72% (target: 80%+)
- **Security**: 0 vulnerabilities
- **Cache Hit Rate**: 90%+ projected

### Performance Targets
- Test execution: <5 min
- Lint/type: <2 min
- Package creation: <2 min

---

## Quick Reference

### Common Commands
```bash
# Codex
python -m codex.cli ingest|analyze|transform|verify

# MCP
./scripts/mcp/mcp-package --list|--topic|--custom

# Testing
make docker-test
pytest tests/ --cov=src/

# Quality
nox -s lint|type|format

# Agent
python -m scripts.space_traversal.audit_runner agent-interface
```

### Entry Points
| System | Entry | Type |
|--------|-------|------|
| Codex CLI | `python -m codex.cli` | Module |
| MCP Package | `./scripts/mcp/mcp-package` | Script |
| Agent Navigator | `agents.workflow_navigator` | Class |
| Tests | `pytest` / `make docker-test` | Command |

---

## Navigation for AI Agents

### Getting Started
1. **Architecture**: This doc → `docs/ARCHITECTURE.md`
2. **Capabilities**: `docs/capabilities/*.md`
3. **Workflows**: `agents/TOKENIZED_WORKFLOWS.md`
4. **MCP**: `docs/mcp/QUICK_START.md`
5. **Contributing**: `docs/CONTRIBUTING.md`

### Finding Things
- **Code**: `src/` (app), `agents/` (agents)
- **Tests**: `tests/` (mirrors `src/`)
- **Scripts**: `scripts/` (automation)
- **Docs**: `docs/` (organized by topic)
- **CI/CD**: `.github/workflows/`

### Common Tasks
- **New capability**: `docs/capabilities/` template
- **Extend agents**: `agents/workflow_navigator.py`
- **Add CI**: `.github/workflows/` templates
- **Package code**: `scripts/mcp/mcp-package`
- **Run tests**: `make docker-test`

---

## Related Documents

- [Codebase Dashboard](CODEBASE_DASHBOARD.md) - Live status & next steps
- [Roadmap](../ROADMAP.md) - Feature roadmap & iterations
- [Architecture](../ARCHITECTURE.md) - Detailed architecture
- [Contributing](../CONTRIBUTING.md) - Contribution guide
- [Admin Guide](../ADMIN_IMPLEMENTATION_GUIDE.md) - Admin setup

---

**Owner**: DevOps + Agent Development Team  
**Review**: Monthly or after major changes  
**Last Reviewed**: 2024-12-30

**Questions?** → [Dashboard](CODEBASE_DASHBOARD.md)
