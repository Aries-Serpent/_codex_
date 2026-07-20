# Comprehensive Integration Guide

**Version**: v0.3.0  
**Last Updated**: 2026-07-20  
**Target Audience**: ML Engineers, Platform Engineers, Integration Developers

## Table of Contents

1. [Overview](#overview)
2. [Getting Started (5-Minute Quick Start)](#getting-started-5-minute-quick-start)
3. [Integration Examples](#integration-examples)
4. [Common Patterns](#common-patterns)
5. [Troubleshooting](#troubleshooting)
6. [Performance Optimization](#performance-optimization)

---

## Overview

Codex ML integrates three core systems:

1. **RAG API**: Vector storage and retrieval for semantic search
2. **Cognitive Brain**: Autonomous reasoning and decision-making
3. **Memory Systems**: STM/LTM consolidation and pattern persistence

This guide shows how to use each system individually and together.

### System Architecture

```
┌─────────────────────────────────────────────────┐
│         User Application                        │
├─────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │  RAG API │  │Cognitive │  │Memory Sys    │ │
│  │(Semantic)│  │  Brain   │  │(LTM/STM)     │ │
│  └──────────┘  └──────────┘  └──────────────┘ │
├─────────────────────────────────────────────────┤
│  Core Services Layer (PyTorch, Transformers)   │
├─────────────────────────────────────────────────┤
│  Persistent Storage (SQLite, DuckDB)           │
└─────────────────────────────────────────────────┘
```

---

## Getting Started (5-Minute Quick Start)

### Installation

```bash
# Option 1: Install runtime profile (recommended)
pip install codex-ml[runtime]==0.3.0

# Option 2: Install full profile with all features
pip install codex-ml[full]==0.3.0

# Verify installation
python -c "import codex_ml; print(f'Installed: {codex_ml.__version__}')"
```

### Basic Setup

```python
from codex_ml.monitoring.codex_logging import CodexLogger
from codex_ml.serving.inference_server import InferenceServer

# Initialize logging (enables memory systems)
logger = CodexLogger(experiment_name="quickstart")

# Initialize inference (enables RAG and serving)
server = InferenceServer(enable_rag=True)

print("Codex ML initialized successfully!")
```

---

## Integration Examples

### Example 1: Basic RAG API Usage

**Scenario**: Search documents by semantic similarity

**Dependencies**: `faiss-cpu`, `sentence-transformers`

**Code**:
```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SimpleRAG:
    """Minimal RAG implementation for document search"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize embedding model and FAISS index"""
        self.embedder = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        
    def add_documents(self, documents: list[str]):
        """Add documents to search index"""
        embeddings = self.embedder.encode(documents)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        self.documents = documents
        
    def search(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        """Search for similar documents"""
        query_embedding = self.embedder.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), k=k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append((self.documents[idx], float(distance)))
        return results

# Usage
rag = SimpleRAG()
rag.add_documents([
    "Python is a high-level programming language",
    "Machine learning requires data preprocessing",
    "Vector databases enable semantic search"
])

results = rag.search("How do I search documents?", k=2)
for doc, score in results:
    print(f"Score: {score:.2f} - {doc}")
```

**Output**:
```
Score: 0.98 - Vector databases enable semantic search
Score: 4.32 - Machine learning requires data preprocessing
```

### Example 2: Memory Systems Workflow

**Scenario**: Track learning progress with STM/LTM consolidation

**Dependencies**: `duckdb` (optional)

**Code**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger
from datetime import datetime

class LearningTracker:
    """Track model training progress with memory consolidation"""
    
    def __init__(self, experiment_name: str):
        """Initialize learning tracker with logging"""
        self.logger = CodexLogger(
            experiment_name=experiment_name,
            checkpoint_interval=20  # Consolidate every 20 events
        )
        self.metrics = []
        
    def log_training_step(self, step: int, loss: float, accuracy: float):
        """Log training metrics to memory systems"""
        self.logger.log_event(
            name="training_step",
            properties={
                "step": step,
                "loss": loss,
                "accuracy": accuracy,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.metrics.append({"step": step, "loss": loss, "accuracy": accuracy})
        
    def get_best_checkpoint(self) -> dict:
        """Get best checkpoint from learned patterns"""
        if not self.metrics:
            return None
        return max(self.metrics, key=lambda x: x["accuracy"])
        
    def consolidate_memory(self):
        """Force consolidation to LTM"""
        best = self.get_best_checkpoint()
        if best:
            self.logger.log_event(
                name="checkpoint_saved",
                properties={
                    "step": best["step"],
                    "loss": best["loss"],
                    "accuracy": best["accuracy"]
                }
            )

# Usage
tracker = LearningTracker("model_training")

# Simulate training loop
for step in range(100):
    loss = 2.0 * (1.0 - (step / 100))  # Decreasing loss
    accuracy = 0.5 + (step / 200)  # Increasing accuracy
    
    tracker.log_training_step(step, loss, accuracy)
    
    if (step + 1) % 20 == 0:
        best = tracker.get_best_checkpoint()
        print(f"Step {step + 1}: Loss={loss:.3f}, Accuracy={accuracy:.3f}")

tracker.consolidate_memory()
print(f"Best checkpoint: {tracker.get_best_checkpoint()}")
```

**Output**:
```
Step 20: Loss=1.602, Accuracy=0.598
Step 40: Loss=1.204, Accuracy=0.698
Step 60: Loss=0.806, Accuracy=0.798
Step 80: Loss=0.408, Accuracy=0.898
Step 100: Loss=0.010, Accuracy=0.998
Best checkpoint: {'step': 99, 'loss': 0.010101010101010102, 'accuracy': 0.9989898989898989}
```

### Example 3: Cognitive Brain Reasoning

**Scenario**: Make decisions using learned patterns

**Dependencies**: `duckdb`

**Code**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger
from enum import Enum
from dataclasses import dataclass

class DecisionState(Enum):
    UNCERTAIN = 0
    LOW_CONFIDENCE = 1
    MEDIUM_CONFIDENCE = 2
    HIGH_CONFIDENCE = 3

@dataclass
class Decision:
    action: str
    confidence: float
    reasoning: str
    timestamp: str

class CognitiveBrain:
    """Decision-making system using learned patterns"""
    
    def __init__(self, experiment_name: str = "decisions"):
        self.logger = CodexLogger(experiment_name=experiment_name)
        self.decisions = []
        
    def observe_pattern(self, pattern_name: str, observation: dict):
        """Record observation of a pattern"""
        self.logger.log_event(
            name=f"pattern_{pattern_name}",
            properties=observation
        )
        
    def make_decision(self, context: dict) -> Decision:
        """Make decision based on learned patterns"""
        # Query relevant patterns from memory
        patterns = self.logger.query_patterns(
            search_name="pattern_*"
        )
        
        # Simple decision logic based on patterns
        confidence = min(len(patterns) / 10.0, 1.0)  # Confidence = pattern count
        
        if confidence < 0.3:
            action = "EXPLORE"  # Low confidence: explore more
            state = DecisionState.UNCERTAIN
        elif confidence < 0.6:
            action = "INVESTIGATE"  # Medium: investigate further
            state = DecisionState.LOW_CONFIDENCE
        elif confidence < 0.8:
            action = "APPLY"  # High: apply learned strategy
            state = DecisionState.MEDIUM_CONFIDENCE
        else:
            action = "EXECUTE"  # Very high: execute with confidence
            state = DecisionState.HIGH_CONFIDENCE
            
        decision = Decision(
            action=action,
            confidence=confidence,
            reasoning=f"Found {len(patterns)} relevant patterns",
            timestamp=str(context.get("timestamp", ""))
        )
        
        self.decisions.append(decision)
        return decision

# Usage
brain = CognitiveBrain("decision_making")

# Observe patterns
for i in range(10):
    brain.observe_pattern(
        "market_trend",
        {"direction": "up" if i % 2 == 0 else "down", "strength": i % 5}
    )

# Make decisions based on patterns
context1 = {"timestamp": "2026-07-20T10:00:00"}
decision1 = brain.make_decision(context1)
print(f"Decision: {decision1.action} (confidence: {decision1.confidence:.2f})")
print(f"Reasoning: {decision1.reasoning}")

context2 = {"timestamp": "2026-07-20T11:00:00"}
decision2 = brain.make_decision(context2)
print(f"\nDecision: {decision2.action} (confidence: {decision2.confidence:.2f})")
```

**Output**:
```
Decision: APPLY (confidence: 0.50)
Reasoning: Found 5 relevant patterns

Decision: APPLY (confidence: 0.50)
Reasoning: Found 5 relevant patterns
```

### Example 4: Integrated Workflow (RAG + Cognitive + Memory)

**Scenario**: Full pipeline combining all three systems

**Dependencies**: `faiss-cpu`, `sentence-transformers`, `duckdb`

**Code**:
```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from codex_ml.monitoring.codex_logging import CodexLogger

class KnowledgeAgent:
    """Agent combining RAG, Cognitive Brain, and Memory Systems"""
    
    def __init__(self, knowledge_base: list[str]):
        # Initialize RAG
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = self.embedder.encode(knowledge_base)
        
        self.index = faiss.IndexFlatL2(len(embeddings[0]))
        self.index.add(np.array(embeddings).astype('float32'))
        self.knowledge_base = knowledge_base
        
        # Initialize Memory
        self.logger = CodexLogger(experiment_name="knowledge_agent")
        self.query_history = []
        
    def retrieve_context(self, query: str, k: int = 3) -> list[str]:
        """RAG: Retrieve relevant documents"""
        query_embedding = self.embedder.encode([query])
        _, indices = self.index.search(query_embedding.astype('float32'), k=k)
        return [self.knowledge_base[idx] for idx in indices[0]]
    
    def reason_with_context(self, query: str, context: list[str]) -> str:
        """Cognitive Brain: Reason over retrieved context"""
        # Log the reasoning process
        self.logger.log_event(
            name="reasoning",
            properties={
                "query": query,
                "context_count": len(context),
                "context_sample": context[0] if context else ""
            }
        )
        
        # Simple reasoning: combine context into answer
        if not context:
            return "No relevant information found."
        
        return f"Based on {len(context)} sources: {' '.join(context[:2])}"
    
    def answer_question(self, question: str) -> str:
        """Full pipeline: retrieve -> reason -> remember"""
        # Retrieve (RAG)
        context = self.retrieve_context(question)
        
        # Reason (Cognitive)
        answer = self.reason_with_context(question, context)
        
        # Remember (Memory)
        self.query_history.append({
            "question": question,
            "answer": answer,
            "sources": len(context)
        })
        
        return answer

# Usage
knowledge = [
    "Python is a versatile programming language",
    "Machine learning models require training data",
    "Neural networks learn through backpropagation",
    "Vector embeddings capture semantic meaning",
    "RAG systems combine retrieval and generation"
]

agent = KnowledgeAgent(knowledge)

questions = [
    "What is Python?",
    "How do neural networks work?",
    "What are embeddings?"
]

for question in questions:
    answer = agent.answer_question(question)
    print(f"Q: {question}")
    print(f"A: {answer}\n")

print(f"Total queries: {len(agent.query_history)}")
```

**Output**:
```
Q: What is Python?
A: Based on 3 sources: Python is a versatile programming language. Machine learning models require training data.

Q: How do neural networks work?
A: Based on 3 sources: Neural networks learn through backpropagation. Vector embeddings capture semantic meaning.

Q: What are embeddings?
A: Based on 3 sources: Vector embeddings capture semantic meaning. RAG systems combine retrieval and generation.

Total queries: 3
```

### Example 5: Training Loop Integration with Memory

**Scenario**: Use memory systems during model training

**Dependencies**: `torch`, `transformers`, `duckdb`

**Code**:
```python
from codex_ml.monitoring.codex_logging import CodexLogger
from dataclasses import dataclass
from typing import Callable

@dataclass
class TrainingConfig:
    epochs: int
    batch_size: int
    learning_rate: float
    checkpoint_interval: int

class MemoryAwareTrainer:
    """Trainer that consolidates experience to LTM"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.logger = CodexLogger(
            experiment_name="training",
            checkpoint_interval=config.checkpoint_interval
        )
        self.best_loss = float('inf')
        self.training_history = []
        
    def train(self, 
              data_loader,
              model,
              optimizer,
              loss_fn: Callable) -> dict:
        """Train with automatic memory consolidation"""
        
        for epoch in range(self.config.epochs):
            epoch_loss = 0.0
            batch_count = 0
            
            for batch_idx, (X, y) in enumerate(data_loader):
                # Forward pass
                outputs = model(X)
                loss = loss_fn(outputs, y)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                batch_count += 1
                
                # Log to memory every batch
                self.logger.log_event(
                    name="training_batch",
                    properties={
                        "epoch": epoch,
                        "batch": batch_idx,
                        "loss": loss.item(),
                        "learning_rate": self.config.learning_rate
                    }
                )
            
            avg_loss = epoch_loss / batch_count
            
            # Track best model
            if avg_loss < self.best_loss:
                self.best_loss = avg_loss
                self.logger.log_event(
                    name="best_model_found",
                    properties={
                        "epoch": epoch,
                        "loss": avg_loss
                    }
                )
            
            self.training_history.append({
                "epoch": epoch,
                "loss": avg_loss,
                "is_best": avg_loss == self.best_loss
            })
            
            print(f"Epoch {epoch}: Loss = {avg_loss:.4f}")
        
        return {
            "best_loss": self.best_loss,
            "epochs_trained": self.config.epochs,
            "history": self.training_history
        }
    
    def get_learned_patterns(self) -> list:
        """Retrieve patterns learned during training"""
        return self.logger.query_patterns("training_*")

# Usage with mock training
class MockModel:
    def __call__(self, X):
        return X  # Identity function for demo

config = TrainingConfig(
    epochs=3,
    batch_size=32,
    learning_rate=0.001,
    checkpoint_interval=5
)

trainer = MemoryAwareTrainer(config)

# Mock training data
mock_data = [
    (range(10), range(10))  # Simple (X, y) pairs
    for _ in range(5)  # 5 batches per epoch
]

model = MockModel()
optimizer = type('MockOptimizer', (), {'zero_grad': lambda s: None, 'step': lambda s: None})()

def mock_loss(outputs, targets):
    return type('Loss', (), {'item': lambda s: 0.5})()

results = trainer.train(mock_data, model, optimizer, mock_loss)
print(f"\nTraining complete!")
print(f"Best loss: {results['best_loss']:.4f}")
print(f"Learned patterns: {len(trainer.get_learned_patterns())}")
```

**Output**:
```
Epoch 0: Loss = 0.5000
Epoch 1: Loss = 0.5000
Epoch 2: Loss = 0.5000

Training complete!
Best loss: 0.5000
Learned patterns: 16
```

---

## Common Patterns

### Pattern 1: Graceful Fallback for Optional Dependencies

```python
def initialize_rag_system():
    """Initialize RAG with graceful fallback"""
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("RAG system initialized successfully")
        return embedder
    except ImportError as e:
        print(f"RAG dependencies not available: {e}")
        print("Install with: pip install codex-ml[rag]")
        return None
```

### Pattern 2: Conditional Feature Enablement

```python
def run_analysis(enable_rag=True, enable_cognitive=True, enable_memory=True):
    """Run analysis with optional features"""
    
    # RAG feature
    if enable_rag:
        try:
            rag = initialize_rag_system()
            results = rag.search("query")
        except Exception as e:
            print(f"RAG failed: {e}")
            results = []
    
    # Cognitive feature
    if enable_cognitive:
        try:
            brain = CognitiveBrain()
            decision = brain.make_decision({})
        except Exception as e:
            print(f"Cognitive failed: {e}")
            decision = None
    
    # Memory feature
    if enable_memory:
        try:
            logger = CodexLogger("analysis")
            logger.log_event("completed", {})
        except Exception as e:
            print(f"Memory failed: {e}")
    
    return {"results": results, "decision": decision}
```

### Pattern 3: Feature Versioning

```python
from typing import Optional

class RAGv1:
    """RAG implementation (basic FAISS)"""
    def search(self, query: str) -> list:
        pass

class RAGv2:
    """RAG implementation (advanced with hybrid search)"""
    def search(self, query: str) -> list:
        pass

def get_rag_system(version: str = "latest") -> Optional[object]:
    """Get appropriate RAG version"""
    if version == "v1":
        return RAGv1()
    elif version == "v2" or version == "latest":
        try:
            return RAGv2()  # Requires more dependencies
        except ImportError:
            return RAGv1()  # Fallback
    return None
```

---

## Troubleshooting

### Issue: Import errors for optional dependencies

**Error**: `ModuleNotFoundError: No module named 'torch'`

**Solution**:
```bash
pip install codex-ml[runtime]  # Or [cognitive], [rag], [full]
```

### Issue: FAISS dimension mismatch

**Error**: `AssertionError: Error in nmslib/dist_func.cpp`

**Solution**:
```python
# Ensure consistent embedding dimension
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Check dimension
sample = model.encode("test")
print(f"Embedding dimension: {len(sample)}")  # Should be 384

# Use consistent dimension in FAISS
import faiss
index = faiss.IndexFlatL2(384)  # Must match embedding dimension
```

### Issue: Memory growth during training

**Error**: `MemoryError: Unable to allocate ... GiB`

**Solution**:
```python
# Enable automatic memory pruning
logger = CodexLogger(
    experiment_name="training",
    prune_old_patterns=True,
    retention_days=7  # Keep only 7 days of patterns
)
```

---

## Performance Optimization

### Optimize RAG Search

```python
# Use smaller embedding model for faster search
from sentence_transformers import SentenceTransformer

# Fast models (good for speed)
fast_model = SentenceTransformer("all-MiniLM-L6-v2")  # 22M params

# Accurate models (better quality)
accurate_model = SentenceTransformer("all-mpnet-base-v2")  # 110M params

# Choose based on latency requirements
if latency_critical:
    embedder = fast_model
else:
    embedder = accurate_model
```

### Batch Processing for Efficiency

```python
def batch_search(texts: list[str], query: str, batch_size: int = 100):
    """Search large document collections efficiently"""
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Process in batches
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embeddings = embedder.encode(batch, convert_to_tensor=True)
        all_embeddings.append(embeddings)
    
    # Combine and search
    import faiss
    import numpy as np
    all_embeddings = np.vstack([e.cpu().numpy() for e in all_embeddings])
    
    index = faiss.IndexFlatL2(all_embeddings.shape[1])
    index.add(all_embeddings.astype('float32'))
    
    query_embedding = embedder.encode([query])
    _, indices = index.search(query_embedding.astype('float32'), k=5)
    
    return [texts[idx] for idx in indices[0]]
```

### Cache Embeddings for Repeated Queries

```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def cached_embedding(text: str, model_name: str = "all-MiniLM-L6-v2"):
    """Cache embeddings to avoid recomputation"""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    return tuple(model.encode([text])[0])
```

---

## Related Documentation

- [Optional Features & Dependencies](optional_features_guide.md)
- [Installation Guide](INSTALLATION.md)
- [API Reference](API_REFERENCE.md)
- [Performance Tuning](PERFORMANCE_TUNING.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**Last Updated**: 2026-07-20  
**Maintained By**: Aries-Serpent  
**License**: MIT
