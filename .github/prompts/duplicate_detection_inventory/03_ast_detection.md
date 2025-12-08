# Phase 3: AST-Based Detection

**Status**: Pending Phase 2 Completion  
**Dependencies**: Phase 1, Phase 2  
**Estimated Time**: 3-4 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Implement AST (Abstract Syntax Tree) based duplicate detection that identifies:
- Identical function/method definitions across files
- Similar class structures
- Duplicate code blocks at function/method level
- Structural similarity (>X% AST shape match)

---

## 📋 Tasks

### Task 3.1: Python AST Parser

**File**: `scripts/analysis/ast_parsers/python_parser.py`

**Requirements**:
- Parse Python files to AST
- Extract function definitions with signatures
- Extract class definitions
- Extract method definitions
- Capture start/end line numbers
- Handle syntax errors gracefully
- Compute AST fingerprint/hash

**Interface**:
```python
@dataclass
class FunctionSignature:
    name: str
    file_path: str
    start_line: int
    end_line: int
    parameters: List[str]
    return_type: Optional[str]
    ast_hash: str
    body_hash: str

class PythonASTParser:
    """Parses Python files to extract functions/classes."""
    
    def parse_file(self, file_path: Path) -> List[FunctionSignature]:
        """Extract all functions from file."""
        pass
    
    def compute_ast_hash(self, node: ast.AST) -> str:
        """Compute hash of AST structure."""
        pass
    
    def get_structural_similarity(self, ast1: ast.AST, ast2: ast.AST) -> float:
        """Compute similarity score (0.0-1.0)."""
        pass
```

### Task 3.2: JavaScript/TypeScript AST Parser

**File**: `scripts/analysis/ast_parsers/javascript_parser.py`

**Requirements**:
- Use esprima or similar for JS/TS parsing
- Extract function declarations
- Extract arrow functions
- Extract class methods
- Handle both JS and TS syntax
- Capture location information

**Note**: If esprima not available, implement basic regex-based extraction as fallback.

### Task 3.3: AST-Based Detector

**File**: `scripts/analysis/ast_detector.py`

**Requirements**:
- Coordinate language-specific AST parsers
- Group functions by identical AST hash
- Find similar functions (configurable threshold)
- Support multi-file comparison
- Generate duplicate groups at function level

**Interface**:
```python
class ASTDetector:
    """Detects duplicates at function/class level."""
    
    def __init__(self, root_path: Path, similarity_threshold: float = 0.85):
        """Initialize with threshold."""
        pass
    
    def scan(self) -> List[DuplicateGroup]:
        """Scan repository for AST-level duplicates."""
        pass
    
    def find_identical_functions(self) -> List[DuplicateGroup]:
        """Find functions with identical AST."""
        pass
    
    def find_similar_functions(self) -> List[DuplicateGroup]:
        """Find functions with similar AST (above threshold)."""
        pass
```

### Task 3.4: AST Similarity Algorithm

**File**: `scripts/analysis/ast_similarity.py`

**Requirements**:
- Compare two AST structures
- Compute structural similarity score
- Handle different node types
- Weight important vs trivial differences
- Return score 0.0 (completely different) to 1.0 (identical)

**Algorithm Options**:
- Tree edit distance
- Node-by-node comparison
- Subtree matching

**Interface**:
```python
class ASTSimilarity:
    """Computes similarity between AST structures."""
    
    def compare(self, ast1: ast.AST, ast2: ast.AST) -> float:
        """Return similarity score."""
        pass
    
    def tree_edit_distance(self, ast1: ast.AST, ast2: ast.AST) -> int:
        """Compute edit distance between trees."""
        pass
```

### Task 3.5: Parser Registry

**File**: `scripts/analysis/ast_parsers/__init__.py`

**Requirements**:
- Registry of language -> parser mapping
- Auto-detect language from file extension
- Extensible for adding new languages
- Fallback for unsupported languages

**Interface**:
```python
class ParserRegistry:
    """Registry of AST parsers by language."""
    
    def get_parser(self, language: str) -> Optional[ASTParser]:
        """Get parser for language."""
        pass
    
    def register(self, language: str, parser: ASTParser):
        """Register custom parser."""
        pass
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect language from file extension."""
        pass
```

### Task 3.6: Integration with Main Scanner

**Update**: `scripts/analysis/duplicate_scanner.py`

**Requirements**:
- Add "ast" mode support
- Handle function-level vs file-level results
- Merge with existing detection results
- Report both file and function duplicates

---

## 🧪 Testing Requirements

### Test 3.1: Python AST Parser Tests

**File**: `tests/analysis/ast_parsers/test_python_parser.py`

**Test Cases**:
- `test_function_extraction` - Extract functions from file
- `test_class_extraction` - Extract classes and methods
- `test_nested_functions` - Handle nested definitions
- `test_syntax_error_handling` - Gracefully handle bad syntax
- `test_ast_hash_consistency` - Same function = same hash
- `test_ast_hash_difference` - Different function = different hash

### Test 3.2: AST Similarity Tests

**File**: `tests/analysis/test_ast_similarity.py`

**Test Cases**:
- `test_identical_functions` - Score should be 1.0
- `test_completely_different` - Score should be 0.0
- `test_minor_differences` - Score should be > 0.8
- `test_major_differences` - Score should be < 0.5
- `test_renamed_variables` - Should be similar (high score)

### Test 3.3: AST Detector Tests

**File**: `tests/analysis/test_ast_detector.py`

**Test Cases**:
- `test_identical_function_detection` - Find exact duplicates
- `test_similar_function_detection` - Find near-duplicates
- `test_threshold_filtering` - Respect similarity threshold
- `test_cross_file_detection` - Find duplicates across files
- `test_python_javascript_separation` - Language-specific grouping

---

## ✅ Acceptance Criteria

- [ ] Python AST parser working
- [ ] Function extraction complete
- [ ] Class/method extraction working
- [ ] AST hash computation consistent
- [ ] Similarity algorithm implemented
- [ ] Threshold-based filtering working
- [ ] JavaScript parser implemented (or fallback)
- [ ] Parser registry extensible
- [ ] Integration with scanner complete
- [ ] All tests passing
- [ ] Code formatted and linted
- [ ] Documentation updated

---

## 🔄 Self-Healing Checklist

1. [ ] Run: `pytest tests/analysis/ast_parsers/ -v`
2. [ ] Run: `pytest tests/analysis/test_ast_detector.py -v`
3. [ ] Run: `python -m black scripts/analysis/`
4. [ ] Manual test: `python scripts/analysis/cli.py . --modes ast`
5. [ ] Verify function-level duplicates found
6. [ ] Test similarity threshold variations
7. [ ] Run code_review tool
8. [ ] Address any issues
9. [ ] Commit with report_progress

---

## 📊 Expected Output Example

```yaml
- id: "dup-ast-001"
  type: "function-ast"
  language: "python"
  representative_path: "scripts/utils/helpers.py"
  member_files:
    - path: "scripts/utils/helpers.py"
      start_line: 45
      end_line: 58
      file_hash: "abc..."
      normalized_hash: "def..."
      similarity_score: 1.0
      function_name: "process_data"
    - path: "lib/processors/data.py"
      start_line: 12
      end_line: 25
      file_hash: "xyz..."
      normalized_hash: "uvw..."
      similarity_score: 1.0
      function_name: "process_data"
  reason: "Identical function definition (AST match)"
  suggested_action: "refactor"
  confidence: "high"
  tags: ["function-duplicate", "ast-identical"]
  meta:
    detection_method: ["ast"]
    function_signature: "process_data(data: List[Dict]) -> Dict"
  summary: "def process_data(data):\n    result = {}\n    for item in data:\n        ..."
```

---

## 📝 Notes

- AST parsing may fail on syntax errors - handle gracefully
- Focus on Python first, JS/TS can be simpler/fallback
- Similarity threshold should be configurable
- Consider caching AST parses like fingerprints
- Line numbers help developers locate duplicates

---

## 🔗 Next Phase

**Phase 4: Semantic Similarity Detection** (`04_semantic_similarity.md`)
