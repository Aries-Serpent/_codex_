# Test Assertion Updater - Usage Examples

## Basic Usage

### Example 1: Simple String Format Change
**Scenario**: Implementation evolved error messages to be more descriptive

**Before (failing test)**:
```python
def test_validation_error():
    with pytest.raises(ValueError) as exc_info:
        validate_input("")
    assert str(exc_info.value) == "Invalid input"
```

**After pytest run**:
```
AssertionError: assert 'Invalid input: empty string not allowed' == 'Invalid input'
```

**Agent Command**:
```bash
python -m test_assertion_updater.src.agent analyze tests/test_validation.py::test_validation_error
```

**Expected Fix**:
```python
def test_validation_error():
    with pytest.raises(ValueError) as exc_info:
        validate_input("")
    assert "Invalid input" in str(exc_info.value)
```

---

### Example 2: Return Value Became Structured
**Scenario**: Function now returns dict instead of simple value

**Before (failing test)**:
```python
def test_user_name():
    result = get_user(123)
    assert result == "John Doe"
```

**After implementation change**:
```python
def get_user(user_id):
    return {"name": "John Doe", "id": user_id, "created_at": "2026-01-12"}
```

**Agent Command**:
```bash
python -m test_assertion_updater.src.agent fix tests/test_users.py::test_user_name --validate
```

**Expected Fix**:
```python
def test_user_name():
    result = get_user(123)
    assert result["name"] == "John Doe"
```

---

## Intermediate Usage

### Example 3: List to List-of-Dicts Evolution
**Scenario**: API evolved to return metadata with each item

**Before (failing test)**:
```python
def test_list_items():
    items = fetch_items()
    assert items == ["apple", "banana", "cherry"]
```

**After implementation change**:
```python
def fetch_items():
    return [
        {"name": "apple", "stock": 10},
        {"name": "banana", "stock": 5},
        {"name": "cherry", "stock": 8}
    ]
```

**Agent Command**:
```bash
python -m test_assertion_updater.src.agent fix tests/test_items.py::test_list_items --validate
```

**Expected Fix**:
```python
def test_list_items():
    items = fetch_items()
    item_names = [item["name"] if isinstance(item, dict) else item for item in items]
    assert item_names == ["apple", "banana", "cherry"]
```

---

### Example 4: Batch Processing Multiple Tests
**Scenario**: Multiple tests failed after API refactoring

**Pytest Output**:
```
tests/test_api.py::test_get_user FAILED
tests/test_api.py::test_get_order FAILED
tests/test_api.py::test_list_products FAILED
```

**Agent Command**:
```bash
# Process entire test file
python -m test_assertion_updater.src.agent fix tests/test_api.py --validate

# Or with dry-run to preview changes
python -m test_assertion_updater.src.agent fix tests/test_api.py --dry-run
```

**Result**: Agent fixes all three tests in sequence, validates each, and commits with detailed messages

---

## Advanced Usage

### Example 5: Using with GitHub Actions
**Scenario**: Auto-fix test assertions in CI/CD pipeline

**Workflow File** (`.github/workflows/test-fixer.yml`):
```yaml
name: Auto-Fix Test Assertions
on:
  workflow_run:
    workflows: ["CI Tests"]
    types: [completed]

jobs:
  fix-assertions:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Test Assertion Updater
        run: |
          cd .github/agents/test-assertion-updater
          python -m src.agent fix --validate
          
      - name: Commit fixes
        run: |
          git config user.name "Test Assertion Updater Bot"
          git config user.email "bot@example.com"
          git add tests/
          git commit -m "fix(tests): auto-update assertions after API evolution"
          git push
```

---

### Example 6: Cognitive Brain Integration
**Scenario**: Learn patterns for future improvements

**After Successful Fix**:
```bash
# Pattern is automatically logged to cognitive brain
cat .codex/cognitive_brain/patterns/test_assertion_evolution.md
```

**Pattern Logged**:
```markdown
## Pattern: String Format Evolution
- **Date**: 2026-01-12
- **Occurrences**: 15
- **Success Rate**: 93%
- **Fix Strategy**: Change exact match to substring containment
- **Example**: `assert x == "msg"` → `assert "msg" in str(x)`
```

---

### Example 7: Property-Based Validation
**Scenario**: Ensure fix works across edge cases

**Test Properties Verified**:
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_fix_handles_all_strings(test_string):
    # Agent ensures the fix works for ANY string value
    result = process(test_string)
    assert "Expected substring" in str(result)
```

**Agent automatically runs 100+ examples** before committing the fix

---

## Common Patterns

### Pattern 1: Error Message Improvements
```python
# Before: assert error == "Failed"
# After:  assert "Failed" in str(error)
```

### Pattern 2: Structured Returns
```python
# Before: assert result == value
# After:  assert result["data"] == value
```

### Pattern 3: List Enrichment
```python
# Before: assert items == ["a", "b"]
# After:  assert [x["name"] for x in items] == ["a", "b"]
```

### Pattern 4: Type Wrappers
```python
# Before: assert count == 5
# After:  assert count["total"] == 5
```

---

## Tips

1. **Always use --validate flag** for production
2. **Run --dry-run first** to preview changes
3. **Check cognitive brain patterns** for learned behaviors
4. **Integrate with CI** for automatic fixes
5. **Review auto-generated commit messages** for accuracy

---

*Version: 1.0.0*  
*Last Updated: 2026-01-12*
