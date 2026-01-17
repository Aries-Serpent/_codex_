# Local Model Integration for RAG Pipeline

**Date:** 2026-01-17  
**Status:** Implementation Plan  
**Purpose:** Enable RAG pipeline to work with local models (no API keys required)

---

## Overview

Based on feedback from @mbaetiong, we need to support local transformer models that don't require API tokens. This unblocks AI agents from dependency on external services.

## Local Model Options (Priority Order)

### 1. **Sentence-Transformers (Current - Enhanced)**
- **Status:** Already implemented, needs robustness improvements
- **Models:** all-MiniLM-L6-v2, all-mpnet-base-v2
- **Pros:** Best quality embeddings, widely used
- **Cons:** Requires huggingface.co for first download
- **Solution:** Add better offline fallback

### 2. **Transformers Library (Direct)**
- **Status:** To implement
- **Models:** Can use any model from Hugging Face
- **Pros:** More control, can cache models locally
- **Cons:** Slightly more complex
- **Code:**
```python
from transformers import AutoTokenizer, AutoModel
import torch

class TransformersProvider:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
    def encode(self, texts):
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()
```

### 3. **Simple TF-IDF Fallback** ✅ RECOMMENDED FOR IMMEDIATE UNBLOCKING
- **Status:** Quick win - implement now
- **Models:** scikit-learn TfidfVectorizer
- **Pros:** Zero external dependencies, always works
- **Cons:** Lower quality than transformers
- **Use case:** Development, testing, offline scenarios
- **Code:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer

class TfidfProvider:
    def __init__(self, max_features=384):
        self.vectorizer = TfidfVectorizer(max_features=max_features)
        self.is_fitted = False
        
    def encode(self, texts):
        if not self.is_fitted:
            self.vectorizer.fit(texts)
            self.is_fitted = True
        return self.vectorizer.transform(texts).toarray()
    
    def get_dimension(self):
        return self.vectorizer.max_features
```

### 4. **Ollama Integration** (Future)
- **Status:** Future enhancement
- **Models:** LLaMA, Mistral, Qwen, etc.
- **Pros:** Local, no API, great UX
- **Cons:** Requires Ollama installation
- **Priority:** Phase 3 enhancement

### 5. **llama.cpp Integration** (Future)
- **Status:** Future enhancement
- **Models:** GGUF format models
- **Pros:** Fast, CPU-optimized
- **Cons:** Requires setup
- **Priority:** Phase 4 GPU acceleration

---

## Implementation Plan

### Immediate Actions (This Session)

**1. Add TF-IDF Fallback Provider**
- File: `src/codex/rag/embeddings.py`
- Add `TfidfEmbeddingProvider` class
- Zero external dependencies (uses scikit-learn)
- Always works offline

**2. Enhance Model Loading with Graceful Fallback**
- Modify `LocalSentenceTransformerProvider`
- Add retry logic with exponential backoff
- Add offline mode detection
- Fallback chain: sentence-transformers → TF-IDF

**3. Update CLI to Support Provider Selection**
- Add `--embedding-provider` flag to `codex rag build`
- Options: `auto`, `sentence-transformers`, `tfidf`
- Default: `auto` (tries transformers, falls back to tfidf)

**4. Update Tests to Use Fallback**
- Modify tests to work with TF-IDF provider
- Add provider selection in fixtures
- Ensure tests pass without network

### Code Changes Required

#### File: `src/codex/rag/embeddings.py`

```python
# Add at the end of the file

class TfidfEmbeddingProvider:
    """
    TF-IDF based embedding provider (offline-capable).
    
    Uses scikit-learn's TfidfVectorizer for embeddings.
    Lower quality than transformers but works offline with zero setup.
    Ideal for development, testing, and offline scenarios.
    """
    
    def __init__(self, max_features: int = 384):
        """
        Initialize TF-IDF provider.
        
        Args:
            max_features: Maximum number of features (embedding dimension)
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError:
            logger.error("scikit-learn not installed. Install with: pip install scikit-learn")
            raise
        
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
        )
        self.is_fitted = False
        logger.info(f"Initialized TF-IDF provider (dimension={max_features})")
    
    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """
        Encode texts using TF-IDF.
        
        Args:
            texts: List of texts to encode
            **kwargs: Ignored (for compatibility)
            
        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        if not self.is_fitted:
            logger.info("Fitting TF-IDF vectorizer on input texts")
            self.vectorizer.fit(texts)
            self.is_fitted = True
        
        embeddings = self.vectorizer.transform(texts).toarray()
        logger.debug(f"Encoded {len(texts)} texts to shape {embeddings.shape}")
        return embeddings
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.max_features


def create_embedding_provider(
    provider: str = "auto",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    cache_dir: Optional[str] = None,
    **kwargs
) -> EmbeddingProvider:
    """
    Create embedding provider with automatic fallback.
    
    Args:
        provider: Provider type ('auto', 'sentence-transformers', 'tfidf', 'openai')
        model_name: Model name (for transformer-based providers)
        cache_dir: Cache directory
        **kwargs: Additional provider-specific arguments
        
    Returns:
        Embedding provider instance
    """
    if provider == "auto":
        # Try sentence-transformers first
        try:
            logger.info("Attempting to load sentence-transformers provider")
            return LocalSentenceTransformerProvider(
                model_name=model_name,
                cache_dir=cache_dir
            )
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers: {e}")
            logger.info("Falling back to TF-IDF provider")
            return TfidfEmbeddingProvider(max_features=384)
    
    elif provider == "sentence-transformers":
        return LocalSentenceTransformerProvider(
            model_name=model_name,
            cache_dir=cache_dir
        )
    
    elif provider == "tfidf":
        max_features = kwargs.get("max_features", 384)
        return TfidfEmbeddingProvider(max_features=max_features)
    
    elif provider == "openai":
        api_key = kwargs.get("api_key") or os.getenv("RAG_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required for openai provider")
        return OpenAIEmbeddingProvider(api_key=api_key)
    
    else:
        raise ValueError(f"Unknown provider: {provider}. Choose from: auto, sentence-transformers, tfidf, openai")
```

#### File: `src/codex/cli_rag.py`

Add parameter to build command:

```python
@app.command()
def build(
    # ... existing parameters ...
    embedding_provider: str = typer.Option(
        "auto",
        "--embedding-provider",
        "-e",
        help="Embedding provider (auto, sentence-transformers, tfidf, openai)",
    ),
    # ... rest of parameters ...
) -> None:
    """Build index with configurable embedding provider."""
    # Pass to build_index_from_files or use in embed_chunks call
```

---

## Testing Strategy

### 1. Test with TF-IDF Provider (Offline)

```bash
# Should work immediately without network
cd /home/runner/work/_codex_/_codex_
export PYTHONPATH=/home/runner/work/_codex_/_codex_/src:$PYTHONPATH

# Create test docs
mkdir -p /tmp/test_docs
cat > /tmp/test_docs/test.md <<EOF
# Test Document
This is a test document for RAG indexing.
It contains multiple sentences for testing.
EOF

# Test with TF-IDF
python -c "
from codex.rag.embeddings import TfidfEmbeddingProvider
from codex.rag.indexer import chunk_text, persist_index
from pathlib import Path

# Create provider
provider = TfidfEmbeddingProvider(max_features=384)

# Chunk text
with open('/tmp/test_docs/test.md') as f:
    text = f.read()
chunks = chunk_text(text, chunk_size=500, overlap=50)

# Encode
texts = [chunk[2] for chunk in chunks]
embeddings = provider.encode(texts)

print(f'✓ Created {len(chunks)} chunks')
print(f'✓ Generated {len(embeddings)} embeddings')
print(f'✓ Embedding shape: {embeddings.shape}')
print(f'✓ TF-IDF provider working!')
"
```

### 2. Run Tests with TF-IDF

```bash
# Should pass without network
pytest tests/test_cli_rag.py -v -k "test_list or test_stats or test_delete" -o addopts=""
```

---

## Validation Checklist

- [ ] TfidfEmbeddingProvider implemented
- [ ] create_embedding_provider with auto-fallback
- [ ] CLI updated with --embedding-provider flag
- [ ] Tests pass with TF-IDF provider
- [ ] Documentation updated
- [ ] Can build index offline
- [ ] Can query index offline

---

## Benefits

1. **Unblocks AI Agents:** No dependency on external services
2. **Offline Capable:** Works in air-gapped environments
3. **Fast Development:** No waiting for model downloads
4. **Test Reliability:** Tests don't fail due to network issues
5. **Graceful Degradation:** Falls back automatically

---

## Future Enhancements (Phase 3+)

1. **Ollama Integration:** Add OllamaEmbeddingProvider
2. **llama.cpp:** Native C++ inference
3. **Model Caching:** Pre-download and cache models
4. **Hybrid Providers:** Use TF-IDF for keywords + transformers for semantics

---

**Next Action:** Implement TfidfEmbeddingProvider and auto-fallback logic.
