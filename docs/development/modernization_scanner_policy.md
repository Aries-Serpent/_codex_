# Modernization Scanner Policy

## Overview

The modernization scanner (`tools/modernization_scanner_v2.py`) automatically detects legacy Python patterns and suggests improvements. This document defines the policy for which patterns are auto-refactorable vs. suggestion-only.

## Severity Levels

| Severity | Meaning | Action | Example |
|----------|---------|--------|---------|
| **ERROR** | Must fix | Block merge | Syntax errors, deprecated syntax |
| **WARNING** | Should fix | CI warning | typing.List instead of list |
| **SUGGESTION** | Optional | Report only | Dataclass opportunity |
| **AUTO_REFACTOR** | Safe to auto-fix | Apply automatically | Import sorting |

## Detected Patterns

### 1. Typing Imports (WARNING)

**Pattern**: `typing.List`, `typing.Dict`, `typing.Set`, `typing.Tuple`

**Modern Alternative**: Built-in generic types (Python 3.9+)

```python
# Old (deprecated in Python 3.9+)
from typing import List, Dict, Set, Tuple

def process(items: List[str]) -> Dict[str, int]:
    pass

# New (recommended)
def process(items: list[str]) -> dict[str, int]:
    pass
```text

**Policy**:
- **Severity**: WARNING
- **Auto-refactor**: NO (requires manual review)
- **Rationale**: Phase 5 affect compatibility if targeting < Python 3.9

**Migration Path**:
1. Scanner reports all instances
2. Developer reviews and updates
3. Run tests to verify
4. Commit changes

### 2. Optional Type Hint (SUGGESTION)

**Pattern**: `typing.Optional[T]`

**Modern Alternative**: Union syntax `T | None` (Python 3.10+)

```python
# Old
from typing import Optional

def get_value(key: str) -> Optional[str]:
    pass

# New (Python 3.10+)
def get_value(key: str) -> str | None:
    pass
```text

**Policy**:
- **Severity**: SUGGESTION
- **Auto-refactor**: NO
- **Rationale**: Readability preference, not a clear win

**Migration Path**:
1. Optional improvement
2. Apply gradually as code is modified
3. Document preference in style guide

### 3. Bare Except Clauses (WARNING)

**Pattern**: `except:` without exception type

**Modern Alternative**: Specific exception types

```python
# Bad (catches everything including SystemExit)
try:
    risky_operation()
except:
    handle_error()

# Good
try:
    risky_operation()
except Exception as e:
    handle_error(e)

# Better
try:
    risky_operation()
except (ValueError, TypeError) as e:
    handle_error(e)
```text

**Policy**:
- **Severity**: WARNING
- **Auto-refactor**: NO (requires understanding intent)
- **Rationale**: Can hide serious errors, needs case-by-case review

**Migration Path**:
1. Scanner identifies all bare except clauses
2. Developer determines appropriate exception type(s)
3. Add specific exception handling
4. Test edge cases

### 4. Dataclass Candidates (SUGGESTION)

**Pattern**: Classes with only `__init__` and simple attribute assignments

**Modern Alternative**: `@dataclass` decorator

```python
# Candidate for dataclass
class Config:
    def __init__(self, epochs: int, lr: float):
        self.epochs = epochs
        self.lr = lr

# Modern
from dataclasses import dataclass

@dataclass
class Config:
    epochs: int
    lr: float
```text

**Policy**:
- **Severity**: SUGGESTION
- **Auto-refactor**: NO (requires verification of behavior)
- **Rationale**: Dataclasses add features (repr, eq) that Phase 5 change behavior

**Migration Path**:
1. Scanner identifies candidates
2. Developer evaluates if dataclass is appropriate
3. Convert and test thoroughly
4. may need to add `frozen=True` or other options

### 5. String Format Methods (SUGGESTION)

**Pattern**: `str.format()` method calls

**Modern Alternative**: f-strings

```python
# Old
message = "Hello, {}!".format(name)
message = "Count: {count}".format(count=value)

# New
message = f"Hello, {name}!"
message = f"Count: {value}"
```text

**Policy**:
- **Severity**: SUGGESTION
- **Auto-refactor**: NO (complex expressions may need review)
- **Rationale**: F-strings usually better but not always

**Migration Path**:
1. Scanner reports usage
2. Developer converts on a case-by-case basis
3. Simpler cases first
4. Complex formatting Phase 5 stay as .format()

### 6. Walrus Operator Opportunities (SUGGESTION, opt-in)

**Pattern**: Assignment followed by check

**Modern Alternative**: Assignment expression `:=` (Python 3.8+)

```python
# Before
result = expensive_computation()
if result:
    process(result)

# After
if (result := expensive_computation()):
    process(result)
```text

**Policy**:
- **Severity**: SUGGESTION
- **Auto-refactor**: NO
- **Rationale**: Readability concern, team preference varies
- **Default**: DISABLED (enable with `--check-walrus`)

**Migration Path**:
1. Opt-in only
2. Apply to obviously beneficial cases
3. Team discussion for coding style
4. Phase 5 remain disabled permanently

## Using the Scanner

### Basic Usage

```bash
# Scan source code
python tools/modernization_scanner_v2.py src/

# Verbose output with suggestions
python tools/modernization_scanner_v2.py src/ --verbose

# Generate reports
python tools/modernization_scanner_v2.py src/ \
  --json .reports/modernization.json \
  --md .reports/modernization_summary.md

# Include walrus operator checks (opt-in)
python tools/modernization_scanner_v2.py src/ --check-walrus

# Fail on ERROR severity (for CI)
python tools/modernization_scanner_v2.py src/ --fail-on-error
```text

### CI Integration

The scanner runs automatically in post-merge validation:

```yaml
- name: Run modernization scanner
  run: |
    python tools/modernization_scanner_v2.py src/ \
      --json .reports/modernization.json \
      --md .reports/modernization_summary.md
  continue-on-error: true  # Non-blocking
```text

**CI Behavior**:
- Runs on every merge to main
- Generates reports uploaded as artifacts
- Does NOT block merge (informational only)
- Tracks technical debt over time

### Interpreting Results

**JSON Report** (`.reports/modernization.json`):
```json
{
  "total_issues": 42,
  "by_severity": {
    "warning": 15,
    "suggestion": 27
  },
  "by_category": {
    "typing-builtin": 10,
    "dataclass-candidate": 12,
    "string-format": 20
  },
  "issues": [...]
}
```text

**Markdown Summary** (`.reports/modernization_summary.md`):
- Overview statistics
- Issues grouped by category
- Top 10 per category with file/line info

## Remediation Strategy

### Priority Levels

**P0 (Immediate)**:
- ERROR severity items
- Security-related patterns
- Deprecated syntax

**P1 (This Sprint)**:
- WARNING severity with high count
- typing.List/Dict replacements
- Bare except clauses

**P2 (Next Sprint)**:
- High-value SUGGESTIONS
- Dataclass conversions for new code
- String format updates

**P3 (Backlog)**:
- Low-impact suggestions
- Walrus operator opportunities
- Style consistency items

### Bulk vs. Incremental

**Incremental Approach** (Recommended):
- Fix issues as you touch related code
- Include in regular refactoring
- Reduces merge conflict risk
- Spreads work over time

**Bulk Approach**:
- One-time cleanup sprint
- Good for specific categories
- Requires comprehensive testing
- Risk of merge conflicts

**Hybrid Approach** (Best):
- Bulk fix high-priority categories
- Incremental for suggestions
- Document in CHANGELOG

## Team Guidelines

### For Developers

**When You See Scanner Output**:
1. Don't ignore WARNING severity
2. Consider SUGGESTION items if touching that code
3. Don't auto-fix without understanding
4. Add tests when refactoring

**Pull Request Reviews**:
- Check if new code follows modern patterns
- Use scanner locally before submitting
- Don't mix refactoring with feature changes

**Style Preferences**:
- Team Phase 5 decide on specific patterns
- Document decisions in style guide
- Scanner can be configured to align

### For Reviewers

**Review Checklist**:
- [ ] New code uses modern patterns
- [ ] No new WARNING-level issues introduced
- [ ] Refactoring is properly tested
- [ ] Changes align with team style

**When to Request Changes**:
- New typing.List/Dict usage
- Bare except clauses
- String formatting in new code

**When to Accept**:
- SUGGESTION items not addressed
- Existing code left as-is
- Team has documented exception

## Customization

### Adding New Patterns

To add a new detection pattern:

1. **Update scanner**: Edit `tools/modernization_scanner_v2.py`
2. **Add AST visitor**: Implement `visit_*` method
3. **Define severity**: Choose appropriate level
4. **Document**: Add to this policy doc
5. **Test**: Verify detection works
6. **Announce**: Notify team

### Configuration

Currently patterns are hard-coded. Future enhancement could support configuration file:

```yaml
# .modernization.yml (future)
patterns:
  typing-builtin:
    enabled: true
    severity: warning
    auto_refactor: false
  
  walrus-operator:
    enabled: false  # Opt-in
    severity: suggestion
```text

## Metrics & Tracking

### Key Metrics

Track over time:
- Total issues by severity
- Issues per 1000 LOC
- Issue introduction rate
- Issue resolution rate

### Technical Debt Trending

```bash
# Generate trend report
python tools/modernization_scanner_v2.py src/ --json .reports/modern_$(date +%Y%m%d).json

# Compare with previous
jq '.total_issues' .reports/modern_*.json
```text

**Goal**: Trending downward or stable

### Dashboard (Future)

Potential visualization:
- Issue count over time (line chart)
- Category breakdown (pie chart)
- Hotspot files (table)
- Resolution rate (bar chart)

## FAQ

**Q: Why not auto-fix everything?**  
A: Safety and correctness. Many refactorings need context and testing.

**Q: Should I fix issues in files I'm not changing?**  
A: Preferably no. Fix issues in files you're actively working on.

**Q: Can I disable specific checks?**  
A: Not yet, but planned for future versions.

**Q: How often should we run the scanner?**  
A: Automatically in CI. Manually before large refactorings.

**Q: What if the scanner is wrong?**  
A: Report false positives. Scanner will be improved.

## References

- [Python Typing Documentation](https://docs.python.org/3/library/typing.html)
- [PEP 585 - Type Hinting Generics](https://peps.python.org/pep-0585/)
- [PEP 604 - Union Types](https://peps.python.org/pep-0604/)
- [Dataclasses Documentation](https://docs.python.org/3/library/dataclasses.html)

---

**Last Updated**: 2025-11-07  
**Owner**: Code Quality Team  
**Review Cycle**: Quarterly
