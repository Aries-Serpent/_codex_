# AI-Optimized Repository Search & Navigation System

## 🎯 Overview

The AI-Optimized Repository Search & Navigation System provides efficient, semantic-aware search capabilities designed specifically for AI assistants and agents. It creates multi-layered indices that enable rapid discovery and navigation of repository contents with contextual understanding.

## 🧠 Architecture

### Multi-Index Design

The system maintains four complementary indices:

1. **Content Index** - File-level details with entities, imports, and metadata
2. **Semantic Index** - Keyword-to-file mappings for intent-based search
3. **Structural Index** - Hierarchical repository topology
4. **Entity Index** - Searchable code entities (classes, functions, methods)
5. **Metadata Index** - Aggregated statistics and summary information

## 📦 Components

### Index Generation (`generate_ai_index.py`)

Scans the repository and creates comprehensive indices:

```bash
# Generate indices for current repository
python scripts/generate_ai_index.py

# Generate indices for specific repository
python scripts/generate_ai_index.py /path/to/repo
```

**Features:**
- AST-based Python code analysis
- Automatic entity extraction (classes, functions, methods)
- Dependency and import tracking
- Semantic keyword extraction from docstrings
- Hierarchical structure mapping
- Language detection and categorization

**Output Location:** `.codex/ai_index/`

### Search Interface (`ai_search.py`)

Provides multiple search strategies:

```bash
# Multi-strategy search (recommended)
python scripts/ai_search.py "pytest marker" --type multi

# Keyword search
python scripts/ai_search.py "chaos" --type keyword

# Entity search (find classes/functions)
python scripts/ai_search.py "RepositoryIndexer" --type entity

# Path pattern search
python scripts/ai_search.py "tests/test_" --type path

# Limit results
python scripts/ai_search.py "config" --max-results 5
```

## 🔍 Search Capabilities

### 1. Keyword Search

Finds files containing specific keywords in:
- Code entity names (classes, functions)
- Docstrings and comments
- File path components

**Example:**
```bash
python scripts/ai_search.py "authentication" --type keyword
```

### 2. Entity Search

Locates specific code entities:
- Classes
- Functions
- Methods
- Async functions

**Example:**
```bash
python scripts/ai_search.py "CodeEntity" --type entity
```

Returns exact line numbers and context.

### 3. Path Pattern Search

Finds files matching path patterns:
- Directory names
- File name patterns
- Module hierarchies

**Example:**
```bash
python scripts/ai_search.py "scripts/security/" --type path
```

### 4. Semantic Tag Search

Searches by contextual tags derived from:
- Directory structure
- Module organization
- Decorator patterns

### 5. Similarity Search

Finds files similar to a reference file based on:
- Shared keywords
- Common semantic tags
- Import patterns

**API Usage:**
```python
from scripts.ai_search import AIRepositorySearch
from pathlib import Path

search = AIRepositorySearch(Path(".codex/ai_index"))
similar = search.find_similar_files("src/codex/cli.py", max_results=5)
```

### 6. Multi-Strategy Search

Combines all search strategies for comprehensive results:
```bash
python scripts/ai_search.py "testing" --type multi
```

## 📊 Index Structure

### Content Index (`content_index.json`)

Per-file detailed information:

```json
{
  "/path/to/file.py": {
    "path": "/absolute/path/to/file.py",
    "relative_path": "src/codex/file.py",
    "language": "python",
    "size": 4501,
    "last_modified": "Previous Cycle-12-21T01:00:00",
    "entities": [
      {
        "type": "class",
        "name": "RepositoryIndexer",
        "path": "src/codex/file.py",
        "line_start": 50,
        "line_end": 200,
        "signature": null,
        "docstring": "Generate AI-optimized repository indices.",
        "dependencies": [],
        "tags": [],
        "complexity": 1,
        "hash": "a1b2c3d4e5f6g7h8"
      }
    ],
    "imports": ["pathlib", "ast", "json"],
    "exports": ["RepositoryIndexer"],
    "summary": "",
    "keywords": ["repository", "indexer", "generate"],
    "semantic_tags": ["codex"]
  }
}
```

### Semantic Index (`semantic_index.json`)

Keyword-to-files mapping:

```json
{
  "pytest": ["tests/test_config.py", "scripts/generate_pytest_config.py"],
  "chaos": ["tests/serving/test_inference_chaos.py", "pytest.ini"],
  "RepositoryIndexer": ["scripts/generate_ai_index.py"]
}
```

### Structural Index (`structural_index.json`)

Hierarchical directory tree:

```json
{
  "src": {
    "codex": {
      "cli.py": {
        "language": "python",
        "entities": 12,
        "size": 52081
      },
      "logging": {
        "__init__.py": {
          "language": "python",
          "entities": 0,
          "size": 627
        }
      }
    }
  }
}
```

### Entity Index (`entity_index.json`)

All code entities by hash:

```json
{
  "a1b2c3d4e5f6g7h8": {
    "type": "class",
    "name": "RepositoryIndexer",
    "path": "scripts/generate_ai_index.py",
    "line_start": 80,
    "line_end": 450,
    "signature": null,
    "docstring": "Generate AI-optimized repository indices.",
    "dependencies": [],
    "tags": [],
    "complexity": 1,
    "hash": "a1b2c3d4e5f6g7h8"
  }
}
```

### Metadata Index (`metadata_index.json`)

Repository summary:

```json
{
  "generated_at": "Previous Cycle-12-21T01:00:00",
  "repository_path": "/home/runner/work/_codex_/_codex_",
  "total_files": 250,
  "total_entities": 1500,
  "languages": {
    "python": 180,
    "config": 50,
    "documentation": 20
  },
  "top_keywords": [
    {"keyword": "test", "count": 45},
    {"keyword": "config", "count": 30}
  ]
}
```

## 🚀 Usage Examples

### For AI Assistants

**Finding test files:**
```python
search = AIRepositorySearch(Path(".codex/ai_index"))
results = search.search_by_path_pattern("test_")
```

**Finding configuration files:**
```python
results = search.search_by_tag("config")
```

**Finding similar implementations:**
```python
similar = search.find_similar_files("src/codex/cli.py")
```

**Getting file details:**
```python
details = search.get_file_details("src/codex/cli.py")
print(f"Entities: {len(details['entities'])}")
print(f"Imports: {details['imports']}")
```

### Command-Line Usage

**Quick search:**
```bash
# Find pytest-related files
python scripts/ai_search.py pytest

# Find specific class
python scripts/ai_search.py AIRepositorySearch --type entity

# Browse test directory
python scripts/ai_search.py "tests/" --type path --max-results 20
```

## 🔄 Integration

### With Existing Tools

The AI search system integrates with:

- **ripgrep** (`src/codex/search/providers.py`) - Content search fallback
- **FAISS** (`src/codex/retrieval/search.py`) - Vector similarity search
- **Repository map** (`_codex_repo_map.json`) - File structure overview

### Automation

Add to `.github/workflows/auto-update-configs.yml`:

```yaml
- name: Update AI indices
  run: |
    python scripts/generate_ai_index.py
    git add .codex/ai_index/
```

Or use pre-commit hook:

```yaml
# .pre-commit-config.yaml
- id: generate-ai-index
  name: Generate AI repository indices
  entry: python3 scripts/generate_ai_index.py
  language: system
  pass_filenames: false
  stages: [manual]
```

## 📈 Performance

### Index Generation

- **Speed**: ~100 files/second
- **Memory**: Minimal (streaming processing)
- **Storage**: ~1-5MB per 1000 files indexed

### Search Performance

- **Keyword search**: O(1) lookup
- **Entity search**: O(n) where n = total entities
- **Path pattern**: O(n) where n = total files
- **Multi-search**: Combined complexity with deduplication

### Optimization Tips

1. **Incremental updates**: Only re-index changed files
2. **Parallel processing**: Use multiprocessing for large repos
3. **Index compression**: Gzip JSON indices for storage
4. **Caching**: Keep frequently accessed indices in memory

## 🔧 Configuration

### Customizing Index Generation

Edit `generate_ai_index.py`:

```python
# Skip additional directories
SKIP_DIRS = {
    '.git', '.venv', 'node_modules',
    'custom_build', 'custom_cache'  # Add custom dirs
}

# Index additional file types
CUSTOM_EXTENSIONS = {'.rs', '.go', '.ts'}
```

### Search Tuning

Adjust relevance scoring in `ai_search.py`:

```python
# Modify similarity calculation
score = (keyword_overlap * 0.7 + tag_overlap * 0.3)
```

## 🧪 Testing

```bash
# Run search system tests
pytest tests/test_ai_search.py -v

# Validate indices
python scripts/ai_search.py --validate

# Benchmark search performance
python scripts/ai_search.py --benchmark
```

## 🐛 Troubleshooting

### Indices Not Found

```bash
❌ Index directory not found: .codex/ai_index
Run: python scripts/generate_ai_index.py
```

**Solution:** Generate indices first.

### Empty Results

Check if file types are indexed:
```bash
python scripts/ai_search.py "" --type multi | head
```

### Slow Search

For large repositories (>10,000 files):
1. Use specific search types instead of multi-search
2. Limit max_results
3. Consider index sharding

## 📚 API Reference

### AIRepositorySearch Class

```python
class AIRepositorySearch:
    def __init__(self, index_dir: Path)
    def search_by_keyword(query: str, max_results: int) -> List[SearchResult]
    def search_by_entity(name: str, type: Optional[str]) -> List[SearchResult]
    def search_by_path_pattern(pattern: str) -> List[SearchResult]
    def search_by_tag(tag: str) -> List[SearchResult]
    def find_similar_files(path: str, max_results: int) -> List[SearchResult]
    def get_file_details(path: str) -> Optional[Dict[str, Any]]
    def get_repository_summary() -> Dict[str, Any]
    def multi_search(query: str, max_results: int) -> List[SearchResult]
```

### SearchResult Class

```python
@dataclass
class SearchResult:
    path: str
    relevance_score: float
    match_type: str
    context: Dict[str, Any]
    snippet: Optional[str] = None
```

## 🔗 Related Documentation

- [AUTO_CONFIG_README.md](AUTO_CONFIG_README.md) - Automated configuration system
- [AGENTS.md](../AGENTS.md) - Agent development guidelines
- Repository map: `_codex_repo_map.json`

## 📝 Changelog

- **Previous Cycle-12-21**: Initial implementation
  - Multi-layered index generation
  - Comprehensive search interface
  - AST-based entity extraction
  - Semantic keyword mapping
  - Integration with existing search infrastructure

## 🎯 Future Enhancements

- [ ] Incremental index updates
- [ ] Parallel index generation
- [ ] Index compression
- [ ] Vector embeddings for semantic search
- [ ] Natural language query parsing
- [ ] Code dependency graphs
- [ ] Cross-reference resolution
- [ ] Index versioning and migration
