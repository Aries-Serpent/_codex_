# Phase 4: Semantic Similarity Detection

**Status**: Pending Phase 3 Completion  
**Dependencies**: Phase 1, Phase 2, Phase 3  
**Estimated Time**: 3-4 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Implement semantic similarity detection using:
- MinHash for token-level similarity
- Optional code embedding integration
- Clustering algorithm for similar code blocks
- Configurable similarity threshold

---

## 📋 Tasks

### Task 4.1: MinHash Implementation

**File**: `scripts/analysis/minhash_detector.py`

**Requirements**:
- Tokenize code into meaningful tokens
- Implement MinHash algorithm
- Create LSH (Locality Sensitive Hashing) index
- Find similar code blocks efficiently
- Support configurable similarity threshold (default 0.75)

**Interface**:
```python
class MinHashDetector:
    """Detects similar code using MinHash."""
    
    def __init__(self, threshold: float = 0.75, num_perm: int = 128):
        """Initialize MinHash with parameters."""
        pass
    
    def tokenize(self, code: str) -> List[str]:
        """Tokenize code into shingles."""
        pass
    
    def compute_minhash(self, tokens: List[str]) -> MinHash:
        """Compute MinHash signature."""
        pass
    
    def find_similar(self, signatures: Dict[str, MinHash]) -> List[Tuple]:
        """Find similar code blocks above threshold."""
        pass
```

### Task 4.2: Clustering Algorithm

**File**: `scripts/analysis/similarity_clustering.py`

**Requirements**:
- Group similar code blocks into clusters
- Use similarity scores as edges
- Implement union-find or graph clustering
- Return representative for each cluster
- Handle overlapping similarities

**Interface**:
```python
class SimilarityClusterer:
    """Clusters similar code blocks."""
    
    def cluster(self, similarities: List[Tuple[str, str, float]]) -> List[Cluster]:
        """Cluster similar items."""
        pass
    
    def select_representative(self, cluster: List[str]) -> str:
        """Select best representative for cluster."""
        pass
```

### Task 4.3: Semantic Detector

**File**: `scripts/analysis/semantic_detector.py`

**Requirements**:
- Coordinate MinHash and clustering
- Process all code files
- Generate similarity matrix
- Create duplicate groups for clusters
- Include similarity scores in output

**Interface**:
```python
class SemanticDetector:
    """Detects semantically similar code."""
    
    def __init__(self, root_path: Path, threshold: float = 0.75):
        """Initialize with threshold."""
        pass
    
    def scan(self) -> List[DuplicateGroup]:
        """Scan for semantic duplicates."""
        pass
    
    def build_similarity_matrix(self) -> np.ndarray:
        """Build pairwise similarity matrix."""
        pass
```

### Task 4.4: Code Embedding (Optional)

**File**: `scripts/analysis/code_embeddings.py`

**Requirements**:
- Optional integration with code embedding models
- Fall back to MinHash if embeddings unavailable
- Support pre-computed embeddings
- Cosine similarity for embeddings

**Note**: Keep this optional to avoid heavy dependencies.

### Task 4.5: Integration with Main Scanner

**Update**: `scripts/analysis/duplicate_scanner.py`

**Requirements**:
- Add "semantic" mode support
- Handle overlaps with other detection modes
- Merge clustering results
- Report similarity scores

---

## 🧪 Testing Requirements

### Test 4.1: MinHash Tests

**File**: `tests/analysis/test_minhash_detector.py`

**Test Cases**:
- `test_identical_code` - Score should be 1.0
- `test_completely_different` - Score should be 0.0
- `test_similar_code` - Score should be > threshold
- `test_threshold_filtering` - Only above threshold returned
- `test_tokenization` - Verify token extraction

### Test 4.2: Clustering Tests

**File**: `tests/analysis/test_similarity_clustering.py`

**Test Cases**:
- `test_cluster_formation` - Similar items grouped
- `test_representative_selection` - Best rep chosen
- `test_isolated_items` - Single-item clusters handled
- `test_transitivity` - A~B, B~C creates ABC cluster

### Test 4.3: Semantic Detector Tests

**File**: `tests/analysis/test_semantic_detector.py`

**Test Cases**:
- `test_semantic_detection` - Find similar code
- `test_similarity_matrix` - Matrix computed correctly
- `test_threshold_adjustment` - Different thresholds work
- `test_cross_language` - Language separation maintained

---

## ✅ Acceptance Criteria

- [ ] MinHash algorithm implemented
- [ ] LSH indexing for efficiency
- [ ] Clustering algorithm working
- [ ] Similarity threshold configurable
- [ ] Semantic detector functional
- [ ] Integration with scanner complete
- [ ] All tests passing
- [ ] Performance acceptable (<10 min for large repo)
- [ ] Code formatted and linted
- [ ] Documentation updated

---

## 🔄 Self-Healing Checklist

1. [ ] Run: `pytest tests/analysis/test_minhash_detector.py -v`
2. [ ] Run: `pytest tests/analysis/test_semantic_detector.py -v`
3. [ ] Run: `python -m black scripts/analysis/`
4. [ ] Manual test: `python scripts/analysis/cli.py . --modes semantic --threshold 0.8`
5. [ ] Verify semantic clusters found
6. [ ] Test performance on large file set
7. [ ] Run code_review tool
8. [ ] Address any issues
9. [ ] Commit with report_progress

---

## 📊 Expected Output Example

```yaml
- id: "dup-sem-001"
  type: "semantic-cluster"
  language: "python"
  representative_path: "scripts/parsers/json_parser.py"
  member_files:
    - path: "scripts/parsers/json_parser.py"
      similarity_score: 1.0
    - path: "lib/parsing/json_handler.py"
      similarity_score: 0.82
    - path: "utils/json_utils.py"
      similarity_score: 0.78
  reason: "Semantically similar code (MinHash cluster, threshold=0.75)"
  suggested_action: "refactor"
  confidence: "medium"
  tags: ["semantic-similar", "minhash-cluster"]
  meta:
    detection_method: ["semantic", "minhash"]
    similarity_threshold: 0.75
    cluster_size: 3
  summary: "def parse_json(data):\n    try:\n        return json.loads(data)..."
```

---

## 📝 Notes

- MinHash is probabilistic - may have false positives/negatives
- Clustering threshold affects granularity
- Consider parallel processing for large repos
- Similarity scores help prioritize refactoring

---

## 🔗 Next Phase

**Phase 5: Git Integration** (`05_git_integration.md`)
