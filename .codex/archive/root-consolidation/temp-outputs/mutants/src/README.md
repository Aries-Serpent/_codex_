# Core Application Code (`src/`)

**Purpose**: Core implementation of the `_codex_` ML/AI platform including ingestion pipeline, RAG systems, verification, and MCP adapters.

---

## 📁 Structure

```
src/
├── codex/           # Codex ingestion pipeline (ingest → analyze → transform → verify)
├── rag/             # RAG pipelines (chunking, embedding, retrieval)
├── verification/    # Chain-of-Verification (CoVe) fact-checking
├── mcp/             # Model Context Protocol adapters (Pinecone, Mock)
├── tools/           # Tool registry and discovery
├── agent/           # Agent orchestration infrastructure
└── codex_ml/        # ML utilities and integrations
```

---

## 🚀 Key Modules

### 1. **Codex Pipeline** (`codex/`)
Complete Python code processing system.

**Entry Point**: `python -m codex.cli`

**Commands**:
```bash
python -m codex.cli ingest <source>        # Ingest from file/ZIP/Git
python -m codex.cli analyze <snapshot-id>  # Static + runtime analysis
python -m codex.cli transform <snapshot-id> --tier A  # Apply transformations
python -m codex.cli verify <snapshot-id>   # Behavior verification
```

**Flow**: Source → Ingest → Analyze → Transform → Verify → PR

**Components**:
- `ingest/` - Code ingestion and snapshot creation
- `analyze/` - Static analysis + runtime sandbox
- `transform/` - Tier-based transformations (A/B/C)
- `verify/` - Behavior verification and test generation
- `intent/` - LLM intent inference (OpenAI integration)
- `cli/` - CLI interface and PR operator

### 2. **RAG Pipelines** (`rag/`)
Retrieval-Augmented Generation infrastructure.

**Components**:
- `pipelines/` - Chunking, embedding, retrieval pipelines
- Document processing
- Vector storage integration

### 3. **Verification System** (`verification/`)
Chain-of-Verification (CoVe) for fact-checking.

**Features**:
- Multi-step verification
- Evidence gathering
- Confidence scoring
- Fact validation

### 4. **MCP Adapters** (`mcp/`)
Model Context Protocol integrations.

**Adapters**:
- `adapters/` - Pinecone, Mock implementations
- `metrics/` - Telemetry and monitoring
- `workers/` - Background embedding workers

### 5. **Tool Registry** (`tools/`)
Centralized tool registration and discovery for agents.

**Features**:
- Tool registration
- Capability discovery
- Execution management

---

## 🔧 Development

### Running Tests
```bash
# Full test suite
pytest tests/

# Specific module
pytest tests/codex/

# With coverage
pytest tests/ --cov=src/
```

### Code Quality
```bash
# Lint
nox -s lint

# Type check
nox -s type

# Format
nox -s format
```

---

## 📚 Documentation

- [Codex Pipeline Guide](../../docs/plans/operational_runbook.md)
- [Architecture Overview](../../docs/ARCHITECTURE.md)
- [API Reference](../../docs/API_REFERENCE.md)
- [Cognitive Map](../../docs/system/CODEBASE_COGNITIVE_MAP.md)

---

## 🤝 Contributing

See [Contributing Guide](../../CONTRIBUTING.md) for development workflow.

---

**Owner**: Core Development Team  
**Last Updated**: 2025-12-30
