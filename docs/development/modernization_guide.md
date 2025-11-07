# Python Modernization Guide

## Overview

This guide covers modern Python patterns and best practices for the _codex_ codebase targeting Python 3.10+.

## Type Hints - Built-in Generics (Python 3.9+)

### Use Built-in Types Instead of `typing` Module

**Old (Deprecated in 3.9+)**:
```python
from typing import List, Dict, Set, Tuple, Optional

def process_items(items: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:
        result[item] = len(item)
    return result
```

**New (Modern)**:
```python
def process_items(items: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result[item] = len(item)
    return result
```

**Optional is still needed**:
```python
from typing import Optional

def get_value(key: str) -> Optional[str]:
    # Returns None if not found
    pass

# Or use union syntax (Python 3.10+)
def get_value(key: str) -> str | None:
    # Returns None if not found
    pass
```

## String Formatting

### Use f-strings

**Old**:
```python
name = "World"
message = "Hello, %s!" % name  # %-formatting
message = "Hello, {}!".format(name)  # .format()
```

**New**:
```python
name = "World"
message = f"Hello, {name}!"  # f-string

# With expressions
count = 42
message = f"Count: {count:04d}"  # Count: 0042
```

## Dataclasses (Python 3.7+)

### Replace Manual `__init__` with Dataclasses

**Old**:
```python
class Config:
    def __init__(self, epochs: int, batch_size: int, lr: float):
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
    
    def __repr__(self):
        return f"Config(epochs={self.epochs}, ...)"
```

**New**:
```python
from dataclasses import dataclass

@dataclass
class Config:
    epochs: int
    batch_size: int
    lr: float = 0.001  # With default
```

## Context Managers

### Use Context Managers for Resource Management

**Old**:
```python
file = open("data.txt")
try:
    data = file.read()
finally:
    file.close()
```

**New**:
```python
with open("data.txt") as file:
    data = file.read()
```

## Path Handling

### Use `pathlib.Path` Instead of `os.path`

**Old**:
```python
import os

filepath = os.path.join("data", "file.txt")
if os.path.exists(filepath):
    with open(filepath) as f:
        content = f.read()
```

**New**:
```python
from pathlib import Path

filepath = Path("data") / "file.txt"
if filepath.exists():
    content = filepath.read_text()
```

## Structural Pattern Matching (Python 3.10+)

### Use Match Statements for Complex Conditionals

**Old**:
```python
def process_command(cmd):
    if cmd["type"] == "create" and cmd.get("entity") == "user":
        return create_user(cmd["data"])
    elif cmd["type"] == "delete" and cmd.get("entity") == "user":
        return delete_user(cmd["data"])
    elif cmd["type"] == "update":
        return update_entity(cmd)
    else:
        return handle_unknown(cmd)
```

**New**:
```python
def process_command(cmd):
    match cmd:
        case {"type": "create", "entity": "user", "data": data}:
            return create_user(data)
        case {"type": "delete", "entity": "user", "data": data}:
            return delete_user(data)
        case {"type": "update", **rest}:
            return update_entity(rest)
        case _:
            return handle_unknown(cmd)
```

## Dictionary Merging (Python 3.9+)

### Use Union Operator for Dict Merging

**Old**:
```python
defaults = {"timeout": 30, "retries": 3}
overrides = {"timeout": 60}

config = {**defaults, **overrides}
# or
config = defaults.copy()
config.update(overrides)
```

**New**:
```python
defaults = {"timeout": 30, "retries": 3}
overrides = {"timeout": 60}

config = defaults | overrides  # Clean and clear
```

## Type Checking Best Practices

### Use Protocols for Duck Typing

**Old**:
```python
from typing import Any

def process(obj: Any):
    obj.read()  # No type checking
```

**New**:
```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

def process(obj: Readable):
    obj.read()  # Type-checked
```

### Use `TypedDict` for Dictionary Structures

**Old**:
```python
def create_user(data: dict) -> dict:
    # What keys are required? What types?
    pass
```

**New**:
```python
from typing import TypedDict

class UserData(TypedDict):
    name: str
    email: str
    age: int

def create_user(data: UserData) -> UserData:
    # Type-checked dictionary
    pass
```

## Error Handling

### Use Specific Exceptions

**Old**:
```python
try:
    result = process()
except Exception as e:  # Too broad
    print(f"Error: {e}")
```

**New**:
```python
try:
    result = process()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return None
```

## List/Dict Comprehensions

### Keep Comprehensions Simple

**Old**:
```python
result = []
for item in items:
    if item.is_valid():
        result.append(item.transform())
```

**New (Simple case)**:
```python
result = [item.transform() for item in items if item.is_valid()]
```

**New (Complex case - use explicit loop)**:
```python
# If complex logic, use explicit loop for readability
result = []
for item in items:
    if item.is_valid() and item.meets_criteria():
        transformed = item.transform()
        if transformed.is_ready():
            result.append(transformed)
```

## Async/Await

### Use Async for I/O-Bound Operations

```python
import asyncio

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_urls(urls: list[str]) -> list[dict]:
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)
```

## Linting and Type Checking

### Use Modern Tools

```bash
# Ruff - Fast linter and formatter
ruff check .
ruff format .

# Mypy - Type checking
mypy src/

# Black - Code formatting
black .

# isort - Import sorting
isort .
```

## Common Pitfalls to Avoid

### Mutable Default Arguments

**Wrong**:
```python
def add_item(item, items=[]):  # Bug: list is shared
    items.append(item)
    return items
```

**Right**:
```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Using `==` for `None`

**Wrong**:
```python
if value == None:
    pass
```

**Right**:
```python
if value is None:
    pass
```

## Scanning Your Code

Use the modernization scanner:

```bash
python tools/modernization_scanner.py src/ --verbose
```

This will identify legacy patterns that can be modernized.

## Resources

- [What's New in Python 3.10](https://docs.python.org/3/whatsnew/3.10.html)
- [What's New in Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)
- [What's New in Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
- [PEP 585 – Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [Real Python - Python Type Checking](https://realpython.com/python-type-checking/)
