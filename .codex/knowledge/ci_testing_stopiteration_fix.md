# StopIteration During Pytest Collection - Quick Fix Guide

## Symptom
```
ERROR tests/path/to/test.py::TestClass::test_method - StopIteration
```

No traceback, error happens during `pytest --collect-only` phase.

## Common Causes

### 1. Class Definition with Unavailable Base Class
```python
# ❌ BAD - Evaluated at import time
class MyMock(torch.nn.Module):  # torch may not be available!
    pass
```

### 2. Module-Level next() Without Default
```python
# ❌ BAD - Raises StopIteration if iterator empty
iterator = iter(some_list)
value = next(iterator)
```

### 3. Generator Expression at Module Level
```python
# ❌ BAD - May raise StopIteration during evaluation
data = [x for x in generator_function()]
```

## Quick Fixes

### Fix 1: Conditional Class Definition
```python
# ✅ GOOD
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None
    pytestmark = pytest.mark.skip("torch not available")

if HAS_TORCH and torch is not None:
    class MyMock(torch.nn.Module):
        pass
else:
    class MyMock:  # Dummy for skipped tests
        pass
```

### Fix 2: Safe Iterator Usage
```python
# ✅ GOOD - Option 1: Default value
value = next(iterator, None)

# ✅ GOOD - Option 2: Exception handling
try:
    value = next(iterator)
except StopIteration:
    value = default_value
```

### Fix 3: Lazy Evaluation
```python
# ✅ GOOD - Evaluate in function, not at module level
def get_data():
    return [x for x in generator_function()]
```

## Python 3.12 Specific

Python 3.12 enforces PEP 479 more strictly:
- StopIteration in generators → RuntimeError
- Stricter handling during module import
- Better to prevent than to catch

## Testing Your Fix

```bash
# 1. Check collection
pytest path/to/test.py --collect-only -v

# 2. Check syntax
python3 -m py_compile path/to/test.py

# 3. Run tests
pytest path/to/test.py -v
```

## Best Practices

1. ✅ Check dependencies BEFORE using them
2. ✅ Use conditional class definitions for optional dependencies
3. ✅ Set fallback values (torch=None) on import failure
4. ✅ Register pytestmark early for module-level skips
5. ✅ Always use default argument with next()
6. ✅ Avoid module-level code that can raise StopIteration

## Related

- PEP 479: https://www.python.org/dev/peps/pep-0479/
- Python 3.12 Changes: https://docs.python.org/3/whatsnew/3.12.html
- Pytest Skip: https://docs.pytest.org/en/stable/how-to/skipping.html
