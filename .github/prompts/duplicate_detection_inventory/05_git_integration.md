# Phase 5: Git Integration

**Status**: Pending Phase 4 Completion  
**Dependencies**: Phase 1-4  
**Estimated Time**: 2 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Integrate git history analysis to enrich duplicate detection with:
- Git blame (top contributors per file/range)
- Churn metrics (commits in last 90 days)
- File age and modification history
- Author attribution

---

## 📋 Tasks

### Task 5.1: Git Metrics Collector

**File**: `scripts/analysis/git_metrics.py`

**Requirements**:
- Use gitpython or subprocess for git commands
- Extract blame information for file ranges
- Count commits touching each file (90-day window)
- Handle repositories without git history
- Cache results for performance

**Interface**:
```python
@dataclass
class GitMetrics:
    top_author: str
    top_author_email: str
    churn_90_days: int
    total_commits: int
    first_commit_date: Optional[datetime]
    last_modified_date: Optional[datetime]

class GitMetricsCollector:
    """Collects git metrics for files."""
    
    def __init__(self, repo_path: Path):
        """Initialize with repository path."""
        pass
    
    def get_file_metrics(self, file_path: Path) -> GitMetrics:
        """Get metrics for entire file."""
        pass
    
    def get_range_metrics(self, file_path: Path, start_line: int, end_line: int) -> GitMetrics:
        """Get metrics for specific line range."""
        pass
    
    def get_blame(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Get blame info: [(line_no, author, email), ...]"""
        pass
```

### Task 5.2: Blame Parser

**File**: `scripts/analysis/blame_parser.py`

**Requirements**:
- Parse `git blame` output
- Extract author and email per line
- Group by author to find top contributor
- Handle binary files gracefully
- Support line range queries

**Interface**:
```python
class BlameParser:
    """Parses git blame output."""
    
    def parse_blame(self, blame_output: str) -> List[BlameLine]:
        """Parse git blame output."""
        pass
    
    def get_top_author(self, blame_lines: List[BlameLine]) -> Tuple[str, str]:
        """Return (name, email) of top contributor."""
        pass
```

### Task 5.3: Churn Analyzer

**File**: `scripts/analysis/churn_analyzer.py`

**Requirements**:
- Count commits affecting file in time window
- Support configurable time windows
- Use `git log --since` for efficiency
- Handle renamed files
- Track churn per-file and per-directory

**Interface**:
```python
class ChurnAnalyzer:
    """Analyzes file churn."""
    
    def __init__(self, repo_path: Path, days: int = 90):
        """Initialize with time window."""
        pass
    
    def get_file_churn(self, file_path: Path) -> int:
        """Count commits touching file in window."""
        pass
    
    def get_hotspots(self, min_churn: int = 5) -> List[Tuple[Path, int]]:
        """Find files with high churn."""
        pass
```

### Task 5.4: Integration with Detectors

**Update**: All detector classes (exact, normalized, ast, semantic)

**Requirements**:
- Add git metrics to MemberFile dataclass
- Populate metrics during scanning
- Handle missing git repo gracefully
- Cache metrics to avoid repeated git calls

**Updated MemberFile**:
```python
@dataclass
class MemberFile:
    path: str
    start_line: Optional[int]
    end_line: Optional[int]
    file_hash: str
    normalized_hash: Optional[str]
    similarity_score: float
    # New git fields:
    git_blame_top_author: Optional[str]
    git_author_email: Optional[str]
    churn_last_90_days: Optional[int]
    test_coverage: Optional[float]
```

### Task 5.5: Git Availability Check

**File**: `scripts/analysis/git_utils.py`

**Requirements**:
- Check if directory is git repository
- Check if git is installed
- Provide graceful fallbacks
- Log warnings when git unavailable

---

## 🧪 Testing Requirements

### Test 5.1: Git Metrics Tests

**File**: `tests/analysis/test_git_metrics.py`

**Test Cases**:
- `test_file_metrics` - Get metrics for file
- `test_range_metrics` - Get metrics for line range
- `test_no_git_repo` - Handle non-git directory
- `test_git_not_installed` - Handle missing git
- `test_blame_parsing` - Parse blame output
- `test_churn_calculation` - Count commits correctly

### Test 5.2: Blame Parser Tests

**File**: `tests/analysis/test_blame_parser.py`

**Test Cases**:
- `test_parse_blame_output` - Parse git blame
- `test_top_author_extraction` - Find top contributor
- `test_multiple_authors` - Handle multiple contributors
- `test_empty_file` - Handle edge cases

### Test 5.3: Integration Tests

**File**: `tests/analysis/test_git_integration.py`

**Test Cases**:
- `test_metrics_in_output` - Git fields populated
- `test_cache_effectiveness` - Metrics cached
- `test_graceful_degradation` - Works without git

---

## ✅ Acceptance Criteria

- [ ] Git metrics collector working
- [ ] Blame parsing functional
- [ ] Churn analysis implemented
- [ ] 90-day window configurable
- [ ] Graceful fallback for non-git repos
- [ ] Metrics integrated into all detectors
- [ ] Caching improves performance
- [ ] All tests passing
- [ ] Code formatted and linted
- [ ] Documentation updated

---

## 🔄 Self-Healing Checklist

1. [ ] Run: `pytest tests/analysis/test_git_metrics.py -v`
2. [ ] Run: `python -m black scripts/analysis/`
3. [ ] Manual test in git repo: `python scripts/analysis/cli.py . --modes exact`
4. [ ] Verify git fields in output
5. [ ] Test in non-git directory
6. [ ] Run code_review tool
7. [ ] Address any issues
8. [ ] Commit with report_progress

---

## 📊 Expected Output Example

```yaml
member_files:
  - path: "scripts/utils/helper.py"
    file_hash: "abc123..."
    similarity_score: 1.0
    git_blame_top_author: "John Doe"
    git_author_email: "john@example.com"
    churn_last_90_days: 12
    test_coverage: null
```

---

## 📝 Notes

- Git operations can be slow - cache aggressively
- Handle large repos with many commits efficiently
- Consider using libgit2/pygit2 for better performance
- Blame for line ranges more useful than full file

---

## 🔗 Next Phase

**Phase 6: Inventory Schema & Output** (`06_inventory_output.md`)
