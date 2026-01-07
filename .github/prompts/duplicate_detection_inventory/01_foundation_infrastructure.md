# Phase 1: Foundation & Infrastructure

**Status**: Ready for Implementation  
**Dependencies**: None  
**Estimated Time**: 2-3 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Create the foundational infrastructure for the comprehensive duplicate detection system, including:
- Base scanner module structure
- SHA256 exact duplicate detection
- Output writers for YAML/JSON/CSV formats
- Schema design for SUPPLEMENTAL_DUPLICATE_INVENTORY
- Basic CLI interface

---

## 📋 Tasks

### Task 1.1: Create Base Module Structure

**File**: `scripts/analysis/__init__.py`
```python
"""
Duplicate detection and analysis toolkit.

This module provides comprehensive duplicate detection across the codebase
using multiple detection methods: exact (SHA256), normalized, AST-based,
and semantic similarity.
"""

__version__ = "1.0.0"
__author__ = "Codex Automation"

from .duplicate_scanner import DuplicateScanner
from .duplicate_detector import DuplicateDetector

__all__ = ["DuplicateScanner", "DuplicateDetector"]
```

### Task 1.2: Implement Exact Duplicate Detection

**File**: `scripts/analysis/exact_detector.py`

**Requirements**:
- Compute SHA256 hash for each file
- Handle binary and text files
- Respect `.gitignore` patterns
- Exclude default directories: `.git`, `node_modules`, `vendor`, `third_party`, `build`, `dist`
- Support include/exclude patterns via configuration
- Group files by identical hash
- Return list of duplicate groups

**Interface**:
```python
class ExactDetector:
    """Detects exact file duplicates using SHA256 hashing."""
    
    def __init__(self, root_path: Path, exclude_patterns: List[str] = None):
        """Initialize detector with repository root and exclusion patterns."""
        pass
    
    def scan(self) -> List[DuplicateGroup]:
        """Scan repository and return list of duplicate groups."""
        pass
    
    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file contents."""
        pass
```

**DuplicateGroup Schema**:
```python
@dataclass
class DuplicateGroup:
    id: str                          # Unique ID for this group
    type: str                        # "exact-file"
    language: Optional[str]          # Detected language
    representative_path: str         # Best representative file
    member_files: List[MemberFile]   # All files in group
    reason: str                      # Human-readable reason
    suggested_action: str            # "refactor" | "consolidate" | etc.
    confidence: str                  # "low" | "medium" | "high"
    tags: List[str]                  # e.g., ["shim", "generated"]
    meta: Dict[str, Any]             # Detection metadata
    summary: str                     # Short code snippet
```

### Task 1.3: Create Schema Definition

**File**: `scripts/analysis/schema.py`

**Requirements**:
- Define complete dataclass models for inventory schema
- Include validation methods
- Support serialization to YAML/JSON
- Match specification from master plan

**Classes**:
- `MemberFile`
- `DuplicateGroup`
- `InventoryMetadata`
- `SupplementalInventory`

### Task 1.4: Implement Output Writers

**File**: `scripts/analysis/inventory_writer.py`

**Requirements**:
- Write YAML format (primary)
- Write JSON format (alternate)
- Write CSV format (flat summary)
- Handle large inventories efficiently
- Pretty-print for readability
- Validate schema before writing

**Interface**:
```python
class InventoryWriter:
    """Writes duplicate inventory to multiple formats."""
    
    def write_yaml(self, inventory: SupplementalInventory, path: Path):
        """Write inventory to YAML file."""
        pass
    
    def write_json(self, inventory: SupplementalInventory, path: Path):
        """Write inventory to JSON file."""
        pass
    
    def write_csv(self, inventory: SupplementalInventory, path: Path):
        """Write flat summary to CSV file."""
        pass
```

### Task 1.5: Create Main Scanner

**File**: `scripts/analysis/duplicate_scanner.py`

**Requirements**:
- Coordinate all detection engines
- Accept configuration
- Manage scanning process
- Collect results from all detectors
- Build complete inventory
- Write output files

**Interface**:
```python
class DuplicateScanner:
    """Main coordinator for duplicate detection."""
    
    def __init__(self, root_path: Path, config: Optional[Dict] = None):
        """Initialize scanner with repo root and configuration."""
        pass
    
    def scan(self, modes: List[str] = None) -> SupplementalInventory:
        """
        Scan repository for duplicates.
        
        Args:
            modes: List of detection modes to use
                   ["exact", "normalized", "ast", "semantic"]
                   If None, uses all modes.
        
        Returns:
            Complete supplemental inventory
        """
        pass
    
    def write_outputs(self, inventory: SupplementalInventory, output_dir: Path):
        """Write inventory to all output formats."""
        pass
```

### Task 1.6: Create Basic CLI

**File**: `scripts/analysis/cli.py`

**Requirements**:
- Accept repository path as argument
- Support output directory option
- Allow mode selection
- Show progress indicators
- Display summary statistics
- Return appropriate exit codes

**Interface**:
```bash
python scripts/analysis/cli.py /path/to/repo --output-dir ./output --modes exact
```

---

## 🧪 Testing Requirements

### Test 1.1: Exact Detection Tests

**File**: `tests/analysis/test_exact_detection.py`

**Test Cases**:
- `test_identical_files_detected` - Create 2 identical files, verify grouping
- `test_different_files_not_grouped` - Create different files, verify separation
- `test_exclusion_patterns` - Verify `.gitignore` and exclude patterns work
- `test_binary_files` - Test with binary files
- `test_empty_files` - Test with empty files
- `test_large_files` - Test with files >10MB

### Test 1.2: Schema Validation Tests

**File**: `tests/analysis/test_schema.py`

**Test Cases**:
- `test_duplicate_group_creation` - Verify all fields required/optional
- `test_serialization` - Test to_dict() methods
- `test_validation` - Test validation logic
- `test_member_file_schema` - Verify MemberFile structure

### Test 1.3: Output Writer Tests

**File**: `tests/analysis/test_inventory_writer.py`

**Test Cases**:
- `test_yaml_output` - Verify YAML format correct
- `test_json_output` - Verify JSON format correct
- `test_csv_output` - Verify CSV format correct
- `test_roundtrip` - Write and read back, verify identity

### Test 1.4: Scanner Integration Tests

**File**: `tests/analysis/test_duplicate_scanner.py`

**Test Cases**:
- `test_scanner_initialization` - Verify config loading
- `test_exact_mode_only` - Run with exact mode only
- `test_output_generation` - Verify all outputs created
- `test_empty_repository` - Handle empty repo gracefully

---

## ✅ Acceptance Criteria

- [ ] All source files created and documented
- [ ] Exact duplicate detection working correctly
- [ ] SHA256 hashing implemented
- [ ] File exclusion patterns respected
- [ ] Schema defined with validation
- [ ] YAML/JSON/CSV output working
- [ ] CLI accepts arguments and runs
- [ ] All tests passing (100%)
- [ ] Code formatted with black
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] No security issues (CodeQL clean)

---

## 🔄 Self-Healing Checklist

After implementation:
1. [ ] Run: `pytest tests/analysis/test_exact_detection.py -v`
2. [ ] Run: `pytest tests/analysis/ -v` (all tests)
3. [ ] Run: `python -m black scripts/analysis/ tests/analysis/`
4. [ ] Run: `python -m ruff check scripts/analysis/`
5. [ ] Run: `mypy scripts/analysis/` (if type checking enabled)
6. [ ] Manual test: `python scripts/analysis/cli.py . --output-dir /tmp/test --modes exact`
7. [ ] Review output files in `/tmp/test`
8. [ ] Run code_review tool
9. [ ] Run codeql_checker
10. [ ] Address any issues found
11. [ ] Commit with report_progress

---

## 📊 Expected Outputs

After running the scanner on a test repository:

**SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml** (partial):
```yaml
metadata:
  generated_at: "2025-12-08T17:55:00Z"
  scanner_version: "1.0.0"
  repository_root: "/home/runner/work/_codex_/_codex_"
  detection_modes: ["exact"]
  total_files_scanned: 1234
  total_groups: 5
  
duplicate_groups:
  - id: "dup-exact-001"
    type: "exact-file"
    language: "python"
    representative_path: "scripts/utils/helper.py"
    member_files:
      - path: "scripts/utils/helper.py"
        file_hash: "a3b5c..."
        similarity_score: 1.0
      - path: "lib/utils/helper.py"
        file_hash: "a3b5c..."
        similarity_score: 1.0
    reason: "Exact file duplicate (SHA256 match)"
    suggested_action: "consolidate"
    confidence: "high"
    tags: ["exact-duplicate"]
    meta:
      detection_method: ["sha256"]
      created_at: "2025-12-08T17:55:00Z"
      scanner_version: "1.0.0"
    summary: "# Helper utilities for data processing..."
```

---

## 🚀 Implementation Commands

```bash
# Create directory structure
mkdir -p scripts/analysis
mkdir -p tests/analysis

# Create __init__ files
touch scripts/analysis/__init__.py
touch tests/analysis/__init__.py

# Start implementation
# (Follow tasks 1.1-1.6 in order)

# Run tests after each task
pytest tests/analysis/ -v --no-cov

# Format code
python -m black scripts/analysis/ tests/analysis/

# Validate
python scripts/analysis/cli.py . --output-dir /tmp/test --modes exact
```

---

## 📝 Notes

- Focus on correctness over performance in this phase
- Ensure proper error handling for file access issues
- Log progress for long-running scans
- Use pathlib for all file operations
- Follow existing code style in repository
- Add type hints for better IDE support

---

## 🔗 Next Phase

After Phase 1 completion and validation, proceed to:
**Phase 2: Normalized Duplicate Detection** (`02_normalized_detection.md`)
