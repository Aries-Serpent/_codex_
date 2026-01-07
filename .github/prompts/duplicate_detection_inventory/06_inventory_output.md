# Phase 6: Inventory Schema & Output

**Status**: Pending Phase 5 Completion  
**Dependencies**: Phase 1-5  
**Estimated Time**: 2-3 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Complete the inventory schema implementation and output generation:
- Full YAML/JSON/CSV output writers
- Human-readable markdown report
- Intentional duplicates detection
- Schema validation
- Summary statistics

---

## 📋 Tasks

### Task 6.1: Complete Schema Implementation

**File**: `scripts/analysis/schema.py`

**Requirements**:
- Full dataclass definitions matching specification
- Validation methods for all fields
- Serialization to dict/YAML/JSON
- Comprehensive field documentation
- Type hints for all fields

**Complete Schema**:
```python
@dataclass
class InventoryMetadata:
    generated_at: str  # ISO8601
    scanner_version: str
    repository_root: str
    detection_modes: List[str]
    total_files_scanned: int
    total_groups: int
    total_violations: int
    scan_duration_seconds: float
    
@dataclass
class MemberFile:
    path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    file_hash: str = ""
    normalized_hash: Optional[str] = None
    similarity_score: float = 1.0
    git_blame_top_author: Optional[str] = None
    git_author_email: Optional[str] = None
    churn_last_90_days: Optional[int] = None
    test_coverage: Optional[float] = None

@dataclass
class DuplicateGroup:
    id: str
    type: str  # exact-file, normalized-file, function-ast, semantic-cluster
    language: Optional[str]
    representative_path: str
    member_files: List[MemberFile]
    reason: str
    suggested_action: str  # refactor, consolidate, vendorize, ignore, whitelist
    confidence: str  # low, medium, high
    tags: List[str]
    meta: Dict[str, Any]
    summary: str

@dataclass
class SupplementalInventory:
    metadata: InventoryMetadata
    duplicate_groups: List[DuplicateGroup]
    intentional_duplicates: List[DuplicateGroup]
    
    def validate(self) -> List[str]:
        """Validate schema, return list of errors."""
        pass
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        pass
```

### Task 6.2: Enhanced Output Writers

**File**: `scripts/analysis/inventory_writer.py`

**Requirements**:
- Complete YAML writer with proper formatting
- JSON writer with indentation
- CSV writer with all relevant fields flattened
- Handle large inventories (streaming if needed)
- Pretty-print for readability
- Validate before writing

**Enhanced Interface**:
```python
class InventoryWriter:
    """Writes inventory to multiple formats."""
    
    def write_yaml(self, inventory: SupplementalInventory, path: Path):
        """Write to YAML with proper formatting."""
        pass
    
    def write_json(self, inventory: SupplementalInventory, path: Path):
        """Write to JSON with indentation."""
        pass
    
    def write_csv(self, inventory: SupplementalInventory, path: Path):
        """Write flattened CSV summary."""
        pass
    
    def write_all(self, inventory: SupplementalInventory, output_dir: Path):
        """Write all formats to directory."""
        pass
```

### Task 6.3: Markdown Report Generator

**File**: `scripts/analysis/report_generator.py`

**Requirements**:
- Generate `supplemental_duplicates.md`
- Include executive summary
- Show top N duplicate groups by severity
- Group by detection type
- Include statistics table
- Add suggested actions section
- Format for readability

**Report Structure**:
```markdown
# Supplemental Duplicate Detection Report

Generated: Previous Cycle-12-08T18:00:00Z
Repository: /path/to/repo
Scanner Version: 1.0.0

## Executive Summary

- Total files scanned: 1,234
- Duplicate groups found: 45
- Files affected: 123 (10% of codebase)
- Detection modes: exact, normalized, ast, semantic

## Summary by Detection Type

| Type | Groups | Files | Severity |
|------|--------|-------|----------|
| exact-file | 5 | 12 | HIGH |
| normalized-file | 8 | 20 | MEDIUM |
| function-ast | 15 | 45 | MEDIUM |
| semantic-cluster | 17 | 46 | LOW |

## Top 10 Duplicate Groups by Impact

### 1. Exact File Duplicate: utils/helper.py (HIGH)
...

## Suggested Actions

### Immediate (High Priority)
1. Consolidate exact file duplicates...

### Short-term (Medium Priority)
...

## Appendix: Complete Group List
...
```

**Interface**:
```python
class ReportGenerator:
    """Generates human-readable markdown reports."""
    
    def generate(self, inventory: SupplementalInventory) -> str:
        """Generate markdown report."""
        pass
    
    def write_report(self, inventory: SupplementalInventory, path: Path):
        """Write report to file."""
        pass
```

### Task 6.4: Intentional Duplicates Detector

**File**: `scripts/analysis/intentional_detector.py`

**Requirements**:
- Detect vendored libraries (look for LICENSE, NOTICE files)
- Detect generated files ("DO NOT EDIT" headers)
- Detect test fixtures (in test directories)
- Check for vendoring directory patterns
- Mark duplicates as intentional
- Separate into `intentional_duplicates.yml`

**Heuristics**:
- Files in `vendor/`, `third_party/`, `external/`
- Files with "AUTO-GENERATED" or "DO NOT EDIT" comments
- Files with identical LICENSE blocks
- Binary blobs (images, compiled files)
- Test fixtures with deliberate duplicates

**Interface**:
```python
class IntentionalDetector:
    """Detects intentionally duplicated files."""
    
    def is_intentional(self, group: DuplicateGroup) -> bool:
        """Check if duplicate group is intentional."""
        pass
    
    def get_intentional_reason(self, group: DuplicateGroup) -> str:
        """Get reason why duplicate is intentional."""
        pass
```

### Task 6.5: Statistics Calculator

**File**: `scripts/analysis/statistics.py`

**Requirements**:
- Calculate summary statistics
- Group counts by type
- File coverage statistics
- Severity distribution
- Language breakdown
- Top contributors to duplicates

---

## 🧪 Testing Requirements

### Test 6.1: Schema Tests

**File**: `tests/analysis/test_schema.py`

**Test Cases**:
- `test_complete_schema` - All fields present
- `test_validation` - Invalid data rejected
- `test_serialization` - to_dict works correctly
- `test_optional_fields` - Handle missing optionals

### Test 6.2: Output Writer Tests

**File**: `tests/analysis/test_inventory_writer.py`

**Test Cases**:
- `test_yaml_format` - Valid YAML produced
- `test_json_format` - Valid JSON produced
- `test_csv_format` - Valid CSV produced
- `test_roundtrip` - Write and read back

### Test 6.3: Report Generator Tests

**File**: `tests/analysis/test_report_generator.py`

**Test Cases**:
- `test_report_generation` - Markdown generated
- `test_report_structure` - Required sections present
- `test_statistics` - Counts accurate
- `test_top_groups` - Sorted by priority

### Test 6.4: Intentional Detection Tests

**File**: `tests/analysis/test_intentional_detector.py`

**Test Cases**:
- `test_vendor_detection` - Vendored files detected
- `test_generated_detection` - Generated files detected
- `test_license_detection` - License files detected
- `test_test_fixtures` - Test fixtures detected

---

## ✅ Acceptance Criteria

- [ ] Complete schema implemented
- [ ] All output formats working
- [ ] Markdown report generated
- [ ] Intentional duplicates separated
- [ ] Statistics calculator working
- [ ] Schema validation functional
- [ ] All tests passing
- [ ] Output files well-formatted
- [ ] Code formatted and linted
- [ ] Documentation complete

---

## 🔄 Self-Healing Checklist

1. [ ] Run: `pytest tests/analysis/test_schema.py -v`
2. [ ] Run: `pytest tests/analysis/test_inventory_writer.py -v`
3. [ ] Run: `pytest tests/analysis/test_report_generator.py -v`
4. [ ] Run: `python -m black scripts/analysis/`
5. [ ] Manual test: Generate all outputs
6. [ ] Validate YAML/JSON schema
7. [ ] Review markdown report readability
8. [ ] Run code_review tool
9. [ ] Commit with report_progress

---

## 📝 Notes

- YAML format is primary, JSON/CSV are alternatives
- Markdown report should be management-friendly
- Intentional duplicates reduce noise
- Statistics help prioritize remediation

---

## 🔗 Next Phase

**Phase 7: SHIM_INVENTORY Integration** (`07_shim_integration.md`)
