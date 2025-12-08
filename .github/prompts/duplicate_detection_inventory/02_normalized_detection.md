# Phase 2: Normalized Duplicate Detection

**Status**: Pending Phase 1 Completion  
**Dependencies**: Phase 1 (Foundation & Infrastructure)  
**Estimated Time**: 2-3 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Implement normalized duplicate detection that identifies duplicates after removing:
- Comments (single-line and multi-line)
- Blank lines and excessive whitespace
- Import statement ordering variations
- Optional: Normalize variable/parameter names

---

## 📋 Tasks

### Task 2.1: Create Normalization Engine

**File**: `scripts/analysis/normalized_detector.py`

**Requirements**:
- Strip all comments (language-specific)
- Remove blank lines
- Normalize whitespace (consistent indentation)
- Optionally normalize identifiers
- Compute normalized fingerprint hash
- Group files by normalized hash
- Preserve original for reference

**Interface**:
```python
class NormalizedDetector:
    """Detects duplicates after normalizing code."""
    
    def __init__(self, root_path: Path, normalize_identifiers: bool = False):
        """Initialize with options."""
        pass
    
    def scan(self) -> List[DuplicateGroup]:
        """Scan and return normalized duplicate groups."""
        pass
    
    def normalize_content(self, content: str, language: str) -> str:
        """Normalize code content for comparison."""
        pass
    
    def compute_normalized_hash(self, normalized_content: str) -> str:
        """Compute hash of normalized content."""
        pass
```

### Task 2.2: Language-Specific Normalizers

**File**: `scripts/analysis/normalizers/__init__.py`
**File**: `scripts/analysis/normalizers/python_normalizer.py`
**File**: `scripts/analysis/normalizers/javascript_normalizer.py`

**Requirements**:
- Python normalizer (# comments, """ docstrings)
- JavaScript normalizer (// and /* */ comments)
- TypeScript normalizer (extends JS)
- Generic normalizer for unknown languages

**Python Normalizer**:
```python
class PythonNormalizer:
    """Normalizes Python code."""
    
    def remove_comments(self, code: str) -> str:
        """Remove # comments and docstrings."""
        pass
    
    def normalize_imports(self, code: str) -> str:
        """Sort and normalize imports."""
        pass
    
    def normalize_whitespace(self, code: str) -> str:
        """Normalize indentation and spacing."""
        pass
```

### Task 2.3: Identifier Normalization (Optional Mode)

**File**: `scripts/analysis/identifier_normalizer.py`

**Requirements**:
- Parse code to AST
- Replace variable names with tokens (VAR_1, VAR_2...)
- Replace function parameter names
- Preserve function/class names
- Create stable mapping (deterministic)
- Support Python initially

**Interface**:
```python
class IdentifierNormalizer:
    """Normalizes identifiers for deeper similarity."""
    
    def normalize(self, code: str, language: str) -> str:
        """Normalize identifiers in code."""
        pass
    
    def create_token_map(self, code: str) -> Dict[str, str]:
        """Create stable identifier token mapping."""
        pass
```

### Task 2.4: Fingerprint Cache System

**File**: `scripts/analysis/fingerprint_cache.py`

**Requirements**:
- Cache normalized fingerprints to disk
- Key by (file_path, mtime, size, normalization_mode)
- Invalidate on file changes
- Significantly speed up repeated scans
- Use JSON or SQLite for storage

**Interface**:
```python
class FingerprintCache:
    """Caches normalized fingerprints."""
    
    def __init__(self, cache_dir: Path):
        """Initialize cache in directory."""
        pass
    
    def get(self, file_path: Path, mode: str) -> Optional[str]:
        """Get cached fingerprint if valid."""
        pass
    
    def set(self, file_path: Path, mode: str, fingerprint: str):
        """Cache fingerprint."""
        pass
    
    def invalidate(self, file_path: Path):
        """Invalidate cached fingerprints for file."""
        pass
```

### Task 2.5: Integration with Main Scanner

**Update**: `scripts/analysis/duplicate_scanner.py`

**Requirements**:
- Add "normalized" mode support
- Pass configuration to NormalizedDetector
- Merge results with exact detection
- Handle overlaps (file might be in both groups)

---

## 🧪 Testing Requirements

### Test 2.1: Normalization Tests

**File**: `tests/analysis/test_normalized_detection.py`

**Test Cases**:
- `test_comments_removed` - Files differing only in comments match
- `test_whitespace_ignored` - Different indentation ignored
- `test_import_order_ignored` - Import reordering ignored
- `test_identifier_normalization` - Variable names normalized
- `test_language_specific` - Python vs JS handled correctly
- `test_multiline_comments` - Docstrings/block comments removed

### Test 2.2: Normalizer Tests

**File**: `tests/analysis/normalizers/test_python_normalizer.py`

**Test Cases**:
- `test_single_line_comments` - # comments removed
- `test_docstrings` - """ and ''' docstrings removed
- `test_inline_comments` - Comments after code removed
- `test_import_sorting` - Imports sorted consistently
- `test_whitespace_normalization` - Spacing normalized

### Test 2.3: Cache Tests

**File**: `tests/analysis/test_fingerprint_cache.py`

**Test Cases**:
- `test_cache_hit` - Cached value returned
- `test_cache_miss` - New fingerprint computed
- `test_invalidation` - Modified file invalidated
- `test_cache_persistence` - Cache survives restarts

---

## ✅ Acceptance Criteria

- [ ] Normalized detection working for Python
- [ ] Comments stripped correctly
- [ ] Whitespace normalization functional
- [ ] Import ordering handled
- [ ] Identifier normalization (optional mode)
- [ ] Cache system speeds up repeat scans
- [ ] JavaScript/TypeScript normalizers working
- [ ] Integration with main scanner complete
- [ ] All tests passing
- [ ] Code formatted and linted
- [ ] Documentation updated

---

## 🔄 Self-Healing Checklist

1. [ ] Run: `pytest tests/analysis/test_normalized_detection.py -v`
2. [ ] Run: `pytest tests/analysis/normalizers/ -v`
3. [ ] Run: `python -m black scripts/analysis/`
4. [ ] Manual test: `python scripts/analysis/cli.py . --modes normalized`
5. [ ] Verify output contains normalized groups
6. [ ] Test cache: run twice, second should be faster
7. [ ] Run code_review tool
8. [ ] Address any issues
9. [ ] Commit with report_progress

---

## 📊 Expected Output Example

```yaml
- id: "dup-norm-001"
  type: "normalized-file"
  language: "python"
  representative_path: "scripts/utils/parser.py"
  member_files:
    - path: "scripts/utils/parser.py"
      file_hash: "abc123..."
      normalized_hash: "def456..."
      similarity_score: 1.0
    - path: "lib/parsers/old_parser.py"
      file_hash: "xyz789..."
      normalized_hash: "def456..."
      similarity_score: 1.0
  reason: "Identical after removing comments and whitespace"
  suggested_action: "consolidate"
  confidence: "high"
  tags: ["normalized-duplicate", "comment-only-diff"]
  meta:
    detection_method: ["normalized", "sha256"]
    normalization_mode: "standard"
  summary: "def parse_data(input):\n    return process(input)"
```

---

## 📝 Notes

- Test with real code samples that differ only in style
- Consider language-specific edge cases
- Balance normalization depth vs false positives
- Cache is critical for performance on large repos

---

## 🔗 Next Phase

**Phase 3: AST-Based Detection** (`03_ast_detection.md`)
