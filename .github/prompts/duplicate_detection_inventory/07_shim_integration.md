# Phase 7: SHIM_INVENTORY Integration

**Status**: Pending Phase 6 Completion  
**Dependencies**: Phase 1-6  
**Estimated Time**: 1-2 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Integrate with existing `.github/SHIM_INVENTORY.yaml` to:
- Read and parse SHIM inventory
- Cross-reference detected duplicates
- Mark which duplicates are already whitelisted
- Flag duplicates NOT in SHIM inventory
- Provide consolidation recommendations

---

## 📋 Tasks

### Task 7.1: SHIM Inventory Reader

**File**: `scripts/analysis/shim_integration.py`

**Requirements**:
- Read `.github/SHIM_INVENTORY.yaml`
- Parse inventory structure
- Extract module paths (legacy and canonical)
- Extract whitelist_duplicates arrays
- Handle missing or invalid SHIM inventory

**Interface**:
```python
@dataclass
class ShimEntry:
    module: str
    legacy_path: str
    canonical_path: str
    status: str
    whitelist_duplicates: List[str]
    
class ShimInventoryReader:
    """Reads SHIM_INVENTORY.yaml."""
    
    def __init__(self, repo_root: Path):
        """Initialize with repository root."""
        pass
    
    def load(self) -> List[ShimEntry]:
        """Load and parse SHIM inventory."""
        pass
    
    def get_whitelisted_paths(self) -> Set[Tuple[str, str]]:
        """Get set of whitelisted (module, path) pairs."""
        pass
```

### Task 7.2: Cross-Reference Engine

**File**: `scripts/analysis/cross_reference.py`

**Requirements**:
- Compare detected duplicates with SHIM inventory
- Match by module name and file paths
- Mark duplicates as "in_shim_inventory" or "not_in_shim_inventory"
- Identify conflicts (whitelisted but still problematic)
- Generate recommendations

**Interface**:
```python
class CrossReference:
    """Cross-references duplicates with SHIM inventory."""
    
    def __init__(self, shim_entries: List[ShimEntry]):
        """Initialize with SHIM inventory."""
        pass
    
    def check_duplicate(self, group: DuplicateGroup) -> CrossReferenceResult:
        """Check if duplicate is in SHIM inventory."""
        pass
    
    def is_whitelisted(self, module: str, path: str) -> bool:
        """Check if module/path is whitelisted."""
        pass
    
    def get_recommendations(self, group: DuplicateGroup) -> List[str]:
        """Get recommendations for duplicate group."""
        pass
```

**CrossReferenceResult**:
```python
@dataclass
class CrossReferenceResult:
    in_shim_inventory: bool
    is_whitelisted: bool
    shim_status: Optional[str]  # active, shim, migrated, scheduled
    recommendations: List[str]
```

### Task 7.3: Enhanced Duplicate Group Schema

**Update**: `scripts/analysis/schema.py`

**Requirements**:
- Add SHIM-related fields to DuplicateGroup
- Include cross-reference results
- Add `not_in_shim_inventory` flag

**Enhanced DuplicateGroup**:
```python
@dataclass
class DuplicateGroup:
    # ... existing fields ...
    
    # SHIM integration fields:
    in_shim_inventory: bool = False
    shim_status: Optional[str] = None
    is_whitelisted: bool = False
    shim_recommendations: List[str] = field(default_factory=list)
```

### Task 7.4: Integration with Scanner

**Update**: `scripts/analysis/duplicate_scanner.py`

**Requirements**:
- Load SHIM inventory during initialization
- Apply cross-reference to all detected groups
- Populate SHIM-related fields
- Generate separate section for non-whitelisted SHIM duplicates

### Task 7.5: Reporting Enhancement

**Update**: `scripts/analysis/report_generator.py`

**Requirements**:
- Add section for SHIM inventory status
- List duplicates NOT in SHIM inventory (priority)
- Show whitelisted vs non-whitelisted
- Provide actionable recommendations

**Enhanced Report Sections**:
```markdown
## SHIM Inventory Status

- Duplicates in SHIM inventory: 8
- Already whitelisted: 8
- Not whitelisted: 0
- Duplicates NOT in SHIM inventory: 12 ⚠️

## High Priority: Duplicates Not in SHIM Inventory

These duplicates are NOT tracked in `.github/SHIM_INVENTORY.yaml` and should be reviewed:

### 1. scripts/utils/parser.py (Exact Duplicate)
- **Action**: Add to SHIM_INVENTORY.yaml or consolidate
- **Files**: scripts/utils/parser.py, lib/parsers/old_parser.py
...
```

---

## 🧪 Testing Requirements

### Test 7.1: SHIM Reader Tests

**File**: `tests/analysis/test_shim_integration.py`

**Test Cases**:
- `test_load_shim_inventory` - Parse SHIM inventory
- `test_extract_whitelist` - Get whitelisted paths
- `test_missing_shim_file` - Handle missing inventory
- `test_invalid_yaml` - Handle malformed YAML

### Test 7.2: Cross-Reference Tests

**File**: `tests/analysis/test_cross_reference.py`

**Test Cases**:
- `test_whitelisted_duplicate` - Match whitelisted
- `test_non_whitelisted` - Identify non-whitelisted
- `test_not_in_inventory` - Flag unknown duplicates
- `test_recommendations` - Generate appropriate recommendations

### Test 7.3: Integration Tests

**File**: `tests/analysis/test_shim_scanner_integration.py`

**Test Cases**:
- `test_shim_fields_populated` - SHIM data in output
- `test_priority_flagging` - Non-inventory duplicates flagged
- `test_report_shim_section` - Report includes SHIM section

---

## ✅ Acceptance Criteria

- [ ] SHIM inventory reader working
- [ ] Cross-reference engine functional
- [ ] Duplicate groups enriched with SHIM data
- [ ] NOT in inventory duplicates flagged
- [ ] Recommendations generated
- [ ] Report enhanced with SHIM section
- [ ] All tests passing
- [ ] Code formatted and linted
- [ ] Documentation updated

---

## 🔄 Self-Healing Checklist

1. [ ] Run: `pytest tests/analysis/test_shim_integration.py -v`
2. [ ] Run: `pytest tests/analysis/test_cross_reference.py -v`
3. [ ] Run: `python -m black scripts/analysis/`
4. [ ] Manual test: Run scanner, check SHIM fields
5. [ ] Verify NOT in inventory section in report
6. [ ] Run code_review tool
7. [ ] Address any issues
8. [ ] Commit with report_progress

---

## 📊 Expected Output Enhancement

```yaml
- id: "dup-exact-001"
  type: "exact-file"
  # ... other fields ...
  in_shim_inventory: true
  shim_status: "shim"
  is_whitelisted: true
  shim_recommendations:
    - "Already tracked in SHIM_INVENTORY.yaml"
    - "Consider consolidating after legacy usage declines"

- id: "dup-exact-002"
  type: "exact-file"
  # ... other fields ...
  in_shim_inventory: false
  shim_status: null
  is_whitelisted: false
  shim_recommendations:
    - "Add to SHIM_INVENTORY.yaml as 'shim' status"
    - "Or consolidate immediately if not in active use"
```

---

## 📝 Notes

- SHIM inventory integration is key differentiator
- Prioritize duplicates NOT in inventory
- Provide actionable recommendations
- Help maintain SHIM inventory accuracy

---

## 🔗 Next Phase

**Phase 8: CLI & Workflow Integration** (`08_cli_workflow.md`)
