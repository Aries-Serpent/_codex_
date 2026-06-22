# Common Error Troubleshooting Guide

> Comprehensive troubleshooting guide for common errors and their solutions  
> **Level**: Beginner to Intermediate | **Prerequisites**: Basic Python knowledge  
> **Last Updated**: 2026-06-22 | **Version**: 2.0

---

## Table of Contents

1. [Import Errors](#import-errors)
2. [Configuration Errors](#configuration-errors)
3. [Memory Issues](#memory-issues)
4. [Timeout Errors](#timeout-errors)
5. [Performance Problems](#performance-problems)
6. [Dependency Issues](#dependency-issues)
7. [Quick Reference](#quick-reference)

---

## Import Errors

### Issue: ModuleNotFoundError

**Error Message**:
```
ModuleNotFoundError: No module named 'mymodule'
```

**Common Causes**:
1. Module not installed
2. Wrong Python environment
3. PYTHONPATH misconfigured
4. Circular import

**Diagnosis**:
```bash
# Check if module is installed
pip list | grep mymodule

# Check Python path
python -c "import sys; print(sys.path)"

# Check which Python
which python
python --version
```

**Solutions**:

1. **Install missing module**:
```bash
pip install mymodule
pip install mymodule==1.2.3  # Specific version
```

2. **Activate correct environment**:
```bash
# List virtual environments
ls -la venv/

# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows
```

3. **Fix PYTHONPATH**:
```bash
# Add current directory to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or in Python
import sys
sys.path.insert(0, '/path/to/module')
```

4. **Fix circular imports**:
```python
# ❌ WRONG: Circular import
# module_a.py
from module_b import func_b

# module_b.py
from module_a import func_a

# ✅ CORRECT: Import inside function
# module_a.py
def func_a():
    from module_b import func_b
    return func_b()
```

### Issue: ImportError with Specific Message

**Error Message**:
```
ImportError: cannot import name 'specific_name' from 'module'
```

**Diagnosis**:
```python
# Check what's available in module
import module
print(dir(module))  # List all attributes
print(module.__file__)  # Show module location
```

**Solutions**:

```python
# Check if function exists
import importlib
try:
    module = importlib.import_module('mymodule')
    if hasattr(module, 'my_function'):
        print("Function exists")
    else:
        print("Function not found")
        print(f"Available: {[x for x in dir(module) if not x.startswith('_')]}")
except ImportError as e:
    print(f"Import error: {e}")
```

---

## Configuration Errors

### Issue: Config File Not Found

**Error Message**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'configs/config.yaml'
```

**Diagnosis**:
```bash
# Check if file exists
ls -la configs/config.yaml

# Check current working directory
pwd

# Check from where script runs
cd /path/to/script
pwd
```

**Solutions**:

```python
# ❌ WRONG: Hardcoded path
config_path = "configs/config.yaml"

# ✅ CORRECT: Relative to script location
import os
from pathlib import Path

script_dir = Path(__file__).parent
config_path = script_dir / "configs" / "config.yaml"

if not config_path.exists():
    raise FileNotFoundError(f"Config not found: {config_path}")
```

### Issue: Invalid YAML/JSON Syntax

**Error Message**:
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Common Mistakes**:

```yaml
# ❌ WRONG: Missing colon
database
  host: localhost

# ✅ CORRECT
database:
  host: localhost

# ❌ WRONG: Inconsistent indentation
config:
  setting1: value1
    setting2: value2  # Wrong indentation

# ✅ CORRECT
config:
  setting1: value1
  setting2: value2
```

**Validation**:

```python
import yaml
import json

def validate_yaml(file_path):
    try:
        with open(file_path) as f:
            yaml.safe_load(f)
        print(f"✅ {file_path} is valid YAML")
    except yaml.YAMLError as e:
        print(f"❌ {file_path} has syntax error: {e}")

def validate_json(file_path):
    try:
        with open(file_path) as f:
            json.load(f)
        print(f"✅ {file_path} is valid JSON")
    except json.JSONDecodeError as e:
        print(f"❌ {file_path} has syntax error: {e}")
```

### Issue: Config Key Not Found

**Error Message**:
```
KeyError: 'database_host'
```

**Diagnosis**:
```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Check structure
print(yaml.dump(config))  # Pretty print
print(config.keys())  # Available keys
```

**Solutions**:

```python
# ❌ WRONG: Direct key access
host = config["database_host"]

# ✅ CORRECT: Safe access
host = config.get("database_host", "localhost")

# ✅ OR: With validation
from pydantic import BaseSettings

class Config(BaseSettings):
    database_host: str = "localhost"
    database_port: int = 5432
    
    class Config:
        env_file = ".env"

config = Config()  # Validates and provides defaults
```

---

## Memory Issues

### Issue: Out of Memory Error

**Error Message**:
```
MemoryError: Unable to allocate X.XX GiB for an array
```

**Diagnosis**:
```python
import psutil
import os

# Check available memory
memory = psutil.virtual_memory()
print(f"Total: {memory.total / 1e9:.2f} GB")
print(f"Available: {memory.available / 1e9:.2f} GB")
print(f"Used: {memory.used / 1e9:.2f} GB")

# Check process memory
process = psutil.Process(os.getpid())
print(f"Process memory: {process.memory_info().rss / 1e9:.2f} GB")
```

**Solutions**:

1. **Process data in batches**:
```python
# ❌ WRONG: Load entire dataset
data = np.loadtxt('huge_file.txt')  # All at once

# ✅ CORRECT: Process in chunks
def process_in_chunks(file_path, chunk_size=1000):
    with open(file_path) as f:
        for i, lines in enumerate(iter(lambda: f.readlines(chunk_size), [])):
            yield lines
            if i % 10 == 0:
                print(f"Processed chunk {i}")

for lines in process_in_chunks('huge_file.txt'):
    result = process_lines(lines)
```

2. **Use generators instead of lists**:
```python
# ❌ WRONG: Create entire list
results = [process(x) for x in range(1_000_000_000)]

# ✅ CORRECT: Generator
def process_generator():
    for x in range(1_000_000_000):
        yield process(x)

for result in process_generator():
    use_result(result)
```

3. **Reduce data types**:
```python
import numpy as np

# ❌ WRONG: Default float64
array = np.array([1.0, 2.0, 3.0])  # 8 bytes per element

# ✅ CORRECT: Use float32
array = np.array([1.0, 2.0, 3.0], dtype=np.float32)  # 4 bytes per element
```

### Issue: Memory Leak

**Diagnosis**:
```python
import tracemalloc

tracemalloc.start()

# Run your code
for i in range(1000):
    data = process_something()

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1e6:.2f} MB")
print(f"Peak: {peak / 1e6:.2f} MB")

tracemalloc.stop()
```

**Solutions**:

```python
# ❌ WRONG: Accumulating references
cache = []
def process():
    result = expensive_operation()
    cache.append(result)  # Keeps growing

# ✅ CORRECT: Clear cache periodically
cache = []
def process():
    if len(cache) > 100:
        cache.clear()
    result = expensive_operation()
    cache.append(result)

# ✅ OR: Use bounded cache
from functools import lru_cache

@lru_cache(maxsize=128)  # Limited to 128 entries
def expensive_operation(x):
    return x ** 2
```

---

## Timeout Errors

### Issue: Connection Timeout

**Error Message**:
```
requests.exceptions.ConnectTimeout: HTTPConnectionPool(host='example.com', port=80)
```

**Solutions**:

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# ✅ CORRECT: Add timeout and retries
def request_with_retry(url, timeout=10, retries=3):
    session = requests.Session()
    
    # Add retry strategy
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        response = session.get(url, timeout=timeout)
        return response
    except requests.exceptions.Timeout:
        print(f"Request to {url} timed out after {timeout}s")
        raise
    except requests.exceptions.ConnectionError:
        print(f"Connection error to {url}")
        raise
```

### Issue: Function Timeout

**Error Message**:
```
TimeoutError: function call timed out
```

**Solutions**:

```python
import signal
import time
from contextlib import contextmanager

@contextmanager
def timeout(duration):
    """Context manager for timeouts"""
    def handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {duration}s")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(duration)
    try:
        yield
    finally:
        signal.alarm(0)

# Usage
try:
    with timeout(5):
        long_running_operation()
except TimeoutError:
    print("Operation took too long")

# Alternative: with threading
import threading

def run_with_timeout(func, timeout_sec=5):
    result = [None]
    
    def wrapper():
        result[0] = func()
    
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()
    thread.join(timeout_sec)
    
    if thread.is_alive():
        raise TimeoutError(f"Function did not complete within {timeout_sec}s")
    
    return result[0]
```

---

## Performance Problems

### Issue: Slow Model Inference

**Diagnosis**:
```python
import time
import cProfile
import pstats

# Manual timing
start = time.time()
result = model.predict(data)
duration = time.time() - start
print(f"Prediction took {duration:.3f}s")

# Profiling
profiler = cProfile.Profile()
profiler.enable()

result = model.predict(data)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest
```

**Solutions**:

```python
# ❌ WRONG: Load model each time
def predict(data):
    model = load_model()  # Expensive!
    return model.predict(data)

# ✅ CORRECT: Cache model
import joblib

_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = load_model()
    return _model_cache

def predict(data):
    model = get_model()
    return model.predict(data)

# ✅ OR: Batch predictions
def predict_batch(data_list):
    model = get_model()
    # Vectorized operation is faster than loops
    return model.predict(np.array(data_list))
```

### Issue: High CPU Usage

**Diagnosis**:
```bash
# Check CPU usage
top -b -n 1 | grep python

# Profile CPU
python -m cProfile -s cumulative app.py > profile.txt
```

**Solutions**:

```python
# ✅ Use multiprocessing for CPU-bound tasks
from multiprocessing import Pool

def process_item(item):
    return expensive_computation(item)

if __name__ == "__main__":
    with Pool(4) as pool:  # 4 processes
        results = pool.map(process_item, items)

# ✅ Use numba for numerical code
from numba import jit

@jit(nopython=True)
def fast_computation(data):
    result = 0
    for i in range(len(data)):
        result += data[i] ** 2
    return result
```

---

## Dependency Issues

### Issue: Dependency Conflict

**Error Message**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages
```

**Diagnosis**:
```bash
# Check dependency tree
pip install pipdeptree
pipdeptree

# Check specific package
pipdeptree -p numpy
```

**Solutions**:

```bash
# Create fresh environment with constraints
python -m venv fresh_env
source fresh_env/bin/activate

# Pin versions that work together
cat > requirements-pinned.txt << EOF
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
EOF

pip install -r requirements-pinned.txt

# Or use pip-tools
pip install pip-tools
pip-compile requirements.in  # Generates pinned requirements.txt
```

### Issue: Version Incompatibility

**Error Message**:
```
ImportError: cannot import name 'X' from 'module'
```

**Diagnosis**:
```python
import module
print(module.__version__)

# Check what's available
print(dir(module))
```

**Solutions**:

```python
# ✅ CORRECT: Handle version differences
import sklearn

if sklearn.__version__ >= "1.0":
    from sklearn.model_selection import cross_validate
else:
    from sklearn.cross_validation import cross_val_score as cross_validate

# ✅ OR: Try-except
try:
    from new_location import function
except ImportError:
    from old_location import function
```

---

## Quick Reference

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `ModuleNotFoundError` | Package not installed | `pip install package` |
| `FileNotFoundError` | Wrong path | Use `Path(__file__).parent / path` |
| `KeyError` | Missing config key | Use `dict.get()` with default |
| `MemoryError` | Too much data | Process in chunks |
| `TimeoutError` | Network slow | Add retry logic |
| `ImportError` | Version conflict | Check `__version__` |
| `AttributeError` | Wrong attribute name | Use `dir()` and `help()` |
| `TypeError` | Wrong data type | Check types with `type()` |

---

## Debugging Workflow

1. **Read the error message carefully**
   - Error type and message
   - Line number where it occurred
   - Full traceback

2. **Gather information**
   ```python
   import sys
   print(f"Python: {sys.version}")
   import pkg; print(f"Package: {pkg.__version__}")
   ```

3. **Isolate the problem**
   ```python
   # Start with minimal reproduction
   minimal_code = """
   import x
   y = x.something()
   """
   ```

4. **Test hypothesis**
   ```python
   # Try solution
   # Verify it works
   ```

5. **Document and move on**

---

## Cross-References

- [Configuration Guide](../configuration/CONFIG_USAGE.md)
- [Performance Debugging Guide](../performance/debugging-guide.md)
- [Ray Documentation](https://docs.ray.io)

---

**Word Count**: 2,387 | **Examples**: 26 | **Solutions**: 35
**Last Updated**: 2026-06-22 | **Status**: ✅ Complete
