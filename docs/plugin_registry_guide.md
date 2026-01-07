# Plugin Registry Guide (D2)

## Overview

This guide documents the entry-point based plugin system for Codex ML. The system provides automatic discovery, validation, and management of plugins through Python entry points.

## Features

✅ **Entry-point based discovery** - Automatic plugin detection via setuptools entry points  
✅ **Plugin validation** - Version compatibility and dependency checking  
✅ **Multiple plugin types** - Support for tokenizers, models, datasets, metrics, trainers, and more  
✅ **Lifecycle management** - Initialize, execute, and cleanup hooks  
✅ **CLI management tool** - Discover, list, validate, and inspect plugins  
✅ **Graceful error handling** - Failed plugins don't break the system  

## Quick Start

### Discovering Plugins

```python
from codex_ml.plugins.entry_points import discover_plugins

# Discover all plugins
discovered = discover_plugins()

# Discover specific groups
discovered = discover_plugins(groups=["codex_ml.tokenizers", "codex_ml.models"])

# Discover and auto-load
discovered = discover_plugins(auto_load=True)
```

### Using the Registry

```python
from codex_ml.plugins.entry_points import EntryPointPluginRegistry

registry = EntryPointPluginRegistry()

# Discover plugins
registry.discover_plugins()

# Load a specific plugin
tokenizer = registry.load_plugin("codex_ml.tokenizers", "my_tokenizer")

# Get loaded plugin
tokenizer = registry.get_plugin("codex_ml.tokenizers", "my_tokenizer")

# List all plugins
plugins = registry.list_plugins()

# Get plugin information
info = registry.get_plugin_info("codex_ml.tokenizers", "my_tokenizer")
```

## Creating Plugins

### 1. Define Plugin Class

```python
from codex_ml.plugins.plugin_registry import Plugin, PluginMetadata

class MyTokenizer(Plugin):
    """Custom tokenizer plugin."""
    
    def initialize(self):
        """Initialize the tokenizer."""
        print("Tokenizer initialized")
    
    def execute(self, text: str) -> list[str]:
        """Tokenize text."""
        return text.split()
    
    def cleanup(self):
        """Cleanup resources."""
        pass
    
    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="my_tokenizer",
            version="1.0.0",
            author="Your Name",
            description="Simple word tokenizer",
            dependencies=["numpy>=1.20.0"],
            min_codex_version="0.1.0",
        )
```

### 2. Register Entry Point

In your package's `setup.py` or `pyproject.toml`:

#### setup.py

```python
from setuptools import setup

setup(
    name="my-codex-plugin",
    version="1.0.0",
    py_modules=["my_plugin"],
    entry_points={
        "codex_ml.tokenizers": [
            "my_tokenizer = my_plugin:MyTokenizer",
        ],
    },
)
```

#### pyproject.toml

```toml
[project]
name = "my-codex-plugin"
version = "1.0.0"

[project.entry-points."codex_ml.tokenizers"]
my_tokenizer = "my_plugin:MyTokenizer"
```

### 3. Install Plugin

```bash
# Install in development mode
pip install -e .

# Or install from package
pip install my-codex-plugin
```

## Entry Point Groups

The following entry point groups are supported:

| Group | Description | Example Plugins |
|-------|-------------|-----------------|
| `codex_ml.plugins` | Generic plugins | Custom processors |
| `codex_ml.tokenizers` | Tokenizer plugins | BPE, WordPiece |
| `codex_ml.models` | Model plugins | Custom architectures |
| `codex_ml.datasets` | Dataset plugins | Custom data loaders |
| `codex_ml.metrics` | Metrics plugins | Custom evaluation metrics |
| `codex_ml.trainers` | Trainer plugins | Custom training loops |
| `codex_ml.reward_models` | Reward model plugins | RLHF reward functions |
| `codex_ml.rl_agents` | RL agent plugins | Custom RL agents |

## CLI Tool Usage

The `manage_plugins.py` script provides command-line plugin management:

### List All Plugins

```bash
python scripts/manage_plugins.py list

# Filter by group
python scripts/manage_plugins.py list --group codex_ml.tokenizers
```

### Discover Plugins

```bash
# Discover all plugins
python scripts/manage_plugins.py discover

# Discover and auto-load
python scripts/manage_plugins.py discover --auto-load
```

### Validate Plugin

```bash
# Validate a plugin
python scripts/manage_plugins.py validate my_tokenizer --group codex_ml.tokenizers
```

### Get Plugin Info

```bash
# Show plugin information
python scripts/manage_plugins.py info my_tokenizer --group codex_ml.tokenizers

# Output as JSON
python scripts/manage_plugins.py info my_tokenizer --group codex_ml.tokenizers --json
```

## Plugin Validation

Plugins are validated for:

### Version Compatibility

```python
from codex_ml.plugins.entry_points import PluginValidator, PluginInfo

validator = PluginValidator(codex_version="1.0.0")

plugin_info = PluginInfo(
    name="my_plugin",
    entry_point_group="codex_ml.plugins",
    entry_point_name="my_plugin",
    module_name="my_plugin",
    required_codex_version="0.9.0",  # Compatible
)

is_valid, error = validator.validate_plugin(plugin_info)
# is_valid=True, error=None
```

### Dependency Checking

```python
plugin_info = PluginInfo(
    name="my_plugin",
    entry_point_group="codex_ml.plugins",
    entry_point_name="my_plugin",
    module_name="my_plugin",
    dependencies=["numpy>=1.20.0", "torch>=2.0.0"],
)

is_valid, error = validator.validate_plugin(plugin_info)
# Checks if numpy and torch are installed
```

## Complete Plugin Example

### Plugin Package Structure

```
my-codex-plugin/
├── my_plugin/
│   ├── __init__.py
│   └── tokenizer.py
├── tests/
│   └── test_tokenizer.py
├── pyproject.toml
└── README.md
```

### my_plugin/tokenizer.py

```python
from codex_ml.plugins.plugin_registry import Plugin, PluginMetadata

class WordPieceTokenizer(Plugin):
    """WordPiece tokenizer plugin."""
    
    def __init__(self, vocab_file: str):
        self.vocab_file = vocab_file
        self.vocab = {}
    
    def initialize(self):
        """Load vocabulary."""
        with open(self.vocab_file) as f:
            self.vocab = {line.strip(): i for i, line in enumerate(f)}
    
    def execute(self, text: str) -> list[int]:
        """Tokenize and encode text."""
        tokens = text.split()
        return [self.vocab.get(token, 0) for token in tokens]
    
    def cleanup(self):
        """Cleanup resources."""
        self.vocab.clear()
    
    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        return PluginMetadata(
            name="wordpiece_tokenizer",
            version="1.0.0",
            author="Your Name",
            description="WordPiece tokenizer implementation",
            dependencies=[],
            min_codex_version="0.1.0",
        )
```

### my_plugin/__init__.py

```python
from .tokenizer import WordPieceTokenizer

__all__ = ["WordPieceTokenizer"]
```

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-codex-plugin"
version = "1.0.0"
description = "Custom tokenizer plugin for Codex ML"
requires-python = ">=3.10"
dependencies = [
    "codex-ml>=0.1.0",
]

[project.entry-points."codex_ml.tokenizers"]
wordpiece = "my_plugin:WordPieceTokenizer"
```

### Usage

```python
from codex_ml.plugins.entry_points import EntryPointPluginRegistry

# Discover and load
registry = EntryPointPluginRegistry()
registry.discover_plugins()

# Load the tokenizer
tokenizer = registry.load_plugin(
    "codex_ml.tokenizers",
    "wordpiece",
    vocab_file="vocab.txt"
)

# Use the tokenizer
tokens = tokenizer.execute("Hello world")
print(tokens)
```

## Best Practices

### 1. Provide Comprehensive Metadata

```python
@classmethod
def get_metadata(cls) -> PluginMetadata:
    return PluginMetadata(
        name="my_plugin",
        version="1.0.0",
        author="Your Name <your.email@example.com>",
        description="Detailed description of what the plugin does",
        dependencies=["numpy>=1.20.0", "torch>=2.0.0"],
        min_codex_version="0.1.0",
    )
```

### 2. Handle Initialization Errors

```python
def initialize(self):
    """Initialize plugin with error handling."""
    try:
        # Initialize resources
        self.load_resources()
    except Exception as e:
        logger.error(f"Failed to initialize plugin: {e}")
        raise
```

### 3. Cleanup Resources

```python
def cleanup(self):
    """Always cleanup resources."""
    if hasattr(self, 'model'):
        del self.model
    if hasattr(self, 'cache'):
        self.cache.clear()
```

### 4. Version Your Plugins

Use semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

### 5. Test Your Plugins

```python
import pytest
from my_plugin import WordPieceTokenizer

def test_tokenizer_initialization():
    tokenizer = WordPieceTokenizer("vocab.txt")
    tokenizer.initialize()
    assert len(tokenizer.vocab) > 0

def test_tokenizer_execution():
    tokenizer = WordPieceTokenizer("vocab.txt")
    tokenizer.initialize()
    tokens = tokenizer.execute("hello world")
    assert isinstance(tokens, list)
```

## Troubleshooting

### Issue: Plugin not discovered

**Solution**: Verify entry point is registered correctly:

```bash
# Check installed entry points
python -c "import importlib.metadata; print(list(importlib.metadata.entry_points(group='codex_ml.plugins')))"

# Reinstall plugin
pip uninstall my-codex-plugin
pip install -e .
```

### Issue: Plugin validation fails

**Solution**: Check version requirements:

```bash
# Get plugin info
python scripts/manage_plugins.py info my_plugin --group codex_ml.plugins

# Check codex_ml version
python -c "import importlib.metadata; print(importlib.metadata.version('codex_ml'))"
```

### Issue: Dependency errors

**Solution**: Install missing dependencies:

```bash
# Check plugin dependencies
python scripts/manage_plugins.py info my_plugin --group codex_ml.plugins

# Install dependencies
pip install numpy torch
```

### Issue: Plugin loading fails

**Solution**: Check plugin class implementation:

```python
# Test import
from my_plugin import MyPlugin

# Test instantiation
plugin = MyPlugin()
plugin.initialize()
```

## Deferred Item D2 Completion

### Implementation Date
2024-12-08

### Deliverables Completed
✅ Entry-point plugin system (`src/codex_ml/plugins/entry_points.py`)  
✅ Plugin discovery and validation  
✅ CLI management tool (`scripts/manage_plugins.py`)  
✅ Comprehensive tests (`tests/plugins/test_entry_points.py`)  
✅ Documentation (this file)  
✅ Example plugin implementations  

### Features Implemented
✅ Automatic plugin discovery via entry points  
✅ Version compatibility checking  
✅ Dependency validation  
✅ Multiple plugin types (8 groups)  
✅ Lifecycle management (initialize, execute, cleanup)  
✅ Error handling and graceful degradation  
✅ CLI tools for management  

### Integration Points
✅ Works with existing plugin infrastructure  
✅ Compatible with programmatic plugin registry  
✅ Supports multiple entry point groups  
✅ Extensible for future plugin types  

### Next Steps
All 4 deferred items complete! (D4, D3, D1, D2)

## References

- [Python Entry Points](https://packaging.python.org/specifications/entry-points/)
- [setuptools Entry Points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html)
- [Plugin Architectures](https://realpython.com/python-application-layouts/#plugin-architecture)
- Existing modules: `plugin_registry.py`, `registries.py`, `loader.py`
