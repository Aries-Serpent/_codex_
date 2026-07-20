# Optional Features & Dependencies Guide

**Version**: v0.3.0
**Last Updated**: 2026-07-20
**Target Audience**: Developers, ML Engineers, DevOps Engineers

## Table of Contents

1. [Overview](#overview)
2. [Feature Categories](#feature-categories)
3. [Installation Profiles](#installation-profiles)
4. [RAG API Features](#rag-api-features)
5. [Cognitive Brain Features](#cognitive-brain-features)
6. [Memory Systems Features](#memory-systems-features)
7. [Graceful Degradation](#graceful-degradation)
8. [Verification & Testing](#verification--testing)
9. [Common Issues](#common-issues)

---

## Overview

Codex ML v0.3.0 supports optional dependencies organized by feature category:

- **RAG API**: Vector store integration, retrieval frameworks, semantic search
- **Cognitive Brain**: Reasoning engines, autonomous agents, decision logic
- **Memory Systems**: STM/LTM consolidation, caching, persistence

Each optional feature degrades gracefully when dependencies are missing, allowing you to install only what you need for your use case.

### Three-Profile Strategy

| Profile | Size | Best For | Installation |
|---------|------|----------|--------------|
| **Core** | 8-15 MB | Lightweight, offline, edge | `pip install codex-ml[core]` |
| **Runtime** | 20-35 MB | Production inference | `pip install codex-ml[runtime]` |
| **Full** | 100+ MB | Development, all features | `pip install codex-ml[full]` |

---

## Feature Categories

### RAG API Features

The RAG (Retrieval-Augmented Generation) API provides semantic search, vector storage, and retrieval capabilities for knowledge integration.

**Use Cases**:
- Semantic document search
- Knowledge base integration
- Vector similarity matching
- Hybrid retrieval (semantic + BM25)

**Core Dependencies**:
- `faiss-cpu` or `pinecone-client`: Vector storage
- `sentence-transformers`: Embedding models
- `langchain`: LLM framework
- `numpy`: Numerical operations

**Installation**:
```bash
# Install runtime profile (includes RAG dependencies)
pip install codex-ml[runtime]

# Or install with RAG extras only
pip install codex-ml[rag]

# Check if RAG is available
python -c "from codex_ml.serving import inference_server; print('RAG available')"
```

### Cognitive Brain Features

The Cognitive Brain module provides autonomous reasoning, decision-making, and multi-agent orchestration with quantum advantage optimization.

**Use Cases**:
- Autonomous decision-making
- Multi-agent orchestration
- Reasoning with uncertainty
- Pattern recognition and inference

**Core Dependencies**:
- `torch`: Tensor operations for neural networks
- `transformers`: Pre-trained models and inference
- `duckdb`: Pattern storage and querying
- `pydantic`: Configuration validation

**Installation**:
```bash
# Install with cognitive extras
pip install codex-ml[cognitive]

# Or get full installation with all features
pip install codex-ml[full]

# Check if Cognitive Brain is available
python -c "from codex_ml.monitoring.codex_logging import setup_logging; print('Cognitive Brain available')"
```

### Memory Systems Features

Memory Systems implement STM/LTM (Short-Term/Long-Term) consolidation, caching strategies, and persistent storage for learned patterns.

**Use Cases**:
- Session-based learning
- Pattern consolidation
- Cache optimization
- Memory compression

**Core Dependencies**:
- `sqlite3`: Built-in Python, persistent storage
- `duckdb`: Analytics on cached data
- `lru-dict` or `cachetools`: In-memory caching
- `pickle` / `json`: Serialization

**Installation**:
```bash
# Install with memory extras
pip install codex-ml[memory]

# Or install full for all memory features
pip install codex-ml[full]

# Check if memory systems are available
python -c "import sqlite3; print('Memory systems available')"
```

---

## Installation Profiles

### Core Profile (`[core]`)

**Size**: 8-15 MB  
**Python**: 3.12+  
**Best For**: Lightweight deployments, offline environments, edge devices

**Includes**:
- Configuration system (Hydra + OmegaConf)
- CLI tools (Typer)
- Code analysis (libcst, parso)
- Safety enforcement

**What's NOT included**:
- PyTorch or model inference
- Vector databases
- ML frameworks
- Tracking systems

**Installation**:
```bash
pip install codex-ml[core]==0.3.0
```

**Typical Use**:
```python
from codex_ml.config import load_config
from codex_ml.cli.main import app

# Use configuration and CLI
config = load_config("config.yaml")
# CLI commands work without ML dependencies
```

### Runtime Profile (`[runtime]`)

**Size**: 20-35 MB  
**Python**: 3.12+  
**Best For**: Production inference, pattern recognition, API services

**Includes**:
- Everything in Core
- PyTorch + CUDA support (CPU by default)
- Transformers for model inference
- FastAPI for HTTP APIs
- Ray Serve for distributed serving
- Basic vector storage (FAISS)

**What's NOT included**:
- Development tools
- Testing frameworks
- Full cognitive brain features
- Advanced memory systems

**Installation**:
```bash
pip install codex-ml[runtime]==0.3.0

# For GPU support (if CUDA available)
pip install torch[cuda118]  # CUDA 11.8
```

**Typical Use**:
```python
from codex_ml.serving.inference_server import InferenceServer
from transformers import AutoModel

# Serve models in production
server = InferenceServer()
server.load_model("model-path")
predictions = server.predict(input_data)
```

### Full Profile (`[full]`)

**Size**: 100+ MB  
**Python**: 3.12+  
**Best For**: Development, research, experimentation with all features

**Includes**:
- Everything in Core and Runtime
- Cognitive Brain components
- Memory Systems (STM/LTM)
- MLflow experiment tracking
- Weights & Biases integration
- Development tools (pytest, sphinx)
- Jupyter notebook support
- All optional integrations

**Installation**:
```bash
pip install codex-ml[full]==0.3.0

# For development (editable install)
pip install -e ".[full]"
```

**Typical Use**:
```python
from codex_ml.training.trainer import Trainer
from codex_ml.monitoring.codex_logging import CodexLogger
from codex_ml.serving.inference_server import InferenceServer

# Full development workflow
logger = CodexLogger()
trainer = Trainer(config=config)
trainer.train()
server = InferenceServer()
server.deploy(trainer.best_model)
```

---

## RAG API Features

### Vector Store Integration

**Feature**: Semantic search using vector embeddings

**Dependencies**:
```python
{
    "faiss-cpu>=1.7.0": "In-memory vector search",
    "pinecone-client>=3.0.0": "Cloud vector database",
    "sentence-transformers>=2.2.0": "Embedding models",
    "numpy>=1.21.0": "Numerical operations"
}
```

**Installation**:
```bash
# Local vector store (FAISS)
pip install codex-ml[rag] faiss-cpu

# Cloud vector store (Pinecone)
pip install codex-ml[rag] pinecone-client

# Or include with runtime
pip install codex-ml[runtime]
```

**Usage Example 1: Local Vector Search**:
```python
from codex_ml.serving.inference_server import InferenceServer
import faiss
import numpy as np

# Initialize embedding model
server = InferenceServer()
embeddings = server.get_embeddings(["doc1", "doc2", "doc3"])

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype('float32'))

# Search
query_embedding = server.get_embeddings(["search query"])
distances, indices = index.search(query_embedding.astype('float32'), k=3)
print(f"Top 3 matches: {indices[0]}")
```

**Usage Example 2: LangChain Integration**:
```python
try:
    from langchain.vectorstores import FAISS
    from langchain.embeddings import HuggingFaceEmbeddings
    
    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create vector store
    vector_store = FAISS.from_documents(
        documents=docs,
        embedding=embeddings
    )
    
    # Retrieve similar documents
    results = vector_store.similarity_search("query", k=5)
    
except ImportError:
    print("LangChain not installed. Install: pip install langchain")
```

**Usage Example 3: Pinecone Cloud Storage**:
```python
try:
    from pinecone import Pinecone
    
    # Initialize Pinecone
    pc = Pinecone(api_key="YOUR_API_KEY")
    index = pc.Index("your-index")
    
    # Upsert embeddings
    index.upsert(vectors=[
        ("doc1", embedding1, {"text": "Document 1"}),
        ("doc2", embedding2, {"text": "Document 2"}),
    ])
    
    # Query
    results = index.query(query_embedding, top_k=5)
    
except ImportError:
    print("Pinecone not installed. Install: pip install pinecone-client")
```

### Retrieval Frameworks

**Feature**: Structured retrieval pipelines for knowledge integration

**Dependencies**:
```python
{
    "langchain>=0.1.0": "LLM framework with retrieval chains",
    "llama-index>=0.9.0": "Data indexing and retrieval",
    "haystack>=1.0.0": "Production retrieval pipeline"
}
```

**Installation**:
```bash
pip install codex-ml[rag] langchain llama-index
```

**Usage Example: LangChain Retrieval Chain**:
```python
try:
    from langchain.chains import RetrievalQA
    from langchain.vectorstores import FAISS
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.llms import HuggingFacePipeline
    
    # Setup components
    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_documents(docs, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Create QA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    # Query
    result = qa.run("What is X?")
    
except ImportError:
    print("LangChain not installed. Install: pip install langchain")
```

---

## Cognitive Brain Features

### Autonomous Reasoning Engine

**Feature**: Multi-step reasoning with uncertainty quantification

**Dependencies**:
```python
{
    "torch>=2.0.0": "Deep learning framework",
    "transformers>=4.30.0": "Pre-trained models",
    "duckdb>=0.8.0": "Pattern storage and retrieval"
}
```

**Installation**:
```bash
pip install codex-ml[cognitive]
```

**Usage Example: Decision-Making**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger

# Initialize cognitive engine
logger = CodexLogger(experiment_name="reasoning-test")

# Log reasoning steps
logger.log_event(
    name="reasoning_step",
    properties={
        "step": 1,
        "hypothesis": "Pattern A suggests action B",
        "confidence": 0.85
    }
)

# Query learned patterns
patterns = logger.query_patterns("action_B")
for pattern in patterns:
    print(f"Pattern: {pattern['name']}, Confidence: {pattern['confidence']}")
```

### Multi-Agent Orchestration

**Feature**: Coordinate multiple agents for complex tasks

**Dependencies**:
```python
{
    "pydantic>=2.0": "Agent configuration",
    "asyncio": "Built-in async support",
    "duckdb>=0.8.0": "Agent state storage"
}
```

**Installation**:
```bash
pip install codex-ml[cognitive]
```

**Usage Example: Agent Coordination**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger
import asyncio

async def agent_task(agent_id: str, task: str, logger: CodexLogger):
    """Execute agent task and log results"""
    logger.log_event(
        name=f"agent_{agent_id}_task",
        properties={"agent_id": agent_id, "task": task, "status": "started"}
    )
    
    # Do work...
    result = await process_task(task)
    
    logger.log_event(
        name=f"agent_{agent_id}_task",
        properties={"agent_id": agent_id, "task": task, "status": "completed", "result": result}
    )

# Orchestrate multiple agents
logger = CodexLogger(experiment_name="multi-agent")
async def run_orchestration():
    await asyncio.gather(
        agent_task("agent1", "task1", logger),
        agent_task("agent2", "task2", logger),
        agent_task("agent3", "task3", logger)
    )

asyncio.run(run_orchestration())
```

---

## Memory Systems Features

### Short-Term Memory (STM)

**Feature**: Session-based pattern storage and recall

**Dependencies**:
```python
{
    "sqlite3": "Built-in persistent storage",
    "duckdb>=0.8.0": "Analytics queries (optional)"
}
```

**Installation**:
```bash
pip install codex-ml[memory]
```

**Usage Example: STM Consolidation**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger

# Create session logger (acts as STM)
logger = CodexLogger(
    experiment_name="learning-session",
    checkpoint_interval=10  # Consolidate every 10 events
)

# Store observations in STM
for i in range(100):
    logger.log_event(
        name="observation",
        properties={
            "step": i,
            "state": f"state_{i}",
            "reward": float(i) * 0.1
        }
    )
    
# Consolidate to LTM (automatic after checkpoint_interval)
# Query consolidated patterns
patterns = logger.query_patterns("state_*", limit=5)
print(f"Learned {len(patterns)} patterns")
```

### Long-Term Memory (LTM)

**Feature**: Persistent pattern storage across sessions

**Dependencies**:
```python
{
    "sqlite3": "Persistent storage",
    "duckdb>=0.8.0": "Analytics and compression",
    "pickle": "Serialization"
}
```

**Installation**:
```bash
pip install codex-ml[memory]
```

**Usage Example: LTM Cross-Session**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger

# Session 1: Learn patterns
logger1 = CodexLogger(experiment_name="training-session-1")
for i in range(50):
    logger1.log_event(
        name="learning",
        properties={"pattern": f"pattern_{i % 5}", "accuracy": 0.8 + i*0.001}
    )

# Session 2: Reuse learned patterns
logger2 = CodexLogger(experiment_name="training-session-2")
# Access patterns from previous session
patterns = logger2.query_patterns(experiment="training-session-1")
print(f"Retrieved {len(patterns)} patterns from previous session")
```

### Cache Management

**Feature**: Optimized caching for performance

**Dependencies**:
```python
{
    "cachetools>=5.0": "Advanced caching strategies",
    "lru-dict>=1.1.0": "LRU cache implementation"
}
```

**Installation**:
```bash
pip install codex-ml[memory] cachetools lru-dict
```

**Usage Example: Embedding Cache**:
```python
try:
    from cachetools import TTLCache
    from functools import wraps
    
    # Create cache with 1-hour TTL
    embedding_cache = TTLCache(maxsize=10000, ttl=3600)
    
    @wraps
    def cached_embedding(text: str):
        if text in embedding_cache:
            return embedding_cache[text]
        
        embedding = get_embedding(text)
        embedding_cache[text] = embedding
        return embedding
    
except ImportError:
    print("cachetools not installed. Install: pip install cachetools")
```

---

## Graceful Degradation

All optional features degrade gracefully when dependencies are missing. The system will:

1. Attempt to import the optional module
2. Catch `ModuleNotFoundError`, `ImportError`, or `AttributeError`
3. Set the module to `None` or provide a fallback implementation
4. Log a warning explaining what feature is unavailable

### Example: Checking Feature Availability

```python
from codex_ml.serving import inference_server
from codex_ml.monitoring import codex_logging

# Check RAG availability
try:
    import faiss
    print("RAG features available")
except ImportError:
    print("RAG features not available. Install: pip install codex-ml[rag]")

# Check Cognitive Brain availability
try:
    import torch
    print("Cognitive Brain available")
except ImportError:
    print("Cognitive Brain not available. Install: pip install codex-ml[cognitive]")

# Check Memory Systems availability
try:
    import duckdb
    print("Advanced memory systems available")
except ImportError:
    print("Memory systems available (basic SQLite only)")
```

### Example: Conditional Feature Usage

```python
import codex_ml

# Try to use RAG features
try:
    from codex_ml.serving.inference_server import InferenceServer
    server = InferenceServer(enable_rag=True)
except ImportError:
    print("RAG not available, using basic inference")
    server = InferenceServer(enable_rag=False)

# Application continues to work with degraded features
predictions = server.predict(input_data)
```

---

## Verification & Testing

### Verify Installation

```bash
# Check installed profile
python -c "import codex_ml; print(codex_ml.__version__)"

# List available features
python -c "
from codex_ml.serving import inference_server
from codex_ml.monitoring import codex_logging
import torch
try:
    import faiss
    print('✓ RAG features available')
except ImportError:
    print('✗ RAG features not available')
try:
    print('✓ Cognitive Brain available')
except ImportError:
    print('✗ Cognitive Brain not available')
print('✓ Memory systems available')
"
```

### Run Feature-Specific Tests

```bash
# Test RAG features
pytest tests/ -k "rag" -v

# Test Cognitive Brain
pytest tests/ -k "cognitive" -v

# Test Memory Systems
pytest tests/ -k "memory" -v

# Test all optional features
pytest tests/ -k "optional" -v
```

### Test with Minimal Installation

```bash
# Install core only
pip install codex-ml[core]

# Run smoke tests
pytest tests/smoke/ -v

# Try importing optional features (should handle gracefully)
python -c "
from codex_ml.serving import inference_server  # May warn
from codex_ml.monitoring import codex_logging  # May warn
print('Core functionality works')
"
```

---

## Common Issues

### Issue: ImportError for optional dependencies

**Symptom**: `ModuleNotFoundError: No module named 'torch'`

**Solution**:
```bash
# Install the appropriate profile
pip install codex-ml[runtime]  # For RAG and serving
pip install codex-ml[cognitive]  # For Cognitive Brain
pip install codex-ml[full]  # For everything
```

### Issue: CUDA/GPU not detected

**Symptom**: PyTorch uses CPU instead of GPU

**Solution**:
```bash
# Install CUDA-enabled PyTorch
pip install torch[cuda118]  # CUDA 11.8
# Or check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Issue: Vector store dimension mismatch

**Symptom**: `AssertionError: dimension mismatch`

**Solution**:
```python
# Ensure all embeddings have the same dimension
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_dim = len(model.encode("test"))  # Should be 384

# Use consistent dimension
embeddings = [model.encode(text) for text in documents]
```

### Issue: Memory growth with LTM consolidation

**Symptom**: Database size grows too large

**Solution**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger

# Enable automatic pruning
logger = CodexLogger(
    experiment_name="training",
    prune_old_patterns=True,  # Enable pruning
    retention_days=30  # Keep patterns for 30 days
)
```

---

## Integration with Installation Profiles

### Core + RAG
```bash
pip install codex-ml[core] faiss-cpu sentence-transformers
```

### Runtime + All Features
```bash
pip install codex-ml[runtime] langchain duckdb pinecone-client
```

### Full Production Setup
```bash
pip install codex-ml[full] torch[cuda118] mlflow wandb
```

---

## Additional Resources

- [Installation Guide](INSTALLATION.md)
- [API Reference](API_DOCUMENTATION.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [Performance Tuning](PERFORMANCE_TUNING.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Last Updated**: 2026-07-20  
**Maintained By**: Aries-Serpent  
**License**: MIT
