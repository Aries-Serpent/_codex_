# AST Framework Architecture Guide
## Multi-Language Code Parsing Infrastructure

> **Version**: 1.0.0  
> **Date**: 2026-02-10  
> **Status**: Production-Ready  
> **Languages**: Python, YAML, JSON

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Language Adapters](#language-adapters)
5. [Usage Examples](#usage-examples)
6. [Extension Guide](#extension-guide)
7. [Performance](#performance)
8. [Best Practices](#best-practices)
9. [API Reference](#api-reference)

---

## Overview

The AST (Abstract Syntax Tree) Framework provides a unified interface for parsing and analyzing code across multiple programming languages and data formats. Built on a plugin architecture, it enables language-agnostic AST operations through standardized node representations.

### Key Features

- **Multi-Language Support**: Python, YAML, JSON (extensible to any language)
- **Unified API**: Consistent interface across all language adapters
- **Standardized Representation**: Language-agnostic AST node structure
- **Tree Operations**: Traversal, querying, statistics generation
- **Metadata Extraction**: Language-specific metadata with extensible schema
- **Path Navigation**: Dot-notation access for YAML/JSON structures
- **Performance**: Optimized parsing with minimal overhead

### Use Cases

- **Code Analysis**: Static analysis across multiple languages
- **Documentation Generation**: Extract docstrings, types, structures
- **Code Transformation**: Parse, modify, regenerate code
- **Configuration Management**: Parse and validate YAML/JSON configs
- **Cross-Language Tools**: Build tools that work across languages

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Application                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    ┌────▼────┐    ┌────▼────┐   ┌────▼────┐
    │ Python  │    │  YAML   │   │  JSON   │
    │ Adapter │    │ Adapter │   │ Adapter │
    └────┬────┘    └────┬────┘   └────┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
              ┌─────────▼─────────┐
              │  BaseASTAdapter   │
              │  (Abstract Base)  │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │StandardizedASTNode│
              │ (Data Structure)  │
              └───────────────────┘
```

### Design Principles

1. **Plugin Architecture**: Easy to add new language adapters
2. **Separation of Concerns**: Parsing logic isolated per language
3. **Single Responsibility**: Each adapter handles one language
4. **Open/Closed**: Open for extension, closed for modification
5. **Dependency Inversion**: Depend on abstractions, not implementations

---

## Components

### BaseASTAdapter (Abstract Base Class)

The foundation of the framework. All language adapters extend this class.

**Responsibilities**:
- Define standard API contract
- Implement common operations (traverse, find_nodes_by_type, get_stats)
- Provide default implementations where possible
- Enforce interface compliance

**Core Methods**:
```python
class BaseASTAdapter(ABC):
    @abstractmethod
    def parse(self, source: str, file_path: Optional[Path] = None) -> StandardizedASTNode:
        """Parse source code to AST"""
        
    def parse_file(self, file_path: Path) -> StandardizedASTNode:
        """Parse file directly"""
        
    def traverse(self, node: Optional[StandardizedASTNode] = None) -> List[StandardizedASTNode]:
        """Traverse AST depth-first"""
        
    def find_nodes_by_type(self, node_type: str) -> List[StandardizedASTNode]:
        """Find all nodes of specific type"""
        
    def get_stats(self) -> Dict[str, int]:
        """Get AST statistics"""
        
    @abstractmethod
    def extract_metadata(self, node: StandardizedASTNode) -> Dict[str, Any]:
        """Extract language-specific metadata"""
```

### StandardizedASTNode (Data Structure)

Language-agnostic representation of AST nodes.

**Structure**:
```python
@dataclass
class StandardizedASTNode:
    node_id: str               # Unique identifier
    node_type: str             # Type (function, class, object, etc.)
    name: str                  # Node name
    file_path: Optional[Path]  # Source file path
    line_start: int           # Starting line number
    line_end: int             # Ending line number
    column_start: int         # Starting column
    column_end: int           # Ending column
    parent: Optional['StandardizedASTNode']  # Parent node
    children: List['StandardizedASTNode']    # Child nodes
    metadata: Dict[str, Any]  # Extensible metadata
    source_text: Optional[str]  # Original source text
```

**Features**:
- **Parent/Child Relationships**: Navigate tree bidirectionally
- **Source Location**: Precise location tracking
- **Extensible Metadata**: Language-specific data
- **Serialization**: Convert to/from dict

---

## Language Adapters

### Python Adapter (libcst)

Parses Python source code using libcst for robust, formatting-preserving parsing.

**Key Features**:
- Function extraction with decorators, type hints, docstrings
- Class extraction with inheritance, decorators, docstrings
- Import statement tracking
- Assignment detection
- Nested structure support

**Node Types**:
- `module` - Module root
- `function` - Function definitions
- `class` - Class definitions
- `import` - Import statements
- `assignment` - Variable assignments

**Example**:
```python
from codex.ast_adapters import PythonASTAdapter

adapter = PythonASTAdapter()
root = adapter.parse("""
def greet(name: str) -> str:
    \"\"\"Greet someone by name.\"\"\"
    return f"Hello, {name}!"
""")

functions = adapter.find_nodes_by_type("function")
func = functions[0]

print(func.name)  # "greet"
print(func.metadata["docstring"])  # "Greet someone by name."
print(func.metadata["type_hints"])  # {"name": "str", "return": "str"}
```

### YAML Adapter (PyYAML)

Parses YAML documents with support for nested structures and path navigation.

**Key Features**:
- Mapping (dict) extraction with keys
- Sequence (list) extraction with length
- Scalar (primitive) extraction with types
- Path-based value retrieval
- Nested structure navigation

**Node Types**:
- `document` - Document root
- `mapping` - YAML mappings (dicts)
- `sequence` - YAML sequences (lists)
- `scalar` - YAML scalars (primitives)

**Example**:
```python
from codex.ast_adapters import YAMLASTAdapter

adapter = YAMLASTAdapter()
root = adapter.parse("""
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
""")

# Path-based navigation
host = adapter.get_value_at_path("database.host")
print(host)  # "localhost"

# Query by type
mappings = adapter.find_nodes_by_type("mapping")
print(len(mappings))  # 2 (database, credentials)
```

### JSON Adapter (json)

Parses JSON documents with support for objects, arrays, and path navigation.

**Key Features**:
- Object extraction with keys
- Array extraction with length
- Primitive extraction with types
- Path-based value retrieval (supports array indexing)
- Nested structure navigation

**Node Types**:
- `document` - Document root
- `object` - JSON objects
- `array` - JSON arrays
- `primitive` - JSON primitives (string, number, boolean, null)

**Example**:
```python
from codex.ast_adapters import JSONASTAdapter

adapter = JSONASTAdapter()
root = adapter.parse('''
{
    "users": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ],
    "total": 2
}
''')

# Path-based navigation
total = adapter.get_value_at_path("total")
print(total)  # 2

# Query by type
objects = adapter.find_nodes_by_type("object")
print(len(objects))  # 3 (root + 2 users)
```

---

## Usage Examples

### Basic Parsing

```python
from codex.ast_adapters import PythonASTAdapter, YAMLASTAdapter, JSONASTAdapter

# Python
py_adapter = PythonASTAdapter()
py_root = py_adapter.parse("def foo(): pass")

# YAML
yaml_adapter = YAMLASTAdapter()
yaml_root = yaml_adapter.parse("key: value")

# JSON
json_adapter = JSONASTAdapter()
json_root = json_adapter.parse('{"key": "value"}')
```

### File Parsing

```python
from pathlib import Path

# Parse Python file
adapter = PythonASTAdapter()
root = adapter.parse_file(Path("script.py"))

# Parse YAML config
yaml_adapter = YAMLASTAdapter()
config = yaml_adapter.parse_file(Path("config.yaml"))

# Parse JSON data
json_adapter = JSONASTAdapter()
data = json_adapter.parse_file(Path("data.json"))
```

### Tree Traversal

```python
# Parse source
adapter = PythonASTAdapter()
root = adapter.parse(source_code)

# Traverse all nodes
for node in adapter.traverse(root):
    print(f"{node.node_type}: {node.name}")
```

### Node Queries

```python
# Find all functions
functions = adapter.find_nodes_by_type("function")
for func in functions:
    print(f"Function: {func.name}")
    print(f"  Decorators: {func.metadata['decorators']}")
    print(f"  Docstring: {func.metadata['docstring']}")

# Find all classes
classes = adapter.find_nodes_by_type("class")
for cls in classes:
    print(f"Class: {cls.name}")
    print(f"  Base classes: {cls.metadata['base_classes']}")
```

### Statistics Generation

```python
# Get AST statistics
stats = adapter.get_stats()
print(stats)
# Output: {'module': 1, 'function': 5, 'class': 2, 'import': 3}
```

### Path-Based Navigation (YAML/JSON)

```python
# YAML
yaml_adapter = YAMLASTAdapter()
yaml_adapter.parse("""
app:
  database:
    host: localhost
    port: 5432
""")

host = yaml_adapter.get_value_at_path("app.database.host")
port = yaml_adapter.get_value_at_path("app.database.port")

# JSON with array indexing
json_adapter = JSONASTAdapter()
json_adapter.parse('{"items": [{"name": "first"}, {"name": "second"}]}')

first_name = json_adapter.get_value_at_path("items[0].name")
# Returns: "first"
```

---

## Extension Guide

### Adding a New Language Adapter

Follow these steps to add support for a new language:

#### Step 1: Create Adapter Class

```python
from pathlib import Path
from typing import Dict, List, Optional, Any
from codex.ast_adapters.base_adapter import BaseASTAdapter, StandardizedASTNode

class MyLanguageASTAdapter(BaseASTAdapter):
    """AST adapter for MyLanguage"""
    
    def __init__(self):
        super().__init__()
    
    def parse(self, source: str, file_path: Optional[Path] = None) -> StandardizedASTNode:
        """Parse MyLanguage source to standardized AST"""
        # 1. Parse source using language-specific parser
        # 2. Convert to StandardizedASTNode tree
        # 3. Store root node: self.root_node = root
        # 4. Return root node
        pass
    
    def extract_metadata(self, node: StandardizedASTNode) -> Dict[str, Any]:
        """Extract language-specific metadata"""
        # Return metadata dict with language-specific keys
        pass
```

#### Step 2: Implement Parsing Logic

```python
def parse(self, source: str, file_path: Optional[Path] = None) -> StandardizedASTNode:
    # Use language-specific parser
    import my_language_parser
    parsed = my_language_parser.parse(source)
    
    # Create root node
    root = StandardizedASTNode(
        node_id=str(uuid.uuid4()),
        node_type="document",
        name="<my_language_document>",
        file_path=file_path,
        line_start=1,
        line_end=len(source.splitlines()),
        column_start=0,
        column_end=0,
        children=[],
        metadata={}
    )
    
    # Convert parsed structure to nodes
    for item in parsed:
        child_node = self._convert_to_node(item, parent=root)
        root.children.append(child_node)
    
    self.root_node = root
    return root
```

#### Step 3: Create Test Suite

```python
import pytest
from codex.ast_adapters.my_language_adapter import MyLanguageASTAdapter

class TestMyLanguageASTAdapter:
    @pytest.fixture
    def adapter(self):
        return MyLanguageASTAdapter()
    
    def test_parse_simple(self, adapter):
        source = "# simple my_language code"
        root = adapter.parse(source)
        assert root.node_type == "document"
    
    def test_find_nodes(self, adapter):
        source = "# code with multiple elements"
        adapter.parse(source)
        nodes = adapter.find_nodes_by_type("my_type")
        assert len(nodes) > 0
```

#### Step 4: Update Package Exports

```python
# src/codex/ast_adapters/__init__.py
from .base_adapter import BaseASTAdapter, StandardizedASTNode
from .python_adapter import PythonASTAdapter
from .yaml_adapter import YAMLASTAdapter
from .json_adapter import JSONASTAdapter
from .my_language_adapter import MyLanguageASTAdapter  # Add this

__all__ = [
    "BaseASTAdapter",
    "StandardizedASTNode",
    "PythonASTAdapter",
    "YAMLASTAdapter",
    "JSONASTAdapter",
    "MyLanguageASTAdapter",  # Add this
]
```

---

## Performance

### Benchmarks

Based on integration tests (see `tests/ast_adapters/test_integration.py`):

| Adapter | Parse Time | Data Size | Test Data |
|---------|------------|-----------|-----------|
| Python | <1s | 100s of lines | Functions, classes, imports |
| YAML | <100ms | KB-scale | Nested configurations |
| JSON | <100ms | KB-scale | API responses |
| JSON | <1s | 1000 items | Large datasets |

### Optimization Tips

1. **Reuse Adapters**: Create once, parse multiple times
2. **Lazy Parsing**: Only parse when needed
3. **Selective Traversal**: Use `find_nodes_by_type()` instead of full traversal
4. **Batch Operations**: Parse multiple files in parallel
5. **Cache Results**: Store parsed ASTs for repeated analysis

### Memory Considerations

- Each StandardizedASTNode is ~300 bytes base + metadata
- Tree structures: O(n) memory where n = nodes
- Typical Python file (200 lines): ~50 nodes, ~15KB memory
- Typical YAML config (50 lines): ~20 nodes, ~6KB memory

---

## Best Practices

### 1. Error Handling

```python
try:
    root = adapter.parse(source)
except ValueError as e:
    print(f"Parse error: {e}")
    # Handle invalid syntax
```

### 2. Resource Cleanup

```python
# Adapters are lightweight, no cleanup needed
adapter = PythonASTAdapter()
root = adapter.parse(source)
# Adapter can be reused or discarded
```

### 3. Thread Safety

```python
# Adapters store state (root_node), create one per thread
from threading import local

thread_local = local()

def parse_in_thread(source):
    if not hasattr(thread_local, 'adapter'):
        thread_local.adapter = PythonASTAdapter()
    return thread_local.adapter.parse(source)
```

### 4. Type Checking

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codex.ast_adapters import StandardizedASTNode

def process_node(node: StandardizedASTNode) -> None:
    # Type hints improve IDE support
    print(node.name)
```

### 5. Metadata Validation

```python
def safe_get_metadata(node, key, default=None):
    """Safely get metadata with fallback"""
    return node.metadata.get(key, default)

# Usage
docstring = safe_get_metadata(func_node, "docstring", "No docstring")
```

---

## API Reference

### BaseASTAdapter

#### Methods

**`parse(source: str, file_path: Optional[Path] = None) -> StandardizedASTNode`**
- Parse source code to AST
- Returns: Root node
- Raises: ValueError on parse error

**`parse_file(file_path: Path) -> StandardizedASTNode`**
- Parse file directly
- Returns: Root node
- Raises: IOError, ValueError

**`traverse(node: Optional[StandardizedASTNode] = None) -> List[StandardizedASTNode]`**
- Traverse AST depth-first
- Args: Starting node (defaults to root)
- Returns: List of all nodes in traversal order

**`find_nodes_by_type(node_type: str) -> List[StandardizedASTNode]`**
- Find all nodes of specific type
- Args: Node type to search for
- Returns: List of matching nodes

**`get_stats() -> Dict[str, int]`**
- Get AST statistics
- Returns: Dict mapping node types to counts

**`extract_metadata(node: StandardizedASTNode) -> Dict[str, Any]`**
- Extract language-specific metadata
- Args: Node to extract from
- Returns: Metadata dictionary

### StandardizedASTNode

#### Properties

**`depth`** - Tree depth from root (0-based)
**`full_name`** - Fully qualified name with parent path
**`to_dict()`** - Serialize to dictionary

---

## Appendix

### Dependencies

- **libcst**: Python parsing (formatting-preserving)
- **PyYAML**: YAML parsing
- **json**: JSON parsing (standard library)

### Version History

- **1.0.0** (2026-02-10): Initial release with Python, YAML, JSON support

### Contributing

See repository CONTRIBUTING.md for guidelines on adding new adapters or improving existing ones.

### License

See repository LICENSE file.

---

**Document Status**: ✅ Complete  
**Last Updated**: 2026-02-10  
**Maintainer**: Codex Team
