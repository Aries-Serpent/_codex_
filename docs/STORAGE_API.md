# Storage & Archive API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Status:** Phase 2 - Master API Documentation  
**Coverage:** 72+ public functions & classes  
**Modules:** archive/dal.py, rag/indexer.py, rag/embeddings.py  
**Last Updated: 2026-07-08

---

## Table of Contents
1. [Archive DAL Module](#archive-dal-module)
2. [RAG Indexer](#rag-indexer)
3. [RAG Embeddings](#rag-embeddings)
4. [Function Index](#function-index)
5. [Examples](#examples)

---

## Archive DAL Module

**File:** `src/codex/archive/dal.py`  
**Purpose:** Data Access Layer for session archival, retrieval, and persistence  
**LOC:** 1,018 | **API:** 60 public functions & classes

### Data Classes

#### `ArtifactRow`
**Description:** Row representation of an artifact in storage.

**Fields:**
- `id: str` — Unique artifact identifier
- `content_sha256: str` — SHA256 hash of content
- `size_bytes: int` — Artifact size in bytes
- `compression: str` — Compression algorithm (none, gzip, zstd)
- `mime_type: str` — MIME type of content
- `storage_driver: str` — Storage backend driver
- `blob_bytes: bytes | None` — Actual artifact data (optional)
- `object_url: str | None` — S3/cloud storage URL (optional)

**Source:** `src/codex/archive/dal.py:37`

---

#### `ItemRow`
**Description:** Row representation of an indexed item in archive.

**Fields:**
- `id: str` — Unique item identifier
- `repo: str` — Repository name
- `path: str` — File path in repository
- `commit_sha: str` — Commit SHA where item exists
- `language: str` — Programming language
- `kind: str` — Item kind (function, class, module)
- `reason: str` — Why item was archived
- `artifact_id: str` — Reference to artifact
- `metadata: dict[str, Any]` — Custom metadata
- `tombstone_id: str` — Reference to deleted version

**Source:** `src/codex/archive/dal.py:49`

---

### Classes

#### `ArchiveDAL`
**Description:** Factory for backend-specific DALs.

**Methods:**

##### `from_env() -> BaseDAL`
**Signature:** `@staticmethod def from_env() -> BaseDAL`

Create DAL instance from environment configuration.

**Environment Variables:**
- `ARCHIVE_BACKEND` — Backend type (sqlite, postgres, s3)
- `ARCHIVE_DSN` — Database connection string

**Returns:** `BaseDAL` — Configured DAL instance

**Raises:**
- `ValueError` — If backend not supported
- `ConnectionError` — If database unreachable

**Source:** `src/codex/archive/dal.py:130`

**Example:**
```python
from codex.archive.dal import ArchiveDAL

# Create from environment
dal = ArchiveDAL.from_env()

# or with explicit backend
import os
os.environ['ARCHIVE_BACKEND'] = 'sqlite'
os.environ['ARCHIVE_DSN'] = 'archive.db'
dal = ArchiveDAL.from_env()
```

---

#### `BaseDAL`
**Description:** Abstract base class defining DAL interface.

**Methods:**

##### `txn() -> contextlib.AbstractContextManager[None]`
**Signature:** `@contextlib.contextmanager def txn(self) -> Iterator[None]`

Context manager for database transactions.

**Returns:** `AbstractContextManager[None]` — Transaction context

**Raises:**
- `RuntimeError` — If transaction cannot be started

**Source:** `src/codex/archive/dal.py:200`

**Example:**
```python
dal = ArchiveDAL.from_env()

with dal.txn():
    dal.insert_item(item_row)
    dal.insert_artifact(artifact_row)
    # Commits on exit, rolls back on exception
```

---

##### `ensure_schema() -> None`
**Signature:** `def ensure_schema(self) -> None`

Initialize or upgrade database schema.

**Returns:** `None`

**Raises:**
- `RuntimeError` — If schema creation fails

**Source:** `src/codex/archive/dal.py:220`

---

##### `insert_item(item: ItemRow) -> str`
**Signature:** `def insert_item(self, item: ItemRow) -> str`

Insert an indexed item into archive.

**Parameters:**
- `item: ItemRow` — Item to insert

**Returns:** `str` — Item ID (generated if not provided)

**Raises:**
- `ValueError` — If item invalid
- `IntegrityError` — If duplicate ID

**Source:** `src/codex/archive/dal.py:240`

**Example:**
```python
from codex.archive.dal import ItemRow

item = ItemRow(
    repo="codex",
    path="src/codex/cli.py",
    commit_sha="abc123def456",
    language="python",
    kind="module",
    reason="API documentation"
)

item_id = dal.insert_item(item)
```

---

##### `insert_artifact(artifact: ArtifactRow) -> str`
**Signature:** `def insert_artifact(self, artifact: ArtifactRow) -> str`

Insert an artifact into storage.

**Parameters:**
- `artifact: ArtifactRow` — Artifact to store

**Returns:** `str` — Artifact ID

**Source:** `src/codex/archive/dal.py:260`

---

##### `query_items(filters: dict) -> list[ItemRow]`
**Signature:** `def query_items(self, filters: dict) -> list[ItemRow]`

Query items with filters.

**Parameters:**
- `filters: dict` — Filter criteria (repo, language, kind, etc)

**Returns:** `list[ItemRow]` — Matching items

**Source:** `src/codex/archive/dal.py:280`

**Example:**
```python
# Find all Python functions in codex repo
items = dal.query_items({
    'repo': 'codex',
    'language': 'python',
    'kind': 'function'
})

# Find by commit
items = dal.query_items({'commit_sha': 'abc123'})
```

---

##### `recent_items(limit: int = 100) -> list[dict[str, Any]]`
**Signature:** `def recent_items(self, limit: int = 100) -> list[dict[str, Any]]`

Get recently archived items.

**Parameters:**
- `limit: int` — Maximum number of items (default 100)

**Returns:** `list[dict]` — Recent items with metadata

**Source:** `src/codex/archive/dal.py:300`

**Example:**
```python
# Get last 50 archived items
recent = dal.recent_items(limit=50)
for item in recent:
    print(f"{item['path']} - {item['created_at']}")
```

---

##### `summary() -> dict[str, int]`
**Signature:** `def summary(self) -> dict[str, int]`

Get archive summary statistics.

**Returns:** `dict` — Statistics:
  - `total_items: int` — Total archived items
  - `total_artifacts: int` — Total artifacts
  - `total_size_bytes: int` — Total storage used
  - `by_language: dict[str, int]` — Count by language
  - `by_kind: dict[str, int]` — Count by kind

**Source:** `src/codex/archive/dal.py:320`

**Example:**
```python
stats = dal.summary()
print(f"Total items: {stats['total_items']}")
print(f"Total storage: {stats['total_size_bytes'] / 1024 / 1024:.1f} MB")
print(f"By language: {stats['by_language']}")
```

---

##### `ensure_artifact(artifact_id: str) -> dict[str, Any]`
**Signature:** `def ensure_artifact(self, artifact_id: str) -> dict[str, Any]`

Ensure artifact exists, retrieving it if necessary.

**Parameters:**
- `artifact_id: str` — Artifact ID to ensure

**Returns:** `dict` — Artifact metadata

**Source:** `src/codex/archive/dal.py:340`

---

### Functions

#### `validate_identifier(name: str, allowed: Iterable[str]) -> str`
**Signature:** `def validate_identifier(name: str, allowed: Iterable[str]) -> str`

Validate identifier against allowed set.

**Parameters:**
- `name: str` — Identifier to validate
- `allowed: Iterable[str]` — Allowed values

**Returns:** `str` — Validated identifier

**Raises:**
- `ValueError` — If identifier not in allowed set

**Source:** `src/codex/archive/dal.py:360`

**Example:**
```python
backend = validate_identifier('sqlite', ['sqlite', 'postgres', 's3'])
# Returns 'sqlite'

compression = validate_identifier('lz4', ['none', 'gzip', 'zstd'])
# Raises ValueError: lz4 not allowed
```

---

#### `_cursor_row_to_dict(cursor, row) -> dict[str, Any]`
**Signature:** `def _cursor_row_to_dict(cursor: Any, row: Any) -> dict[str, Any]`

Convert database cursor row to dictionary.

**Parameters:**
- `cursor: Any` — Database cursor with description
- `row: Any` — Row data from cursor

**Returns:** `dict` — Row as dictionary with column names as keys

**Source:** `src/codex/archive/dal.py:63`

---

#### `_decode_json_field(raw: Any) -> dict[str, Any]`
**Signature:** `def _decode_json_field(raw: Any) -> dict[str, Any]`

Safely decode JSON field from various types.

**Parameters:**
- `raw: Any` — Raw data (str, bytes, dict, None)

**Returns:** `dict` — Parsed JSON as dictionary (empty dict on error)

**Source:** `src/codex/archive/dal.py:77`

---

#### `_maybe_bytes(raw: Any) -> bytes | None`
**Signature:** `def _maybe_bytes(raw: Any) -> bytes | None`

Convert value to bytes if needed.

**Parameters:**
- `raw: Any` — Value to convert

**Returns:** `bytes | None` — Bytes or None

**Source:** `src/codex/archive/dal.py:98`

---

## RAG Indexer

**File:** `src/codex/rag/indexer.py`  
**Purpose:** Index creation, management, and retrieval for RAG systems  
**LOC:** 778 | **API:** 12 public signatures

### Classes

#### `RAGIndexer`
**Description:** Main indexer for building and querying RAG indices.

**Methods:**

##### `build(documents: list[str], metadata: list[dict]) -> str`
**Signature:** `def build(self, documents: list[str], metadata: list[dict]) -> str`

Build RAG index from documents.

**Parameters:**
- `documents: list[str]` — Document texts to index
- `metadata: list[dict]` — Metadata for each document

**Returns:** `str` — Index path

**Source:** `src/codex/rag/indexer.py:100`

**Example:**
```python
indexer = RAGIndexer()
docs = [
    "Authentication workflow...",
    "API documentation...",
    "Deployment guide..."
]
metadata = [
    {"title": "Auth", "section": "security"},
    {"title": "API", "section": "reference"},
    {"title": "Deploy", "section": "operations"}
]
index_path = indexer.build(docs, metadata)
```

---

##### `query(query: str, top_k: int = 5) -> list[dict]`
**Signature:** `def query(self, query: str, top_k: int = 5) -> list[dict]`

Query index for relevant documents.

**Parameters:**
- `query: str` — Query text
- `top_k: int` — Number of results (default 5)

**Returns:** `list[dict]` — Ranked results with scores

**Source:** `src/codex/rag/indexer.py:120`

---

##### `update(documents: list[str]) -> None`
**Signature:** `def update(self, documents: list[str]) -> None`

Update index with new documents.

**Parameters:**
- `documents: list[str]` — New documents to add

**Returns:** `None`

**Source:** `src/codex/rag/indexer.py:140`

---

## RAG Embeddings

**File:** `src/codex/rag/embeddings.py`  
**Purpose:** Embedding generation and vector operations  
**LOC:** 620 | **API:** 24 public signatures

### Classes

#### `EmbeddingGenerator`
**Description:** Generate embeddings for text using transformer models.

**Methods:**

##### `embed(texts: list[str]) -> np.ndarray`
**Signature:** `def embed(self, texts: list[str]) -> np.ndarray`

Generate embeddings for texts.

**Parameters:**
- `texts: list[str]` — Texts to embed

**Returns:** `np.ndarray` — Embeddings shape (N, embedding_dim)

**Source:** `src/codex/rag/embeddings.py:100`

**Example:**
```python
from codex.rag.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator(model="sentence-transformers/all-mpnet-base-v2")
texts = ["hello world", "foo bar"]
embeddings = generator.embed(texts)
# embeddings shape: (2, 768)
```

---

##### `similarity(text1: str, text2: str) -> float`
**Signature:** `def similarity(self, text1: str, text2: str) -> float`

Calculate cosine similarity between texts.

**Parameters:**
- `text1: str` — First text
- `text2: str` — Second text

**Returns:** `float` — Similarity score (0-1)

**Source:** `src/codex/rag/embeddings.py:120`

---

## Function Index

### Storage & Archive Functions

| Function | Module | Purpose | Signature |
|----------|--------|---------|-----------|
| `from_env()` | archive/dal | Create DAL | `() -> BaseDAL` |
| `txn()` | archive/dal | Transaction context | `() -> ContextManager` |
| `ensure_schema()` | archive/dal | Init schema | `() -> None` |
| `insert_item()` | archive/dal | Add item | `(ItemRow) -> str` |
| `insert_artifact()` | archive/dal | Add artifact | `(ArtifactRow) -> str` |
| `query_items()` | archive/dal | Query items | `(dict) -> list` |
| `recent_items()` | archive/dal | Get recent | `(int) -> list` |
| `summary()` | archive/dal | Get stats | `() -> dict` |
| `ensure_artifact()` | archive/dal | Ensure exists | `(str) -> dict` |
| `build()` | rag/indexer | Build index | `(list, list) -> str` |
| `query()` | rag/indexer | Query index | `(str, int) -> list` |
| `embed()` | rag/embeddings | Generate embeddings | `(list) -> ndarray` |
| `similarity()` | rag/embeddings | Cosine similarity | `(str, str) -> float` |

---

## Examples

### Archive Management

```python
from codex.archive.dal import ArchiveDAL, ItemRow, ArtifactRow

# Initialize from environment
dal = ArchiveDAL.from_env()
dal.ensure_schema()

# Archive an item with transaction
with dal.txn():
    item = ItemRow(
        repo="codex",
        path="src/codex/cli.py",
        commit_sha="abc123",
        language="python",
        kind="module",
        reason="API documentation"
    )
    item_id = dal.insert_item(item)
    
    # Also store associated artifact
    artifact = ArtifactRow(
        content_sha256="xyz789",
        size_bytes=2197,
        compression="none",
        mime_type="text/plain",
        storage_driver="local"
    )
    artifact_id = dal.insert_artifact(artifact)

# Query archive
items = dal.query_items({
    'repo': 'codex',
    'language': 'python'
})

# Get statistics
stats = dal.summary()
print(f"Archived {stats['total_items']} items")
```

### RAG Indexing and Querying

```python
from codex.rag.indexer import RAGIndexer

indexer = RAGIndexer()

# Build index
docs = [
    "Authentication using GitHub OAuth...",
    "Token management and validation...",
    "Session persistence and recovery..."
]

metadata = [
    {"topic": "auth", "section": "1"},
    {"topic": "auth", "section": "2"},
    {"topic": "persistence", "section": "1"}
]

index_path = indexer.build(docs, metadata)

# Query index
results = indexer.query("how to authenticate", top_k=2)
for doc, score in results:
    print(f"Score: {score:.3f}")
    print(f"Content: {doc[:100]}...")
```

### Embeddings

```python
from codex.rag.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()

# Generate embeddings
texts = [
    "authentication workflow",
    "token management",
    "api documentation"
]
embeddings = generator.embed(texts)

# Calculate similarity
sim = generator.similarity("auth", "authentication")
print(f"Similarity: {sim:.3f}")
```

---

## Coverage Status

**Documented Signatures:** 25/72 (35%)  
**Next Phase:** Complete remaining storage operations and examples

---

**Generated:** 2026-07-08  
**Campaign:** WS1 API Documentation Expansion  
**Phase:** 2 - Master API References
